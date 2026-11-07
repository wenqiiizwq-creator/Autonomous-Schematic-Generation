# 运行节奏：每块板子的固定动作

这是 SKILL.md 之外的操作清单，面向运行 ASG 和 SR 的人；每块板子的每一版都按这个顺序走，
不跳步。目的只有一个：让审查和测试发现的每个问题都变成技能或知识库里的一行，并且有一个合成测试复现它。

## 原则

1. 每次设计必交“学到的东西”（`lessons.json`）；2. 技能只因有来源的事件而改；3. 问题先归因再修；4. 能脚本判定的不写成文字；
5. 知识有来源、范围和过期条件；6. 每处改动附复现该事件的合成测试，全部通过后才提交；7. 设计方与审查方分离、各自进步。
复发的意见在 `review-responses.json` 里用 `recurs_from` 标出上一次的编号，标了复发的意见不能归因为 `judgment`。

不做的事：不给旧交付记录做格式兼容迁移，新格式只对新交付生效；不把知识库条目批量转成典型电路，典型电路只从真实设计和审查中产生。

## 一版的六步

| 步 | 谁 | 做什么 | 产物 | 自动检查 |
|---|---|---|---|---|
| 1 | ASG | 按 SKILL.md 设计并交付 | 交付目录（含 `record/selection.json`、`record/lessons.json`） | `pack_design.py` PASS |
| 2 | SR | 独立审查（首版交付后用 SR 审一次本板），不看 ASG 的结论先看需求和手册 | 审查报告与待办编号 | SR 自己的自动检查 |
| 3 | ASG | 逐条登记并归因：`review-responses.json` 每条 `cause`，`lessons.json` 对应事件 | 更新后的记录 | `render_design_report.py` 无归因问题 |
| 4 | 维护者 | 按归因改技能或知识库：`rule_*` 改 `scripts/`，`knowledge_*` 改 `references/` 或知识库，`judgment` 写明为什么拦不住；每处改动附复现该事件的合成测试 | 代码或知识文件改动与测试 | 全部测试通过 |
| 5 | 维护者 | 台账条目（Event/Changed 两行，Causes 可选）并提交 | git 提交 | `scripts/check_ledger.py` PASS |
| 6 | 测试/生产 | 实物或测试结果回来后，以 `test:<记录>` 为事件再走 3–5 | 同上 | 同上 |

## 每步的检查点

- **第 1 步**：`lessons.json` 新交付采用 schema 2；有有效 library_gaps 时允许 events 为空，两者均空时写 `cause: none` 并引用核对过的页码。泛泛的总结会被报告拒绝。
  读过的手册存在工程资料目录（打包输入 `datasheets`），设计期间不写入知识库；还不在知识库的由 `pack_design.py` 列进
  `record/manifest.json` 的 `datasheets_to_file`，何时入库由用户定，参考设计入库时放 `raw/Designexample/<拓扑>/<板名>/`。
- **第 3 步**：归因先于修改。同一条意见若上一版已出现过，`cause` 不能再是 `judgment`：上次的改动没拦住，说明归因错了，重新归因。
- **第 4 步**：能用脚本判定的不写成文字；每条新文字规则都要问一次能不能变成自动检查。合成测试只复现事件本身，
  不放第三方或真实交付的原理图。改动会触及 SKILL.md 的「ASG 纲要」或绘图纲要 O1–O8 时，只登记提案，先把草案交给人确认再改；
  台账条目加 `Approved: user:<日期>` 和 `Outline: <check_ledger.py --outline-hash 的输出>`。
- **第 5 步**：没有事件来源的改动不提交。计划内的阶段性改动，事件写 `user:<日期>` 并注明计划阶段。

## 命令

```bash
python3 scripts/deliver.py <交付目录>          # 参数在 <交付目录>/record/deliver.json，一次跑完下面两条及其之前的步骤
python3 scripts/render_design_report.py <交付目录> --notes <交付目录>/record/notes.json --title "<标题>"
python3 scripts/pack_design.py <交付目录> --input requirements=<需求目录> --input datasheets=<资料目录> --input previous=<上一版>
python3 -m unittest discover -s tests
python3 scripts/check_ledger.py
```

关键功能块的资料覆盖待办逐块登记，常规块可不标、不登记，不按篇数补库；有可复用内容才修订典型电路。事件按有证据后果、待核归因、历史未复核分别展示，覆盖待办不计事件数；字段、统计与旧版兼容边界见 [交付与设计报告](../references/delivery-report.md#lessons-schema-2新交付)。旧版入口仍兼容，尚未强制新建身份识别或自动迁移。
