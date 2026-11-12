# 术语对照

报告、记录（`design-closure.json` 等）和 `notes.json` 用同一套术语，没有另一层口语说明。
第一张表“不用的词”一列由 `render_design_report.py` 读取：记录或 notes 的文字里出现这些词算记录问题，打包被拒。
“技能文档用词”一张管 SKILL.md 和 references 本身的叫法，由 `tests/test_terminology.py` 检查。

## 术语

| 用词 | 含义 | 不用的词 |
|---|---|---|
| 自动检查 | `verify_schematic.py` 一次运行里由脚本和 KiCad 完成的检查项：ERC、网表逐脚对照、层次、符号、可读性、几何等 | 门禁 |
| 图面审阅 | 按本版 PDF 逐页审阅读图路径和全部图面待审对象，写出看到了什么 | 看图检查 |
| 完成、关闭 | 设计完成：需求、计算和待办都已处理；关闭：一条待办有证据地处理完 | 设计闭环 |
| 设计定型 | 设计完成且独立审查通过，可以交后续环节实施；对应 schematic-review 的冻结准出（`schematic_freeze`） | 定稿 |
| 技术转交 | 状态为 `handoff` 的要求，交 PCB、结构、样机验证等后续环节落实 | 交接、移交 |
| KiCad 导出 | KiCad 自己导出的网表、ERC 报告和 PDF | 原生 |
| 外围电路核对表 | `reference-input.json`：核心器件引脚与手册的对照和外围电路检查（USB PD 协议的“合同”是协议术语，照用） | 契约 |
| 待办 | `design-closure.json` 的 `work_items` 中的一条，任何状态 | |
| 未关闭项 | 状态为 `open` 的待办（`handoff` 计入技术转交，不算未关闭项） | |
| 独立审查 | 由 schematic-review 技能或其他审查方做的审查；ASG 只做自检 | |
| 设计成立、依赖工程估计、依赖厂家资料 | 计算结论的三档，由参数和门槛的依据推出（`parameter_version: 2`/`3`），见 [design-closure.md](design-closure.md) | |
| 后果等级 | 由 `consequence_class` 和 `occurrence` 按规则推出的 P0–P3，见 [design-closure.md](design-closure.md) | |
| 引用待人工核对 | 所引手册页的文字里没找到的数值，需对照原页确认 | |
| 白话说明 | 不再使用：notes 与记录按本表同一套术语写 | 白话 |

## 技能文档用词

SKILL.md 和 references 写同一概念只用一个词。“不用的词”一列出现在这些文档里算测试失败；文件名、JSON 字段名、脚本名和
`docs/` 下的历史记录不改。

| 用词 | 指什么 | 不用的词 |
|---|---|---|
| 关键器件、特殊器件、常规件 | [part-roles.md](part-roles.md) 第 1 节的三级器件分级（与 schematic-review 对齐）；“核心器件”另指要做选型比较的器件角色，属于关键器件 | 料号件、规格件 |
| 设计网表 | `electrical-intent.json`：从需求和数据手册独立写出的器件、网络与 NC；与 KiCad 导出的“导出网表”`netlist.xml` 对照 | 设计要求表 |
| 自动检查、检查项 | `verify_schematic.py` 一次运行叫自动检查，其中每一项（ERC、网表、几何……）叫检查项 | 一键验证、一键自动检查 |
| 图面待审对象 | `geometry.render_review_items` 列出、留给图面审阅逐条处置的对象；引脚文字按库符号列，每种一条 | 待看图 |
| 分页方案 | `page-plan.json`：每页的读者任务、功能块与典型电路 | 页面方案、方案表 |
| 图页脚本 | 生成一页原理图的 .py 脚本 | 页面脚本 |
| 引脚号、引脚名、引脚类型 | 符号或封装上的引脚编号、名称和电气类型；封装上的编号叫物理引脚号 | 脚号、脚名、脚型 |
| 网络名 | 网络的名字 | 网名 |
| 回流路径、地网络、地域 | 电流返回的路径；PGND/SGND 这类网络叫地网络；彼此隔离的各组地叫地域。控制上的 loop 叫环路；“回路”只留在回路电感这类固定说法里 | 返回路径、回路域 |
| 交付目录 | 设计报告、原理图、设计资料、record 四样组成的目录 | 四件套 |
| 数据手册、原厂资料 | 器件的 datasheet 叫数据手册（简称手册）；手册、应用笔记和参考设计合称原厂资料 | 器件资料 |
| 外围电路要求 | 外围电路核对表 `reference-input.json` 里逐项核对的内容 | 外围契约 |
| 共用规范 | 硬件设计规范发布的 G01–G10：G01–G09 拆成设计准则（登记在设计准则库），G10 是降额与应力规范（`references/shared/derating-rules.md`、`stress-spec.md`、`commodity-floors.json`，规则编号自成一套，不进准则登记） | |
| 设计准则、设计准则库 | 共用规范 G01–G09 拆成的单条可核对要求（`G0x-nnn`，含 `asg_action`/`sr_check`），全部准则的汇编叫设计准则库（`references/shared/guideline-criteria.json`，2026-11-02 由“规范规则/规则库”改名） | 规范规则、规则卡、规则库 |
| 典型电路、实现方案 | 一个功能通常怎么搭叫典型电路（知识包 `references/knowledge/典型电路/`），同一典型电路的几种搭法各叫一个实现方案；分页方案按 `典型电路#实现方案` 标注 | 电路模式、模式库 |
| 知识包 | 从硬件设计知识框架同步、装在 `references/knowledge/` 的一份知识（依据的框架版本见 `knowledge-sync.json`）：需求要素、板级架构模式、接口约定、典型电路、计算方法、器件参数、失效与故障分析；“知识库”仍指原厂资料所在的 `~/Documents/知识库/HardwareWiki` | 典型电路库 |

## 报告固定用语

| 用语 | 对应字段 |
|---|---|
| 责任方 | `owner` |
| 处理措施 | `action`（缺外部资料的待办写作“关闭方式”） |
| 外部依赖原因 | `why_external` |
| 失效后果 | `consequence` |
| 替代方案 | `fallback` |
| 前置项 | `blocked_by` |
| 关联需求 | `requirements` |
| 设计假设 | `assumption` |
| 本版进展 | `progress` |

## 计数

记录与 notes 里写总数时用“共”或“全部”，并与记录一致，否则算记录问题：

| 写法 | 核对对象 |
|---|---|
| 共 N 项计算 | `design-closure.json` 的 `calculations` 条数 |
| 共 N 件未关闭项 | 状态为 `open` 的待办数 |
| 共 N 条需求 | `requirements` 条数 |
| 共 N 个器件 | 设计网表的 `components` 个数 |
| 共 N 页 | 图纸页数（`summary.json` 的 `sheets`） |

不带“共/全部”的数字是部分计数（“其中 3 条需求有条件成立”），不核对。
