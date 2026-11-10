# 需求澄清：当场问用户，答复写回需求清单

需求没说清、而设计要靠它定时，**当场问用户**，用户答复后**马上写回需求清单**，再按定下的需求往下设计；
不把“需求没定”留到交付时才问（2026-10-27，用户：在 ASG 的设计中遇到需求未明的问题时，也应该及时和用户沟通）。
问题和答复写在 `record/requirements.json`（模块 C1 的产品）的 `clarifications`，本页是它的字段与核对约定。
与 schematic-review 共享的字段：`id`、`requirement_ids`、`question`、`requirement_text`、`proposed_requirement`、`answer`（`decision`、`text`、`by`、`date`、`source`、`requirement_files`）；`found_in`、`merged_into` 是 ASG 独有字段。
两边对暂缓（`DEFERRED`）的处理不同：ASG 按建议条文设计并挂 `requirement` 待办；交给审查方后，这些需求不审，列在审查报告“本次不审的范围”里。

## 问什么

只问证据和工程判断解决不了、且确实要用户决定的产品取舍：需求没写、写得含糊、前后矛盾或尚未确认。
先查需求文档、接口约定和已确认的对话，问题里写明查过什么。与本设计无关的模板空白不问。

| 情况 | 处理 |
|---|---|
| 需求没写、含糊或冲突，且会改变架构、选型、设计值或保护目标 | 当场问 |
| 需求已定，缺原厂资料 | `external` 待办，不问 |
| 需求已定，设计没做完 | `design` 待办，不问 |
| 设计约束没给（环境温度、裕量），在合理取值范围内选型和取值都不变 | 写明假设及出处（行业常用、厂家建议），不问 |
| 同上，但取值会改变选型或取值 | 问 |
| 启动计算要用的启动期负载（阻性/恒流/恒功率的值）需求没给，负载又不在本板上（用户 2026-11-04；审计 `startup_load_undeclared`，见[设计记录](design-closure.md)“工况输入的来源”） | 问，附按需求上限算的结果和推荐值；不把估计值写进算式 |
| 降额等级（I/II/III 级）需求没写 | 问，附建议等级（按 [降额规范](shared/derating-rules.md)“降额等级从哪来”一节，写明产品失效后果和工作方式）；暂缓的按建议等级作为写明的假设 |
| 可预见的误接或对外暴露（反接、对外接口 ESD、用台架电源代替规定的源）需求没提，后果只是本板可更换的局部损坏 | 写成假设或技术转交，不问 |
| 同上，但后果涉及安全（起火、触电、无保护电池被短接），或会让需求内的功能失效 | 问，问题里写明危害路径和推荐的电路方案 |
| 实际热、布局、实测等后续环节的事 | 技术转交，不问 |
| 成本估算超过需求的目标，或设计改动要在成本、体积、余量之间重新取舍 | 问，附估算和各方案的代价（R8：加了器件却没估成本） |
| 答复只定了一侧界限，另一侧会影响功能（只定了 LED 电流上限，亮度下限决定看不看得清） | 答复时当场确认另一侧，不留到设计中途 |

一个独立决定只问一次，同一个决定影响多处时只建一项；不同参数即使来自同一本需求书，也不合并。

## 什么时候问

- **任务 C1.1**：录完需求后盘点一遍要用户定的问题，**一次汇总问用户**，不逐颗器件打断。
- **任务 C2.1–C5.1 中途**：选型、核手册、计算或写设计网表时又发现新的需求依赖，停在当前任务问；
  答复写回需求清单后，从受影响的任务重做，会改变架构的回到 1.2。
- **处理审查意见时**：要用户定需求的意见同样当场问，答复写回需求清单后从受影响的模块重做。

**有未答复的问题不进入 C4。** 审计在自动检查（`verify_schematic.py --design-closure`）、生成报告和打包时都把未答复的问题判为 FAIL，
`pack_design.py` 拒绝打包。由外部流程派发、无人当场答复时，见 [任务输入输出格式](workflow-handoff.md) 的 `clarification_answers`。

## 答复只有三种

| `answer.decision` | 含义 | 写回需求清单 |
|---|---|---|
| `DECIDED` | 用户给定需求 | `requirements` 加一条，编号与澄清相同，`text` 就是 `answer.text`；计算参数可引用 `req:<澄清编号>` |
| `ADOPTED_PROPOSAL` | 采纳 ASG 的建议条文 | 同上；`answer.text` 与 `proposed_requirement` 一字不差 |
| `DEFERRED` | 用户明确暂缓 | 建一件 `requirement` 待办：`clarification` 写澄清编号，`assumption` 照抄建议条文；`requirement_ids` 点名的需求不能是 `design_supported`；依赖它的计算写进该待办的 `calculations`，结论为有条件成立（`rests_on: user_deferred`） |

用户一时定不下来时，只能采纳建议或明确暂缓，不能“先挂着”。暂缓时 ASG 仍要交出能画的电路，所以按建议条文设计。
**给定或采纳后，问用户要不要直接改原始需求文件**（2026-10-27，用户：ASG和SR都需要提示用户，是否直接更改原始的需求文件。用户确认后，直接改）。
问的时候点名改哪个文件的哪一处（如工程规格 §4.1 某行、决定表新增一行），给出要写入的文字；用户确认后马上直接改，
不确认就只写回需求清单。不论改不改，都在 `answer.requirement_files` 记下用户的决定。暂缓的不问：需求还没定。
改过的需求文件在打包时按新的哈希登记进 manifest，没改的文件保持原样。
暂缓的需求后来定下了，把答复改为 `DECIDED` 或 `ADOPTED_PROPOSAL`、写回需求清单、关闭待办，再按定下的数值复算。

## 字段

```json
"clarifications": [{
  "id": "CL-LOAD",
  "requirement_ids": ["REQ-OUT-02"],
  "found_in": "2.2",
  "question": "5 V 输出最大连续电流没给，电感饱和电流、限流门限和损耗没有依据",
  "requirement_text": "需求规格 Rev A §3.2：“输出能驱动常见负载”，未给最大电流",
  "proposed_requirement": "5 V 输出最大连续电流 2 A（25～60 ℃），峰值 3 A 持续不超过 100 ms",
  "answer": {"decision": "ADOPTED_PROPOSAL", "text": "5 V 输出最大连续电流 2 A（25～60 ℃），峰值 3 A 持续不超过 100 ms",
             "by": "用户", "date": "2026-10-27",
             "source": {"source": "对话记录", "locator": "2026-10-27 需求澄清第 1 问"},
             "requirement_files": {"decision": "UPDATED", "files": ["需求/需求规格.md"]}}
}]
```

- `id` 写成 `CL-<名字>`，不与需求文档里的编号重复。
- `requirement_ids` 列这次澄清涉及的需求编号，须在 `requirements` 里；需求文档根本没提到时写 `[]`。
- `found_in` 写在哪项任务发现的（`1.1`、`2.2`、`review` …）。
- `question` 写设计卡在哪里；`requirement_text` 引需求原文及位置，没提到时写“未提及”并列出查过的文档与章节；
  `proposed_requirement` 写建议补进需求的条文，要具体到可验收的数值、工况或允许/禁止的行为，有多个口径时写推荐项并注明其他选项。
- 还没答复时不写 `answer`。答复写 `decision`、`text`（定下的需求，或暂缓的原话）、`by`、`date` 和能定位的 `source`
  （对话记录或任务书 `clarification_answers` 里的一处）。`by` 写真实答复人或角色，不虚构。

  | 答复来自 | `by` | `source` |
  |---|---|---|
  | 用户当场答复 | 真实答复人或角色（“用户”“产品负责人”） | `{"source": "对话记录", "locator": …}` |
  | 任务书逐项预填 | 与 `clarification_answers` 该项的 `by` 相同 | `{"source": "任务书", "locator": "<任务 id> clarification_answers <澄清编号>"}` |
  | 任务书代答 | `delegate:<代答人>:<日期>`，与 `delegation` 一致 | `{"source": "任务书", "locator": "<任务 id> delegation"}`；代答只能采纳建议（`ADOPTED_PROPOSAL`） |

  后两种都要把派发的 task.json 原样复制为 `record/task.json`。
- 给定和采纳的答复还要写 `requirement_files`：`decision` 为 `UPDATED`（用户确认后已直接改原始需求文件，`files` 列改过的文件，非空）
  或 `KEPT`（用户不让改，只写回需求清单）。暂缓的不写。

`audit_design_closure.py` 核对：

| 代码 | 含义 |
|---|---|
| `clarification_unanswered` | 问题还没有答复 |
| `adopted_text_differs` | 采纳建议，但答复文字与建议条文不一致 |
| `clarification_not_written_back` | 给定或采纳的需求没有以同编号、同文字写进 `requirements`；或答复写了 `merged_into: <需求编号>`（并入已有需求，不再复制一条同编号需求），而那条需求的 `clarifications` 没列它、文字不含答复（或 `merged_quote` 引的那段，答复里的数都要在其中） |
| `deferred_without_requirement_item` | 暂缓的问题没有对应的未关闭 `requirement` 待办 |
| `deferred_requirement_claimed_supported` | 暂缓涉及的需求写成了有设计依据 |
| `requirement_without_clarification` | 未关闭的 `requirement` 待办没有指向一个暂缓的澄清（不再“随交付一起问”） |
| `assumption_differs_from_proposal` | 暂缓待办的 `assumption` 与建议条文不一致 |
| `requirement_files_not_asked` | 给定或采纳的答复没有记下用户是否让改原始需求文件（`requirement_files` 缺失或 `decision` 不是 `UPDATED`/`KEPT`） |
| `requirement_files_without_files` | 记为已改原始需求文件，但 `files` 是空的 |
| `decision_self_assigned` | `by` 或 `source` 是运行者自拟的（含 eval-run、auto、无用户、运行者、预先授权、代填），不是用户的答复（整板评测 2026-11-07） |
| `delegate_without_task` | `source` 写任务书或 `by` 写 `delegate:`，交付目录 `record/task.json`（派发的任务书原样复制）没有这项 `clarification_answers` 或没有 `delegation` |
| `delegate_mismatch` | 答复与任务书 `clarification_answers` 该项不一致（`decision`、`text`、`by`、`date`）；或代答人、日期与 `delegation` 不一致、`scope` 不含 `clarification`、答复不是采纳建议 |

## 报告

报告单列“需求澄清记录”一节，逐项写需求原文、问题、建议条文、答复（用户给定/采纳建议/用户暂缓）、答复人与日期、涉及的需求，
以及原始需求文件改了没有（改了哪些文件，或用户不让改）。
定下的需求已经按它设计，结论在各计算和需求里；暂缓的需求列在“未关闭项”最前面，依赖它的计算列在“依赖暂缓的需求的计算”。
