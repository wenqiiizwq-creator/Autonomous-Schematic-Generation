# 此前问题点的改造闭环

Every entry from here on ends with lines the test suite checks
(`scripts/check_ledger.py`): `Event:` the review item, datasheet page, test
record or user correction that caused the change (a cited datasheet must exist
in the library and have the cited page); `Changed:` the files touched.
`Causes:` (how many items fell in each cause class) is an optional note. An
entry that changes the ASG 纲要 or the 绘图纲要 O1–O8 also carries `Approved:
user:<date>` and `Outline:` the hash from `check_ledger.py --outline-hash`.








## 整板评测门禁 A1/A4/A5：准则覆盖、defer 闭合、library_gaps 先检索（2026-11-07）

整板评测基线（ASG 128178e，三块板）发现纲要已有要求、脚本没执行的三处：
A1 `pack_design` 在 `guideline_uncovered` 非空时照样打包（Matrix 适用 366 条未覆盖 366 条，PoE 397 条未覆盖 366 条），现在拒绝打包，除非每条未覆盖准则在 `guideline_scope.not_applicable` 写了理由；
A4 `scheme-criteria.json` 的 `defer` 不核闭合（校准板“SM712 钳位对收发器总线额定”留给 2.2，CALC-RS485 没算，G04-005/G05-033 却挂在它上面），现在每个 defer 名要由引用该规则的计算里一项有结论的核对闭合（name 含该数值名，或核对的 `defer` 字段写它），否则报未闭合并点名只做了形式覆盖的计算；
A5 `library_gaps` 不核库里有没有（Matrix 复位块 U702 登记缺口，`multi-domain-reset` 正适用），现在开着的缺口按块名（与 `find_parts.py --circuits` 同样检索）和 target 文件名的英文词检索典型电路，命中的文件名要写进 reason 说明为什么不适用。
用三板归档副本重放：三处证据都被拦下，校准板 A1 不报。

- Event: test:评测记录/ASG/2026-11-07-wholeboard-128178e, user:2026-11-07（把你发现的这些问题，逐项都修正好，可以开多个分支对话完成）
- Changed: scripts/pack_design.py, scripts/render_design_report.py, references/delivery-report.md, references/typical-circuits.md, tests/test_design_report.py, tests/test_scheme_criteria.py, tests/test_lessons_v2.py, docs/improvement-ledger.md

## 谁做的决定：每个核心角色要有确认记录，答复人不得自拟，无人值守走任务书代答（2026-11-07）

整板评测基线 A2、A3、A6：校准板 10 个选型角色 `decision` 为 null 照样过（只在有 `options` 时查）；校准板与 Matrix 的澄清答复 `by` 写 `eval-run:auto` 也通过；Matrix 两个角色写 `user:2026-11-07`，同一对象却写着 `basis: eval-run:auto`。现在 `render_design_report.check_selection` 要求每个核心角色有 `decision`：`user:<日期>`，或 `scheme:<证据编号>`（引用户的需求或方案文档，`quote` 原样在文件里且含选定型号，不能是 ASG 自己写的 `设计资料/`、`record/`）；确认记录或澄清答复里出现运行者自拟标记（eval-run、auto、无用户、运行者、预先授权、代填）报 `decision_self_assigned`；澄清来源写“任务书”的，要在 `record/task.json` 的 `clarification_answers` 有一字不差的对应项（`delegate_without_task`、`delegate_mismatch`）。报告“核心器件选型”表加“确认来源”列。归档重放：校准板 10 个角色与 CL-SURGE-ZS、Matrix 两个冒填与三项澄清被拦；PoE 温湿度传感器的真实 `user:` 不报，其余 9 个运行者自认的角色报缺确认记录。改进 7（纲要，按 docs/决定来源与代答-草案-2026-11-07.md 实施）：新增第三种来源 `delegate:<代答人>:<日期>`，由 `task.json.delegation`（`by`、`date`、`scope` 取 clarification/selection、`rule: adopt_recommendation`、授权原文）授权；1.1 澄清、1.4 选型确认、② 中改变已确认方案三处统一接受，审计核对 `record/task.json` 里的授权与代答人、日期、范围一致，澄清只能采纳建议条文、选型只能选推荐方案；`user:` 选型确认要写 `locator`；报告摘要列出代答的各处与授权原文。SKILL.md 改 1.1 正文、1.4 选型确认与做完的标志、2.x“处理差距”末句。重放：校准板副本按合法代答改写后 11 处全部通过；PoE 副本补上 locator 后温湿度传感器通过。

- Event: user:2026-11-07（整板评测改进方案逐项修正，经主会话转达；草案：按草案实施）
- Approved: user:2026-11-07
- Outline: b13b0ce872252ae7
- Changed: SKILL.md, scripts/render_design_report.py, scripts/audit_design_closure.py, tests/test_design_report.py, tests/test_design_closure.py, references/core-part-selection.md, references/requirement-clarifications.md, references/workflow-handoff.md, docs/improvement-ledger.md, docs/决定来源与代答-草案-2026-11-07.md

## 纲要：2.2、2.4、5.1 加“对全部对象核对”（2026-11-07）

按已确认的草案（docs/纲要草案-对全部对象核对与状态表-2026-11-07.md）改 SKILL.md：任务 2.2 新增“同一判据对全部对象核对”一条；任务 2.4 做完的标志要求 `object_matrices.py` 列出的矩阵与状态表逐格有结论；任务 5.1 做完的标志加“矩阵与状态表没有缺结论或不满足的格”。打包门禁未改（pack_design 仍只拒绝 FAIL）。

- Event: user:2026-11-07（按草案改）
- Approved: user:2026-11-07
- Outline: 3f062fd197b39849
- Changed: SKILL.md, docs/纲要草案-对全部对象核对与状态表-2026-11-07.md, docs/improvement-ledger.md

## 整板评测改进 4、5：对全部对象核对的矩阵与保护逻辑状态表（2026-11-07）

整板评测基线（ASG 128178e）6 个漏项里 3 个是同一条判据只核了一个对象（Matrix 复位门限只对 STM32 的 2.0 V、没对 YT9218 的 3.135 V；−45 ℃ 存储只写“由器件额定覆盖”；低边防反接 MOS 断开地回路没有识别），1 个是软件正常关断时固件判据会不会误置锁没有列；校准板 SM712 钳位对收发器总线脚额定也没有比较。新增 `object_matrices.py`：从设计网表列出受监督轨门限 × 每颗负载、每颗器件工作/存储温度 × 需求范围、端口应力 × 路径上每颗器件（含回线被开关器件断开时经其他端口的地回路）、有锁存/关断/复位的块的状态 × 锁状态，逐格要结论；结论引用的检查要点名这个对象、核的是这条判据。closure 审计在 `matrix_version: 1` 时核对，缺格与不满足记 INCOMPLETE。用 Matrix 与校准板归档交付物重放：上述漏项都成了缺结论的格。纲要（2.2、2.4）改动只写了草案，待确认。

- Event: test:评测记录/ASG/2026-11-07-wholeboard-128178e
- Changed: scripts/object_matrices.py, scripts/audit_design_closure.py, scripts/render_design_report.py, scripts/README.md, references/design-closure.md, tests/test_object_matrices.py, tests/test_design_report.py, docs/纲要草案-对全部对象核对与状态表-2026-11-07.md, docs/improvement-ledger.md

## 清理矛盾 收尾：scheme-criteria 规则收为一处（2026-11-07）

`record/scheme-criteria.json` 何时必须有、字段与格式示例只在 typical-circuits.md 规则一节定义；delivery-report.md 原先独有的几条（guideline_scope 含关键电路类型时必有、key_blocks 必须比较、ports 与 typed-only 的引用范围、不代替 2.2 核算）并入该节，delivery-report 只留引用。

- Event: user:2026-11-07（scheme-criteria 相关规则全部收进 typical-circuits）
- Changed: references/typical-circuits.md, references/delivery-report.md, docs/improvement-ledger.md

## 清理矛盾 第 3 批：删除与合并历史文档（2026-11-07）

D8：删除 docs/shared-release-migration.md（M0–M4 验收记录，v1 指纹已取消；现行流程只在规范 README）和 docs/improvement-plan.md（阶段计划已实施或撤销，仍有效的七条原则与不做的事并入 operating-cadence）；execution-evidence.md 的快照检查并入 delivery-report 后删除；engineer-template-comparison.md 的通用部分并入 reference-driven-board-design.md、显式字段 API 并入 schematic-generation.md、TPS53355 个案移到 examples/tps53355_compact/README.md 后删除；upstream-integration.md 压缩为采纳清单（保留文件名供代码注释引用）；pdf-schematic-extraction.md 删去与 ASG 分页和标签规则相反的“重建/组织多页”与泛泛步骤；README 按五步列入口、共用层段改为指向规范源与 shared-layer.md；agents/openai.yaml 的默认提示补全五步范围。

- Event: user:2026-11-07（逐条裁决 D1–D8，按推荐执行）
- Approved: user:2026-11-07
- Outline: d1f85c57173a5323
- Changed: SKILL.md, README.md, agents/openai.yaml, docs/improvement-ledger.md, docs/operating-cadence.md, references/delivery-report.md, references/reference-driven-board-design.md, references/schematic-generation.md, references/schematic-drawing-standards.md, references/upstream-integration.md, references/pdf-schematic-extraction.md, examples/tps53355_compact/README.md

## 清理矛盾 第 2 批：去重与口径对齐（2026-11-07）

每条规则只留一处权威定义，其余改为引用：SKILL 主流程的需求澄清、外部依赖选型、应力判法、器件性能、间距与 name_run_steps、System_block、PWR_FLAG、图面审阅、lessons 细则改为指向 references；scheme-criteria 格式只在 typical-circuits（测试钉住的权威出处），delivery-report 改为引用并保留其独有规则；标签角色只在 HR-07；自动检查清单只在 SKILL 4.1；最弱档和降额数值改引用共用层 json。纲要两处只增修正：架构表①产出补 scheme-criteria.json，任务 1.4 补单候选例外。口径对齐：D1 等级未定按 unset_level 预判；D2 应力超幅按共用判法挂待办；D3 交接角色只留审查方实际读取的必需角色和 ASG 实际产出的归档角色；D5 共用规范 G01–G10（G10 降额与应力）；设计定型对应 SR 冻结准出；需求澄清写明与 SR 共享字段和 DEFERRED 差异；calculation-preflight 加两技能差异表（ASG 不设表达式上限，保持 2026-10-23 的决定）。

- Event: user:2026-11-07（逐条裁决 D1–D8，按推荐执行）
- Approved: user:2026-11-07
- Outline: 5c53a489bb6f3d72
- Changed: SKILL.md, docs/improvement-ledger.md, references/calculation-preflight.md, references/component-requirements.md, references/delivery-report.md, references/design-closure.md, references/drawing-recipes.md, references/human-readable-routing.md, references/requirement-clarifications.md, references/requirements-to-intent.md, references/schematic-drawing-standards.md, references/terminology.md, references/typical-circuits.md, references/workflow-handoff.md

## 清理矛盾 第 1 批：事实修正（2026-11-07）

按 ASG/SR/规范源三方排查修正与代码或现行规则不符的文字：交付目录允许 record/sr-review/（与 pack_design 一致）、外围电路核对表文件名统一为 reference-input.json、热可行性归入 2.2、台账两行、circuits 用“典型电路#实现方案”、选型在 1.4、MST/A* 只属低层后端、KiCad 版本归口 README、part-roles 改引用共用层 commodity-floors.json、删除对 SR 已不存在文件的引用、典型电路索引补 reviewed-bias-and-latch；任务 5.2 的“首版后用 SR 审”移到 operating-cadence（P6 边界）。

- Event: user:2026-11-07（逐条裁决 D1–D8，按推荐执行）
- Approved: user:2026-11-07
- Outline: de7a9e605793b9b2
- Changed: SKILL.md, README.md, docs/operating-cadence.md, docs/improvement-ledger.md, scripts/README.md, references/circuit-ir.md, references/component-requirements.md, references/core-part-selection.md, references/delivery-report.md, references/design-closure.md, references/existing-project-redraw.md, references/human-readable-routing.md, references/native-geometry.md, references/part-roles.md, references/project-verification.md, references/requirements-to-intent.md, references/review-comments.md, references/schematic-drawing-standards.md, references/schematic-generation.md, references/symbol-and-peripheral-contracts.md, references/typical-circuits.md

## 1.3 文字去掉库里没有的字段（2026-11-07）

9620a80 合入的 1.3 文字提到“相邻文件”“按文件的决定条件”“排除条件”“未比较”，这些是试点格式的字段，main 的库文件没有。改为：决定条件由 ASG 写出并给本板取值，对照每种候选的适用范围；库里候选不足时先检索知识库再比较。其余句子与做完的标志不变。

- Event: user:2026-11-07（把这个问题修正掉；按草案改）
- Approved: user:2026-11-07
- Outline: 804fb160cd9fd208
- Changed: SKILL.md, docs/improvement-ledger.md

## 1.3 候选比较记录与弱化典型电路库联动（2026-11-07）

用户只合入 typical-route 分支的 b060c50；它依赖的 c9dfc9d 只取代码部分：取消 `guideline_scope_circuit` 联动（`audit_design_closure.py`、`typical_circuits.py` 删 `claimed`），以及 `references/typical-circuits.md` 规则一节。试点的 3 个多方案文件、40 个文件的“方案覆盖”行、`find_parts.py` 决定条件检索、格式模板新增字段（决定条件、方案覆盖、相邻文件、排除条件、代价、可信度）都没有合入；评估见 `docs/典型电路库选型试点评估与架构建议-2026-11-07.md`。

- 任务 1.3：关键功能块在 `scheme-criteria.json` 写决定条件及本板取值、候选及来源、选中和淘汰理由；`check_scheme_criteria.py` 核单一可行说明、来源格式、未证实禁选、选定方案与页计划一致（无页计划时跳过）。
- 典型电路标注和 `library_gaps` 只要求关键块；页计划用 `key_blocks`、`circuits`。
- 库中电路类型和落实规则不再扩展本板 `guideline_scope`，适用准则的普通覆盖核对保留。必算项、已知坑、落实规则可不填全，来源要求不变；SR 坑回填改为“可以”。

- Event: user:2026-11-07（只合 b060c50，合进来之后不用重新跑）
- Approved: user:2026-11-07
- Outline: 26b87d409f77ae53
- Changed: SKILL.md, references/typical-circuits.md, references/typical-circuits/chassis-y-cap.md, references/delivery-report.md, references/design-closure.md, docs/operating-cadence.md, scripts/typical_circuits.py, scripts/check_scheme_criteria.py, scripts/render_design_report.py, scripts/audit_design_closure.py, tests/test_typical_circuits.py, tests/test_scheme_criteria.py, tests/test_design_report.py, tests/test_lessons_v2.py, docs/improvement-ledger.md


## 清理历史遗留：源数据已丢失的基准与已实现的草案（2026-11-06）

`overstrict_bench`、`delivery_replay`、`mutation_bench` 及其辅助（`bench_common.py`、`run_binding.py`、`incremental_delivery.py`、`incremental_deliveries.json`、`compare_calibration_runs.py`、`README-calibration.md`）依赖的 `~/Documents/ChatGPT/Auto-Development/ASG提升计划/` 历史十轮与第 2 批交付已不在本机，也找不到移动后的位置，M6 总验收记为 NOT_RUN，永远无法再跑；连同只测这些基准的三个测试一并移除。`README-calibration.md` 第一段（评测集案例的用法）保留为 `evals/README.md`。`docs/proposals/` 下 11 份草案均已实施或被取代、无任何引用；`docs/release-validation.md` 是 2026-09-15 的发布验证记录，已过时。以上都可从 Git 历史取回。

- Event: user:2026-11-06（“清理ASG、SR、设计规范，这三者里面的历史任务和历史遗留”）
- Causes: knowledge_wrong 1
- Changed: evals/README.md, evals/README-calibration.md, evals/overstrict_bench, evals/delivery_replay, evals/mutation_bench, evals/bench_common.py, evals/run_binding.py, evals/incremental_delivery.py, evals/incremental_deliveries.json, evals/compare_calibration_runs.py, tests/test_benchmark_run_binding.py, tests/test_benchmark_revision3.py, tests/test_auto_like_operator.py, docs/proposals, docs/release-validation.md, docs/improvement-ledger.md
- Gates: 1302 passed（移除的三个基准测试文件共 34 条）；check_ledger.py PASS

## M6：最终集成与过时入口清理（2026-11-06）

清理 README 中 M3/M4 尚待实施的过时说法，指向各自本地发布检查与显式评测入口。核查草案所列无用 SR_PASSIVE、G02 未接入/登记1.1、G06–G09 待接入和旧双向同步已在 M2/M3/M4 消除，不重复修改发布包或历史文字。N/E 当前入口局部更新，原有历史台账与记录保留；正式包仍为 1.9.4，工程输入与数值不变。ASG 历史回放输入缺失，按 NOT_RUN 独立披露，不作为 PASS。

- Event: user:2026-11-06（按关系梳理草案推荐方案完成更改，本批 M6）
- Causes: rule_not_enforced 1
- Changed: README.md, docs/improvement-ledger.md
- Gates: 不设配对变量：ASG 全量 1336 passed（499.43 s，无跳过），SR 全量 3078 passed（168.81 s，无跳过，5 条既有 warnings）；SR 官方 --changed aee8b4b --tier unit 260/260 KILLED（仅临时排序，未变异副本先通过）；M1665/M1666 独立功能变异 2/2 KILLED；SR 原生回放新约定13例195/195 MATCH、0 KNOWN/0 MISMATCH，父约定不改；ASG 历史10轮因缺源 NOT_RUN，不计 PASS；E 工具28 passed、规范工具4 passed、文档/最弱档 --check PASS；两边 check_ledger.py、diff --check、quick_validate PASS；十载荷与1.9.4同字节同指纹，N十八受控输入同快照。


## M5：显式绑定外部评测发布输入（2026-11-06）

E 校验、评测运行与打分显式选择准则发布包，ID/状态只读该包；核安装件一致，记录版/指纹/格式、E 提交与实际工作区、案例原件哈希、技能提交与字节身份。ASG prepare 不给答案且先写来源记录；SR 保存原始运行、成绩与汇总，清除测试替代准则并核实际计划。缺 E 单独报告外部评测 skip；旧成绩不自动晋升。只改评测与维护入口，不改五步、判断责任、准则或工程数值。

- Event: user:2026-11-06（按关系梳理草案推荐方案完成更改，本批 M5）
- Causes: rule_not_enforced 2, rule_missing 1
- Changed: docs/improvement-ledger.md, evals/eval_set.py, evals/circuit_cases/run.py, evals/README-calibration.md, tests/test_circuit_cases.py, tests/test_evaluation_binding.py
- Gates: ASG 全量 1336 passed（469.61 s，无跳过），SR 全量 3076 passed（155.45 s，无跳过、5 条既有 warnings）；不设配对变量；SR 官方 --changed aee8b4b --tier unit 258/258 KILLED（临时插件仅排序，未变异副本先通过）；新增 SR 6/6、ASG 2/2、E 4/4 独立功能变异 KILLED；E 工作区工具 28 passed、本批提交影像 25 passed；搬移 E 显式包校验 34 案例/96 测试点/100 板/0 错误；ASG 方案案例 1/1 hit，SR 自动层 1 hit/4 not_run；两边 check_ledger.py、diff --check、skill-creator quick_validate PASS；共用十载荷及规范18输入与1.9.4同字节。


## M4：分离工程身份与维护文字（2026-11-06）

工程指纹 v2 绑定八个受控工程文件的相对路径与哈希，纯说明和维护历史不进工程身份；十文件完整性不减。保留旧 v1 算法与身份校验，历史缺格式只解释 v1，新包下重生成计划/审计并复验，不静默重算或转移旧 PASS。替代输入绑定真实字节，修复 P15。新 ASG 审计和 SR 格式 8 计划明确 fingerprint_format，SR 历次架构决定同步；报告按记录显示身份。未改准则含义、工程数值或五步流程，未做 M5/M6。

- Event: user:2026-11-06（“按照这个草案的推荐方案，逐个完成这个草案的更改，都按照你推荐的方式来”；本批明确批准第 7 节 M4 行文字）
- Causes: rule_not_enforced 2, rule_missing 1
- Changed: SKILL.md, docs/improvement-ledger.md, docs/shared-release-migration.md, references/shared/guideline-criteria.json, references/shared/guideline-criteria.md, references/shared/shared-layer.md, scripts/audit_design_closure.py, scripts/guideline_criteria.py, scripts/render_design_report.py, shared-release.json, tests/test_engineering_fingerprint.py, tests/test_guideline_closure.py, tests/test_shared_release.py
- Approved: user:2026-11-06（批准关系梳理草案推荐方案，按草案第 7 节文字）
- Outline: 6cf0a9d8e914dd11
- Gates: 不设配对变量：ASG 全量 1333 passed（447.37 s，无跳过），SR 全量 3069 passed（115.16 s，5 条既有 warnings，无跳过）；SR 官方 mutation --changed aee8b4b --tier unit 252/252 KILLED，未变异副本先通过；新增 M1649–M1658 限定指纹/计划功能测试独立 10/10 KILLED（不跑实际安装件一致断言）；规范工具测试 4 passed；正式包 29 文件独立重建全等，两安装件 10/10 与正式包相同；旧发布 1.9.0–1.9.3 全部校验且字节保持；两边 check_ledger.py、git diff --check、术语/架构/阅读路径 PASS。


## M3：本地发布包独立校验与批准的依赖边界文字（2026-11-06）

按已批准草案第 4.4、6、7 节移除 D07/D08/D09 的对方源码、工作区/HEAD 读取及无用 SR_PASSIVE。各自核本地已安装包的十文件清单、版本、指纹与准则有效性；配对字节检查移入规范显式发布验收。原分类、应力、覆盖、BASIS 可达性与独立性测试保留，分类对照改为明确预期（全 25 类线索、原 15 引用例、全部本地 IC 角色排除负载），不再由另一技能给答案。指定 SKILL.md 段落逐字采用批准文字；项目基线可核代替另一安装目录必须同版，五步与判断责任不变。共用校验入口与说明变化按规范发布 1.9.3，保持现行指纹格式；M4/M5 不提前做。

- Event: user:2026-11-06（“按照这个草案的推荐方案，逐个完成这个草案的更改，都按照你推荐的方式来”；本批明确批准第 7 节 M1/M3 文字）
- Causes: rule_not_enforced 3, rule_missing 1
- Changed: SKILL.md, docs/improvement-ledger.md, docs/shared-release-migration.md, references/shared/guideline-criteria.json, references/shared/guideline-criteria.md, references/shared/shared-layer.md, scripts/guideline_criteria.py, shared-release.json, tests/test_component_requirements.py, tests/test_derating_audit.py, tests/test_derating_rules.py, tests/test_guideline_closure.py, tests/test_installed_release.py, tests/test_part_classes.py
- Approved: user:2026-11-06（批准关系梳理草案推荐方案，按草案第 7 节文字）
- Outline: d4f7e8be8d8d95d6
- Gates: 不设配对变量／对方读取不可用／对方为 1.9.0 三场景：ASG 各 1314 passed，SR 各 3047 passed、5 warnings，全部无跳过；SR 官方 mutation --changed aee8b4b --tier unit 126/126 KILLED（未变异副本先通过）；新增 M1644–M1648 只跑本地包功能测试、排除实际安装件一致断言后亦 5/5 KILLED；规范发布检查及生成测试 4 passed；两安装件与同一 1.9.3 包十文件相等；check_ledger.py、git diff --check、术语及阅读路径 PASS。


## M2：消除工程取值、词表与人读表的重复维护（2026-11-06）

按已批准草案第 4、6 节执行。SR 默认封装读取既有 assumed_resistor_package；双方分类定义只从本地词表读取名字/标题，分类线索、顺序及所有行为字段与 M1 逐项相等。规范准则条目和工程取值表从登记渲染，SR 三张最弱档数值表从 JSON 渲染，解释段保留。共用装载器增加元数据读取接口，故按发布流程安装 1.9.2；全部工程 JSON 除版本外相等，指纹格式不变。规范首轮生成纠正既有正文漂移（G05-031 动作、五条关闭阶段），未改任何登记；再次生成无差异。SKILL.md 留 M3。详见 docs/shared-release-migration.md。

- Event: user:2026-11-06（按关系梳理草案推荐方案完成更改，本批 M2）
- Causes: rule_not_enforced 3
- Changed: docs/improvement-ledger.md, docs/shared-release-migration.md, references/shared/guideline-criteria.json, scripts/guideline_criteria.py, scripts/schematic_layout/part_classes.py, shared-release.json, tests/test_shared_consumers.py
- Gates: ASG 全量 1294 passed（补齐已安装 Poppler 的 PATH 后，无跳过）；SR 全量 3028 passed、5 warnings；SR mutation --changed aee8b4b --tier unit 121/121 KILLED；新增 M1639–M1643 仅消费者/表格功能测试亦 5/5 KILLED；规范生成测试 1 passed、九份正文 --check PASS，SR 最弱档表重生成同字节；工程 JSON 除版本外全等；全部分类字段与顺序逐项相等；check_ledger.py、git diff --check PASS。


## M1：共用源收回规范并确定性发布 1.9.1（2026-11-06）

按已批准关系梳理草案方案 A 第 4、6 节：规范维护共用源及两个脚本，显式九份直接子登记与词表构建；确定性清单、持久输入快照、同版不覆盖、核清单后整批安装与失败回滚。生产默认固定安装包，替代输入显式声明测试模式；现有合成测试按原用途声明模式。两边从同一包安装，工程数据不变；SKILL.md、主流程和指纹算法不改，M2–M6 不提前做。SR 架构决定同步记录用户原话。验收、四个有意字节变化及回退见 docs/shared-release-migration.md。

- Event: user:2026-11-06（“按照这个草案的推荐方案，逐个完成这个草案的更改，都按照你推荐的方式来”；本批 M0/M1）
- Causes: rule_missing 2, rule_not_enforced 1
- Changed: README.md, references/shared/shared-layer.md, references/shared/guideline-criteria.md, references/shared/guideline-criteria.json, scripts/guideline_criteria.py, shared-release.json, tests/test_shared_release.py, tests/test_board_defect_guards.py, tests/test_derating_audit.py, tests/test_design_closure.py, docs/shared-release-migration.md, docs/improvement-ledger.md
- Gates: ASG 全量 1293 passed；SR 全量 3024 passed（5 warnings）；SR mutation --changed aee8b4b --tier unit 15/15 KILLED；新增 M1631–M1638 仅发布功能测试 8/8 KILLED；新增 20 项测试在旧码失败、最终两边通过；两边 check_ledger.py PASS；git diff --check PASS；ASG 术语与 SR 阅读路径 PASS；两位置完整发布目录同字节，快照重建同字节，十文件两边与发布件相同；原内容除 library_version 外全等；指纹 f62f9e757234 → 702e9b357e13。


## M0：固定共用层 1.9.0 发布输入（2026-11-06）

按关系梳理草案方案 A 归档现行十文件与 19 个持久构建输入，固定完整指纹、逐文件哈希及评测集实际工作区身份；不改载荷。验收与回退锚点见 docs/shared-release-migration.md 和规范 发布/1.9.0/manifest.json。

- Event: user:2026-11-06（按关系梳理草案推荐方案完成更改，本批 M0）
- Causes: rule_not_enforced 1
- Changed: docs/shared-release-migration.md, docs/improvement-ledger.md
- Gates: ASG 全量 1273 passed；SR 全量 3004 passed（5 warnings）；SR mutation --changed aee8b4b --tier unit 0 mutations（仅文档）；两边 check_ledger.py PASS；git diff --check PASS；归档输入重建 JSON 与安装件同字节，十文件与两边同字节，完整指纹 f62f9e757234。


## 撤销 Matrix 电源与保护 R3 后解除资料依赖（2026-11-06）

用户决定完全撤销该版本并重新开始。保留该事件触发的技能修复、知识和既有台账；只解除运行资料对撤销工程的依赖。

- `ideal-diode-hotswap.md` 的 TPS4800-Q1 改引库内原始手册；去掉特定工程的 47/68 µH 估算依据与入口主保护设计记录，分段模型和分离式耦合分析明确为工程推论，并引用各控制器手册。
- `high-side-quad.md` 改引独立保留的 TPS281C30 Rev C，去掉工程候选比较；删去“Rev B 与 Rev C 页码相同”的说法，启动短路峰值页码核为 p9。
- `chassis-y-cap.md` 去掉系统接地设计文档及撤销工程的接壳计算依据；源侧搭接和共模分流改为待本项目输入确认的推论，元件类别与整机抗扰的区别只引 VY1 手册。
- `efuse-bfet-short-latch.md` 去掉通道预检和输出负浪涌筛查记录，低压误判短路保留为由 TPS2663 故障与锁定模式推导的反例。
- 运行代码、既有合成测试、纲要及共用设计准则库不改；HardwareWiki 原始资料迁移及评测集的独立提交另行执行。

- Event: user:2026-11-06
- Changed: references/typical-circuits/ideal-diode-hotswap.md, references/typical-circuits/high-side-quad.md, references/typical-circuits/chassis-y-cap.md, references/typical-circuits/efuse-bfet-short-latch.md, docs/improvement-ledger.md
- Gates: 1273 passed in 436.16s（ASG_SR_SHARED_ROOT=/Users/skyfend/.agents/skills/schematic-review；Poppler 已在 PATH）；check_ledger.py PASS；git diff --check 通过；四份文档的 30 处手册引用可定位到库内文件；两技能共用层同字节且未改；既有台账条目逐字保留

## 任务 1.3 方案准则核对入口与 basis 性质核对（2026-11-06）

方案阶段重跑发现：PT100 记录读过格式说明仍使用自用字段，现有核对只在报告阶段运行；部分工程方法被标成 `standard`，核对未报问题。各项先写测试确认失败，再做最小修改。

- 新增 `check_scheme_criteria.py <设计目录>`，读取 `record/design-closure.json` 和方案准则记录，调用报告里的原有核对函数，打印问题并用非零退出码表示失败；PT100 原记录逐字节复制为测试夹具，格式正例通过，记录缺失或读不出来时报告问题。
- 按已确认文字，仅在 SKILL.md 任务 1.3 的“做完的标志”后加一句运行核对的要求。
- `basis: standard` 只接受规则卡 `nature: shall/should`，其余提示按实际依据改成 `requirement` 或 `inference`；格式说明补充工程方法/项目输入、绝对额定与推荐工作条件的区别，以及没有排除候选的规则放 `searched`。原格式正例继续通过。

- Event: test:评测集/运行结果/ASG/2026-11-05-km-analysis/scheme-criteria/rerun-main-a820e80；user:2026-11-06
- Causes: rule_missing 2, rule_not_enforced 1
- Changed: scripts/check_scheme_criteria.py, scripts/render_design_report.py, SKILL.md, references/typical-circuits.md, tests/test_scheme_criteria.py, tests/test_skill_steps.py, tests/fixtures/scheme-criteria/rt-afe-pt100.json, docs/improvement-ledger.md
- Approved: user:2026-11-06（AskUserQuestion 答复“照草案写入（建议）”）
- Outline: a8c8e1ea87150f50
- Gates: 1273 passed in 356.52s（ASG_SR_SHARED_ROOT=/Users/skyfend/.agents/skills/schematic-review；首轮 PATH 缺 Poppler 中止，补齐 PATH 后全量重跑通过）；新增 15 项测试，其中 13 项先失败后通过、2 项为 shall/should 正向对照；check_ledger.py PASS；git diff --check 通过；SKILL.md 仅加指定一句；references/shared/、R3 设计目录与准则登记未改

## G09 定稿的 ASG 接入项：BOM 装配状态列、MLCC 介质、swd-debug 落实规则（2026-11-06）

G09 定稿（2026-11-05）列的三项技能侧接入。代码类先写失败测试再修。

- G09-018：`bom_rows` 原来没有装配状态，不装位号只靠原生 DNP 属性。加 `Assembly` 列（“装”/“不装（DNP）”，与 `Orderable` 同为常量），不装的位号照常留在 BOM。闭合审计 `audit_placeholders` 新增 `dnp_in_value`：值里写 NC、N.C.、DNP、DNI、DNF、不装、未装（独立词，区分大小写，不误报 100 nF、NC7SZ125）记错。生成脚本已按 `dnp` 写原生属性且 `in_bom yes`，不改。
- G09-021：原有核对只要求常规电容写耐压、电感写额定电流，MLCC 介质没核。`part_classes.audit_identity` 对 MLCC 类常规电容加介质检查（C0G/NP0/U2J 与 X5R、X7R 等 EIA 代码，写在值或 `fields.Specification`）；电解等其他电容不要求。`requirements-to-intent.md` 写明介质与 `dnp` 写法。
- `swd-debug.md`：“落实规则：无”改为 G09-010、012、013、015，必算项补齐对应内容（针表对照工具要求、调试口地域与保护地、调试脚其他负载与复用、NRST 复位下连接与读保护后的恢复）；上下拉（G09-011，手册未写内部上下拉，不凭推断）与手接静电（G09-026）没写进做法，不列。

- Event: user:2026-11-05（G09 定稿：ASG 的 BOM 导出加装配状态列、MLCC 介质由脚本核、swd-debug.md 落实规则更新；见 原理图设计规范/维护/分项待办/G09_制造与可测试性规范/待完成任务.md）；user:2026-11-06（主会话转达：G09 接入项按同样规则做）
- Causes: rule_missing 2, knowledge_missing 1
- Changed: scripts/schematic_layout/component_requirements.py, scripts/schematic_layout/part_classes.py, scripts/audit_design_closure.py, references/requirements-to-intent.md, references/typical-circuits/swd-debug.md, tests/test_component_requirements.py, tests/test_calibration_board_issues.py, tests/test_typical_circuits.py, docs/improvement-ledger.md
- Gates: 1258 passed in 365.62s（ASG_SR_SHARED_ROOT=SR）；新增 4 条测试先失败后通过；check_ledger.py PASS；git diff --check 通过；SKILL.md 纲要与 references/shared/ 未改

## SKILL.md 任务 2.2 写明工况输入要有来源（2026-11-06）

审计（`operating_inputs.py`、`audit_design_closure.py`）和 `design-closure.md`“工况输入的来源”早已要求板外工况参数写 `input_role` 并有来源、启动计算声明启动期负载，但纲要任务 2.2 没写，设计方只在审计报错时才知道。按用户确认的草案逐字加一条。

- Event: user:2026-11-06（确认 SKILL.md 草案“照草案写入”；起因 Matrix R2 CALC-CH-START 把 1 A 启动负载写死，见 design-closure.md 同节）
- Causes: rule_not_enforced 1
- Changed: SKILL.md, docs/improvement-ledger.md
- Approved: user:2026-11-06（AskUserQuestion 答复“照草案写入（建议）”）
- Outline: ab575dfd17617a49

## Matrix R3 剩余技能事件：四个规则缺陷、资料规则残留、八条典型电路知识（2026-11-06）

R3 `record/lessons.json` 里尚未处理的 13 条事件逐条先核实再改（S07、S25、S29、S35 已在 main 修好，S15 随设计准则库 1.9.0 解决，S12、S19、S24 是判断类，不改技能）。代码类先写复现事件的失败测试再修。

- S06：`check_selection` 在设计网表写出（任务 2.4）之前不查位号绑定和“核心器件没有选型记录”，任务 1.4 只查候选、资料和用户决定；网表存在后照旧全查。`core-part-selection.md` 写明两段检查。
- S26：性能记录同一参数允许一条 `ge` 加一条 `le`（区间），唯一性改按（参数，比较符）；下限大于上限记错；核准件同一项 `properties` 要同时满足两条。`sheet_errors`/`record_errors` 由按参数建字典改为逐条要求。`component-requirements.md` 写区间写法。
- S27：`Sheet.pitch_for` 把可见的 `Performance` 字段（与 `generate.py` 同一可见条件）计入并排间距。
- S30：`banned_terms` 跳过术语表的表头行和 `|---|` 分隔行，`---` 与“不用的词”不再是禁词。
- S01：`requirements-to-intent.md` §4、`core-part-selection.md` §2、`docs/operating-cadence.md` 第 1 步改为按 SKILL.md 任务 2.1 资料规则存工程资料目录、设计期间不写知识库；测试禁止这几处旧说法再出现。
- 典型电路（只写有来源的内容，推论标“推论”）：`efuse-bfet-short-latch` 加启动即短路判据与状态表、输出端口浪涌矩阵及 5 条已知坑，并改正“手册不给 OUT 负向额定”的旧说法（S02、S08）；`efuse-aux-branch` 加输入反接与输出负压分开核（S08）；`ideal-diode-hotswap` 加短路峰值分段算法与 2 条动作时间坑（S10），新增“单管理想二极管 + 独立热插拔 + 两者之间取辅助电源”实现方案（S03）；`chassis-y-cap` 新增“源侧直流搭接 + 本板 R 并 Y 电容”实现方案（S04）；`fault-memory-comparator` 加低电平保证条件与接口备选、外推不构成保证（S05）；`high-side-quad` 加按变体核、两脚有符号差分额定、SNS 逐状态编码和启动高限流（S09、S20，写在智能高边开关的典型电路而不是 ideal-diode-hotswap，因为这些是高边开关自身的行为）。
- 核实中的出入：S10 所引 TPS4800-Q1 “p12 计时波形”实为 p11 图 6-1；TPS281C30 的 R3 副本是 Rev C，库内是 Rev B，所引页码两版相同，典型电路引库内版；TPS4800-Q1 未入库，引 R3 工程资料目录路径。

- Event: test:Matrix网络交换板/方案设计/电源与保护_R3/record/lessons.json（S01–S06、S08–S10、S20、S26、S27、S30）；test:Matrix网络交换板/方案设计/电源与保护_R3/record/evidence/research-excerpts/selection-stage-check.json；test:Matrix网络交换板/方案设计/电源与保护_R3/record/evidence/skill-events/range-parameter-rejection.json；test:Matrix网络交换板/方案设计/电源与保护_R3/record/evidence/skill-events/terminology-markdown-separator.json；test:Matrix网络交换板/方案设计/电源与保护_R3/record/recipe-reports.json；user:2026-11-06（主会话转达：R3 先不做，ASG/SR/准则相关先做完）
- Causes: rule_missing 4, knowledge_wrong 1, knowledge_missing 8
- Changed: scripts/render_design_report.py, scripts/schematic_layout/component_requirements.py, scripts/schematic_layout/recipes.py, references/component-requirements.md, references/core-part-selection.md, references/requirements-to-intent.md, references/typical-circuits/efuse-bfet-short-latch.md, references/typical-circuits/efuse-aux-branch.md, references/typical-circuits/ideal-diode-hotswap.md, references/typical-circuits/chassis-y-cap.md, references/typical-circuits/fault-memory-comparator.md, references/typical-circuits/high-side-quad.md, docs/operating-cadence.md, tests/test_design_report.py, tests/test_component_requirements.py, tests/test_terminology.py, tests/test_skill_steps.py, docs/improvement-ledger.md
- Gates: 1254 passed in 342.94s（ASG_SR_SHARED_ROOT=SR）；新增 6 条测试先失败后通过；check_ledger.py PASS；git diff --check 通过；SKILL.md 纲要与 references/shared/ 未改

## 1.9.0 覆盖层写回登记，覆盖层工具删除（2026-11-05）

合入 main 前把 `docs/registry-overlay-2026-11-05.json` 的 49 条修改（43 条 coverage、5 条 closing_stage+coverage、G05-031 动作与版本）在维护锁下写回准则登记（G05–G09 五份文件；写前九份源哈希与覆盖层一致，原文件备份在会话临时目录）。从登记直接 `build --library-version 1.9.0` 得到的规则库与 `references/shared/guideline-criteria.json` 逐字节一致。覆盖层文件、`scripts/build_registry_overlay.py` 和它的测试随之删除；`shared-layer.md` 那一节改为“已写回”，共用层指纹 430c93a02bbf → f62f9e757234（只改这段文字）。

- Event: user:2026-11-05（“修缺陷并升版”：合入 main 时写回覆盖层）
- Causes: rule_not_enforced 1
- Changed: references/shared/shared-layer.md, scripts/build_registry_overlay.py, tests/test_registry_overlay.py, docs/registry-overlay-2026-11-05.json, docs/improvement-ledger.md
- Gates: 1249 passed（配对 ASG_SR_SHARED_ROOT=SR integration）；check_ledger.py PASS；从登记重建与 1.9.0 逐字节一致；两边共用层同指纹 f62f9e757234

## Matrix R3 四个技能缺陷：离板单端网、候选物理身份、共地连接器误判隔离、报告门计数（2026-11-05）

R3 交付失败的门禁里有两项来自技能本身（R3 `record/lessons.json` S07、S25、S29、S35，复现证据在 R3 `record/evidence/skill-events/`）。每项先用最小合成输入写失败测试再修。

- S25：`audit_pin_dispositions` 对单端网络无条件报 `single_endpoint_net`。`boundary.audit_contracts` 新增可选 `verified` 集合，只收合同文件存在且表格有该网络行的离板网络；闭合审计把它传给 `audit_binding`/`audit_pin_dispositions`，只放过这些网络。未声明的单端网、合同不成立的声明（照旧另报 `boundary_contract_missing`/`boundary_net_not_in_contract`）和真正开脚照旧报错。
- S07：`project` 对按型号采购（`procurement.mode: mpn`）的候选不再删 `mpn`/`datasheet`，照写 `selection` 的料号和手册作为物理设计身份；采购状态由 `SelectionStatus: candidate` 和 BOM 新列 `Orderable`（“不可按此采购：候选待核，性能未核准”）表达；`audit` 对这类候选按候选料号核 MPN。按规格采购的候选、已核准件行为不变；身份审计未放松。
- S29：`safety_positions` 判跨隔离时，另一侧的 DC 域必须在板上接到本器件以外的器件；只连本器件一个脚或只在本器件脚间的网络（离板 PPS 针、同一连接器的普通离板信号）不算另一地域。真实隔离件（光耦、变压器、Y 电容）照旧判出。
- S35：报告 `GATES` 加 `design_closure`，`GATE_RESULTS` 加 `INCOMPLETE`（与 CONDITIONAL 一样有才显示），并断言各状态数之和等于门数。原有一条测试的期望值本身含此缺陷（summary 有 design_closure 却计 3 项），随之改为 4 项。

R3 副本只读重跑（集成基线 2ed02aa 对比本分支）：闭合审计 `single_endpoint_net` 6→0；按新投影重投 R3 交付网表后身份问题 57→0；共地 D 连接器跨隔离 6→0；报告顶部 11 项 0 失败 → 12 项 1 失败 1 未完成。

- Event: test:Matrix网络交换板/方案设计/电源与保护_R3/record/evidence/skill-events; user:2026-11-05 (主会话转达：修 S07、S25、S29、S35 四个已确认缺陷)
- Causes: rule_missing 4
- Changed: scripts/audit_design_closure.py, scripts/schematic_layout/boundary.py, scripts/schematic_layout/component_requirements.py, scripts/schematic_layout/part_classes.py, scripts/render_design_report.py, references/component-requirements.md, references/part-roles.md, tests/test_board_defect_guards.py, tests/test_component_requirements.py, tests/test_part_classes.py, tests/test_design_report.py, docs/improvement-ledger.md
- Gates: python3 -m pytest tests -q（配对 ASG_SR_SHARED_ROOT=SR integration）1 failed, 1239 passed in 380.44s；唯一失败 test_schematic_review_holds_the_same_shared_layer 是 SR integration 工作区未提交的 scripts/guideline_criteria.py 与本分支基线 2ed02aa 不同字节，基线导出同样失败，与本次无关；新增/改动测试所在四个文件全绿；scripts/check_ledger.py PASS；git diff --check 通过

## scheme-criteria.json 格式写到任务 1.3 读得到的地方（2026-11-05）

按 `2ce9f67` 重跑 10 题步骤 ①：10 题都生成了记录，但只有 2 题照规定字段写，多数没写 `basis`，因为格式只在 `delivery-report.md`，步骤 ① 不读。`typical-circuits.md`（任务 1.3 链接）加字段说明和例子，测试核例子能通过 `check_scheme_criteria`。纲要不变。重跑结果见评测集 `运行结果/ASG/2026-11-05-km-analysis/scheme-criteria/README.md`。

- Event: test:评测集/运行结果/ASG/2026-11-05-km-analysis/scheme-criteria/README.md
- Causes: rule_not_enforced 1
- Changed: references/typical-circuits.md, tests/test_scheme_criteria.py, docs/improvement-ledger.md
- Gates: 1238 passed in 467.66s（配对 ASG_SR_SHARED_ROOT=SR integration）；check_ledger.py PASS；git diff --check 通过

## 任务 1.3 关键功能块对照会淘汰候选的规则（2026-11-05）

规则库升到 1.9.0 后难题判据合计不变（9/19 对 9/19），`rt-hard-field-negative` 需要的 G07-022、G07-023 在运行日志里没出现：适用规则只在闭环时核对，选方案时不读。按草案 `原理图设计规范/维护/ASG方案阶段对照规则-草案-2026-11-05.md` 第 3 节逐字改任务 1.3 两处；`guideline_criteria.py select` 加 `--typed-only`（去掉全板通用规则）和 `--ports`（加回 G07 全板端口规则）；新记录 `record/scheme-criteria.json`，`render_design_report.py` 加 `check_scheme_criteria`、`render_scheme_criteria`，guideline_scope 含关键电路类型时必有，引用的规则须对该块适用，`basis` 区分需求、标准原文、手册绝对额定与工程推论，推论不作硬排除（用户 2026-11-05 原则）。闭环覆盖口径不变。SR 同字节共用脚本，对账清单只读块名和规则编号。

- Approved: user:2026-11-05（主会话转达原话：“分支对话的草案，请帮我批准，然后驱动分支对话修改草案”）
- Outline: e0d456d895a3df38
- Event: user:2026-11-05
- Causes: rule_not_enforced 1
- Changed: SKILL.md, scripts/guideline_criteria.py, scripts/render_design_report.py, references/delivery-report.md, tests/test_scheme_criteria.py, docs/improvement-ledger.md
- Gates: 1237 passed in 413.60s（配对 ASG_SR_SHARED_ROOT=SR integration）；check_ledger.py PASS；git diff --check 通过；共用层两边同指纹 430c93a02bbf

## G01–G09 运行包 1.9.0 与登记只读覆盖层（2026-11-05）

按 integration brief 升级；当前登记 534 条已不含指定排除的五个编号，故运行包为 534 而非 brief 预期 529，不再任意删规则。ASG 覆盖层锁定九份源哈希；G05-031 动作逐字采用批准草案、版本 1.1→1.2；五条 handoff 的关闭阶段按原文交接对象最小修正，正文不动。合入 main 时才把覆盖层写回登记，本次不写登记、不提交。共享层两边同字节。

只恢复 SKILL 的两处 G01–G09 表述，其余纲要不动。旧 DC_24V 选择测试增加 G07 四条，仍核 G01 不混入 −48 V 专用输入。覆盖层测试核可复现、源只读、源漂移拒绝及真实运行包逐字段匹配。

- Approved: user:2026-11-05
- Outline: 482b047d825d22fc
- Event: user:2026-11-05
- Causes: rule_not_enforced 2, rule_missing 2
- Changed: SKILL.md, references/shared/guideline-criteria.json, references/shared/shared-layer.md, tests/test_guideline_closure.py, docs/registry-overlay-2026-11-05.json, scripts/build_registry_overlay.py, tests/test_registry_overlay.py, docs/improvement-ledger.md
- Gates: 1227 passed in 396.37s (0:06:36)；check_ledger.py PASS；git diff --check 通过；配对 ASG_SR_SHARED_ROOT=SR integration；完整日志见指定 integration/实施说明.md。


## 设计准则覆盖方式 coverage：基线和交接批量覆盖，item 不放松 (2026-11-04)

加入 G07、G08 后 R2 适用准则从 185 升到 277，新增的很多只是项目基线输入或下游交接，逐条引用只会逼出批量凑数。准则加可选字段 `coverage`，缺省 `item`，行为不变。`project_input` 由 `guideline_project_input` 的 `baseline` 和 `answers` 一次回答（需求、需求澄清、`<基线>#<节>` 或 `TBR`），别处引用不能代替；`handoff` 由一件待办或一条证据覆盖多条，不要逐条 `guideline_evidence`。`item` 写进批量证据或 `answers` 记 `guideline_batch_mixed_item`；`guideline_evidence_repeated` 仍拦 `item`。`handoff` 的 `closing_stage` 不能是 `schematic`。报告把这两类各合成一张表。

校准板与 Matrix R2 的记录新旧代码审计输出逐字节相同（去掉 `shared_sha256` 后比）。库内容未改，分类和升版由主会话做。

- Event: user:2026-11-04 (主会话转达：规则库升版前让非逐条的准则批量处理，ASG、SR 只对原理图负责)
- Causes: audit_gap 1
- Changed: scripts/guideline_criteria.py, scripts/audit_design_closure.py, scripts/render_design_report.py, references/design-closure.md, references/shared/guideline-criteria.md, tests/test_guideline_closure.py, docs/improvement-ledger.md
- Gates: python3 -m pytest tests -q 1185 passed（配对 ASG_SR_SHARED_ROOT=sr-criteria-coverage）；scripts/check_ledger.py

## 工况输入的需求数值连单位一起核；多个候选值取不利值 (2026-11-04)

上一条的核对只比数字且接受 SI 换算，1500 µF 引只写 1.5 A 的需求能靠 1.5 通过；启动计算里没写 `input_role`、依据是 `requirement` 的负载电容则根本不核。现在数和单位一起比，同一量纲才换算前缀，范围下端取上端的单位，没有单位的参数只比数；负载电容按名字核时也包括 `requirement`。

同一条需求同时写 1.5 A 和 1 A、声明 1 A 仍能通过，这次不修：`design-closure.md` 写明多个候选值取不利值、理由写进参数，核对清单 `multiple_candidates` 和报告列出来由人看。

- Event: user:2026-11-04 (主会话转达：修掉数值核对不看单位的放行漏洞)
- Causes: audit_gap 1
- Changed: scripts/operating_inputs.py, scripts/render_design_report.py, references/design-closure.md, tests/test_operating_inputs.py, docs/improvement-ledger.md
- Gates: python3 -m pytest tests -q; scripts/check_ledger.py

## 设计审计核工况输入的来源：启动期负载硬检查，其余工况分层 (2026-11-04)

Matrix R2 的 CALC-CH-START 核“启动浪涌 ≤ I(OL) 下限”，浪涌＝负载电容充电电流＋写死在算式里的 1 A，参数名写“负载电容上限 + 1 A”，基准是 `derived`；这 1 A 没有来源，用户没被问过，换成需求的单路 1.5 A 约 2.14 A，超过下限 1.80 A，结论反了。G03-017 的 `inputs` 早已列出启动期负载，但 `inputs` 是自由文本，审计不读。

新增 `scripts/operating_inputs.py`，`audit_design_closure.py` 对 `parameter_version` 2、3 的记录都跑：
- 硬检查：参数写 `input_role` 就核来源（需求且文字写出这个数、手册页、有来源的推导；本板负载写 `load_refs`，用户暂缓走 `clarification`）；引用 G03-017 或对 eFuse、热插拔、负载开关做启动检查的计算必须声明 `startup_load`，浪涌值要是一个写了 `formula` 的参数，审计复算、不许写死的数、必须用到声明的负载；任何计算的名字和推导里“+ 1 A”这种没声明的数报错。
- 核对清单（不挡交付，报告“工况输入来源”）：按关键词把引用准则的 `inputs` 归成 8 类工况（354 条里 105 条有），不逐条维护。
- 回归：Matrix R2 副本从 INCOMPLETE 变 FAIL，新增 7 条错，1 A 以三种方式报出；工业校准板副本原有 4 条错，新增 2 条（同一条 CALC-INRUSH，浪涌检查值 1.29 A 里的逻辑电流没声明），都是真问题。

没改 `references/shared/`、SKILL.md。没有来源的判断只查有没有，查不出取错了（需求同时写 1.5 A 和 1 A 时声明 1 A 也过）。

- Event: user:2026-11-04 (用户确认要做，并推广到其他准则列出的输入)
- Causes: audit_gap 1
- Changed: scripts/operating_inputs.py, scripts/audit_design_closure.py, scripts/render_design_report.py, scripts/README.md, references/design-closure.md, references/requirement-clarifications.md, tests/test_operating_inputs.py, docs/improvement-ledger.md
- Gates: pytest tests/test_operating_inputs.py 26; python3 -m pytest tests -q

## 资料覆盖待办与知识问题分离，准确描述运行覆盖（2026-11-05）

按已确认草案 A、C 实施；B 等待 R3 后规则库升级。先用 schema 2 反例复现一条 knowledge_missing 全局放行两块，再加入 library_gaps 的逐页逐块绑定、文件/条目定位、closed 与页计划交叉检查；真实知识事件区分 observed 与 uncertain，覆盖待办不进事件索引。旧版与缺版本保留历史语义并标注未复核，不改冻结输入。新交付强制版本与受控历史身份尚无明确入口，保留兼容并如实列明限制，未扩展迁移工具。共用层不变。

- Event: user:2026-11-05
- Approved: user:2026-11-05
- Outline: 55065d7228ecfda1
- Causes: rule_not_enforced 1（全局豁免未绑定功能块）；judgment 2（覆盖待办混作问题归因、运行覆盖描述超出证据；用户确认修订）
- Changed: SKILL.md, references/typical-circuits.md, scripts/render_design_report.py, references/review-comments.md, references/delivery-report.md, docs/improvement-plan.md, docs/operating-cadence.md, tests/test_lessons_v2.py, docs/improvement-ledger.md
- Gates: 缺陷复现 1 failed in 0.06s；首次全量 1 failed, 1178 passed（5.2 段落位置触发任务结尾结构检查，移动原文后修复）；最终定向 121 passed in 8.33s；结构与台账 11 passed in 0.05s；最终全量 1185 passed in 361.95s (0:06:01)；check_ledger.py PASS；git diff --check 通过；冻结 helper ready=0，十轮回放 NOT_RUN，未改冻结输入。

## 电路评测集搬到规范目录，新增按电路跑的入口 (2026-11-05)

`evals/calibration_boards/` 搬到 `原理图设计规范/评测集/案例/校准板/`，与 SR 共用。新增 `evals/circuit_cases/run.py`：只把一个电路的需求摘录交给 ASG，案例答案不进工作目录。历史回放基准（overstrict、mutation、delivery）依赖本地冻结来源，不动。

- Event: user:2026-11-05 (能否将这些电路做成给SR和ASG两项技能进行评测和改进的，专门的评测集合？放在电路设计规范里。改现在的SR、ASG的架构)
- Changed: evals/eval_set.py, evals/circuit_cases/run.py, evals/calibration_boards/, evals/README-calibration.md, references/typical-circuits/chassis-y-cap.md, tests/test_circuit_cases.py, docs/improvement-ledger.md
- Gates: pytest 1148 passed；评测集不在时 test_circuit_cases 3 skipped

## IC 角色线索对齐 SR p24：protectioncontroller、surgestopper 归负载开关 (2026-11-04)

SR 修 Matrix R2 首审误报 1.11（LTC4367 被当线性稳压器问压差）时给 load_switch 角色加了两条手册标题线索；ASG `part_classes.IC_ROLE_CUES` 同步，保持两边分类线索对等（`tests/test_part_classes.py` 的包含关系测试）。

- Event: user:2026-11-04 (你用新修改的SR技能跑一遍修改好的R2…总结问题，发现SR技能的不足)
- Causes: knowledge_wrong 1
- Changed: scripts/schematic_layout/part_classes.py, docs/improvement-ledger.md
- Gates: pytest tests/test_part_classes.py 30

## 准则库 1.8.0：G05-098 外部锁存判据在正常动作下不成立、G03-017 加热插入负载；两个典型电路补 SR 审查坑 (2026-11-04)

SR 首审 Matrix 电源与保护 R2 发现两处 P1：通道命令关断时 EN_DLY 只随 SHDN 放电、PG 先变低，短路锁被误置（F-001）；已开通道热插入电容负载 PG 跌破门限、充回时间远长于消抖，锁被误置（F-002）。G05-060/063、G03-017 都没问到。用户 2026-11-04 批准写入：新增 G05-098"外部锁存判据在正常动作与允许负载下不成立"（POWER_PROTECTION，method；来源 TPS2663 SLVSE94G V(SHUTF)/tPGOODF/图 8-23，ECSS 4.2.1.1 n、5.7.4 f 方法延伸），G03-017 1.1→1.2 加"已开通道热插入允许负载"工况与输入；登记文件 G03 1.8、G05 1.4，共用层重建 1.8.0（354 条，指纹 ea8f1a727df3 → 9208f5369375），SR 同字节。典型电路 efuse-bfet-short-latch、fault-memory-comparator 落实规则加 G05-098，已知坑写 review:matrix/power-protection-r2/F-001、F-002。

- Event: user:2026-11-04 (写入)
- Causes: rule_missing 2, knowledge_missing 2
- Changed: references/shared/guideline-criteria.json, references/typical-circuits/efuse-bfet-short-latch.md, references/typical-circuits/fault-memory-comparator.md, docs/improvement-ledger.md
- Gates: pytest tests/test_typical_circuits.py tests/test_guideline_closure.py 24；合并后全量 1145（befe983）

## Matrix R2 回看：离板网络声明、单器件供电复核、应力超幅挂待办 (2026-11-04)

R2 跑完后找到的三处设计记录缺口。
一、离板网络：到 MCU 板的约 40 个网络只在一页出现，全局标签必报 `single_global_label`，R2 只好逐网画局部标签加理由。设计网表新增
`boundary_nets: [{net, to, contract}]`；`page_intents` 与 `Sheet` 把声明的网络算进 `external`（单页也画全局标签），`native.verify` 与
`verify_schematic.py` 只对声明网络豁免 `single_global_label`、`isolated_pin_label`（列为 `boundary_waived`），其余 ERC 照常；设计记录审计核对
接口合同文档存在、每个声明网络在其表格里有行（`boundary_contract_missing`、`boundary_net_not_in_contract`）。新模块 `schematic_layout/boundary.py`。
二、`reviewed_circuit_supply` 原来至少两个位号，R2 的 `SW_12`（LM70880 内部开关驱动）只好把 5 颗输入电容凑进去。现在允许单位号加
`basis: "datasheet:…#p"`，核对时按手册引用检查该页存在（页不存在记 `circuit_basis_citation`）；多位号写法不变。
三、应力超幅：R2 U701 估算结温 146 ℃ 对 II 级 95 ℃、额定 150 ℃，只报“合格但有风险”。新规则（阈值全取共用层）：项目等级比 III 严且应力超过
III 级降额值，至少要 P2 待办；离额定的余量小于估算所需（温度类取 G02 `est_junction_margin` 20 ℃，其他取检查的 `uncertainty`）要 P1。检查写
`work_item` 指向未关闭的 design/validation 待办，等级由其 consequence_class/occurrence 推出；缺了或不够记 error。报告“应力风险”节写明阈值和每处要求。
R2 副本复跑：U701 要求 P1、U401（短路重试平均结温 120 ℃）要求 P2，均因没挂待办记 error；U402（100 ℃，在 III 级 105 ℃ 内、余量 50 ℃）仍是普通应力风险。
把两处检查挂到 W-PROTO 并补 damage/fault 后这两条 error 消失。
共用层 stress-spec.md 写的是偏离“不另挂待办”，第三条是 ASG 设计记录在其上加的要求，未改共用层；是否同步到共用层与 SR 待用户定。

- Event: user:2026-11-04 (跑完这个ASG test并提交后，就开始修改你找到的这些问题)
- Causes: rule_missing 3
- Changed: scripts/schematic_layout/boundary.py, scripts/schematic_layout/native.py, scripts/schematic_layout/pages.py, scripts/schematic_layout/recipes.py, scripts/verify_schematic.py, scripts/schematic_layout/circuit_supply.py, scripts/audit_design_closure.py, scripts/render_design_report.py, references/requirements-to-intent.md, references/drawing-recipes.md, references/schematic-drawing-standards.md, references/design-closure.md, references/reviewed-circuit-supply.md, tests/test_boundary_nets.py, tests/test_reviewed_circuit_supply.py, tests/test_derating_audit.py, tests/test_design_report.py, docs/improvement-ledger.md
- Gates: pytest 1124 passed, 1 failed (test_guideline_closure 共用层与已装 SR 不一致：SR 已是 1.7.4、本分支 1.7.3，未改本分支同样失败)；几何类 11 项因并发 KiCad renderer 报错，空闲时单独重跑通过
## Matrix R2 问题修改：引脚表 type_note、性能标注按实际宽度、设计资料正文型号核对 (2026-11-04)

R2 跑完后找到的三处工具问题。（1）引脚表每个脚加可选 `type_note`（非空文字）：手册类型码怎么读成 `datasheet_type`（TI 的 `P` 功能栏写输出按 `PWR_OUT` 记）或符号类型为何不同，R2 只能写在 `设计资料/外围电路核对表.md`；`reference_contract.py` 接受并把它原样带进 `reference-contract.json` 该器件的 `type_notes`，`audit_design_closure.py` 只查非空（空记 `schema`），不放过 `pin_type_contradicts_datasheet`；`fill_pin_maps.py` 不写它。（2）`Sheet.performance_notes` 的 `width` 改为按几何检查的 `text_extent` 量的西文字符宽（中文约 1.24），不再按字数换行：换行的标题在 `pdftotext -layout` 里与旁边文字交错，PDF 核对就找不到这条标注；有一行超宽即在构建时报错，指出 CR、该行、多宽和够用的 `width`。测试样本用 R2 的 CR-R301（按字数 57 ≤ 60，量得 62.5 列）。（3）`pack_design.py` 加 `设计资料/*.md` 正文“位号 型号”核对：位号字母是设计网表用到的前缀、紧随的词含数字和大写字母且至少 4 个字符、不是带单位的数值、不是 Pin3/4 这类词加编号；位号不在网表、或型号与 mpn 对不上（忽略大小写和连字符，可省封装/变体后缀和 SN74 类前缀）即打包 error，带文件和行号；表格行和代码块不核。R2 的 9 份 Markdown 试跑：正文命中 14 处全部与网表一致，误报候选 J201 Pin3/4、Pin1/2 由“词加编号”规则排除，R301 3.3 等数值不算，表格行与代码块 39 处跳过；在副本第 22 行植入“U801 LM5060”即报出。
注意：工业 I/O 校准板 `record/scripts/draw_iio.py` 用 `width=48`，其 CR 标题量得最宽 61.2 列，重跑会在构建时报错，需改 `width=62` 以上（校准板只读，本次未改）。

- Event: user:2026-11-04 (跑完这个ASG test并提交后，就开始修改你找到的这些问题)
- Causes: rule_missing 1, rule_wrong 1, rule_not_enforced 1
- Changed: scripts/schematic_layout/reference_contract.py, scripts/audit_design_closure.py, scripts/fill_pin_maps.py, scripts/schematic_layout/recipes.py, scripts/pack_design.py, references/symbol-and-peripheral-contracts.md, references/design-closure.md, references/component-requirements.md, references/delivery-report.md, tests/test_board_defect_guards.py, tests/test_calibration_board_issues.py, tests/test_design_report.py, docs/improvement-ledger.md
- Gates: pytest tests 1101 passed, 12 failed；其中 11 个原生几何用例报 renderer configuration changed during job（并行 KiCad，干净 HEAD 同时同样失败），KiCad 空闲后单独重跑 39 passed + 7 passed；余 1 个 test_guideline_closure 共用层比对失败，因 SR 工作树有别的子任务未提交的准则库 1.7.4（本分支未动共用层）；改动相关 6 个测试文件 213 passed
## 同网同功能多脚改用 KiCad 叠脚编号 [a,b]，可见叠放记 overprinted_pin_numbers (2026-11-04)

R2 发现规则互相卡：引脚合同要求手册 PWR_OUT 的脚在符号里是 power_out；`symbol_integrity` 的 `hidden_power` 只认隐藏的 passive 副本（隐藏电源副本 INSUFFICIENT）；KiCad 只在同位置同名时豁免同网 power_out 互连；场景、符号完整性、电路 IR 又不认 KiCad 的叠脚编号。结果 TPS26630 OUT 17/18 只能可见叠放（PDF 引脚号叠印，R2 图面审阅记 9 处），LM70880 SW1～SW4 只能读成 power_in 再用 PWR_FLAG 和供电声明补来源。
定的规则（候选 a）：同网同功能多脚画成一个可见引脚，引脚号用 KiCad 10 叠脚写法 `[17,18]`、`[20-22,5]`，类型照手册。KiCad 10.0.7 实测：XML 按物理脚展开成同名同类型节点，ERC 当一个脚、不报互连，PDF 引脚号竖排不叠印；官方库已用这种写法。不选 (b)：隐藏电源副本仍要靠"同网"推断，图上看不到第二个脚号，且 ERC 仍会报同符号电源输出互连。
实现：`scene.physical_numbers` 解析叠脚号（逗号、带同一字母前缀的范围，空项/空格/逆序/重复拒绝），场景把叠脚展开成同一点上的各物理脚（`Sheet` 用 `U1.17`、`U1.18` 引用），`generate` 实例引脚按库引脚号写一次；`symbol_integrity` 按物理脚出行（`stacked_number`），XML 覆盖照常核；新加 `overprinted_pin_numbers`：显示引脚号的符号里几个可见引脚落在同一点即 FAIL；`circuit_ir.symbol_catalog` 也展开。旧的隐藏 passive 副本照旧，隐藏电源副本仍 INSUFFICIENT，提示改叠脚。
R2 副本验证：符号改 OUT [17,18]、SW [20-22,5]（power_out），去掉 SW_12 的 PWR_FLAG 与供电声明，引脚表 SW 四脚改 PWR_OUT + name_note；`deliver.py --for-review` 自动检查 ERC 0、符号完整性 PASS、引脚合同 PASS、供电声明 PASS，PDF 第 4/6/10 页引脚号竖排不叠印；用新代码审原 R2 图，9 个 TPS26630 记 `overprinted_pin_numbers`。

- Event: user:2026-11-04 (跑完这个ASG test并提交后，就开始修改你找到的这些问题)
- Causes: rule_wrong 1
- Changed: scripts/schematic_layout/scene.py, scripts/schematic_layout/symbol_integrity.py, scripts/schematic_layout/generate.py, scripts/schematic_layout/circuit_ir.py, tests/test_stacked_pins.py, references/symbol-and-peripheral-contracts.md, references/drawing-recipes.md, references/design-closure.md, docs/improvement-ledger.md
- Gates: pytest 1117 passed, 1 failed (test_schematic_review_holds_the_same_shared_layer：main 已是准则库 1.7.4、本分支 1.7.3，合并 main 后消失)；R2 副本 deliver --for-review：ERC 0、符号完整性/引脚合同/供电声明/几何 PASS（几何第 3 次重跑，前两次 renderer configuration changed）
## 自动检查误报与脆弱：分立件极性语义认 Unicode 减号与 TVS 后缀说明；几何检查遇配置变化自动重试 (2026-11-04)

Matrix 电源与保护 R2 的 discrete_semantics 17 处 INSUFFICIENT 全是误报：BSS123LT1 手册首页写 `N−Channel`（U+2212），正则只认 ASCII `-`；30KPA 系列手册单向/双向混排，前 3 页计数 4:5 判 ambiguous，而第 6 页订货说明写明 "CA Bi-Directional"。改为手册文字先把 `−‐‒–—` 等统一成 `-`；TVS 先读整本手册的后缀说明（行首代号 + Bi/Uni-directional，代号区分大小写），与料号后缀（30KPA28CA → CA）对上才判定，依据页码与句子写进 `evidence_page`/`evidence_text`，说明里没有该后缀或自相矛盾再回到前 3 页计数。
几何检查：同一任务的所有导出须见同一份配置，别的会话跑 KiCad 时报 "renderer configuration changed during job/between exports"（收尾时 "geometry configuration changed during job"）整版 INSUFFICIENT。改为删掉本次输出、按 30/60/90 s 等待后整任务重做（只重做单次导出不行，已做的导出用的是旧配置），最多 3 次，原因、变了的配置文件、等待写进 `context.json` 的 `retries` 和 verify 几何门禁的 `native_retries`，仍变才 INSUFFICIENT。查原因时发现每次启动 kicad-cli 都把 `kicad_common.json` 的 `system.working_dir` 改成自己的工作目录，多个工作树并发跑测试时它一直在变（第一次 R2 复跑 4 次全因此失败），这个键不影响渲染，算配置哈希时剔除。

- Event: user:2026-11-04 (跑完这个ASG test并提交后，就开始修改你找到的这些问题)
- Causes: rule_not_enforced 2
- Changed: scripts/schematic_layout/discrete_semantics.py, scripts/schematic_layout/native_geometry_context.py, scripts/verify_schematic.py, tests/test_discrete_semantics.py, tests/test_native_geometry_context.py, references/symbol-and-peripheral-contracts.md, references/native-geometry.md, docs/improvement-ledger.md
- Gates: pytest 1114 passed, 2 failed：test_guideline_closure 的 SR 共用层比对（SR 已是准则库 1.7.4，本分支从 2584064 分出仍是 1.7.3，与本改动无关，合并 main 后消失）、test_native_circle_controls 并发 flake（单独重跑 7 passed）；R2 副本 verify_schematic：discrete_semantics PASS、unresolved 0（checked 34），geometry PASS（并发下重试 1 次）
## 主流程加两处固定暂停点：1.4 选型确认、2.3 与已确认决定矛盾时停下 (2026-11-04)

Matrix R2 绘图时子任务把澄清与选型确认全推迟到报告里，①②里何时该停下来问设计师只靠任务书临时定。1.1 的需求澄清暂停点原本就有；补 1.4"选型确认（固定暂停点）"——选型清单汇总一次确认、用户 `decision` 前不进步骤 ②、与方案文档一致的只列不问、证明不成立的列为建议改动连证据问；补 2.3 第 4 点——处理差距要改用户已确认的器件方向/结构/取值时停在本任务，交 2–3 个改法由用户定，不自行换方案。草案 2026-11-04 交用户，答复"照此写入"。

- Event: user:2026-11-04 (照此写入)
- Approved: user:2026-11-04
- Outline: 7d2be268d7fbe45e
- Changed: SKILL.md, docs/improvement-ledger.md
- Gates: pytest tests/test_terminology.py tests/test_skill_steps.py tests/test_ledger.py 15

## 准则库 1.7.4：G03-025 加 STARTUP；chassis-y-cap 去掉 ISOLATION；电感类编号 (2026-11-04)

R2 绘图暴露的三处知识层问题：(1) G03-025（复位门限高于负载最低工作电压）适用类型不含 STARTUP，multi-domain-reset 做了核算却不能引用——HardwareWiki G03 登记表 1.6→1.7，G03-025 条目 1.0→1.1 加 STARTUP，共用层重建 1.7.4（353 条，指纹 d4c79a47c214 → ea8f1a727df3），SR 同字节；multi-domain-reset 落实规则加 G03-025。(2) chassis-y-cap 声明 ISOLATION，无隔离板引用它会把隔离器、RS-485 等 18 条准则拉进适用范围（R2 lessons knowledge_wrong）——电路类型改 无、落实规则改 无（G04-040 由隔离接口的典型电路落实），已知坑记录原因。(3) cot-buck、dc-24v-input-protection 的"24 功率电感"按 part-roles.md 改为"21 功率电感"。

- Event: user:2026-11-04 (跑完这个ASG test并提交后，就开始修改你找到的这些问题)
- Causes: rule_missing 1, knowledge_wrong 2
- Changed: references/shared/guideline-criteria.json, references/typical-circuits/multi-domain-reset.md, references/typical-circuits/chassis-y-cap.md, references/typical-circuits/cot-buck.md, references/typical-circuits/dc-24v-input-protection.md, docs/improvement-ledger.md
- Gates: pytest tests/test_typical_circuits.py tests/test_find_parts.py tests/test_guideline_closure.py tests/test_calibration_board_issues.py tests/test_design_closure.py 139；全量在合并修改分支后跑

## Matrix 电源与保护 R2：补写 9 个典型电路（第四批） (2026-11-04)

R2 任务 1.3 在 `lessons.json` 登记了 9 个没有典型电路的功能块（knowledge_missing），设计完成后补写：hotswap-latch-powerlimit（LM5069 类锁定热插拔 + 开漏管保持 UVLO）、efuse-aux-branch、internal-comp-buck、dcs-low-voltage-buck、ext-comp-current-mode-buck、ovp-cutoff-efuse、efuse-bfet-short-latch、fault-memory-comparator、multi-domain-reset。每个文件一种实现方案，按器件类写，必算项对应 R2 的 CALC-* 与 calculation-preflight 的类型，落实规则只写实现方案确实做到的 active 准则（环路裕量 G03-007～009、负载跃变 G03-026、保护链协调 G05-020 等 R2 交样机或没算的不引），已知坑 4～8 条全部引手册页（`datasheet:…#p`）或 R2 设计记录发现（`user:2026-11-03`，括注计算编号）。索引加第四批表，测试计数 31→40，已知坑来源检查覆盖新 9 个。
未决：multi-domain-reset 只能引 G04-010——G03-025（复位门限高于负载最低工作电压，R2 CALC-RESET 做了）的适用类型不含 STARTUP，是否给它加 STARTUP 待用户定（准则库改动）。

- Event: user:2026-11-04 (现在开始补ASG典型电路库缺的 9 个功能块)
- Causes: knowledge_missing 9
- Changed: references/typical-circuits/hotswap-latch-powerlimit.md, references/typical-circuits/efuse-aux-branch.md, references/typical-circuits/internal-comp-buck.md, references/typical-circuits/dcs-low-voltage-buck.md, references/typical-circuits/ext-comp-current-mode-buck.md, references/typical-circuits/ovp-cutoff-efuse.md, references/typical-circuits/efuse-bfet-short-latch.md, references/typical-circuits/fault-memory-comparator.md, references/typical-circuits/multi-domain-reset.md, references/typical-circuits.md, tests/test_typical_circuits.py, docs/improvement-ledger.md
- Gates: pytest tests/test_typical_circuits.py tests/test_find_parts.py 21

## 资料规则：项目手册留在工程资料目录，打包不再拒绝，交付后提示入库 (2026-11-04)

Matrix 电源与保护 R2 打包时因 LTC4359、LTC4367、30KPA、PSMN1R4-100ASE 四份手册不在 HardwareWiki 而 FAIL，设计子任务按"知识库只读"的约束停下来等人。用户定：当前设计项目用到的手册放在当前工程的资料目录就够，设计完成后再提示用户放进 HardwareWiki。任务 2.1 资料规则、2.1/5.3 做完的标志与 delivery-report 照改；`pack_design.py` 不再因手册不在库拒绝打包，改为把不在库的列进 `manifest.json` 的 `datasheets_to_file` 并打印 `TO_FILE:` 行，`deliver.py` 据此多一步"手册待入库 N 份"；核对规则（同哈希或同文件名算在库）不变。

- Event: user:2026-11-04 (这个规则现在先改成，在当前设计项目里面用到的手册，放到当前设计项目的元器件手册里面就可以。在设计完了之后，提示用户要放到hardwarewiki里面)
- Approved: user:2026-11-04
- Outline: 381fc9fb3f368e47
- Changed: SKILL.md, references/delivery-report.md, scripts/pack_design.py, scripts/deliver.py, tests/test_design_report.py, docs/improvement-ledger.md
- Gates: pytest tests/test_design_report.py tests/test_deliver.py tests/test_delivery_freshness.py 95

## 工业 I/O 校准板：W-BUCK-RIPPLE 按 LM5160 式 8 复核，典型电路 cot-buck 补纹波注入必算项 (2026-11-03)

校准板 LM5160 Type 3 纹波注入（R206 100 kΩ、C206 1 nF、C207 100 nF）原按参考值取、留了 W-BUCK-RIPPLE。新计算 `CALC-BUCK-RIPPLE` 按手册 SNVSA03E 8.1.1 Table 3 式 8（p16，本版手册在 8.1.1 而非 7.3）与 TI AN-1481（SNVA166A，2013-04 修订，从 ti.com 取得）p8 核：20.4 V、TON 保证下限外推、CA +20 %、分压泄放下 FB 注入斜坡最小约 75 mV ≥ 25 mV，RA·CA 121 µs ≤ 式 8 上限 380 µs，CB×(R204∥R205)×fSW 约 113 ≥ 5，CB/CA 约 67 ≥ 3，输出纹波峰峰上限约 22 mV、5 V 带 4.87～5.11 V 在 ±5 % 内；器件不改，W-BUCK-RIPPLE 关闭。`cot-buck` 必算项加“注入斜坡最小幅值对 25 mV、CB 交流耦合”，已知坑写明方程位置与 CB 取值来源。

- Event: user:2026-11-03 (这两件事也做了)
- Causes: knowledge_missing 1
- Changed: references/typical-circuits/cot-buck.md, docs/improvement-ledger.md
- Gates: pytest tests/test_typical_circuits.py 10

## 工业 I/O 校准板：SR 四件取舍落地、引脚表自动填 (2026-11-03)

用户定的四件按建议落地：D102/OV 窗记为已知边界（需求 C17）；FIELD+ 按直流电源口核浪涌（C18），`CALC-FIELD-SURGE` 算出原设计 D602 线-线约 160～215 A，加 R602 22 Ω 抗浪涌电阻、C601 改 100 µF 铝电解后 D602 27.5 A、V24 脚 33.5 V；
DI 输入 `CALC-DI-PIN-SURGE`：SN65HVS883 无内部钳位、IPx 约 59.7 V，每路加 30 V±2 % 稳压管后 IPx ≤33.1 V；U401 保留预量产 XISOW3080PDWER，交接待办 `W-U401-PRODUCTION`；W-SR-DECIDE 关闭。
新增 `scripts/fill_pin_maps.py` 从手册引脚表填 `datasheet_name/datasheet_type/datasheet_page`（校准板 239 脚填全 165 脚，binding 试跑 505→199 条，余下按类别列出），`reference_contract.py` 允许 `datasheet_page`。
画 DI 页时修 `recipes.Sheet` 重复支路检查（按锚点分组比较）；打包白名单加 `record/sr-review/`；典型电路 `industrial-di-serializer` 补必需外围与已知坑；核心选型加预量产料号的登记要求。详见 `docs/proposals/calibration-decisions-2026-11-03.md`。

- Event: user:2026-11-03 (按建议执行)
- Causes: rule_missing 2, rule_not_enforced 1, knowledge_missing 3
- Changed: scripts/fill_pin_maps.py, tests/test_fill_pin_maps.py, scripts/schematic_layout/reference_contract.py, scripts/schematic_layout/part_classes.py, scripts/schematic_layout/recipes.py, tests/test_drawing_recipes.py, scripts/pack_design.py, tests/test_design_report.py, scripts/README.md, references/symbol-and-peripheral-contracts.md, references/design-closure.md, references/delivery-report.md, references/core-part-selection.md, references/typical-circuits/industrial-di-serializer.md, docs/proposals/calibration-decisions-2026-11-03.md, docs/improvement-ledger.md
- Gates: pytest 1108
## 准则库 1.7.1：G04-091 的 WCH 出处核过原件；86 块板待采集资料并入清单 (2026-11-02)

从 WCH 官方 GitHub `openwch/ch32v307` 取得 `EVT/PUB/CH32V30xSCH.pdf`（V3.0，提交 bb6ee13，2026-04-16），第 9 页 ETH 区 HR911105A 中心抽头 4/5 共接 3V3、C14=0.1 µF 属实；G04-091 的 `source.edition` 由"版次未核"改为核过的版次，条目版本不变，G04 登记文件 1.3，共用层重建为 1.7.1（353 条）。86 块板暴露的 31 项待采集资料并入 `evals/calibration_boards/datasheets-to-collect.md`。

- Event: user:2026-11-02 (再帮我执行"已识别但没做的改进")
- Causes: knowledge_missing 1
- Changed: references/shared/guideline-criteria.json, evals/calibration_boards/datasheets-to-collect.md, docs/improvement-ledger.md
- Gates: pytest 1096
## 准则库 1.7.3：G03-023、G05-090 适用类型加 HOLD_UP (2026-11-03)

用户 2026-11-03 定（"这两件事也做了"）：共用词表有了 `HOLD_UP` 后，掉电保持相关的两条准则补上适用类型——G03-023（须保持的轨在中断期间的保持电容满足保持时间）与 G05-090（输出可能高于输入的支路有反向电流阻断）的 `applies_when.circuit_types` 各加 `HOLD_UP`，条目版本 1.0→1.1；HardwareWiki 登记文件 G03 1.6、G05 1.3，正文块与文末版本说明同步；共用层重建为 1.7.3（353 条），指纹 48c61bb3a5e7 → d4c79a47c214，SR 同字节。典型电路 `hold-up` 仍声明三种类型，因其余 4 条落实规则只按 POWER_CONVERTER/POWER_PROTECTION 选出。

- Event: user:2026-11-03 (这两件事也做了)
- Causes: rule_missing 2
- Changed: references/shared/guideline-criteria.json, docs/improvement-ledger.md
- Gates: pytest 1109（合并 calib-ripple 后在 main 上跑）

## 共用层同步 1.7.2：词表加 HOLD_UP、SIGNAL_PROTECTION (2026-11-03)

SR 合并步 7（用户 2026-11-03"按建议执行"）在共用词表 `circuit_types` 加 `HOLD_UP`（掉电保持）和 `SIGNAL_PROTECTION`（信号端口保护），准则库重建为 1.7.2（353 条，条款与 1.7.1 逐条相同），指纹 3e50da53d0b5 → 48c61bb3a5e7；本仓库同字节复制。典型电路 `hold-up` 的电路类型加 `HOLD_UP`，仍保留 POWER_CONVERTER、POWER_PROTECTION，因为它落实的 G03-023/024/025/038/039、G05-090 目前只按这两类选出；准则适用类型是否加 HOLD_UP 留给人定。

- Event: user:2026-11-03 (按建议执行)
- Causes: rule_missing 2
- Changed: references/shared/vocabulary.json, references/shared/guideline-criteria.json, references/typical-circuits/hold-up.md, docs/improvement-ledger.md
- Gates: pytest 1109

## 纲要第 3 处文字改动：引脚表先用 fill_pin_maps.py 批量填 (2026-11-03)

`docs/proposals/calibration-closeout-2026-11-02.md` 第 5 节建议 1 经用户确认后写入 `SKILL.md`：任务 2.4 做完的标志的 `binding_version 1` 括注里加"引脚表的手册引脚名与类型先用 `scripts/fill_pin_maps.py` 从符号库和手册引脚表批量填入，填不上的再逐脚补"。工具 `fill_pin_maps.py` 由校准板取舍落地一步交付（校准板 505 条错误降到 199 条）。

- Event: user:2026-11-03 (照此写入)
- Causes: rule_missing 1
- Changed: SKILL.md, docs/improvement-ledger.md
- Gates: pytest 1108（合并 calib-decide 后分支内跑）; check_ledger PASS
- Approved: user:2026-11-03
- Outline: 610dc3ae3c86f99d

## 纲要 2 处文字改动：交付后 SR 审查进典型电路、文档类准则挂证据条目 (2026-11-03)

`docs/proposals/calibration-closeout-2026-11-02.md` 第 5 节的建议 2、3 经用户确认后写入 `SKILL.md`：任务 5.2 加"首版交付后用 SR 审一次本板，审查发现按本节归因；落在某个典型电路上的坑写进该典型电路的已知坑，来源写 `review:calibration/<板>/<编号>`"；任务 5.1 做完的标志改为"已关闭的待办引用的每条准则指到落实它的证据位置；文档类准则可直接挂在接口表、工况矩阵、FMEA 等证据条目的 `guidelines` 上，不以一件待办批量引用代替"。审计同步认 `evidence` 条目的 `guidelines`（覆盖记 `evidence:<编号>`，形状错记 `schema`），`design-closure.md` 同步。建议 1（引脚表自动填路径）待工具落地后再写入。

- Event: user:2026-11-03 (照此写入)
- Causes: rule_missing 2
- Changed: SKILL.md, scripts/audit_design_closure.py, references/design-closure.md, tests/test_guideline_closure.py, docs/improvement-ledger.md
- Gates: pytest 1098（全量跑时 1 条原生几何测试受并行 KiCad 作业干扰失败，单独重跑通过）
- Approved: user:2026-11-03
- Outline: 4677fc2a4c53216d

## 工业 I/O 校准板收口：SR 审查归因、W-DOC 逐条证据、第三批典型电路 12 个 (2026-11-02)

用 SR 按完整流程审了校准板（856 项检查、42 个功能框架；板子回路深度，门禁不 valid），22 条发现归因：真缺陷 3（D501 料号不在订货表、四颗自建符号引脚名与官方脚表不符）、误报 11、资料缺口 2、需人判 6，漏报 3；
真缺陷在校准板设计记录里改掉，4 件需设计方取舍写成待办 W-SR-DECIDE。校准板 W-DOC 批量引用改为逐条证据并补 7 条新准则，审计 0 错误。
按审查发现补写 12 个典型电路（已知坑引用 review:calibration/industrial-io-rs485-can/<编号>），`typical-circuits.md` 加第三批表；测试守数量与第三批已知坑都有来源。lessons.json 第 15 条的改法与归因理由改正。详见 `docs/proposals/calibration-closeout-2026-11-02.md`。

- Event: user:2026-11-02 (再帮我执行"已识别但没做的改进")
- Causes: knowledge_missing 12
- Changed: references/typical-circuits.md, references/typical-circuits/dc-24v-input-protection.md, references/typical-circuits/ideal-diode-hotswap.md, references/typical-circuits/hold-up.md, references/typical-circuits/cot-buck.md, references/typical-circuits/ldo.md, references/typical-circuits/mcu-min-system.md, references/typical-circuits/swd-debug.md, references/typical-circuits/industrial-di-serializer.md, references/typical-circuits/di-digital-isolation.md, references/typical-circuits/high-side-quad.md, references/typical-circuits/chassis-y-cap.md, references/typical-circuits/status-led.md, tests/test_typical_circuits.py, docs/proposals/calibration-closeout-2026-11-02.md, docs/improvement-ledger.md

## 纲要 7 条文字改动：引脚表照手册、订货变体一致、未用脚处置、澄清并入需求、准则逐条指证据 (2026-11-02)

`docs/proposals/asg-from-boards-2026-11-02.md` 第 2 节的 7 条纲要改动经用户确认后写入 `SKILL.md`：任务 2.1 做完的标志加"引脚表读所选订货变体的手册，每个脚照手册写引脚名和引脚类型，符号引脚名不同的写明原因"（改动 1+7）；任务 2.3 做完的标志加"值、料号与手册指同一订货变体，料号写全订货码；电容额定与 TVS 工作电压不低于所在电源轨最坏最高电压"（改动 2）；任务 2.4 正文与做完的标志加"未用脚逐脚写手册处置和页码、电源轨写最高电压、不留占位值，以 `binding_version 1` 无错误为准"（改动 3、4）；任务 1.1 做完的标志允许澄清答复并入已有需求并引用（改动 5）；任务 5.1 做完的标志要求已关闭待办引用的每条准则指到证据位置（改动 6）。P1–P7 与 O1–O8 未动。

- Event: user:2026-11-02 (ASG纲要7条文字改动请执行)
- Causes: rule_missing 7
- Changed: SKILL.md, docs/improvement-ledger.md
- Gates: pytest 1096
- Approved: user:2026-11-02
- Outline: bf0d4d8e1fa74ca7

## 准则库 1.7.0：86 块开源板暴露的准则空白与 USB 适用范围 (2026-11-02)

86 块开源 KiCad 板经 SR 审查归因后，14 条准则问题裁决为准则确有问题 9 条（USB 七条同根因：Type-C/PD 条款被套到 A/B/Micro-B 口）、检查器误用 1 条、归工具 2 条、需人判 1 条；201 条真缺陷里 142 条没有准则承接。草案见 SR `docs/proposals/criteria-from-boards-2026-11-02.md`。
新增 9 条：G02-036 器件身份唯一、G02-037 原理图/BOM/图纸同版一致、G02-038 不交付占位值、G02-039 工作在手册推荐条件内、G03-059 外部前馈电容按手册窗、G04-101 符号脚按官方脚表、G04-102 未用/保留/专用脚按手册处置、G04-103 USB 外围按控制器手册、G04-104 Type-C CC 按端口角色端接。修订 12 条 39 处（G01-026/029/030/031 限定到 Type-C/PD 并保留 Type-A 默认 VBUS 例外，G03-005 关联，G04-010 加 STARTUP，G04-036/037/039 隔离类型不展开到磁珠，G04-091 改为千兆 PHY 厂家建议，G05-030/031 逐通道核且追到滤波后器件），各条版本 1.0→1.1。登记文件 G01 1.5、G02 1.3、G03 1.5、G04 1.2、G05 1.2，规范正文同步。厂家出处核过原件：PCA9517A Rev. 4.1、RP2350 2026-01-10 构建版、ADS1299 SBAS499C、DFLS1100 DS30497 Rev. 14-2；WCH CH32V30x 评估板原理图未取得原件，登记为版次未核。草案列的 5 件待定事项按草案原样入库：G01-028 不改、词表不加 USB_TYPEC、STORAGE 词表不动、新条目放 G02/G04、图面标注类不入库。

- Event: user:2026-11-02 (按草案入库)
- Causes: rule_missing 9, rule_wrong 12
- Changed: references/shared/guideline-criteria.json, references/shared/shared-layer.md, tests/test_guideline_closure.py, docs/improvement-ledger.md
- Gates: pytest 1035
## 工业 I/O 校准板的 26 条流程问题 (2026-11-02)

逐条对照分支核对。放行了不该放行的五处改成拦住：自定门槛的数要写进理由、检查名写的门槛要等于 limit（#23）；已关闭待办引用准则要逐条指到证据，一处顶 3 条以上算批量（#9/#24）；
引脚表照手册写引脚名，与符号不同要说明（#25）；检查可指定依赖的估计参数（#6）；澄清答复可并入已有需求（#8）。
晶体按规格采购、接电源轨的连接器写额定（#7/#21），TVS 类型词加 surge protection device（#18/#19），补 isolated-rs485、can-with-miswire 两个典型电路（#13）。
工具报错与流程：#1、#3、#5、#11、#15–17、#20、#26。#2、#4、#10 不改，#12、#14、#22 是资料缺口，写进提案；纲要建议加 3 条。
拿校准板记录试跑新审计：9 条自定门槛没写出数，2 条检查名与门槛不符，W-DOC 批量引用被拦。

- Event: user:2026-11-02 (这里面找到的问题，请提醒主对话进行修改)
- Causes: rule_not_enforced 6, rule_missing 8, knowledge_missing 2
- Changed: scripts/audit_design_closure.py, scripts/schematic_layout/component_requirements.py, scripts/schematic_layout/part_classes.py, scripts/schematic_layout/reference_contract.py, scripts/schematic_layout/recipes.py, scripts/schematic_layout/generate.py, scripts/schematic_layout/net_roles.py, scripts/deliver.py, references/design-closure.md, references/requirement-clarifications.md, references/part-roles.md, references/component-requirements.md, references/symbol-and-peripheral-contracts.md, references/delivery-report.md, references/drawing-recipes.md, references/typical-circuits.md, references/typical-circuits/isolated-rs485.md, references/typical-circuits/can-with-miswire.md, tests/test_calibration_board_issues.py, tests/test_board_defect_guards.py, tests/test_typical_circuits.py, docs/proposals/asg-from-boards-2026-11-02.md, docs/improvement-ledger.md
- Gates: pytest 1095

## 86 块开源板的缺陷类落到 ASG 生成侧防线 (2026-11-02)

SR 在 86 块开源板上确认 201 条真缺陷。按类问“ASG 画图时怎样不犯”：占位值与未编号位号不分记录版本都拦；
`binding_version 1` 核值/料号/手册是同一型号、晶体频率、引脚表读的手册与脚类型（新字段 `datasheet_type`）、连接器以外每个 NC 脚的手册处置、单端网络、电源轨最高电压对电容额定与 TVS 的 VRWM。
性能记录加 `basis: datasheet`，电容与 TVS 要写电压下限，标称容量要满足有效容量下限。Type-C 受电口与 LDO 两个实现方案补必算项和落实规则。
纲要改动 4 条与准则缺失 9 项写在提案里，未改 SKILL.md、共用层和准则条款。订货后缀、封装对料号、图注语义机械判不出，提案写明替代防线。

- Event: user:2026-11-02 (把这个86块板子上找到的问题，在规则库、ASG和SR技能中进行改进)
- Causes: rule_missing 7, knowledge_missing 2
- Changed: scripts/audit_design_closure.py, scripts/schematic_layout/component_requirements.py, scripts/schematic_layout/reference_contract.py, scripts/render_design_report.py, references/design-closure.md, references/component-requirements.md, references/symbol-and-peripheral-contracts.md, references/requirements-to-intent.md, references/typical-circuits/type-c-port-protection.md, references/typical-circuits/reviewed-bias-and-latch.md, tests/test_board_defect_guards.py, tests/test_design_report.py, docs/proposals/asg-from-boards-2026-11-02.md, docs/improvement-ledger.md
- Gates: pytest 1062

## 准则库 1.6.1：G01-053 按 GB/T 17626.29 修订 (2026-11-02)

用户取得 GB/T 17626.29-2006 全文（等同 IEC 61000-4-29:2000）。G01-053 改为按表 1a、1b 写明选定的暂降与中断组合，中断分高阻抗和低阻抗，恢复判据按 §9，低阻抗反灌接 G03-031；登记文件 G01 1.4。
该标准 §1 写明严酷度由技术委员会、用户或制造商选择，所以仍不设默认等级。24 V 电压窗与 PS1/PS2 仍缺，要靠 GB/T 15969.2-2024。

- Event: user:2026-11-02 (入库并修订)
- Causes: knowledge_missing 1
- Changed: references/shared/guideline-criteria.json, docs/improvement-ledger.md
- Gates: pytest 1034

## 校准板说明对齐准则库 1.6.0 的 DC_24V (2026-11-02)

合并 main 后，工业板需求和校准板 README 中“缺 `DC_24V`”的说法已过时，改为写 `DC_24V`（选中 G01-051～054）并同时声明 `POWER_PROTECTION`、`POWER_CONVERTER`。
类型表保留准则入口，等级指向已闭合的 C01、C12、C13。按 G01-054 的端口归类，把工业板 24 V 口写明为按连接长距离线路归类，等级数值不变。

- Event: user:2026-11-02 (合并并修正)
- Changed: evals/calibration_boards/industrial-io-rs485-can/requirements.md, evals/calibration_boards/README.md, docs/improvement-ledger.md

## 工业校准板需求写入用户答复，升 v0.2 (2026-11-02)

用户答复 C02、C09、C10，采纳 9 项建议条文和各项剩余部分的建议值，并要求直接改需求文件、升 v0.2。
C04、C15 按 ASG 处理写明；产品决定已全部闭合，标准正文未取得的记 `external` 待办并逐项注明。
答复是本次校准选定的工况，除注明的 GB/T 17799.2—2023 和 Siemens 转引外不代表标准限值。PoE 板未改。

- Event: user:2026-11-02 (全部采纳；直接改，升 v0.2)
- Changed: evals/calibration_boards/industrial-io-rs485-can/requirements.md, evals/calibration_boards/README.md, docs/improvement-ledger.md

## 盘点两块校准板开工前的知识缺口 (2026-11-02)

对照工业 I/O 与 PoE 传感节点两份需求，按 20 个功能块查手册库、典型电路和需求可追溯性，出报告和待采集清单。
手册库只缺 3 类，都在 PoE 的 RJ45 与数据磁件（无 PoE 额定的分立磁件、集成磁件 RJ45、无磁 RJ45）；典型电路缺 14 个。
30 项待澄清分诊为 6 个必问决定、18 项建议条文和 5 项不问（工业 C11–C13、PoE C12–C14 各合并问一次，C02 与 C11 同问）；POE-003 的 37 V 与库内手册写的 802.3af 36 V 有出入，列为存疑。
只读分析：未改需求、典型电路、共用层和 HardwareWiki，未执行校准；归因计数为缺手册的器件类数。

- Event: user:2026-11-02 (可以现在就做的，放到另一个子对话里面)
- Causes: knowledge_missing 3
- Changed: docs/proposals/calibration-boards-readiness-2026-11-02.md, evals/calibration_boards/datasheets-to-collect.md

## 准则库 1.6.0：DC_24V 的 4 条接口准则 (2026-11-02)

`DC_24V` 进词表后选不中任何准则。新增 G01-051～054（G01 登记文件 1.3）：只有 G01-054 按 GB/T 17799.2 表 2、表 3 登记端口浪涌与快速瞬变，电压窗、反接、中断都要求项目写明，未给定标 TBR，因为 IEC 61131-2 与 IEC 61000-4-29 没有原文。
纲要第 114 行的对外接口清单加 `DC_24V`。规范正文同步了这 4 条和 1.5.0 放宽的 9 条“适用”行。校准板说明里已过期的“缺词”改掉。

- Event: user:2026-11-02 (按建议全部入库)
- Causes: rule_missing 1
- Changed: SKILL.md, references/shared/guideline-criteria.json, references/shared/shared-layer.md, tests/test_guideline_closure.py, evals/calibration_boards/README.md, evals/calibration_boards/industrial-io-rs485-can/requirements.md, docs/proposals/dc-24v-criteria-draft-2026-11-02.md, docs/improvement-ledger.md
- Gates: pytest 1034
- Approved: user:2026-11-02
- Outline: c2674c38f46374e8

## 准则库 1.5.0：DC_24V 与典型电路补 10 处引用 (2026-11-02)

典型电路映射留下的 10 处“准则侧待办”涉及 9 条准则，适用条件不覆盖对应实现方案；校准板的正 24 V 输入在词表里也没有类型。
词表加 `DC_24V`；放宽 G03-007/008/009/017、G04-040、G05-036/037/041/060 的适用条件（G05-036/037/060 加 POWER_CONVERTER），每条 version +0.1，登记文件 G03 1.4、G04 1.1、G05 1.1。
7 个典型电路补 10 处引用，缺的必算项各加一句。`SKILL.md` 未改，其对外接口列表仍是 6 个，加 `DC_24V` 待用户批准；目前没有准则挂 `DC_24V`，它自身不选中准则。

- Event: user:2026-11-02 (可以现在就做的，放到另一个子对话里面)
- Causes: rule_missing 1
- Changed: references/shared/vocabulary.json, references/shared/guideline-criteria.json, references/shared/guideline-criteria.md, references/typical-circuits/ac-input-protection.md, references/typical-circuits/aux-overvoltage-latch.md, references/typical-circuits/isolated-feedback.md, references/typical-circuits/pd-output-control.md, references/typical-circuits/qr-flyback.md, references/typical-circuits/reviewed-bias-and-latch.md, references/typical-circuits/safety-bridging.md, docs/proposals/typical-circuits-criteria-gap-2026-11-02.md, docs/improvement-ledger.md
- Gates: pytest 1033

## 增加工业 I/O 与 PoE 传感节点两类校准需求输入 (2026-11-02)

现有典型电路来自同一块 100 W USB PD 充电器，工业接口、隔离 I/O、PoE 和以太网缺少不同板型的需求输入。
新增两份可追溯需求和 ASG 使用说明，分别定义非隔离 CAN 的工业 I/O 板与 IEEE 802.3af 受电传感节点。
区分产品范围、标准正文、预览和厂家转引；没有依据的量化指标列入任务 1.1 澄清清单。
按现有词表列出预期类型及准则核对入口，说明正 24 V 缺少专用类型，不能误用电信 −48 V 类型。
本次只准备输入，不生成电路、不改变共用层，也不宣称已执行校准或硬件验收。

- Event: user:2026-11-02 (请安排这样的工作，并调用codex…)
- Causes: knowledge_missing 1
- Changed: evals/calibration_boards/README.md, evals/calibration_boards/industrial-io-rs485-can/requirements.md, evals/calibration_boards/poe-pd-sensor-node/requirements.md, docs/improvement-ledger.md

## 典型电路必算项补到设计准则深度 (2026-11-02)

逐条核对草案的 48 处 uncertain：37 处补齐计算、限值或生产/测试约束并引用，10 处因适用类型或文本边界留作准则侧待办，1 处因功能不对应不引用。修改 14 个典型电路文件，报告保留逐项处置和按电路类型统计的前后对比，输入草案随提交保留；不改共用层、SKILL.md、落实规则标签及既有来源。归因计数为 37 处实际补齐的知识缺项，其余 11 处仅在报告记录判断。

- Event: user:2026-11-02 (请安排这样的工作，并调用codex…)
- Causes: knowledge_missing 37
- Changed: references/typical-circuits/ac-input-protection.md, references/typical-circuits/aux-bias-supply.md, references/typical-circuits/aux-overvoltage-latch.md, references/typical-circuits/current-sensing.md, references/typical-circuits/isolated-feedback.md, references/typical-circuits/ntc-temperature-sensing.md, references/typical-circuits/output-filter-storage.md, references/typical-circuits/pd-output-control.md, references/typical-circuits/pfc-boost.md, references/typical-circuits/production-test-points.md, references/typical-circuits/reviewed-bias-and-latch.md, references/typical-circuits/synchronous-rectification.md, references/typical-circuits/type-c-port-protection.md, references/typical-circuits/zcd-sensing.md, docs/proposals/typical-circuits-criteria-gap-2026-11-02.md, docs/proposals/typical-circuits-criteria-draft-2026-11-02.json, docs/improvement-ledger.md
- Gates: 指定五组 pytest 103 passed；check_ledger.py PASS；48 处处置一致；11 个受保护文件字节不变

## 正式电路用语：设计准则、典型电路、实现方案（连文件名与字段一起改） (2026-11-02)

用户问“规则、模式、覆盖这些名词在电路专用术语里怎么讲”，随后要求把它们改成正式电路名词，并选择连文件名和字段一起改。
三个名词定为：**设计准则**（原“规范规则/规则卡”，单条可核对要求；汇编叫**设计准则库**，原“规则库”）、**典型电路**（原“电路模式/模式库”）、
**实现方案**（原同一典型电路下的“做法”）。“覆盖”一词及其动词（落实准则 / 核对准则）用户要求先缓，本轮不改。
文件与标识符随之改名：`references/shared/guideline-rules.json/.md` → `guideline-criteria.json/.md`，`scripts/guideline_rules.py` → `guideline_criteria.py`
（模块名、`$GUIDELINE_CRITERIA` 环境变量同改），汇编与规范登记里的 `rules` 键 → `criteria`，规范工作目录的 `G0x_规则登记.json` → `G0x_准则登记.json`（5 份，经维护锁改）；
`references/circuit-patterns/` → `typical-circuits/`，`circuit-patterns.md` → `typical-circuits.md`，`scripts/circuit_patterns.py` → `typical_circuits.py`，
`find_parts.py --patterns` → `--circuits`，`page-plan.json` 的 `patterns` 字段 → `circuits`（值仍是 `典型电路#实现方案`），审计 `guidelines.pattern_rules` → `circuit_criteria`，
典型电路文件的 `## 做法` → `## 实现方案`（`落实规则` 一行暂留）。设计准则库 1.4.1 因键名改变重建（内容不变，`content_sha256` 变）；
共用层指纹随之变化，SR 同步。术语表“技能文档用词”加两行，旧词进“不用的词”；纲要文字随名词改，哈希变。
已交付记录里的 `page-plan.json` 旧字段 `patterns` 不再被识别，重新出图时按新字段写。

- Event: user:2026-11-02 (把这些名词都改成正式的电路名词; 设计准则/典型电路/实现方案可以，改吧; 连文件名和字段一起改)
- Causes: judgment 1
- Changed: README.md, SKILL.md, references/component-requirements.md, references/delivery-report.md, references/design-closure.md, references/human-readable-routing.md, references/shared/derating-rules.md, references/shared/guideline-criteria.json, references/shared/guideline-criteria.md, references/shared/shared-layer.md, references/terminology.md, references/typical-circuits.md, references/typical-circuits/ac-indicator.md, references/typical-circuits/ac-input-protection.md, references/typical-circuits/aux-bias-supply.md, references/typical-circuits/aux-overvoltage-latch.md, references/typical-circuits/current-sensing.md, references/typical-circuits/isolated-feedback.md, references/typical-circuits/ntc-temperature-sensing.md, references/typical-circuits/output-filter-storage.md, references/typical-circuits/pd-output-control.md, references/typical-circuits/pfc-boost.md, references/typical-circuits/production-test-points.md, references/typical-circuits/qr-flyback.md, references/typical-circuits/reviewed-bias-and-latch.md, references/typical-circuits/safety-bridging.md, references/typical-circuits/synchronous-rectification.md, references/typical-circuits/type-c-port-protection.md, references/typical-circuits/zcd-sensing.md, scripts/audit_design_closure.py, scripts/find_parts.py, scripts/guideline_criteria.py, scripts/render_design_report.py, scripts/schematic_layout/component_requirements.py, scripts/typical_circuits.py, tests/test_bias_latch_cases.py, tests/test_component_requirements.py, tests/test_derating_audit.py, tests/test_derating_rules.py, tests/test_design_closure.py, tests/test_design_report.py, tests/test_find_parts.py, tests/test_guideline_closure.py, tests/test_part_classes.py, tests/test_typical_circuits.py
- Gates: pytest 1033
- Approved: user:2026-11-02
- Outline: f10aa370dbb0f34c

## 共用层第二轮：词表、最弱档、共用应力核对进共用层；模式做法落实规则 (2026-11-02)

用户要求把零散的规则归入新架构，并且不再逐项确认方案（“按照你推荐的方式，现在就开始执行”；“我不确认方案了…一直到都做完”）。
① 词表：`references/shared/vocabulary.json` 成为基线、电路类型、器件类别名字与标题的唯一出处，规则库汇编从它取词表（`build` 不再有 `--base`），
`part_classes.KINDS` 对着它核对（`test_part_classes` 不再伸手到 SR 的 checkout 读 `device_kinds.py`，只剩分类线索的对等比较）；`zener`/`fuse` 标题统一为“稳压管”“保险丝”。
② 常规件最弱档：`references/shared/commodity-floors.json` 一份（片式电阻 8 个封装的 70 ℃ 功率与耐压、MLCC 可订购档、触点），
`audit_design_closure.RESISTOR_FLOORS` 与 `component_requirements.RESISTOR_VOLTAGE_FLOORS` 从它构造，两条用 `ast` 解析 SR 源码的测试改读共用文件；
`weakest_share`、`assumed_resistor_package` 迁入规则库 G02 工程取值，规则库 1.4.1。④ 定界表剩余估算倍数查无数值，不做。
③ 共用应力核对 `scripts/stress_check.py`：某级降额限值（`derated_limit`）、一条应力对额定与降额值的判法（`verdict`）、没点名规则时按器件类别与量纲挑规则（`fit_rules`）
只写一份，两技能同字节、进共用层指纹；`audit_design_closure` 删掉自己的 `derated_limit` 和挑规则逻辑改为调用它（SR `derating.py` 同步）。
模式→规则映射（与 SR `catalog.BASIS` 对称）：17 个模式文件各加一行 `电路类型：`（词表名，`ac-indicator`、`production-test-points` 无对应类型写“无”），
每种做法加一行 `落实规则`（只引用 active、按本模式类型/器件类别/全板触发、且做法正文做到了其 asg_action 的规则；部分覆盖不引用，`aux-overvoltage-latch` 因 G05-036/037 适用文本限于热插拔暂写“无”）。
新模块 `scripts/circuit_patterns.py` 读它们，`render_design_report.pattern_approaches` 改为调用；设计完成核对读 `record/page-plan.json` 标注的做法，
声明的类型不在 `guideline_scope.circuit_types` 或落实的规则按范围不适用记 `guideline_scope_circuit`（本轮改名前叫 guideline_scope_pattern），审计 `guidelines.pattern_rules` 列出模式声称落实的规则。
草案由 opus 子代理按库逐条对照做法正文生成，本人逐条复核后写入；当前模式覆盖规则库很低（POWER_CONVERTER 38 条可引用 8 条，USB/ISOLATION 0 条），因为模式都来自同一块 PD 充电器。
纲要（SKILL.md）本轮未改，哈希不变。

- Event: user:2026-11-02 (按照你推荐的方式，现在就开始执行; 我不确认方案了，你先找你推荐的方式把1/2/4做完之后做3，一直到都做完)
- Causes: judgment 1
- Changed: references/shared/vocabulary.json, references/shared/commodity-floors.json, references/shared/guideline-rules.json, references/shared/guideline-rules.md, references/shared/derating-rules.json, references/shared/derating-rules.md, references/shared/stress-spec.md, references/shared/shared-layer.md, references/circuit-patterns.md, references/design-closure.md, references/circuit-patterns/ac-indicator.md, references/circuit-patterns/ac-input-protection.md, references/circuit-patterns/aux-bias-supply.md, references/circuit-patterns/aux-overvoltage-latch.md, references/circuit-patterns/current-sensing.md, references/circuit-patterns/isolated-feedback.md, references/circuit-patterns/ntc-temperature-sensing.md, references/circuit-patterns/output-filter-storage.md, references/circuit-patterns/pd-output-control.md, references/circuit-patterns/pfc-boost.md, references/circuit-patterns/production-test-points.md, references/circuit-patterns/qr-flyback.md, references/circuit-patterns/reviewed-bias-and-latch.md, references/circuit-patterns/safety-bridging.md, references/circuit-patterns/synchronous-rectification.md, references/circuit-patterns/type-c-port-protection.md, references/circuit-patterns/zcd-sensing.md, scripts/guideline_rules.py, scripts/stress_check.py, scripts/circuit_patterns.py, scripts/audit_design_closure.py, scripts/render_design_report.py, scripts/schematic_layout/component_requirements.py, scripts/schematic_layout/part_classes.py, tests/test_guideline_closure.py, tests/test_derating_rules.py, tests/test_part_classes.py, tests/test_derating_audit.py, tests/test_component_requirements.py, tests/test_circuit_patterns.py, docs/improvement-ledger.md
- Gates: pytest 1033（含 test_circuit_patterns 9 条）；SR pytest 2406

## 共用层目录制：references/shared/、工程取值唯一出处、一个指纹 (2026-11-02)

用户要求重新调整与 SR 的共用层，让结构清晰简单、映射明确。此前共用层是两次决定叠出来的：规则库三份文件和
降额表、应力规范散在 `references/` 与 `scripts/`，两套版本、两条对齐测试、工程取值在规则库（41 项）和降额表（3 项）两个家，
六份文档各说一遍“与 schematic-review 共用”。现在 `guideline-rules.json/.md`、`derating-rules.json/.md`、`stress-spec.md`
搬进 `references/shared/`，新增 `shared-layer.md` 作为共用层唯一说明页（四件事、谁读、哪条测试守、怎么改、同名不共用）；
降额表剩下的 `unset_level`、`thermal_calc_trigger`（G01）与 `soa_segment_share`（G03）迁入规则库 1.4.0，
`component_requirements.voltage_share` 和 `audit_design_closure` 改读 `guideline_rules.engineering_value`；
`guideline_rules.shared_digest()` 给整个共用层一个指纹，设计完成核对把它写进审计 `guidelines.shared_sha256`，
报告“共用规范”一行印“共用层 <指纹>，规则库 1.4.0，降额 v1”；`test_guideline_closure` 一条整目录对齐测试取代原来规则库、降额各一条。
主流程 1.1、2.2 里三处链接的路径随之改成 `references/shared/…`，纲要文字别无变化，哈希随路径变。
用户在方案（目录制、3 项工程取值迁进规则库）批准时确认。

- Event: user:2026-11-02 (帮我重新调整一下这部分共用层的架构，让结构清晰简单，映射明确; 目录制; 迁进规则库)
- Causes: judgment 1
- Changed: SKILL.md, references/shared/shared-layer.md, references/shared/guideline-rules.json, references/shared/guideline-rules.md, references/shared/derating-rules.json, references/shared/derating-rules.md, references/shared/stress-spec.md, references/component-requirements.md, references/delivery-report.md, references/design-closure.md, references/pdf-schematic-extraction.md, references/requirement-clarifications.md, references/requirements-to-intent.md, scripts/guideline_rules.py, scripts/audit_design_closure.py, scripts/render_design_report.py, scripts/schematic_layout/component_requirements.py, tests/test_guideline_closure.py, tests/test_derating_rules.py, docs/improvement-ledger.md
- Gates: pytest 1023
- Approved: user:2026-11-02
- Outline: 05cb56c08f9d7126

## 器件认知表跟上 2026-11-01 整理后的器件库；检索不再混入旧版手册 (2026-11-01)

`test_find_parts` 的真实库比对失败：当天的器件库整理新增了子类，表里缺 8 行，已补，并在倒排索引里加了晶体和 LED。
库里 `<一级类>/versions/<哈希>/` 的旧版手册被索引算成子类 `versions`，`--mpn DS18B20` 还把旧版排在现行版前面。`find_parts.py` 的检索和子类统计现在跳过这些存档，`library_index` 仍能按哈希找到它们。
器件库一侧把重复子类“逻辑门_缓冲器与驱动器”的 3 份手册并回“标准逻辑门”和“缓冲器_收发器”，所以不必为它加一行。

- Event: user:2026-11-01 (补上并推送；如有必要修改 HardwareWiki 的 datasheet 分类)
- Causes: rule_missing 1
- Changed: docs/improvement-ledger.md, references/part-roles.md, scripts/find_parts.py, tests/test_find_parts.py

## 规则库 1.0.0（G01–G03）装入：接口电路类型、选型引用规则 (2026-11-01)

用户确认《规则库 v1.0 技能接入方案》的四项决定并说“开工”；方案第四节写明确认方案即视为批准纲要小改。
1.1 从需求声明 6 个对外接口电路类型，写入 `guideline_scope`，接口规则靠它选中；2.3 的性能记录可写 `guidelines`，`audit_design_closure.py` 读 `record/component-requirements.json` 计入覆盖，落实处记 `component:<位号>`。
共用文件同步：规则库 143 条、39 项工程取值；降额规范删去 `typical_band`、`forced_beta_k`（迁到 G02）。ASG 只读 `unset_level`，不受影响。
真实规则库下核对：POWER_CONVERTER、POE_PD 范围适用 97 条，都不引用时 97 条待完成；全部引用后无 guideline 类问题；改航天基线再多 11 条待完成。同一范围下与 SR 选出的规则集相同。
测试：设计待办和降额审计两组测试用无规则库，规则行为由 `test_guideline_closure.py` 覆盖。`test_find_parts` 的真实库比对在 main 上同样失败，与本次无关。发现但未改：示例 `build_compact.py` 仍给 `check_scene` 传已移除的 `grid=`，联调时临时兼容后跑通。

- Event: user:2026-11-01 (开工)
- Approved: user:2026-11-01
- Outline: df4f8f0aaa826e52
- Causes: rule_missing 1
- Changed: SKILL.md, docs/improvement-ledger.md, references/component-requirements.md, references/shared/derating-rules.json, references/shared/derating-rules.md, references/design-closure.md, references/shared/guideline-rules.json, references/shared/guideline-rules.md, scripts/audit_design_closure.py, scripts/guideline_rules.py, scripts/render_design_report.py, scripts/schematic_layout/component_requirements.py, tests/test_derating_audit.py, tests/test_design_closure.py, tests/test_guideline_closure.py

## 接入共用规范规则库 G01–G09 (2026-10-31)

用户确认《ASG与SR规则接入方案草稿》并要求执行（“请开始执行这个方案，慢慢来，一步一步来修改。遇到问题的时候先按照你的建议来执行。”）。
九份共用规范的规则卡汇编成 `references/shared/guideline-rules.json`，与说明 `guideline-rules.md`、脚本 `scripts/guideline_rules.py`
在 ASG 与 schematic-review 两边同字节（沿用降额规范的做法，两个仓库独立发布也能用；两边测试互相逐字节比对）。
ASG 侧：1.1 定产品基线（默认工业/通信板卡）与功能电路类型、器件类别，记入 `design-closure.json` 的 `guideline_scope`（`guideline_version: 1`）；
2.2 落实规则卡设计动作的计算写 `guidelines`，原理图之后关闭的规则用技术转交待办引用；5.1 做完的标志加“适用规则都已引用或写明不适用”。
审计新增 `guideline_uncovered`（待完成）、`guideline_unknown`、`guideline_cited_not_applicable`、`guideline_downstream_without_work_item`、
`guideline_scope`、`guideline_scope_missing`；报告新增“共用规范规则覆盖”“下游约束（共用规范）”两节和结论一行。
规则库现在为空（规范尚在成文），审计与报告不变；规则库有规则后旧记录要补 `guideline_scope`。
基线测试：变基到 KiCad 10.0.7 修复之后，全量 1020 个测试通过，含新增 8 个。

- Event: user:2026-10-31 (请开始执行这个方案)
- Approved: user:2026-10-31
- Outline: 6322a2833548105c
- Causes: rule_missing 1
- Changed: SKILL.md, references/shared/guideline-rules.md, references/shared/guideline-rules.json, references/design-closure.md, references/delivery-report.md, scripts/guideline_rules.py, scripts/audit_design_closure.py, scripts/render_design_report.py, tests/test_guideline_closure.py, docs/improvement-ledger.md

## KiCad 10.0.7 列入原生几何已验证版本 (2026-10-30)

本机 kicad-cli 已升到 10.0.7，`native_geometry_context`、`native_circle_contacts` 只认 10.0.6，原生几何门一律报
“native version profile not qualified”，13 个原生测试失败。改为 `native.QUALIFIED_VERSIONS = ("10.0.6", "10.0.7")`，
两处共用。依据：在 10.0.7 上全量测试 1012 个通过，含篡改、越界、外来导线等全部反例控制，测试未改。
另 2 个 ERC 测试失败（`lib_symbol_issues` 39 条）是本机全局符号库表不含 KiCad 标准库所致，属环境问题，未改代码。

- Event: test:2026-10-30 (kicad-cli 10.0.7; 用户：这两个问题请帮我解决)
- Causes: knowledge_missing 1
- Changed: scripts/schematic_layout/native.py, scripts/schematic_layout/native_geometry_context.py, scripts/schematic_layout/native_circle_contacts.py, docs/improvement-ledger.md

## 热计算触发值、典型值估算带、强制 β 并入降额规范工程取值 (2026-10-29)

用户要求把上一条里列为“未改”的几处也处理（“这些也都处理”）：共用 `derating-rules.md/json` 的“工程取值”新增
`thermal_calc_trigger`（0.3 W 或封装额定 50% 时估算结温，触发条件不是判据）、`typical_band`（SR 定界 G9 ③ 典型 ±30%）、
`forced_beta_k`（SR 强制 β k = 2）。ASG `requirements-to-intent.md` 改为引用 `thermal_calc_trigger`，不再自写数字；
SR 侧脚本改为从规范读取，同日 SR 条目记。数值未改。

- Event: user:2026-10-29 (这些也都处理)
- Causes: rule_not_enforced 1
- Changed: references/shared/derating-rules.md, references/shared/derating-rules.json, references/requirements-to-intent.md, tests/test_derating_rules.py, docs/improvement-ledger.md

## 单立的降额类规则并入降额规范：电阻工作电压提示、PDF 补电容耐压 (2026-10-29)

用户问两条规则是否符合降额规范，并要求“类似这种单一的规则，都先不要，全都并入到降额规范里面去”。
1. `component_requirements.py` 的电阻工作电压提示按“封装最弱常用件耐压的一半”（`VOLTAGE_SHARE = 0.5`）判不起约束，
   它照抄的是 SR 已删除的 50% 预判门限，与 SR 现行判据（最弱档 × RES-SMD-V）不一致。改为最弱档 × RES-SMD-V，
   记录里没有降额等级，按规范工程取值 `unset_level`（I 级，最严，对任何等级都不会误报“不起约束”）。
2. `pdf-schematic-extraction.md` 的“电容没写耐压按电源轨 1.5–2 倍选”不符合规范：1.5 倍即 67%，钽电容各级（50/60/70%）都不满足。
   改为额定 ≥ 轨最高电压 ÷ 该电容类型电压规则的本级取值（等级未定按 `unset_level`）。
`requirements-to-intent.md` 里“功耗达到约 0.3 W 或封装额定的一半时估算结温”是何时做热计算的触发条件，不是判据，本次未改，已告知用户。

- Event: user:2026-10-29 (这两条是符合降额规范的吗？类似这种单一的规则，都先不要，全都并入到降额规范里面去)
- Causes: knowledge_wrong 2
- Changed: scripts/schematic_layout/component_requirements.py, references/component-requirements.md, references/pdf-schematic-extraction.md, tests/test_component_requirements.py, tests/test_derating_rules.py, docs/improvement-ledger.md

## SOA 段系数并入降额规范；常规件 50% 预判门限删除 (2026-10-29)

SR 里两处降额相关数字不在共用降额规范里：MOS 高温 SOA 段系数（恒功率段 100%、热不稳定段 80%）和常规件 50% 预判门限
（等级未定取 2 倍应力，ASG `audit_design_closure.py` 的 `UNSET_POWER_SHARE` 照抄了这一条）。四份降额标准都没有 MOSFET
安全工作区的降额值，SOA 段系数并入规范；50% 门限出自经验说法、比 RES-SMD-P/V 三级都严，删除。
用户决定（“SOA段系数和常规件预判门限，需要并入到这个降额规范里面去…如果不合理的话就删掉”；“按方案改”）：

1. 共用 `derating-rules.md/json` 新增“工程取值”`engineering_values`：`soa_segment_share`（user:2026-10-23）与 `unset_level`
   （等级未定时常规件预判与 BOM 最低额定按 I 级，user:2026-10-29）；R11 改为不在本表和工程取值之外另乘系数。
2. ASG 删除 `UNSET_POWER_SHARE`：等级未定时电阻最低额定功率按 `unset_level` 的 RES-SMD-P（0.7），不再取 2 倍；
   等级缺失本身仍报 `derating_level_missing`。`design-closure.md` 同步。

ASG 纲要（SKILL.md）没改。SR 侧同日条目记其余改动。

- Event: user:2026-10-29 (SOA段系数和常规件预判门限，需要并入到这个降额规范里面去。常规件预判门限是否合理？如果不合理的话就删掉；按方案改)
- Causes: knowledge_wrong 1, rule_not_enforced 1
- Changed: references/shared/derating-rules.md, references/shared/derating-rules.json, references/design-closure.md, scripts/audit_design_closure.py, tests/test_derating_audit.py, tests/test_derating_rules.py, docs/improvement-ledger.md

## R10 暴露的四个问题：规格件关闭、要求收敛、不满足的计算、估计余量 (2026-10-28)

SR 会话分析 ASG 生成的 100W PD R10，找到几类问题，用户选“先改前四条”。

1. 按规格采购的常规阻容只有 `by_spec` 一条关闭途径，要企业受控标准料号，项目没有，114 颗里 109 颗永远“型号未定”，
   结论铺了约 150 行。用户确认（“同意按此做”）新增 `by_bom_spec`（BOM规格已写全）：每条要求的参数、方向和数值都在本次导出
   BOM 与 XML 的 `RequirementSpec` 里核到即关闭，不写 MPN、`standard_id`；找料与核对保证值列在审核结果 `procurement`，
   报告只写一行总数，不挡交付。
2. 性能要求套模板：110 颗都写了工作电压（R503 ≥ 0.063125 V），9 颗电阻共用同一句漂移条件，整段条件印在图上，
   被 PWR_FLAG 文字插断后报 36 条英文误报。改为 `le`/`ge` 数值超过 3 位有效数字记错（`conservative` 按保守方向取整）；
   电阻工作电压不到封装最弱常用件耐压一半、同一句波形/漂移条件出现在 3 颗以上时 `hints` 提示（耐压表抄自 SR
   `passive_stress.py`，测试核对一致）；图面只印“参数 比较符 数值 单位”，条件留在记录和 BOM；PDF 逐条短标签核对，消息写中文。
3. ENERGY 三档最好情景都不满足，报告两张计算表都没有它。报告新增“不满足的计算”放在计算表最前面，列不满足的检查、
   `contributors` 最大几项和改设计候选；检查写 `scenario: best` 而不满足时，要有 design 待办写 `redesign`
   （`best_case_failed_without_redesign`），改设计由用户批准。
4. 靠工程估计过关的检查余量比估计误差还小（96.9 对 97.6 V）。用户选“判风险”：`uncertainty_version: 1` 下 `model` 参数写
   `uncertainty`，余量占门槛比例小于它的检查合格但有风险，写 `improvement`，审计列 `estimate_margins`，报告单列一节；
   降额检查的余量对额定算，不与降额值叠加（R12）。

共用的 `derating-rules.md`、`derating-rules.json`、`stress-spec.md` 没改；ASG 纲要（SKILL.md）没改。
另有四个程序错误本次不改（停产核对读磁件设计单、比较符写反、U501 选型理由、KiCad 10.0.7 支持）。

- Event: user:2026-10-28
- Causes: rule_missing 4
- Changed: scripts/schematic_layout/component_requirements.py, scripts/audit_design_closure.py, scripts/render_design_report.py, tests/test_component_requirements.py, tests/test_estimate_margins.py, tests/test_design_report.py, references/component-requirements.md, references/design-closure.md, references/delivery-report.md, docs/improvement-ledger.md


## 定制磁件按磁件设计单关闭选型 (2026-10-28)

codex 应用 ASG 时反馈“磁件设计单状态尚未接通”：定制磁件的依据是自己的设计单，器件性能记录只有厂家/受控标准保证能核准，
磁件永远停在候选待核；正式 MPN 只给已核准件，又与“定制磁件 mpn 写设计单编号”冲突。用户看过草案后选口径 A
（“按 A 实施”）：新增采购方式 `design_sheet` 与状态 `by_design_sheet`，只用于带 `fields.DesignSheet` 的磁件；逐项核对设计单
哈希、本位号/编号那一节里的引文、数值单位、条件、大小关系和样件验收方法；核实后选型关闭，设计单编号投影为 MPN，
样件验收在审核结果 `acceptance` 和报告里单列为外部项，不挡交付、不宣布定型。纲要 P3 与 2.3 已写“设计单”，不改纲要。
补测通过路径、引到别的磁件一节、无对应分节、数值不满足、缺验收方法、冒充厂家保证、换文件与改文件、非磁件、
未核实时为未完成，以及 KiCad 原生导出后 BOM/XML/图面一致。

- Event: user:2026-10-28
- Causes: rule_not_enforced 1
- Changed: scripts/schematic_layout/component_requirements.py, scripts/render_design_report.py, references/component-requirements.md, references/part-roles.md, tests/test_component_requirements.py, tests/test_design_report.py, docs/improvement-ledger.md

## 没点名降额规则的额定比较按唯一适用的比例规则核 (2026-10-28)

SR 审查 100W PD 板时，5 A 额定的 USB-C 母座跑满 5 A，以零余量判了通过，也没报应力风险；用户认可共用应力规范新加一条，
要求 ASG 设计检查同样核（“这两件事也都推进做”）。`audit_derating` 对门槛是保证额定、没写 `derating_rule` 的检查，按器件
类型和单位的量找唯一一条 worst/steady 的 `ratio` 规则（USB 母座、器具耦合器按身份区分，其余取“其他”），应力超过本级
降额值即列为应力风险并要求 `improvement`，与点名规则一致；在降额值以内的照旧只出提示。行为照 SR 的 `implied_ratio`。
补测 III 级 USB-C 5 A 走 USB-I（4.5 A）、接线端子走 CONN-I（4.25 A）、降额值以内只提示、点名规则与非额定比较不受影响。

- Event: user:2026-10-28
- Causes: rule_not_enforced 1
- Changed: scripts/audit_design_closure.py, references/design-closure.md, tests/test_derating_audit.py, docs/improvement-ledger.md

## 将器件性能要求固化到计算、选型、出图和交付流程 (2026-10-28)

用户批准流程草案后实施：P3与任务2.2–2.4先由用途/工况定义可采购性能，再核实候选，按规格采购与必须绑定型号分开。
新增版本化性能记录、用途分组筛选、来源哈希/定位、要求与保证值的独立字段、显式IR/BOM与精确标称值投影；候选不得写正式MPN。
受控规格及其保证已核实时用by_spec完成规格采购核实，不强迫绑定订货号；只有自拟要求而无受控保证的仍保留未选料。
图面显示完整短规格或同页索引与技术注释，原生PDF/XML/可见属性/BOM共同核对；准备、验证、报告及打包使用同一记录。
保留旧记录未检查状态、核心器件/安全/认证/曲线绑定要求及共享应力规范。补测公差不等式、J公差误写、MOV类别、待计算、
候选冒充核准、隐藏字段、同页注释、过期计算/BOM与典型值误作保证等失败路径，包含真实KiCad导出。

- Event: user:2026-10-28
- Approved: user:2026-10-28
- Outline: 07ee30fe07332d10
- Causes: rule_not_enforced 1, rule_wrong 1
- Changed: SKILL.md, references/component-requirements.md, references/part-roles.md, references/requirements-to-intent.md, references/requirement-clarifications.md, references/delivery-report.md, scripts/audit_component_requirements.py, scripts/audit_design_closure.py, scripts/deliver.py, scripts/pack_design.py, scripts/render_design_report.py, scripts/verify_schematic.py, scripts/schematic_layout/component_requirements.py, scripts/schematic_layout/generate.py, scripts/schematic_layout/pages.py, scripts/schematic_layout/part_classes.py, scripts/schematic_layout/recipes.py, tests/test_component_requirements.py, docs/improvement-ledger.md

## R8独立审查后的宽范围偏置与身份核对案例 (2026-10-28)

补入高压Buck、VCC低电流指示、比较器高有效FAULT、反向保护LDO与SR隔离二极管的参考做法；记录线感知门限与两档反馈耦合、J公差和MOV身份三个判断案例。合成测试仅复现数字/分区/身份，不将文档存在等同电气证明；不改纲要或判定门槛。

- Event: review:SR-20261028-R8-从头审查-61166f3/F-001, review:SR-20261028-R8-从头审查-61166f3/F-002, review:SR-20261028-R8-从头审查-61166f3/F-004, review:SR-20261028-R8-从头审查-61166f3/F-005, review:SR-20261028-R8-从头审查-61166f3/F-006
- Causes: judgment 5
- Changed: references/circuit-patterns/reviewed-bias-and-latch.md, tests/test_bias_latch_cases.py, docs/improvement-ledger.md

## 功耗要考虑的电阻写额定功率 (2026-10-27)

用户：“照道理来说，在设计的时候，如果要考虑功耗，不仅要考虑阻值和精度，还需要写上功率等级，作为给以后的约束。ASG里面就要这样来做，
SR同样要审核这一点”。SR 的无源应力预判已要求：最坏功耗超过按已写字段能买到的最弱件（封装最弱档的一半）的降额值、BOM 又没写额定功率的电阻，
写 BOM 约束“额定功率 ≥ 应力 ÷ RES-SMD-P”或判 FAIL。ASG 照同一判据设计：`audit_derating` 对 `ref` 为电阻、单位 W/mW 的功耗检查，
按封装（没封装按 0402）最弱档 × 0.5 × 本级 RES-SMD-P（等级未定 0.5）判功耗是否要考虑，要考虑而 `value` 和字段都没写额定功率的记
`resistor_power_rating_missing`，给出最低额定；`value` 写成 `阻值/公差/额定功率`。封装最弱档表与份额抄自 SR `passive_stress.py`，
测试 `test_the_floors_are_schematic_reviews` 核对两边一致。审计只看得到写成检查的功耗，文档要求设计时算轨上和高压电阻的最坏功耗。

- Event: user:2026-10-27
- Causes: rule_not_enforced 1
- Changed: scripts/audit_design_closure.py, tests/test_derating_audit.py, references/design-closure.md, references/requirements-to-intent.md, docs/improvement-ledger.md

## IC 角色线索对齐 schematic-review：linearregulator (2026-10-27)

SR 在 7b49463 给 IC 角色线索加了 `linearregulator`，ASG 的器件类型对齐测试（`test_quotes_name_the_same_kinds_in_both_skills`）
因此失败；`part_classes.IC_ROLE_CUES` 补上同一条线索。

- Event: user:2026-10-27
- Causes: rule_not_enforced 1
- Changed: scripts/schematic_layout/part_classes.py, docs/improvement-ledger.md

## 纲要 2.2：降额判法与覆盖统一到器件应力规范 (2026-10-27)

SR 复查 R8、把共用降额规范接进 SR 后，用户定了三点：降额等级的来源“照 ASG”；“将共用规范R6和ASG统一到现在的“应力”规范下来，
制定单独的应力规范”；“ASG里面现在每颗器件都有降额规则，这个过于严苛了。请将其统一到余量审核规则上来”。
新增与 SR 逐字相同的 `references/shared/stress-spec.md`（器件应力规范），`derating-rules.md` 的 R6 改为指向它；`derating-rules.json` 不变。
ASG 改法：在额定内但超过降额值不再是有条件成立加降额待办或用户接受，而是合格但有风险（应力）：计算照常推出结论，检查写
`improvement`（缺记 `stress_risk_without_improvement`），审计在 `derating.stress_risks` 列出，报告“应力风险”一节逐条列出，不挡交付；
超过额定仍为 `failed`。去掉 `rests_on: derating` 一档、design 待办的 `derating` 字段与 `derating_without_item`。覆盖按写出来的应力：
去掉 `derating.parts` 声明与 `derating_part_undeclared`、`derating_type_unknown`、`derating_not_covered`；点名规则的检查照旧核规则、
器件类型、等级与降额值；拿应力与额定比却没点名规则、而规范有这类器件的规则时，只在 `derating.hints` 出提示 `derating_rule_available`。
降额等级的来源 `derating {level, source}` 不变。一致性测试加 `stress-spec.md`。

- Event: user:2026-10-27
- Approved: user:2026-10-27
- Outline: 798c19acd30beee2
- Causes: rule_wrong 1
- Changed: SKILL.md, references/shared/stress-spec.md, references/shared/derating-rules.md, references/design-closure.md, references/delivery-report.md, references/requirements-to-intent.md, scripts/audit_design_closure.py, scripts/render_design_report.py, tests/test_derating_audit.py, tests/test_derating_rules.py, tests/test_design_report.py, docs/improvement-ledger.md

## 纲要 1.1/2.2：问降额等级，关键与特殊器件按等级核对应力 (2026-10-27)

降额规范写好后，用户确认纲要草案：任务 1.1 把降额等级（I/II/III）当作一条需求，需求没写时与其他需求澄清一并问用户，
附建议等级，暂缓的按建议等级作为写明的假设；任务 2.2 让关键器件与特殊器件在工作包络角点和瞬态下的应力按
`derating-rules.json` 中本项目等级那一列核对，常规件的规格写出的最低额定 = 最坏应力 ÷ 本级降额系数；超过额定为不成立，
在额定内但超过降额值为有条件成立并挂降额待办（改设计或用户接受）。两件待定按建议：常规件不逐颗核对；未关闭的降额待办不拦交付。
实现：`derating_version: 1` 记录 `derating {level, source, parts}`；降额检查写 `derating_rule`、`ref`、`rating`、`rating_source`，
门槛由规则推出并核对（`derating_limit_mismatch` 等 10 个审计码）；降额偏离有未关闭待办时计算为 `conditional`/`derating`
（报告“超过降额值”），用户接受（`accepted: user:<日期>`）后不再有条件，超过额定为 `failed`；关键与特殊器件声明降额类型，
每条规则有检查或不适用理由。报告写降额等级与来源、列出降额偏离，旧记录在“记录版本”一行说明没有核对降额。
需求澄清表把降额从“不问的设计约束”移出，加一行问降额等级。

- Event: user:2026-10-27
- Approved: user:2026-10-27
- Outline: d56c1d2a6ad48ddd
- Causes: rule_missing 1
- Changed: SKILL.md, scripts/audit_design_closure.py, scripts/render_design_report.py, references/design-closure.md, references/requirement-clarifications.md, references/requirements-to-intent.md, tests/test_derating_audit.py, tests/test_design_report.py, docs/improvement-ledger.md

## 元器件降额规范：I/II/III 三级，与 schematic-review 共用一份 (2026-10-27)

R8 复查时用户问 ASG 何时做裕量检查，决定建立“建立在电路知识和器件基础上”的裕量规则，第一批只做器件应力降额；
超过降额但在额定内为有条件成立并挂待办，超过额定为不成立。用户下载 T/CPSS 1013—2021、T/CPSS 1006—2024、GJB/Z 35—93
放入知识库 `raw/Standard/`（IPC-9592B 只有目录，未收录），并要求按 I/II/III 三级给值、ASG 与 SR 都按项目的降额等级取值、
不只用于消费类产品。用户确认的取值规则：来源按 1013 → GJB → 1006 优先；1006 只有一级，三级同值；GJB 给范围的取保守端；
1013 已控电感绕组温度和磁饱和时不叠加 GJB 表29 的工作电流系数；只给一个系数时对稳态与瞬态的最坏组合生效，手册单列的冲击、
脉冲额定按表中比例比较。新增 `references/shared/derating-rules.json`（223 条，每条写器件类型、参数、工况、判据、三级取值和 PDF 页码）
与同内容的 `derating-rules.md`（等级从哪来、取值规则、各类器件的表），两份与 schematic-review 逐字相同。
测试核对每条的类型属于器件类型词表、判据与工况已定义、页码在来源页数内、三级从 I 到 III 降额递减、未分级来源三级同值、
文档列出每条、来源文件的 SHA-256 与知识库一致、两个仓库的文件相同。ASG 计算按等级取值、任务 1.1 问降额等级要改纲要，另行提案。

- Event: user:2026-10-27
- Causes: knowledge_missing 1
- Changed: references/shared/derating-rules.json, references/shared/derating-rules.md, SKILL.md, tests/test_derating_rules.py, docs/improvement-ledger.md

## R8 暴露的记录问题：缺口分类、门槛出处、需求检查、经验落点、本机路径引用、小数显示 (2026-10-27)

用户让 Codex 按 ASG 做完 R8 后，查报告发现：7 件未关闭项都记成外部资料缺口且共用一句“为什么是外部依赖”，其中系统级 ESD 试验、
采购报价和可以拿手册额定比对的冲击电流并不是资料缺口；65 个工程估计参数共用一句理由，需求里的数（264 Vac、220 V、87600 h）
标成估计值，“20 J 采购资格”“60 V 筛查值”这类自定门槛和额定写法一样；成本需求写“在选型记录中估算”却没算；补写的电路模式写在
交付目录里，技能没学到；手册引用写本机绝对路径；报告把 379 ns > 343 ns 显示成“0 > 0 s”。
用户确认的改法：`gap_version 2` 给每条缺口写 `kind`（手册没给 / 只有典型值 / 固件 / 芯片内部），试验、认证、承认、报价改记
validation，只有典型值或没给的要写已评估的替代做法，几件待办共用一句理由报 `gap_reason_repeated`；`parameter_version 3`
给每条检查写门槛的依据与出处（自定门槛使结论依赖工程估计），每条需求要有检查或写 `no_check_reason`；报告对共用理由的估计、
写在交付目录的经验列为记录问题，结论一行写明旧版本没核对的内容；审计拒绝本机绝对路径的手册引用；
需求澄清加“成本估算超目标”“答复只定一侧界限”两种要问的情况；同步整流模式加 VCC 经二极管取电的启动门限已知坑。
旧记录（parameter_version 1/2、gap_version 1）照旧可读，缺版本号时报告要求写新版本。
检查加 `==` 比较符写一致性核对（R8 C-LIFE 把每日能量配对写成“218 ≤ 218 Wh”）。草案里列出裕量不到 5% 的检查的报告一节，试跑时把这条一致性核对算成裕量 0%，用户决定去掉这一节（用户：这一点本来就不应该进入到裕量计算的过程中）。

- Event: user:2026-10-27
- Causes: rule_missing 6, knowledge_missing 1
- Changed: scripts/audit_design_closure.py, scripts/render_design_report.py, scripts/schematic_layout/citations.py, references/design-closure.md, references/requirement-clarifications.md, references/delivery-report.md, references/terminology.md, references/circuit-patterns/synchronous-rectification.md, tests/test_design_closure.py, tests/test_design_report.py, docs/improvement-ledger.md

## 器件类型对齐 schematic-review 的“器件类型的依据”：共模扼流圈、耦合电感、整词 fuse 与压制规则 (2026-10-27)

SR 在 main（c806601）落地“器件类型的依据”后，ASG 的类型词表对齐测试失败：SR 新增的 `common_mode_choke`、`coupled_inductor` ASG 没有。
补齐：两类放在 `diode` 之后、`ferrite`/`inductor` 之前，词与线索照 SR；`fuse` 加线索 `pptc`；短线索与 `fuse` 按 SR 的 `named_by` 整词匹配
（可带复数，小写接大写算分词，“Littelfuse”不命中）；原文说出 IC 角色时压掉分立器件、`fuse`、`relay`（ASG 照 SR `catalog.DEVICE_ROLES`
抄一份 IC 角色线索，只用于压制，对齐测试核对不少于 SR），说出 `ntc`/`varistor` 时压掉 `fuse`，去空格后含 `relaydriver` 时压掉 `relay`；
ASG 的电感线索有 inductor/choke 而 SR 没有，所以说出两种多绕组磁件时压掉 `inductor`。以前认成电感的这两类照电感处理：
可作为 `inductor` 符号上的更具体声明、带磁件设计单为关键器件、常规件要写额定电流。新增逐句与 SR 比对线索结果的测试。

- Event: user:2026-10-27
- Causes: rule_missing 1
- Changed: scripts/schematic_layout/part_classes.py, references/part-roles.md, tests/test_part_classes.py, docs/improvement-ledger.md

## 需求澄清定下后问用户要不要直接改原始需求文件 (2026-10-27)

R8 的两条需求澄清答复后只写回了 `design-closure.json` 的需求清单，用户需求.md 和工程规格.md 没动，因为规则写着“用户的需求文档本身不改”。
用户指出 ASG 和 SR 都要提示用户是否直接改原始需求文件，确认后直接改。改为：给定或采纳的答复，问用户要不要改原始需求文件
（点名文件、位置和要写入的文字），确认后直接改；答复里记 `requirement_files`（`UPDATED` 列改过的文件，或 `KEPT`），
暂缓的不问。没记的审计报 `requirement_files_not_asked`，记了已改却没列文件的报 `requirement_files_without_files`；
报告的需求澄清记录加“原始需求文件”一列。纲要文字不变。

- Event: user:2026-10-27
- Causes: rule_missing 1
- Changed: references/requirement-clarifications.md, references/workflow-handoff.md, scripts/audit_design_closure.py, scripts/render_design_report.py, tests/test_design_closure.py, tests/test_design_report.py, docs/improvement-ledger.md

## 需求没说清时当场问用户，答复写回需求清单，对齐 schematic-review (2026-10-27)

用户要求 SR 遇到需求不明时及时问用户、改需求清单后，指出 ASG 设计中遇到需求未明也应及时沟通。原做法只在任务 1.1 问会改变架构的缺口，
其余按假设设计、记成 `requirement` 待办“随交付一起问”；设计中途发现的缺口没有规定，答复不写回需求清单，没答复也能出图打包
（R6、R7 的 `design-closure.json` 里 `requirement` 待办都是 0 件，看不出是没有缺口还是没记）。
用户确认的改法：纲要任务 1.1、5.1 与架构表 ① 行改为需求缺口当场问用户，任务 1.2–2.3 中途发现的同样停下来问；每问附可验收的建议条文；
答复只有用户给定、采纳建议、明确暂缓三种（字段与 SR 的需求澄清相同），给定和采纳的以同编号写进 `requirements`；
暂缓的按建议条文作为假设设计，挂一件 `requirement` 待办，依赖它的计算为有条件成立（`rests_on: user_deferred`，报告写“依赖暂缓的需求”）；
未答复的问题审计 FAIL、报告列为记录问题、打包被拒；没有对应暂缓澄清的 `requirement` 待办不再允许；审查意见 `ASK_USER` 改为引用需求澄清；
`task.json` 可带 `clarification_answers`，没覆盖到的问题交 `NEEDS_INPUT`（无脚本读取 task.json，这一条只改了格式说明）。

- Event: user:2026-10-27
- Approved: user:2026-10-27
- Outline: ef01c0a229a92b30
- Causes: rule_missing 1
- Changed: SKILL.md, references/requirement-clarifications.md, references/requirements-to-intent.md, references/design-closure.md, references/review-comments.md, references/workflow-handoff.md, references/delivery-report.md, scripts/audit_design_closure.py, scripts/render_design_report.py, tests/test_design_closure.py, tests/test_design_report.py, docs/improvement-ledger.md

## 器件分级细化：电阻电容子类与档位、保护器件阈值计算、安全防护位置认证、类型声明照 SR 核对 (2026-10-26)

评估上一版分级时找出三处不完整，用户逐项定了改法（草案 `docs/proposals/2026-10-26-器件分级第3-5-6项草案.md`）。
一、常规件的规格只核电容耐压和电感电流，也不知道规格是否超出常规范围：电阻、电容按知识库二级类分子类（`fields.Category`，
依据为声明、手册所在库目录或推断），检流电阻和功率电阻按知识库目录核出的档位定级（WSL、ERJ 低阻、CRL、CRA、PR0x、AC 系列，注明页码），
档内为常规件、超档或要求脉冲/浪涌为特殊器件；检流电阻要写阻值、容差、功率，功率电阻要写容差、功率。
二、特殊器件的配合计算按保护作用、安规认证按安全防护位置：保险丝、压敏、TVS、稳压管和电源路径 NTC 要进两侧都算的阈值计算；
按 SR `domains.py` 的口径划分直流域，跨危险电压域的器件和 `high_voltage_nets` 上的安规件要写 `fields.Approval`，X/Y 电容要进放电/接触电流计算，
有安规器件而没写 `high_voltage_nets` 是记录问题。
三、类型声明核得粗、写得累：核对照 SR `datasheet_kinds.verify` 的六种结果（取不到文字列为“类型声明没核对”，不算通过也不拦），
具体类型优先，三个字母以内的关键词按整词匹配；`propose_part_kinds.py` 从手册首页前 8 行给候选（R6/R7 实测前 8 行 39/51 个唯一且正确、0 个给错，
整页约一半）。型号族关键词加边界：R7 U701 TPS26630（eFuse）曾被 `PS2[5-9]\d\d` 认成光耦（SR 同样，已在 SR 另开 session 修），
20 个公开工程重跑另修正 10 个（BSS138 被 `SS\d{2}` 认成二极管、LTV-817/827 光耦漏认）。
R6 试算：R303（0.30 Ω 1% 2 W 超 S4）和 R403、R407、R504、R604（脉冲）升为特殊器件，R304/R305 缺容差，F101、RV101、TH101、D303 缺阈值计算，
CX101、CY301 缺放电/接触电流计算；R7：R106、R201、R303、R503 只写了阻值，CY301 缺接触电流计算；两版都没写 `high_voltage_nets`。

- Event: user:2026-10-26
- Causes: rule_missing 3
- Changed: references/part-roles.md, references/requirements-to-intent.md, references/design-closure.md, scripts/schematic_layout/part_classes.py, scripts/render_design_report.py, scripts/propose_part_kinds.py, tests/test_part_classes.py, tests/test_design_report.py, docs/proposals/2026-10-26-器件分级第3-5-6项草案.md, docs/improvement-ledger.md

## 纲要 P3 与器件分级对齐 schematic-review：只有关键器件和特殊器件要写料号 (2026-10-26)

用户指出 ASG 作为设计方不应要求所有器件都有料号，P3“电路以确切 MPN 的数据手册为准”管得太宽，两个技能在器件分类上要对齐：
SR 对常规件不索要料号，按最弱档定界，超出的最低额定写进 DEV-D04 的 BOM 约束。上一版分级按位号和符号直接定级，
没有回答“这是什么器件”。现在分两步：先定器件类型（词表与 SR `device_kinds.py` 相同，另加 `mechanical`；关键器件和特殊器件按本器件手册
用 `fields.Kind`/`KindSource`/`KindQuote` 声明，常规件按符号与型号关键词、最后才按位号推断，矛盾或认不出都是记录问题），
再由类型和位置定级：关键器件（集成电路、晶体管、光耦、变压器与定制磁件、稳压管、TVS、整流桥）、特殊器件（安规件、
接在 `high_voltage_nets` 上的连接器与继电器、电源路径上的 NTC、计算引用了其手册的器件；未声明 `high_voltage_nets` 时连接器、继电器和 NTC
一律按特殊器件）要写 `mpn`、`datasheet` 和类型声明；常规件写值和规格，每个电容写耐压、每个电感写额定电流。用户定了四处：
高压连接器和电源路径 NTC 算特殊器件，继电器、电池、晶体算常规件，寿命需求下的电解电容写规格要求（按某系列寿命公式算的仍升为特殊器件）。
R6 需要料号的器件从 52 个降到 35 个；R7 缺料号或手册的从 24 个降到 8 个（另有 31 个关键/特殊器件要补类型声明）；
20 个公开工程的 2774 个器件中 11 个认不出类型（扬声器、麦克风、蜂鸣器、天线、振动马达、自定义机械件），须声明。
需求指定了系列或料号的器件按特殊器件写，脚本不读需求原文，由任务 1.1 核对。

- Event: user:2026-10-26
- Approved: user:2026-10-26
- Outline: 957c22f0f9387fc0
- Changed: SKILL.md, references/part-roles.md, references/requirements-to-intent.md, references/design-closure.md, references/terminology.md, scripts/schematic_layout/part_classes.py, scripts/render_design_report.py, tests/test_part_classes.py, tests/test_design_report.py, docs/improvement-ledger.md

## 器件分级改为位号前缀与符号家族都算、规格件白名单 (2026-10-26)

用 `part_classes.py` 给 GitHub 上 20 个公开 KiCad 工程的 2774 个器件分级，按器件实际类型逐组核对，错判 153 个，其中 150 个是该写料号的器件落成了规格件。
原因有两处：一是只看符号名或只看位号，按 MPN 命名的项目库符号（`Diode:1N4148WT`、`Power_Protection:PRTR5V0U2X`、自定义库的 RJ45/USB-C 连接器、
位号 AH/AL 的 `Q_NMOS`、位号 TR 的变压器、位号 REF 的 TL431）都漏了；二是“其余都是规格件”，表里没列到的类（晶体与振荡器、自恢复保险丝、磁珠、
继电器、电池、蜂鸣器/麦克风、天线、主控模块）全部放过。现在位号前缀和符号家族任一命中即算，规格件改为白名单（电阻与电位器、无极性电容、测试点、
跳线、开关、键盘轴、机械件），其余默认料号件。同一批器件错判降为 6 个（3 个自定义机械件被多要料号，3 个用 U 位号的连接器/LED 判为核心器件，
两者同样要求料号）；规则是照这批数据写的，这是样本内结果。R1–R7 的设计网表分级与改前完全相同。电解电容画成 `Device:C` 时按符号认不出，
`part-roles.md` 第 1 节改为要求用有极性符号。

- Event: test:扫描20个公开KiCad工程2774个器件现行分级错判153个其中150个料号件落成规格件
- Causes: rule_missing 2
- Changed: references/part-roles.md, scripts/schematic_layout/part_classes.py, tests/test_part_classes.py, docs/improvement-ledger.md

## 器件分级：核心器件和料号件必须写确切料号和数据手册 (2026-10-26)

对比 R6 与 R7 的设计结果时发现，R7 从需求重新设计后设计网表的料号精度倒退：电容的 MPN 全部丢失（C-LIFE 却按 BXW、PZJ 系列算寿命），
BAT54、S3J 只写系列名，压敏、安规电容、USB-C 插座等没有数据手册，而自动检查全部 PASS。按“计算或选型引用了某个系列”触发的检查
抓不到这些：R7 的计算只有 7 个位号引用了手册且都对得上，系列名只出现在检查名、`model` 参数和不带位号的资料缺口里。
用户要求分类有依据而不是自由选择，于是在 `part-roles.md` 第 1 节定义三级：核心器件（U/Q/T）、料号件（设计依赖的参数只有具体料号的手册保证：
分立半导体、保护件、安规电容、电解电容、电感与共模扼流圈、连接器）、规格件（值加通用规格即可），级别由符号库与位号判定
（`schematic_layout/part_classes.py`）。规则一：核心器件和料号件要写 `mpn` 和能找到的 `datasheet`（定制磁件用 `fields.DesignSheet`），
新设计缺了是记录问题、拒绝打包；有 `change-contract.json` 时只拦本版新增或改动的器件，沿用基线的列入未完成项。
规则二：引用器件手册的计算参数要写 `ref`、资料缺口要写 `refs`，且该位号在设计网表里的 `datasheet` 是同一份手册（同字节或型号名相同），
标准与定制磁件的磁芯手册除外。R1–R7 试算：七版核心器件都不缺；料号件缺料号或手册 R7 21 个、R1–R6 3–7 个（J101 交流输入端子每版都缺）；
R6 有 43 处引用未写位号，R7 有 6 处。“确切订货型号”无法从手册正文自动判定（R6 45 个正确料号中 10 个按编码表拼成，正文查不到原样），仍由任务 2.1 人工核对。

- Event: test:R6与R7设计结果对比R7有21个料号件缺料号或数据手册
- Causes: rule_missing 2
- Changed: references/part-roles.md, references/design-closure.md, references/requirements-to-intent.md, scripts/schematic_layout/part_classes.py, scripts/render_design_report.py, tests/test_part_classes.py, tests/test_design_report.py, docs/improvement-ledger.md

## 术语统一与步骤–任务分解 (2026-10-26)

用户要求像 schematic-review 那样把 ASG 的名词统一成专业术语，并按“步骤–任务”分解。同一概念此前有几种叫法
（`electrical-intent.json` 叫设计要求表、整板设计要求表、intent；`verify_schematic.py` 叫一键验证、一键自动检查；
“回路”既指回流又指控制环路），17 份 reference 中 16 份是英文。原九步（0–8）有四处与实际设计流程不符：分页放在架构一步、
选型与计算同一步、组装根图放在验证一步、“继续可完成的设计项”放在交付一步。按确认的草案
（`docs/proposals/2026-10-26-术语统一与步骤任务草案.md`）：主流程改为五个步骤、15 项任务（① 需求与方案、② 详细设计、
③ 原理图绘制、④ 设计检查、⑤ 设计输出），每项任务以“做完的标志”结尾，标志取自脚本已有的输出；架构一节加步骤–任务总表；
原各步规则文字搬到对应任务下，未删内容。统一用词写进 `terminology.md` 的“技能文档用词”表；16 份英文 reference 译成中文，
绘图纲要标题随之改为“绘图纲要（怎样决定结构）”（`check_ledger.py` 的 OUTLINE 同步）；`deliver.py` 的“一键验证”一步改名“自动检查”，
报告与打包提示里的“设计要求表”改为“设计网表”。新增 `tests/test_terminology.py`（文档里出现替换掉的词即失败）和
`tests/test_skill_steps.py`（每步 1–5 项连续编号的任务、每项以做完的标志结尾、总表与正文一致）。旧交付不回改。

- Event: user:2026-10-26
- Causes: knowledge_wrong 1
- Changed: SKILL.md, references/*.md (31 份), scripts/check_ledger.py, scripts/deliver.py, scripts/pack_design.py, scripts/render_design_report.py, tests/test_deliver.py, tests/test_design_report.py, tests/test_terminology.py, tests/test_skill_steps.py, docs/proposals/2026-10-26-术语统一与步骤任务草案.md, docs/improvement-ledger.md
- Approved: user:2026-10-26
- Outline: ed0ddfd0d1f4176a

## 位号块互换可读即拦下 (2026-10-24)

R6 重画的图面审阅发现 07_PD 的 R602/R603 两组位号与值并排夹在 CS+/CS− 两线之间，看不出归属，几何与可读性检查都通过。
先试“字段块离别的本体不比离自己的远”：R1–R6 的 48 页里 0.5 mm 容差命中 51 处，逐个对照已审阅的 PDF，
除 R602/R603 外都是旁边那件有自己更近的标注、读者不会认错。改为成对判断：两件的标注块互换后到本体的距离和
不比原样多出 1.27 mm 就算读得通两种归属。它在 R1–R5、原 R6、R5 从头审查导出的 49 页里只命中 R602/R603（容差 0–3 mm 结果不变），
重画后的 R6、tests 下 41 张图（99 个器件）和一块人工绘制的 RK3588 板为 0。`field_placer.swapped_label_pairs`
在 `Sheet.build()` 放完字段后运行，命中即报错（草稿记入失败项）；单边靠近而对方另有标注的情况仍归图面审阅。

- Event: test:R6重画图面审阅07_PD页R602与R603位号并排
- Changed: scripts/schematic_layout/field_placer.py, scripts/schematic_layout/recipes.py, references/human-readable-routing.md, tests/test_swapped_labels.py, docs/improvement-ledger.md

## R6 重画：四线交汇、图面审阅绑定本版 PDF、没算项可挂厂家资料待办 (2026-10-24)

按用户 2026-10-23 决定电气不变重画 100 W PD R6。ERC 把 four_way_junction 设为 error 后，03_PFC、05_Bias_Control、07_PD
有四处电源符号落在三线交汇点上；`Sheet.build()` 新增 `_check_junctions`：一点汇合四条以上导线、引脚和电源/标志符号即报错，
同一符号叠放的多个引脚（功率管的几个漏极脚）按 KiCad 算一个。重画后第一次出报告，`visual-review.json` 还是上一次导出的
审阅（method 写着“按位号沿用”），报告却写“图面审阅：已完成”：`check_visual_items` 在 `REVIEWED` 时要求 `pdf_sha256`
等于本版 `schematic.pdf` 去掉 /CreationDate、/ModDate 后的 SHA-256（两次导出只差这两项），method 也查“沿用”，
`render_design_report.py --pdf-sha256` 给出该值。审阅中 07_PD 的 R602/R603 两组位号并排夹在两线之间、看不出归属，
几何与可读性都通过，写进 human-readable-routing.md 第 4 节的审阅要点。升 parameter_version 2 时 R6 的 PORT-GATE 等没算项
等的是厂家资料，原规则只允许指向 design 待办：`not_calculated` 也可指向未关闭的 external 待办。
R5 从头审查暂缓的 W-T301-ISAT、W-U601-CV-ACCURACY 归因为缺知识，补进 qr-flyback.md、pd-output-control.md 的必算项与已知坑。

- Event: test:R6重画一键验证ERC四线交汇, test:R6重画报告把上一次导出的图面审阅当成已完成, test:R6重画图面审阅07_PD页R602与R603位号并排, review:SR-20261023-R5-从头审查-claude-5802e8c/W-T301-ISAT, review:SR-20261023-R5-从头审查-claude-5802e8c/W-U601-CV-ACCURACY, user:2026-10-23
- Changed: scripts/schematic_layout/recipes.py, scripts/render_design_report.py, scripts/audit_design_closure.py, references/delivery-report.md, references/design-closure.md, references/human-readable-routing.md, references/circuit-patterns/qr-flyback.md, references/circuit-patterns/pd-output-control.md, tests/test_four_way_junction.py, tests/test_design_report.py, tests/test_design_closure.py, docs/improvement-ledger.md

## 计算结论分三档，由参数依据推出：parameter_version 2 (2026-10-23)

R1–R6 六版 164 条计算全部 `conditional`：`supported` 要求没有任何遗漏项，而每条都能写出“样件实测”一类的项；
`missing_guarantee` 是自由文字，R6 的 PFC-CS 与 `omitted_terms` 逐字相同；98 个 `model` 参数里有 12 个需求输入和 1 个物性常数。
用户按 `docs/proposals/2026-10-23-计算结论分层草案.md` 定为三档。`parameter_version: 2` 时审计用 `calculation_basis()` 推出结论：
有 `typical`/`unspecified` 参数或挂着未关闭的缺资料待办为依赖厂家资料，有 `model` 参数或没算的项为依赖工程估计，
否则设计成立；写的 `conclusion`/`rests_on`/`coverage` 与推出的不一致即 FAIL。遗漏项分 `not_calculated`（指向未关闭的 design 待办）
和 `verify_by_test`（指向 validation 技术转交）；依据加 `requirement`、`constant`；需求挂着不成立的计算不能记 `design_supported`。
报告按三档计数并分两节列出每条依赖的参数。版本 1 照旧审计，报告写明没有分层；R6 不回改。

- Event: user:2026-10-23
- Changed: SKILL.md, references/design-closure.md, references/delivery-report.md, references/terminology.md, scripts/audit_design_closure.py, scripts/render_design_report.py, tests/test_design_closure.py, tests/test_design_report.py, docs/proposals/2026-10-23-计算结论分层草案.md, docs/improvement-ledger.md
- Approved: user:2026-10-23
- Outline: bc996312760f5e9a

## 按步审视的修正：工况角点、停产料号、暂缓意见归因 (2026-10-23)

按步审视 ASG 第 0–8 步对照 R1–R6 记录：R5 验收与从头审查的电气错误全部出在第 2 步，画图一侧没有。
其中三个 P1 不在原有工况清单里：21 V 轻载同步整流最短导通时间（F-SR-TONMIN）、90 Vac 被判为高线（F-PFC-90V）、
反馈光耦单点开路时输出越过电容额定（F-A）。第 2 步与 requirements-to-intent.md 第 4 节的清单加入“工作包络角点”
和“单点故障”两类，“最坏情况属于独立审查”改为只指逐参数的形式化证明，角点和单点故障由 ASG 算；
三条写进对应模式文件的必算项与已知坑。D201 MUR550APFG 在手册订货表里列为 DISCONTINUED（F-D201），技能没有任何地方查：
新增 `schematic_layout/lifecycle.py`，`render_design_report.py` 对设计要求表里有 `mpn` 和 `datasheet` 的每个器件读手册全文，
列在停产/不推荐新设计标题下的料号算记录问题，`lifecycle_reason` 保留时在报告“停产料号”一节列出；R6 的 45 个这类器件里只查出 D201。
R6 把 9 条暂缓的审查意见记为 `cause: none`、“下一轮再归因”，其中有 P1 的 F-SR-TONMIN：`cause: none` 的 `why_none`
写推迟归因的话算记录问题。原生几何通道范围冻结，不再增加对象类型，新缺口交图面审阅。

- Event: review:SR-20261023-R5-从头审查-claude-5802e8c/F-SR-TONMIN, review:SR-20261023-R5-验收-claude-6d74689/F-PFC-90V, review:SR-20261023-R5-验收-claude-6d74689/F-A, review:SR-20261023-R5-验收-claude-6d74689/F-D201, user:2026-10-23
- Changed: SKILL.md, references/requirements-to-intent.md, references/core-part-selection.md, references/review-comments.md, references/native-geometry.md, references/circuit-patterns/synchronous-rectification.md, references/circuit-patterns/pfc-boost.md, references/circuit-patterns/isolated-feedback.md, scripts/schematic_layout/lifecycle.py, scripts/render_design_report.py, tests/test_lifecycle.py, tests/test_design_report.py, docs/improvement-ledger.md
- Approved: user:2026-10-23
- Outline: 3e5d2f9bf2a2a798

## 建图与几何检查共用一条导线判定，页边统一 5 mm (2026-10-23)

`Sheet.build()` 手写了三条导线检查（离开 12 mm 内框、进标题栏、穿器件本体），几何检查又用 5 mm 边距和另一段
穿本体判定各查一遍，标题栏保留区的数在 `qa.py` 与 `generate.py` 各抄一份；同一根线可能建图不过而门禁通过，或反过来。
用户定为统一 5 mm。现在 `qa.wire_findings` 是唯一判定（`FRAME_MARGIN_MM = 5`、`title_block()`），建图对计划中的线段、
门禁对写出的导线各调用一次；建图时电源符号与标签的页内范围、可读性的纸张判断（HR-11）也用同一边距。
R6 八页的纸张判断不变，全部 PASS。

- Event: user:2026-10-23
- Changed: scripts/schematic_layout/qa.py, scripts/schematic_layout/recipes.py, scripts/schematic_layout/generate.py, scripts/schematic_layout/readability.py, references/drawing-recipes.md, references/human-readable-routing.md, tests/test_wire_envelope.py, docs/improvement-ledger.md

## 检查只为电路正确或交代不确定性：合并改动 (2026-10-23)

用户审定 9 个改进点后要求全量审查每一项检查：凡不服务于电路正确、也不交代不确定性的检查删除或改写，
并按 `docs/proposals/2026-10-23-合并改动草案.md` 逐步执行。本次落地：
删除 58 项只核记录形式或互相抵消的检查（网名来源证据、图面锁定、回归集、负责方措辞、无引脚对象的外部角色合同等），
改写 45 项为直接核对电路或写明“没核对”；无引脚对象改由符号的 `ComponentRole`（mechanical/documentation）加
“所有单元无引脚”判定；KiCad 10（20260306）注释格式加入并用 KiCad 10.0.6 实际保存的工程复核；
生成的工程把 `single_global_label`、`four_way_junction` 设为 error，一键验证读取工程 ERC 设置，除
`simulation_model_issue`、`footprint_filter` 外被设为忽略的规则即 FAIL；`deliver.py` 改为白名单状态、缺结果即停、
预检文件不成对 FAIL、新鲜度在打包前；新增手册引用核对（`schematic_layout/citations.py`：文件与页码错 FAIL，
数值找不到列入报告“引用待人工核对”，R6 的 190 条引用全部核对通过）；后果等级由 `consequence_class` × `occurrence`
推出；审查回复加 `recurs_from`，复发的意见不能归 `judgment`；图面审阅核对每个待看图对象都有处置、不得“沿用”；
新增 `references/terminology.md`，报告用语专业化，记录与 notes 里的禁用词和“共/全部 N …”总数由报告核对。
纲要按草案第四节修改（验证、支撑、P6、P7、第 5–8 步与全文术语）；第 8 步台账说明随 `check_ledger.py` 改为 Event/Changed 两行。

- Event: user:2026-10-23
- Changed: SKILL.md, README.md, references/terminology.md, references/design-closure.md, references/delivery-report.md, references/core-part-selection.md, references/review-comments.md, references/symbol-and-peripheral-contracts.md, references/project-verification.md, references/drawing-recipes.md, references/human-readable-routing.md, references/change-preflight.md, references/requirements-to-intent.md, scripts/deliver.py, scripts/audit_design_closure.py, scripts/render_design_report.py, scripts/verify_schematic.py, scripts/verify_design_preflight.py, scripts/check_ledger.py, scripts/pack_design.py, scripts/schematic_layout/citations.py, scripts/schematic_layout/native.py, scripts/schematic_layout/native_hierarchy.py, scripts/schematic_layout/design_change.py, scripts/schematic_layout/project_audit.py, scripts/schematic_layout/symbol_integrity.py, scripts/schematic_layout/reference_contract.py, scripts/schematic_layout/recipes.py, scripts/schematic_layout/readability.py, scripts/schematic_layout/scene.py, scripts/schematic_layout/system_block.py, scripts/schematic_layout/root.py, scripts/schematic_layout/qa.py, scripts/schematic_layout/net_name_origin.py, scripts/run_regression.py, tests/test_citations.py, tests/test_pinless_evidence.py, tests/test_design_report.py, tests/test_design_closure.py, tests/test_deliver.py, docs/improvement-ledger.md
- Approved: user:2026-10-23
- Outline: 1751f50ca861aaf9

## 交付按固定顺序一次跑完：deliver.py (2026-10-23)

R6 从待办记录到打包要手工串十来个命令，出过约 8 次操作错误：新鲜度检查拿错了文件（manifest.json）、
`--reference-contract` 给错文件、预检“有条件通过”时退出码非零把命令链断开、旧预检报告没删导致拒绝覆盖、
重放漏 `--output-root`；`delivery-evidence.json` 每版都要另写脚本生成。技能只有分步命令，没有执行顺序和参数的规范（rule_missing）。
现在 `scripts/deliver.py <交付目录>` 按固定顺序跑：准备、待办审计、生成前预检、出图、一键验证、交付预检、生成报告、
交付证据、证据新鲜度、打包、输入核对；参数记在 `record/deliver.json`，每版沿用；`inputs` 同时传给待办审计
（新增 `--input`）、一键验证和打包；每步状态从它写出的结果读，只有 PASS、DONE、有条件通过、未完成、AUTOMATED_PASS、
FRESH 继续，其余状态、没写出结果或命令出错即停；预检文件只有一个算 FAIL；交付证据按本次运行写出的文件生成。用 R6 副本实跑验证。

- Event: user:2026-10-23
- Causes: rule_missing 1
- Changed: SKILL.md, references/delivery-report.md, docs/operating-cadence.md, scripts/deliver.py, scripts/audit_design_closure.py, scripts/verify_schematic.py, scripts/README.md, tests/test_deliver.py, tests/test_design_closure.py, docs/improvement-ledger.md
- Approved: user:2026-10-23
- Outline: ec7bab061aca9f4d

## 待办只看本版；外部条件不确定时给出选型方案并先问再画 (2026-10-23)

用户审视 R3–R6 后指出：待办编号是否跨版本一致不重要，重要的是内容；每次交付的待办只由本版设计过程中确认仍需做的事项决定，
不需要版本之间的比较和收敛规则。原规则让每版比较未解决数与器件数、`pack_design.py` 在待办变多或有依据的需求变少时
要求 `regression_reason`，R6 也因此把 R5 的待办整体搬过来（judgment：规则把版本比较当成了设计状态）。
选型方面，RT7209B 一颗芯片带出 16 件外部资料待办中的 10 件，选型却不比较外部依赖，也不给用户可选方案（rule_missing）。
现在删除版本间比较（review-comments §3、design-closure 的收敛估算与每轮比较、`pack_design` 的倒退检查、notes 的 `regression_reason`），
保留“改图”点名的位号须与上一版不同这一核对；待办每版重新确认。每个选定候选写 `external_dependencies`；不为空时要有 2–3 个
`options`、一个推荐和理由，以及用户的 `decision`，第 2 步结束时先问再画；报告新增“外部条件不确定的选型”一节。
“上一版已审查的型号不换”改为作为候选之一同等比较。R4 的选型记录没写外部依赖，多一个报告问题（R1–R3 没有选型记录，原本就报缺失），按运行节奏第 5 步更新基线。

- Event: user:2026-10-23
- Causes: judgment 1, rule_missing 1
- Changed: SKILL.md, references/design-closure.md, references/review-comments.md, references/delivery-report.md, references/core-part-selection.md, scripts/pack_design.py, scripts/render_design_report.py, tests/test_design_report.py, tests/regression/baseline.json, docs/improvement-ledger.md
- Approved: user:2026-10-23
- Outline: 01b2862ba30f8cfa

## 不依赖计算的资料缺口写明理由 (2026-10-23)

把 R6 迁到 gap_version 1 时，W-VTR（固件上电行为确认）和 W-ISO（加强绝缘资格）没有任何数值计算依赖它们，
`calculations` 非空的要求只能靠挂不相关的计算来满足（rule_missing）。现在允许空列表加 `no_calculation_reason`，
报告在“影响的计算”写“无”并给出理由。

- Event: user:2026-10-23
- Causes: rule_missing 1
- Changed: references/design-closure.md, scripts/audit_design_closure.py, scripts/render_design_report.py, tests/test_design_closure.py, docs/improvement-ledger.md

## 资料缺口在待办里当场写清，报告按负责方汇总问题 (2026-10-23)

逐条讲解 R6 的外部待办时，用户发现设计时已经知道的资料缺口，报告没有讲清楚：待办只有一句 action，
缺的是哪条规格、为什么只能找原厂、要问什么都不在报告里；14 件 external 待办只用了两句共用的替代做法；
找谁写成“电路设计与原厂应用支持”；缺口细节只在“有条件成立的计算”表里，和待办没有关联。
归因：`missing_guarantee` 只要求写在计算上，external 待办只要求 owner/action/fallback，审计和报告都不要求说明缺口（rule_missing）。
现在 `gap_version: 1` 的未关闭 external 待办要写 missing（手册给了 / 还需要 / 页码）、why_external、calculations、consequence、
questions 和具体的 owner、本项自己的 fallback；审计报缺字段、出处格式、计算不存在或非 conditional、泛称负责方和重复替代做法；
报告逐件列出缺口、影响的计算和问题，新增“要向外部要的资料”一节按负责方汇总，计算表反查对应待办，结论单列缺外部资料一行。
有未关闭 external 待办却没有 `gap_version` 的交付报告提出问题；R1–R4 因此各多一个报告问题，这是真问题，按运行节奏第 5 步更新基线。R6 尚未迁移。

- Event: user:2026-10-23
- Causes: rule_missing 1
- Changed: references/design-closure.md, references/delivery-report.md, scripts/audit_design_closure.py, scripts/render_design_report.py, tests/test_design_closure.py, tests/test_design_report.py, tests/regression/baseline.json, docs/improvement-ledger.md

## 计算参数逐项有来源；优先手册规定的工作方式 (2026-10-23)

R5 的 U601（RT7209BGQW）GPIO1/GPIO3 用开漏灌电流直驱光耦 U403/U202。手册 GPIO 一节只有开路电压和偏置电流档，
没有灌电流、VOL 或导通电阻，参考电路 GPIO 悬空；R4-OPTO 计算却写了"VOL≤0.4V"，W-OPTO 记为 external 后照样交付。
归因：第 2 步已写"空白不能写成保证的 ≤/≥"，但 design-closure 的计算只有 checks 和自由文本假设，审计不查参数来源
（rule_not_enforced）；没有"优先手册规定的工作方式"的规则，"不用加电路去关闭证据缺口"和收敛估算反而把外置缓冲判为不采用
（rule_missing）；模式库"故障/许可信号光耦"把 GPIO 灌电流当默认驱动（knowledge_wrong）。
现在 `parameter_version: 1` 的计算逐项列 `parameters`（basis 与 `datasheet:<路径>#p<页>` 定位），手册没给的标 `unspecified`
并指向 `operating_points`；有可行的规定内替代却保留未规定方式即 FAIL、拒绝打包；缺 `parameter_version` 的交付报告提出问题。
R1–R4 的旧记录因此各多一个报告问题，这是真问题（旧计算确实没有参数来源），按运行节奏第 5 步更新基线。

- Event: review:SR-20261023-R5-从头审查-claude-5802e8c/F-GPIO-SINK, review:SR-20261023-R5-全新独立复审-1fe4df6/W-OPTO, user:2026-10-23
- Causes: rule_not_enforced 1, rule_missing 1, knowledge_wrong 1
- Changed: SKILL.md, references/design-closure.md, references/circuit-patterns/isolated-feedback.md, scripts/audit_design_closure.py, scripts/render_design_report.py, tests/test_design_closure.py, tests/test_design_report.py, tests/regression/baseline.json, docs/improvement-ledger.md
- Approved: user:2026-10-23
- Outline: 2c8f8fa9a4aa0bac

## 根图与 System_block 助手；纲要哈希覆盖主流程 (2026-10-23)

框架复查发现：第 1 步强制 System_block，第 6 步却只写"由工程脚本组装根图"，技能里没有任何组装代码或样例。
100 W PD R4 的 `record/scripts/assemble.py` 手写了层次图框坐标、子页实例路径改写、System_block
箭头逐点坐标与文字对齐特判、`.kicad_pro` 和 `sym-lib-table`，每块新板都要重写一遍，System_block 只能事后审计。
新增 `schematic_layout/root.py`：`Root.page/flow/isolation/write` 由页框推出流向线端点与箭头，
能量流与控制链线宽不同，写盘前拒绝压线文字并跑 System_block 审计；两页小板端到端 `verify_schematic.py`
为 AUTOMATED_PASS（`tests/test_root.py`）。同时纲要写明主流程步骤也须人确认，但哈希原先只覆盖纲要一节和 O1–O8，
现把 SKILL.md「主流程」纳入；硬性规则中与 P1–P7 重复的说法改为引用 P 编号。三项均经用户确认后实施。

- Event: user:2026-10-23
- Causes: rule_missing 2, knowledge_missing 1
- Changed: SKILL.md, README.md, references/drawing-recipes.md, scripts/README.md, scripts/schematic_layout/root.py, scripts/check_ledger.py, tests/test_root.py, docs/improvement-ledger.md
- Approved: user:2026-10-23
- Outline: 5c9fb9e09c709245

## ASG 纲要定为核心标准 (2026-10-23)

用户要求整个架构体现在纲要里，纲要作为 ASG 的核心标准，后续改纲要须先和人确认。
此前"纲要"只指绘图规则 O1–O8，核心原则分散在 SKILL.md 硬性规则、README 设计约定和改进计划三处；
改进闭环第 4 步允许按归因直接改技能，没有任何东西保护纲要。现在 SKILL.md 增加「ASG 纲要（核心标准）」
（架构、P1–P7、修改规则），O1–O8 改称绘图纲要并归入其中；`check_ledger.py` 对两段纲要文字取哈希，
与最新一条带 `Outline:` 的已确认台账条目不一致即 FAIL。草案经用户逐项确认后写入。

- Event: user:2026-10-23
- Causes: rule_missing 1
- Changed: SKILL.md, README.md, references/drawing-recipes.md, docs/operating-cadence.md, docs/improvement-ledger.md, scripts/check_ledger.py, tests/test_ledger.py
- Approved: user:2026-10-23
- Outline: 84c5b3a6360b1107

## Library lookup recognises renamed copies (2026-10-19)

Filing the 100 W PD datasheets showed that `locate_file` only matched a
library copy by the catalog's (stale) SHA-256 or by file name, so 25 files
that were already in the library under another name were reported missing.
It now also hashes library files of the same byte size, and one walk of
`raw/` serves a whole datasheets folder (130 files: 31 s → a few seconds).
On the 100 W PD inputs the unfiled list went 34 → 3 (one part and two
licence documents).

- Event: test:2026-10-19-100W-PD-datasheets-filed (filing session's report), user:2026-10-19
- Causes: rule_not_enforced 1
- Changed: scripts/find_parts.py, scripts/pack_design.py, tests/test_find_parts.py

## Reviewer side of selection and attribution (2026-10-19)

Improvement plan stage 5, done in the schematic-review repository
(`scripts/review_selection.py`, `references/selection-review.md`, its own
`docs/improvement-ledger.md` and `check_ledger.py`). SR now re-judges every
selection role and every attributed comment independently. On this side
review-comments.md says how those verdicts come back: a DISAGREE with an
alternative part is a DESIGN/REDESIGN item, a wrong rejection reason is
knowledge_wrong, a missing decisive condition is knowledge_missing, and a
comment that recurs after a judgment attribution may not be judgment again.
Left open: SR's own regression set over the same deliveries, which needs
reproducible review runs.

- Event: user:2026-10-19 (accepted improvement plan, stage 5)
- Causes: rule_missing 1
- Changed: references/review-comments.md

## Circuit pattern library, first batch (2026-10-19)

Improvement plan stage 4. part-roles.md says what a kind of part does;
nothing said how a function is usually built, which approaches exist and
what each one's known pitfalls are, so every board started from a reference
design's BOM. `references/circuit-patterns/` holds 16 patterns extracted
from 100 W PD R1–R4 (input protection, PFC, QR flyback, ZCD, Y-cap
bridging, bias supply, aux OVP latch, isolated feedback, synchronous
rectification, output storage, current sensing, PD output control, Type-C
protection, NTC sensing, test points, AC indicator); each approach lists
its part classes, required peripherals, calculations, pitfalls that cite
the R4 review items, and sources. `find_parts.py --patterns` searches
them; `page-plan.json` names a pattern approach per functional block (the
report checks it exists, or that lessons.json registers the gap). The
patterns live in the skill because the wiki schema has no such page type.

- Event: review:SR-20261019-R3-改版前独立审查-41f4ad3/W-OPTO, W-MLCC, W-SR, W-PORT-SOA, W-AUX-OVP, W-ZCD, W-CAL and the other R4 items cited in the pattern files; user:2026-10-19 (plan stage 4)
- Causes: knowledge_missing 16
- Changed: references/circuit-patterns.md, references/circuit-patterns, scripts/find_parts.py, scripts/render_design_report.py, tests/test_find_parts.py, tests/test_design_report.py, SKILL.md, references/delivery-report.md, README.md

## Operating cadence (2026-10-19)

Improvement plan stage 6. `docs/operating-cadence.md` fixes the seven
steps of every board version (deliver, independent review, attribute,
change, regress, ledger and commit, feed back test results), the checkpoint
of each step and the three numbers recorded per version.

- Event: user:2026-10-19 (accepted improvement plan, stage 6)
- Causes: rule_missing 0 (process document, no finding)
- Changed: docs/operating-cadence.md, SKILL.md

## Decisive conditions judged by the script (2026-10-19)

Improvement plan stage 3. `selection.json` recorded decisive conditions as
prose, so the report could only check that something was written, not that
the chosen part met it. Conditions are now objects (`param`, `op` in
<=, >=, covers, equals, has, `limit`, `unit`, `requirement`); every
candidate records the value it was read at with the page; selected and
alternate candidates must satisfy every condition, a rejected one must fail
at least one or carry a `reject_kind` (dependency, data, availability, cost,
preference). The report's selection table shows each rejection's basis. The
R4 record was converted: 11 roles, 48 candidates, 6 rejected on preference,
1 on data, the rest on a failed condition.

- Event: user:2026-10-19 (accepted improvement plan, stage 3)
- Causes: rule_not_enforced 1
- Changed: scripts/render_design_report.py, tests/test_design_report.py, references/core-part-selection.md

## Datasheet filing gate (2026-10-19)

Improvement plan stage 2. SKILL.md step 2 has long said every downloaded
datasheet is copied into the HardwareWiki library, and nothing checked it:
R4 declares 130 vendor documents as its datasheets input and the library's
coverage of them was unknown. `pack_design.py` now locates every PDF of the
`datasheets` input in the library (catalog SHA-256, else file name under
`raw/`) and refuses to pack while any is missing, naming them;
`find_parts.py --file <pdf>` answers for one file.

- Event: user:2026-10-19 (accepted improvement plan, stage 2)
- Causes: rule_not_enforced 1
- Changed: scripts/pack_design.py, scripts/find_parts.py, tests/test_find_parts.py, tests/test_design_report.py, SKILL.md, references/delivery-report.md

## Regression skeleton and the feedback channel (2026-10-19)

Improvement plan stages 0 and 1 (`docs/improvement-plan.md`). Until now a
review's findings became skill changes only when someone read the report and
decided what to change, and a rule change was verified only on synthetic
fixtures.

- `scripts/run_regression.py` re-runs the report and packing checks on the
  real deliveries listed in `tests/regression/boards.json` (100 W PD R1–R4;
  missing folders are skipped) and fails when a board's report problems,
  packing errors or gate statuses get worse than `baseline.json`. Nothing in
  a delivery is written.
- `record/lessons.json` is a required delivery record: one event per review
  item, datasheet page, test record or user correction, with a cause class
  and the file the change landed in (rules go to `scripts/`, knowledge to
  `references/` or the library, `judgment` must say why no rule could catch
  it, `none` must cite what was checked). The report lists them under
  本版学到的东西.
- Every review response carries `cause`; a cause other than `none` must have
  a matching event in `lessons.json` with the same class.
- `scripts/check_ledger.py` checks this ledger's newest entry for the three
  lines below; `tests/test_ledger.py` runs it on the real ledger.
- The 23 R4 review items were attributed: 14 rule_not_enforced (calculations
  the skill asked for but never enforced until d86e397's missing_guarantee
  and progress checks), 1 rule_missing (System_block gate, 20c7011), 7
  knowledge_missing (selection decisive conditions and part-roles rows), 1
  judgment (calibration budget).

- Event: review:SR-20261019-R3-改版前独立审查-41f4ad3/W-AC … W-DRAW (23 items, see the R4 delivery's lessons.json), user:2026-10-19
- Causes: rule_not_enforced 14, rule_missing 1, knowledge_missing 7, judgment 1
- Changed: scripts/run_regression.py, scripts/check_ledger.py, scripts/render_design_report.py, tests/regression/boards.json, tests/test_regression.py, tests/test_ledger.py, tests/test_design_report.py, SKILL.md, references/review-comments.md, references/delivery-report.md, README.md

## Core part selection (2026-10-19)

Asked how ASG decides which core parts to use, the honest answer was that it
did not: step 2 verified whatever MPN the architecture step had already
written, and the 100 W PD revisions took every IC from the one reference
design in the knowledge base. The skill also had no picture of what kinds of
parts exist, so it could not even start a search from the function needed.

- `references/part-roles.md` gives that picture: every category and
  subcategory of `HardwareWiki/raw/Datasheet` with what the part does, where
  it sits in a circuit and the parameters that eliminate candidates, plus a
  function → category index to start from. `find_parts.py --roles-coverage`
  keeps it aligned with the library's real subcategories (new subcategory in
  the library = missing row).
- `scripts/find_parts.py` searches the library's `catalog.json` (vendor,
  model, category, facets, optional first pages), lists PDFs not yet indexed
  as 未入索引, and finds reference designs and application notes by path. The
  library stays outside the skill (`HARDWARE_WIKI`, default
  `~/Documents/知识库/HardwareWiki`).
- `references/core-part-selection.md` fixes the candidate sources in order
  (user's parts list, previous reviewed revision, same-topology reference
  designs, library category search, external search last with the datasheet
  filed into the library), the elimination order and the record
  `record/selection.json`. `render_design_report.py` requires it: each role
  needs decisive conditions, sources and at least two candidates (or a
  reason), exactly one selected candidate whose MPN is the part's value in
  the intent, a reason per candidate, a datasheet that exists in the
  library, and every U/Q/T part covered by a role. The report gains a
  核心器件选型 section; `pack_design.py` refuses a delivery without it.

## 100 W PD R4 review follow-up (2026-10-19)

The R4 report passed every drawing gate and still showed the skill letting a
revision stand still. Traced to rules that only checked presence, not content:

- 18 of 23 review responses shared one `detail` sentence and 8 `DESIGN`
  responses pointed at work items whose `action` was the comment itself.
  `check_responses` rejects a `detail` reused across comments, requires an
  open design work item referenced by `DESIGN` to carry `progress` (what this
  version did, not equal to `action`), requires `REDESIGN` changes to name a
  part or page, and adds `CALC_DOC` (补计算/补文档) for document-only work so
  it is no longer called 改图. The report states after the summary how many
  comments were actually redrawn or recalculated.
- Open design work went 0 → 10 and supported requirements 8 → 0 between R3
  and R4 without a word. `pack_design.py --input previous=` compares both
  counts and refuses a regression unless `notes.json` gives
  `regression_reason`; it also checks that a `REDESIGN` response's named
  parts differ from the previous intent.
- All 27 calculations were `partial`/`conditional`, including 1.33 A < 3 A.
  `conditional` now needs `missing_guarantee` (which guarantee is absent) and
  `partial` needs non-empty `omitted_terms`; the report prints values with
  three significant digits instead of 16-digit floats.
- draw_pages.py kept gap=38 and pitch=35 behind 12 `justify` calls.
  `justify` takes `conflict` (part, pin or `text:<field>`) for spacing
  deviations, a reason alone leaves the finding open, and more than three
  justified spacing deviations on a page is a finding.
- `highlights` carried process talk ("第二轮将核销"); process words in
  highlights are a report problem.

## 100 W PD R3 drawing review (2026-10-19)

Reading the eight rendered pages of the R3 delivery against the drawing rules,
with every automated gate at PASS:

- All seven circuit pages were A3 with the drawing in 25–38 % of the 25.4 mm
  cells; 02_Input fitted A4 with its frame margin. The page scripts reached
  passing builds by widening gaps (C407 at 38 steps, R404 at 25, stubs of 24–25,
  pitches of 35) and never shrank them, which HR-11 forbids but nothing
  measured. `readability.measure` now reports `paper`, `content_size_mm`,
  `fits_paper`, `occupancy`, `cell_coverage`, `part_groups` and
  `longest_segment_mm`; a sheet whose content fits a smaller paper fails the
  gate (`oversized_paper`, waivable with a reason). Recipes record any gap,
  stub, explicit pitch, lead or rail/label length beyond `MAX_SPACING_STEPS`
  (12) and the structure audit lists them until `justify` names them. O7/O8
  say to shrink back after the build passes and to choose the paper afterwards.
- 03_PFC joined the FB divider to U201 and the drive to the power stage with
  13 local labels justified as "block boundary"; 06_Secondary was three islands
  (SR driver, output bank, shunt) joined only by rail symbols. `Sheet` takes
  the page plan's `blocks={name: [refs]}` and the audit rejects a local join
  label whose wired parts all belong to one block (HR-01); `part_groups`
  shows islands against the declared blocks.
- The System_block page had eight unnamed arrows, a control polyline ending in
  the void and a solid "isolation boundary" that looked like a wire and ended
  twice in the void; 06_Secondary sat on the primary row so the boundary had
  to snake. `schematic_layout.system_block` audits the cover: flow lines need
  a text within 6 mm, both ends on a block/arrowhead/line, a 隔离-labelled
  straight boundary that crosses no block, every block reached. It runs as the
  `system_block` gate in `verify_schematic.py` when the root holds sheets, and
  as `scripts/audit_system_block.py` alone. On R3 it lists 10 findings.
- The visual review dispositioned all 84 pin-text items with one copied
  sentence per page and cited "pixel-identical to the previously reviewed
  PDF" as its basis; the step-4 page plan was never saved. `page-plan.json`
  is now a required record (file, reader tasks, blocks covering every part on
  the page); `render_design_report.py` checks that each page's review traced
  at least one path per reader task and that each `render_review_items`
  disposition names its own symbol and is not reused across symbols.

## Finite native diameter semicircles, 2026-10-13

- A subsequent independent audit found terminal `Z` could append a 4097th
  segment after an exactly 4096-segment arc. All arc-path additions now use
  one bounded append operation, with a final total check. The 4096 budget is
  unchanged. Reject-first controls include the actual SVG consumer, closure,
  preceding ML strokes, later subpaths, repeated Z and token/radius overflow;
  exactly 4096 segments with and without closure remain legal. This closes
  a profile-budget violation; the audit did not establish lost electrical ink.

- A native absolute circular `A` on one page previously aborted full-project
  SVG parsing and prevented every page from obtaining a fresh context. Added
  the bounded, exact-diameter, unrotated half-circle profile documented in
  `references/native-geometry.md`; no reference, model or coordinate special
  cases, no page-failure isolation and no unknown-curve skipping.
- Every arc chord carries stroke+sagitta+serialization+numerical protection,
  shared by native ink consumers and foreign foreground contact checks.
  Physical conductor/pin-cap/pin-leg attribution remains strict MLZ. Full
  primitive equality, hidden text, causal deletions and fresh input/tool/raw
  producer bindings are unchanged.
- Reject-first vectors cover arc interior versus endpoint/bbox shortcuts,
  near tangency and wide paint, both sweeps, foreign dashes, malformed/overflow
  inputs, ellipses, transforms, filled glyphs and finite segment budgets.
  Native fixtures also retain wide-wire/tiny-aperture/glyph protections. A
  supported far native arc does not remove an existing unknown sheet-object
  gap or hide a measured finding behind that gap.
- ERC zero-violation policy is unchanged. Duplicate physical common-output
  facts require a future explicitly evidenced generic rule; same reference or
  same name does not authorize independent power outputs to connect.
- This entry describes scope and regression controls, not benchmark results,
  whole-page PASS, G1 reduction or hardware approval. Those require independent
  same-input measurement and review.

## Symbol and peripheral generation gates, 2026-09-15

- Added actual inner-pin-to-stroke checks, distinct from symbol AABBs and native
  electrical continuity. Stroke width, arc sweep, unit/style, hidden/zero-length
  pins and standard separate bodyless supply units have explicit treatment.
- Added source-bound exact MPN/package and full physical pin name/type contracts,
  direct native peripheral/assembly assertions and declared functional stages.
- Added automatic symbol checks to native generation verification and optional
  `--reference-contract` on both generation entrypoints. Supplying a contract
  makes its assertions a required automated gate; omitted evidence is not verified.
- Reproduced 33 corrected internal-leg/artwork candidates on a private full-board
  before/after regression while retaining two intentional NC-terminal candidates
  for explicit disposition. No private design or manufacturer PDF is packaged.
- Added 35 regression tests for real failure modes and negative mutations; all
  136 current tests passed. Scope adequacy, datasheet interpretation, functional
  performance, footprint dimensions and production release remain separate gates.

## Existing-project electrical changes and delivery, 2026-09-15

- Added a native-XML change-contract verifier: explicit component additions,
  removals and before/after identity/partition changes; retained physical NC
  pins; optional frozen-baseline hash and named/same-net/distinct-net contracts.
- Added a root hierarchy audit: instance-aware page/component counts, portable
  sheet paths, missing/cyclic children, annotation coverage, cached-library and
  multi-unit pin signatures, actual PDF count and descriptive baseline delta.
- Added neutral failure fixtures and native KiCad before/after resistor pin/value
  changes. Tests cover unexpected opens/shorts, DNP drift, pin loss, stale hashes,
  cache conflicts, reused sheets and historical PDF count mismatch.
- Carried forward System_block as the architecture cover, and documented module
  expansion, electrical redesign, canonical cross-page symbols and CopperPilot
  candidate provenance. No private board or vendor reference package is included.
- The tools are read-only verifiers, not an automatic multi-page writer. The
  project-specific geometry extensions are documented as bounded work requiring
  native validation; the stock engine's unsupported objects remain insufficient.
- All earlier generation, redraw and population mechanisms are retained. The
  release evidence is in `release-validation.md`; electrical/production approval
  and external service availability are not implied by these checks.

对应 2026-09-08 调研清单，更新于 2026-09-14。本表说明程序真正执行的规则，
不把流程文字或单一 ERC 结果当成已解决图面问题。

| 编号/原问题 | 落地变化 | 证据与边界 |
| --- | --- | --- |
| G1 临时写坐标和 S 表达式，缺稳定接口 | Circuit IR v2 → pin 编译 → 自动 layout → route → writer → native verification | `build_circuit.py`、输入/编译/每次尝试快照；旧 v1 明确定位接口继续可用 |
| G2 把 Buck 布局套到所有稳压器 | 分开 rc/divider/capacitor_bank/ldo/buck_async/integrated_power/functional | 角色合同拒绝缺失/不支持的角色；电源模板是布局模板，特定 IC 仍须电气与原生回归 |
| G3 控制区只考虑本体间距 | 按 body、pin 出线、Reference/Value 总占用计算行列；扩距重排 | 12 只长 Value 电容；改变字长后占用扩大；纸张不足明确失败 |
| G4 wire_geometry 只有统计，无穿芯检测 | 回读真实缓存符号，线段检查本体/字段/引脚 | 既有穿芯/线穿文字反例 + 生成前避障 + 生成后独立 QA |
| G5 按坐标猜功能组 | 原始电路模块/实例/角色；默认布局按实际连接遍历 | 两组 RC 实例隔离、单页拼排；不是完整电路功能识别或任意拓扑优化器 |
| G6 geometry check 缺统一覆盖与结果 | PASS/FAIL/INSUFFICIENT/REVIEW；对象、坐标、缺口、版本与 hash | 未覆盖的隐藏脚、叠加脚、复杂原生页对象不会伪装成零碰撞 |
| G7 固化可疑的连线规则 | 保留 KiCad 10.0.4 原生直连/未分段 T/旋转镜像实验 | 每次回归重做 native XML；不推广为所有历史版本必然相同 |
| G8 为了排版改变引脚或接口定义 | 编译器锁真实物理引脚；named pin 必须实库解析；符号 hash | 错脚、重名脚、遗漏脚、重复位号、库 hash 漂移全部拒绝 |
| G9 机械套公共地母线/PWR_FLAG | 标签必须在 presentation 显式选择；端口只绑定已声明网络 | 无自动标签降级、无自动补 PWR_FLAG 或改 pin type；复杂电源符号未覆盖则失败 |
| G10 没有固定生成回归包 | 旧 29 项加 IR/自动布局/多单元/属性/锁定/导入回归 | fixtures、原生 XML/ERC/PDF、源码对象探针、最终产物 hash；示例均标为测试夹具 |

四类主要痛点的自动验收：

- **器件堆叠**：分开分配真实总占用；生成后本体/字段相交仍是硬失败。
- **走线穿芯**：引脚朝向约束 + 完整线段避障；路由失败触发有限重排。
- **Value 堆积**：可见字段水平并预留宽度，采购/额定值另存隐藏属性；不截断原值。
- **布局不清楚/标题栏侵入**：按功能模块、方向、标题、留白拼页，预留页框和标题栏。
  自动布局只在硬约束通过后交付候选；可读性仍以最终原生全页与局部目检确认。

架构阶段的当前边界：

| 原建议阶段 | 当前状态 |
| --- | --- |
| 一：坏图必须被拦住 | 已有统一几何门禁与坏图反例；明确报告模型未覆盖对象 |
| 二：单功能块稳定生成 | 已有电路表示、模板、真实空间预算、自动放置/布线/复验；RC、电容阵列、多单元夹具实测；实际 Buck/LDO 等仍按具体器件复验 |
| 三：多块多页 | 模块复用、逻辑层次/端口/标量总线、多块单页已实现；原生多页 sheet/跨页导出、图形总线仍未实现 |
| 四：增量编辑 | 已有带差异与锁定检查的新目录再生成；不宣称支持任意手工工程原位编辑或任意已有分页工程的局部重排 |

对已有的复杂硬件工程，应先回读原生网表和组件身份，再建立经确认的 IR。
资料不足保持 INSUFFICIENT；本次没有把历史 LM5013/RK3576/SSA100 原图当作
已修复或已电气验收的成果，也没有改动它们。

复验入口：`python3 -m unittest discover -s tests -v`，以及
`tests/probe_structured_upstream.py`（可选上游隔离环境）。具体运行结果保存在
本地 `output/ir-integration/`，不把临时路径或测试数据当成正式产品输入。

## Engineer-reference comparison, TPS53355 Rev B (2026-09-10)

- Added explicit local routing groups with exact terminal partition validation,
  original-net labels and per-group fixed rails. Replaced the TPS53355 test's
  temporary-name monkeypatch with a supported low-level API.
- Added measured explicit visible fields, including 90-degree capacitor-bank
  fields, reserved before automatic fields and routing. Pin corridors are now
  also protected when placing labels on wired nets; interior wire label anchors
  are normalized as real split points.
- Added four regressions including native group connectivity/identity, rotated
  fields, invalid groups, immutable IR and collision rejection. Adapted the
  unsplit-T native probe to merge all contiguous segments, including extra
  label split points, before testing the same physical topology.
- Added an engineer-comparison guide and a reproducible compact TPS53355 draft.
  This is an explicit project recipe; automatic packing still does not choose
  this topology, capacitor MPNs/DC-bias guarantees or production constraints.

## Control-pin and peripheral completeness, TPS53355 Rev C (2026-09-11)

- Added explicit pin-provenance and peripheral-function ledgers to the workflow;
  distinguish datasheet-required connections, calculated values, default
  population and engineering options. Reference-image NC/DNP resistors retain
  actual wired pads instead of disappearing into an IC no-connect marker.
- Extended the TPS53355 example from 37 to 47 components (40 fitted, 7 DNP),
  with RF/MODE options, PG/VDD/VREG isolation links and VIN/load bypasses.
  Default RF remains electrically open at nominal 500 kHz; documented RF
  alternatives are held for frequency-dependent redesign and validation.
- Added a recipe-specific population gate: remove DNP, collapse fitted 0-ohm
  links, enforce mutually exclusive controls and compare retained baseline pin
  groups. Eight regressions cover errors that native all-pads ERC cannot detect.
  This is not a universal analog or arbitrary-assembly validator.

## Reference circuits and existing-project redraw (2026-09-14)

- Added datasheet peripheral contracts, explicit local branch ownership and
  negative mutations for a bounded KSZ8081RNA example. Added shared-terminal
  coverage and power-marker geometry regressions; connectivity includes each
  physical pad even where one drawn stem is shared.
- Documented the project-specific multi-page redraw workflow in
  `existing-project-redraw.md`: preserve hierarchy/identity, plan local circuits,
  compare complete native pin partitions and named interfaces, retain raw ERC
  and inspect its semantic delta. Existing electrical findings remain visible.
- Recorded native-grid and actual drawing-frame checks, per-page visual review,
  explicit handling of changed local net names, protected application to the
  original project and verification from the delivered path. Compare decoded
  pixels rather than PNG file hashes for visual equivalence.
- These are reusable checks and drawing procedures derived from project work.
  The project-specific multi-page writer and proprietary engineering sources
  are not distributed. The general generator remains a bounded single-sheet
  backend; this update does not claim arbitrary automatic board layout or
  electrical/production qualification of the examples.

## Readable drawing construction (2026-09-30)

- Root cause from a rejected 100 W charger redraw: blind coordinates and
  page-spanning ground wires, not the router. Added `recipes.Sheet`
  (`drawing-recipes.md`): supporting parts are placed from real pin geometry by
  series/shunt/bank/divider/lane recipes with explicit wires, power symbols named
  by net and fields placed last. Different-net contact, wires through bodies and
  unnamed disconnected pieces are rejected at build time.
- The readability checker is now a mandatory gate with reported locations and
  reasoned per-sheet waivers. HR-07 fixes label roles, including small local
  names on selected nets.
- Regression pair `tests/fixtures/drawing/recipe_board.py`: identical native
  partitions; the bad drawing reproduces the charger's support-net crossing and
  two-terminal U-turn and fails the gate. The fixture is not a qualified design,
  and the builder does not choose a topology's structure.
- Outline rules O1-O8 with `Sheet.plan` (proposed part and net roles from
  connectivity) and a structure audit; deviations need recorded reasons.
  Vertical global/local labels and names, render-verified on KiCad 10.0.6; the
  scene reader accepts the four tested local label styles. QA no longer reports
  a pin's own straight exit through graphics that overhang its tip (11 such
  findings on the charger v0.2.4 pages); foreign wires are still reported.
- Nine-page charger redraw (v0.2.5) with recipes: native identity, partitions and
  ERC by net group unchanged; readability, structure audit and geometry PASS on
  all pages. Added from that work: `bank` lead/depth, draft builds, corner
  fields, frame margin, named-part body clearance messages, coincident pads
  counted once for junctions, rung-vs-lane planning fix, and native global-label
  outlines in the scene reader (v0.2.4 pages: 60 QA errors -> 2).

## Requirements-first drawing focus (2026-10-07)

- SKILL.md now covers only the drawing flow from requirement documents to a
  verified schematic (936 → about 200 lines). Strict review is handed to
  `schematic-review`; the analyzer documentation moved unchanged to
  `references/analysis-toolkit.md`, without the mandatory SPICE/EMC review
  contract (those companion skills and `analyze_emc.py` are not shipped).
- New `references/requirements-to-intent.md`: requirement inventory, function
  trace, board intent format (`fields.Circuit` page key), OPEN items, handoff.
- Outline rules: O1 covers controller pages and folding a long path (the O1/O8
  conflict is removed), O2 groups anchors of one function, O3 resolves parts on
  nets shared by several anchors and anchor-less chains, O4 places negative
  rails; the audit coverage table states that the structure audit covers O4
  and O6 only.
- From the charger v0.4.0 project scripts: `Sheet.place(..., pin=, facing=,
  order=)` and `Sheet.orient()` replace project helpers that used the private
  `_shape`; `schematic_layout.pages.page_intents()` splits a board intent into
  page intents with external nets and page rails; `scripts/verify_schematic.py`
  replaces per-project gate runners. On charger v0.4.0 it reproduces the
  project's own results in about 3 s (intent partitions, hierarchy, symbols,
  readability PASS; the eight inherited `power_pin_not_driven` ERC findings;
  root `System_block` geometry INSUFFICIENT for sheet/polyline objects).


## 100 W PD R1 review follow-up (2026-10-16)

Problems found reviewing the 100 W PD R1 delivery, traced to skill rules:

- D403 aux-OVP zener shipped with prose only ("30 V envelope"); by estimate the circuit
  trips near 24 V output and no calculation covered it. Calculations now carry
  `refs` and numeric `checks`; `kind: "threshold"` needs both a
  `no_false_trip` and a `protection` side; every zener/TVS/reference in the
  intent must be named by a calculation (`threshold_part_uncalculated`).
- All 16 calculations were `conditional` because the project script hardcoded
  it. The conclusion must now agree with the checks
  (`conclusion_contradicts_checks`); a calculation without checks is rejected.
- LDO dissipation (0.73 W, MSOP) was left as "verify": device thermal
  feasibility (power → junction temperature) is now part of selection; only
  heat-sinking implementation goes to PCB.
- Repeated net text (`PFC_DRV PFC_DRV`): `Sheet.name()` no longer places a
  name on a connected piece that already has a label or rail symbol of that net.
- Geometry was INSUFFICIENT on every page with a symbol: pin numbers were
  appended as gaps unconditionally, shared-cache pin names too, and hidden
  `${INTERSHEET_REFS}`/cached `${KICAD9_SYMBOL_DIR}` counted as display
  variables. Library-hidden pin text is ignored; visible unqualified pin text
  is `render_review_items` for the render review. On R1: 5 pages PASS, 2 REVIEW
  (the two dispositioned clearance warnings), 1 INSUFFICIENT (filled arc in the
  USB-C symbol); pin-text items about 520 → 93.
- Calculation assumptions were English: record prose shown in the report must
  be Chinese; `render_design_report.py` reports English sentences as problems.
- D702–D706 (unidirectional PESD5V0L1UA, SMBJ24A) were drawn with KiCad
  `Device:D_TVS`, which is bidirectional only (A1/A2). Connectivity matched the
  intent, so no gate saw it. New `discrete_semantics` gate compares each
  symbol's cached description/pin names with the datasheet's first pages and
  standard TVS MPN suffixes (TVS direction, MOSFET channel, BJT type); on R1
  it fails all five and passes Q302/Q501/Q701.
- The last R2 geometry gap was two filled half discs in KiCad's
  `Connector:USB_C_Receptacle_USB2.0_16P`. Filled paths in the qualified
  circular-A profile are now covered by their bounding box (fill inside the
  boundary hull); curved glyphs and translucent fills stay unsupported.
- R2 geometry stayed REVIEW on two rail symbols within 1.27 mm of IC bodies,
  "dispositioned" in the visual review. That is a drawing defect ASG can
  close itself: `Sheet.build()` now runs the page gate's body_clearance /
  body_overlap check on the built page and fails (draft: records it), and
  SKILL.md forbids handing geometry REVIEW to a human. The report shows
  REVIEW as 没通过：要改图.
- Simplified: the geometry gate has no REVIEW state any more. Its four former
  warnings (body_clearance, graphic_text, graphic_wire/pin, wire_crossing) are
  errors, so a page is PASS, FAIL or INSUFFICIENT; a readability/geometry FAIL
  is a report problem and blocks packing.
