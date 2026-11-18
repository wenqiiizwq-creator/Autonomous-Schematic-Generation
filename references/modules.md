# 块设计、合并与网表导入

分块设计（[quick-design.md](quick-design.md) 的“分块设计”）用到的两种记录和合并命令，以及只给网表重画时的导入。

## architecture.json

```json
{"schema_version": 1,
 "domains": [{"name": "一次侧", "ground": "PGND"}, {"name": "二次侧", "ground": "GND"}],
 "blocks": [{"id": "PSU", "name": "隔离电源", "domain": "二次侧", "ref_range": [100, 199]}],
 "flows": [{"name": "VIN", "kind": "power", "from": "IN", "to": "PSU", "nets": ["VIN"]}]}
```

- **domains**：每个电压域写 `name`；有地网络的写 `ground`（地网络名），各块接这个域的地就用这个名字作端口。
- **blocks**：每个功能块写 `id`、`name`、所在电压域 `domain` 和位号编号段 `ref_range`（`[起, 止]`，本块器件位号的数字部分在段内，各块的段不重叠）。
- **flows**：每条跨块流向写一个名字，代表它承载的电源轨或信号。`kind` 取 `power` 或 `signal`；`nets` 写它承载的整板网络名（一条总线写多个），两端块的端口只能用这些名字。
- 块的边界放在少数几个参数就能说清的地方：两块之间要靠控制环、共用一颗芯片或多条模拟连线才能工作的，合成一块。

只给网表重画时没有这个文件，功能块划分由任务 C6.1 从网表定。

## blocks/<块>.json

```json
{"schema_version": 1, "block": "PSU",
 "components": [{"ref": "U101", "lib_id": "…", "value": "…", "mpn": "…", "datasheet": "…"}],
 "nets": {"VIN": ["U101.1", "C101.1"], "+3V3": ["U101.5", "C102.1"], "GND": ["U101.3", "C101.2", "C102.2"], "FB": ["U101.4", "R101.2"]},
 "ports": ["VIN", "+3V3", "GND"],
 "no_connect": ["U101.6"],
 "net_roles": {"+3V3": "power", "GND": "return", "FB": "signal"},
 "net_voltages": [{"net": "+3V3", "max": 3.45, "unit": "V", "source": "calc:C-OUT"}],
 "external_supply": [], "filtered_supply": []}
```

- 器件的写法与设计网表相同（见 [requirements-to-intent.md](requirements-to-intent.md) 第 5 节）；`fields.Circuit` 不用写，合并时写成块名。
- `ports` 是要和别的块接起来的网络，只能是与本块相连的流向的 `nets`，或电压域的 `ground`。不在 `ports` 里的是块内网络，不能用整板网络名，也不能与别的块的块内网络重名。
- 位号在本块的 `ref_range` 内。合并时不改号，重号报错。
- 本块网络的 `net_roles`、`net_voltages`（列表，每项 `{net, max, unit, source}`）、`high_voltage_nets` 跟着网络写，共享网络的标注各块写得要一致；
  `external_supply`、`filtered_supply`、`reviewed_circuit_supply` 写在 `pin`（或 `via`）所在的块。
- **BOARD.json**：整板核对者只差接口件（上拉、电平转换、隔直）时写的整板层块，格式相同，位号不受编号段限制，端口可用任何流向的网络名；可写 `header`（`revision`、`title` 等整板表头）。

`python3 scripts/blocks.py merge <设计目录>` 读 `record/blocks/` 和 `record/architecture.json`，按网络名合并，写出 `record/electrical-intent.json`。
块内网络重名、端口没有对端、位号重复、同一网络各块的角色或电压不一致都报错，由整板核对者改有关的块文件再合并。
`blocks.py roundtrip <整板网表> --plan <分页方案>` 把已有整板网表按分页方案的功能块拆开再合回去逐脚比对，只用来验证块格式。

## 只给网表重画

用 `import_netlist.py <netlist.xml> --out record/electrical-intent.json --source-schematic <根图> --library-dir 设计资料/symbols` 把 KiCad XML 网表转成设计网表，再照 [module-c6-schematic.md](module-c6-schematic.md) 画图。

- 源工程里内嵌的符号会抽成项目符号库，画图时用 `Sheet(dirs=[...])` 指向这个目录（`generate_schematic.py` 是 `--symbol-dir`）。
- 引脚号里带“.”的网表无法用“位号.引脚”表达，导入时会报 FAIL。
- 子页局部标签的网络名去掉页路径（`/09_CH12/IN_D1` 写成 `IN_D1`；两页同名时写成 `页_名字`），原名记在 `source_netlist.net_names`。重画可以自由分页，画图时按这些名字标注。
- 源工程的器件字段原样带入，包括器件性能字段。
- 网表里没有电源轨角色和网络电压，任务 C6.1 按需要补写。
