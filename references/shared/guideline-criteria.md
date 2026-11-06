# 共用设计准则库（G01–G09）

> 读者：SR 维护者（与 ASG 维护者、写设计准则的人共用；共用层文件，见 [shared-layer.md](shared-layer.md)）。

本文件、`guideline-criteria.json` 和 `scripts/guideline_criteria.py` 属于 ASG 与 SR 的共用层，两个技能里是同一份字节；
怎么改、哪条测试守见 [shared-layer.md](shared-layer.md)。

九份《硬件设计与审查共用规范》（G01 设计输入与工况 … G09 制造与可测试性）把标准条款写成设计准则。
ASG 按设计准则的 `asg_action` 设计并留证据，SR 按 `sr_check` 独立复核；两边用同一版设计准则库，但 SR 不继承 ASG 的结论。

## 一、文件

| 文件 | 内容 |
|---|---|
| `references/shared/guideline-criteria.json` | 汇编后的设计准则库：版本、词表、默认基线、全部设计准则与全部工程取值（含降额标准没给的 `unset_level`、`soa_segment_share`、`thermal_calc_trigger`） |
| `scripts/guideline_criteria.py` | 校验、汇编、按适用条件选规则、统计覆盖、共用层指纹；只用标准库 |
| `references/shared/vocabulary.json` | 词表：基线、电路类型、器件类别，每项名字与标题，加默认基线 |
| 规范工作目录下各 `G0x_准则登记.json` | 规则的源头（规范成文时写），汇编时读入 |

设计准则库里没有规则时（`rules: []`），两个技能照常运行，相关段落不出现。

## 二、汇编文件格式（`schema_version: 1`）

| 字段 | 含义 |
|---|---|
| `library_version` | 设计准则库版本，每次汇编由维护者给定 |
| `default_baseline` | 默认产品基线：`industrial_telecom`（工业/通信电路板卡） |
| `vocabulary` | 触发词表：`baselines`、`circuit_types`、`device_kinds` 的名字，汇编时从 `vocabulary.json` 抄入（词表的唯一出处，名字和标题都在那里；SR 的 `catalog.CIRCUIT_TYPES`、`device_kinds.KINDS` 和 ASG 的 `part_classes.KINDS` 都对着它核对）。校验器拒收与 `vocabulary.json` 不一致的汇编 |
| `specs` | 各规范的版本，如 `{"G03": "0.1"}` |
| `content_sha256` | 规则（有工程取值时连同工程取值）的规范 JSON 哈希；报告用它绑定确切内容 |
| `rules` | 设计准则，按编号排序 |
| `engineering_values` | 工程取值，按名称排序；没有时不出现。见第七节 |

## 三、设计准则字段

| 字段 | 要求 |
|---|---|
| `id` | `G0x-nnn`，如 `G03-005`；稳定不复用。与 SR 的审查要点 G1–G7、定界推法 G1–G6 格式不同，不会混 |
| `title`、`spec`（= 编号前三位）、`version` | 必填 |
| `status` | `draft` / `active` / `retired`；只有 `active` 被选用 |
| `nature` | `shall` / `should` / `method` / `project`。`project`（航天、军车等专用）必须写 `applies_when.baselines`，且不含默认基线 |
| `applies_when` | 见第四节 |
| `not_applicable`、`tailoring` | 不适用条件、允许的裁剪（文字） |
| `inputs` | 所需输入（文字列表）；跨规范只写到规范级（如“G01 电源输入工况”），不写其他规范的条号 |
| `asg_action` | ASG 的设计动作、本条特有的取值端（通用计算方法按 G02，不逐条引用）、应形成的证据、交下游的约束 |
| `sr_check` | SR 的独立检查方法、判据、证据要求、缺口处理、复验关闭条件 |
| `source` | 至少一条 `{document, edition, clause, page}`；**公开预览不能作出处**，文件名含“公开预览”“非全文”的被拒 |
| `relations` | `related` / `primary` / `reuses` / `conflicts`，各为准则编号列表，须在库内 |
| `closing_stage` | `schematic` / `pcb` / `simulation` / `prototype` / `production`；不是 `schematic` 的规则在两边都作下游约束列出 |
| `coverage` | 可选，覆盖方式。缺省即 `item`：逐条引用、逐条证据。`project_input`：一份需求基线或需求澄清记录一次回答，只核基线写明。`handoff`：列进下游交接清单，一条待办或交接表可覆盖多条，只核清单列出；`closing_stage` 不能是 `schematic` |

## 四、适用条件与选规则

`applies_when`：`baselines`、`circuit_types`、`device_kinds` 三个列表，加 `board`（全板规则）和 `text`（说明）。
一条 `active` 规则适用，当且仅当：

1. `baselines` 为空，或含本项目基线；并且
2. `board: true`，或本设计有它列出的某个电路类型，或有它列出的某个器件类别。

取值必须在词表里；词表外的值被拒。没有触发词又不是全板规则的规则被拒。

## 五、覆盖

`coverage()` 对适用准则分四类：被引用的（`covered`，列出引用处）、注明不适用及理由的（`not_applicable`）、
都没有的（`uncovered`），以及关闭阶段在原理图之后的（`downstream`，与前几类并列）。引用了库里没有的编号记 `unknown_cited`。有 `coverage` 不是 `item` 的准则时另有 `by_coverage` 分列三类，`project_input` 只由基线回答算覆盖。

- **ASG**：在需求追溯时于 `design-closure.json` 写 `guideline_version: 1` 和 `guideline_scope`
  （`library_version`、`baseline`、`circuit_types`、`device_kinds`、`not_applicable: [{id, reason}]`），
  在计算、待办和器件性能记录里用 `guidelines` 引用准则编号；关闭阶段在原理图之后的规则要有待办引用（交给下游）。设计完成核对与报告据此统计。
- **SR**：基线写 `intent.guideline_baseline`（不写取默认），电路类型与器件类别由 SR 自己的计划推出；
  规则总表里的 `BASIS` 把 SR 规则映射到设计准则，计划中出现的 SR 规则就覆盖了它映射的设计准则。
  映射的 SR 规则这次没有展开的（本板没有输入滤波器、首审没有改版、电路还没声明）记 `not_triggered`，报告写“未展开”；只有没有映射的才记 `uncovered`。
  电路类型要等电路决定写进 intent 后才齐：冷扫描时只有名称命中的电路类型，按其他电路类型触发的规则此时还不会出现
  （2026-10-31 联调：同一块锂电充电板，ASG 声明了 POWER_CONVERTER，SR 冷扫描只推出 USB）。
  7 个对外接口类型（`DC_48V`、`DC_24V`、`AC_MAINS`、`INDUSTRIAL_DI`、`POE_PD`、`VEHICLE_28V`、`SHIP_AC`）网络名没有识别到、intent 也没有声明时，
  报告提示“未声明对外接口”，不靠单一网络名判断。

## 六、更新设计准则库

1. 在硬件设计规范的 `准则登记/` 修改登记，并同步对应正文；词表、降额表、最弱档、应力规范及共用代码只在规范源目录维护。
2. 唯一构建、发布和安装入口是规范 `工具/guideline_criteria.py`，操作见 [shared-layer.md](shared-layer.md) 第四节及规范 `README.md`。词表显式指定，只读取九份直接子登记；正式包保存完整输入快照，同版不同字节拒绝覆盖。
3. 两个选定技能 worktree 均从同一发布包核清单后安装并各跑全量测试；技能内不得编辑共用载荷，不从一个技能向另一个复制。
4. 版本或指纹变化后，受影响的设计和审查按各自的复验规则重新打开；本次不改变既有指纹算法。

## 七、工程取值

标准不给数、要靠工程判断的取值（统计覆盖率、环路裕量下限、只有典型值时的估算倍数等）写在各规范登记的
`engineering_values` 里，汇编时并入设计准则库，**设计准则库是唯一出处**；技能不在代码或其他文档里另写数值。

| 字段 | 要求 |
|---|---|
| 名称（键） | 蛇形小写，如 `wca_statistical_coverage`、`g03_loop_pm_min`；全库唯一，两份规范定义同名时汇编报错 |
| `value` | 必填，任意 JSON 值 |
| `unit` | 可选 |
| `applies`、`basis`、`confirmed` | 必填：用在哪、依据、用户确认日期 |
| `spec` | 汇编时写入，取自所在登记 |

规则正文点名取值有两种写法：反引号括住的名称（`` `typical_band` ``），或 `g0x_` 开头的裸名。
校验器核对点到的名称都在库里。代码读取用 `guideline_criteria.engineering_value(name)`，命令行用
`python3 scripts/guideline_criteria.py value <name>`。
