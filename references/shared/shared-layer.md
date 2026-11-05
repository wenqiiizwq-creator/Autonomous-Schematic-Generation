# 共用层（ASG 与 SR 同字节）

> 读者：SR 维护者（与 ASG 维护者共用；本页说明共用层本身，审查员和设计者只需知道这些文件两技能相同）。

ASG 设计和 SR 审查用同一套判据、同一张降额表、同一种判法。这些文件在 `autonomous-schematic-generation` 和
`schematic-review` 两个技能里逐字节相同，放在各自的 `references/shared/`，加上 `scripts/guideline_criteria.py` 和 `scripts/stress_check.py`。
本页是共用层唯一的说明：哪些文件、各管什么、谁读、哪条测试守、怎么改。其他文件只链接到这里，不再各自解释“与对方共用”。

## 一、四件事

| 事 | 文件 | 回答的问题 | 形状 |
|---|---|---|---|
| 判据 | `guideline-criteria.json`、`guideline-criteria.md` | 这种情况下该做什么（`asg_action`）、该查什么（`sr_check`），出处是哪条标准 | 设计准则（534 条，按基线、电路类型、器件类别选用）+ **全部工程取值**（标准不给、经用户确认的数） |
| 取值 | `derating-rules.json`、`derating-rules.md`；`commodity-floors.json` | 某类器件的某个应力在 I/II/III 级降到多少；常规件按封装能买到的最弱档是多少 | 查表（降额 233 条，数值来自四份降额标准；最弱档：片式电阻 8 个封装、MLCC 可订购档 5 行、触点 7 行，数值来自厂家目录，带核对日期） |
| 词表 | `vocabulary.json` | 基线、电路类型、器件类别叫什么 | 名字 + 标题；设计准则库汇编时抄入，SR 的 catalog/device_kinds 和 ASG 的 part_classes 都对着它核对 |
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
| `vocabulary.json` | `guideline_criteria.py`（汇编）、`part_classes.py` 对着它核对 | `guideline_criteria.py`、`catalog.py`/`device_kinds.py` 对着它核对 | ASG `test_part_classes.py`；SR `test_guideline_criteria.py` |
| `stress-spec.md`、`*.md` | 设计者读 | 审查员读 | 两边的对齐测试逐字节比对 |
| `scripts/guideline_criteria.py` | 以上 ASG 脚本导入 | 以上 SR 脚本导入 | 同上 |
| `scripts/stress_check.py` | `audit_design_closure.py`（降额限值核对、没点名规则的应力） | `derating.py`（余量判法、`implied_ratio`） | ASG `test_derating_audit.py`；SR `test_derating_rules.py`、`test_stress_spec.py`；对齐测试逐字节比对 |

对齐只有一条规则：`references/shared/` 下的每一份文件和 `scripts/guideline_criteria.py`、`scripts/stress_check.py`，两技能字节相同；目录里只能有
`guideline_criteria.SHARED_FILES` 列出的文件。ASG 的 `test_guideline_closure.py` 和 SR 的 `test_guideline_criteria.py`
在两边都装了时各做一次整目录比对。

## 三、指纹与版本

`python3 scripts/guideline_criteria.py shared` 打印每份文件的 sha256 和一行标签：**共用层 <指纹前 12 位>，设计准则库 <版本>，降额 v<版本>**。
指纹是 `SHARED_FILES` 里各文件 sha256 列表的 sha256，由已装文件现算，没有另一份要同步的清单。

- SR 出计划时把指纹写进 `review-plan.json` 的 `guidelines.shared_sha256`，门禁核对它与已装共用层一致，不一致要求重生成计划；报告的“共用设计准则覆盖”一节首行印这行标签。
- ASG 设计完成核对把指纹写进审计的 `guidelines.shared_sha256`，报告“共用规范”一行印这行标签。
- 设计准则库自己的 `library_version`、`content_sha256` 和降额表的 `version` 照旧，各管各的内容；共用层指纹把它们绑成一个。

## 四、怎么改

1. 在一边改（设计准则库从规范工作目录重建：`python3 scripts/guideline_criteria.py build --from <规范工作目录> --library-version <新版本> --out references/shared/guideline-criteria.json`；
   降额表、应力规范、本页直接改）。
2. 把 `references/shared/` 整个目录和 `scripts/guideline_criteria.py`、`scripts/stress_check.py` 复制到另一边。
3. 两边 `python3 scripts/guideline_criteria.py shared` 打出同一指纹。
4. 两边跑全量测试（SR `python3 -m pytest scripts/tests -q`，ASG `python3 -m pytest tests -q`）。
5. 共用层属于两个技能的工程规则身份：指纹变化后，受影响的设计和审查按各自的复验规则重新打开。

## 五、同名不共用

`calculation-preflight.md`、`workflow-handoff.md`、`requirement-clarifications.md` 两边都有，但内容各自独立：
ASG 的写设计方怎么做，SR 的写审查方怎么做（交接页是同一约定的两面）。它们不在 `references/shared/`，不比对字节。

## 1.9.0 的登记覆盖层（2026-11-05）

登记目录只读，ASG 的 `docs/registry-overlay-2026-11-05.json` 锁定九份源文件哈希；
用 `python3 scripts/build_registry_overlay.py` 在 `/tmp/codex-work/g01-g09/` 临时汇编。
运行包含 G01–G09。G06-025（外壳与板材阻燃）、G08-012（大件加固）、G08-046（焊点疲劳）、
G09-003（生产单路验证）、G09-006（探针意外短接）按用户决定排除，理由逐条见覆盖层。
当前登记已没有这五个编号，534 条全部保留；brief 的 529 预期与实读源不符，不能再次减五。
覆盖方式来自维护分类；五条 handoff 的 closing_stage 按原文接收对象作格式一致性修正，正文不改。
G05-031 按已批准草案 B 逐字替换动作并升条目版本。仅合入 main 时才把覆盖层写回登记。
条目存在与映射存在只说明进入适用清单，不能证明实际设计或审查已执行。
