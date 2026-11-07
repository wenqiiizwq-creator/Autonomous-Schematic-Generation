# 确定性的单页生成

把已确定的电路画成新的 KiCad 图时阅读。模块化的电路输入和自动摆放用 [Circuit IR v2](circuit-ir.md)。
这个低层接口接受复核过的电路和显式的摆放；脚本解析真实的符号几何、放置可见字段、走线并检查。
它们不选 IC、不推断缺失的连接，也不优化任意的电路板。
这是低层确定性后端，只用于导入、固定夹具与草稿；交付页一律按 SKILL.md 任务 3.2 用 recipes 画，不由 MST/A* 出可读页面。

## 支持的范围

- 运行时只需 Python 3.10+ 标准库；需要已安装的 KiCad CLI 和官方/自定义符号库。KiCad 版本见 README。
- 单张横向 ISO A 图纸，使用真实的缓存符号、矩形/折线/圆/圆弧、正交旋转和 x/y 镜像。
  符号继承从选定的 `.kicad_sym` 库解析。多单元器件需要显式完整的 `units` 列表（如 `[1,2,3]`），
  摆放的键为 `U1:1`、`U1:2`、`U1:3`。网络中的物理引脚仍写 `U1.编号`。
  物理引脚只在公共单元 0 中的单视图符号使用隐含的单元 1；其缓存的单元编号不变。这只适用于默认本体样式 0/1 中的公共物理引脚，
  不适用于只有图形或只有替代样式的符号。仍需要完整的物理引脚设计网表。
- 物理引脚 ID `位号.编号` 与有名字的电气网络分开。每个真实引脚必须恰好出现一次，在某个网络或 `no_connect` 中。
- 显式摆放、可选的水平电源轨、可见的局部导线和有意的远程局部标签。走线器遇到异网交叉就拒绝，不尝试给一般的非平面原理图走线。
- 同一网络上同一符号的重合端子（包括支持的隐藏无源副本）在 KiCad 导出中保留各自的物理引脚号。冲突的分配和不支持的隐藏/堆叠排列 FAIL。
- 完整的层次写出、不支持的堆叠/隐藏引脚、没有正常 KiCad 网表器件身份的电源/虚拟符号、图形总线写出和任意的原位编辑需要另外的写出器。
  不要为了让真实符号通过这个有界后端而修改它。已有的层次工程用 [existing-project-redraw.md](existing-project-redraw.md)
  中分阶段、按工程定制的做法，不把单页 CLI 当作自动的层次编辑器。

## 输入：设计网表与布图分开

可运行的例子是 `tests/fixtures/generation/rc_filter.intent.json` 和 `tests/fixtures/generation/rc_filter.layout.json`。
它们的值是测试样例，不是合格的硬件设计。每次运行用新的输出目录。

`electrical_intent.json`：

```json
{
  "schema_version": 1,
  "title": "Reviewed circuit block",
  "revision": "draft",
  "components": [
    {"ref":"R1","lib_id":"Device:R","value":"10k","footprint":"Resistor_SMD:R_0603_1608Metric","mpn":"actual selected part","datasheet":"source URL"},
    {"ref":"R2","lib_id":"Device:R","value":"10k","footprint":"Resistor_SMD:R_0603_1608Metric"}
  ],
  "nets": [{"name":"DIV_MID","pins":["R1.2","R2.1"]}],
  "no_connect": ["R1.1","R2.2"]
}
```

这个语法例子只是两只互连的测试电阻，不是实际的分压设计。真实电路要包含所有必需的电源轨和器件。
器件可选的 `dnp` 会保留到原理图。数据手册公式、额定值和工程决定属于随附的设计证据；生成器不会把提供的 URL 或值变成电气核实。

`layout_plan.json`：

```json
{
  "schema_version": 1,
  "paper": "A4",
  "grid_mm": 1.27,
  "placements": {
    "R1":{"at":[50.8,50.8],"rotation":0},
    "R2":{"at":[50.8,76.2],"rotation":0}
  },
  "nets": {"DIV_MID":{"label":true}}
}
```

坐标单位为毫米，X 向右、Y 向下。每个器件有 `at`、可选的 `rotation`（0/90/180/270）、可选的 `mirror`（`x` 或 `y`）。
摆放条目必须恰好覆盖所有器件位号。不要把库内的引脚坐标当作图纸坐标：后端会旋转、镜像并翻转 Y 轴，
再按选定栅格核对得到的引脚端点，不做吸附。未知的布图/摆放/走线键会被拒绝，以暴露拼写错误。
隐藏的 `fields`/`ratings`、MPN、Datasheet 和 DNP 会保留并在 KiCad XML 中比较；多单元的引脚覆盖也会核对。
可选的 `design_id` 和器件的 `stable_id` 把 UUID 绑定到稳定的身份，而不是随值改变。
KiCad 字段以居中锚点写出，避免随镜像变化的单侧对齐；局部标签用核实过的水平 0° 样式。

每个网络的布图选项：

| 键 | 含义 |
| --- | --- |
| `mode: "wire"` | 默认。MST 配对 + 有界的正交走线；失败就是失败。 |
| `mode: "labels"` | 有意的远程连接。每个引脚得到一段经核对的向外短线和相同的局部标签。标签拥挤时可能失败。 |
| `rail_y: number` | 固定的水平电源轨；把这个网络的引脚接到轨上。仅用于 wire 模式。 |
| `label: true` | 在走线成功的导线上加一个可见的网络标签。 |
| `priority: number` | 数值小的先走。允许一次反转网络顺序的重试。 |

可选的 `reserved` 是 `[xmin,ymin,xmax,ymax]` 禁布区列表。默认预留右下角 115×40 mm 区域，页边距 5 mm。
自定义图框要显式映射它实际的标题/注释禁布区，并核对 KiCad 渲染。可选的 `max_route_states` 默认为每对 150000。
除这个后端的禁布区外，还要核对 KiCad 实际的打印图框；模型 5 mm 的边距不能确立与 KiCad 10 mm 图框的间距。
优先用 KiCad 的 1.27 mm 连接栅格。更细的几何栅格（如 0.635 mm）本身不能消除 KiCad 的离栅发现。
按 KiCad ERC 核对变换后的引脚端点；从不悄悄移动电气引脚让检查通过。

## 命令与输出

在技能/仓库根目录运行；在别处运行时换成它的绝对路径：

```bash
python3 scripts/generate_schematic.py \
  tests/fixtures/generation/rc_filter.intent.json \
  tests/fixtures/generation/rc_filter.layout.json \
  --output-dir output/rc-filter-run-01 --name rc_filter

python3 scripts/check_schematic_geometry.py \
  output/rc-filter-run-01/rc_filter.kicad_sch \
  --layout output/rc-filter-run-01/layout_plan.json \
  --output output/rc-filter-run-01/geometry-recheck.json
```

自动发现不够时用 `--symbol-dir /path/to/symbols`（可重复）或 `--kicad-cli /path/to/kicad-cli`。新的输出工程得到一份本地
`sym-lib-table`，绑定实际读取的库；不碰全局 KiCad 配置。这些绝对库路径换机器后需要重新绑定。

- 复制的设计网表/布图输入可以复现失败。
- `generation.json` 记录输入/库哈希、解析出的引脚/字段、走线顺序/重试、导线/交汇点数量和几何发现。
- `.kicad_sch`、`.kicad_pro`、`sym-lib-table` 构成可编辑的 KiCad 工程。
- `native/erc.json`、`native/netlist.xml`、`native/schematic.pdf` 是 KiCad 的输出。
- `native/symbol-integrity.json` 核对实际的引脚到本体线条和物理引脚覆盖。它是必需的 KiCad 检查项，自定义符号也包括在内。
- 可选的 `--reference-contract path/to/contract.json` 把来源/引脚/外围电路事实加为必需的检查项，并写出 `native/reference-contract.json`。
  格式、覆盖范围和限制见 [symbol-and-peripheral-contracts.md](symbol-and-peripheral-contracts.md)。
- `verification.json` 记录确切的原理图 SHA-256、CLI 版本/命令和各检查项结果。走线/格式失败保留原输入文件和一份错误报告；
  从不覆盖已有的输出目录。

退出码 0 / `AUTOMATED_PASS` 表示在其声明的模型内几何、符号完整性、KiCad ERC、精确的网表分区以及提供的外围电路核对表都通过，
并生成了 PDF。它**不是最终的设计验收**。`native_render_review` 和 `datasheet_review` 保持 `PENDING`，直到另做有证据的审阅。

## 几何覆盖与审阅

检查器独立读取序列化的 KiCad 文件。它核对本体间距、穿过本体的导线、Reference/Value/标签（包括同一归属的碰撞）、
文字与引脚引线/导线、图框/标题禁布区、离栅的电气锚点、悬空的标签/NC 标记/交汇点、孤立端点、重复导线、
未打点的交叉，以及提供了引脚设计网表时的跨网接触。

顶层注释折线只在显式的有限正线宽、默认线型、有限非零线段且无填充（省略或 `none`）时覆盖。
检查沿每段墨迹及半线宽圆头包络进行，不是轮廓的空内部或斜线的外接框。文字/本体和图框/标题碰撞是保守边界模型内的发现。
文字包络是保守估计：候选的墨迹/文字相交是要重画消除的 FAIL，不是声称 KiCad 字形相碰，也不是要人工分类的项目。
注释墨迹穿过电气导线或引脚引线也是要重画的 FAIL；它从不产生网络接触或锚点。未知的属性、填充、虚线样式、
隐含/零线宽和格式错误的点保留覆盖缺口。层次图框和其他不支持的页图形是另外的缺口。

`PASS` 表示模型内没有发现。`FAIL` 是检测到的缺陷；`INSUFFICIENT` 是不支持的几何或缺少缓存符号。没有警告状态：
间距过近、未打点的交叉和注释重叠都是 ASG 通过重画修正的绘图缺陷。从不为了得到通过的报告而抹掉覆盖缺口。
引脚名/引脚号、自定义图形和确切的字体度量需要 KiCad 渲染。圆弧边界是保守的整圆外框。已有的旋转/镜像非居中字段和其他局部标签旋转
报告为覆盖缺口，因为这里没有模拟它们在 KiCad 中的对齐。合法的共享电气节点和导线拐角不需要装饰性的点。

把 KiCad PDF 渲染成 PNG，既看整页也看有内容的区域：

```bash
pdftoppm -scale-to 2200 -png -singlefile \
  output/rc-filter-run-01/native/schematic.pdf \
  output/rc-filter-run-01/native/schematic
```

电气计算和分析器发现分开审阅。图面审阅记录按确切的原理图哈希保存；一次干净的渲染不代表任意未来输入电路的结论。
用另一个写出器重画时，除设计网表外还要比较改动前后 KiCad XML 的分区和身份字段；不要把这个新工程生成器当作原位编辑器。

## 回归与维护

```bash
python3 -m unittest discover -s tests -v
python3 tests/probe_upstream.py --output output/upstream-probe.json
```

第一条命令只用标准库；KiCad/库不可用时，KiCad 相关测试会明确跳过。跳过的测试不是执行证据。
有 `pdftotext` 时，变换测试还核对 KiCad PDF 中 Value 的实际外框，检查竖排文字和镜像后侵入本体。
可选的第二条命令需要下载的两个 `upstream/` 仓库和支持 TypeScript 剥离的 Node；它只执行选定的纯源码模块。
运行时生成既不需要上游仓库也不需要 Node。每个新的真实失败都加一个最小测试样例，然后测试预期的可观察不变量和 KiCad 输出。
复用更多代码前先钉住改动的上游提交。

## 显式的图面字段与网络组

`generate_schematic.py` 和 `make_root` 在低层摆放 JSON 里接受可见字段位置（世界坐标，角度 0 或 90，字号至少 1 mm）：

```json
{"C1":{"at":[50.8,63.5],"fields":{
  "Reference":{"at":[54.61,63.5],"angle":90,"font_mm":1.016},
  "Value":{"at":[56.388,63.5],"angle":90,"font_mm":1.016}
}}}
```

显式字段在自动字段和走线之前预留；有碰撞就拒绝。这不给自动 v2 排布增加字段样式选择。

网络策略可以声明由真实 `位号.引脚` 端子组成的组。每个引脚恰好出现一次。组内局部连线，组间用真实网络名连接；
内部的组键不进入原理图。组对象还可以选 `rail_y`、`mode` 或 `priority`：

```json
{"VIN_5V":{"groups":[
  {"pins":["J1.1","C1.1","U1.12"],"rail_y":104.14},
  ["U1.19","C9.1"]
]}}
```

KiCad 导出的检查比较原来完整的网络分区和标签名。分组不改变 circuit IR，也不授权只用标签的回退。
