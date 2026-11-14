# C6 原理图绘制

做本模块前读 [SKILL.md](../SKILL.md) 和本文件。各模块的总表见 [SKILL.md 的主流程](../SKILL.md#主流程)，关卡与交接文件见 [能力模块](modules.md)，单独运行时的任务书见 [任务书格式](workflow-handoff.md)。

给定输入：设计网表；串联运行时另读 `architecture.json` 与各块的 `block-circuits/<块>.json`（各块选定的典型电路）；单独运行时只给网表。产出：`page-plan.json`、KiCad 工程、`summary.json`、`visual-review.json`。

## C6.1 分页方案

分页时给需要展示的性能要求分配位置：基本数值放元件旁，较长的条件放同页技术要求表或注释，用位号/注号对应。只显示设计与替代需要的信息，不把整段计算或数据手册搬到图上。表格和说明必须进入正常的布局与几何检查。

按功能、隔离/电压域和可读面积分页；几个很小的功能块合成一页，不单独占一张 A3。
为每页写一张简短的分页方案，内容包括：读者任务（跟随能量流、看懂反馈、追一个受保护接口……）、
功能块及每块的位号、主路径、电源轨、出页网络及目的功能/页码、标签边界。先保证一条功能路径易读，再决定拆页或加大纸张。
分页方案随交付保存为 `record/page-plan.json`（每页 `file`、`reader_tasks`、`blocks`、`key_blocks`、`circuits`），本页每个器件都要属于一个功能块，
每个关键功能块标注所用典型电路与实现方案 `"<典型电路文件名>#<实现方案名>"`（第一页是架构页，免标；没有适用典型电路的关键块写 `none`）；
图面审阅按它逐条追路径。见 [human-readable-routing.md](human-readable-routing.md) 第 1 节。
单独运行 C6、没有 `architecture.json` 和块文件时，功能块划分由本任务从网表定，`key_blocks`、`circuits` 留空，C6 关卡不做典型电路标注检查。
纸张在画完后定：内容能放进 A4 就用 A4；一页只剩零散小块时并页，不把小电路摊在 A3 上。

- 按拓扑选结构（Buck、LDO、隔离反激、滤波、MCU 各不相同），见
  [schematic-drawing-standards.md](schematic-drawing-standards.md) 第 2 节。不得为别的拓扑编造 SW 节点或电感级。
- 按绘图纲要 决定页面流向、锚点、器件归属、画法、出线、标签、间距和修复顺序，见
  [drawing-recipes.md](drawing-recipes.md)。
- 图面的目标是逻辑清晰、按功能块划分、方便工程师理解、能指导 PCB 设计；按绘图纲要里的画图习惯落实（块标题、块内导线块间标签、不绕远、
  密度与纸张、多单元器件按单元画、去耦画在引脚旁、写给 PCB 的短注），见同一文件。

做完的标志：`render_design_report.py` 的分页方案检查无问题：每页的读者任务、功能块与关键块的典型电路标注（库里没有适用的写 none）齐全，每个器件属于一个功能块。

## C6.2 图页脚本

```python
from schematic_layout.pages import page_intents
from schematic_layout.recipes import Sheet, DOWN, RIGHT, UP, LEFT, add
from schematic_layout.sexpr import dump

RAILS = {"GND": "power:GND", "+3V3": "power:+3V3"}
for n, (key, page) in enumerate(page_intents(board, rails=RAILS).items(), 1):
    s = Sheet(page["intent"], rails=page["rails"], external=page["external"],
              power_ref_start=n * 100 + 1)
    s.place("U201", (101.6, 76.2), pin="3", facing={"3": LEFT})   # 锚点：按引脚朝向定姿
    ...                                                             # series / shunt / bank / divider / label
    root, report = s.build(key)            # 先用 draft=True 出图调试，交付不能是 draft
```

- 先看 `s.plan` 给出的器件角色和网络标签角色。只给锚点写坐标，其余器件用与角色相符的画法从引脚推出。
  有意偏离绘图纲要时用 `s.justify(对象, 理由)` 记录。把分页方案的功能块传给 `Sheet(..., blocks={块名: [位号]})`：
  同一块内的器件之间不许用局部连接标签代替导线（HR-01），审计会列出只连一块的标签。
- 间距只为通过检查而加大，通过后缩回：上限与豁免按 O7（超过 12 格进结构审计，一页超过 3 处间距豁免即审计不通过，改为折行或重新锚定）；
  带小网络名的串联段或本引脚短线，放置前用 `s.name_run_steps` 预留直段，用法见 [drawing-recipes.md](drawing-recipes.md)。
- `build()` 遇到硬缺陷会直接报错。`report["structure"]` 必须为 PASS，`report["readability"]["gate"]` 必须为 PASS。
  失败时按 O8 改结构（方向、间隙、顺序 → 锚点 → 拆行）后重建，不得手调坐标打补丁。
  `report["readability"]` 还给出 `cell_coverage`（有东西的 25.4 mm 格占比）、`part_groups`（只靠标签/电源符号相连的器件组）
  和 `fits_paper`：覆盖率低、组数多于分页方案的功能块、内容能放进更小的纸张，都说明这页要并块、缩间距或换纸。
- 元件旁的基本规格和同页性能注释从 `component-requirements.json` 生成（长要求用 `Sheet.performance_notes(at)`），不手工回抄；
  措辞与可见性要求见 [器件性能要求](component-requirements.md)。仍缺计算的审阅草稿标注“待计算”，不能凭此声明完成。
- 图页脚本随交付版本一起保存；下一版只重生成有变化的页面。

做完的标志：每页 `Sheet.build()` 不报错，`report["structure"]` 与 `report["readability"]["gate"]` 为 PASS；每页间距豁免不超过 3 处。

## C6.3 组装工程

多页工程用 `schematic_layout.root.Root` 组装根图：`page()` 放各页的层次图框，`flow()` 画带名字、两端落在图框上的流向线
（`kind="power"` 能量流、`"signal"` 控制链，线宽不同），`isolation()` 画隔离边界，`write()` 写出根图 `System_block`、
各页（实例路径改写到根工程）、`.kicad_pro` 和 `sym-lib-table`；文字压线或系统框图审计不通过时直接报错。
用法见 [drawing-recipes.md](drawing-recipes.md) 多页一节。
第 1 页 `System_block` 按任务 C2.1 的架构画，要求见 [reference-driven-board-design.md](reference-driven-board-design.md) 的 System_block 一节。

做完的标志：`Root.write()` 不报错，写出根图、各页、`.kicad_pro` 与 `sym-lib-table`。

## C6.4 自动检查

```bash
python3 <skill>/scripts/verify_schematic.py <root.kicad_sch> --intent electrical-intent.json \
  --out <新的空目录> [--expected-pages N] [--symbol-exceptions F] [--readability-waivers F] \
  [--reference-contract F] [--design-closure D --artifact-root R]
```

它一次完成：KiCad ERC / XML 网表 / PDF 导出，网表分区与器件身份逐脚对比设计网表（图上画出的网络名须等于设计网表里同一组引脚的网络名，
只允许页路径前缀；KiCad 自动网络名不比），层次与 PDF 页数，根图的系统框图检查（`system_block`），
符号引脚完整性，分立器件符号含义与手册/型号后缀是否一致（`discrete_semantics`），可读性检查（零异网交叉、零三折以上两端连线、
内容放得进更小纸张的页算 FAIL），以及每个有效页面的几何检查，汇总到 `summary.json`。
只有全部检查项为 PASS 时结果才是 `AUTOMATED_PASS`。
可以用 `scripts/deliver.py <交付目录>` 一次跑完出图、自动检查到打包，参数记在 `record/deliver.json`，见 [交付与设计报告](delivery-report.md)。

- 器件性能检查核对性能定义、选型符合性状态和设计网表/BOM/图面的一致性：规格绑定以 KiCad 导出的属性/XML 为准，可见内容以实际 PDF 为准，
  判法见 [器件性能要求](component-requirements.md)；检查器覆盖不到的图面对象转任务 C6.5，不自动判通过。
- 新设计提供 `--design-closure`，核对需求实现、外部依赖、计算覆盖和证据是否最新；格式与边界见 [设计待办记录](design-closure.md)。未提供时明确为 NOT_CHECKED，不能据此声明全流程完成。
- ERC 要求零违规。
- ERC 摘要按原始报告的 UUID/object 对应实际层次实例、引脚及 KiCad 网络，再归因到电源轨；
  不凭位号或网络名文字猜问题对象。无法对应时保留原违规与待核边界，见 [project-verification.md](project-verification.md#erc-摘要对应到对象)。
- 几何检查只覆盖本次 KiCad 导出中已合格的对象，范围与未支持对象见 [native-geometry.md](native-geometry.md)；
  外部 JSON 回执不能授权放行。`geometry` 为 INSUFFICIENT 时保留缺口并在 KiCad 渲染图上核对，有限 PASS 不等于整案通过。
  库里隐藏的引脚号/引脚名不计；可见但无法由 KiCad 导出核对的引脚文字列在 `geometry.render_review_items`（图面待审对象），
  不算缺口。引脚文字是库符号自带的，同一种库符号只列一条，并列出用它画的位号；每只器件的引脚号有没有被别的文字或导线压住由几何检查逐只查
  （`pin_number_text`、`pin_number_wire`）。任务 C6.5 图面审阅覆盖这些对象并在 visual-review.json 里写明。
- 图面检查只有三种结果：PASS、FAIL（画图问题，如外框间距不足 1.27 mm、导线交叉不打点、注释压线）、
  INSUFFICIENT（检查器覆盖不到的对象）。FAIL 由 ASG 改图关闭，不交给人复核；可读性或几何 FAIL 时
  `pack_design.py` 拒绝打包。只有 INSUFFICIENT 缺口留给图面审阅核对。
- KiCad 自动生成的 `Net-(...)` 网络名不与设计网表比名；设计网表里的网络名必须显式标注在图上，与导出网表一致，见
  [project-verification.md](project-verification.md#自动网络名不比对)；
  编码斜杠层次字段只用 [schematic-drawing-standards.md](schematic-drawing-standards.md) 的有限回退，不推广。
- 工程的 ERC 规则不得设为忽略（`simulation_model_issue`、`footprint_filter` 除外），自动检查读取工程设置核对。
- 失败时修改相应图页脚本，在新的运行目录重新生成并检查。不得为了降低计数而加 PWR_FLAG、加排除项或改引脚类型。
- PWR_FLAG 只用于设计网表逐网声明的 `external_supply`（只由连接器引入、板上没有电源输出脚驱动的电源或地）和 `filtered_supply`
  （经一颗串联电阻、电感、磁珠或保险丝从已有驱动的电源派生的供电网，逐条列入设计报告），用 `Sheet.power_flag()` 每网放一个，由 `external_supply` 检查项核对；
  声明格式见 [requirements-to-intent.md](requirements-to-intent.md) 第 5 节“连接器角色与外部供电”。
- 整流、变压器或分立稳压电路没有 KiCad `power_out` 时，不冒充连接器供电、不改引脚类型，按[分立供电复核](reviewed-circuit-supply.md)
  的 `reviewed_circuit_supply` 处理；自动检查只核证据是否最新和 KiCad 拓扑，未完成复核时保留 ERC。
- `symbol_integrity` 的 `unnamed_pins` 只作诊断（KiCad 运放、单门逻辑等符号的输入/输出脚按库惯例不写名字）。
  列出的每个器件（不限核心器件）都要在外围电路核对表里按数据手册名字逐脚对应，并在设计报告中列出这些脚；
  否则按引脚名核对时会对不上。

做完的标志：`summary.json` 没有 FAIL 的检查项，INSUFFICIENT 的逐条列出原因；导出网表与设计网表逐脚一致；ERC 零违规。

## C6.5 图面审阅

在实际 PDF 上逐页核对性能标注（位号/注号对应、参数与单位、“要求/器件保证/待核”含义清楚、表格未压线），按位号记录结果；隐藏属性完整不代替这一步。

打开导出的 PDF，逐页按 `page-plan.json` 的读者任务追主路径、支持网络与回流路径、重复通道、地域和隔离跨越；
逐页核对绘图纲要画图习惯里不自动检查的各条，`report["readability"]["detours"]` 列出的绕远连线逐条处置；
逐条处置 `geometry.render_review_items`：每种库符号挑一只器件在本版 PDF 上看它的引脚号和引脚名，处置里写明看的是哪一只、看到了什么；
同一种库符号在别的页不必重复处置。没改动的页面也重新审阅，不沿用上一版的处置。
追法、三种状态（待返工 / 待图面审阅 / 已完成图面审阅）和 `pdf_sha256` 的写法见 [human-readable-routing.md](human-readable-routing.md) 第 4 节
与 [delivery-report.md](delivery-report.md) 的 `visual-review.json` 一行。用户否决会重新打开图面审阅。

做完的标志：`visual-review.json` 为 `REVIEWED`，每页路径数不少于读者任务数，每个图面待审对象有本版的处置，`pdf_sha256` 对得上本版 PDF。
