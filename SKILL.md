---
name: autonomous-schematic-generation
description: >-
  Autonomous-Schematic-Generation (ASG): starting from requirement documents,
  draw readable, electrically correct KiCad schematics verified by KiCad's own
  exports. Six capability modules, run in sequence or one at a time with given
  inputs: C1 requirements and clarification → C2 board architecture → C3 block
  circuit, core-part selection and interface freeze → C4 detailed design, calculations and part
  selection → C5 whole-board closure and design netlist → C6 schematic drawing
  and checks (ERC, netlist, readability, geometry, visual review); then the
  generated report and fixed delivery folder.
  C6 alone redraws a given KiCad netlist. Self-checks only; owns
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

ASG 负责需求到电路的方案可行性、选型依据、设计计算和功能实现，不能把未做完的设计留给别人。
设计遵循 [设计待办记录](references/design-closure.md)，区分工程可完成、真实外部依赖和后续环节验证；
审计列出的可执行设计动作须继续完成，不能把缺口清单当成结束条件。

以下验收与独立复核不由 ASG 负责：

| 事项 | 交给 |
| --- | --- |
| 独立的电气审查和设计定型结论 | 由审查方给出；ASG 只做自检，收到的审查意见按 P7 回到负责的模块重做 |
| PCB封装库、焊盘/孔/钢网、布局布线、DFM与散热实现 | 实现由 PCB、结构负责；原理图阶段定下的边界（热阻目标、铜面积、爬电间隙、走线载流等）写进《下游约束表》交出 |
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

1. **把设计问题定准**（C1）：需求里的工况是完整的，输入范围、负载、环境、接口对端和故障情形都有数或已澄清。能看出哪个缺失的条件会改变方案或取值，并把它问清。
2. **整板结构合理**（C2）：每条需求落到确定的功能块；电源树的级数和各级电压有来由；隔离和电压域的边界放在需求要求的位置；块与块之间用少数几个参数就能说清；一个块的故障不会无保护地传到别的块。
3. **功能电路选得合适**（C3）：选定方案的适用范围覆盖本板工况；都能满足的候选里选结构最简单、依赖最少的，选更复杂的要有需求、标准或手册上的理由；核心器件靠保证值覆盖决定条件；按核心器件的端口限值把块与块之间的接口参数定下来，各块据此能独立设计。
4. **电路实现正确且有度**（C4）：外围电路按手册的应用条件接全，每个引脚有着落；取值按最坏情况算出，应力在降额之内；裕量够用，不无故取高；环路、启动和关断成立。
5. **异常工况与全板配合成立**（C4 管块内，C5 管跨块）：过压、过流、反接、短路、掉电和热插拔下电路的表现是确定的；保护门槛两侧都成立，上下级保护有先后；跨块的电平、时序、电源预算、复位和故障传递相互适配；对外端口的防护与它面对的环境相称。
6. **图面清晰易读**（C6）：模块清晰，图形连接明确，读图的人能沿功能路径看懂电路。按 P4 和绘图纲要 画出并审阅。
7. **知道自己哪里知识不够，并据此改进**：设计中遇到库里没有、依据不足或回到上游重做的地方，如实留下记号，不用印象补上。每次运行由工具从各模块的产品里抽出知识缺口清单；跨多次运行和评测，把重复出现的缺口归纳成能力缺陷，改进后用题目验证。

评测 ASG 按能力模块分别进行：每个模块用标准上游作给定输入单独评测；从需求串联到交付的整板运行作集成测试。判定按合理性五条：充分不成立的算不通过，稳健不足的算风险，必要不成立的算过度设计、单独计数。
能力缺陷的归纳和改进在评测侧做，不在单次设计里做。每条缺陷带一道能稳定暴露它的题目；改进之后这道题通过、留出的题目没有变差，才算修好。评测体系在本技能之外，题目、基线和现状以与知识框架并列的 `硬件设计评测/` 目录为准，本技能不记它的状态。

### 架构

ASG 的**设计能力框架**由六个能力模块（C1–C6）组成，与硬件设计知识框架对应：知识框架管知道什么，能力框架管会做什么，每个能力模块查知识框架的指定组件。能力七项中第 5 项由 C4、C5 分担，第 7 项不归某个模块，所以能力框架指这六个模块，不等于七项能力。每个模块是主流程中连续的几项任务，有固定的给定输入、产出和关卡，可以单独运行，也可以串联。
主流程按 C1→C6 排列，串起来就是从需求做新设计的默认编排。先弄清本次从哪个模块进、跑到哪个模块（见“选择工作流”），再按“主流程”逐项任务做，每项任务做到“做完的标志”为止；一个模块各项任务的做完标志合起来就是它的关卡（`check_module.py`）。

- **输入**：需求、器件知识库、知识框架（`知识/`，含典型电路）；单独运行时的给定输入
- **支撑**：KiCad CLI（唯一证据来源）、`schematic_layout`（布图与检查）、`references/`（规则与知识）

工程判据（设计准则与降额）和其余设计知识都直接读本机的硬件设计知识框架；准则由 `guideline_criteria.py` 从框架的准则登记汇编，降额值、常规件最弱档、词表也从框架读，路径见[知识框架的用法](references/knowledge-package.md)。运行和本地测试不读取 SR 源码。
准则以外的知识（需求要素、板级架构模式、接口约定、典型电路、计算方法、器件参数、器件类别、失效与故障分析）读框架 `知识/` 下的同名目录；框架位置由环境变量 `HARDWARE_KNOWLEDGE_FRAMEWORK` 或技能根目录的 `.knowledge-framework` 指定，脚本经 `knowledge_source.py` 定位，只读不改。交付物记读取日期。各模块查哪部分见[知识框架的用法](references/knowledge-package.md)。
查阅时先用 `check_module.py entries <设计目录>` 按本板的电路类型、器件类别（`guideline_scope`）列出知识框架里声明了它们的条目（条目头部的 `电路类型：`、`器件类别：`），再按需读；C1、C3、C4 的关卡把声明了本板类型、查阅记录里却没有的条目列为提示（不判失败），读过不适用的也记一条并写理由。
原厂资料（数据手册、应用笔记、参考设计、标准）在原件总库：知识框架里的 `原件/`（它指向 HardwareWiki/raw），脚本经 `knowledge_source.raw_root()` 找，不另设位置。
C1–C5 每次查知识框架后用 `check_module.py lookup` 记一条：哪项任务、哪个组件、查的什么、查到哪些条目，没查到也记；写进 `record/modules.json` 的 `knowledge_lookups`。这五个模块的关卡核对每个该查的组件都有记录、所记条目在知识框架里，不判查得对不对。任务 C3.1 选了哪个典型电路的哪种方案另记在方案记录里。
用到的条目里的每一项都要回答，写进 `record/knowledge-checklist.json`（必答清单，`knowledge_checklist.py build` 从条目里抽，不手抄）：C1 查到的需求要素条目的每个条件，C4 各块选定实现方案的必算项、必需外围、已知坑和查到的计算方法条目的取值步骤、算完核对，逐项写落实在哪（需求或澄清编号、计算编号、位号、怎样避开）或不适用及理由；C1、C4 的关卡核对没有漏项、落实处指向的记录存在。见[知识框架的用法](references/knowledge-package.md)的“必答清单”。

| 模块 | 任务 | 给定输入 | 产出 |
|---|---|---|---|
| C1 需求理解与澄清 | C1.1 | 需求文件；任务书里的澄清答复与代答授权 | `requirements.json`：需求条文与来源、需求澄清、降额等级、准则范围；`knowledge-checklist.json` 的 C1 部分 |
| C2 板级方案 | C2.1 | C1 的产出 | `architecture.json`：功能块、电压域、电源树、隔离边界、跨块流向（接口参数预算）、对外接口和各块的块规格 |
| C3 块电路选择与接口定稿 | C3.1 · C3.2 · C3.3 | `architecture.json`（块规格与跨块流向） | 每块一个 `block-circuits/<块>.json`；`interfaces.json`：每条跨块流向定稿的接口参数；工作记录 `scheme-criteria.json`、`selection.json` |
| C4 详细设计与器件选型（每块一次） | C4.1 · C4.2 · C4.3 · C4.4 | 块规格、`interfaces.json` 中与本块相连的流向、`block-circuits/<块>.json` | 每块一个块设计 `blocks/<块>.json`；工作记录 `reference-input.json`、计算记录、`component-requirements.json`、`knowledge-checklist.json` 的 C4 部分 |
| C5 全板闭合 | C5.1 · C5.2 | `architecture.json`、`interfaces.json`、各块的块设计 | `electrical-intent.json`、整板层块 `blocks/BOARD.json`、需求追溯、闭合矩阵、FMEA 与 EMC 端口矩阵 |
| C6 原理图绘制 | C6.1–C6.5 | 设计网表；串联运行时另读 `architecture.json` 与各块的 `block-circuits/<块>.json`；单独运行时只给网表 | `page-plan.json`、KiCad 工程、`summary.json`、`visual-review.json` |

交付（设计完成核对、报告与打包）是编排的收尾，负责汇总各模块状态并打包，不是能力模块。

**快速设计与分块设计（默认的做法）。** 不按六个模块分别留记录和过关卡，计算和依据写在设计报告里，见 [快速设计](references/quick-design.md)：
- 器件不多的板（预计不超过约 40 个位号）：一位设计者在一个上下文里从需求做到设计网表和设计报告，一位绘图者画图并跑 KiCad 的自动检查。
- 器件多的板：一位架构师定板级方案，各功能块的设计者并行做，一位整板核对者合并各块、按每种供电方式走查并做减法，绘图者画图；不设接口定稿，不逐级回退。

能力目标和核心原则不变，知识框架照查。工作流 `workflows/asg-design.js` 按规模自动选（`mode` 可指定）。
上面的六个模块及其记录和关卡只在用户点名要它时才走（`mode: full`）：H-001 小板和 M-001 中型板（2026-11-16、17）上它用时是直接设计的 3 到 12 倍，
回退多数是记录之间的账面不一致，交出的设计经独立审查问题并不更少。

独立审查（schematic-review 技能或其他审查方）在设计输出之后，不属于 ASG。

### 核心原则

- **P1 证据**：只认 KiCad 导出的 ERC、XML 网表和 PDF；JSON、脚本成功都不算证据。
- **P2 电气与几何分离**：设计网表从需求和手册独立写出，不从图上回抄；摆放不改变电气。
- **P3 真值**：器件先形成与实际工况对应的性能要求；需绑定型号的器件以确切料号或定制设计单为依据，可按规格采购的器件以算得的性能要求为依据。性能定义与候选器件符合性的核实状态分别记录，料号不能替代性能核验。
- **P4 可读**：页面结构按绘图纲要 决定，坐标从引脚几何推出；可读性是交付标准。
- **P5 失败改结构，不改计数**：不靠 PWR_FLAG、豁免、改引脚类型或标签来掩盖问题。
- **P6 责任边界**：设计完成由 ASG 负责，只做自检；独立审查交给独立审查方（schematic-review 技能）。
- **P7 模块契约**：单独运行时，给定输入只读，并带 SHA-256。产出按契约写；关卡（做完的标志）过了才交下游，并在 `record/modules.json` 记下上游与产出的指纹；上游一变，下游即过期。发现给定输入有问题时，只登记 `INPUT` 待办，不改上游；串联运行时回到上游模块重做，并在 `record/modules.json` 的 `returns` 记一条：哪个模块的哪项任务发现、回到哪个模块的哪项任务、原因和依据。

### 纲要的修改

纲要只有本节。本节的任何增、删、改或重排，都须先把改动草案交给人确认后才能写入。
主流程的模块表、`references/module-*.md` 七个细则文件、绘图纲要和 `scripts/`、`references/` 里的其余内容都是本节的展开，可以直接修改；一旦与本节冲突，就先写纲要草案交人确认。
经确认的改动在 `docs/outline-approvals.md` 加一条，写确认日期、用户原话和改后纲要哈希
（`python3 scripts/check_ledger.py --outline-hash` 输出当前哈希）；纲要文字与最新确认的哈希不一致时 `check_ledger.py` 报 FAIL。

## 选择工作流

| 任务 | 编排 |
| --- | --- |
| 从需求做新设计 | C1 → C6，再交付 |
| 单独运行某个模块（评测或分工） | 按 [任务书](references/workflow-handoff.md) 的 `modules` 给定上游，只跑指定模块，交模块报告 |
| 重画已有工程，电气不变 | 单独运行 C6：用 `import_netlist.py` 把工程网表导成设计网表（见 [modules.md](references/modules.md)） |
| 修改本技能做出的设计（含改值） | 从受影响的最上游模块重做，下游按 `modules.json` 指纹重跑 |
| 收到审查意见 | 每条意见找到负责的模块，按 P7 从该模块重做并写明原因，重过关卡，下游按指纹重跑 |

## 主流程

主流程按六个能力模块排列。每个模块先写给定输入和产出，下面逐项任务做到“做完的标志”为止；最后一节“交付”是编排的收尾。

做某个模块前读本文件和该模块的细则文件（下表最后一列）。

| 模块 | 做什么 | 给定输入 → 产出 | 关卡 | 细则 |
|---|---|---|---|---|
| C1 需求理解与澄清 | 建需求清单，问清会改变方案或取值的缺口，定降额等级与准则范围 | 需求文件、任务书的澄清答复与代答授权 → `requirements.json`、必答清单 C1 部分 | `check_module.py C1 <设计目录>` | [module-c1-requirements.md](references/module-c1-requirements.md) |
| C2 板级方案 | 定功能块、电压域、电源树、隔离边界和跨块流向，写各块的块规格 | C1 的产出 → `architecture.json` | `check_module.py C2 <设计目录>` | [module-c2-architecture.md](references/module-c2-architecture.md) |
| C3 块电路选择与接口定稿 | 选各块实现方案与核心器件，经确认后抽出块文件，按端口限值定稿接口参数 | `architecture.json` → `block-circuits/<块>.json`、`interfaces.json`（工作记录 `scheme-criteria.json`、`selection.json`） | `check_scheme_criteria.py <设计目录>`；`check_module.py C3 <设计目录>` | [module-c3-block-circuits.md](references/module-c3-block-circuits.md) |
| C4 详细设计与器件选型（每块一次） | 核手册与外围电路，按最坏情况计算并核降额，定器件性能要求与选型，写块设计 | 块规格、`interfaces.json` 中本块的流向、`block-circuits/<块>.json` → `blocks/<块>.json`（工作记录 `reference-input.json`、计算记录、`component-requirements.json`） | `check_module.py C4 <设计目录> [--block <块>]` | [module-c4-detailed-design.md](references/module-c4-detailed-design.md) |
| C5 全板闭合 | 合并整板设计网表，写需求追溯，按整板审计核对全板 | `architecture.json`、`interfaces.json`、各块的块设计 → `electrical-intent.json`、`blocks/BOARD.json`、需求追溯、闭合矩阵、FMEA 与 EMC 端口矩阵 | `check_module.py C5 <设计目录>` | [module-c5-board-closure.md](references/module-c5-board-closure.md) |
| C6 原理图绘制 | 分页、写图页脚本、组装工程、自动检查、图面审阅 | 设计网表（串联运行时另读 `architecture.json` 与块文件）→ `page-plan.json`、KiCad 工程、`summary.json`、`visual-review.json` | `verify_schematic.py`；`check_module.py C6 <设计目录>` | [module-c6-schematic.md](references/module-c6-schematic.md) |
| 交付 | 设计完成核对，生成报告并打包 | 各模块的产出 → 固定交付目录 | `deliver.py <交付目录>`（打包 `pack_design.py`） | [module-delivery.md](references/module-delivery.md) |

## 带任务书运行

单独运行部分模块、或无人当场答复时，读 [任务书格式](references/workflow-handoff.md)。
任务书只给定输入、答复和授权；设计、查资料、计算与改图仍由 ASG 完成，交付仍按「交付」一节（[module-delivery.md](references/module-delivery.md)）“报告与打包”规定的目录。

## 硬性规则

原则见「ASG 纲要」的核心原则；这里只列具体操作约束。

- P2：位号、值、MPN、引脚号、装配状态和网络归属不因摆放改变；不为布图方便改符号的引脚映射。
- P4/P5：不手写辅助器件坐标；不把可读页面交给 MST/A* 自动路由；不用标签掩盖失败的连线。
- 标签角色：全局标签只用于出页网络；电源轨和地网络用 Value 等于网络名的电源符号；隔离的地网络不能用通用 GND。
- DNP 器件保留连线和焊盘，它不等于 IC 的 NC 引脚。
- 不得静默拍平已有层次工程；草稿图生成在新目录，确认基线未变后才写回原工程。
- P1：`AUTOMATED_PASS` 只代表脚本自动检查通过；数据手册审查和图面审阅另行完成。如实报告缺口。
- 给人看的文字一律用中文：`design-closure.json` 的假设、没算进去的项、核对项名称、待办、实现说明和 notes 都会原样进报告；
  器件型号、单位和缩写（PFC、OVP）可以保留。计算脚本里写的说明也按此写。`render_design_report.py` 发现英文句子会报问题。
- 技能文档与报告用 [术语对照](references/terminology.md) 的统一用词。

## 参考文件

| 何时读 | 文件 |
| --- | --- |
| 做某个模块或交付：该模块的任务与做完的标志 | [C1](references/module-c1-requirements.md)、[C2](references/module-c2-architecture.md)、[C3](references/module-c3-block-circuits.md)、[C4](references/module-c4-detailed-design.md)、[C5](references/module-c5-board-closure.md)、[C6](references/module-c6-schematic.md)、[交付](references/module-delivery.md) |
| 能力模块的关卡、`architecture.json`、接口定稿 `interfaces.json`、块设计与合并（`blocks.py`）、`modules.json` 与过期判定（`check_module.py`）；单独运行模块、只给网表画图（`import_netlist.py`） | [modules.md](references/modules.md) |
| 设计待办记录、依赖与计算结论审计 | [design-closure.md](references/design-closure.md) |
| 交付目录、设计报告、打包检查 | [delivery-report.md](references/delivery-report.md) |
| 从需求写设计网表 | [requirements-to-intent.md](references/requirements-to-intent.md) |
| 需求没说清：问什么、什么时候问、答复怎样写回需求清单 | [requirement-clarifications.md](references/requirement-clarifications.md) |
| 架构页、参考设计外围 | [reference-driven-board-design.md](references/reference-driven-board-design.md) |
| 核心器件从哪找候选、怎么比较、`selection.json` | [core-part-selection.md](references/core-part-selection.md) |
| 每类器件干什么、选它看什么参数（按知识库分类） | [part-roles.md](references/part-roles.md) |
| 知识框架的用法：需求要素、板级架构模式、接口约定、典型电路（一个功能有几种实现方案、各自的必算项与已知坑）、计算方法、器件参数、失效与故障分析；各模块查哪部分、典型电路标注与 `scheme-criteria.json` 格式、框架位置怎么配 | [knowledge-package.md](references/knowledge-package.md) |
| 选符号、引脚表、外围电路要求 | [symbol-and-peripheral-contracts.md](references/symbol-and-peripheral-contracts.md) |
| 计算条件记录 | [calculation-preflight.md](references/calculation-preflight.md) |
| 器件性能要求、BOM 与图面标注 | [component-requirements.md](references/component-requirements.md) |
| KiCad 导出几何的范围 | [native-geometry.md](references/native-geometry.md) |
| 非线性极值、条件匹配与插值边界 | [worst-case-bounds.md](references/worst-case-bounds.md) |
| 设计准则（G01–G09）：适用条件、引用与覆盖、下游约束 | 框架 `知识/设计准则/工具/包说明/guideline-criteria.md`、`知识/设计准则/准则登记/` |
| 必写的设计文档（FMEA、EMC 端口矩阵）：何时要写、必备章节与对象 | [guideline-evidence-groups.md](references/guideline-evidence-groups.md)、`references/guideline-evidence-groups.json` |
| 设计准则、降额数据和词表在框架里的位置、各文件的字段 | 框架 `知识/设计准则/工具/包说明/shared-layer.md` |
| 降额规范 降额与应力规范（G01–G09 设计准则之外的第十份，不进准则登记）：I/II/III 级降额值、等级从哪来、取值规则、应力怎么判、查到什么程度 | 框架 `知识/设计准则/降额与应力/` 下的 `应力判法.md`、`降额规范.md`、`降额值.json` |
| 绘图纲要（结构规则与画图习惯）与 recipes API | [drawing-recipes.md](references/drawing-recipes.md) |
| 阅读路径、HR 规则、图面审阅 | [human-readable-routing.md](references/human-readable-routing.md) |
| 拓扑结构、标签策略、检查项 | [schematic-drawing-standards.md](references/schematic-drawing-standards.md) |
| ERC 摘要对应到对象、自动网络名不比对、层次与 PDF | [project-verification.md](references/project-verification.md) |
| 交付证据与是否最新 | [delivery-report.md](references/delivery-report.md) 的“交付证据（快照检查）” |
| 用词 | [terminology.md](references/terminology.md) |
| 低层生成器 | [schematic-generation.md](references/schematic-generation.md) |

运行依赖见 [README.md](README.md) 的“安装”一节。
