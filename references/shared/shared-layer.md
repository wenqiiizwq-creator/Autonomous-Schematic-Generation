# 共用层（固定发布包）

> 读者：SR 维护者（与 ASG 维护者共用；本页说明共用层本身，审查员和设计者按项目固定采用的版本与指纹）。

共用工程判据由硬件设计规范发布；ASG 和 SR 各自使用本技能中已安装并固定版本的发布包。采用同一发布包时全部载荷逐字节相同；独立分支可以采用不同版本，项目基线须可核。载荷放在各自的 `references/shared/`，加上 `scripts/guideline_criteria.py` 和 `scripts/stress_check.py`。
本页是共用层唯一的说明：哪些文件、各管什么、谁读、哪条测试守、怎么改。其他文件只链接到这里，不再各自解释“与对方共用”。

## 一、五项内容

共用规范 G01–G10：G01–G09 是设计准则（登记 534 条，ID `G0x-nnn`），汇编为 `guideline-criteria.json`；G10 是降额与应力规范（查表加判法，规则编号自成一套，如 `RES-FILM-V`、`*-TJ`，不进准则登记），发布为 `derating-rules.*`、`stress-spec.md`、`commodity-floors.json`。


| 事 | 文件 | 回答的问题 | 形状 |
|---|---|---|---|
| 判据 | `guideline-criteria.json`、`guideline-criteria.md` | 这种情况下该做什么（`asg_action`）、该查什么（`sr_check`），出处是哪条标准 | 设计准则（534 条，按基线、电路类型、器件类别选用）+ **全部工程取值**（标准不给、经用户确认的数） |
| 取值 | `derating-rules.json`、`derating-rules.md`；`commodity-floors.json` | 某类器件的某个应力在 I/II/III 级降到多少；常规件按封装能买到的最弱档是多少 | 查表（降额 233 条，数值来自四份降额标准；最弱档：片式电阻 8 个封装、MLCC 可订购档 5 行、触点 7 行，数值来自厂家目录，带核对日期） |
| 词表 | `vocabulary.json` | 基线、电路类型、器件类别叫什么 | 名字 + 标题；设计准则库汇编时抄入，SR 的 catalog/device_kinds 和 ASG 的 part_classes 都从它读取名字与标题 |
| 判法 | `stress-spec.md` | 一条应力余量怎么判：超额定不成立、超降额是应力风险、降额内合格 | 文字判法 |
| 代码 | `scripts/guideline_criteria.py`；`scripts/stress_check.py` | 校验、汇编、选规则、统计覆盖、共用层指纹；应力核对的算数：某级降额限值、一条应力对额定与降额值的判法（`verdict`）、没点名规则时按器件类别与量纲挑规则（`fit_rules`） | 只用标准库，不导入任一技能的模块；两边的 `derating.py` / `audit_design_closure.py` 只读记录、只管措辞 |

分工的边：**标准给的数**在降额表，**厂家目录给的数**在最弱档表；**标准不给、靠工程判断的数**全部在设计准则库 `engineering_values`（含降额表原有的
`unset_level`、`soa_segment_share`、`thermal_calc_trigger`，2026-11-02 迁入 G01/G03；`passive_stress` 原有的 `weakest_share`、`assumed_resistor_package`，同日迁入 G02）；
**该做什么、该查什么**在设计准则；**余量怎么判**在应力规范，算这个判法的代码在 `stress_check.py`；**名字**在词表。一个数、一个名字、一种算法只有一个家。

## 二、谁读、谁守

| 文件 | ASG 读它的脚本 | SR 读它的脚本 | 守它的测试 |
|---|---|---|---|
| `guideline-criteria.json` | `audit_design_closure.py`（选规则、统计覆盖、读 `unset_level`）、`render_design_report.py`、`schematic_layout/component_requirements.py`（`unset_level`） | `catalog.py`（`BASIS` 校验）、`plan_review.py`（选规则）、`validate_review.py`（门禁核对）、`render_report.py`、`bound_formulas.py`（`soa_segment_share`、`typical_band`、`forced_beta_k`）、`checkers/passive_stress.py`（`unset_level`） | ASG `tests/test_guideline_closure.py`；SR `scripts/tests/test_guideline_criteria.py`、`test_guideline_plan.py` |
| `derating-rules.json` | `audit_design_closure.py`、`schematic_layout/component_requirements.py` | `derating.py`、`checkers/passive_stress.py` | ASG `tests/test_derating_rules.py`、`test_derating_audit.py`；SR `scripts/tests/test_derating_rules.py`、`test_stress_spec.py` |
| `commodity-floors.json` | `audit_design_closure.py`（功率最弱档）、`schematic_layout/component_requirements.py`（耐压最弱档） | `checkers/passive_stress.py`（`RESISTOR_FLOORS`、`MLCC_ORDERABLE`） | ASG `test_derating_audit.py`、`test_component_requirements.py`；SR `test_commodity_floors.py`（含 `commodity-floors.md` 三张表与文件逐项相等） |
| `vocabulary.json` | `guideline_criteria.py`（汇编）、`part_classes.py` 读取名字与标题 | `guideline_criteria.py`、`catalog.py`/`device_kinds.py` 读取名字与标题 | ASG `test_part_classes.py`；SR `test_guideline_criteria.py` |
| `stress-spec.md`、`*.md` | 设计者读 | 审查员读 | 各自的本地安装包完整性测试；配对字节核查由规范发布检查承担 |
| `scripts/guideline_criteria.py` | 以上 ASG 脚本导入 | 以上 SR 脚本导入 | 同上 |
| `scripts/stress_check.py` | `audit_design_closure.py`（降额限值核对、没点名规则的应力） | `derating.py`（余量判法、`implied_ratio`） | ASG `test_derating_audit.py`；SR `test_derating_rules.py`、`test_stress_spec.py`；本地包校验与规范发布检查 |

本地回归只检查本技能的 `shared-release.json`、十个受控文件、版本与指纹，不访问对方源码、工作区或 HEAD。
`python3 scripts/guideline_criteria.py verify-installed` 校验本地安装包；功能测试继续用明确输入与预期核对分类、应力和覆盖。
配对字节一致检查由规范的 `工具/check_release_consumers.py <候选包> --target <ASG快照> --target <SR快照>` 承担，目标必须显式给出。
它先核候选包完整清单，再核各目标本地包与该候选的版本、指纹及全部载荷哈希；损坏或不同包都拒绝。

## 三、指纹与版本

`python3 scripts/guideline_criteria.py shared` 打印每份文件的 sha256 和一行标签：**共用层 <指纹前 12 位>，设计准则库 <版本>，降额 v<版本>**。
工程指纹只有一种格式 `shared-paths-sha256-v2`：对相对路径到文件 SHA-256 的映射按键排序，以 UTF-8 紧凑 JSON（无末尾 LF）求 SHA-256，不依赖隐含列表顺序。
工程范围为准则 JSON、词表、降额 JSON 及含规范性规则的降额 Markdown、最弱档、应力规范、两个共用脚本。
本页与 `guideline-criteria.md` 为说明，不进工程指纹；所有十个载荷及发布输入仍逐文件核完整性。
维护历史保存在规范目录的维护与历史记录中，不属于运行工程身份。

计划/审计记录须写明采用的共用层版本、指纹及指纹格式；版本或工程身份变化按规定重验。

- SR 计划 `guidelines` 与 ASG 审计 `guidelines` 写 `library_version`、`shared_sha256`、`fingerprint_format`，报告按记录显示身份。
- 规范 `发布/` 只保留现行版，旧版只在 `发布/版本历史.md` 留一行；版本兼容靠统一到现行版。缺格式、旧格式或非现行版的记录一律报“重生成”，不做旧算法校验。
- 新包下须重新生成旧计划/审计并复验受影响项，不批量补字段或重算旧指纹，不迁移旧 PASS；原计划、结果和审计保留。
- 准则 `content_sha256` 只表示准则与工程取值，不替代共用层身份；版本或工程指纹变化均触发规定的重验。

## 四、怎么改

唯一维护源在硬件设计规范：准则与词表在 `准则登记/`，G10 在 `规范正文/G10_元器件降额与应力规范/`（源文件名 `降额规范.md`、`降额值.json`、`应力判法.md`、`常规件最弱档.json`，发布时映射为本包文件名），本页与 `guideline-criteria.md` 在 `工具/包说明/`，共用脚本在 `工具/`。**技能内不得编辑共用载荷。**
发布、安装、验收与清理旧版的完整步骤和命令只写在规范 `README.md`“增改准则”一节。指纹变化后，受影响的设计和审查按各自的复验规则重新打开。

生产默认装载固定安装包；`GUIDELINE_CRITERIA` 替代输入仅在显式 `GUIDELINE_CRITERIA_TESTING=1` 的测试模式允许。生产误设替代输入会报错，不继续配上安装包指纹。替代输入同时绑定实际 JSON 字节的 SHA-256 和 `guideline_input`；即使显式启用测试模式，也不能标成安装包身份。内存合成输入按规范 JSON 序列化绑定。检查其他文件使用显式路径，发布与安装不读取测试替代输入。

## 五、同名不共用

`calculation-preflight.md`、`workflow-handoff.md`、`requirement-clarifications.md`、`docs/improvement-ledger.md` 两边都有，但内容各自独立：
ASG 的写设计方怎么做，SR 的写审查方怎么做；交接页的角色名与 `task.json` 字段两边一致。SR 的 `references/commodity-floors.md` 是 `commodity-floors.json` 的人读表加审查方法，三张表由 SR 测试与本包逐项核对。它们不在 `references/shared/`，不比对字节。

## 六、跨技能状态词对照（只读，不约束各自用词）

| ASG | SR | 含义 |
|---|---|---|
| 计算结论 `supported` | 余量依据为保证值的 PASS | 全部输入为保证值、推导值、设计选定值、需求值或物理常数 |
| `conditional`（依赖工程估计） | 合格但有风险（估算） | 用到工程估计 |
| `conditional`（依赖厂家资料）、参数依据 `unspecified` | INSUFFICIENT / 缺厂家资料（`VENDOR_DATUM`） | 用到典型值、手册未给参数或未关闭的缺资料待办 |
| `failed` | FAIL / 不合格 | 算出不满足 |
| 设计定型 | 冻结准出（`schematic_freeze`） | 设计完成且独立审查通过 |
| 技术转交 | 下游移交 | 交给 PCB、结构、固件等后续环节的约束 |
| `external_supply`（设计网表字段：声明只由连接器引入的电源或地） | `source_role` 取值 `external_supply`（电源轨来源节点的角色） | 同名不同义 |
