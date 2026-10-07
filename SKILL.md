---
name: autonomous-schematic-generation
description: >-
  Autonomous-Schematic-Generation (ASG): starting from requirement documents,
  draw readable, electrically correct, natively verified KiCad schematics.
  Requirements → function trace → System_block and pages → exact-MPN pin maps,
  peripheral contracts and calculations → board electrical intent → page scripts
  with pin-geometry drawing recipes and outline rules O1-O8 → one-shot native
  gates (ERC, pin-by-pin netlist against intent, hierarchy, symbol integrity,
  readability, geometry) → render review → handoff to schematic-review. Also
  redraws existing KiCad projects without electrical change, applies authorized
  electrical revisions and extracts PDF reference designs. Self-checks only;
  strict electrical review belongs to schematic-review. Use for .kicad_sch
  generation or redraw, 原理图自动生成、从需求画原理图、画原理图、重画原理图、原理图排版.
---

# Autonomous-Schematic-Generation (ASG)

## 目的与边界

ASG 从需求文档出发，让 Agent 在 KiCad 中画出**可读、电气正确、经原生验证**的原理图。

- **电气正确**：电路来自已确认的需求和确切 MPN 的数据手册，用一份独立写出的板级电气意图表达；
  原生网表必须与意图逐脚一致。
- **可读**：结构由 Agent 按纲要 O1–O8 决定，坐标由 `recipes.Sheet` 按真实引脚几何推出。
- **经原生验证**：以 KiCad 导出的 ERC、XML 网表和 PDF 为准；JSON、脚本成功或 solver 的 `solved` 都不算证据。

ASG 不负责以下事项：

| 事项 | 交给 |
| --- | --- |
| 严格的电气审查：工况、裕量、应力、保护、需求符合性、冻结结论 | `schematic-review` |
| 封装、散热、布局实现 | 《结构与PCB设计要求》交接文档 |
| EasyEDA 出图 | `easyeda-schematic-draw` |
| 生产准出、PCB、SI/PI、EMC | 下游流程 |

## 选择工作流

| 任务 | 做法 |
| --- | --- |
| 从需求做新设计 | 主流程第 0–8 步 |
| 给已有工程新增模块或页面 | 第 0 步只读相关需求，第 2–8 步；改动已有网络时按“电气改版” |
| 重画已有工程，电气不变 | [existing-project-redraw.md](references/existing-project-redraw.md) 冻结基线，再走第 4–8 步 |
| 授权的电气改版 | 先读 [electrical-redesign.md](references/electrical-redesign.md) 和 [change-preflight.md](references/change-preflight.md)，再走主流程 |
| 从 PDF 参考设计提取电路 | [pdf-schematic-extraction.md](references/pdf-schematic-extraction.md)；提取结果只作线索，仍按第 2 步核对手册 |
| 模块化数据、SKiDL/circuit-synth 导入、锁定基线 | [circuit-ir.md](references/circuit-ir.md)。人读的页面仍按第 5 步用 recipes 画 |
| 用户要求 CopperPilot 协助 | [copperpilot-reference-workflow.md](references/copperpilot-reference-workflow.md) |

## 主流程

### 0. 读需求

按 [requirements-to-intent.md](references/requirements-to-intent.md) 第 1–2 节建立需求清单和
功能追溯表。只用已确认的需求，缺口标 OPEN。只问会改变电路方案的问题。

### 1. 架构与分页

第 1 页必须是 `System_block`，画出真实的系统架构、电源与信号流向、板与隔离边界、接口和各页编号；
只有页面索引不算。按功能、隔离/电压域和可读面积分页。
见 [reference-driven-board-design.md](references/reference-driven-board-design.md)。

### 2. 选型、外围合同与计算

- 每个核心器件绑定确切 MPN/封装的物理引脚表、典型应用、必需外围和装配状态，记录实际阅读的手册页码。
  见 [symbol-and-peripheral-contracts.md](references/symbol-and-peripheral-contracts.md)。
- 数值计算按 [calculation-preflight.md](references/calculation-preflight.md) 写明保证条件。
- 原理图阶段 `footprint` 可以留空；散热和机械需求写进交接文档。
- **资料规则**：新下载的器件数据手册存入工程，同时复制到
  `~/Documents/知识库/HardwareWiki/raw/Datasheet/<分类>/<子类>/`，文件名为 `Vendor - PartNumber.pdf`
  （厂商简称按 `raw/Datasheet/VENDORS.yaml`，分类按 `raw/Datasheet/元器件体系/器件统一分类大表.md`，
  无分类放 `ZZ_其他` 并报告）。raw/ 中已有相同哈希或型号时跳过。只复制原文件，不改工程路径，
  也不触发知识库入库。参考设计和评估板手册放 `raw/Designexample/<拓扑>/<板名>/`，
  文件名为 `Vendor - BoardName - Title.pdf`；应用笔记和标准不放 Datasheet 目录。

### 3. 板级电气意图

写一份整板 `electrical-intent.json`：器件、网络 `{name: [ref.pin]}`、`no_connect`，以及每个器件的页面
`fields.Circuit`。格式和规则见 [requirements-to-intent.md](references/requirements-to-intent.md) 第 5 节。
每个物理引脚要么接入网络，要么有依据地标 NC。意图从需求和手册写出，不从候选图回抄。

### 4. 页面方案

为每页写一张简短的方案表，内容包括：读者任务（跟随能量流、看懂反馈、追一个受保护接口……）、
功能块、主路径、rails、出页网络和标签边界。见 [human-readable-routing.md](references/human-readable-routing.md) 第 1 节。

- 按拓扑选结构（Buck、LDO、隔离反激、滤波、MCU 各不相同），见
  [schematic-drawing-standards.md](references/schematic-drawing-standards.md) 第 2 节。不得为别的拓扑编造 SW 节点或电感级。
- 按纲要 O1–O8 决定页面流向、锚点、器件归属、画法、出线、标签、间距和修复顺序，见
  [drawing-recipes.md](references/drawing-recipes.md)。

### 5. 写图页脚本

```python
from schematic_layout.pages import page_intents
from schematic_layout.recipes import Sheet, DOWN, RIGHT, UP, LEFT, add
from schematic_layout.sexpr import dump

RAILS = {"GND": "power:GND", "+3V3": "power:+3V3"}
for n, (key, page) in enumerate(page_intents(board, rails=RAILS).items(), 1):
    s = Sheet(page["intent"], rails=page["rails"], external=page["external"],
              power_ref_start=n * 100 + 1)
    s.place("U201", (101.6, 76.2), pin="3", facing={"3": LEFT})   # 锚点：按引脚朝向定姿
    ...                                                             # series / shunt / bank / divider / label
    root, report = s.build(key)            # 先用 draft=True 出图调试，交付不能是 draft
```

- 先看 `s.plan` 给出的器件角色和网络标签角色。只给锚点写坐标，其余器件用与角色相符的画法从引脚推出。
  有意偏离纲要时用 `s.justify(对象, 理由)` 记录。
- `build()` 遇到硬缺陷会直接报错。`report["structure"]` 必须为 PASS，`report["readability"]["gate"]` 必须为 PASS。
  失败时按 O8 改结构（方向、间隙、顺序 → 锚点 → 拆行）后重建，不得手调坐标打补丁。
- 图页脚本随交付版本一起保存；下一版只重生成有变化的页面。

### 6. 组装与一键验证

多页工程由工程脚本组装根图（层次图框、`System_block`），ASG 不自动写多页层次。之后运行：

```bash
python3 <skill>/scripts/verify_schematic.py <root.kicad_sch> --intent electrical-intent.json \
  --out <新的空目录> [--expected-pages N] [--symbol-exceptions F] [--readability-waivers F] \
  [--reference-contract F] [--baseline-xml B --change-contract C --preflight P]
```

它一次完成：KiCad ERC / XML 网表 / PDF 导出，网表分区与器件身份逐脚对比意图，层次与 PDF 页数，
符号引脚完整性，可读性门禁，以及每个有效页面的几何检查，汇总到 `summary.json`。
只有全部门禁为 PASS 时结果才是 `AUTOMATED_PASS`。

- 新设计要求 ERC 零违规。重画工程时保留基线和最终两份原始 ERC，逐条确认没有新增违规，并披露继承的问题。
- `geometry` 为 INSUFFICIENT 时（例如根页含层次图框），说明该页超出检查器覆盖范围，必须在渲染图上核对。
- 失败时修改相应页面脚本，在新的运行目录重新生成并验证。不得为了降低计数而加 PWR_FLAG、加排除项或改引脚类型。

### 7. 渲染目检

打开导出的 PDF，逐页按方案表追一遍读者任务：主路径、每个支持网络到对应引脚和正确回路、
重复通道、每个回路域和隔离跨越。记录追过的路径和发现的问题；“看过所有页”不算证据。
状态写 待返工（REWORK_REQUIRED）、待目检（REVIEW_PENDING）或 已目检（REVIEWED）。
用户否决会重新打开目检。见 [human-readable-routing.md](references/human-readable-routing.md) 第 4 节。

### 8. 交付与交接

- 按 [execution-evidence.md](references/execution-evidence.md) 写 `delivery-evidence.json`，报告前运行
  `scripts/check_delivery_freshness.py`；任何导出后的修改都会使旧结果作废。
- 交接给 `schematic-review` 的内容：工程文件和哈希、电气意图、需求追溯表、器件合同、计算、OPEN 清单、
  `summary.json` 和目检记录。报告时如实写出 PASS/FAIL/INSUFFICIENT 各项及其数量（含零）。

## ASG 自检与 schematic-review 的分工

| ASG 出图时自检 | 交 schematic-review |
| --- | --- |
| 原生 ERC；网表与意图逐脚一致；器件身份/MPN/字段 | 需求符合性与功能完整性判定 |
| 确切 MPN 引脚表；声明的外围合同（`--reference-contract`） | 工况、裕量、应力、保护和时序的系统审查 |
| 计算预检的条件与门槛 | 全面的最坏情况分析与 FAIL/待核判定 |
| 层次、符号完整性、几何、可读性；渲染目检 | 冻结/放行结论、P0–P3 分级、修改建议 |

需要快速看懂一张已有原理图或 PDF 参考设计时，可以用 [analysis-toolkit.md](references/analysis-toolkit.md)
中的分析器。它们只是辅助，不构成审查结论。

## 硬性规则

- 意图独立于几何：位号、值、MPN、引脚编号、装配状态和网络归属不因摆放改变；不为布图方便改符号的引脚映射。
- 不手写辅助器件坐标；不把可读页面交给 MST/A* 自动路由；不用标签掩盖失败的连线。
- 标签角色：全局标签只用于出页网络；电源轨和回路用 Value 等于网络名的电源符号；隔离的回路不能用通用 GND。
- DNP 器件保留连线和焊盘，它不等于 IC 的 NC 引脚。
- 不得静默拍平已有层次工程；候选图生成在新目录，确认基线未变后才写回原工程。
- `AUTOMATED_PASS` 只代表脚本门禁通过；数据手册审查和渲染目检另行完成。如实报告缺口。

## 参考文件

| 何时读 | 文件 |
| --- | --- |
| 从需求写电气意图 | [requirements-to-intent.md](references/requirements-to-intent.md) |
| 架构页、参考设计外围、学习工程师图面 | [reference-driven-board-design.md](references/reference-driven-board-design.md) |
| 选符号、引脚表、外围合同 | [symbol-and-peripheral-contracts.md](references/symbol-and-peripheral-contracts.md) |
| 计算条件合同 | [calculation-preflight.md](references/calculation-preflight.md) |
| 纲要 O1–O8 与 recipes API | [drawing-recipes.md](references/drawing-recipes.md) |
| 阅读路径、HR-01–HR-11、目检 | [human-readable-routing.md](references/human-readable-routing.md) |
| 拓扑结构、标签策略、验证门禁 | [schematic-drawing-standards.md](references/schematic-drawing-standards.md) |
| 重画已有工程 | [existing-project-redraw.md](references/existing-project-redraw.md) |
| 电气改版与预检 | [electrical-redesign.md](references/electrical-redesign.md)、[change-preflight.md](references/change-preflight.md)、[project-verification.md](references/project-verification.md) |
| 对照工程师模板 | [engineer-template-comparison.md](references/engineer-template-comparison.md) |
| 交付证据与新鲜度 | [execution-evidence.md](references/execution-evidence.md) |
| Circuit IR、低层生成器 | [circuit-ir.md](references/circuit-ir.md)、[schematic-generation.md](references/schematic-generation.md) |
| 发布验证、上游来源、改造记录 | [release-validation.md](references/release-validation.md)、[upstream-integration.md](references/upstream-integration.md)、[improvement-ledger.md](references/improvement-ledger.md) |
| 可选分析器（原理图/PCB/Gerber/PDF 等） | [analysis-toolkit.md](references/analysis-toolkit.md) |

运行不需要上游完整仓库、新的 MCP 服务、Bun 或网络连接。
