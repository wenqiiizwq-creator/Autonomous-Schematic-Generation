# 从需求文档到电气意图

新设计或新增功能时使用：把受控需求文档变成一份可绘制、可验证的板级电气意图。
意图从需求和原厂资料独立写出，不能从候选原理图回抄；回抄只能证明自洽。

## 1. 读需求，建需求清单

- 读项目受控的需求文档（用户需求、工程规格、范围与交付），逐条记下需求 ID、要求和适用边界。
  只用已确认的条目；待确认、含糊或冲突的条目标 OPEN，不替用户补产品要求。
- 只问会改变电路方案的缺口（输入范围、输出档位、接口、隔离等级、保护目标等）。
  成本、体积等优化目标用于取舍，不当作硬门槛。
- 分清三类事项：原理图要实现的电路；固件、结构、PCB 要落实的事项（写交接说明，不画进原理图）；
  验证与认证事项（记录，不在出图阶段关闭）。

## 2. 功能分解与追溯

在工程目录里保存一张追溯表（Markdown 即可，工具不检查它）：

| 功能 ID | 功能 | 需求 ID | 实现方式 | 页面 | 状态 |
| --- | --- | --- | --- | --- | --- |
| F-PWR-01 | 3.3 V 辅助电源 | REQ-PWR-002 | LDO | 02_ldo | 已确认（CONFIRMED） |

每条影响电路的需求至少对应一个功能；没有对应的需求写明原因（属固件/结构/验证）。
实现方式写“模块”时，模块外部必需电路仍要画出（见 [symbol-and-peripheral-contracts.md](symbol-and-peripheral-contracts.md)）。

## 3. 架构与分页

按 [reference-driven-board-design.md](reference-driven-board-design.md) 画第 1 页 `System_block`：
电源与信号流向、隔离边界、接口和各页编号。按功能、隔离/电压域和可读面积分页，
页面 ID（如 `02_ldo`）在追溯表、意图和文件名中保持一致。

## 4. 选型、外围合同与计算

- 每个核心器件记录：确切 MPN、数据手册版本/哈希/实际阅读页码、物理引脚表、典型应用、
  必需外围、可选/DNP 支路。分立器件也要按确切订货型号核对引脚（同族通用符号可能脚序不同）。
- 需要机器核对时写 `reference-contract.json`，出图后用 `verify_schematic.py --reference-contract` 检查。
- 数值计算按 [calculation-preflight.md](calculation-preflight.md) 记录保证条件；条件不覆盖时结论只能是
  条件成立（CONDITIONAL）。
- 原理图阶段不定封装、不解决散热：`footprint` 可以留空；功耗、温升、布局约束写进
  《结构与PCB设计要求》交接文档。器件热能力只在影响选型可行性时考虑。
- 新下载的数据手册按 SKILL.md 的资料规则同时存入 HardwareWiki。

## 5. 写板级电气意图

一份 `electrical-intent.json` 覆盖整板，格式如下（充电器工程实际使用的形式）：

```json
{
  "schema": "project-hardware-intent-v1",
  "revision": "v0.1.0",
  "components": [
    {"ref": "U201", "lib_id": "Regulator_Linear:AMS1117-3.3", "value": "AMS1117-3.3",
     "footprint": "", "mpn": "AMS1117-3.3", "datasheet": "datasheets/AMS - AMS1117.pdf",
     "fields": {"Circuit": "02_ldo", "Requirement": "REQ-PWR-002",
                "Evidence": "DS rev C p5 Fig 3", "Status": "Selected"}}
  ],
  "nets": {"+5V": ["U201.3", "C201.1"], "+3V3": ["U201.2", "C202.1"],
           "GND": ["U201.1", "C201.2", "C202.2"]},
  "no_connect": []
}
```

- 每个物理引脚要么在一个网络里，要么在 `no_connect`；NC 要有手册依据。
- `fields.Circuit` 是页面 ID，`pages.page_intents()` 据此拆页。
- `mpn`、`datasheet`、`fields` 会作为隐藏属性写进原理图，`verify_schematic.py` 逐字段比对，值一律写字符串。
  `Requirement`、`Evidence`、`Status` 是建议字段，便于追溯，工具不解释其内容。
- 电源轨和回路网络名就是图上电源符号的 Value；不同回路（初级地、次级地、端口地）用不同网络名，
  不能为了好看合并。跨页网络在每页用同名全局标签。
- 引脚编号来自确切 MPN 的数据手册，符号库只是载体。

## 6. 开放项

未选型、参数待定、需求待确认的事项列成 OPEN 清单，附关闭条件。图上用 `Status` 字段或注释
标明条件设计，不把它画成已完成的电路，也不编造料号或阻值。

## 交接

意图、追溯表、合同、计算和 OPEN 清单与原理图放在同一版本目录；出图验证通过后，
连同 `verify_schematic.py` 的 `summary.json` 一起交给 `schematic-review` 做完整电气审查。

### 连接器角色与外部供电

两触点自定义连接器在 `fields.ComponentRole` 写 `connector`，并在现有器件合同中绑定原厂资料位置与实际接触脚。
该字段让 `Sheet` 使用锚点画法，并供外供审计核对意图/原生角色一致；它不是机械身份或电气额定值的证明。
常规 `Connector` / `Connector_*` 库已有显式连接器角色；普通 R/C 的二端分类不变。

板上没有 power_out 驱动、经连接器引入的电源/回路，逐网声明
`external_supply: [{"net": "VCC", "pin": "J1.1", "reason": "主机引入电源，见器件合同"}]`。
用 `Sheet.power_flag()` 放每网一个标记。审计验证精确身份、装配状态与整个连接器引脚表及声明触点的 passive 类型，
并检查未声明网、重复标记和板上电源输出。原厂来源含义、供电能力、保护和完整性另交 SR。
核心引脚参考合同的 names/types 不接受空、空白或 `~` 别名；显式未分配的空 footprint 仍合法。
