# 交付目录与设计报告

每一版交付都是同一个固定形状的小目录。给人看的只有 `设计报告.md`，其余是原理图本身和可复核的记录。

## 目录

| 位置 | 放什么 | 不放什么 |
|---|---|---|
| `设计报告.md` | `render_design_report.py` 生成 | 手写的 README、说明、HTML |
| `原理图/` | `.kicad_pro`、根图与各页 `.kicad_sch`、项目符号库/封装库及库表、`schematic.pdf`、`netlist.xml`、`BOM.csv` | 草稿图、旧版图 |
| `设计资料/` | 跨版本有效、每版更新的设计文档，名字固定：如 `方案与选型依据.md`、`器件选型与用法依据.md`、`磁件设计单.md`；`PCB与结构要求.md` 只在需求要求时写，PCB 要求平时由 `pcb` 阶段的技术转交待办带给下游 | 按版本号命名的说明（`v12…`、`v16…`），把仍有效的内容并入固定文档 |
| `record/` | 见下表 | 日志、历史快照、审查方的其他文件（本版独立审查报告放 `sr-review/`） |

`record/` 内容：

| 文件 | 说明 |
|---|---|
| `electrical-intent.json` | 设计网表（每个器件、网络应该怎样） |
| `requirements.json` | 需求清单：需求条文与来源、需求澄清、降额等级、准则范围（模块 C1，格式见 [能力模块](modules.md)） |
| `design-closure.json` | 需求追溯、待办、计算的处理情况；证据路径相对交付目录，所引证据必须在本目录内；需求、原厂资料可留在 `--input` 登记的位置（按文件名找到并核对 SHA-256） |
| `design-closure-audit.json` | `audit_design_closure.py` 的输出（`verify_schematic.py` 输出目录里的 `design-closure.json`，改名放入） |
| `summary.json` | `verify_schematic.py` 的自动检查结果，原样复制 |
| `component-requirements.json` | 新性能流程的唯一源记录：用途筛选、计算得到的性能要求、采购方式、候选核实状态；格式与准备/出图接口见 [器件性能要求](component-requirements.md) |
| `component-requirements-check.json` | 从本次原生图纸、PDF、XML与BOM复核的结果；不与源记录重名，不用历史PASS代替本次核对 |
| `page-plan.json` | 分页方案：`{"schema_version": 1, "pages": [{"file", "reader_tasks": [...], "blocks": {块名: [位号]}, "key_blocks": [关键块名], "circuits": {块名: "典型电路#实现方案"}}]}`；本页每个器件属于一个功能块，关键块标注知识包 `references/knowledge/典型电路/` 里的典型电路与实现方案，库里没有适用的写 `none`，常规块可不标；显式标注均检查（第一页架构页免标） |
| `selection.json` | 核心器件选型：每个角色的位号、决定性条件、≥2 个候选（选中/淘汰理由、相对知识库的手册路径）；每个 U/Q/T 器件都要属于一个角色；选定候选写外部依赖，依赖未公开资料时附 2–3 个方案、建议和用户的决定，格式见 [核心器件选型](core-part-selection.md) |
| `scheme-criteria.json` | 任务 C3.1 关键功能块的候选比较；何时必须有、字段与格式示例见 [知识包](knowledge-package.md) 的规则一节 |
| `visual-review.json` | 图面审阅：`{"status": "REVIEWED/REVIEW_PENDING/REWORK_REQUIRED", "pdf_sha256", "pages": [{"page", "file", "paths", "problems", "render_review_items": [{"item", "disposition"}]}]}`；每页 `paths` 不少于读者任务数；`summary.json` 的 `geometry.render_review_items` 列出的每个图面待审对象都要有非空处置，写出在本版 PDF 上看到了什么；引脚文字的条目按库符号列，处置里要写明看的是 `render_review_refs` 里的哪一只，在一页处置过的库符号别的页不必再写；没改动的页面也按本版 PDF 重新看，处置、路径和 `method` 不写“沿用”“同上一版”；`REVIEWED` 时 `pdf_sha256` 必须是本版 `原理图/schematic.pdf` 去掉导出时间后的 SHA-256（`render_design_report.py --pdf-sha256 原理图/schematic.pdf` 给出），PDF 图面变了就要重新审阅 |
| `delivery-evidence.json` | 导出后有没有再改过的核对记录 |
| `calculations/` | 本版设计还在依赖的计算（不管是哪一版算的），作废的不带 |
| `interfaces.json` | 任务 C3.3 接口定稿：每条跨块流向源块要保证、负载块能接受的范围（模块 C3，格式见 [能力模块](modules.md)） |
| `knowledge-gaps.json` | 知识缺口清单：`knowledge_gaps.py <交付目录> [--input datasheets=<资料目录>]` 从记录抽出，不手写；`deliver.py` 在生成报告前运行它，报告的“知识缺口”一节照它列出。`{"schema_version": 1, "counts": {信号: 数量}, "gaps": [{"signal", "module", "task", "item", "detail", "source"}]}`。信号有八种：`no_typical_circuit`（块文件里选定方案没有标典型电路）、`knowledge_missing`（知识包其他组件查不到的：`modules.json` 的 `knowledge_lookups` 里 `found` 为空的行，见 [知识包](knowledge-package.md) 的查阅记录）、`unverified_candidate`（方案候选 `unverified`）、`datasheet_not_in_library`（手册不在知识库）、`weak_basis`（计算参数或门槛的依据是 `typical`/`model`/`unspecified`）、`external_item`（未关闭的外部资料待办）、`returned_upstream`（`modules.json` 的 `returns`）、`user_overrode`（用户给定的需求与建议条文不同，或选定方案不是推荐方案）。清单不拦交付；打包只核它是从当前记录抽出的（手册条目取决于知识库，不比对）。能力缺陷的归纳在评测侧做 |
| `block-circuits/` | 每个功能块一个块文件，由 `block_circuits.py` 从 `scheme-criteria.json`、`selection.json` 抽出（模块 C3，格式见 [能力模块](modules.md)） |
| `scripts/` | 图页脚本，下一版只重生成有变化的页面 |
| `evidence/` | 设计结论引用的截图、手册摘页等 |
| `sr-review/` | 本版交独立审查（schematic-review）时的审查报告、`findings.json` 与审查记录；没有就不建 |
| `manifest.json` | `pack_design.py` 写：需求、原厂资料的路径和 SHA-256，本目录每个文件的 SHA-256，所用知识包的版本与指纹（`knowledge_release`，从 `knowledge-release.json` 读） |

单个文件超过 10 MB 说明带了不该带的东西：仿真原始波形、整份手册、历史台账。只留结论引用的部分，
其余留在工作目录，或用 `--input` 按路径登记。

## 设计报告

`render_design_report.py <交付目录> [--notes notes.json] [--title 标题]` 从 `record/` 生成，顺序固定：

1. **结论**：器件数、页数；图纸自动检查各项结果的数量；图面审阅；需求状态；
   设计是否完成，没完成时逐条列出还差什么；有用户暂缓的需求时单列一行点名；有缺外部资料的待办时单列一行，
   按负责方计数并给出受影响的有条件计算数；有外部条件不确定的选型时单列一行，点名角色和你选的方案。
2. **这版改了什么**：notes 的 `changes`。
   **需求澄清记录**：问过用户的每个需求问题：需求原文、问题、建议条文、答复（用户给定/采纳建议/用户暂缓）、答复人与日期、涉及的需求；有未答复的问题算记录问题（打包被拒），见 [需求澄清](requirement-clarifications.md)。
3. **待办**：`design-closure.json` 里未关闭的待办。用户暂缓的需求（`requirement`）的排最前，其余按由 `consequence_class` 和 `occurrence` 推出的等级
   从重到轻排；写明类型、本版按什么假设设计、要做什么、找谁、拿不到时的替代做法。
   缺外部资料的待办（`gap_version: 2`）改写为：找谁、为什么只能找他、搞错的后果、资料到手后怎么关、拿不到时的替代做法，
   再列缺什么（手册给了 / 设计还需要 / 出处）、影响的计算（附它依赖的参数）和要问的问题。
   **要向外部要的资料**：按负责方汇总上述问题，每题注明对应待办，可整段发给负责方。
4. **交给后续环节的要求**：状态为 handoff 的 validation / pcb 待办，按负责方列表。
   **引用待人工核对**：设计待办记录、选型记录里的数值在所引手册页的文字里没找到的，逐条列出位置、手册页和数值，请对照原页确认；手册文件不存在或页码越界算记录问题（打包被拒）；没有知识库或 PDF 工具时写明“没核对”。
   **不满足的计算**（计算表的第一节）：每条不满足的检查的值与门槛（最好情景注明）、`contributors` 里最大的几项、
   design 待办的改设计候选（须用户批准）和对应待办。
   **依赖厂家资料的计算**、**依赖工程估计的计算**、**依赖暂缓的需求的计算**（`parameter_version: 3`，分档由审计推出，见 design-closure.md）：列出算出的值与门槛（`checks`）、依赖的参数或没算的项和对应待办；结论一节按设计成立 / 依赖工程估计 / 依赖厂家资料 / 依赖暂缓的需求 / 不满足计数。
   **应力风险**（`derating_version: 1`）：在额定内但超过降额值的应力，逐条列出计算、位号、降额规则、应力 / 降额值 / 额定和改进；
   合格但有风险，不挡交付（见 [器件应力规范](shared/stress-spec.md)）。结论一节的“降额等级”一行写等级、来源、应力风险处数和没点名规则的提示数。
   **余量不足以覆盖估计误差**（`uncertainty_version: 1`）：余量小于所依赖工程估计不确定度的检查，列值 / 门槛、余量 / 不确定度和改进；
   合格但有风险，不挡交付，结论一节写处数。
   **共用设计准则**（`guideline_version: 1`）：报告只在结论一节写一行设计准则库版本和各类条数，不逐条列准则；
   每条准则的落实处、不适用理由、分组核对结果和下游约束只留在 `record/design-closure-audit.json` 的 `guidelines`（用户 2026-11-08）。
   准则对设计的影响按决定写在别的节里：淘汰候选方案的写在方案比较（`scheme-criteria.json`），转交下游的写在“交给后续环节的要求”。
   器件性能流程一行之后：按 BOM 规格转交采购的件只写一行总数；性能要求提示（不起约束的要求、套用的同一句条件）每类一行。
   记录不是现行版本（[design-closure.md](design-closure.md) 开头列的六个版本）时，报告开头提出记录问题，打包被拒，按现行格式重写。
5. **自动检查明细**、**设计资料**链接、**关键设计依据**（notes 的 `highlights`，最多 8 条）、**数字一览**、**详细记录**。

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

顺序固定：准备 → 待办审计 → 出图（替换 `原理图/` 里的 KiCad 工程，BOM 等其他文件保留）→ 自动检查
（KiCad 导出进 `原理图/`，自动检查结果进 `record/`，各页几何进 `record/evidence/geometry-*.json`）→ 生成报告 →
交付证据（本次运行写出的文件是输出，`原理图/`、`设计资料/`、`record/` 里其余文件是输入）→ 证据新鲜度 → 打包 → 输入核对。
`inputs` 同时传给待办审计、自动检查和打包，三处按同一组资料目录找证据。每步的状态从它写出的结果读，不看退出码；
只有 PASS、DONE、有条件通过、未完成、AUTOMATED_PASS、FRESH 继续往下，其余状态、没写出结果或命令出错都停下并说明是哪一步。
下面的分步命令仍然可用。

图面审阅要看本次导出的 PDF。出图是确定的（同一输入每次画出同一份图），任务 4 自动检查导出的 PDF 与 `deliver.py` 重新导出的 PDF 渲染内容相同（`render_design_report.py --pdf-sha256` 不计导出时间），所以按任务 4 的 PDF 写好 `record/visual-review.json` 后，`deliver.py` 跑一遍就到打包。`visual-review.json` 缺、不是 `REVIEWED` 或 `pdf_sha256` 对不上本次 PDF 时，运行在自动检查之后停在“图面审阅”（退出码 2，打印本次 PDF 的哈希），不再跑到报告才失败；按这份 PDF 审阅后再跑。`--for-review` 仍可用，自动检查后无条件停下。自写出图脚本要保证确定：对集合、字典的遍历排序时给全序键（Matrix 2026-11-07：按“是否回线”一个布尔键排序，平局时顺序随 `PYTHONHASHSEED` 变，两脚器件朝向随之翻转，两次 PDF 不同）。器件性能记录的 `RequirementsSHA256` 不含来源文件的哈希，只改计算脚本不会让图面字段和 PDF 变化（来源文件另行按哈希核对）。打包后列出的“手册待入库”只是提示，不使运行失败。

## 交付证据（快照检查）

导出后的任何清理、图形、标签或字段改动都使旧的导出和 PASS 作废，要重新导出再写本记录。

最终导出/检查之后，把 `delivery-evidence.json` 存在工程根目录或交付目录的 `record/` 中；放在 `record/` 时其中的路径相对于交付目录
（如 `原理图/board.kicad_sch`）：

```json
{
  "schema_version": 1,
  "root": "board.kicad_sch",
  "inputs": {"board.kicad_sch": "<sha256>", "child.kicad_sch": "<sha256>"},
  "outputs": {"board.xml": "<sha256>", "erc.json": "<sha256>", "geometry.json": "<sha256>", "board.pdf": "<sha256>"},
  "roles": {"netlist": ["board.xml"], "erc": ["erc.json"], "geometry": ["geometry.json"], "render": ["board.pdf"]}
}
```

包含每张活动页、工程配置、符号表和本地 `symbols/*.kicad_sym` 输入。哈希所有引用的输出，用到时包括基线增量和图面审阅记录；
允许 `identity`、`routing`、`visual_review` 等额外角色。存真实的 SHA-256 字符串，不是占位符。

报告交付前立即运行 `python3 scripts/check_delivery_freshness.py <工程>/delivery-evidence.json`。它核对活动层次的覆盖，
拒绝缺失/被改动的输入、输出和必需的角色证据。`FRESH` 只表示这份声明的快照没有变。它不能证明某条命令运行过或有人看过 PDF，
也从不把 ERC 失败、几何缺口、继承的未关闭问题或电气 NO_GO 升为 PASS。

## 打包检查

```bash
python3 <skill>/scripts/pack_design.py <交付目录> --input requirements=<需求目录> \
  --input datasheets=<原厂资料目录>
```

检查失败就修正后重跑，直到 PASS：顶层只能有上面四样；`原理图/` 和 `record/` 的必需文件齐全；
`设计资料/` 里的表格（有位号列的 CSV）和装配文件（JSON 的 `ref`/`refs`/`fit`/`dnp`）提到的位号都在设计网表里，
表格给出的型号（mpn）和值（value）与设计网表一致；`设计资料/*.md` 正文里写成“位号 型号”的（如“U801 LTC4367”：位号字母是设计网表用到的前缀，紧随的词含数字和大写字母、至少 4 个字符，不是带单位的数值如 100uF、不是 Pin3/4 这类词加编号），位号要在设计网表里，型号要与该位号的 mpn 对得上（忽略大小写和连字符，可省封装/变体后缀和 SN74 这类系列前缀：LM5069-1 对 LM5069MM-1/NOPB、LVC07A 对 SN74LVC07APWR），否则按文件和行号报错（Matrix R2：器件改成 LTC4367 后 `供电路径复核.md` 还写着“U801 LM5060”）；表格行（`|` 开头）和代码块不核，其余说明文字（只提位号不写型号、写功能描述）不在自动检查范围，改设计时要人工清理；
`record/` 只有允许的子目录；没有日志和超大文件；`design-closure.json` 在交付目录内重新审核不出错，且没有 `design_document_incomplete`（有对外连接器的板 FMEA 与 EMC 端口矩阵齐全，见[必写的设计文档](guideline-evidence-groups.md)；没引用的适用准则不挡打包），也没有 `matrix_cell_missing`、`matrix_cell_failed`（`object_matrices.py` 列出的矩阵与状态表逐格有结论且满足）；
报告用到的记录没有问题——可读性或几何检查 FAIL 也算问题（画图问题要改图到 PASS），打包失败；
通过后写 `record/manifest.json`。`datasheets` 目录里还不在知识库 `~/Documents/知识库/HardwareWiki/raw/` 的 PDF
（同哈希或同文件名都算在库，`find_parts.py --file <pdf>` 可查）不挡打包，列进 manifest 的 `datasheets_to_file` 并打印出来，
设计完成后提示用户复制进知识库（SKILL.md 任务 C4.1 的资料规则）。
