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

### 审查方对选型的复核

审查方对 `selection.json` 提出的意见，以待办编号回到报告里：

- 角色 `DISAGREE` 并给出候选之外的型号：按 `DESIGN` 登记，把该型号加进候选、按决定性条件判定后再定；改了选定型号的记 `REDESIGN`。
- `DISAGREE` 指出淘汰理由有误：改 `selection.json` 里该候选的 `values`/`reason`。
- `conditions_complete: false`：缺的决定性条件按本板补进 `selection.json`，重新判定候选。

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
