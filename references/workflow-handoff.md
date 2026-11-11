# 任务书格式 v1

任务书是一个 `task.json`，在三种情况下用：单独运行部分模块、预先答复需求澄清、无人当场答复时授权代答。
独立使用 ASG、有人当场答复时不需要它。ASG 不修改任务书；用到它时原样复制为 `record/task.json`，供审计核对。

| 字段 | 含义 |
|---|---|
| `id` | 任务编号；答复来源的 `locator` 和模块报告引用它 |
| `modules` | 可选：只运行部分能力模块（SKILL.md「架构」、P7）。`{from, to, given}`：`from`、`to` 取 C1–C6；`given` 键是 `record/` 下的文件名，值 `{path, sha256}`，只能是 `from` 之前模块的产出。没有这个字段就是从需求到交付的整板流程。做法与交付见 [能力模块](modules.md) |
| `clarification_answers` | 可选：对需求澄清的答复，每项 `{id, decision, text, by, date, source, requirement_files}`，按澄清编号对上；`requirement_files` 写是否让 ASG 直接改原始需求文件（见 [需求澄清](requirement-clarifications.md)） |
| `delegation` | 可选：无人当场答复时的代答授权 `{by, date, scope, rule, text}`。`by` 代答人（不含 `:` 和空格），`date` 为 `YYYY-MM-DD`；`scope` 取 `clarification`（需求澄清）、`selection`（选型确认，含 C4 中改变已确认选型后的重新确认）；`rule` 目前只有 `adopt_recommendation`（只能采纳 ASG 的建议）；`text` 授权原文，报告照录 |

无人当场答复时：有逐项答复的按答复填 `answer`；没有逐项答复但有 `delegation` 的，需求澄清采纳建议条文、选型确认采纳推荐。
答复人和来源怎么写见 [需求澄清](requirement-clarifications.md)、[核心器件选型](core-part-selection.md)。两者都没覆盖到的问题不往下设计，停下来问。
