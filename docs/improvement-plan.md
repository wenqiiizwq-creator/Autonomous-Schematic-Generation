# ASG 持续改进计划

日期：2026-10-19。依据：ASG main 5c0dff6，schematic-review（SR）main 41f4ad3，
100W PD R1–R4 的交付与 17 份审查记录，HardwareWiki 知识库现状。
目标：把"每次审查后靠人看报告再想改什么"变成固定动作，让技能在画不同类型板子的过程中自己积累。

计划遵守已接受的七条规则：
(1) 每次设计必交"学到的东西"；(2) 技能只因事件而改；(3) 问题先归因再修；(4) 能脚本判定的不写成文字；
(5) 知识有来源、范围、过期条件；(6) 每处改动附复现该事件的合成测试；(7) 设计方与审查方分离、各自进步。

## 总览

| 阶段 | 内容 | 对应规则 | 规模 | 依赖 |
|---|---|---|---|---|
| 0 | 回归骨架（2026-10-23 撤销，改为每处改动附合成测试） | 6 | — | — |
| 1 | 回流通道：`lessons.json`、意见归因、台账格式门禁 | 1 2 3 | 中，1–2 个会话 | 无 |
| 2 | 资料入库门禁：读过的手册必须进知识库 | 5 | 小，1 个会话 | 无 |
| 3 | 选型决定性条件结构化，脚本判定候选是否满足 | 4 5 | 中，1 个会话 | 无 |
| 4 | 功能电路模式库：按功能归类做法、适用范围、已知坑 | 5 | 大，持续 | 1（坑来自归因） |
| 5 | 审查方对接：SR 读选型与教训记录，SR 自己的台账与回归 | 7 | 中，在 SR 仓库做 | 1 3 |
| 6 | 运行节奏：每块板子后的固定动作清单 | 全部 | 小，文档 | 0 1 |

建议顺序：0 → 1 → 2 → 3 → 6 → 4（随后每块板子持续）→ 5。
1 先做，因为后面每一步的改动都需要事件来源。

## 阶段 0：回归骨架（已撤销）

2026-10-23 撤销（`user:2026-10-23`）。回归集只登记了同一块板的 R1–R4，ASG 用于通用电路设计，
除非登记一个很大的板子集合，否则保护不了跨类型的改动。删除 `run_regression.py` 和 `tests/regression/`，
改为每处改动附一个复现该事件的合成测试，全部测试通过后才提交。

## 阶段 1：回流通道

现状：审查意见进来后由人判断改什么，没有固定通道；设计结束时没有"学到什么"的输出；
台账是自由文本，没有事件来源字段。

做什么：
1. **`record/lessons.json` 成为交付必需文件**（规则 1）。历史格式（保留示例，仅历史回放；新交付 schema 2 见下）：
   ```json
   {"schema_version": 1, "events": [
     {"source": "review:SR-20261019-R4-修改后复审-41f4ad3/W-07",
      "cause": "knowledge_missing",
      "change": "references/part-roles.md: 栅极驱动器 行补 SR 最小导通时间",
      "verified_by": "tests/test_find_parts.py::test_roles_table_covers_library_subcategories"},
     {"source": "datasheet:raw/Datasheet/08_电源管理/USB PD 控制器/Richtek - RT7209.pdf#p12",
      "cause": "none", "why_none": "手册 p12 的 CC 去耦要求与 part-roles.md 现有行一致"}]}
   ```
   `source` 只能是 `review:<审查目录>/<待办编号>`、`datasheet:<库内路径>#p<页>`、`test:<记录>`、`user:<日期>`；
   `cause` 只能是五类：`rule_missing`、`rule_not_enforced`、`knowledge_missing`、`knowledge_wrong`、`judgment`，或 `none`。
   `change` 必须指向技能或知识库里的具体文件和位置；`none` 必须带 `why_none` 并引用来源页码。
   `render_design_report.py` 检查格式，泛泛的总结句（无文件、无页码）算记录问题。
2. **审查意见必须归因**（规则 3）。`review-responses.json` 每条加 `cause`（同上五类），
   `check_responses` 要求：`rule_*` 的意见必须在 `lessons.json` 里有对应 `change` 指向 `scripts/`，
   `knowledge_*` 的指向 `references/` 或知识库，`judgment` 的写明为什么规则和知识都无法拦住。
3. **台账格式门禁**（规则 2）。`docs/improvement-ledger.md` 每条目固定三段：事件来源（审查编号与待办编号，或手册页码）、
   归因类别统计、改动文件清单。`scripts/check_ledger.py` 校验最新条目，纳入测试；没有事件来源的条目不通过。
4. SKILL.md 第 8 步加"写 lessons.json"，review-comments.md 加归因步骤。

完成标准：R4 补写 `lessons.json`（从 23 条审查意见归因）能通过检查；本计划以后的每次技能改动，台账条目都能被 `check_ledger.py` 接受。

## 阶段 2：资料入库门禁

现状：SKILL.md 有资料规则，但没有检查"本次读过的手册是否都进了知识库"；R4 的 130 份原厂资料与库的对应关系不明。

做什么：
- `pack_design.py` 对 `--input datasheets=` 目录里的每个 PDF，按 SHA-256 或 `Vendor - PartNumber` 文件名在
  `HardwareWiki/raw/Datasheet` 查找；找不到的列入 `manifest.json` 的 `not_in_library`，数量大于 0 时报告写明并算记录问题。
- `find_parts.py --file <pdf>` 给出该文件在库内的位置或"不在库内"，供入库时用。

完成标准：R4 打包时列出不在库内的手册；补入库后清零。

## 阶段 3：选型决定性条件结构化

现状：`selection.json` 的 `decisive` 是自由文本，脚本只查有没有写，不查候选是否真的满足。

做什么：
- `decisive` 改为对象：`{"param": "输入电压范围", "op": "covers", "limit": [90, 264], "unit": "VAC", "requirement": "R-IN-01"}`；
  运算符限 `<=`、`>=`、`covers`、`equals`、`has`（功能/协议有无）。
- 每个候选加 `values`：`{"输入电压范围": {"value": [85, 265], "page": 3}}`。
- `check_selection` 逐条判定：selected 候选每条决定性条件都满足且有页码；rejected 候选至少一条不满足（或理由为依赖/资料/可得性类）。
  判定不满足却被选中算记录问题。
- 报告的选型表加"不满足的条件"列。

完成标准：R4 的 `selection.json` 改成结构化后 11 个角色全部通过判定；故意改坏一条限值能被拦住。

## 阶段 4：功能电路模式库（持续）

现状：`part-roles.md` 回答"这类器件干什么"，没有东西回答"这个功能通常怎么实现、有几种做法、各自的坑"。
HardwareWiki 的 `wiki/` 有 7000 多条概念和发现，但按来源聚类，不按功能组织，ASG 不读它。

做什么：
- 模式放知识库 `HardwareWiki/wiki/patterns/<功能>.md`（库外，其它技能共用），技能内只放格式和检索规则
  （`references/circuit-patterns.md`，`find_parts.py --patterns <功能>`）。
- 每个模式文件固定结构：功能；做法列表，每种做法写适用范围（功率、电压、频率、隔离等级）、核心器件类
  （指向 part-roles.md 的二级类）、必需外围、必算项（指向 calculation-preflight 的计算类型）、已知坑（每条引用审查待办编号或手册页码）、
  来源（参考设计板名或手册）。没有来源的做法不写。
- 第一批从 100W PD 提取 10 个左右：输入整流与浪涌、PFC 升压、QR 反激、同步整流、隔离反馈、PD 输出控制与 VBUS 开关、
  偏置电源、高压启动、X 电容泄放、输出过压保护。
- SKILL.md 第 1 步：`page-plan.json` 每个功能块标注所用模式与做法；没有适用文件的功能块要在 `lessons.json.library_gaps` 逐块登记覆盖待办，
  设计完成后补写模式。覆盖待办不作为问题事件；真实知识缺陷另按证据归因。

完成标准：第一批模式写完并有来源；R4 的 8 页功能块全部能指向模式；之后每版核对覆盖待办，有可复用内容才新增或修订，不按篇数补库。

## 阶段 5：审查方对接（SR 仓库）

现状：SR 不读 `selection.json`，审查选型时从头判断；SR 自己没有台账和回归；两边的交接只靠报告里的"待办 W-…"。

做什么：
- SR 增加选型审查项：读 `selection.json`，对每个角色独立给出"是否同意选定、若不同意选谁、依据页码"；
  不同意时必须给出 ASG 候选之外的型号或 ASG 淘汰理由中的错误。读 `lessons.json`，核对 `cause` 归因是否成立。
- SR 增加 `docs/improvement-ledger.md` 与同格式门禁；SR 的回归集用同一批交付，指标是漏报（后续版本或实物发现而本轮没报）与误报（ASG 以证据驳回）。
- `references/workflow-handoff.md`（SR）与 `review-comments.md`（ASG）同步更新：意见编号、归因、教训文件的传递方式。

完成标准：SR 对 R4 的选型记录出具独立结论；两边台账格式一致。

## 阶段 6：运行节奏

每块板子的固定动作，写成 `docs/operating-cadence.md`，作为 SKILL.md 之外的操作清单：

1. ASG 交付（含 `selection.json`、`lessons.json`）。
2. SR 独立审查。
3. ASG 逐条归因（阶段 1），改技能或知识库，台账条目带事件来源。
4. 每处改动附复现该事件的合成测试，跑全部测试。
5. 全部测试通过后提交，带台账条目。
6. 实物或测试结果回来后，按 `test:` 来源再走一遍 3–5。

## 怎么知道计划有效

2026-10-23 起不再记录效果指标（`user:2026-10-23`）。复发的意见在 `review-responses.json` 里用 `recurs_from`
标出上一次的编号，标了复发的意见不能归因为 `judgment`。

## 不做的事

- 不给已有的 R1–R4 记录做格式兼容；新格式只对新交付生效，旧记录作历史。
- 不把知识库的 7000 条 wiki 条目批量转成模式；模式只从真实设计和审查中产生。
- 不在本计划内改 SR 的结论记录结构，那是 `SR架构简化规划-20261019.md` 的范围。

## 2026-11-05：覆盖待办与事件分离

新交付采用 lessons schema 2：library_gaps 单独记录资料覆盖待办，分页后绑定 page/block；有效待办非空时 events 可以为空，两者皆空仍写 none 核对记录。不按篇数补库，仅有缺文件不能统计成 knowledge_missing。真实知识缺陷分 observed（完整后果和证据）与 uncertain（不确定原因和待核内容）；历史归因单列未复核，不能混计。保留旧 schema 1/缺版本的历史校验与回放，不自动迁移；未知版本报错。入口尚无受控历史身份判定，未强制所有新交付的版本；迁移工具留待单独设计。完整字段与例子见 [交付与设计报告](../references/delivery-report.md#lessons-schema-2新交付)。
