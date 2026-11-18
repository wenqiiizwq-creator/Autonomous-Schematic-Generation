---
name: autonomous-schematic-generation
description: >-
  Autonomous-Schematic-Generation (ASG): starting from requirement documents,
  design a board and draw readable, electrically correct KiCad schematics verified
  by KiCad's own exports. Small boards: one designer then one drafter. Larger
  boards: an architect, parallel block designers, a whole-board checker, then the
  drafter. Checks: ERC, netlist comparison, readability, geometry, visual review.
  Can also redraw a given KiCad netlist. Self-checks only; owns
  design feasibility, selection, calculations and functional completion. Use for .kicad_sch
  generation or redraw, 原理图自动生成、从需求画原理图、画原理图、重画原理图、原理图排版.
---

# Autonomous-Schematic-Generation (ASG)

## 目的与边界

ASG 从需求文档出发，让 Agent 在 KiCad 中画出**可读、电气正确、经 KiCad 验证**的原理图。

- **电气正确**：电路来自已确认的需求、关键与特殊器件的数据手册和常规件的规格，用一份独立写出的设计网表表达；
  KiCad 导出网表必须与设计网表逐脚一致。
- **可读**：结构由 Agent 按绘图纲要 决定，坐标由 `recipes.Sheet` 按真实引脚几何推出。
- **经 KiCad 验证**：以 KiCad 导出的 ERC、XML 网表和 PDF 为准；JSON、脚本成功或 solver 的 `solved` 都不算证据。

ASG 负责需求到电路的方案可行性、选型依据、设计计算和功能实现，不能把未做完的设计留给别人：
工程上做得完的做完，只有真实的外部依赖和后续环节才能验证的事写进设计报告的“未核实与待验证”。

以下验收与独立复核不由 ASG 负责：

| 事项 | 交给 |
| --- | --- |
| 独立的电气审查和设计定型结论 | 由审查方给出；ASG 只做自检，收到的审查意见按“选择工作流”改版 |
| PCB封装库、焊盘/孔/钢网、布局布线、DFM与散热实现 | 实现由 PCB、结构负责；原理图阶段定下的边界（热阻目标、铜面积、爬电间隙、走线载流等）写进设计报告的“交给后续环节的约束”交出 |
| 生产放行、PCB、SI/PI、EMC | 后续环节 |

## ASG 纲要（核心标准）

本节是 ASG 的核心标准。其余章节、`references/` 和 `scripts/` 都是它的展开与实现，不得与之冲突。

### 能力目标

ASG 的输入是一块板卡的设计需求，输出是设计方案确定后的电路原理图。ASG 的能力是把电路设计得合理，把图画清楚，并能发现自己知识不够的地方加以改进。架构、核心原则和主流程都为这些能力服务。

**合理**指同时做到下面五条，不以经济成本为准：

- **充分**：稳态、瞬态、上下电、故障和极限环境下，都满足需求和器件的保证条件。
- **必要**：每个器件、每一级、每档裕量都有来由。去掉它或取小一档后其余四条仍然成立的，就是过度设计。
- **匹配**：方案适合它的工况，不用在适用范围的边缘；器件之间、块之间相互适配。
- **稳健**：对容差、温度、老化和单一故障有确定的表现；保护两侧都成立，不误动，也真能保护。
- **有据**：每个决定的依据是需求、手册保证值或计算，不是印象或典型值。

能力分七项：

1. **把设计问题定准**：需求里的工况是完整的，输入范围、负载、环境、接口对端和故障情形都有数或已澄清。能看出哪个缺失的条件会改变方案或取值，并把它问清。
2. **整板结构合理**：每条需求落到确定的功能块；电源树的级数和各级电压有来由；隔离和电压域的边界放在需求要求的位置；块与块之间用少数几个参数就能说清；一个块的故障不会无保护地传到别的块。
3. **功能电路选得合适**：选定方案的适用范围覆盖本板工况；都能满足的候选里选结构最简单、依赖最少的，选更复杂的要有需求、标准或手册上的理由；核心器件靠保证值覆盖决定条件。
4. **电路实现正确且有度**：外围电路按手册的应用条件接全，每个引脚有着落；取值按最坏情况算出，应力在降额之内；裕量够用，不无故取高；环路、启动和关断成立。
5. **异常工况与全板配合成立**：过压、过流、反接、短路、掉电和热插拔下电路的表现是确定的；保护门槛两侧都成立，上下级保护有先后；跨块的电平、时序、电源预算、复位和故障传递相互适配；对外端口的防护与它面对的环境相称。
6. **图面清晰易读**：模块清晰，图形连接明确，读图的人能沿功能路径看懂电路。按 P4 和绘图纲要 画出并审阅。
7. **知道自己哪里知识不够**：设计中遇到库里没有、依据不足的地方，如实写进设计报告的“未核实与待验证”，不用印象补上。

评测 ASG 用整板题目：从需求做到交付，由独立审查判定。判定按合理性五条：充分不成立的算不通过，稳健不足的算风险，必要不成立的算过度设计、单独计数。
评测体系在本技能之外，题目、基线和现状以与知识框架并列的 `硬件设计评测/` 目录为准，本技能不记它的状态。

### 架构

ASG 按板子规模分两种做法，计算和依据都写在设计报告里，细则见 [快速设计](references/quick-design.md)：

- **快速设计**（器件不多的板，预计不超过约 40 个位号）：一位设计者在一个上下文里从需求做到设计网表和设计报告，一位绘图者画图并跑 KiCad 的自动检查。
- **分块设计**（器件多的板）：一位架构师定板级方案，各功能块的设计者并行做，一位整板核对者合并各块、按每种供电方式走查并做减法，绘图者画图；不设接口定稿，不逐级回退。

工作流 `workflows/asg-design.js` 按规模自动选（`mode` 可指定）。

- **输入**：需求、器件知识库、知识框架（`知识/`，含典型电路）；只给网表重画时是 KiCad 网表
- **支撑**：KiCad CLI（唯一证据来源）、`schematic_layout`（布图与检查）、`references/`（规则与知识）

工程判据（设计准则与降额）和其余设计知识都直接读本机的硬件设计知识框架，只读不改；框架位置由环境变量 `HARDWARE_KNOWLEDGE_FRAMEWORK` 或技能根目录的 `.knowledge-framework` 指定，
查什么见[知识框架的用法](references/knowledge-package.md)。原厂资料（数据手册、应用笔记、参考设计、标准）在原件总库：知识框架里的 `原件/`。

由来：2026-11-17 以前 ASG 按六个能力模块（C1–C6）分别留记录、过关卡。H-001 小板和 M-001 中型板（2026-11-16、17）上它用时是直接设计的 3 到 12 倍，
回退多数是记录之间的账面不一致，交出的设计经独立审查问题并不更少，所以删去；要用它出旧板的图，检出标签 `last-with-six-modules`。

独立审查（schematic-review 技能或其他审查方）在设计输出之后，不属于 ASG。

### 核心原则

- **P1 证据**：只认 KiCad 导出的 ERC、XML 网表和 PDF；JSON、脚本成功都不算证据。
- **P2 电气与几何分离**：设计网表从需求和手册独立写出，不从图上回抄；摆放不改变电气。
- **P3 真值**：器件先形成与实际工况对应的性能要求；需绑定型号的器件以确切料号或定制设计单为依据，可按规格采购的器件以算得的性能要求为依据。性能定义与候选器件符合性的核实状态分别记录，料号不能替代性能核验。
- **P4 可读**：页面结构按绘图纲要 决定，坐标从引脚几何推出；可读性是交付标准。
- **P5 失败改结构，不改计数**：不靠 PWR_FLAG、豁免、改引脚类型或标签来掩盖问题。
- **P6 责任边界**：设计完成由 ASG 负责，只做自检；独立审查交给独立审查方（schematic-review 技能）。

### 纲要的修改

纲要只有本节。本节的任何增、删、改或重排，都须先把改动草案交给人确认后才能写入。
绘图纲要和 `scripts/`、`references/` 里的其余内容都是本节的展开，可以直接修改；一旦与本节冲突，就先写纲要草案交人确认。
经确认的改动在 `docs/outline-approvals.md` 加一条，写确认日期、用户原话和改后纲要哈希
（`python3 scripts/check_ledger.py --outline-hash` 输出当前哈希）；纲要文字与最新确认的哈希不一致时 `check_ledger.py` 报 FAIL。

## 选择工作流

| 任务 | 做法 |
| --- | --- |
| 从需求做新设计 | 按规模走快速设计或分块设计（[quick-design.md](references/quick-design.md)） |
| 重画已有工程，电气不变 | 用 `import_netlist.py` 把工程网表导成设计网表，再由绘图者画（见 [modules.md](references/modules.md)） |
| 修改本技能做出的设计（含改值）、收到审查意见 | 一位设计者逐条处置：改设计网表（分块设计的板改有关的块文件再合并）和设计报告，写明每条怎么改的或为什么不改；绘图者重画并重跑自动检查 |

无人当场答复时，读 [任务书格式](references/workflow-handoff.md)：任务书只给答复和授权；设计、查资料、计算与改图仍由 ASG 完成。

## 硬性规则

原则见「ASG 纲要」的核心原则；这里只列具体操作约束。

- P2：位号、值、MPN、引脚号、装配状态和网络归属不因摆放改变；不为布图方便改符号的引脚映射。
- P4/P5：不手写辅助器件坐标；不把可读页面交给 MST/A* 自动路由；不用标签掩盖失败的连线。
- 标签角色：全局标签只用于出页网络；电源轨和地网络用 Value 等于网络名的电源符号；隔离的地网络不能用通用 GND。
- DNP 器件保留连线和焊盘，它不等于 IC 的 NC 引脚。
- 不得静默拍平已有层次工程；草稿图生成在新目录，确认基线未变后才写回原工程。交付目录的 `设计方案/` 里可能有 PCB 环节的板子文件，重画时只替换原理图文件，不清空目录。
- P1：`AUTOMATED_PASS` 只代表脚本自动检查通过；数据手册审查和图面审阅另行完成。如实报告缺口。
- 给人看的文字一律用中文；器件型号、单位和缩写（PFC、OVP）可以保留。
- 技能文档与报告用 [术语对照](references/terminology.md) 的统一用词。

## 参考文件

| 何时读 | 文件 |
| --- | --- |
| 设计者、架构师、块设计者、整板核对者、绘图者各做什么，设计报告和交付目录 | [quick-design.md](references/quick-design.md) |
| 画图：分页、图页脚本、组装工程、自动检查、图面审阅 | [module-c6-schematic.md](references/module-c6-schematic.md) |
| `architecture.json`、块设计与合并（`blocks.py`）、只给网表重画（`import_netlist.py`） | [modules.md](references/modules.md) |
| 设计网表怎么写 | [requirements-to-intent.md](references/requirements-to-intent.md) |
| 需求没说清：问什么、什么时候问、答复怎样记 | [requirement-clarifications.md](references/requirement-clarifications.md) |
| 无人当场答复时的任务书 | [workflow-handoff.md](references/workflow-handoff.md) |
| 架构页、参考设计外围 | [reference-driven-board-design.md](references/reference-driven-board-design.md) |
| 核心器件从哪找候选、怎么比较 | [core-part-selection.md](references/core-part-selection.md) |
| 每类器件干什么、选它看什么参数（按知识库分类） | [part-roles.md](references/part-roles.md) |
| 知识框架的用法：设计时查哪部分、典型电路、框架位置怎么配 | [knowledge-package.md](references/knowledge-package.md) |
| 选符号、引脚表、外围电路要求 | [symbol-and-peripheral-contracts.md](references/symbol-and-peripheral-contracts.md) |
| 没有电源输出脚的分立供电电路怎样声明 | [reviewed-circuit-supply.md](references/reviewed-circuit-supply.md) |
| KiCad 导出几何的范围 | [native-geometry.md](references/native-geometry.md) |
| 非线性极值、条件匹配与插值边界 | [worst-case-bounds.md](references/worst-case-bounds.md) |
| 设计准则（G01–G09）：适用条件、引用与覆盖 | 框架 `知识/设计准则/工具/包说明/guideline-criteria.md`、`知识/设计准则/准则登记/` |
| 降额与应力规范：I/II/III 级降额值、等级从哪来、应力怎么判 | 框架 `知识/设计准则/降额与应力/` 下的 `应力判法.md`、`降额规范.md`、`降额值.json` |
| 绘图纲要（结构规则与画图习惯）与 recipes API | [drawing-recipes.md](references/drawing-recipes.md) |
| 阅读路径、HR 规则、图面审阅 | [human-readable-routing.md](references/human-readable-routing.md) |
| 拓扑结构、标签策略、检查项 | [schematic-drawing-standards.md](references/schematic-drawing-standards.md) |
| ERC 摘要对应到对象、自动网络名不比对、层次与 PDF | [project-verification.md](references/project-verification.md) |
| 用词 | [terminology.md](references/terminology.md) |
| 低层生成器 | [schematic-generation.md](references/schematic-generation.md) |

运行依赖见 [README.md](README.md) 的“安装”一节。
