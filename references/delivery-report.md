# 交付目录与设计报告

每一版交付都是同一个固定形状的小目录。给人看的只有 `设计报告.md`，其余是原理图本身和可复核的记录。

## 目录

| 位置 | 放什么 | 不放什么 |
|---|---|---|
| `设计报告.md` | `render_design_report.py` 生成 | 手写的 README、说明、HTML |
| `原理图/` | `.kicad_pro`、根图与各页 `.kicad_sch`、项目符号库/封装库及库表、`schematic.pdf`、`netlist.xml`、`BOM.csv` | 草稿图、旧版图 |
| `设计资料/` | 跨版本有效、每版更新的设计文档，名字固定：如 `方案与选型依据.md`、`器件选型与用法依据.md`、`PCB与结构要求.md`、`磁件设计单.md` | 按版本号命名的说明（`v12…`、`v16…`），把仍有效的内容并入固定文档 |
| `record/` | 见下表 | 日志、历史快照、审查方的结果文件 |

`record/` 内容：

| 文件 | 说明 |
|---|---|
| `electrical-intent.json` | 设计网表（每个器件、网络应该怎样） |
| `design-closure.json` | 需求、待办、计算的处理情况；证据路径相对交付目录，所引证据必须在本目录内；需求、原厂资料可留在 `--input` 登记的位置（按文件名找到并核对 SHA-256） |
| `design-closure-audit.json` | `audit_design_closure.py` 的输出（`verify_schematic.py` 输出目录里的 `design-closure.json`，改名放入） |
| `summary.json` | `verify_schematic.py` 的自动检查结果，原样复制 |
| `component-requirements.json` | 新性能流程的唯一源记录：用途筛选、计算得到的性能要求、采购方式、候选核实状态；格式与准备/出图接口见 [器件性能要求](component-requirements.md) |
| `component-requirements-check.json` | 从本次原生图纸、PDF、XML与BOM复核的结果；不与源记录重名，不用历史PASS代替本次核对 |
| `page-plan.json` | 分页方案：`{"schema_version": 1, "pages": [{"file", "reader_tasks": [...], "blocks": {块名: [位号]}, "patterns": {块名: "模式#做法"}}]}`；本页每个器件属于一个功能块，每块标注 `references/circuit-patterns/` 里的做法（第一页架构页免标） |
| `selection.json` | 核心器件选型：每个角色的位号、决定性条件、≥2 个候选（选中/淘汰理由、相对知识库的手册路径）；每个 U/Q/T 器件都要属于一个角色；选定候选写外部依赖，依赖未公开资料时附 2–3 个方案、建议和用户的决定，格式见 [核心器件选型](core-part-selection.md) |
| `lessons.json` | 本版学到的东西：`{"schema_version": 1, "events": [{"source", "cause", "change" 或 "why_none", "why_not_rule"}]}`；来源只能是 `review:<审查目录>/<待办编号>`、`datasheet:<库内路径>#p<页>`、`test:<记录>`、`user:<日期>`；`datasheet:` 来源核对文件和页码；归因与改动位置的要求见 [处理审查意见](review-comments.md) |
| `visual-review.json` | 图面审阅：`{"status": "REVIEWED/REVIEW_PENDING/REWORK_REQUIRED", "pdf_sha256", "pages": [{"page", "file", "paths", "problems", "render_review_items": [{"item", "disposition"}]}]}`；每页 `paths` 不少于读者任务数；`summary.json` 的 `geometry.render_review_items` 列出的每个图面待审对象都要在对应页有非空处置，写出在本版 PDF 上看到了什么；没改动的页面也按本版 PDF 重新看，处置、路径和 `method` 不写“沿用”“同上一版”；`REVIEWED` 时 `pdf_sha256` 必须是本版 `原理图/schematic.pdf` 去掉导出时间后的 SHA-256（`render_design_report.py --pdf-sha256 原理图/schematic.pdf` 给出），PDF 图面变了就要重新审阅 |
| `delivery-evidence.json` | 导出后有没有再改过的核对记录 |
| `review-responses.json` | 收到审查意见时必有，格式见 [处理审查意见](review-comments.md) |
| `design-change.json` 等 | 改版时的改动核对与动手前检查 |
| `calculations/` | 本版设计还在依赖的计算（不管是哪一版算的），作废的不带 |
| `scripts/` | 图页脚本，下一版只重生成有变化的页面 |
| `evidence/` | 设计结论引用的截图、手册摘页等 |
| `manifest.json` | `pack_design.py` 写：需求、原厂资料、前一版设计的路径和 SHA-256，本目录每个文件的 SHA-256 |

单个文件超过 10 MB 说明带了不该带的东西：仿真原始波形、整份手册、历史台账。只留结论引用的部分，
其余留在工作目录，或用 `--input` 按路径登记。

## 设计报告

`render_design_report.py <交付目录> [--notes notes.json] [--title 标题]` 从 `record/` 生成，顺序固定：

1. **结论**：器件数、页数；图纸自动检查各项结果的数量；图面审阅；需求状态；收到的审查意见及处理方式的数量；
   设计是否完成，没完成时逐条列出还差什么；有用户暂缓的需求时单列一行点名；有缺外部资料的待办时单列一行，
   按负责方计数并给出受影响的有条件计算数；有外部条件不确定的选型时单列一行，点名角色和你选的方案。
2. **这版改了什么**：器件数变化，加上 notes 的 `changes`。
   **需求澄清记录**：问过用户的每个需求问题：需求原文、问题、建议条文、答复（用户给定/采纳建议/用户暂缓）、答复人与日期、涉及的需求；有未答复的问题算记录问题（打包被拒），见 [需求澄清](requirement-clarifications.md)。
3. **审查意见怎么处理的**：逐条列出意见、处理方式、说明。
4. **待办**：`design-closure.json` 里未关闭的待办。用户暂缓的需求（`requirement`）的排最前，其余按由 `consequence_class` 和 `occurrence` 推出的等级
   从重到轻排；写明类型、本版按什么假设设计、要做什么、找谁、拿不到时的替代做法。
   缺外部资料的待办（`gap_version: 2`，旧记录 1）改写为：找谁、为什么只能找他、搞错的后果、资料到手后怎么关、拿不到时的替代做法，
   再列缺什么（手册给了 / 设计还需要 / 出处）、影响的计算（附它依赖的参数）和要问的问题。
   **要向外部要的资料**：按负责方汇总上述问题，每题注明对应待办，可整段发给负责方。
5. **交给后续环节的要求**：状态为 handoff 的 validation / pcb 待办，按负责方列表。
   **引用待人工核对**：设计待办记录、选型记录里的数值在所引手册页的文字里没找到的，逐条列出位置、手册页和数值，请对照原页确认；手册文件不存在或页码越界算记录问题（打包被拒）；没有知识库或 PDF 工具时写明“没核对”。
   **依赖厂家资料的计算**、**依赖工程估计的计算**、**依赖暂缓的需求的计算**（`parameter_version: 3`，旧记录 2，分档由审计推出，见 design-closure.md）：列出算出的值与门槛（`checks`）、依赖的参数或没算的项和对应待办；结论一节按设计成立 / 依赖工程估计 / 依赖厂家资料 / 依赖暂缓的需求 / 不满足计数。旧记录（版本 1）仍是一节“有条件成立的计算”，列写明的假设或没算进去的项。
   **应力风险**（`derating_version: 1`）：在额定内但超过降额值的应力，逐条列出计算、位号、降额规则、应力 / 降额值 / 额定和改进；
   合格但有风险，不挡交付（见 [器件应力规范](stress-spec.md)）。结论一节的“降额等级”一行写等级、来源、应力风险处数和没点名规则的提示数。
   结论一节的“记录版本”一行写明旧版本没核对的内容（版本 2 没核门槛出处和需求检查，`gap_version 1` 没给缺口分类）。
6. **自动检查明细**、**设计资料**链接、**关键设计依据**（notes 的 `highlights`，最多 8 条）、**数字一览**、**详细记录**。

报告里的数字和状态都来自记录，不手改报告；要改内容就改记录后重新生成。agent 只通过 notes.json 补充摘要和说明，与记录按 [术语对照](terminology.md) 同一套术语写：

```json
{"summary": "1–3 句：这一版的状态和最要紧的一件事",
 "changes": "这版改了什么、为什么，一段话",
 "items": {"W1": "这件待办的问题与影响"},
 "highlights": ["已经核对清楚、值得一提的设计结论（最多 8 条）"]}
```

`highlights` 写设计结论。报告的摘要后面会自动加一句本版多少条意见真正改图或补算、多少条只是登记。
计算的值和门槛按 3 位有效数字打印。

写给硬件工程师看：用“设计定型”“待办”“技术转交”这类说法（见 [术语对照](terminology.md)），不写内部代号和英文状态码；
`action`、`owner`、`fallback`、需求的 `implementation`、计算的 `assumptions`/`omitted_terms`/`checks[].name`、
需求澄清的 `question`/`requirement_text`/`proposed_requirement`/`answer.text`
也按这个要求**用中文写**，因为它们原样出现在报告里；器件型号、单位、缩写可以保留。
生成报告时发现英文句子会列为问题（报告顶部显示，命令返回非零），改记录后重新生成。

## 一次跑完：`deliver.py`

```bash
python3 <skill>/scripts/deliver.py <交付目录>
```

参数记在 `record/deliver.json`，随交付保存、每版沿用：`prepare`（可选，本项目先跑的命令，如生成待办记录、预检输入）、
`generate`（出图命令与输出里原理图所在的子目录，`{root}` 是交付目录，`{out}` 是新的空目录）、`root`（根图）、
`verify`（`verify_schematic.py` 的其余参数）、`inputs`（打包登记的需求、原厂资料、上一版）、`check_inputs`（可选，重放的输入核对命令）、
`title`（可选）。格式见脚本说明。

顺序固定：准备 → 待办审计 → 生成前预检 → 出图（替换 `原理图/` 里的 KiCad 工程，BOM 等其他文件保留）→ 自动检查
（KiCad 导出进 `原理图/`，自动检查结果进 `record/`，各页几何进 `record/evidence/geometry-*.json`）→ 交付预检 → 生成报告 →
交付证据（本次运行写出的文件是输出，`原理图/`、`设计资料/`、`record/` 里其余文件是输入）→ 证据新鲜度 → 打包 → 输入核对。
`inputs` 同时传给待办审计、自动检查和打包，三处按同一组资料目录找证据。预检在 `design-preflight.json` 和
`change-contract.json` 都在时做，两个都没有时跳过，只有其中一个算 FAIL。每步的状态从它写出的结果读，不看退出码；
只有 PASS、DONE、有条件通过、未完成、AUTOMATED_PASS、FRESH 继续往下，其余状态、没写出结果或命令出错都停下并说明是哪一步。
下面的分步命令仍然可用。

## 打包检查

```bash
python3 <skill>/scripts/pack_design.py <交付目录> --input requirements=<需求目录> \
  --input datasheets=<原厂资料目录> [--input previous=<前一版交付目录>]
```

检查失败就修正后重跑，直到 PASS：给了 `previous` 时，标为“改图”的审查回复点名的位号必须与上一版设计网表不同
（待办和需求状态不与上一版比较，只由本版设计确认）。顶层只能有上面四样；`原理图/` 和 `record/` 的必需文件齐全；
`设计资料/` 里的表格（有位号列的 CSV）和装配文件（JSON 的 `ref`/`refs`/`fit`/`dnp`）提到的位号都在设计网表里，
表格给出的型号（mpn）和值（value）与设计网表一致——说明文字里提到的位号和描述不在自动检查范围，改版时要人工清理；
`record/` 只有允许的子目录；没有日志和超大文件；`design-closure.json` 在交付目录内重新审核不出错；
报告用到的记录没有问题——可读性或几何检查 FAIL 也算问题（画图问题要改图到 PASS），打包失败；
`datasheets` 目录里的每个 PDF 都已在知识库 `~/Documents/知识库/HardwareWiki/raw/`（同哈希或同文件名，`find_parts.py --file <pdf>` 可查），
没入库的列出来，按 SKILL.md 任务 2.1 的资料规则入库后重跑。通过后写 `record/manifest.json`。
