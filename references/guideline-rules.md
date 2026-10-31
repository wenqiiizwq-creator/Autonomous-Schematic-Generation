# 共用规范规则库（G01–G09）

> 读者：SR 维护者（与 ASG 维护者、写规范规则的人共用）。

本文件、`guideline-rules.json` 和 `scripts/guideline_rules.py` 在 ASG 与 SR 两个技能里是同一份字节，改动时两边一起改；
SR 的 `test_guideline_rules.py` 在两边都装了时逐字节比对。

九份《硬件设计与审查共用规范》（G01 设计输入与工况 … G09 制造与可测试性）把标准条款写成规则卡。
ASG 按规则卡的 `asg_action` 设计并留证据，SR 按 `sr_check` 独立复核；两边用同一版规则库，但 SR 不继承 ASG 的结论。

## 一、文件

| 文件 | 内容 |
|---|---|
| `references/guideline-rules.json` | 汇编后的规则库：版本、词表、默认基线、全部规则卡 |
| `scripts/guideline_rules.py` | 校验、汇编、按适用条件选规则、统计覆盖；只用标准库 |
| 规范工作目录下各 `G0x_规则登记.json` | 规则的源头（规范成文时写），汇编时读入 |

规则库里没有规则时（`rules: []`），两个技能照常运行，相关段落不出现。

## 二、汇编文件格式（`schema_version: 1`）

| 字段 | 含义 |
|---|---|
| `library_version` | 规则库版本，每次汇编由维护者给定 |
| `default_baseline` | 默认产品基线：`industrial_telecom`（工业/通信电路板卡） |
| `vocabulary` | 触发词表：`baselines`、`circuit_types`（SR `catalog.CIRCUIT_TYPES` 的名称）、`device_kinds`（SR `device_kinds.KINDS`，与降额规范同一套）。SR 测试核对与登记一致 |
| `specs` | 各规范的版本，如 `{"G03": "0.1"}` |
| `content_sha256` | 规则列表的规范 JSON 哈希；报告用它绑定确切内容 |
| `rules` | 规则卡，按编号排序 |

## 三、规则卡字段

| 字段 | 要求 |
|---|---|
| `id` | `G0x-nnn`，如 `G03-005`；稳定不复用。与 SR 的审查要点 G1–G7、定界推法 G1–G6 格式不同，不会混 |
| `title`、`spec`（= 编号前三位）、`version` | 必填 |
| `status` | `draft` / `active` / `retired`；只有 `active` 被选用 |
| `nature` | `shall` / `should` / `method` / `project`。`project`（航天、军车等专用）必须写 `applies_when.baselines`，且不含默认基线 |
| `applies_when` | 见第四节 |
| `not_applicable`、`tailoring` | 不适用条件、允许的裁剪（文字） |
| `inputs` | 所需输入（文字列表）；工况引用 G01 规则编号 |
| `asg_action` | ASG 的设计动作、计算方法（引用 G02）、应形成的证据、交下游的约束 |
| `sr_check` | SR 的独立检查方法、判据、证据要求、缺口处理、复验关闭条件 |
| `source` | 至少一条 `{document, edition, clause, page}`；**公开预览不能作出处**，文件名含“公开预览”“非全文”的被拒 |
| `relations` | `related` / `primary` / `reuses` / `conflicts`，各为规则编号列表，须在库内 |
| `closing_stage` | `schematic` / `pcb` / `simulation` / `prototype` / `production`；不是 `schematic` 的规则在两边都作下游约束列出 |

## 四、适用条件与选规则

`applies_when`：`baselines`、`circuit_types`、`device_kinds` 三个列表，加 `board`（全板规则）和 `text`（说明）。
一条 `active` 规则适用，当且仅当：

1. `baselines` 为空，或含本项目基线；并且
2. `board: true`，或本设计有它列出的某个电路类型，或有它列出的某个器件类别。

取值必须在词表里；词表外的值被拒。没有触发词又不是全板规则的规则被拒。

## 五、覆盖

`coverage()` 对适用规则分四类：被引用的（`covered`，列出引用处）、注明不适用及理由的（`not_applicable`）、
都没有的（`uncovered`），以及关闭阶段在原理图之后的（`downstream`，与前几类并列）。引用了库里没有的编号记 `unknown_cited`。

- **ASG**：在需求追溯时于 `design-closure.json` 写 `guideline_version: 1` 和 `guideline_scope`
  （`library_version`、`baseline`、`circuit_types`、`device_kinds`、`not_applicable: [{id, reason}]`），
  在计算和待办里用 `guidelines` 引用规则编号；关闭阶段在原理图之后的规则要有待办引用（交给下游）。设计完成核对与报告据此统计。
- **SR**：基线写 `intent.guideline_baseline`（不写取默认），电路类型与器件类别由 SR 自己的计划推出；
  规则总表里的 `BASIS` 把 SR 规则映射到规范规则，计划中出现的 SR 规则就覆盖了它映射的规范规则。
  电路类型要等电路决定写进 intent 后才齐：冷扫描时只有名称命中的电路类型，按其他电路类型触发的规则此时还不会出现
  （2026-10-31 联调：同一块锂电充电板，ASG 声明了 POWER_CONVERTER，SR 冷扫描只推出 USB）。

## 六、更新规则库

1. 在规范工作目录改 `G0x_规则登记.json`（文件为 `{spec, version, rules}`）。
2. `python3 scripts/guideline_rules.py build --from <规范工作目录> --library-version <新版本> --out references/guideline-rules.json`。
3. 把三份共用文件复制到另一个技能，两边跑全量测试。
4. 规则库进入两个技能的工程规则身份：版本变化后，受影响的设计和审查按各自的复验规则重新打开。
