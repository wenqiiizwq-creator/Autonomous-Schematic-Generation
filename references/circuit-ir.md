# 结构化电路与自动布局（Circuit IR v2）

用于从已确认电路创建新图。`build_circuit.py` 将模块化电路编译为逐脚设计网表，
按真实符号、引脚出线区和字段尺寸自动放置，再调用避障布线和 KiCad 验证。
运行时只需 Python 3.10+、KiCad CLI 与符号库；不依赖上游仓库或在线服务。
自动放置与避障布线只用于固定夹具与草稿；交付页一律按 SKILL.md 任务 3.2 用 recipes 画，不由 MST/A* 出可读页面。

## 从两个项目提取的内容

| 来源 | 提取机制 | 在本 skill 中的实现 |
| --- | --- | --- |
| SKiDL `Circuit/Part/Pin/Net` | 电路是器件与真实引脚构成的连接图，图面属性是另一个层次 | `circuit_ir.py` 编译器；真实库引脚解析；独立 presentation JSON |
| SKiDL `Node`、`@subcircuit`、`tag` | 子电路复用；实例路径和稳定标签；父子接口 | `modules/root/instances/bindings`；稳定 component ID、明确 reference map 和 UUID |
| SKiDL `generate_schematic` | 按功能分块、放置布线、有限重试 | 按块选模板，测量占用，拼入允许纸张；3 次有限扩距重排并保留失败记录 |
| circuit-synth 连接感知放置 | 使用已知连接组织器件 | `functional` 按连接遍历，高扇出网络不支配顺序；外加本体/字段/出线区硬占用 |

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
  对应只可引用父模块已声明的网络，端口必须全部且只对应一次。拒绝递归定义。
- 模块 `ports` 列出外部可连接的本地网络名；未导出的网络按实例路径隔离，
  例如 `filter_a__OUT` 和 `filter_b__OUT`。同名并非同一网络；限定名碰撞直接失败。
- 模块 `parameters` 定义允许的参数及默认值。值通过 `{"param":"resistance"}`
  引用；只做数据替换，不执行表达式、不推算电气参数，未知参数报错。
- `pins` 使用本模块的 `component_id.真实引脚号`。也可使用
  `{"component":"amp","pin_name":"V+"}`，按真实库解析；重名脚必须改用
  实际号码或明确 `"all":true`。编译记录保留选择器到物理引脚的映射。
- 每个真实物理引脚必须恰好在一个网络或 `no_connect` 中。遗漏不会补 NC，
  模板不会添加 PWR_FLAG、改变引脚类型或猜测接线。
- 组件必填 `id/lib_id/value/footprint`。草图可明确填写空 footprint；它不是
  已完成封装选型。可选 `mpn/datasheet/dnp/fields/ratings/evidence/role`。
  `fields/ratings` 保存采购或额定值；写入隐藏 KiCad 属性，避免长 MPN 堆在 Value。
  所有可见 Value 保持原值，不截断或用简化值替换电气数据。
- `symbol_sha256` 可锁定解析后的实际符号。复制 `compiled.json` 中的值；
  换库/符号内容改变会失败。完整库文件 hash 也记录在每次构建中。
- 库中多个单元自动展开为 `U1:1/U1:2/U1:3` 图形视图，同一物理器件仍是 U1。
  全部单元都必须有位置。支持已覆盖的可见独立脚单元；重复/叠加编号、隐式
  隐藏脚仍拒绝。LM358 只含电源脚的独立单元用真实内部引脚坐标形成保守包络。
- `class/constraints/evidence` 等电气依据保存在编译记录，电气审查仍为 PENDING，不会因属性齐全变成 PASS。

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
| `rc_filter` | input, series, shunt, output | 两组重复 RC、参数变化、KiCad 逐脚验证 |
| `divider` | input, upper, lower, output | 角色位置模板；须对目标器件跑 KiCad 逐脚验证 |
| `capacitor_bank` | capacitor（其他角色按序排入阵列） | 12 只长 Value 电容、额定值、MPN、DNP 回读 |
| `ldo` | input, input_cap, regulator, output_cap, output, control, feedback | 角色模板；不构成某款 LDO 的电气设计验证 |
| `buck_async` | input, input_cap, regulator, diode, inductor, output_cap, output, bootstrap, feedback, compensation, control | 角色位置模板；不是通用 Buck 电路生成器 |
| `integrated_power` | input, input_cap, regulator, output_cap, output, feedback, control | 不强加外部电感/开关节点 |
| `functional`（默认） | 任意功能角色 | 连接遍历组织、真实边界预算；LM358 三单元 KiCad 验证 |

`orientations` 以物理位号或多单元 view key 指定 rotation/mirror；不需给
绝对坐标。多个同角色器件分配不同格位，列宽/行高由真实总占用决定。
模块有独立标题和留白，按可用边缘位置拼页；标题栏始终是禁放区。
默认尝试 A4、A3，也可明确限制纸张。布线/字段失败最多重排 3 次，每次
扩大间距 40%，上限可设 1–5；从不把失败的连线自动改为标签。
网络 `mode/rail_y/label/priority` 沿用 [低层后端格式](schematic-generation.md)。

当前图面模式 `pack` 将逻辑模块排入**一张 KiCad 图纸**，保留完整模块路径与
端口注册表。尚不生成 KiCad 层次 sheet/跨页端口或自动分页；放不下会失败，
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
每次 attempt 的布局/失败诊断、KiCad 工程及 ERC/XML/PDF/verification。
KiCad 验证还自动执行内部引脚与符号图形衔接检查，并输出 `native/symbol-integrity.json`。
可用 `--reference-contract path/to/contract.json` 将资料、封装引脚及外围事实纳入通过条件；
格式与边界见 [符号与外围约束](symbol-and-peripheral-contracts.md)。未提供记录不代表资料已核验。
引脚网表之外，还回读 Value、Footprint、MPN、额定值、自定义字段、DNP、单元
数量和全部物理引脚（含 NC）。精确字形/引脚名称与编号仍需 KiCad 全页及局部图面审阅。

```bash
python3 scripts/build_circuit.py revised.circuit.json presentation.json \
  --baseline output/dual-filter-01 --lock-block filter_a \
  --output-dir output/dual-filter-02
```

基线必须是本构建器已通过自动验证的结果，工程 ID 和源文件 hash 一致。
锁定模块电气内容或库脚表改变即失败；保留其位置。锁定只保证电气内容不变，
图面每版都按本版 PDF 重新看图，不因锁定而免看。输出 `electrical-diff.json`。这提供新目录中的**受保护再生成**，并非任意已有
KiCad 工程的原位增量编辑；其他模块加入后若无法同时满足锁定和几何约束，
必须调整候选或换合适 writer，不能移动锁定模块来取得通过。

开发验证：`python3 -m unittest discover -s tests -v`。所有示例均是软件验证夹具，
`AUTOMATED_PASS` 不能代替目标电路的电气及 KiCad 图面审查。
