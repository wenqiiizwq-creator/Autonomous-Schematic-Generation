---
name: autonomous-schematic-generation
description: >-
  Autonomous-Schematic-Generation (ASG): starting from requirement documents,
  draw readable, electrically correct KiCad schematics verified by KiCad's own
  exports. Five steps: requirements and solution → detailed design (pin maps,
  calculations, component performance requirements, selection, design netlist) →
  schematic drawing (page plan, pin-geometry recipes, project assembly) → design
  checks (ERC, netlist, hierarchy, symbol integrity, readability, geometry, visual
  review) → design output (generated report and fixed delivery folder).
  Also redraws existing KiCad projects without
  electrical change, applies authorized electrical revisions, works through
  review comments and extracts PDF reference designs. Self-checks only; owns
  design feasibility, selection, calculations and functional completion. Use for .kicad_sch
  generation or redraw, 原理图自动生成、从需求画原理图、画原理图、重画原理图、原理图排版.
---

# Autonomous-Schematic-Generation (ASG)

## 目的与边界

ASG 从需求文档出发，让 Agent 在 KiCad 中画出**可读、电气正确、经 KiCad 验证**的原理图。

- **电气正确**：电路来自已确认的需求、关键与特殊器件的数据手册和常规件的规格，用一份独立写出的设计网表表达；
  KiCad 导出网表必须与设计网表逐脚一致。
- **可读**：结构由 Agent 按绘图纲要 O1–O8 决定，坐标由 `recipes.Sheet` 按真实引脚几何推出。
- **经 KiCad 验证**：以 KiCad 导出的 ERC、XML 网表和 PDF 为准；JSON、脚本成功或 solver 的 `solved` 都不算证据。

ASG 负责需求到电路的方案可行性、选型依据、设计计算和功能实现，不能把未做完的设计留给别人。
新设计和电气改版同时遵循
[设计待办记录](references/design-closure.md)，区分工程可完成、真实外部依赖和后续环节验证。
电气改版按其中从审查缺口回到电路的做法执行；审计列出的可执行设计动作须继续完成，不能把缺口清单当成结束条件。

以下验收与独立复核不由 ASG 负责：

| 事项 | 交给 |
| --- | --- |
| 独立的电气审查和设计定型结论 | 由审查方给出；ASG 只做自检，并处理收到的审查意见 |
| PCB封装库、焊盘/孔/钢网、布局布线、DFM与散热实现 | 《结构与PCB设计要求》技术转交文档 |
| 生产放行、PCB、SI/PI、EMC | 后续环节 |

## ASG 纲要（核心标准）

本节是 ASG 的核心标准。其余章节、`references/` 和 `scripts/` 都是它的展开与实现，不得与之冲突。

### 架构

ASG 是五个步骤的流程，每个步骤下有几项任务（1.1、1.2 …），按实际原理图设计流程排列；
先弄清自己在哪一步、产出什么，再按“主流程”逐项任务做，每项任务做到“做完的标志”为止。

- **输入**：需求、器件知识库、电路模式库、已有工程/审查意见
- **支撑**：KiCad CLI（唯一证据来源）、`schematic_layout`（布图与检查）、`references/`（规则与知识）、
  持续改进（lessons → 归因 → 修改 → 合成测试）

| 步骤 | 任务 | 这一步的目的 | 产出 |
|---|---|---|---|
| ① 需求与方案 | 1.1 需求追溯 · 1.2 系统架构 · 1.3 功能块做法 · 1.4 核心器件选型与方案确认 | 把需求落到功能块和核心器件；需求缺口当场问用户，答复写回需求清单，会改变方案的取舍由用户定下 | 需求追溯、需求澄清、系统架构、`selection.json` |
| ② 详细设计 | 2.1 数据手册核对与外围电路 · 2.2 设计计算与性能要求 · 2.3 器件选型与性能符合性 · 2.4 设计网表 | 按核心器件手册确定外围约束，从工况计算器件性能要求，核对采购来源或候选器件的符合性，再写出设计网表 | `reference-input.json`、计算记录、`component-requirements.json`、`electrical-intent.json` |
| ③ 原理图绘制 | 3.1 分页方案 · 3.2 图页脚本 · 3.3 组装工程 | 按绘图纲要 O1–O8 把设计网表画成可读的 KiCad 工程 | `page-plan.json`、图页脚本、KiCad 工程 |
| ④ 设计检查 | 4.1 自动检查 · 4.2 图面审阅 | 用 KiCad 导出核对电气与图面，再按 PDF 逐页审阅 | `summary.json`、`visual-review.json` |
| ⑤ 设计输出 | 5.1 设计完成核对 · 5.2 经验总结 · 5.3 报告与打包 | 设计做完才交付，记下学到的东西，生成报告并打包 | 交付目录、`lessons.json` |

独立审查（schematic-review 技能或其他审查方）在设计输出之后，不属于 ASG。

### 核心原则

- **P1 证据**：只认 KiCad 导出的 ERC、XML 网表和 PDF；JSON、脚本成功都不算证据。
- **P2 电气与几何分离**：设计网表从需求和手册独立写出，不从图上回抄；摆放不改变电气。
- **P3 真值**：器件先形成与实际工况对应的性能要求；需绑定型号的器件以确切料号或定制设计单为依据，可按规格采购的器件以算得的性能要求为依据。性能定义与候选器件符合性的核实状态分别记录，料号不能替代性能核验。
- **P4 可读**：页面结构按绘图纲要 O1–O8 决定，坐标从引脚几何推出；可读性是交付标准。
- **P5 失败改结构，不改计数**：不靠 PWR_FLAG、豁免、改引脚类型或标签来掩盖问题。
- **P6 责任边界**：设计完成由 ASG 负责，只做自检；独立审查交给独立审查方（schematic-review 技能）。
- **P7 进步**：每版必须记下学到的东西；技能只因有来源的事件而改；每处改动附复现该事件的合成测试，全部测试通过后才提交。

### 纲要的修改

本节（架构、P1–P7）、主流程的步骤、任务与做完的标志，以及绘图纲要 O1–O8，任何增、删、改或重排，都须先把改动草案交给人确认后才能写入。
持续改进中归因到纲要的事件，只在 `lessons.json` 和台账里登记为提案，不直接修改。
`scripts/` 和 `references/` 中的实现细节可以按事件修改，但一旦与纲要冲突，就转为纲要提案。
经确认的改动在 `docs/improvement-ledger.md` 的条目里写 `Approved: user:<日期>` 和 `Outline: <哈希>`
（`python3 scripts/check_ledger.py --outline-hash` 输出当前哈希）；纲要文字与最新确认的哈希不一致时 `check_ledger.py` 报 FAIL。

## 选择工作流

| 任务 | 做法 |
| --- | --- |
| 从需求做新设计 | 主流程步骤 ①–⑤ |
| 给已有工程新增模块或页面 | 任务 1.1 只读相关需求，再从任务 1.3 做起；改动已有网络时按“电气改版” |
| 重画已有工程，电气不变 | [existing-project-redraw.md](references/existing-project-redraw.md) 锁定基线，再走步骤 ③–⑤ |
| 已授权、保持连线与图面的 Value 参数修改 | [value-patch.md](references/value-patch.md) 生成 KiCad 验证的草稿图，再更新设计网表/脚本与计算，走步骤 ④–⑤ |
| 授权的电气改版 | 先读 [electrical-redesign.md](references/electrical-redesign.md) 和 [change-preflight.md](references/change-preflight.md)，再走主流程 |
| 收到审查意见后继续设计 | 按 [处理审查意见](references/review-comments.md) 逐条登记处理方式，再按电气改版处理需要改图的项；每条意见写本版做了什么，补设计的待办写 `progress`，没改电路的叫“补计算/补文档”不叫“改图” |
| 从 PDF 参考设计提取电路 | [pdf-schematic-extraction.md](references/pdf-schematic-extraction.md)；提取结果只作线索，仍按任务 2.1 核对数据手册 |
| 模块化数据、SKiDL/circuit-synth 导入、锁定基线 | [circuit-ir.md](references/circuit-ir.md)。人读的页面仍按任务 3.2 用 recipes 画 |
| 用户要求 CopperPilot 协助 | [copperpilot-reference-workflow.md](references/copperpilot-reference-workflow.md) |

## 主流程

### ① 需求与方案

#### 1.1 需求追溯

按 [requirements-to-intent.md](references/requirements-to-intent.md) 第 1–2 节建立需求清单和
功能追溯表。每项映射具体功能路径、器件/固件责任和验收；不能批量挂整板位号代替追溯。
需求没写、写得含糊、前后矛盾或尚未确认，而设计要靠它定的，**当场问用户**（[需求澄清](references/requirement-clarifications.md)）：
录完需求后一次汇总提问，不逐颗器件打断用户；每问附一条可验收的建议条文；答复后马上写回需求清单，再按定下的需求往下设计。
只问证据和工程判断解决不了的产品取舍；缺厂家资料、设计没做完、属于后续环节的事项不问。
任务 1.2–2.4 中途发现新的需求缺口，同样停在当前任务问，答复写回需求清单后从受影响的任务重做（会改变架构的回到 1.2）。
用户暂缓的，按建议条文作为写明的假设设计，相关需求和计算为有条件成立，记成 `requirement` 待办。
降额等级（I/II/III 级，见[降额规范](references/derating-rules.md)）是一条需求：需求没写时，与其他需求澄清一并问用户，
附按产品失效后果和工作方式给出的建议等级；答复写回需求清单。用户暂缓的，按建议等级作为写明的假设设计。
共用规范规则（G01–G09，与 schematic-review 同一版，见[共用规范规则库](references/guideline-rules.md)）按产品基线和本设计的功能电路类型、器件类别适用：
产品基线默认工业/通信板卡，需求写明航天、军用时按需求定；功能电路类型与器件类别随架构确定后补全。

做完的标志：`design-closure.json` 的每条需求有功能路径和承担器件（或写明理由的空列表）；每个需求澄清都有答复
（用户给定、采纳建议或明确暂缓），给定和采纳的已成为需求清单里的一条需求。有未答复的需求澄清不进入步骤 ②。
降额等级已定（需求给定、用户答复或写明的假设），记入 `design-closure.json`。
规则库有规则时，产品基线、功能电路类型与器件类别记入 `design-closure.json` 的 `guideline_scope`（`guideline_version: 1`）。

#### 1.2 系统架构

定出真实的系统架构：功能块及其电压域、电源与信号流向、板与隔离边界、接口，以及每条跨块流向代表的电源轨或信号
（RECT、BULK、FB/FAULT 光耦……）。它在任务 3.3 画成第 1 页 `System_block`，只有页面索引不算架构。
见 [reference-driven-board-design.md](references/reference-driven-board-design.md)。

做完的标志：每个功能块有输入输出和所在电压域；每条跨块流向有名字；隔离边界两侧各有哪些功能块已定。

#### 1.3 功能块做法

每个功能块先在 [功能电路模式库](references/circuit-patterns.md) 里找做法（`find_parts.py --patterns <功能>`）：
做法给出核心器件类、必需外围、必算项和已知坑；没有合适做法的功能块在 `lessons.json` 登记 `knowledge_missing`，设计完成后补写模式文件。

功能做法同时指出器件的设计用途、工作状态和需要核算的性能。放电、吸收、检流、限流、滤波等用途触发相应核算；“脉冲/浪涌”等关键词触发性能要求核验，不自动推出某个具体料号。普通器件可复用受控标准物料规范，仍须确认本设计工况在其适用范围内。

做完的标志：每个功能块有选定的模式与做法，或在 `lessons.json` 登记了 `knowledge_missing`；影响选型、替代或功能的器件用途与性能核算项已列明，交任务 2.2。

#### 1.4 核心器件选型与方案确认

- **先选型再核数据手册**：每个核心器件角色（控制器、协议 IC、功率开关、磁件、隔离/反馈器件、MCU）按
  [core-part-selection.md](references/core-part-selection.md) 找候选、比较并记录到 `record/selection.json`：
  至少两个候选、写明决定性条件和每个候选选中/淘汰的理由。原厂资料在本机知识库
  `~/Documents/知识库/HardwareWiki/raw/`（数据手册、参考设计、应用笔记），用 `scripts/find_parts.py` 检索；
  每类器件干什么、选它看什么参数见 [part-roles.md](references/part-roles.md)，从"按功能找类"定二级类再找候选。
  库里没有合适候选才外部检索，下载的手册按任务 2.1 的资料规则入库。
- **外部条件不确定时给出方案**：推荐候选依赖未公开的资料或行为（会产生外部资料待办）时，列出 2–3 个选型方案，
  比较各自的外部依赖、代价和优缺点，给出 ASG 的建议，交用户决定。用户定下来之前不进入步骤 ②。
  格式见 [core-part-selection.md](references/core-part-selection.md)。
- 核实决定架构的确切型号/固件能力；未证实的依赖保持条件状态，并评估替代实现。

做完的标志：`render_design_report.py` 的选型检查无问题：每个核心器件角色有候选比较，选定候选写了 `external_dependencies`，
不为空的角色有 2–3 个方案、ASG 的建议和用户的 `decision`（`user:<日期>`）。

### ② 详细设计

#### 2.1 数据手册核对与外围电路

本任务先从已确定的核心器件取得外围约束，记录参数的数值、条件、保证性质和出处，作为任务2.2的输入。外部电阻、电容等尚未选具体料号时，不填入未经核实的型号；后续依次完成性能要求和候选符合性。核心器件、物理引脚、固件身份及认证依赖的型号要求仍在本任务保留。

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
- **资料规则**：新下载的数据手册存入工程，同时复制到
  `~/Documents/知识库/HardwareWiki/raw/Datasheet/<分类>/<子类>/`，文件名为 `Vendor - PartNumber.pdf`
  （厂商简称按 `raw/Datasheet/VENDORS.yaml`，分类按 `raw/Datasheet/元器件体系/器件统一分类大表.md`，
  无分类放 `ZZ_其他` 并报告）。raw/ 中已有相同哈希或型号时跳过。只复制原文件，不改工程路径，
  也不触发知识库入库。`pack_design.py` 核对 `datasheets` 目录里的每个 PDF 都已在库内（同哈希或同文件名），没入库的拒绝打包。
  参考设计和评估板手册放 `raw/Designexample/<拓扑>/<板名>/`，
  文件名为 `Vendor - BoardName - Title.pdf`；应用笔记和标准不放 Datasheet 目录。

做完的标志：每个核心器件在外围电路核对表 `reference-input.json` 里有引脚表与外围检查，核对通过或列出资料不足的项；
分立器件的符号含义与料号一致；新数据手册已入库（`pack_design.py` 的入库检查通过）。

#### 2.2 设计计算与性能要求

- 数值计算按 [calculation-preflight.md](references/calculation-preflight.md) 写明保证条件；按
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
- **器件应力按降额等级核对**（按[器件应力规范](references/stress-spec.md)）：关键器件与特殊器件在工作包络角点和瞬态下的
  电压、电流、功率与温度应力，与额定比较的检查点名 `derating-rules.json` 里适用的规则，按本项目等级那一列取降额值；
  额定取最坏温度下的保证值。只给一个系数的项对稳态与瞬态的最坏组合生效，手册单列的冲击、脉冲额定按表中比例比较。
  常规件的规格写出的最低额定 = 最坏应力 ÷ 本级降额系数。只审写出来的应力，不要求每颗器件、每条规则都有一条比较。
  超过额定为 `failed`；在额定内但超过降额值为合格但有风险（应力），写 `improvement`（换额定更高的件或降低应力），
  列入报告的应力风险，不挡交付，不挂待办。
- **参数逐项有来源**：每条计算在 `design-closure.json` 的 `parameters` 里列出用到的每个参数：值、单位、依据（`basis`）、
  位号和手册定位（`datasheet:<库内路径>#p<页>` 加表名/符号）。依据另有 `requirement`（来自需求，`source` 写 `req:<需求编号>`）
  和 `constant`（物理常数），不再归入 `model`。手册没给的器件参数标 `unspecified`，不能写成保证值，
  也不能支撑 `supported`。格式见 [设计待办记录](references/design-closure.md)，`audit_design_closure.py` 核对。
- **按适用的共用规范规则设计**：规则卡的 `asg_action` 是设计动作；落实它的计算在 `guidelines` 里写规则编号，
  关闭阶段在原理图之后的规则用一件技术转交待办引用；确实不适用的写进 `guideline_scope.not_applicable` 并写理由。

**把计算落实为可采购的器件性能要求**：将实际需要核算的器件记入 `record/component-requirements.json`，由它统一生成设计网表属性、BOM规格和图面标注。字段及执行接口见 [器件性能要求](references/component-requirements.md)；新设计采用 `component_requirements_version: 1`，按用途分组筛选位号，不给每颗普通件增加全参数计算。
- 每项要求写明位号、用途、参数、比较方向、数值/范围、单位、适用条件、计算/需求来源及依据性质。额定值与降额后的可用值分开；设计要求与所选器件保证值分开。
- 放电电阻计算实际电流波形、起止电压和时间、峰值功率、单次电阻耗能、重复平均功耗及初始温度，给出能量/波形、重复间隔、累计次数及允许漂移要求；不能直接把电容总储能当作外部电阻实际耗能。采用保守上界或裕量分配时写明依据。
- 电容按用途核耐压、实际偏压/温度下的有效容量、纹波/ESR或脉冲要求；电感按用途核实际温度/偏置下的电感量、饱和/有效电流和损耗。只记录本设计依赖的性能，不要求每颗器件核所有可能参数。
- 合格标准料可引用受控规格及其适用工况，不强迫所有普通电阻逐颗比较供应商。不能用无来源的默认1%/0.125W补齐设计要求。
- 数据不足时，由ASG提出有依据的工程假设和暂定性能要求，保留有条件结论与实际缺口；本可计算却尚未计算的，仍是设计未完成，不能用“待采购确认”代替。

做完的标志：`audit_design_closure.py` 无错误；没有 `failed` 的计算；每条计算的结论、`rests_on` 与 `coverage` 与参数依据推出的一致。与额定比较的应力都点名适用降额规则；超降额未超额定按原规范列风险。每个已识别的性能核算项都有数值、条件和出处，或有明确的有条件要求与假设；仍缺可独立完成的计算时不得标记本任务完成。

#### 2.3 器件选型与性能符合性

输入为任务2.2的性能要求。逐项决定采购定义方式并核对来源：
1. **按规格采购**：性能可用完整规格定义的器件，采用受控标准物料或寻找符合要求的来源；未锁定料号时允许保留可采购性能规格，说明可行性依据，不把假设中的器件能力当成现成保证。
2. **按型号或设计单定义**：电路依赖物理引脚、接口/固件行为、认证、特定曲线或型号特性的器件，继续明确料号/订货变体/设计单，核对手册条件。安全认证与定制磁件要求不得因“按规格”而取消。
查阅原厂手册以核实候选，不自动意味着电路只能绑定该料号；可转为完整可替代性能约束的，优先保留规格采购方式。
3. **核对候选**：将要求值、候选保证值及双方适用条件逐项对照，记录资料来源、符合/不符合/尚未核实的结论。需要比较核心器件方案时仍执行任务1.4，不给所有普通料新增“两候选”义务。
4. **处理差距**：算出不满足时换料、调整电路或重新分配性能，并回到受影响计算。厂家保证缺失时保留真实外部依赖；不要先把候选写成已核准，再附一句“关键性能待确认”。
5. **记录状态**：性能定义是否完整、采购定义方式、候选是否已经核实分别记录。未核准的候选放入候选栏；“型号未定”“候选待核”“已核准”不能混用。按规格采购可以有多个经核准的来源。

做完的标志：每项性能要求都有采购定义方式和来源/候选处置；无已知不满足被当成满足，无未核实候选被当成已核准。尚缺外部数据的可有条件进入出图，但报告不能宣布其型号核实或设计定型已完成。

#### 2.4 设计网表

将任务2.2的唯一性能记录按位号关联到设计网表：生成基本值、性能规格、采购定义方式及选型状态，不在绘图/BOM脚本另写一套默认值。具体器件的标称参数与设计允许范围使用不同字段，不能把“要求容差≤5%”与“所选器件实际为±1%”误判为冲突。
准备脚本调用 `component_requirements.project` 和 `write_bom`，或运行 `audit_component_requirements.py --project-intent ... --write-bom ...`；记录不完整或候选未核准的，保留真实状态，不补默认料号。

写一份整板设计网表 `electrical-intent.json`：器件、网络 `{name: [ref.pin]}`、`no_connect`，以及每个器件的页面
`fields.Circuit`。格式和规则见 [requirements-to-intent.md](references/requirements-to-intent.md) 第 5 节。
每个物理引脚要么接入网络，要么有依据地标 NC。设计网表从需求和手册写出，不从草稿图回抄。
用 `net_roles` 区分 power/return/signal，至少覆盖电源轨与阈值/反馈等易混淆网络；声明 signal 后 recipes 禁止给它放电源符号。
只由连接器引入的电源或地、经一颗串联件从已有电源派生的供电网，在本任务逐网声明 `external_supply`、`filtered_supply`（任务 4.1 核对）。
电气改版先按 [change-preflight.md](references/change-preflight.md) 写生成前预检。

做完的标志：每个物理引脚接入网络或有依据地标 NC；`net_roles` 覆盖电源轨与阈值/反馈网络；
电气改版的生成前预检为 PASS 或 CONDITIONAL。

### ③ 原理图绘制

#### 3.1 分页方案

分页时给需要展示的性能要求分配位置：基本数值放元件旁，较长的条件放同页技术要求表或注释，用位号/注号对应。只显示设计与替代需要的信息，不把整段计算或数据手册搬到图上。表格和说明必须进入正常的布局与几何检查。

按功能、隔离/电压域和可读面积分页；几个很小的功能块合成一页，不单独占一张 A3。
为每页写一张简短的分页方案，内容包括：读者任务（跟随能量流、看懂反馈、追一个受保护接口……）、
功能块及每块的位号、主路径、电源轨、出页网络及目的功能/页码、标签边界。先保证一条功能路径易读，再决定拆页或加大纸张。
分页方案随交付保存为 `record/page-plan.json`（每页 `file`、`reader_tasks`、`blocks`、`patterns`），本页每个器件都要属于一个功能块，
每个功能块标注所用模式与做法 `"<模式文件名>#<做法名>"`（第一页是架构页，免标；没有模式的块要在 `lessons.json` 登记）；
图面审阅按它逐条追路径。见 [human-readable-routing.md](references/human-readable-routing.md) 第 1 节。
纸张在画完后定：内容能放进 A4 就用 A4；一页只剩零散小块时并页，不把小电路摊在 A3 上。

- 按拓扑选结构（Buck、LDO、隔离反激、滤波、MCU 各不相同），见
  [schematic-drawing-standards.md](references/schematic-drawing-standards.md) 第 2 节。不得为别的拓扑编造 SW 节点或电感级。
- 按绘图纲要 O1–O8 决定页面流向、锚点、器件归属、画法、出线、标签、间距和修复顺序，见
  [drawing-recipes.md](references/drawing-recipes.md)。

做完的标志：`render_design_report.py` 的分页方案检查无问题：每页的读者任务、功能块与模式齐全，每个器件属于一个功能块。

#### 3.2 图页脚本

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
- 间距只为通过检查而加大，通过后缩回：gap、stub、pitch、lead 和电源符号/标签引线超过 12 格（约 15 mm）
  会进结构审计，要么缩小，要么 `justify(对象, 理由)` 写明为什么需要这段间距；
  一页超过 3 处间距豁免本身就是审计不通过，改为折行或重新锚定。不得用加大间距把一页摊满。
- 先列真实 planned 局部网络名及其字号。在相应 series 段或 own-pin stub 放置前，显式用
  `max(原gap, s.name_run_steps(原net, font=原字号))` 预留直段，之后仍调用原 `s.name`。
  多段链逐段按真实网络预算；不得全局加gap、缩字、改名或用标签绕过连线。预算不证明无遮挡或 KiCad 字体覆盖。
- `build()` 遇到硬缺陷会直接报错。`report["structure"]` 必须为 PASS，`report["readability"]["gate"]` 必须为 PASS。
  失败时按 O8 改结构（方向、间隙、顺序 → 锚点 → 拆行）后重建，不得手调坐标打补丁。
  `report["readability"]` 还给出 `cell_coverage`（有东西的 25.4 mm 格占比）、`part_groups`（只靠标签/电源符号相连的器件组）
  和 `fits_paper`：覆盖率低、组数多于分页方案的功能块、内容能放进更小的纸张，都说明这页要并块、缩间距或换纸。
- 从 `component-requirements.json` 生成元件旁的基本规格和同页性能注释，不手工回抄。正式完成的图纸使用确定数值及适用条件；仍缺计算的审阅草稿明确标注“待计算”，不能凭此声明完成。
  长要求在页计划预留位置，用 `Sheet.performance_notes(at)` 生成；元件旁显示同页索引，普通隐藏属性不算图面表达。
- 性能要求使用“要求/至少/至多”等措辞；已核实的器件参数另标为器件额定或保证值。完整性能要求不能仅放隐藏属性、BOM或报告中，元件旁至少有可见规格或可见的同页要求引用。
- 图页脚本随交付版本一起保存；下一版只重生成有变化的页面。

做完的标志：每页 `Sheet.build()` 不报错，`report["structure"]` 与 `report["readability"]["gate"]` 为 PASS；每页间距豁免不超过 3 处。

#### 3.3 组装工程

多页工程用 `schematic_layout.root.Root` 组装根图：`page()` 放各页的层次图框，`flow()` 画带名字、两端落在图框上的流向线
（`kind="power"` 能量流、`"signal"` 控制链，线宽不同），`isolation()` 画隔离边界，`write()` 写出根图 `System_block`、
各页（实例路径改写到根工程）、`.kicad_pro` 和 `sym-lib-table`；文字压线或系统框图审计不通过时直接报错。
用法见 [drawing-recipes.md](references/drawing-recipes.md) 多页一节。
第 1 页 `System_block` 按任务 1.2 的架构画：每条流向线在线旁写出它代表的电源轨或信号，两端都落在页块、箭头或另一条线上；
隔离边界是一条写着“隔离”的直线，一次侧页块在一边、二次侧在另一边，不穿过任何页块。

做完的标志：`Root.write()` 不报错，写出根图、各页、`.kicad_pro` 与 `sym-lib-table`。

### ④ 设计检查

#### 4.1 自动检查

```bash
python3 <skill>/scripts/verify_schematic.py <root.kicad_sch> --intent electrical-intent.json \
  --out <新的空目录> [--expected-pages N] [--symbol-exceptions F] [--readability-waivers F] \
  [--reference-contract F] [--design-closure D --artifact-root R] \
  [--baseline-xml B --change-contract C --preflight P]
```

它一次完成：KiCad ERC / XML 网表 / PDF 导出，网表分区与器件身份逐脚对比设计网表（图上画出的网络名须等于设计网表里同一组引脚的网络名，
只允许页路径前缀；KiCad 自动网络名不比），层次与 PDF 页数，根图的系统框图检查（`system_block`：流向线有名字、两端有着落、隔离边界不穿块、每个页块有线到达，悬空线和无名箭头算 FAIL），
符号引脚完整性，分立器件符号含义与手册/型号后缀是否一致（`discrete_semantics`），可读性检查（零异网交叉、零三折以上两端连线、
内容放得进更小纸张的页算 FAIL），以及每个有效页面的几何检查，汇总到 `summary.json`。
只有全部检查项为 PASS 时结果才是 `AUTOMATED_PASS`。
可以用 `scripts/deliver.py <交付目录>` 一次跑完出图、自动检查到打包，参数记在 `record/deliver.json`，见 [交付与设计报告](references/delivery-report.md)。

- 新流程增加器件性能检查：核对用途对应的性能定义、数值/单位/条件/计算来源、选型符合性状态，以及设计网表/BOM/图面的一致性。相同规格不得分别硬编码在多个生成脚本中。
- 以KiCad导出的属性/XML核规格绑定，以实际PDF核可见内容及同页引用。仅字段存在、字符串匹配或“已生成”标记都不能证明图面已表达。检查器覆盖不到的图面对象明确转任务4.2，不自动判通过。
- 设计要求与候选实参分开比较：实际±1%可以满足“容差≤5%”，但料号实际±5%而“器件标称容差”写±1%属于信息冲突；MOV也不能被通用电阻模板覆写。
- 无料号但完整采用规格采购的器件，不仅因缺MPN判失败；确需型号绑定的器件缺料号，或关键性能缺失/自相矛盾，仍不得当作完成。厂家未给保证值与本可计算却未计算分开处理。
- 新设计提供 `--design-closure`，核对需求实现、外部依赖、计算覆盖和证据是否最新；格式与边界见 [设计待办记录](references/design-closure.md)。未提供时明确为 NOT_CHECKED，不能据此声明全流程完成。
- 新设计要求 ERC 零违规。重画工程时保留基线和最终两份原始 ERC，逐条确认没有新增违规，并披露继承的问题。
- ERC 摘要按原始报告的 UUID/object 对应实际层次实例、引脚及 KiCad 网络，再归因到电源轨；
  不凭位号或网络名文字猜问题对象。无法对应时保留原违规与待核边界，见 [project-verification.md](references/project-verification.md#erc-摘要对应到对象)。
- 几何检查只覆盖本次 KiCad 导出中已合格的对象，范围与未支持对象见 [native-geometry.md](references/native-geometry.md)；
  外部 JSON 回执不能授权放行。`geometry` 为 INSUFFICIENT 时保留缺口并在 KiCad 渲染图上核对，有限 PASS 不等于整案通过。
  库里隐藏的引脚号/引脚名不计；可见但无法由 KiCad 导出核对的引脚文字列在 `geometry.render_review_items`（图面待审对象），
  不算缺口，任务 4.2 图面审阅必须逐页覆盖这些对象并在 visual-review.json 里写明。
- 图面检查只有三种结果：PASS、FAIL（画图问题，如外框间距不足 1.27 mm、导线交叉不打点、注释压线）、
  INSUFFICIENT（检查器覆盖不到的对象）。FAIL 由 ASG 改图关闭，不交给人复核；可读性或几何 FAIL 时
  `pack_design.py` 拒绝打包。只有 INSUFFICIENT 缺口留给图面审阅核对。
- KiCad 自动生成的 `Net-(...)` 网络名不与设计网表比名；设计网表里的网络名必须显式标注在图上，与导出网表一致，见
  [project-verification.md](references/project-verification.md#自动网络名不比对)；
  编码斜杠层次字段只用 [schematic-drawing-standards.md](references/schematic-drawing-standards.md) 的有限回退，不推广。
- 工程的 ERC 规则不得设为忽略（`simulation_model_issue`、`footprint_filter` 除外），自动检查读取工程设置核对。
- 失败时修改相应图页脚本，在新的运行目录重新生成并检查。不得为了降低计数而加 PWR_FLAG、加排除项或改引脚类型。
- 受控的自动结构资格有两类，都在设计网表中逐网声明、用 `Sheet.power_flag()` 每网放一个 PWR_FLAG，由 `external_supply` 检查项核对：
  只由连接器引入、板上没有电源输出脚驱动的电源或地（`external_supply`）；经一颗串联电阻、电感、磁珠或保险丝
  从已有驱动的电源派生的电源脚供电网，例如 RC 滤波的模拟电源（`filtered_supply`，逐条列入设计报告）。声明格式与核对内容见
  [requirements-to-intent.md](references/requirements-to-intent.md) 第 5 节“连接器角色与外部供电”。
- 整流、变压器或分立稳压电路没有 KiCad `power_out` 时，不冒充连接器供电，也不修改器件引脚类型。
  先复核实际能量来源、回流路径、极性、启动和故障状态，再使用 [分立供电复核](references/reviewed-circuit-supply.md)
  的 `reviewed_circuit_supply`。该类是证据对应的人工供电语义结论；自动检查只核证据是否最新和 KiCad 拓扑，
  不自动证明电压、电流、效率或保护成立。未完成复核时保留 ERC，不凭降低计数批准标记。
- `symbol_integrity` 的 `unnamed_pins` 只作诊断（KiCad 运放、单门逻辑等符号的输入/输出脚按库惯例不写名字）。
  列出的每个器件（不限核心器件）都要在外围电路核对表里按数据手册名字逐脚对应，并在设计报告中列出这些脚；
  否则按引脚名核对时会对不上。

做完的标志：`summary.json` 没有 FAIL 的检查项，INSUFFICIENT 的逐条列出原因；导出网表与设计网表逐脚一致；ERC 零违规（重画工程无新增违规）。

#### 4.2 图面审阅

在实际PDF上逐页检查性能标注：位号/注号能对应到元件，参数、单位、条件及“要求/器件保证/待核”含义清楚，表格可读且未压线。按位号记录性能标注的核对结果；隐藏属性完整不代替这一步。

打开导出的 PDF，逐页按 `page-plan.json` 的读者任务追一遍：主路径、每个支持网络到对应引脚和正确的回流路径、
重复通道、每个地域和隔离跨越。每页记录的路径条数不少于读者任务数；“看过所有页”“与上一版像素一致”都不算证据。
`geometry.render_review_items` 里的图面待审对象逐条处置：每条处置写出在本版 PDF 上看到了什么
（引脚号在引脚外侧、引脚名未被导线压住……）；没改动的页面也按本版 PDF 重新审阅，不沿用上一版的处置。
`render_design_report.py` 核对每个图面待审对象都有处置，且处置不写“沿用”“同上一版”；`REVIEWED` 时 `pdf_sha256`
须是本版 `schematic.pdf` 去掉导出时间后的 SHA-256（`render_design_report.py --pdf-sha256` 给出）。
状态写 待返工（REWORK_REQUIRED）、待图面审阅（REVIEW_PENDING）或 已完成图面审阅（REVIEWED）。
用户否决会重新打开图面审阅。见 [human-readable-routing.md](references/human-readable-routing.md) 第 4 节。

做完的标志：`visual-review.json` 为 `REVIEWED`，每页路径数不少于读者任务数，每个图面待审对象有本版的处置，`pdf_sha256` 对得上本版 PDF。

### ⑤ 设计输出

#### 5.1 设计完成核对

还有可独立完成的设计项就回到对应任务做完，不以列出缺口代替完成。待办只由本版设计过程中确认仍需做的事项决定，不与上一版比较。

同时核对性能定义与选型状态：可独立完成的性能要求计算须完成；仅有料号但关键性能未核实的，不能写“已核准”。有条件性能要求和真实外部依赖继续按现有计算依据分类，不因图纸已输出而转成保证。

做完的标志：未关闭项只剩外部资料待办、技术转交、用户暂缓的需求和已登记理由的设计待办；没有未答复的需求澄清；审计列出的可执行设计动作都已完成；适用的共用规范规则都已在计算或待办里引用，或写明不适用的理由。

#### 5.2 经验总结

**写本版学到的东西** `record/lessons.json`：每条审查意见、每份改变了认识的手册页、每次用户纠正都是一个事件，
写来源（`review:<审查目录>/<待办编号>`、`datasheet:<库内路径>#p<页>`、`test:…`、`user:<日期>`）、归因
（`rule_missing`/`rule_not_enforced` 改 `scripts/`，`knowledge_missing`/`knowledge_wrong` 改 `references/` 或知识库，
`judgment` 写 `why_not_rule`）和改了哪个文件的哪一行；确实没学到的写 `cause: none` 并引用核对过的页码。
泛泛的总结不算，报告会拒绝。审查意见的归因同时写进 `review-responses.json` 的 `cause`，见 [处理审查意见](references/review-comments.md)。
技能或知识库改完后，在 `docs/improvement-ledger.md` 加条目（Event/Changed 两行，`scripts/check_ledger.py` 检查），
再跑全部合成测试。

做完的标志：报告不拒绝 `lessons.json`；技能有改动时 `check_ledger.py` 为 PASS，全部合成测试通过。

#### 5.3 报告与打包

交付增加 `record/component-requirements.json`，报告分别给出性能定义完整程度、选型核实状态和未关闭项；BOM及图面的可见规格由该记录生成。打包检查性能记录和图纸/BOM是否同源、最新、一致；完整规格采购、候选待核与型号已核准各自表述，不能统一写成选型完成。

- 按 [execution-evidence.md](references/execution-evidence.md) 写 `delivery-evidence.json`，报告前运行
  `scripts/check_delivery_freshness.py`；任何导出后的修改都会使旧结果作废。
- 交付目录只有下面四样，由 [交付与设计报告](references/delivery-report.md) 规定，`pack_design.py` 检查：

```
<交付目录>/
  设计报告.md     唯一给人看的文件：render_design_report.py 由记录生成，notes.json 的摘要与说明和记录按同一套专业术语写
  原理图/         KiCad 工程（根图、各页、项目符号库与封装库）、schematic.pdf、netlist.xml、BOM.csv
  设计资料/       跨版本有效、每版更新的设计文档（方案与选型依据、PCB与结构要求、磁件设计单等）
  record/         设计网表、分页方案、待办处理情况、自检结果、图面审阅、审查意见处理、本版用到的计算、
                  图页脚本、manifest.json（需求、原厂资料、前一版设计按路径+SHA-256 登记，不复制）
```

```bash
python3 <skill>/scripts/render_design_report.py <交付目录> [--notes notes.json] [--title 标题]
python3 <skill>/scripts/pack_design.py <交付目录> --input requirements=<需求目录> \
  --input datasheets=<资料目录> [--input previous=<前一版交付目录>]
```

也可以用 `deliver.py <交付目录>` 按固定顺序一次跑完生成报告、写交付证据、新鲜度检查和打包，见任务 4.1。
报告如实写出各项自检的 PASS/FAIL/INSUFFICIENT 及数量（含零）。历史版本快照、日志、仿真中间文件、
审查方的结果都不放进交付目录。

做完的标志：`deliver.py` 各步为 DONE、PASS、CONDITIONAL、INCOMPLETE 或 FRESH 且跑到打包，打包 PASS。

## 在任务流程中运行

由外部流程派发任务时，读 [任务输入输出格式](references/workflow-handoff.md)。
以 `task.json` 的需求、版本、前版设计和审查意见为输入；架构生成、查资料、计算与改图仍由 ASG 完成。
交付仍按任务 5.3 的目录；用流程提供的 `pack-result` 生成 `result.json`。独立使用本技能不依赖外部流程。

## 硬性规则

原则见「ASG 纲要」P1–P7；这里只列具体操作约束。

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
| 新设计/电气改版的设计待办记录、依赖与计算结论审计 | [design-closure.md](references/design-closure.md) |
| 收到审查意见：逐条处理、采用建议改法、收敛判断 | [review-comments.md](references/review-comments.md) |
| 交付目录、设计报告、打包检查 | [delivery-report.md](references/delivery-report.md) |
| 从需求写设计网表 | [requirements-to-intent.md](references/requirements-to-intent.md) |
| 需求没说清：问什么、什么时候问、答复怎样写回需求清单 | [requirement-clarifications.md](references/requirement-clarifications.md) |
| 架构页、参考设计外围、学习工程师图面 | [reference-driven-board-design.md](references/reference-driven-board-design.md) |
| 核心器件从哪找候选、怎么比较、`selection.json` | [core-part-selection.md](references/core-part-selection.md) |
| 技能怎样持续改进：事件、归因、台账、合成测试 | [docs/improvement-plan.md](docs/improvement-plan.md)、每版的固定动作 [docs/operating-cadence.md](docs/operating-cadence.md) |
| 每类器件干什么、选它看什么参数（按知识库分类） | [part-roles.md](references/part-roles.md) |
| 一个功能通常怎么实现、有几种做法、各自的必算项与已知坑 | [circuit-patterns.md](references/circuit-patterns.md) 与 `references/circuit-patterns/` |
| 选符号、引脚表、外围电路要求 | [symbol-and-peripheral-contracts.md](references/symbol-and-peripheral-contracts.md) |
| 计算条件记录 | [calculation-preflight.md](references/calculation-preflight.md) |
| 非线性极值、条件匹配与插值边界 | [worst-case-bounds.md](references/worst-case-bounds.md) |
| 共用规范规则（G01–G09）：规则卡、适用条件、引用与覆盖、下游约束（与 schematic-review 共用，同字节） | [guideline-rules.md](references/guideline-rules.md)、`references/guideline-rules.json` |
| 器件应力降额：I/II/III 级降额值、等级从哪来、取值规则、应力怎么判、查到什么程度（与 schematic-review 共用） | [stress-spec.md](references/stress-spec.md)、[derating-rules.md](references/derating-rules.md)、`references/derating-rules.json` |
| 绘图纲要 O1–O8 与 recipes API | [drawing-recipes.md](references/drawing-recipes.md) |
| 阅读路径、HR-01–HR-11、图面审阅 | [human-readable-routing.md](references/human-readable-routing.md) |
| 拓扑结构、标签策略、检查项 | [schematic-drawing-standards.md](references/schematic-drawing-standards.md) |
| 重画已有工程 | [existing-project-redraw.md](references/existing-project-redraw.md) |
| 电气改版与预检 | [electrical-redesign.md](references/electrical-redesign.md)、[change-preflight.md](references/change-preflight.md)、[project-verification.md](references/project-verification.md) |
| 对照工程师模板 | [engineer-template-comparison.md](references/engineer-template-comparison.md) |
| 交付证据与是否最新 | [execution-evidence.md](references/execution-evidence.md) |
| 用词 | [terminology.md](references/terminology.md) |
| Circuit IR、低层生成器 | [circuit-ir.md](references/circuit-ir.md)、[schematic-generation.md](references/schematic-generation.md) |

运行不需要上游完整仓库、新的 MCP 服务、Bun 或网络连接。
