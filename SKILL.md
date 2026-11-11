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
| PCB封装库、焊盘/孔/钢网、布局布线、DFM与散热实现 | `pcb` 阶段技术转交待办；需求要求时另写《PCB与结构要求》 |
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
能力缺陷的归纳和改进在评测侧做，不在单次设计里做。每条缺陷带一道能稳定暴露它的题目；改进之后这道题通过、留出的题目没有变差，才算修好。评测体系在本技能之外，题目、基线和现状以硬件设计知识框架的 `评测/` 为准，本技能不记它的状态。

### 架构

ASG 的**设计能力框架**由六个能力模块（C1–C6）组成，与硬件设计知识框架对应：知识框架管知道什么，能力框架管会做什么，每个能力模块查知识包的指定组件。能力七项中第 5 项由 C4、C5 分担，第 7 项不归某个模块，所以能力框架指这六个模块，不等于七项能力。每个模块是主流程中连续的几项任务，有固定的给定输入、产出和关卡，可以单独运行，也可以串联。
主流程按 C1→C6 排列，串起来就是从需求做新设计的默认编排。先弄清本次从哪个模块进、跑到哪个模块（见“选择工作流”），再按“主流程”逐项任务做，每项任务做到“做完的标志”为止；一个模块各项任务的做完标志合起来就是它的关卡（`check_module.py`）。

- **输入**：需求、器件知识库、知识包（`references/knowledge/`，含典型电路）；单独运行时的给定输入
- **支撑**：KiCad CLI（唯一证据来源）、`schematic_layout`（布图与检查）、`references/`（规则与知识）

共用工程判据由硬件设计规范发布，ASG 使用本技能中已安装并固定版本的发布包；准则版本与共用层指纹由发布包读取。运行和本地测试不读取 SR 源码。
计划/审计记录采用的共用层版本、指纹及指纹格式；版本或工程身份变化按规定重验，维护历史不属于工程身份。
准则以外的知识（需求要素、板级架构模式、接口约定、典型电路、计算方法、器件参数、失效与异常工况）由硬件设计知识框架以固定知识包发布，装在 `references/knowledge/`，版本与指纹由 `knowledge-release.json` 读取；运行不读知识框架目录。各模块查哪部分见[知识包](references/knowledge-package.md)。
C1–C5 每次查知识包后用 `check_module.py lookup` 记一条：哪项任务、哪个组件、查的什么、查到哪些条目，没查到也记；写进 `record/modules.json` 的 `knowledge_lookups`。这五个模块的关卡核对每个该查的组件都有记录、所记条目在知识包里，不判查得对不对。任务 C3.1 选了哪个典型电路的哪种方案另记在方案记录里。

| 模块 | 任务 | 给定输入 | 产出 |
|---|---|---|---|
| C1 需求理解与澄清 | C1.1 | 需求文件；任务书里的澄清答复与代答授权 | `requirements.json`：需求条文与来源、需求澄清、降额等级、准则范围 |
| C2 板级方案 | C2.1 | C1 的产出 | `architecture.json`：功能块、电压域、电源树、隔离边界、跨块流向（接口参数预算）、对外接口和各块的块规格 |
| C3 块电路选择与接口定稿 | C3.1 · C3.2 · C3.3 | `architecture.json`（块规格与跨块流向） | 每块一个 `block-circuits/<块>.json`；`interfaces.json`：每条跨块流向定稿的接口参数；工作记录 `scheme-criteria.json`、`selection.json` |
| C4 详细设计与器件选型（每块一次） | C4.1 · C4.2 · C4.3 · C4.4 | 块规格、`interfaces.json` 中与本块相连的流向、`block-circuits/<块>.json` | 每块一个块设计 `blocks/<块>.json`；工作记录 `reference-input.json`、计算记录、`component-requirements.json` |
| C5 全板闭合 | C5.1 · C5.2 | `architecture.json`、`interfaces.json`、各块的块设计 | `electrical-intent.json`、整板层块 `blocks/BOARD.json`、需求追溯、闭合矩阵、FMEA 与 EMC 端口矩阵 |
| C6 原理图绘制 | C6.1–C6.5 | 设计网表；串联运行时另读 `architecture.json` 与各块的 `block-circuits/<块>.json`；单独运行时只给网表 | `page-plan.json`、KiCad 工程、`summary.json`、`visual-review.json` |

交付（设计完成核对、报告与打包）是编排的收尾，负责汇总各模块状态并打包，不是能力模块。

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

本节（架构、核心原则）、主流程的步骤、任务与做完的标志，以及绘图纲要的每一条，任何增、删、改或重排，都须先把改动草案交给人确认后才能写入。
`scripts/` 和 `references/` 中的实现细节可以直接修改，但一旦与纲要冲突，就先写纲要草案交人确认。
经确认的改动在 `docs/outline-approvals.md` 加一条，写确认日期、用户原话和改后纲要哈希
（`python3 scripts/check_ledger.py --outline-hash` 输出当前哈希）；纲要文字与最新确认的哈希不一致时 `check_ledger.py` 报 FAIL。

## 选择工作流

| 任务 | 编排 |
| --- | --- |
| 从需求做新设计 | C1 → C6，再交付 |
| 单独运行某个模块（评测或分工） | 按 [任务输入输出格式](references/workflow-handoff.md) 的 `modules` 给定上游，只跑指定模块，交模块报告 |
| 重画已有工程，电气不变 | 单独运行 C6：用 `import_netlist.py` 把工程网表导成设计网表（见 [modules.md](references/modules.md)） |
| 修改本技能做出的设计（含改值） | 从受影响的最上游模块重做，下游按 `modules.json` 指纹重跑 |
| 收到审查意见 | 每条意见找到负责的模块，按 P7 从该模块重做并写明原因，重过关卡，下游按指纹重跑 |

## 主流程

主流程按六个能力模块排列。每个模块先写给定输入和产出，下面逐项任务做到“做完的标志”为止；最后一节“交付”是编排的收尾。

### C1 需求理解与澄清

给定输入：需求文件；任务书里的澄清答复与代答授权。产出：`record/requirements.json`（需求条文与来源、需求澄清、降额等级、准则范围）。

#### C1.1 需求追溯

按 [requirements-to-intent.md](references/requirements-to-intent.md) 第 1–2 节建立需求清单：每条需求写编号、可验收的条文和来源，记入 `record/requirements.json`。
按板上的对外端口查知识包 `需求要素/` 的对应条目（另有全板条目），逐行核需求有没有给。功能追溯（功能路径、承担器件、依赖的待办）在任务 C5.1 写。
需求没写、写得含糊、前后矛盾或尚未确认，而设计要靠它定的，**当场问用户**：录完需求后一次汇总提问，每问附一条可验收的建议条文，
答复后马上写回需求清单再往下设计；问什么、不问什么、中途发现缺口和用户暂缓怎么处理见[需求澄清](references/requirement-clarifications.md)。
**无人当场答复时**，只接受任务书里写明的答复或代答授权（[任务输入输出格式](references/workflow-handoff.md) 的 `clarification_answers`、`delegation`）；
两者都没有就停下来问，或交 `NEEDS_INPUT`，不自拟答复人。
降额等级（I/II/III 级）是一条需求：需求没写时一并问用户，附建议等级（[降额规范](references/shared/derating-rules.md)“降额等级从哪来”）；
用户暂缓的按建议等级作为写明的假设设计。等级定下之前，点名降额规则的比较只按 `unset_level` 预判（[器件应力规范](references/shared/stress-spec.md)）。
共用设计准则（G01–G09，见[共用设计准则库](references/shared/guideline-criteria.md)）按产品基线和本设计的功能电路类型、器件类别适用：
产品基线默认工业/通信板卡，需求写明航天、军用时按需求定；功能电路类型与器件类别随架构确定后补全。
需求有 −48 V 直流、正 24 V 工业直流、交流市电、工业数字输入、PoE 受电、军车 28 V、舰船交流这些对外接口的，写进功能电路类型（`DC_48V`、`DC_24V`、`AC_MAINS`、`INDUSTRIAL_DI`、`POE_PD`、`VEHICLE_28V`、`SHIP_AC`），这些接口的规则靠它选中。

做完的标志：`record/requirements.json` 的每条需求有编号、条文和来源；每个需求澄清都有答复
（用户给定、采纳建议或明确暂缓），给定和采纳的已成为需求清单里的一条需求，或并入已有需求并在该需求里引用这条澄清。有未答复的需求澄清不进入 C4。
降额等级已定（需求给定、用户答复或写明的假设），记入 `requirements.json`。
设计准则库有准则时，产品基线、功能电路类型与器件类别记入 `requirements.json` 的 `guideline_scope`（`guideline_version: 1`）。

### C2 板级方案

给定输入：C1 的产出。产出：`record/architecture.json`（含各块的块规格和跨块流向的接口参数预算）。

#### C2.1 系统架构

定出真实的系统架构：功能块及其电压域、电源与信号流向、板与隔离边界、接口，以及每条跨块流向代表的电源轨或信号
（RECT、BULK、FB/FAULT 光耦……）。它在任务 C6.3 画成第 1 页 `System_block`，只有页面索引不算架构。
见 [reference-driven-board-design.md](references/reference-driven-board-design.md)；电源树、电压域、隔离、接地、保护分层等结构选择查知识包 `板级架构模式/`。
架构记入 `record/architecture.json`，并为每个功能块写块规格（输入、输出、功率与指标，只写要什么，不写拓扑）。隔离边界的位置在这里定，块内的隔离实现方式留给任务 C3.1。
每条跨块流向写它承载的整板网络名（`nets`）和接口参数的预算值（`params`：电源轨写电压范围与最大电流，信号写电平、方向与驱动方式，模拟量写量程与源阻抗，差分对写差分阻抗，按知识包 `接口约定/参数模板/` 写，总线按 `接口约定/总线与电平/`；预算在任务 C3.3 按核心器件的端口限值定稿）；地网络按电压域的 `ground` 命名。各块端口只用这些网络名。
块的边界放在少数几个参数就能说清的地方：两块之间要靠控制环、共用一颗芯片或多条模拟连线才能工作的，合成一块。每块给一个位号编号段。

做完的标志：`record/architecture.json` 中每个功能块有输入输出、所在电压域和块规格；每条跨块流向有名字；隔离边界两侧各有哪些功能块已定。每条流向有网络名和接口参数；每块有位号编号段，各段不重叠。

### C3 块电路选择与接口定稿

给定输入：`architecture.json`（块规格与跨块流向）。产出：每块一个 `record/block-circuits/<块>.json`、`record/interfaces.json`。工作记录：`scheme-criteria.json`、核心角色的 `selection.json`。

#### C3.1 功能块实现方案

关键功能块先在知识包的[典型电路](references/knowledge-package.md)（`references/knowledge/典型电路/`）里找候选方案（`find_parts.py --circuits <功能>`）：写出决定选哪种方案的条件及本板取值，对照每种候选的适用范围，选出方案并写明其他候选被淘汰的理由。库里候选不足时，先检索知识库再比较；仍只有一种可行方案的，写明查过哪些资料。模型自身知识提出的候选须当次查到来源，查不到标`未证实`，不能选定。常规功能块可直接选用。

关键功能块（功率变换拓扑、保护架构、块内隔离实现方式、信号链架构、对外接口）定方案前，先用 `guideline_criteria.py select` 按该块的电路类型和器件类别列出按类型触发的规则，有对外端口的块再加上端口矩阵对应的 G07 规则；从中找出会淘汰某个候选方案的规则，逐条写明它排除了哪个候选、选定方案怎样满足、哪些数值留给任务 C4.2 核算，记入 `record/scheme-criteria.json`。没有规则能淘汰候选的块写明查过的规则范围。不要求逐条列出全部适用规则，不能淘汰候选、不改变选型也不进入计算的规则不要求逐条落实。

实现方案同时指出器件的设计用途、工作状态和需要核算的性能。放电、吸收、检流、限流、滤波等用途触发相应核算；“脉冲/浪涌”等关键词触发性能要求核验，不自动推出某个具体料号。普通器件可复用受控标准物料规范，仍须确认本设计工况在其适用范围内。

做完的标志：每个关键功能块在 `record/scheme-criteria.json` 写明了决定条件、候选及来源、选中和淘汰的理由，以及会淘汰候选的规则或查过的范围；影响选型、替代或功能的器件用途与性能核算项已列明，交任务 C4.2。
写完运行 `check_scheme_criteria.py <设计目录>`，无问题再结束任务 C3.1。

#### C3.2 核心器件选型与方案确认

- **先选型再核数据手册**：每个核心器件角色（控制器、协议 IC、功率开关、磁件、隔离/反馈器件、MCU）按
  [core-part-selection.md](references/core-part-selection.md) 找候选、比较并记录到 `record/selection.json`：
  至少两个候选、写明决定性条件和每个候选选中/淘汰的理由（唯一可选时写 `single_candidate_reason`，见 core-part-selection.md）。原厂资料在本机知识库
  `~/Documents/知识库/HardwareWiki/raw/`（数据手册、参考设计、应用笔记），用 `scripts/find_parts.py` 检索；
  每类器件干什么、选它看什么参数见 [part-roles.md](references/part-roles.md)，从"按功能找类"定二级类再找候选。
  库里没有合适候选才外部检索，下载的手册按任务 C4.1 的资料规则存入工程资料目录。
- **外部条件不确定时给出方案**：推荐候选依赖未公开的资料或行为（会产生外部资料待办）时，按 [core-part-selection.md](references/core-part-selection.md)
  列出 2–3 个选型方案并给出 ASG 的建议，交用户决定；用户定下来之前不进入 C4。
- **选型确认（固定暂停点）**：核心器件选型做完后，把选型清单（角色、选定候选、主要依据、与方案文档已确认决定的异同、新增的关键料号）
  汇总成一次确认交给用户；**每个核心角色**都要有确认记录（`decision`）才进入 C4：用户确认的写 `user:<日期>`；方案文档已写明"用户已确认"且选型与之一致的器件
  一并列出即可，不另问，`decision` 写 `scheme:<证据编号>` 并引原文；无人当场确认时，只能按任务书的代答授权写 `delegate:<代答人>:<日期>`，没有授权就停下来问。
  手册或计算证明某个已确认选择不成立的，列为"建议改动"连同证据一起问，不自行换方案。
- 核实决定架构的确切型号/固件能力；未证实的依赖保持条件状态，并评估替代实现。
- **端口限值**：每个核心器件写它在本块各端口上的限值（供电电压上下限与最大电流，数字口的输入门限、输出电平与耐压），注手册页码，记在 `selection.json` 该角色下，随块文件抽出，供任务 C3.3 定接口参数。
- **抽出块文件**：选型确认后运行 `block_circuits.py <设计目录>`，按 `scheme-criteria.json` 各块和 `selection.json` 各角色写的 `block_id`（`architecture.json` 的功能块 `id`），每块抽出一个 `record/block-circuits/<块>.json`：选定方案、核心器件与角色、核心器件的端口限值、决定条件的本板取值、留给任务 C4.2 核算的数值。块文件由工具抽出，不手写；C4 只读块文件。

做完的标志：`render_design_report.py` 的选型检查无问题：每个核心器件角色有候选比较和确认记录 `decision`（`user:`、`scheme:` 或 `delegate:`），
选定候选写了 `external_dependencies`，不为空的角色有 2–3 个方案、ASG 的建议和所选方案；`block_circuits.py` 抽出的块文件与两份工作记录一致。每个核心器件写了端口限值和手册页码。

#### C3.3 接口定稿

任务 C2.1 写的接口参数是预算；核心器件选定后，按各块 `block-circuits/<块>.json` 里核心器件的端口限值，把每条跨块流向的参数定成各块设计时要遵守的数，记入 `record/interfaces.json`。每条流向要写哪些量按知识包 `接口约定/参数模板/`，总线和电平按 `接口约定/总线与电平/`。
每条流向写两头。负载端写它能接受的范围（`accepts`）：电源轨写电压上下限、最大取用电流和上电时序要求，信号写输入门限与耐压；数值取自核心器件的端口限值并注手册页码，没有核心器件的块沿用任务 C2.1 的预算。
源端写它要保证的范围（`provides`）：电源轨写输出电压上下限与电流能力，信号写输出电平与驱动方式；由各负载的范围推出：电压落在所有负载接受范围的交集内，电流能力不小于各负载取用之和。
交集为空，或电流之和超出源块的块规格时，先看能否在 C3.2 换核心器件解决（按 C3.2 的选型确认重新确认）；要改架构或块规格的回到任务 C2.1，C3 按指纹重跑。两种都在 `record/modules.json` 的 `returns` 记一条，不在本任务凑数。
C4 的源块按 `provides` 设计，负载块按 `accepts` 设计，都不读对方的块。

做完的标志：每条跨块流向在 `interfaces.json` 有 `provides` 和每个负载块的 `accepts`，数值写了来源（手册页码或任务 C2.1 的预算）；每条电源轨 `provides` 的电压范围落在各负载 `accepts` 的交集内，电流能力不小于各负载取用之和；每条信号两端的电平相容。

### C4 详细设计与器件选型

C4 每块做一次。给定输入：本块的块规格、`interfaces.json` 中与本块相连的流向（网络名，本块要保证的 `provides` 或可依赖的 `accepts`）、`record/block-circuits/<块>.json`（方案与核心器件）。产出：块设计 `record/blocks/<块>.json`；工作记录 `reference-input.json`、计算记录、`component-requirements.json`。
本块的设计只依据这些输入，不读别的块；接口参数不够用或不成立时，回到任务 C3.3。

#### C4.1 数据手册核对与外围电路

本任务先从已确定的核心器件取得外围约束，记录参数的数值、条件、保证性质和出处，作为任务 C4.2的输入。外部电阻、电容等尚未选具体料号时，不填入未经核实的型号；后续依次完成性能要求和候选符合性。核心器件、物理引脚、固件身份及认证依赖的型号要求仍在本任务保留。

- 每个核心器件对应确切 MPN/封装的物理引脚表、典型应用、必需外围和装配状态，记录实际阅读的手册页码。
  分立器件的**符号含义**也按确切料号选：TVS 单向/双向、MOS N/P 沟道、NPN/PNP，引脚名按手册（单向二极管用 K/A）。
  KiCad `Device:D_TVS` 只表示双向 TVS，不能用于单向器件。
  见 [symbol-and-peripheral-contracts.md](references/symbol-and-peripheral-contracts.md)。
- 外围电路要求中的每个数值上/下界也须逐项核原表：确切变体、版本、页/表/参数行、单位、MIN/TYP/MAX 列、脚注及测试条件。
  不能只核计算输入；TYP 或所需限值列的空白/破折号不能写成保证的 `≤`/`≥`，依赖它的负载/时序结论继续保留未知。
- **优先手册规定的工作方式**：引脚的驱动或负载方式要落在手册规定的范围内（有对应特性表、典型应用或参考电路接法）。
  需要依赖 `unspecified` 参数时，先评估规定范围内的替代做法：外加小信号管缓冲、手册规定的电流源/驱动档位、参考电路接法。
  有可行的就必须采用；确实没有才保留，在 `operating_points` 写明已评估的替代做法和不可行的理由，并挂 external 厂家确认待办。
  有可行替代却保留手册未规定的方式，审计 FAIL，`pack_design.py` 拒绝打包。
- 原理图阶段 `footprint` 可以留空。必须核实所选订货变体、实际物理引脚号（含EP/Kelvin）及电气/热额定适用条件；PCB封装库制作、焊盘尺寸、孔径、钢网、courtyard、布线与DFM交给PCB阶段，不能作为原理图设计定型的门槛。既有封装候选仅作为未确认的后续环节输入，不用填充率证明电气选型完成。
- **资料规则**（2026-11-04 改）：本项目用到的数据手册存在当前设计工程的资料目录（打包输入 `datasheets`，
  通常是交付目录 `设计资料/datasheets/`），文件名为 `Vendor - PartNumber.pdf`（厂商简称按知识库 `raw/Datasheet/VENDORS.yaml`）；
  设计期间不复制进知识库 `~/Documents/知识库/HardwareWiki/raw/`，也不触发知识库入库。
  `pack_design.py` 核对 `datasheets` 目录里哪些 PDF 还不在知识库（同哈希或同文件名），不拒绝打包，
  列进 `record/manifest.json` 的 `datasheets_to_file`；设计完成后在汇报里提示用户把它们复制到
  `raw/Datasheet/<分类>/<子类>/`（分类按 `raw/Datasheet/元器件体系/器件统一分类大表.md`，无分类放 `ZZ_其他`），何时入库由用户定。
  参考设计和评估板手册放 `raw/Designexample/<拓扑>/<板名>/`，
  文件名为 `Vendor - BoardName - Title.pdf`；应用笔记和标准不放 Datasheet 目录。

做完的标志：每个核心器件在外围电路核对表 `reference-input.json` 里有引脚表与外围检查，核对通过或列出资料不足的项；
引脚表读的是所选订货变体的手册（与设计网表的 `datasheet` 同一份），每个脚照手册写了引脚名和引脚类型（不从符号回抄），符号引脚名与手册不同的写明原因，符号脚类型与手册相符；
分立器件的符号含义与料号一致；新数据手册已存入工程资料目录（打包输入 `datasheets`）。

#### C4.2 设计计算与性能要求

- 取值按知识包 `计算方法/` 对应条目的取值步骤（每步写了输入取哪一端、算完要满足哪条准则）；数值计算按 [calculation-preflight.md](references/calculation-preflight.md) 写明保证条件；按
  [requirements-to-intent.md](references/requirements-to-intent.md) 第 4 节清单逐项核这些工况：上电/热插拔、关断/掉电、
  全温角点、引脚应力、工作包络角点（最低/最高输入 × 空载/轻载/满载 × 每个输出档位的组合）和单点故障
  （反馈开路、光耦失效、检测电阻开路等：保护要在被保护对象越限前动作）。
- 按 [worst-case-bounds.md](references/worst-case-bounds.md) 推导真正的上下界：非线性量检查区间端点、内部驻点和约束边界，
  保留变量依赖；重放同一算式只验证算术。源表条件须匹配实际电压、温度、电流及测试条件，
  仅在厂家明确许可的范围内使用其插值；工程估计和未知轴不能升为保证。
- **计算门槛按设计用途**：计算的目的是把值选对、留出裕量，让图一次出对。结论由参数的依据推出：
  输入全部是保证值、推导值、设计选定值、需求值或物理常数时为设计成立（`supported`）；用到工程估计时为依赖工程估计，
  用到典型值、手册未给的参数或挂着未关闭的缺资料待办时为依赖厂家资料（两者都是 `conditional`，不阻塞出图）；
  只有算出不满足（`failed`）才是必须先解决的设计缺口。工作包络角点和单点故障由 ASG 算出数值；逐个参数的形式化最坏情况证明属于独立审查，ASG 不重复这一层。
- 每条计算给出位号（`refs`）和算出的值对门槛（`checks`），结论由数字决定；保护/检测/钳位阈值两侧都算
  （不误动作 + 保护有效），稳压管/TVS/基准源都要有计算。缺的保证由审计从 `parameters` 里列出
  （依据为 `model`/`typical`/`unspecified` 的参数名），不另写文字；没算进去的项分两种：影响检查结果却没算的
  （`coverage: partial`，算设计没做完）和只能靠样件或试验确认的（指向一件 validation 技术转交待办，不影响 `coverage`）。
  见 [设计待办记录](references/design-closure.md)。
- 器件热可行性（功耗→结温）属于设计，在本任务算；散热实现才交 PCB。见 requirements-to-intent.md 第 4 节。
  损耗预算列出主要遗漏项及有依据的边界，不能用子总和证明达标。
- **器件应力按降额等级核对**：关键器件与特殊器件在工作包络角点和瞬态下的电压、电流、功率与温度应力，与额定比较的检查点名
  `derating-rules.json` 里适用的规则；取值见[降额规范](references/shared/derating-rules.md)，判定见[器件应力规范](references/shared/stress-spec.md)，
  记录写法见 [design-closure.md](references/design-closure.md) 的 `derating_version`。只审写出来的应力，不要求每颗器件、每条规则都有一条比较。
  常规件的规格写出的最低额定 = 最坏应力 ÷ 本级降额系数。超过额定为 `failed`；应力超幅按共用判法挂待办，其余应力风险写 `improvement`、
  列入报告的应力风险，不挡交付，不挂待办。
- **同一判据对全部对象核对**：复位/欠压门限对受监督轨上每颗负载的最低工作电压，工作温度与存储温度对每颗器件，
  端口的每项外部应力对路径上每颗器件的绝对最大值（含回线被开关器件断开时经其他端口的地回路），
  有锁存、关断、复位的功能块列出上电、正常开、正常关、短路、复位与锁状态的组合并逐行给结论。
  行和格由 `scripts/object_matrices.py` 从设计网表列出，不自选对象；记录写法见 [design-closure.md](references/design-closure.md) 的 `matrix_version`。
- **参数逐项有来源**：每条计算在 `design-closure.json` 的 `parameters` 里列出用到的每个参数：值、单位、依据（`basis`）、
  位号和手册定位（`datasheet:<库内路径>#p<页>` 加表名/符号）。依据另有 `requirement`（来自需求，`source` 写 `req:<需求编号>`）
  和 `constant`（物理常数），不再归入 `model`。手册没给的器件参数标 `unspecified`，不能写成保证值，
  也不能支撑 `supported`。格式见 [设计待办记录](references/design-closure.md)，`audit_design_closure.py` 核对。
  器件保证值先查知识包 `器件参数/`（保证值与手册页码），没有的再读手册；用 onsemi 等原件时，`原件勘误.md` 名单里文字层单位有问题的原件看页面图像核单位。
- **工况输入有来源**：负载、源阻抗、环境温度、输入电压窗、外部瞬态、线缆这些板外工况，参数写 `input_role`，来源只能是需求、负载器件手册或由它们推导；
  需求只给了标准和等级（例如 ISO 7637-2 的严酷度、GB/T 17799.2 的端口电平、GJB 151C 的 CS117）时，该等级对应的波形和数值查知识包 `接口约定/环境与电磁等级/`，来源按“由需求推导”记并引所用条目；
  需求没给、取值又会改变选型的，按[需求澄清](references/requirement-clarifications.md)问用户，不自定。启动计算必须声明启动期负载。
  判法见[设计待办记录](references/design-closure.md)“工况输入的来源”，`audit_design_closure.py` 核对。
- **按适用的共用设计准则设计**：设计准则的 `asg_action` 是设计动作。只有进入计算的准则逐条落实：落实它的计算在 `guidelines` 里写准则编号，
  任务 C3.1 留给本任务的数值由引用该准则的计算关闭。其余准则按设计动作照做，不要求逐条引用；审计列出适用与已引用的准则供审查对照。
  有对外连接器的板写 FMEA 和 EMC 端口矩阵，登记为证据并写 `carrier`，审计核对必备章节与连接器齐全。

**把计算落实为可采购的器件性能要求**：将实际需要核算的器件记入 `record/component-requirements.json`，由它统一生成设计网表属性、BOM规格和图面标注。字段及执行接口见 [器件性能要求](references/component-requirements.md)；新设计采用 `component_requirements_version: 1`，按用途分组筛选位号，不给每颗普通件增加全参数计算。
- 每项要求的字段、各类器件按用途核哪些性能（放电电阻的能量与波形、电容的有效容量、电感的饱和电流等）、受控标准料的引用和数据不足时的暂定要求，
  见 [器件性能要求](references/component-requirements.md)。本可计算却尚未计算的，仍是设计未完成，不能用“待采购确认”代替。

做完的标志：`audit_design_closure.py` 无错误；没有 `failed` 的计算；每条计算的结论、`rests_on` 与 `coverage` 与参数依据推出的一致。与额定比较的应力都点名适用降额规则；超降额未超额定按原规范列风险。每个已识别的性能核算项都有数值、条件和出处，或有明确的有条件要求与假设；仍缺可独立完成的计算时不得标记本任务完成。任务 C3.1 留给 C4.2 的数值都已由计算关闭。

#### C4.3 器件选型与性能符合性

输入为任务 C4.2的性能要求。逐项决定采购定义方式并核对来源：
1. **按规格采购**：性能可用完整规格定义的器件，采用受控标准物料或寻找符合要求的来源；未锁定料号时允许保留可采购性能规格，说明可行性依据，不把假设中的器件能力当成现成保证。
2. **按型号或设计单定义**：电路依赖物理引脚、接口/固件行为、认证、特定曲线或型号特性的器件，继续明确料号/订货变体/设计单，核对手册条件。安全认证与定制磁件要求不得因“按规格”而取消。
查阅原厂手册以核实候选，不自动意味着电路只能绑定该料号；可转为完整可替代性能约束的，优先保留规格采购方式。
3. **核对候选**：将要求值、候选保证值及双方适用条件逐项对照，记录资料来源、符合/不符合/尚未核实的结论。需要比较核心器件方案时仍执行任务 C3.2，不给所有普通料新增“两候选”义务。
4. **处理差距**：算出不满足时换料、调整电路或重新分配性能，并回到受影响计算。厂家保证缺失时保留真实外部依赖；不要先把候选写成已核准，再附一句“关键性能待确认”。处理差距若要改变用户已确认的器件方向、结构或取值（方案文档或任务 C3.2 的 `decision`），停在本任务，把矛盾、证据和 2–3 个改法交用户定（无人当场答复时同任务 C3.2，只接受任务书代答）；答复改选型的回到任务 C3.2（改 `selection.json` 并重新抽出块文件），改需求的回到 C1，本块按指纹重跑后再继续；不自行改成别的方案，也不在本任务改上游的记录。
5. **不过度设计**：满足性能要求之后，额定、精度、封装和保护级数按需要取，不无理由地取高一档；取高的写明理由（降额、统一物料、可得性等）。
6. **按准则选型**：设计准则的 `asg_action` 改变了选型或性能要求的，在对应性能记录的 `guidelines` 写准则编号（电源输入器件、接口保护器件等）。
7. **记录状态**：性能定义是否完整、采购定义方式、候选是否已经核实分别记录。未核准的候选放入候选栏；“型号未定”“候选待核”“已核准”不能混用。按规格采购可以有多个经核准的来源。

做完的标志：每项性能要求都有采购定义方式和来源/候选处置；无已知不满足被当成满足，无未核实候选被当成已核准；
按型号采购的器件，值、料号与数据手册指同一订货变体，料号写全订货码；电容额定电压与 TVS 工作电压不低于所在电源轨的最坏最高电压。
尚缺外部数据的可有条件进入出图，但报告不能宣布其型号核实或设计定型已完成。

#### C4.4 块设计

把本块写成块设计 `record/blocks/<块>.json`（格式见 [modules.md](references/modules.md)）：器件、块内网络 `{name: [ref.pin]}`、端口、`no_connect`，以及本块网络的 `net_roles`、`net_voltages`、`external_supply`、`filtered_supply`。
器件的值、性能规格、采购定义方式与选型状态由任务 C4.2 的性能记录按位号生成，不另写默认值；记录不完整或候选未核准的保留真实状态。
位号在 C2 给本块的编号段内。端口用流向给的整板网络名，块内网络不与端口重名。
每个物理引脚要么接入网络，要么有依据地标 NC；不接的脚和按手册接地、上下拉的未用脚，逐脚写手册规定的处置和页码。
本块输出的电源轨写最坏最高电压和来源。值写设计值，不留库默认名或占位。用 `net_roles` 区分 power/return/signal，至少覆盖电源轨与阈值/反馈等易混淆网络。
只由连接器引入的电源或地、经一颗串联件从已有电源派生的供电网，逐网声明 `external_supply`、`filtered_supply`。

做完的标志：本块每个物理引脚接入网络或有依据地标 NC，处置有手册页；端口都是流向给的网络名；位号都在本块编号段内；本块输出的电源轨写了最高电压；没有占位值和未编号位号。

### C5 全板闭合

给定输入：`architecture.json`、`interfaces.json`、各块的块设计 `record/blocks/`。产出：整板 `electrical-intent.json`、整板层块 `blocks/BOARD.json`、需求追溯、闭合矩阵、FMEA 与 EMC 端口矩阵。

#### C5.1 设计网表

用 `scripts/blocks.py merge` 把各块的块设计按网络名合成整板设计网表 `electrical-intent.json`：同名端口接成一个网络，每个器件的 `fields.Circuit` 写所属块。合并报错（块内网络重名、端口没有对端、位号重复、同一网络各块的角色或电压不一致）时，按原因回到 C4 或 C2，不在 C5 改块设计。
各块之间只差接口件（上拉、电平转换、隔直）的，C5 写进整板层块 `blocks/BOARD.json` 再合并；要改块内设计的回到该块的 C4，根因在电压域或流向划分的回到 C2。
在 `design-closure.json` 的 `traceability` 为 `requirements.json` 的每条需求写追溯：功能路径、承担器件、状态和依赖的待办，用需求编号引用；不能批量挂整板位号代替追溯。

做完的标志：`blocks.py merge` 无错误，`electrical-intent.json` 由它生成；每条需求在 `traceability` 有功能路径和承担器件（或写明理由的空列表）；每条电源轨写了最高电压；
`object_matrices.py` 按本版设计网表列出的矩阵与状态表逐格有结论（`matrix_version 1` 的审计没有 `matrix_cell_missing`、`matrix_cell_failed` 和 `matrix_*` 错误）。

#### C5.2 全板闭合核对

整板设计网表写完后，按整板审计核对全板：引脚处置、网络电压、对象矩阵与状态表、跨板接口约定。有对外连接器的板写 FMEA 与 EMC 端口矩阵（[必写的设计文档](references/guideline-evidence-groups.md)）；端口矩阵里各端口的试验项目、等级和波形查知识包 `接口约定/环境与电磁等级/`，器件失效方式与分析步骤查 `失效与异常工况/`，从准则编号反查条目用 `准则支撑表.md`。不满足的格改设计，不以列出缺口代替完成。

做完的标志：`audit_design_closure.py`（不带 `--module`）无错误；矩阵与状态表没有缺结论或不满足的格；有对外连接器的板 FMEA 与 EMC 端口矩阵章节与连接器齐全。

### C6 原理图绘制

给定输入：设计网表；串联运行时另读 `architecture.json` 与各块的 `block-circuits/<块>.json`（各块选定的典型电路）；单独运行时只给网表。产出：`page-plan.json`、KiCad 工程、`summary.json`、`visual-review.json`。

#### C6.1 分页方案

分页时给需要展示的性能要求分配位置：基本数值放元件旁，较长的条件放同页技术要求表或注释，用位号/注号对应。只显示设计与替代需要的信息，不把整段计算或数据手册搬到图上。表格和说明必须进入正常的布局与几何检查。

按功能、隔离/电压域和可读面积分页；几个很小的功能块合成一页，不单独占一张 A3。
为每页写一张简短的分页方案，内容包括：读者任务（跟随能量流、看懂反馈、追一个受保护接口……）、
功能块及每块的位号、主路径、电源轨、出页网络及目的功能/页码、标签边界。先保证一条功能路径易读，再决定拆页或加大纸张。
分页方案随交付保存为 `record/page-plan.json`（每页 `file`、`reader_tasks`、`blocks`、`key_blocks`、`circuits`），本页每个器件都要属于一个功能块，
每个关键功能块标注所用典型电路与实现方案 `"<典型电路文件名>#<实现方案名>"`（第一页是架构页，免标；没有适用典型电路的关键块写 `none`）；
图面审阅按它逐条追路径。见 [human-readable-routing.md](references/human-readable-routing.md) 第 1 节。
单独运行 C6、没有 `architecture.json` 和块文件时，功能块划分由本任务从网表定，`key_blocks`、`circuits` 留空，C6 关卡不做典型电路标注检查。
纸张在画完后定：内容能放进 A4 就用 A4；一页只剩零散小块时并页，不把小电路摊在 A3 上。

- 按拓扑选结构（Buck、LDO、隔离反激、滤波、MCU 各不相同），见
  [schematic-drawing-standards.md](references/schematic-drawing-standards.md) 第 2 节。不得为别的拓扑编造 SW 节点或电感级。
- 按绘图纲要 决定页面流向、锚点、器件归属、画法、出线、标签、间距和修复顺序，见
  [drawing-recipes.md](references/drawing-recipes.md)。
- 图面的目标是逻辑清晰、按功能块划分、方便工程师理解、能指导 PCB 设计；按绘图纲要里的画图习惯落实（块标题、块内导线块间标签、不绕远、
  密度与纸张、多单元器件按单元画、去耦画在引脚旁、写给 PCB 的短注），见同一文件。

做完的标志：`render_design_report.py` 的分页方案检查无问题：每页的读者任务、功能块与关键块的典型电路标注（库里没有适用的写 none）齐全，每个器件属于一个功能块。

#### C6.2 图页脚本

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
  有意偏离绘图纲要时用 `s.justify(对象, 理由)` 记录。把分页方案的功能块传给 `Sheet(..., blocks={块名: [位号]})`：
  同一块内的器件之间不许用局部连接标签代替导线（HR-01），审计会列出只连一块的标签。
- 间距只为通过检查而加大，通过后缩回：上限与豁免按 O7（超过 12 格进结构审计，一页超过 3 处间距豁免即审计不通过，改为折行或重新锚定）；
  带小网络名的串联段或本引脚短线，放置前用 `s.name_run_steps` 预留直段，用法见 [drawing-recipes.md](references/drawing-recipes.md)。
- `build()` 遇到硬缺陷会直接报错。`report["structure"]` 必须为 PASS，`report["readability"]["gate"]` 必须为 PASS。
  失败时按 O8 改结构（方向、间隙、顺序 → 锚点 → 拆行）后重建，不得手调坐标打补丁。
  `report["readability"]` 还给出 `cell_coverage`（有东西的 25.4 mm 格占比）、`part_groups`（只靠标签/电源符号相连的器件组）
  和 `fits_paper`：覆盖率低、组数多于分页方案的功能块、内容能放进更小的纸张，都说明这页要并块、缩间距或换纸。
- 元件旁的基本规格和同页性能注释从 `component-requirements.json` 生成（长要求用 `Sheet.performance_notes(at)`），不手工回抄；
  措辞与可见性要求见 [器件性能要求](references/component-requirements.md)。仍缺计算的审阅草稿标注“待计算”，不能凭此声明完成。
- 图页脚本随交付版本一起保存；下一版只重生成有变化的页面。

做完的标志：每页 `Sheet.build()` 不报错，`report["structure"]` 与 `report["readability"]["gate"]` 为 PASS；每页间距豁免不超过 3 处。

#### C6.3 组装工程

多页工程用 `schematic_layout.root.Root` 组装根图：`page()` 放各页的层次图框，`flow()` 画带名字、两端落在图框上的流向线
（`kind="power"` 能量流、`"signal"` 控制链，线宽不同），`isolation()` 画隔离边界，`write()` 写出根图 `System_block`、
各页（实例路径改写到根工程）、`.kicad_pro` 和 `sym-lib-table`；文字压线或系统框图审计不通过时直接报错。
用法见 [drawing-recipes.md](references/drawing-recipes.md) 多页一节。
第 1 页 `System_block` 按任务 C2.1 的架构画，要求见 [reference-driven-board-design.md](references/reference-driven-board-design.md) 的 System_block 一节。

做完的标志：`Root.write()` 不报错，写出根图、各页、`.kicad_pro` 与 `sym-lib-table`。

#### C6.4 自动检查

```bash
python3 <skill>/scripts/verify_schematic.py <root.kicad_sch> --intent electrical-intent.json \
  --out <新的空目录> [--expected-pages N] [--symbol-exceptions F] [--readability-waivers F] \
  [--reference-contract F] [--design-closure D --artifact-root R]
```

它一次完成：KiCad ERC / XML 网表 / PDF 导出，网表分区与器件身份逐脚对比设计网表（图上画出的网络名须等于设计网表里同一组引脚的网络名，
只允许页路径前缀；KiCad 自动网络名不比），层次与 PDF 页数，根图的系统框图检查（`system_block`），
符号引脚完整性，分立器件符号含义与手册/型号后缀是否一致（`discrete_semantics`），可读性检查（零异网交叉、零三折以上两端连线、
内容放得进更小纸张的页算 FAIL），以及每个有效页面的几何检查，汇总到 `summary.json`。
只有全部检查项为 PASS 时结果才是 `AUTOMATED_PASS`。
可以用 `scripts/deliver.py <交付目录>` 一次跑完出图、自动检查到打包，参数记在 `record/deliver.json`，见 [交付与设计报告](references/delivery-report.md)。

- 器件性能检查核对性能定义、选型符合性状态和设计网表/BOM/图面的一致性：规格绑定以 KiCad 导出的属性/XML 为准，可见内容以实际 PDF 为准，
  判法见 [器件性能要求](references/component-requirements.md)；检查器覆盖不到的图面对象转任务 C6.5，不自动判通过。
- 新设计提供 `--design-closure`，核对需求实现、外部依赖、计算覆盖和证据是否最新；格式与边界见 [设计待办记录](references/design-closure.md)。未提供时明确为 NOT_CHECKED，不能据此声明全流程完成。
- ERC 要求零违规。
- ERC 摘要按原始报告的 UUID/object 对应实际层次实例、引脚及 KiCad 网络，再归因到电源轨；
  不凭位号或网络名文字猜问题对象。无法对应时保留原违规与待核边界，见 [project-verification.md](references/project-verification.md#erc-摘要对应到对象)。
- 几何检查只覆盖本次 KiCad 导出中已合格的对象，范围与未支持对象见 [native-geometry.md](references/native-geometry.md)；
  外部 JSON 回执不能授权放行。`geometry` 为 INSUFFICIENT 时保留缺口并在 KiCad 渲染图上核对，有限 PASS 不等于整案通过。
  库里隐藏的引脚号/引脚名不计；可见但无法由 KiCad 导出核对的引脚文字列在 `geometry.render_review_items`（图面待审对象），
  不算缺口，任务 C6.5 图面审阅必须逐页覆盖这些对象并在 visual-review.json 里写明。
- 图面检查只有三种结果：PASS、FAIL（画图问题，如外框间距不足 1.27 mm、导线交叉不打点、注释压线）、
  INSUFFICIENT（检查器覆盖不到的对象）。FAIL 由 ASG 改图关闭，不交给人复核；可读性或几何 FAIL 时
  `pack_design.py` 拒绝打包。只有 INSUFFICIENT 缺口留给图面审阅核对。
- KiCad 自动生成的 `Net-(...)` 网络名不与设计网表比名；设计网表里的网络名必须显式标注在图上，与导出网表一致，见
  [project-verification.md](references/project-verification.md#自动网络名不比对)；
  编码斜杠层次字段只用 [schematic-drawing-standards.md](references/schematic-drawing-standards.md) 的有限回退，不推广。
- 工程的 ERC 规则不得设为忽略（`simulation_model_issue`、`footprint_filter` 除外），自动检查读取工程设置核对。
- 失败时修改相应图页脚本，在新的运行目录重新生成并检查。不得为了降低计数而加 PWR_FLAG、加排除项或改引脚类型。
- PWR_FLAG 只用于设计网表逐网声明的 `external_supply`（只由连接器引入、板上没有电源输出脚驱动的电源或地）和 `filtered_supply`
  （经一颗串联电阻、电感、磁珠或保险丝从已有驱动的电源派生的供电网，逐条列入设计报告），用 `Sheet.power_flag()` 每网放一个，由 `external_supply` 检查项核对；
  声明格式见 [requirements-to-intent.md](references/requirements-to-intent.md) 第 5 节“连接器角色与外部供电”。
- 整流、变压器或分立稳压电路没有 KiCad `power_out` 时，不冒充连接器供电、不改引脚类型，按[分立供电复核](references/reviewed-circuit-supply.md)
  的 `reviewed_circuit_supply` 处理；自动检查只核证据是否最新和 KiCad 拓扑，未完成复核时保留 ERC。
- `symbol_integrity` 的 `unnamed_pins` 只作诊断（KiCad 运放、单门逻辑等符号的输入/输出脚按库惯例不写名字）。
  列出的每个器件（不限核心器件）都要在外围电路核对表里按数据手册名字逐脚对应，并在设计报告中列出这些脚；
  否则按引脚名核对时会对不上。

做完的标志：`summary.json` 没有 FAIL 的检查项，INSUFFICIENT 的逐条列出原因；导出网表与设计网表逐脚一致；ERC 零违规。

#### C6.5 图面审阅

在实际 PDF 上逐页核对性能标注（位号/注号对应、参数与单位、“要求/器件保证/待核”含义清楚、表格未压线），按位号记录结果；隐藏属性完整不代替这一步。

打开导出的 PDF，逐页按 `page-plan.json` 的读者任务追主路径、支持网络与回流路径、重复通道、地域和隔离跨越；
逐页核对绘图纲要画图习惯里不自动检查的各条，`report["readability"]["detours"]` 列出的绕远连线逐条处置；
逐条处置 `geometry.render_review_items`，写出在本版 PDF 上看到了什么，没改动的页面也重新审阅，不沿用上一版的处置。
追法、三种状态（待返工 / 待图面审阅 / 已完成图面审阅）和 `pdf_sha256` 的写法见 [human-readable-routing.md](references/human-readable-routing.md) 第 4 节
与 [delivery-report.md](references/delivery-report.md) 的 `visual-review.json` 一行。用户否决会重新打开图面审阅。

做完的标志：`visual-review.json` 为 `REVIEWED`，每页路径数不少于读者任务数，每个图面待审对象有本版的处置，`pdf_sha256` 对得上本版 PDF。

### 交付

#### 设计完成核对

还有可独立完成的设计项就回到对应任务做完，不以列出缺口代替完成。待办只由本版设计过程中确认仍需做的事项决定，不与上一版比较。

同时核对性能定义与选型状态：可独立完成的性能要求计算须完成；仅有料号但关键性能未核实的，不能写“已核准”。有条件性能要求和真实外部依赖继续按现有计算依据分类，不因图纸已输出而转成保证。

做完的标志：各模块在 `record/modules.json` 都是 OK；未关闭项只剩外部资料待办、技术转交、用户暂缓的需求和已登记理由的设计待办；没有未答复的需求澄清；审计列出的可执行设计动作都已完成；淘汰候选方案、改变选型和进入计算的准则都已落实在方案比较、性能记录或计算里。

#### 报告与打包

交付增加 `record/component-requirements.json`，报告分别给出性能定义完整程度、选型核实状态和未关闭项；BOM及图面的可见规格由该记录生成。打包检查性能记录和图纸/BOM是否同源、最新、一致；完整规格采购、候选待核与型号已核准各自表述，不能统一写成选型完成。

- 按 [交付证据（快照检查）](references/delivery-report.md#交付证据快照检查) 写 `delivery-evidence.json`，报告前运行
  `scripts/check_delivery_freshness.py`；任何导出后的修改都会使旧结果作废。
- 交付目录只有下面四样，由 [交付与设计报告](references/delivery-report.md) 规定，`pack_design.py` 检查：

```
<交付目录>/
  设计报告.md     唯一给人看的文件：render_design_report.py 由记录生成，notes.json 的摘要与说明和记录按同一套专业术语写
  原理图/         KiCad 工程（根图、各页、项目符号库与封装库）、schematic.pdf、netlist.xml、BOM.csv
  设计资料/       跨版本有效、每版更新的设计文档（方案与选型依据、FMEA、EMC 端口矩阵、磁件设计单等；其他按需求选做）
  record/         设计网表、分页方案、待办处理情况、自检结果、图面审阅、本版用到的计算、知识缺口清单、
                  图页脚本、manifest.json（需求、原厂资料按路径+SHA-256 登记，不复制；记知识包版本与指纹）
```

```bash
python3 <skill>/scripts/render_design_report.py <交付目录> [--notes notes.json] [--title 标题]
python3 <skill>/scripts/pack_design.py <交付目录> --input requirements=<需求目录> \
  --input datasheets=<资料目录>
```

`knowledge_gaps.py <交付目录>` 从各模块的产品里抽出知识缺口清单 `record/knowledge-gaps.json`，不手写：知识包哪个组件查不到什么（典型电路没有适用方案、`modules.json` 的 `knowledge_lookups` 里没查到的）、候选来源未证实、计算依据是典型值或估计、回到上游重做、用户否定了 ASG 的建议。清单只如实列出，不拦交付；它是评测侧归纳能力缺陷的输入。
也可以用 `deliver.py <交付目录>` 按固定顺序一次跑完生成报告、写交付证据、新鲜度检查和打包，见任务 C6.4。
报告如实写出各项自检的 PASS/FAIL/INSUFFICIENT 及数量（含零）。历史版本快照、日志、仿真中间文件、
审查方的其他文件都不放进交付目录；本版独立审查的报告只放 `record/sr-review/`。

做完的标志：`deliver.py` 各步为 DONE、PASS、CONDITIONAL、INCOMPLETE 或 FRESH 且跑到打包，打包 PASS；
打包列出的 `datasheets_to_file`（本项目用到、知识库还没有的手册）在汇报里提示用户复制进知识库。

## 在任务流程中运行

由外部流程派发任务时，读 [任务输入输出格式](references/workflow-handoff.md)。
以 `task.json` 的需求、版本和给定输入为输入；审查意见按 P7 回到负责的模块重做；架构生成、查资料、计算与改图仍由 ASG 完成。
交付仍按「交付」一节“报告与打包”规定的目录；`result.json` 由派发任务的外部流程按该页格式生成，本技能不带这个工具。独立使用本技能不依赖外部流程。

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
| 能力模块的关卡、`architecture.json`、接口定稿 `interfaces.json`、块设计与合并（`blocks.py`）、`modules.json` 与过期判定（`check_module.py`）；单独运行模块、只给网表画图（`import_netlist.py`） | [modules.md](references/modules.md) |
| 设计待办记录、依赖与计算结论审计 | [design-closure.md](references/design-closure.md) |
| 交付目录、设计报告、打包检查 | [delivery-report.md](references/delivery-report.md) |
| 从需求写设计网表 | [requirements-to-intent.md](references/requirements-to-intent.md) |
| 需求没说清：问什么、什么时候问、答复怎样写回需求清单 | [requirement-clarifications.md](references/requirement-clarifications.md) |
| 架构页、参考设计外围 | [reference-driven-board-design.md](references/reference-driven-board-design.md) |
| 核心器件从哪找候选、怎么比较、`selection.json` | [core-part-selection.md](references/core-part-selection.md) |
| 每类器件干什么、选它看什么参数（按知识库分类） | [part-roles.md](references/part-roles.md) |
| 知识包：需求要素、板级架构模式、接口约定、典型电路（一个功能有几种实现方案、各自的必算项与已知坑）、计算方法、器件参数、失效与异常工况；各模块查哪部分、典型电路标注与 `scheme-criteria.json` 格式、本地校验（版本以根目录 `knowledge-release.json` 为准） | [knowledge-package.md](references/knowledge-package.md) 与 `references/knowledge/` |
| 选符号、引脚表、外围电路要求 | [symbol-and-peripheral-contracts.md](references/symbol-and-peripheral-contracts.md) |
| 计算条件记录 | [calculation-preflight.md](references/calculation-preflight.md) |
| 器件性能要求、BOM 与图面标注 | [component-requirements.md](references/component-requirements.md) |
| KiCad 导出几何的范围 | [native-geometry.md](references/native-geometry.md) |
| 非线性极值、条件匹配与插值边界 | [worst-case-bounds.md](references/worst-case-bounds.md) |
| 共用设计准则（G01–G09，运行包版本以根目录 `shared-release.json` 为准）：设计准则、适用条件、引用与覆盖、下游约束（共用层，见 shared-layer.md） | [guideline-criteria.md](references/shared/guideline-criteria.md)、`references/shared/guideline-criteria.json` |
| 必写的设计文档（FMEA、EMC 端口矩阵）：何时要写、必备章节与对象 | [guideline-evidence-groups.md](references/guideline-evidence-groups.md)、`references/guideline-evidence-groups.json` |
| 共用层：哪些文件两技能同字节、各自的角色、谁读、哪条测试守、怎么改 | [shared-layer.md](references/shared/shared-layer.md) |
| 共用规范 G10 降额与应力规范（G01–G09 设计准则之外的第十份，不进准则登记）：I/II/III 级降额值、等级从哪来、取值规则、应力怎么判、查到什么程度（共用层，见 shared-layer.md） | [stress-spec.md](references/shared/stress-spec.md)、[derating-rules.md](references/shared/derating-rules.md)、`references/shared/derating-rules.json` |
| 绘图纲要（结构规则与画图习惯）与 recipes API | [drawing-recipes.md](references/drawing-recipes.md) |
| 阅读路径、HR 规则、图面审阅 | [human-readable-routing.md](references/human-readable-routing.md) |
| 拓扑结构、标签策略、检查项 | [schematic-drawing-standards.md](references/schematic-drawing-standards.md) |
| ERC 摘要对应到对象、自动网络名不比对、层次与 PDF | [project-verification.md](references/project-verification.md) |
| 交付证据与是否最新 | [delivery-report.md](references/delivery-report.md) 的“交付证据（快照检查）” |
| 用词 | [terminology.md](references/terminology.md) |
| 低层生成器 | [schematic-generation.md](references/schematic-generation.md) |

运行依赖见 [README.md](README.md) 的“安装”一节。
