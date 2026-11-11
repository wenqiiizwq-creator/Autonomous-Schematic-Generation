# 核心器件选型

本文规定 ASG 怎样为每个**核心器件角色**找候选、比较并记录结论。核心器件指决定架构或固件/配置依赖的器件：
控制器与协议 IC（PFC、反激、SR、PD、MCU）、功率开关、磁件、隔离与反馈器件；两脚通用件（电阻、电容、普通二极管）按计算直接定值，
不走本流程。选型在任务 C3.2 做（任务 C2.1 定架构、C3.1 定实现方案之后，任务 C4.1 核数据手册之前）：先定型号，再按 [symbol-and-peripheral-contracts.md](symbol-and-peripheral-contracts.md) 核对它的手册。

## 1. 器件库在哪里

原厂资料不在本技能内，在本机知识库 `~/Documents/知识库/HardwareWiki`（环境变量 `HARDWARE_WIKI` 可改）：

| 位置 | 内容 | 怎么找 |
|---|---|---|
| `raw/Datasheet/<一级类>/<二级类>/Vendor - PartNumber.pdf` | 器件手册，约四千份；`catalog.json` 索引了厂商、型号、分类、标签和前几页正文 | `scripts/find_parts.py --category "<二级类>" 关键词…`、`--mpn 型号`；`--text` 连正文一起搜（正文多为英文，关键词用英文） |
| `raw/Designexample/<拓扑>/<板名>/` | 参考设计、评估板手册 | `find_parts.py --designs 关键词…`，结果按板文件夹归并 |
| `raw/Applicationnote/` | 应用笔记 | `find_parts.py --notes 关键词…` |
| `raw/Datasheet/元器件体系/器件统一分类大表.md` | 分类规则与各厂商产品线 | 决定一个新手册放哪个目录 |
| `wiki/entities/` | 已整理的器件/概念条目 | 直接按文件名打开 |

每类器件是干什么的、选它看什么参数，见 [part-roles.md](part-roles.md)；选型从那张表的"按功能找类"开始，
先定二级类，再在类里检索候选。没入索引的 PDF 检索结果标 `未入索引`，可以用，但要自己读文件名核对型号。

## 2. 候选从哪里来（按优先级）

1. 用户指定或用户的优选料表：有就以它为准，其余候选只用来证明它可行或说明为什么不行。
2. 上一版用的型号：作为候选之一，和其他候选同等比较，不因为沿用而优先。
3. 同拓扑参考设计的核心器件：`find_parts.py --designs <拓扑/功率/接口>`，打开板手册的 BOM，把它用的控制器、开关、磁件抄成候选，记下板名。
4. 库内同类手册：按 part-roles.md 定二级类，`find_parts.py --category "<二级类>"` 列出全部，
   用决定性参数先筛掉明显不合的，剩下的打开手册首页核。
5. 库里没有合适的类或候选不足两个时才外部检索（Digikey/JLCPCB MCP 工具或网页），下载的手册按 SKILL.md 任务 C4.1 的资料规则存入工程资料目录（设计期间不写入知识库），
   然后它和第 4 条的候选同等比较，`datasheet` 写交付目录内的路径。记录里写明这一步做过。

## 3. 怎么比较

每个角色先写**决定性条件**：从需求表抽出的、能直接淘汰候选的量（输入电压范围、功率等级、协议版本、隔离等级、
开关频率、封装热阻上限、固件/配置工具依赖、成本或可得性目标）。不写泛泛的"性能好"。
每条条件是一个对象 `{"param", "op", "limit", "unit", "requirement"}`，`op` 只有五种：
`<=`、`>=`（数值）、`covers`（候选范围 `[低, 高]` 覆盖要求范围）、`equals`（字符串，忽略空格、连字符和大小写）、
`has`（功能有无，`limit` 为 true/false）。"计算已绑定""沿用上一版"不是决定性条件，写进 `reason` 或 `sources`。
比较时逐条对照手册首页/特性表，把读到的值和页码记进候选的 `values`；脚本按 `op` 判定，不是人工宣称满足。
只在淘汰或决定时才深读。

淘汰顺序：

1. 电气不满足决定性条件（电压、功率、协议、隔离）。
2. 依赖拿不到：需要 NDA、专有配置工具、未公开固件，而需求没有给出获得途径。
3. 资料不足：库里只有简介没有完整手册，且外部也拿不到——不能选。
4. 封装/热/可得性/成本：按需求的目标；需求没给目标时记"未评估"，不编数字。
5. 剩下多个都能用时，优先参考设计已验证的组合（减少外围设计风险），其次库里资料最全的。

淘汰候选要么有至少一条决定性条件判定不满足（值和页码在 `values` 里），要么写 `reject_kind`：
`dependency`（依赖拿不到）、`data`（资料不足）、`availability`、`cost`、`preference`（都能用，按第 5 条落选）。
`preference` 淘汰的候选在报告里和真正不满足的分开显示，太多说明决定性条件写得不够。

至少两个候选才算比较过；只有一个时写 `single_candidate_reason`（用户指定、沿用上一版、该类库里只有一份且外部检索也没找到……）。

**订货状态按手册订货表核。** 选定的确切料号要在手册订货表里查状态：列在 DISCONTINUED、OBSOLETE、
NOT RECOMMENDED FOR NEW DESIGN、NRND、LAST TIME BUY 下的料号不用于新设计，改用同一手册里在售的料号
（例如同系列不同包装的后缀）。这条不限核心器件：设计网表里有 `mpn` 和 `datasheet` 的每个器件，
`render_design_report.py` 都读手册全文核对，列为停产的算记录问题；确需保留（用户指定、已有库存）时在该器件写
`lifecycle_reason`，报告的“停产料号”一节列出。
订货表只有 Preview、Pre-Production、ADVANCE INFORMATION 状态（预量产，常带 X/P 前缀）的料号可以用于样机，
但要在设计待办里登记一件 `validation`/`handoff` 的投产前换料（采购/产品方，写候选与要重核的项）；
设计网表的 `mpn` 写订货表里真有的码，不写手册正文里的去前缀名（工业校准板 U401：正文写 ISOW3080P，订货表只有 XISOW3080PDWER，2026-11-03）。

**外部依赖作为比较条件。** 每个候选写 `external_dependencies`：选它之后，设计要依赖哪些手册没公开的资料或行为
（固件默认态、内部时序、编码表、全温保证……），每条一句话，写明查过哪页没有；没有就写空列表。
这一项不淘汰候选，而是和代价一起比较：依赖越多，交付时缺外部资料的待办越多。

**外部条件不确定时给出方案，先问再画。** 选定候选的 `external_dependencies` 不为空时，列出 2–3 个选型方案
（例如“单芯片方案”“通用控制器 + MCU”“换一家资料公开的控制器”），比较各自的外部依赖、代价和优缺点，
给出 ASG 的建议和理由，在任务 C3.2 结束时交用户决定；用户定下来之前不进入 C4。用户的决定记在 `decision` 里，
选定候选必须属于用户选的方案。

## 4. 记录：`record/selection.json`

```json
{
  "schema_version": 1,
  "library_root": "~/Documents/知识库/HardwareWiki",
  "roles": [
    {
      "role": "PFC 控制器",
      "block_id": "PFC",
      "refs": ["U201"],
      "requirements": ["R-IN-01", "R-EFF-02"],
      "decisive": [
        {"param": "输入电压范围", "op": "covers", "limit": [90, 264], "unit": "Vac", "requirement": "R-IN-01"},
        {"param": "轻载 DCM/跳周期", "op": "has", "limit": true, "requirement": "R-EFF-02"},
        {"param": "待机功耗", "op": "<=", "limit": 75, "unit": "mW", "requirement": "R-EFF-02"},
        {"param": "外置 MOSFET 驱动", "op": "has", "limit": true}
      ],
      "sources": ["designexample:raw/Designexample/USB-PD/NCP1343PD100WGEVB", "catalog:08_电源管理/AC-DC 转换器"],
      "candidates": [
        {"mpn": "NCP1623", "vendor": "onsemi", "status": "selected",
         "datasheet": "raw/Datasheet/08_电源管理/AC-DC 转换器/onsemi - NCP1623.pdf",
         "reason": "参考设计验证的组合；多模 CrM/DCM 满足轻载效率", "pages": "1, 6", "external_dependencies": [],
         "values": {"输入电压范围": {"value": [85, 265], "page": 1}, "轻载 DCM/跳周期": {"value": true, "page": 1},
                    "待机功耗": {"value": 30, "page": 6}, "外置 MOSFET 驱动": {"value": true, "page": 1}}},
        {"mpn": "L4984D", "vendor": "ST", "status": "rejected",
         "datasheet": "raw/Datasheet/08_电源管理/AC-DC 转换器/ST - L4984D.pdf",
         "reason": "固定 CCM，没有轻载 DCM/跳周期", "pages": "1",
         "values": {"轻载 DCM/跳周期": {"value": false, "page": 1}}}
      ]
    }
  ]
}
```

字段要求（`render_design_report.py` 检查，不满足算记录问题，`pack_design.py` 拒绝打包）：

- 每个角色有 `role`、`block_id`（所属功能块，`architecture.json` 的 `blocks[].id`；`block_circuits.py` 按它把角色抽进块文件）、非空 `refs`、非空 `decisive`（对象列表，见第 3 节）、`candidates`；`sources`（候选从哪里找的）可选。
- 选定候选写 `port_limits`：它在本块各端口上的限值和手册页码（格式见 [能力模块](modules.md) 的块文件一节），供任务 C3.3 定接口参数；
- `selected` 和 `alternate` 候选对每条决定性条件都有 `values[param] = {"value", "page"}` 且判定满足；
  `rejected` 候选至少一条判定不满足，或写 `reject_kind`。
- 候选 ≥ 2，否则要有 `single_candidate_reason`；`status` 只能是 `selected`/`rejected`/`alternate`，恰好一个 `selected`。
- 每个候选有 `mpn`、`reason`、`datasheet`；`datasheet` 是相对 `library_root` 的路径，文件必须存在（也可以是交付目录内 `设计资料/` 下的文件）。
  `values` 的每个 `page` 必须在该手册页数之内，否则算记录问题；数值在那一页的文字里找不到时列入报告“引用待人工核对”，不拦。
- `selected` 的每个位号都在设计网表里，且该器件的 `value` 或 `mpn` 含选定型号。
- 设计网表里每个 U/Q/T 开头的器件都属于某个角色；一个角色可以覆盖多个位号（例如两只并联 MOS）。
- 上两条是位号绑定，设计网表写出（任务 C5.1）后才查；任务 C3.2 还没有设计网表，`check_selection` 只查候选、资料和用户决定
  （Matrix R3：1.4 时设计网表不存在，绑定检查使做完的标志无法达到）。
- 每个角色都有确认记录 `decision`（任务 C3.2 选型确认，整板评测 2026-11-07）：用户确认的写 `{"source": "user:<日期>", "locator": "<对话里哪一处>"}`；
  需求或方案文档已写明用户确认、选型与之一致的写 `{"source": "scheme:<证据编号>", "locator": "<文档里哪一处>", "quote": "<原文>"}`，
  证据编号在 `design-closure.json` 的 `evidence` 里，文件是用户的文档（不是 ASG 写的 `设计资料/`、`record/`），`quote` 原样在文件里且含选定型号。
  无人当场确认、任务书有代答授权（[任务输入输出格式](workflow-handoff.md) 的 `delegation`，`scope` 含 `selection`）时写
  `{"source": "delegate:<代答人>:<日期>"}`，代答人与日期和授权一致；代答只能采纳 ASG 的建议，有 `options` 的角色要选 `recommended` 的方案。
  C4 中改变已确认的选型后重新确认，同样按这三种来源写。
  一次汇总确认的清单，各角色写同一个来源。`user:` 来源与用户答复里不得出现运行者自拟的标记（eval-run、auto、无用户、运行者、预先授权、代填）：
  没人确认、也没有代答授权就停下来问，不自填 `user:`。
- `selected` 候选写 `external_dependencies`（字符串列表，没有写空列表）。不为空时角色还要有：
  - `options`：2–3 个方案，每个 `{name, parts, external_dependencies, cost, pros, cons, recommended}`，
    `parts` 是涉及的型号列表，恰好一个 `recommended: true`，各方案的 `cons` 不能一字不差；
  - `recommendation`：ASG 推荐哪个、为什么，拿到哪些资料后结论会变；
  - `decision` 另写 `option`（用户选的方案名），选定候选的型号必须在该方案的 `parts` 里。

```json
"external_dependencies": ["补偿网络编码表（p13 只给范围）", "阻断管驱动的带载能力与关断时延（p18 只在空载测试）"],
"options": [
  {"name": "控制器 A 单芯片", "parts": ["CTRL-A"], "external_dependencies": ["补偿网络编码表", "阻断管驱动时延"],
   "cost": "器件最少", "pros": "内置环路与驱动", "cons": "关键行为在固件里，要原厂答复", "recommended": false},
  {"name": "控制器 B + 外置环路", "parts": ["CTRL-B", "TL431"], "external_dependencies": [],
   "cost": "增加约 8 个器件，重画一页", "pros": "环路与保护可按公开手册计算", "cons": "器件多、板面积增加", "recommended": true}],
"recommendation": "推荐方案 2：没有外部依赖，环路与保护能按公开资料算清；若原厂能答复编码表和驱动时延，方案 1 更省器件",
"decision": {"option": "控制器 B + 外置环路", "source": "user:2026-10-24"}
```

报告的"核心器件选型"一节由这份记录生成：角色、选定型号、候选数、一句理由、每个淘汰候选的依据（哪条条件不满足，或 `reject_kind`）和确认来源。
有方案的角色另列"外部条件不确定的选型"一节：每个方案的型号、外部依赖、代价、优缺点，ASG 的建议和你的决定。
理由用中文，型号和单位可以保留。
