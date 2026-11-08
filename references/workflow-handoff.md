# 任务输入输出格式 v1

由外部流程派发任务时读本页。它只规定 ASG 收什么、交什么，不改变 ASG 内部的设计和自检规则。
独立使用 ASG 不需要这些文件。

## 输入：task.json

由流程生成，ASG 不修改：

| 字段 | 含义 |
|---|---|
| `schema_version: 1`、`id`、`project_id` | 格式版本、任务、项目 |
| `skill` | `ASG` 或 `SR`；本页只讲 `ASG` 任务 |
| `design_version` | 当前可读版本号；每次交付另由任务 ID 区分 |
| `phase` | 默认 `design_iteration`；明确要求设计定型时为 `schematic_freeze` |
| `requirements` | 需求版本、目录、逐文件 SHA-256 |
| `skills` | 技能路径和版本信息，由程序管理 |
| `design` | 前一版设计交付目录及其哈希；首轮可为 null |
| `previous_review` | 前次审查意见，首轮可为 null；ASG 接受任何格式（SR 任务里是前次 SR 完整包）；按 [处理审查意见](review-comments.md) 逐条登记 |
| `open_items` | 前一轮留下的待办 |
| `clarification_answers` | 可选：对 ASG 上一轮提出的需求澄清的答复，每项 `{id, decision, text, by, date, source, requirement_files}`，按澄清编号对上；`requirement_files` 写是否让 ASG 直接改原始需求文件（见 [需求澄清](requirement-clarifications.md)） |
| `delegation` | 可选：无人当场答复时的代答授权 `{by, date, scope, rule, text}`。`by` 代答人（不含 `:` 和空格），`date` 为 `YYYY-MM-DD`；`scope` 取 `clarification`（需求澄清）、`selection`（选型确认，含 ② 中改变已确认选型后的重新确认）；`rule` 目前只有 `adopt_recommendation`（只能采纳 ASG 的建议）；`text` 授权原文，报告照录 |
| `output` | 本任务 result.json 的绝对路径 |

需求文档保留原文与未决项。设计网表（`electrical-intent.json`）由 ASG 从需求和手册独立写出，
不从图中回抄，也不拿别人的记录改名代替。

## 输出：result.json

仅支持以下顶层字段：

```json
{
  "schema_version": 1,
  "task_id": "任务 id",
  "task_digest": "task.json 对象的规范 JSON SHA256",
  "skill": "ASG",
  "status": "DELIVERED",
  "files": {"相对文件路径": "文件字节 SHA256"},
  "roles": {"角色": ["相对文件路径"]},
  "open_items": []
}
```

- 路径相对于 result.json 的父目录；禁止绝对路径、`..`、符号链接和重复路径。角色引用的文件都必须在 files 中。
- 交付内容就是 SKILL 任务 5.3 的交付目录（`设计报告.md`、`原理图/`、`设计资料/`、`record/`），先用
  `pack_design.py` 检查通过，再用流程提供的 `pack-result --roles roles.json --open-items open-items.json`
  生成 result.json；不手填哈希。
- 无人当场答复需求澄清时，ASG 用 `task.json` 的 `clarification_answers` 填 `answer`（`source` 写
  `{"source": "任务书", "locator": "<任务 id> clarification_answers <澄清编号>"}`，`by` 照抄该项）；没有逐项答复但有 `delegation` 的，
  需求澄清采纳建议条文、选型确认采纳推荐，来源写 `delegate:<代答人>:<日期>`（见 [需求澄清](requirement-clarifications.md)、[核心器件选型](core-part-selection.md)）。
  用到任务书答复或代答时，把 task.json 原样复制为 `record/task.json` 供审计核对。两者都没覆盖到的问题不往下设计，
  `status` 写 `NEEDS_INPUT`，每个问题是一件 `REQUIREMENT` 待办，`summary` 写问题，`next_action` 写建议条文。
- `DELIVERED` 只表示交付目录完整、可核对，不表示电路通过。缺需求、资料或方案输入时用 `NEEDS_INPUT`；
  工具没跑完用 `TOOL_FAILED`。后两者可以没有文件，但至少要有一个待办，不得用假文件凑角色。
- 每个待办为 `{id, kind, summary, next_action}`，均为非空字符串，ID 不重复。kind 取值：

| kind | 用于 |
|---|---|
| `DESIGN` | 还能用现有资料完成的设计、计算、选型、改图（含审查意见的 `REDESIGN` / `DESIGN`） |
| `EVIDENCE` | 需要厂家或别人提供的资料（含 `OBTAIN_DATA`） |
| `REQUIREMENT` | 没答复的需求澄清（含 `ASK_USER`），或用户暂缓的需求（待办阶段 `requirement`） |
| `REVIEW` | ASG 自检或图面审阅没通过、没做完 |
| `DOWNSTREAM` | 交给 PCB、结构、样机测试的要求（含 `HANDOFF`） |
| `TOOL` | 工具没跑完 |

## 角色

必需角色是审查方实际读取的文件，ASG 与 schematic-review 的交接约定用同一组名字：

| 角色 | 指向 |
|---|---|
| `schematic` | `原理图/` 下唯一的根 .kicad_sch；其他图页也在 files 中 |
| `netlist`、`render`、`bom` | `原理图/netlist.xml`、`原理图/schematic.pdf`、`原理图/BOM.csv` |
| `requirements` | 本任务的全部需求文件（字节哈希与 task.json 一致），可多个 |

可选的归档角色是 ASG 实际产出、随包收入的记录；审查方为保持独立不读取、不引用它们：

| 角色 | 指向 |
|---|---|
| `report` | `设计报告.md` |
| `electrical_intent` | `record/electrical-intent.json`（设计网表） |
| `design_closure` | `record/design-closure.json`（需求追溯、计算、待办与技术转交） |
| `native_summary` | `record/summary.json`（verify_schematic.py 原样输出） |
| `visual_review` | `record/visual-review.json`（图面审阅） |
| `delivery_evidence` | `record/delivery-evidence.json` |
| `manifest` | `record/manifest.json` |
| `review_responses` | `record/review-responses.json`；有审查意见时必填 |

除 `requirements` 外每个角色恰好一个文件。改版还应带上改动核对、动手前检查和复验记录（`record/` 内）。
临时文件放在技能目录以外的任意临时位置（默认 `$ASG_WORK_DIR`，未设置时用系统临时目录），不放进交付目录。
