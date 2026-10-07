# ASG/SR 工作流交接合同 v1

本合同只封装技能之间的交接，不替代技能内部的电气判据。独立使用 ASG/SR 不要求安装控制器。
参与薄控制器流程时读本页；`contract.py` 校验封装，`adapters.py` 调用现有技能校验器。

## 输入：task.json

控制器生成任务，不由工作者修改：

| 字段 | 含义 |
|---|---|
| `schema_version: 1`、`id`、`project_id` | 合同版本、唯一任务、项目身份 |
| `skill` | `ASG` 或 `SR` |
| `design_version` | 当前用户可读版本；每次候选另由任务 ID 唯一标识 |
| `phase` | 默认 `design_iteration`；明确申请冻结后为 `schematic_freeze` |
| `requirements` | 已持久化的需求版本、目录、逐文件 SHA256 和清单 digest |
| `skills` | ASG/SR 路径、工程规则身份和接口兼容信息；由程序管理 |
| `design` | 当前/前版设计包的目录、文件哈希、角色、收据和自检记录；首轮可为 null |
| `previous_review` | 前次 SR 完整包，首审可为 null；不得把前次 PASS 直接迁移 |
| `open_items` | 前轮尚待处理的问题；详细电气判据仍以 SR 原生记录为准 |
| `output` | 本任务最终 result.json 的绝对路径 |

需求文档保留原文与未决项。ASG 独立构建设计意图；SR 独立构建审查意图、覆盖计划和结论。
`electrical-intent.json` 与 SR `intent.json` 不能互相改名替代，也不从图中回抄意图来证明正确。
SR 的 `review_sources` 必须列出 task.requirements 中全部受控文件的绝对路径与定位说明，使最终
`review_inputs.documents` 绑定同一需求基线。器件资料、计算等可读来源需收入交接包或引用已有受控包。

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

路径相对于 result.json 的父目录；禁止绝对路径、`..`、符号链接和重复路径别名。
角色引用的每个文件都必须在 files 清单中；ASG 工程的全部有效图页、配置、符号、原生导出及
delivery-evidence.json 引用的文件均须完整打包，保持相对目录结构。

日常调用 `pack-result --roles roles.json --open-items open-items.json` 自动生成文件清单和任务绑定；
roles.json 只填写角色到相对路径的映射，open-items.json 只填写问题。无开放项时可省略 --open-items。
无需手动命名候选版本、计算或复制 SHA256。封装仍保持 v1，以兼容已生成的任务和结果。

`DELIVERED` 只表示工作完成并形成可验证交接包，不表示电路通过。
需要需求/资料/方案输入时用 `NEEDS_INPUT`；工具未完成执行用 `TOOL_FAILED`。后两者允许
files/roles 为空，但必须至少给一个开放项；不得用伪造文件补齐角色。

每个开放项为 `{id, kind, summary, next_action}`，均为非空字符串，ID 不重复。
kind 取 `REQUIREMENT / EVIDENCE / DESIGN / REVIEW / TOOL / DOWNSTREAM`。
ASG 自检或目检未通过/未完成时必须保留开放项。SR 封装必须包含原生 workflow.current_work_items
中每个任务的 ID，原生记录中的关闭条件、阶段和证据不能被封装覆盖。

## ASG → SR 必需角色

| 角色 | 内容 |
|---|---|
| `schematic` | 唯一根 .kicad_sch；其他有效图页也收入 files |
| `netlist`、`render`、`bom` | 唯一原生 XML 网表、项目 PDF、BOM |
| `electrical_intent` | ASG 板级电气意图 |
| `requirements` | 全部需求基线文件，字节哈希与 task 完全一致；可多个 |
| `requirement_trace` | 需求到模块/图页的追溯表 |
| `device_contracts` | 确切 MPN、引脚和外围合同及适用资料 |
| `calculations` | 计算/适用仿真及条件；无需计算时保存有依据的不适用说明 |
| `open_items` | 设计内部 OPEN 台账，不用封装的短摘要替代 |
| `native_summary` | 现有 verify_schematic.py 的 summary.json，保留原始状态和 gates |
| `visual_review` | JSON；status 为 REVIEWED / REVIEW_PENDING / REWORK_REQUIRED，并保留实际逐页路径记录 |
| `delivery_evidence` | 现有 delivery-evidence.json，所有引用文件均在包内 |
| `downstream_constraints` | PCB/结构/固件等交接约束 |

除 requirements 外，每个上述角色恰好指向一个文件，可用索引文件组织多份器件/计算证据。
控制器重跑 ASG 新鲜度检查，拒绝遗漏有效图页和证据引用。自检缺口原样交给 SR；FRESH 不是电气通过。
改版还应收入 change contract、preflight、基线和复验记录，可使用附加角色。

## SR → ASG/控制器必需角色

每个角色指向一个文件：`review_intent`、`db`、`review_plan`、`review_results`、`review_gate`、
`lint_cold`、`lint_hot`、`report`。器件证据、计算、裁图等引用材料也收入 files。
原生格式继续使用 SR 当前的 intent、plan、results schema，不另造简化审查格式。

控制器执行以下校验：

1. SR intent 等于最终 plan 的 review_inputs.intent，审查阶段与 task.phase 一致。
2. 用当前 SR parse_kicad.py 重新解析 ASG 交付的 XML；db 必须与解析结果完整一致。
3. 重跑 validate_review.py，带 `--db`、冷/热 lint、`--require-actionable`、`--require-bindings`。
4. review_mode=revision 时必须包含 old_db/old_plan 角色，绑定 task.previous_review 的对应文件，
   并使用 `--require-revision-impact`。规则变更后可进行完整 first 审查，不能盲复用历史结论。
5. supplied review_gate 必须与重跑结果一致，且 valid=true。NO_GO 的有效报告仍可交付，用于整改。
6. schematic_freeze 再加 `--require-release`；GO/CONDITIONAL_GO 才进入 READY_FOR_FREEZE。
   风险接受与下游接收只能来自 SR 要求的真实责任记录，控制器不代填。

先在临时目录输出原生 gate，再写入最终交接包。临时文件统一在 `/tmp/codex-work/<任务>/`。
最终输入、结果和证据保存在项目中。所有引用资料的版本/适用性仍由技能判断。

## 接收、恢复与变更

`check-result` 只校验；`complete` 校验后复制成持久化快照，并以 SQLite 事务记录状态和事件。
同一任务重复接收相同结果是幂等操作；不同结果、过期任务或被篡改的文件会被拒绝。
发布中断后可用相同结果再次 complete；已写入相同哈希的文件可复用，冲突文件不能覆盖。

next 重复调用返回同一未完成任务。resume 默认只恢复状态并提示下一步，不自动再次启动工作者。
run 接受显式 worker 命令，追加 task.json 和 result.json 两个位置参数，不经 shell；已启动的任务
需要检查记录的进程退出后才能 `resume --retry`。工作者应检查已有最终结果，避免重复外部副作用。

## 简化的版本与校验策略

日常出图、排版和整改使用任务 ID 标识候选，继续当前版本；只有需求基线变化、重要电气改版或冻结
才记录里程碑。init 默认 v1；revise 的 --version 可省略并自动生成。冻结记录绑定准确候选与 SR 结果。

status 默认显示进度、问题和当前任务，不扫描文件，也不显示 hash；integrity=NOT_CHECKED 明确表示
未做内容核验。需要核对当前依赖时用 status --check；需要内部记录时用 --details。
进入 SR、接收结果和冻结时继续严格校验当前设计、需求、证据和本次引用的旧基线。
resume 仅恢复任务状态；下次实际交接仍需校验。不能把轻量状态查询当成通过证明。

无关历史文件不参与日常门禁。audit --history 显式检查历史，记录 STALE_OR_INVALID 和原因；
不改变工作队列。若旧文件被当前任务作为基线/复验证据引用，则其完整性仍必须成立。

工程规则身份（v2）覆盖算法语法树、规范判据与未知规则文件；测试、缓存、README、接口页和入口
元数据不触发电气重审。Python 注释/docstring/排版变化忽略；常量、逻辑和规范判据变化触发重新验证。
未知 references 默认仍作为规则，不能自动推断任意自然语言改写都没有工程影响。说明内容宜放 README、
接口页和元数据；判据与执行纪律放受控正文/规范 references。保持算法、阈值、输入版本和审查证据约束。

refresh-skills 区分接口兼容更新与规则更新：前者保留任务、已有结论与冻结状态，由封装/原生接口校验
确认兼容；后者重新打开对应设计/审查。新算法不会自动接受旧 PASS。旧 v1 全字节规则身份无法可靠
推断哪些变化只属说明，首次转换需 refresh-skills 建立 v2 基线并完成相应重新验证，此后采用上述分级。
