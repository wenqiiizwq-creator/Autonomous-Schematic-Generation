# 从需求文档到设计网表

新设计或新增功能时使用：把受控需求文档变成一份可绘制、可验证的整板设计网表。
设计网表从需求和原厂资料独立写出，不能从草稿原理图回抄；回抄只能证明自洽。

第 1 到第 4 步（读需求、定方案、选核心器件、计算）见 [quick-design.md](quick-design.md) 的“设计者做什么”；本页从第 5 节起只讲设计网表怎么写。

## 5. 写块设计与整板设计网表

快速设计由设计者直接写整板 `electrical-intent.json`；分块设计每块写一个块设计 `record/blocks/<块>.json`，整板核对者用 `blocks.py merge` 按网络名合成整板 `electrical-intent.json`。
块设计的格式、端口与位号规则见 [modules.md](modules.md)；器件、网络、`no_connect` 和下面各项的写法两者相同。整板设计网表格式如下：

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

- 每个物理引脚要么在一个网络里，要么在 `no_connect`；NC 要有手册依据（手册规定未用时悬空、接地还是上下拉），在设计报告里写明。
- `fields.Circuit` 是器件所属的功能块，由合并写成块名；`pages.page_intents()` 默认据此拆页，分页另有安排时用 `page_of` 映射。
- `mpn`、`datasheet`、普通 `fields` 会作为隐藏属性写进原理图，`verify_schematic.py` 逐字段比对，值一律写字符串。
- 哪些器件必须写确切 `mpn` 和 `datasheet` 由 [part-roles.md](part-roles.md) 第 1 节的分级决定（与 schematic-review 对齐）：
  关键器件和特殊器件必须写，并用 `fields.Kind`、`fields.KindSource`、`fields.KindQuote` 按本器件手册声明器件类型；
  定制磁件用 `fields.DesignSheet` 指向磁件设计单代替 `datasheet` 和类型声明；常规件写 `value` 和规格字段，写出算得的最低额定
  （每个电容写耐压，MLCC 另写介质如 X7R/X5R/C0G，每个电感写额定电流；G09-021，`part_classes.audit_identity` 核）。
  不装的位号写 `dnp: true`，值只写值和规格，不写 NC、DNP；它留在 BOM 里，`write_bom` 的 `Assembly` 列写“不装（DNP）”（G09-018）。工作电压高于 30 V 或接市电的网络列在顶层 `high_voltage_nets`，
  据此判定高压连接器、继电器、电源路径上的 NTC 和安全防护位置；跨隔离与市电侧的器件写 `fields.Approval`（认证）。
  电阻和电容按知识库二级类写 `fields.Category`；检流电阻写阻值、容差和功率，功率电阻写容差和功率；
  功耗要考虑的电阻旧格式 `value` 写成 `阻值/公差/额定功率`（如 `620/1%/0.125W`）。
  `Requirement`、`Evidence`、`Status` 是建议字段，便于追溯，工具不解释其内容。
- 电源轨和地网络的网络名就是图上电源符号的 Value；不同地网络（初级地、次级地、端口地）用不同网络名，
  不能为了好看合并。跨页网络在每页用同名全局标签。
- 引脚编号来自确切 MPN 的数据手册，符号库只是载体。
- 离开本设计、另一端在别的板或别的设计里的网络（如到 MCU 板的使能、故障、复位、ADC 网络）逐网声明
  `boundary_nets: [{"net": "EN_N1", "to": "MCU 板", "contract": "设计资料/MCU与固件接口.md"}]`：`to` 写对端，
  `contract` 写接口合同文档（相对交付目录），文档里要有一张表、该网络占一行（整词出现在以 `|` 开头的行里）。
  声明的网络即使只在一页出现也画全局标签（`page_intents` 把它算进该页的 `external`，`Sheet` 也自动算进），
  KiCad 对它报的 `single_global_label`、`isolated_pin_label` 在 ERC 检查项里按声明豁免并列为 `boundary_waived`，
  其余 ERC 结论照常；没声明的网络仍按原规则。不要再逐网写局部标签加理由（Matrix R2 约 40 个 MCU 网络）。

### 连接器角色与外部供电

两触点自定义连接器在 `fields.ComponentRole` 写 `connector`，并在现有器件选型与用法依据中对应原厂资料位置与实际接触脚。
该字段让 `Sheet` 使用锚点画法，并供 `external_supply` 检查项核对设计网表/KiCad 角色一致；它不是机械身份或电气额定值的证明。
常规 `Connector` / `Connector_*` 库已有显式连接器角色；普通 R/C 的二端分类不变。

板上没有 power_out 驱动、经连接器引入的电源/地网络，逐网声明
`external_supply: [{"net": "VCC", "pin": "J1.1", "reason": "主机引入电源，见器件选型与用法依据"}]`，
用 `Sheet.power_flag()` 每网放一个 PWR_FLAG。未声明的网不得放 PWR_FLAG。
`external_supply` 自动检查核对：每个 PWR_FLAG 都在已声明的网上；每个声明网恰好一个；声明的连接器脚在该网上；
该网没有板上 power_out 驱动；连接器的精确身份、装配状态与设计网表一致，声明触点及整个库引脚表都是 passive。
自动检查按缓存的 KiCad power/power_out 标记识别所有 namespace 的旗标，缓存缺失或继承无法解析记 INSUFFICIENT。
旗标只使用实际放置的 unit/body style 及适用的 common 定义；未使用的输出脚不能借给输入型实例。
重命名 KiCad 探针中每个旗标须恰有一个已知编号的实际 power_out 节点，类型或应用范围未知不能记 PASS。
原厂来源含义、供电能力、保护和完整性仍须在设计依据里单独论证。

器件的电源输入脚经一颗串联电阻、电感、磁珠或保险丝从已有驱动的电源取电时（例如 RC 滤波的模拟电源 AVCC），
KiCad 看不到无源器件传过来的驱动，必报 `power_pin_not_driven`。逐网声明
`filtered_supply: [{"net": "AVCC", "from": "PVCC", "via": "R1", "reason": "10 Ω/1 µF RC 滤波"}]`，
同样用 `Sheet.power_flag()` 每网放一个。自动检查核对：`via` 的设计网表库 ID 是 KiCad`Device:` 库中的电阻、电感、磁珠或保险丝符号（`R`、`R_Small`、`L`、`L_Small`、`FerriteBead`、`Fuse`、
`Polyfuse` 等；LED、灯泡、光敏电阻不算），或以 MPN 命名的非 `Device:` 库件加 `fields.ComponentRole`：`series_resistor`/`inductor`/`ferrite_bead`/`fuse`，已贴装、身份与 KiCad 一致、
恰好两只 passive 脚，一端在 `from` 的 KiCad 网、一端在声明网（网络名只允许页路径前缀）；`from` 所在 KiCad 网有板上 power_out
驱动（不计 DNP 器件）、是已声明的 `external_supply` 网，或是已合格的 `filtered_supply` 网（可链式）；声明网上至少有一个
电源输入脚、没有 power_out 驱动、恰好一个旗标；地/回流类网（按网络名或其电源输入脚的 KiCad 引脚名判断）只能与地/回流类网互相派生。
声明只解决 ERC 记账：按该脚最大电流核串联压降，并确认手册允许该脚串联阻抗；偏置馈电（如手册要求的串联大电阻）
与滤波电源分开写理由。逐条列入设计报告，并写明取值、压降和纹波依据。
串联件整体库表仍须恰两只 passive 脚，实际 KiCad 节点还须逐脚编号唯一、完整且类型为 passive；
不能用静态库类型覆盖实际脚类型，复合类型也不能拆出 passive 当作证明。
明确的 KiCad ComponentRole 须与设计网表相符；重复或矛盾的元数据不能作为资格。
即使设计网表未填写角色，明确的 KiCad 非串联角色也不能借 `Device:R` 等库 ID 获得资格。
缺 KiCad 角色的 legacy 项目保留既有设计网表角色兼容，仍不免除身份、类型和原厂来源复核。

核心引脚对照记录的 names/types 不接受空、空白或 `~` 别名；显式未分配的空 footprint 仍合法。
