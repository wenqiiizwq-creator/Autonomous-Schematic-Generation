# 处理审查意见

收到别人对原理图的审查意见后、改图之前读本页。意见可以是任何形式：文字、表格、批注、
另一个工具输出的报告。ASG 不依赖意见的文件格式，只要求能逐条定位（第几条、哪一行、哪一节）。

## 1. 逐条登记

每条意见登记到 `record/review-responses.json`，一条意见一行，不合并、不改写原意：

```json
{
  "schema_version": 1,
  "sources": [
    {"id": "S1", "path": "/abs/path/审查报告.md", "sha256": "<SHA256>", "from": "谁给的、哪一版图"}
  ],
  "items": [
    {"id": "RC1", "source": "S1", "locator": "待办 FW_RELATIVE_OVP", "comment": "意见原文或忠实摘要",
     "response": "DESIGN", "detail": "怎么处理、为什么", "work_items": ["W3"], "changes": [], "evidence": []}
  ]
}
```

`response` 只能取下面一种，报告里显示右边的说法：

| response | 报告里写 | 必须同时给出 |
|---|---|---|
| `REDESIGN` | 改图 | `changes`：改了哪些位号/网络/页（每条点名位号或页名），及复验证据 `evidence`；打包时对照前一版设计网表，点名的位号必须真的变了 |
| `CALC_DOC` | 补计算/补文档 | `changes`：补的计算编号或 `设计资料/` 里的文件名；没有改到电路的不叫改图 |
| `DESIGN` | 补设计（计算、选型、配置） | `work_items`：design 阶段的待办，待办里写 `progress`（本版算到哪、定了什么），报告在待办下列出 |
| `OBTAIN_DATA` | 补资料 | `work_items`：external 阶段的待办（含替代方案评估） |
| `ASK_USER` | 请用户定需求 | `clarifications`：当场问用户的需求澄清编号（在 `design-closure.json` 里，见 [需求澄清](requirement-clarifications.md)）；问完按答复改图或补算 |
| `HANDOFF` | 交给后续环节 | `work_items`：validation 或 pcb 阶段、状态 handoff 的待办 |
| `DECLINE` | 不采纳 | `detail` 写理由，`evidence` 给依据（计算、手册页） |
| `DEFERRED` | 已暂缓 | `detail` 写谁、何时决定暂缓 |

- 意见里说“缺资料”“证据不足”时，先在已有资料里读算；能回答的直接给出结论（`DECLINE` 并附依据，
  或 `REDESIGN`），不要原样变成待办。意见写着“已读某页，再按 … 复算”的，是审查方没算完的计算，
  按 `DESIGN` 自己算完给结论；标准规定的量（预期短路电流、海拔系数）按条款取值后 `DECLINE` 或 `REDESIGN`。
- 意见要固件镜像、读回、量产校准结果的：配置表按 `DESIGN` 定型，镜像验证按 `HANDOFF` 交固件/生产；
  意见只要“厂家保证寿命末期参数”这类不会有人给的数据，用声明的折减系数计算后 `DECLINE` 并附依据。
- 同一方法套在几个对象上的几条意见（几路光耦 CTR、几只电解寿命）合并成一个 design 待办、列全位号。
- 意见只要求实物测试结果（能效、EMC、闭壳热、寿命、实际寄生）时用 `HANDOFF`，写清验证方法，不改图。
- 意见指出的是审查工具自身的限制时，用 `DECLINE` 并说明设计本身已有的依据。
- `detail` 写这一条意见本版做了什么；同一句话用在两条以上意见会被报告拒绝。
  “本次未宣称关闭，保留原任务”不是处理，是没处理。
- 每条意见还要**归因**（`cause`）：这条意见为什么没有被技能自己拦住。只能取下面一种：

  | cause | 含义 | 必须随之发生的事 |
  |---|---|---|
  | `rule_missing` | 没有规则或自动检查覆盖这件事 | 在 `scripts/` 加检查，`lessons.json` 写明文件 |
  | `rule_not_enforced` | 规则有，但没有脚本强制，被跳过了 | 把规则做成自动检查，`lessons.json` 写明文件 |
  | `knowledge_missing` | 设计当时缺少可复用知识并有具体问题证据（schema 2 区分 observed/uncertain） | 补 `references/` 或知识库，`lessons.json` 写明文件和行 |
  | `knowledge_wrong` | 有这条知识但是错的 | 改正并记来源，`lessons.json` 写明文件和行 |
  | `judgment` | 规则和知识都在，判断还是错了 | `lessons.json` 写 `why_not_rule`：为什么规则和知识拦不住 |
  | `none` | 意见不反映技能缺口（需求取舍、审查方自身限制） | 无 |

  `cause` 不是 `none` 时，`record/lessons.json` 里必须有 `source` 为 `review:<审查目录>/<意见编号>` 的事件，归因一致，
  `change` 指向对应目录下的具体文件；报告会核对。归因先于修改：归因错了，修的就是错的地方。
  归因与本版改不改无关：暂缓（`DEFERRED`）的意见同样要归因，`why_none` 写“下一轮再归因”会被报告拒绝。

  上一轮审查提过的同一问题再次出现时，该条写 `recurs_from: "review:<上一轮审查目录>/<意见编号>"`。标了复发的意见
  不能归因为 `judgment`：上一轮没有拦住，说明缺规则、规则没执行或知识有缺口。报告在处理说明后注明“复发自 …”。

### 审查方对选型与归因的复核

SR 按其 `references/selection-review.md` 独立复核 `selection.json` 和上一轮的归因，结果以待办编号回到报告里：

- 角色 `DISAGREE` 并给出候选之外的型号：按 `DESIGN` 登记，把该型号加进候选、按决定性条件判定后再定；改了选定型号的记 `REDESIGN`。
- `DISAGREE` 指出淘汰理由有误：改 `selection.json` 里该候选的 `values`/`reason`，`cause` 多为 `knowledge_wrong`。
- `conditions_complete: false`：缺的决定性条件补进 `references/core-part-selection.md` 或 `part-roles.md`，有具体问题证据时 `cause` 为 `knowledge_missing`，按 observed/uncertain 登记；仅缺文件的另记 library_gaps。
- 归因不同意：改 `lessons.json` 与 `review-responses.json` 的 `cause`，按新的归因改对应文件；复发的意见按上面的 `recurs_from` 处理，不能归 `judgment`。

## 2. 意见附带的改法

审查意见可能附带建议的电路改法。它是候选方案，不是改图指令：

1. 意见指出的是已确认的电路错误，或建议方明确说资料拿不到：按建议改，或给出更好的改法。
2. 其余情况先尝试补资料或补计算；补不出来再改图。
3. 不论哪种，改图前都在设计记录里写明这项改动预计解决哪些意见、新增哪些器件和新的待办，
   见 [设计待办记录](design-closure.md#从审查缺口回到电路)；是否采用按设计判断，并写明理由。

“不用加电路去补资料缺口”仍然成立：只有计算证明现电路确实不满足，才构成改图理由。

## 3. 登记的核对

`render_design_report.py` 会检查这份登记：每条意见必须有处理方式和对应的必填内容，
引用的待办必须存在于 `design-closure.json`，阶段也要对得上；`detail` 不能重复；`DESIGN` 引用的未关闭待办要有 `progress`；
`REDESIGN` 的 `changes` 要点名位号或页；`CALC_DOC` 的 `changes` 要是计算编号或设计资料文件。
`sources` 的 `path` 读得到时核对 `sha256`，不一致算记录问题；读不到时报告写明“来源未核对”。
报告在摘要后会写明本版多少条意见真正改了图或补了计算、多少条只是登记。

schema 2 中，`knowledge_missing` 只记录缺少可复用途径、判据或已知坑而导致具体问题的事件，写 knowledge_kind、problem 和 impact。有证据后果（observed）写 consequence 和 evidence；疑似归因（uncertain）写 uncertainty 和 pending，单列待核、不计已证实知识缺陷。规则当时已有且适用但未落实的按 rule_not_enforced 复核；只缺典型电路文件的登记 library_gaps，不能满足审查意见必须有对应 events 的要求。来源可定位不证明因果成立。旧版保持历史语义，标注尚未按新口径复核。字段与引用定位见 [交付与设计报告](delivery-report.md#lessons-schema-2新交付)。
