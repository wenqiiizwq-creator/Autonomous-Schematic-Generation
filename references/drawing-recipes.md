# 绘图画法（按引脚几何画出可读的页面）

每张给人读的页面都用，无论新画还是重画。agent 写一段简短的图页脚本说明**结构**；`schematic_layout.recipes.Sheet`
从真实的库引脚推出几何并写出显式导线。这是 [human-readable-routing.md](human-readable-routing.md) 背后的构图层。

可读的连线是摆放问题。引脚背对它所接的网络时，任何走线器都只能绕回来。一块 100 W 充电器上，手工摆放的 v0.2.2 页面有 29 处异网交叉、
237 个拐弯。同一电路从引脚出发放置支持器件、用显式主干重画后，交叉为 0，拐弯 82 个。

## 做法

1. 按 human-readable-routing.md 第 1 节写分页方案（阅读路径、功能块、电源轨、标签）。整板时用
   `pages.page_intents(board, rails=...)` 得到每页的设计网表和出页网络。
2. `sheet = Sheet(intent, rails={...}, external=[...])`，读 `sheet.plan`：每个器件建议的角色和每个网络的标签角色。
3. 按下面的绘图纲要写图页脚本：先放锚点，再按角色允许的画法画其他器件。只给锚点和有意的 Z 形段写坐标。
   每处有意的偏离在做出时用 `sheet.justify(part_or_net, reason)` 记录。
   带小网络名的段先按下文 `name_run_steps` 一段预留直段。
4. `root, report = sheet.build(name)`，然后写出 `dump(root)`。遇到任何硬缺陷 build 都会报错（见下）；改结构，不改症状。
5. `report["structure"]` 必须为 PASS：每条发现要么已修正，要么是记录了理由的偏离。
6. 运行 `scripts/verify_schematic.py <root.kicad_sch> --intent <设计网表> --out <新目录>`：一次完成 KiCad ERC、
   设计网表分区与身份、层次/PDF、符号完整性、必需的可读性检查项，以及每张活动页的几何检查。整板时，图上画出的每个（非自动的）网络名
   必须等于设计网表中同一组引脚的网络名，只允许页路径前缀。`compare_netlist(xml, intent, report["layout"])` 则按单页的布图策略
   核对该页的标签和电源轨名字。
7. 用 KiCad 渲染，并追每个声明的读者任务。

## 绘图纲要（怎样决定结构）

这些规则是 SKILL.md 中 ASG 纲要里的绘图纲要：任何改动都须先把草案交给人确认（SKILL.md「纲要的修改」）。

拓扑决定由 agent 做；这些规则让决定可重复。按顺序使用。后面的规则细化前面的，从不推翻；只有 O8 按它写明的顺序改变前面的决定。

| # | 决定 | 规则 |
| --- | --- | --- |
| O1 | 页面流向 | 先选这页的读者任务。**路径页**（功率级、滤波、受保护接口）的主能量/信号路径沿一行从左到右，从输入接口到输出接口；第二条路径在下面另起一行，各行按它们在系统中的位置排序。主路径比绘图区宽时，在已是电容组、电源轨或测试点的节点折到下一行；折行延续同一条路径。**控制器页**（MCU、PD/协议控制器、PHY）把控制器放在中间；每个引脚组的支持电路放在该引脚组一侧，对外接口放在朝向其连接器或页的页边。 |
| O2 | 锚点 | 锚点是三脚及以上的器件和连接器（`sheet.plan` 会建议）。先放锚点，尽量正立；只为让输入朝上游、输出朝下游才旋转或镜像（`place(..., facing=...)`）。构成一个功能的锚点（如控制器及其 MOS、驱动器及其桥）共用一个功能块；否则每个锚点一个功能块，按路径顺序排列。 |
| O3 | 归属 | 两脚器件归属于它所接引脚网络的锚点。几个锚点共用该网络时，归属于赋予它功能的那个引脚（上拉归它拉的开漏输出，去耦归它去耦的电源引脚，栅极电阻归它的栅极），否则归路径顺序上的第一个锚点。位于两个锚点之间、或在没有锚点引脚的无源链中的器件，归属于它所在的路径段，按路径顺序画。从不把支持器件画进另一个锚点的功能块里。 |
| O4 | 按角色选画法 | 用 `sheet.plan` 建议的角色：`series` 在路径轴上；`shunt` 从其节点引向其电源轨（地网络向下，正电源向上，负电源轨在其地网络下方）；`bank` 用于接在相同网络上的并联器件，画成一组、一个地网络；`divider` 竖直叠放，抽头侧向引到检测引脚；`lane_*` 画成排列相同的串联+并联通道；`decoupling` 在其锚点的电源引脚处画成并联支路或组。 |
| O5 | 引脚出线 | 每条支路从引脚沿其向外方向开始（`stub`，或从引脚起始的画法）。需要够到锚点另一侧引脚的支持支路，从锚点功能块的上方或下方绕过，从不穿过另一条支路；做不到就把器件移到那个引脚一侧。 |
| O6 | 电源轨与标签 | 电源轨和地网络用声明的 `rails` 里的电源符号；全局标签只用于 `external` 网络；小网络名用于方案里的 `name` 网络；局部连接标签只在有边界理由时使用。 |
| O7 | 间距 | 画法的间隙至少两格，至多 `MAX_SPACING_STEPS`（12 格，约 15 mm），除非脚本记录了理由；同样的上限适用于短线、显式的组间距和引线，以及电源轨/标签引线。先加大间隙再手工移动器件，构建通过后再缩回。带小网络名的网络需要一段比名字长两格以上的直线。带长值的竖放器件需要一侧留出那段文字的宽度。功能块之间的间隔大于块内器件之间的间隔；不为填满纸张而撑大页面。 |
| O8 | 修复顺序 | 构建出错或检查项失败时，先改画法的方向、间隙或顺序；再改锚点的位置或朝向；然后折行或把功能块拆成几行（O1）。从不加标签来掩盖失败的导线。页面通过后读 `report["readability"]`：缩小审计列出的间隙；`fits_paper` 比当前纸张小时，换到那张纸，或把本页剩下的功能块并过去。 |

自动检查覆盖的部分：

| 规则 | 由谁检查 | 不检查的（在渲染图上追） |
| --- | --- | --- |
| O4 | 结构审计：画法与角色是否相符、组是否画成一组、通道是否相同 | 角色本身是否适合电路 |
| O6 | 结构审计：全局标签恰好在出页网络上、电源轨只用其电源符号、选定的网络名都在、没有无理由的未选定局部标签；提供 `blocks` 时，连接的器件都属于同一功能块的局部连接标签 | 标签措辞 |
| O7 | `build()` 硬拒绝：本体间距、文字碰撞、导线穿本体；结构审计：超过 `MAX_SPACING_STEPS` 且无理由的间隙、短线、间距、引线；可读性检查项：内容放得进更小纸张的页 | 功能块与器件间距之比、`cell_coverage` 低的页是否该并页 |
| O1、O2、O3、O5 | 可读性检查项能抓到部分后果（交叉、U 形回头） | 路径顺序、功能块成员、归属、支路所在侧 |

所以结构审计 PASS 只覆盖 O4 和 O6。称页面可读之前，在渲染页上审阅其他规则。

## API

| 调用 | 画什么 |
| --- | --- |
| `Sheet(intent, rails, external, paper, dirs, power_ref_start, blocks)` | 一张页。`rails` 把网络映射到 `power:` 符号，`external` 列出离开本页的网络；两者使 `plan` 和审计可用。`power_ref_start` 让 `#PWR` 位号在各页间唯一。`blocks` 是分页方案的 `{功能块: [位号]}`；提供后审计拒绝只连接同一功能块器件的局部连接标签（HR-01）。 |
| `plan` | `{"parts": {ref: {role, why, ...}}, "nets": {net: "power" \| "global" \| "name" \| None}}`。`intent["net_roles"]` 声明为 return 的网络是地网络；只有未声明的电源轨才退回按电源符号方向判断。电阻是 `Device:R*` 器件或 `fields.ComponentRole` 为 `resistor` 的器件。 |
| `justify(part_or_net, reason)` | 记录一处有意的偏离；审计连同理由一起列出。间距偏离的 `reason` 写明多出的空间避开的器件、引脚或 `text:<字段>`。 |
| `place(ref, at, rotation, mirror, pin, facing, order)` | 锚点：控制器、连接器、磁件、桥。`facing={pin: direction}` 按要求的引脚出线方向选旋转/镜像（`order=(a, b, axis)` 让引脚 a 在 b 之前）；给了 `pin` 时，`at` 是该引脚的端点。 |
| `orient(ref, facing, order)` | `facing` 会选出的 (rotation, mirror)；没有朝向能给出这些出线时报错。 |
| `put(ref, pin, at, toward)` | 把器件的 `pin` 放在 `at`，沿 `toward` 延伸（引脚朝回）。多于两脚的器件保持正立。 |
| `stub(pin, n)` | 沿引脚自身方向出线；返回端点。 |
| `series(start, [refs], toward, gap, net)` | 按电路顺序在一条轴上的串联链；接当前网络的引脚朝向起点。返回各远端引脚的点。 |
| `shunt(node, ref, toward, gap, rail)` | 从节点引出的两脚支路；远端引脚接其声明的电源轨符号（`rail=False`：返回远端引脚）。 |
| `bank(start, refs, toward, hang, pitch, gap, rail, common, depth, lead)` | 从主干按实测间距引出的并联器件；`common` 时一条笔直的公共地网络线和一个符号（`rail=False`：公共线是信号网络，如 L_EMI 下的 N_EMI，或驱动线旁的栅极线）。`depth` 固定公共线的距离；`lead=0` 把第一个器件放在 `start`（与引脚对齐）。`hang=RIGHT` 配 `toward=DOWN` 得到经典的并排并联对。返回主干末端。 |
| `divider(top, upper, lower, toward, gap, rail)` | 叠放的分压；返回中点导线上的抽头点。 |
| `connect(a, b, first, x, y)` | 引脚/点之间的 L 形（`first` 为 h/v）或 Z 形（中段在 `x` 或 `y`）。 |
| `wire(*pins_or_points, net)` | 显式的正交折线；每个引脚都必须在 `net` 上。 |
| `power(target, symbol, net, length)` | Value 为网络名的电源轨/地网络符号（默认用声明的符号）；垂直方向的引脚会侧向引出，足以避开器件本体。 |
| `label(target, kind, length, outward, net, reason)` | 网络离开本页处的全局标签，或带 `reason` 的局部连接标签。沿引脚方向或 `outward`（left、right、up、down）延伸。设计网表 `boundary_nets` 声明的离板网络由 `Sheet` 算进 `external`，单页出现也画全局标签，不写局部标签加理由（见 [requirements-to-intent.md](requirements-to-intent.md)）。 |
| `name_run_steps(net, font=1.0)` | 只读的必需直线段预算：对声明的原始逻辑网络/字号，取已有局部 `label_geometry` 的宽度加两格，向上取整到格数。不添加摆放或标签。 |
| `name(net, at, font=1.0)` | 网络自身导线上的小局部网络名，放在线段中部并避开引脚和点：水平导线在上方，否则在竖直导线旁。只用于尚无该网络标签或电源轨符号的连通片段；每个片段都已显示名字时 `build()` 跳过它（`report["names_skipped_already_labelled"]`），对这样的片段显式给 `at` 会报错。 |
| `select_local_names(intent, external, rails)` | 默认选择：接到三脚及以上器件的页内局部网络。 |
| `text(text, at, font)` | 功能块标题或注释。 |

每种画法把超过 `MAX_SPACING_STEPS` 的间隙、短线、间距、引线或引线长度记入 `sheet.spacing`；除非 `justify(ref_or_pin, reason)`
说明这段走线为什么需要空间，审计把每处列为 `spacing` 发现；一页超过 `MAX_SPACING_DEVIATIONS`（3）处有理由的间距偏离本身就是一条发现：
折行或重新定锚点（O8）。实测的组间距（`pitch_for`）从不算发现。报告中的可读性指标另有
`paper`、`content_size_mm`、`fits_paper`、`oversized_paper`（检查项不通过的原因之一）、`occupancy`、`cell_coverage`（有任何对象的 25.4 mm 格占比）、
`part_groups`/`part_group_refs`（只靠标签或电源轨符号相连的器件算不同的组）和 `longest_segment_mm`。

`build(name, draft=False)` 返回 KiCad 根对象和一份报告。`draft=True` 时，名字和字段失败列在 `draft_failures` 里而不报错，
这样修页面期间可以出图；草稿从不交付。哪一侧都放不下的字段（桥、四面都连线的器件）放在本体空着的角上。
内容保持在页边以内 5 mm、不进入标题栏：导线离开该区域、进入标题栏或穿过本体时 `build()` 报错，用的是几何检查项自己的检查
（`qa.wire_findings`）。报告包含每个画法决定、交叉位置、标签和电源轨集合、带检查项结果的可读性指标、结构审计，
以及一份 `layout`，`compare_netlist` 用其网络策略核对标签和电源轨名字。

`name_run_steps` 校验声明的逻辑网络和有限的正数字号；它不解码、不缩短名字，不解析变量，也不选字号。栅格为 1.27 mm；
局部网络名字号默认 1.0 mm，与 Reference/Value 字段的默认值无关。摆放前显式预留可以避免之后因长度不足被拒，但长度足够只是空间预算。
器件、文字、外来导线、交汇点、页边界和 KiCad 字形覆盖仍需不变的严格构建和 KiCad 检查。这个查询不给编码/标记/CJK/变量文字、
外部字体或镜像字形任何新的资格。保留它们已有的来源和覆盖边界。

对一个声明的局部网络 `node`，一段串联可以这样规划：

```python
font = 1.0
gap = max(existing_gap, sheet.name_run_steps(node, font))
sheet.series(start_pin, [support_ref], toward, gap=gap)
sheet.name(node, font=font)
```

`start_pin` 必须确实在 `node` 上；多器件链中后面每一段的网络可能不同，各需自己的预算。同一查询也可以在连那个本引脚出线之前显式预算
`stub(pin, max(existing_length, ...))`。它不移动已有锚点，也不保证整个第一次构建就通过。

多页工程保留一份整板设计网表（见 [requirements-to-intent.md](requirements-to-intent.md)），用 `schematic_layout.pages.page_intents(board, rails=...)` 拆分：
每页得到自己的器件、每个网络在本页的部分、本页的 NC 引脚和 `external` 网络（在其他页也有引脚、且不是电源轨的网络）。
每页用自己的 `power_ref_start` 构建。重画时，写出前恢复基线身份（符号属性、UUID、引脚 UUID、实例路径、页 UUID、标题栏）。
用 `schematic_layout.root.Root` 组装根图：

```python
from schematic_layout.root import Root

r = Root("PD100_R5", date="2026-10-23", rev="R5")          # paper defaults to A4
r.page("02_Input", input_root, (25.4, 50.8), note="交流 / EMI / 整流")
r.page("03_PFC", pfc_root, (119.38, 50.8))
...                                                         # the other pages
r.flow("RECT", "02_Input", "03_PFC")                        # same row: straight, arrow at 03_PFC
r.flow("FB/FAULT", "07_PD", "05_Bias", kind="signal", via=[(345.44, 223.52), (157.48, 223.52)])
r.isolation(x=302.26)                                       # straight line labelled 隔离
r.write(out_dir, libraries={"PD100": "PD100.kicad_sym"})
```

`page` 接受 `Sheet.build` 返回的根对象（或 `.kicad_sch` 路径），按添加顺序从 2 开始给页编号。没有 `via` 的流向线要求两个页块在同一行或同一列带；
`via` 点给出一条正交路线，首末两段笔直地离开和进入页块。流向线名字放在最长一段旁；`label_at` 可移动它。
`write` 把每个子页符号的实例路径改写到根工程，把封面、各页、`.kicad_pro` 和 `sym-lib-table` 写入一个新目录；
封面文字压在线上或系统框图审计不通过时报错。然后用整板设计网表对根图运行 `scripts/verify_schematic.py`。
充电器重画（该工程中的 `design/v0.2.5-recipes/scripts/redraw.py`）是用这种方式画九张层次页的实例。

KiCad 标签样式（在 KiCad 10.0.6 上经渲染核实）：全局标签在 0/`right` 时向左延伸，180/`left` 向右，90/`left` 向上，270/`right` 向下；
局部标签用 0/`left bottom`、180/`right bottom`、90/`left bottom`、270/`right bottom`，KiCad 会把文字画成可读的方向（水平导线上方、竖直导线左侧）。

## `build()` 的硬拒绝

- 未摆放的器件；离栅或重合的端子（来自 `make_root`）。
- 斜线；导线压过另一网络的端子；不同网络相接或重叠（干净的垂直交叉允许，但会报告）。
- 导线穿过器件本体（引脚自身的向外出线不算穿过）、距页边不足 5 mm 或进入标题栏：与几何检查项对写出的导线运行的同一个 `qa.wire_findings` 检查。
- 未连线的引脚；一个网络画成分开的几段，除非每段都带它的标签或电源轨符号。
- 碰撞的电源轨符号、标签或网络名；Reference/Value 没有空位。

典型的修法：加长 `gap` 或短线、改变画法方向、移动或重新定向锚点、把拥挤的功能块拆成几行、反转链的顺序。

电源轨摆放被拒时保留其网络/锚点前缀，并为第一个失败的 `body` 或 `Value` 包络附加 `diagnostic=` JSON。它指出实际的外来导线段、
障碍的位号/引脚/注释或预留区序号、之前的电源轨请求和页边。这些是构图定位线索和保守的包络检查，不是 KiCad 对象 UUID、墨迹测量或电气短路发现。
按 O8 使用它们；它们既不移动电源轨，也不豁免原来的拒绝。单凭坐标不能确立引脚归属。

相距 7.62 mm 的两个引脚不能都向下挂并联支路：把一条支路折向上，或让下方引脚的走线比上方的短。除非方案声明了那个边界，
从不用标签代替失败的导线。

## 实例

`tests/fixtures/drawing/recipe_board.py` 在 A4 上画了一个 12 V 转 5 V 的 buck、一个带指示灯的 3.3 V LDO 和两条 USB ESD 通道
（22 个器件，0 处交叉，11 个拐弯）：

```python
s = Sheet(INTENT, rails={'GND': 'power:GND', '+5V': 'power:+5V', '+3V3': 'power:+3V3'},
          external=['MCU_DP', 'MCU_DN', 'USB_VBUS'])
s.place('J1', (20.32, 50.8)); s.power('J1.2')
s.series('J1.1', ['F1', 'D1'], RIGHT, gap=3)            # input chain
vin = s.bank('D1.1', ['C1', 'C2'], RIGHT)               # input bank, one return
s.put('U1', '1', add(vin, RIGHT, 12), RIGHT); s.wire(vin, 'U1.1')
sw = s.stub('U1.2', 3); s.shunt(sw, 'D2', DOWN)          # catch diode at SW
out = s.bank(s.series(sw, ['L1'], RIGHT, gap=6)[-1], ['C3', 'C4'], RIGHT)
rail = s.wire(out, add(out, RIGHT, 3)); s.power(rail)   # declared +5V symbol
r1 = s.series(rail, ['R1'], RIGHT, gap=3)[-1]            # upper divider leg
tap = s.wire(r1, add(r1, RIGHT, 2)); s.shunt(tap, 'R2', DOWN)
fb = s.stub('U1.4', 2); s.connect(fb, tap, y=fb[1] - 10.16)   # FB over the top
```

`draw(bad=True)` 是反例：同一网表，反馈导线从 +5 V 主干穿过，LED 反向画成 U 形回头。检查项点名交叉（`+5V`/`FB`）和曲折的连接
（`D3.2`、`R3.2`）；结构审计点名 D3：它的角色是并联支路却被手工摆放。

## 生成脚本随交付保存

把图页脚本（设计网表推导、画法重画、组装）存在每个交付版本目录里，放在 KiCad 工程旁。下一次电气改版只从上一版的设计网表加这些脚本
重新生成改动过的页面；交付不带生成脚本就只能手改可读的页面，而本流程禁止手改。整理目录时，只要后续版本仍从某一版派生，就不得删除该版的生成脚本。

## 限制

- 结构由 agent 选择；这里没有任何东西识别拓扑。
- 只支持单单元符号。按功能分组引脚的表示用符号需要自己的、经核实的物理引脚映射（见 symbol-and-peripheral-contracts.md）。
- 同网同功能多脚用 KiCad 叠脚编号（`[17,18]`）画成一个引脚：场景把它展开成同一点上的各物理脚，`Sheet` 用任一物理引脚号（`U1.17`）引用，
  连一次即全连；不要再把几个可见引脚叠在同一点（引脚号叠印，符号完整性记 `overprinted_pin_numbers`），电源脚也不要做成隐藏副本。
  设计网表仍逐物理脚写，漏写的同点脚用 `scripts/expand_stacked_pins.py --write` 补（KiCad 官方库的“可见脚 + 同点隐藏 passive 副本”同样适用）。
- 每页一个 `Sheet`。层次工程从基线页复制每个符号的工程实例路径和 UUID，因为重画必须保留它们。
- `check_scene` 接受引脚自身笔直向外、穿过伸出其端点的图形的出线（LED 箭头、磁件圆弧、热敏电阻标记）；其他穿过本体框的导线仍会报告。
- 文字宽度是估计；KiCad 渲染审阅仍是必需的。
