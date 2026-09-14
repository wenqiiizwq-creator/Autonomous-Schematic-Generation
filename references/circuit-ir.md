# 结构化电路与自动布局（Circuit IR v2）

用于从已确认电路创建新图。`build_circuit.py` 将模块化电路编译为逐脚意图，
按真实符号、引脚出线区和字段尺寸自动放置，再调用避障布线和原生验证。
运行时只需 Python 3.10+、KiCad CLI 与符号库；不依赖上游仓库或在线服务。

## 从两个项目提取的内容

| 来源 | 提取机制 | 在本 skill 中的实现 |
| --- | --- | --- |
| SKiDL `Circuit/Part/Pin/Net` | 电路是器件与真实引脚构成的连接图，图面属性是另一个层次 | `circuit_ir.py` 编译器；真实库引脚解析；独立 presentation JSON |
| SKiDL `Node`、`@subcircuit`、`tag` | 子电路复用；实例路径和稳定标签；父子接口 | `modules/root/instances/bindings`；稳定 component ID、明确 reference map 和 UUID |
| SKiDL `Bus/Interface` | 有序网络集合及命名接口 | 模块端口和有序 scalar bus；编译记录保持每一位的网络身份 |
| SKiDL `generate_schematic` | 按功能分块、放置布线、有限重试 | 按块选模板，测量占用，拼入允许纸张；3 次有限扩距重排并保留失败记录 |
| circuit-synth `Component.to_dict`、`NetlistExporter.to_dict` | 器件字典、引脚号/名称/类型、网络连接、递归子电路、属性元数据 | `import_circuit_synth.py` 导入；`importers.py` 适配两种已核实的 net 形式 |
| circuit-synth 连接感知放置 | 使用已知连接组织器件 | `functional` 按连接遍历，高扇出网络不支配顺序；外加本体/字段/出线区硬占用 |

精确源文件及 commit 见 [upstream-sources.json](upstream-sources.json)。
SKiDL 对象桥读取已建立的真实对象；circuit-synth JSON 不区分局部/外部网络，
同名网络跨子电路出现时必须明确声明共享或独立，不能自动合并。
没有移植 SKiDL 的自动标签降级/ERC 修正循环，也没有采用隐式重新编号。

## 电气输入

完整可运行样例：`tests/fixtures/generation/dual_filter.circuit.json`。
最小形式如下（测试用串联电阻，不是完整硬件设计）：

```json
{
  "schema_version": 2,
  "design_id": "series_example",
  "references": {"first":"R1", "second":"R2"},
  "root": {
    "components": [
      {"id":"first", "lib_id":"Device:R", "value":"1k", "footprint":""},
      {"id":"second", "lib_id":"Device:R", "value":"2k", "footprint":""}
    ],
    "nets": [{"name":"MID", "pins":["first.2", "second.1"]}],
    "no_connect": ["first.1", "second.2"]
  }
}
```

- `design_id` 是持久工程标识。保持不变时，仅修改另一模块的参数不会使
  全图 UUID 随意改变。`references` 必须精确覆盖所有 `实例路径/组件id`；
  根组件直接用 id。禁止重复物理位号和隐式自动重编号。
- `modules` 是可复用定义字典；`root` 与模块具有相同结构。实例格式：
  `{"id":"filter_a","module":"rc","bindings":{"IN":"INPUT_A","OUT":"OUTPUT_A","GND":"GND"},"parameters":{"resistance":"2k"}}`。
  绑定只可引用父模块已声明的网络，端口必须全部且只绑定一次。拒绝递归定义。
- 模块 `ports` 列出外部可连接的本地网络名；未导出的网络按实例路径隔离，
  例如 `filter_a__OUT` 和 `filter_b__OUT`。同名并非同一网络；限定名碰撞直接失败。
- 模块 `parameters` 定义允许的参数及默认值。值通过 `{"param":"resistance"}`
  引用；只做数据替换，不执行表达式、不推算电气参数，未知参数报错。
- `pins` 使用本模块的 `component_id.真实脚号`。也可使用
  `{"component":"amp","pin_name":"V+"}`，按真实库解析；重名脚必须改用
  实际号码或明确 `"all":true`。编译记录保留选择器到物理引脚的映射。
- 每个真实物理引脚必须恰好在一个网络或 `no_connect` 中。遗漏不会补 NC，
  模板不会添加 PWR_FLAG、改变引脚类型或猜测接线。
- 组件必填 `id/lib_id/value/footprint`。草图可明确填写空 footprint；它不是
  已完成封装选型。可选 `mpn/datasheet/dnp/fields/ratings/evidence/role`。
  `fields/ratings` 保存采购或额定值；写入隐藏原生属性，避免长 MPN 堆在 Value。
  所有可见 Value 保持原值，不截断或用简化值替换电气数据。
- `symbol_sha256` 可锁定解析后的实际符号。复制 `compiled.json` 中的值；
  换库/符号内容改变会失败。完整库文件 hash 也记录在每次构建中。
- 库中多个单元自动展开为 `U1:1/U1:2/U1:3` 图形视图，同一物理器件仍是 U1。
  全部单元都必须有位置。支持已覆盖的可见独立脚单元；重复/叠加编号、隐式
  隐藏脚仍拒绝。LM358 只含电源脚的独立单元用真实内部引脚坐标形成保守包络。
- `buses:[{"name":"DATA","members":["DATA0","DATA1"]}]` 保存位序与标量网络。
  它不会自动生成 KiCad 图形 bus/entry。`class/constraints/evidence` 等电气
  依据保存在编译记录，电气审查仍为 PENDING，不会因属性齐全变成 PASS。

ID/网络名使用字母、数字、`_+-`；层次分隔符由编译器管理。复杂外部名称需
显式映射并保留来源。未知结构字段报错，不静默丢弃拼写错误。

## 图面输入与自动放置

`presentation.json` 示例：

```json
{
  "schema_version": 2,
  "papers": ["A4", "A3"],
  "grid_mm": 1.27,
  "gap_mm": 12.7,
  "max_attempts": 3,
  "blocks": {"filter_a":{"template":"rc_filter","orientations":{"J1":{"mirror":"y"}}}},
  "nets": {"GND":{"mode":"labels"}, "INPUT_A":{"label":true}}
}
```

`blocks` 键是组件所属的逻辑实例路径，根组件使用 `root`。同一模块实例
中的组件按 `role` 分配模板位置；位号、引脚和连接不随角色改变。

| template | 支持角色 | 验证范围 |
| --- | --- | --- |
| `rc_filter` | input, series, shunt, output | 两组重复 RC、参数变化、原生逐脚验证 |
| `divider` | input, upper, lower, output | 角色位置模板；须对目标器件跑完整原生回归 |
| `capacitor_bank` | capacitor | 12 只长 Value 电容、额定值、MPN、DNP 回读 |
| `ldo` | input, input_cap, regulator, output_cap, output, control, feedback | 角色模板；不构成某款 LDO 的电气设计验证 |
| `buck_async` | input, input_cap, regulator, diode, inductor, output_cap, output, bootstrap, feedback, compensation, control | 必须有 regulator/inductor/diode；不是通用 Buck 电路生成器 |
| `integrated_power` | input, input_cap, regulator, output_cap, output, feedback, control | 不强加外部电感/开关节点 |
| `functional`（默认） | 任意功能角色 | 连接遍历组织、真实边界预算；LM358 三单元原生验证 |

`orientations` 以物理位号或多单元 view key 指定 rotation/mirror；不需给
绝对坐标。多个同角色器件分配不同格位，列宽/行高由真实总占用决定。
模块有独立标题和留白，按可用边缘位置拼页；标题栏始终是禁放区。
默认尝试 A4、A3，也可明确限制纸张。布线/字段失败最多重排 3 次，每次
扩大间距 40%，上限可设 1–5；从不把失败的连线自动改为标签。
网络 `mode/rail_y/label/priority` 沿用 [低层后端格式](schematic-generation.md)。

当前图面模式 `pack` 将逻辑模块排入**一张原生图纸**，保留完整模块路径与
端口注册表。尚不生成原生层次 sheet/跨页端口或自动分页；放不下会失败，
不会裁剪、丢模块或悄悄拉平一个现有多页工程。复杂 SoC/总线图需专用 writer。

## 命令和证据

```bash
python3 scripts/build_circuit.py \
  tests/fixtures/generation/dual_filter.circuit.json \
  tests/fixtures/generation/dual_filter.presentation.json \
  --output-dir output/dual-filter-01
```

输出 `circuit.json/presentation.json` 原输入、`compiled.json` 层次/端口/
引脚解析/源库 hash、`electrical_intent.json`、`layout_plan.json`、`planning.json`、
每次 attempt 的布局/失败诊断、原生工程及 ERC/XML/PDF/verification。
引脚网表之外，还回读 Value、Footprint、MPN、额定值、自定义字段、DNP、单元
数量和全部物理引脚（含 NC）。精确字形/引脚名称与编号仍需原生全页及局部目检。

```bash
python3 scripts/build_circuit.py revised.circuit.json presentation.json \
  --baseline output/dual-filter-01 --lock-block filter_a \
  --output-dir output/dual-filter-02
```

基线必须是本构建器已通过自动验证的结果，工程 ID 和源文件 hash 一致。
锁定模块电气内容、库脚表或模板配置改变即失败。保留其位置，重新生成后
逐一比较符号、字段、导线、标签、注释及 UUID；有任何漂移仍失败。
输出 `electrical-diff.json`。这提供新目录中的**受保护再生成**，并非任意已有
KiCad 工程的原位增量编辑；其他模块加入后若无法同时满足锁定和几何约束，
必须调整候选或换合适 writer，不能移动锁定模块来取得通过。

## 两种上游入口

```bash
python3 scripts/import_circuit_synth.py exported.json --design-id imported \
  --shared-net GND --local-net SENSE --output-dir output/import-01
```

只支持已核实的 `nets[name]=[connection]` 和 `nets[name]={nodes:[connection],...}`。
缺 lib_id/真实脚号拒绝导入；遗漏 NC 在编译时仍失败。重复名字须声明 shared
或 local，混合共享范围应编辑 IR 的显式端口绑定。原坐标、注释和其他源数据
保存在 `import-audit.json`，不冒充已采用的布局或已验证的电气约束。

对可信且已构建的 SKiDL Circuit，在其 Python 环境调用：

```python
from schematic_layout.importers import skidl_to_ir
document = skidl_to_ir(circuit, "my_design", {"R1":"Device:R", "R2":"Device:R"})
# 把 document 保存为 JSON，再交给 build_circuit.py。
```

将本 skill 的 `scripts` 目录加入 Python import 路径。桥接函数读取真实
Circuit/Node/Part/Net 对象、实际连接对象及 NC，不执行传入源码，不改写源电路。
必须明确提供每个实体器件的符号映射；SKiDL 的临时/备份库名称不能替代真实
KiCad 库身份。Node/Part tag 保持实例与器件稳定，重复 tag/name 直接拒绝。

开发验证：`python3 -m unittest discover -s tests -v`；可选的
`tests/probe_structured_upstream.py` 要求固定 SKiDL 源码安装在隔离环境中，
实际验证其对象提取，以及 circuit-synth 原始 `to_dict` 方法的两种输出形式。
该探针未运行两个上游的整套布局/布线系统。所有示例均是软件验证夹具，
`AUTOMATED_PASS` 不能代替目标电路的电气及原生图面审查。
