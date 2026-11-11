# 能力模块：关卡、交接文件与指纹

SKILL.md「架构」把 ASG 分成六个能力模块，P7 规定了模块契约。本页说明怎样落实：每个模块的关卡查什么、`architecture.json` 怎么写、`modules.json` 记什么。

## 关卡

`python3 scripts/check_module.py <模块> <设计目录>` 运行该模块的关卡，只查这个模块拥有的部分：

| 模块 | 关卡 |
|---|---|
| C1 | `audit_design_closure --module C1`：只查 `requirements.json`：每条需求有编号、条文和来源，澄清都已答复并写回，降额等级、准则范围已定；不需要设计网表 |
| C2 | `record/architecture.json`，格式见下节 |
| C3 | `check_scheme_criteria.py` 的方案记录、`selection.json` 的核心选型；再用 `block_circuits.py` 抽出块文件，核对它们与这两份工作记录一致；每个核心器件写了端口限值；接口定稿 `record/interfaces.json`（任务 C3.3）对 `architecture.json` 和块文件的端口限值成立；选定方案没有标典型电路、库里却有命中的，候选里要说明为什么不适用；不查分页方案，也不查留给 2.2 的数值 |
| C4 | 每个块设计对 `architecture.json` 的核对（端口、块内网络名、位号编号段）；`interfaces.json` 里本块这一头的接口参数齐全；把已写的块设计宽松合并（端口还没有对端不报错）后做 `audit_design_closure --module C4`：计算、工况、降额、引脚表、引脚处置、准则引用；`component-requirements.json`；块文件里留给 C4.2 的数值都已闭合（只读块文件，不读 C3 的工作记录）。`--block <块>` 只核一个块，不记指纹 |
| C5 | `electrical-intent.json` 与 `blocks.py merge` 的合并结果逐脚一致；整板设计闭合审计（不带 `--module`），包括需求追溯、网络电压、矩阵、接口约定、FMEA 与 EMC 端口矩阵 |
| C6 | 分页方案、图面审阅、`summary.json` 没有 FAIL 的绘图检查项；有块文件时，块文件里的选定方案与分页方案标注的典型电路一致（只读 C3 的产品 `block-circuits/`，不读它的工作记录） |

没有错误就是通过，待办（PENDING）不拦关卡。通过后，指纹写进 `record/modules.json`。

C4 每块写一个块设计 `record/blocks/<块>.json`，不写整板网表；C5 用 `blocks.py merge` 把它们合成 `electrical-intent.json` 再做闭合。

整板交付（`render_design_report.py`、`deliver.py`）仍然一次核对全部内容。

## architecture.json（任务 C2.1，模块 C2）

```json
{"schema_version": 1,
 "domains": [{"name": "一次侧", "ground": "PGND"}, {"name": "二次侧", "ground": "GND"}],
 "blocks": [{"id": "PSU", "name": "隔离电源", "domain": "二次侧", "ref_range": [100, 199],
             "inputs": ["VIN"], "outputs": ["+3V3"],
             "spec": {"text": "24 V 输入，3.3 V 1 A，隔离 1500 Vrms", "requirements": ["R1"]}}],
 "flows": [{"name": "VIN", "kind": "power", "from": "IN", "to": "PSU", "nets": ["VIN"],
            "params": {"voltage": "18～36 V", "current_max": "0.3 A"}}],
 "boundaries": [{"name": "电源隔离", "sides": ["一次侧", "二次侧"]}],
 "interfaces": [{"name": "电源端子", "block": "IN"}]}
```

- **domains**：每个电压域写 `name`；有地网络的写 `ground`（地网络名），各块接这个域的地就用这个名字作端口。
- **blocks**：每个功能块写 `id`、`name`、所在电压域 `domain`、`inputs`、`outputs`、块规格 `spec` 和位号编号段 `ref_range`（`[起, 止]`，本块器件位号的数字部分在段内，各块的段不重叠）。
  - `spec.text` 写输入、输出、功率与指标，只写“要什么”，不写拓扑。块内用反激还是正激、光耦还是数字隔离器由 C3 决定。
  - `spec.requirements` 引用 requirements.json 里的需求编号。
- **flows**：每条跨块流向写一个名字，代表它承载的电源轨或信号。`kind` 取 `power` 或 `signal`。`power` 流向连起来就是电源树。
  - `nets` 写它承载的整板网络名（一条总线写多个），两端块的端口只能用这些名字。
  - `params` 写接口参数的预算值，供 C3 选方案用；C4 用的是任务 C3.3 定稿的数（见下节）：电源轨写电压范围与最大电流，信号写电平、方向与驱动方式，模拟量写量程与源阻抗，差分对写差分阻抗。
- 块的边界放在少数几个参数就能说清的地方：两块之间要靠控制环、共用一颗芯片或多条模拟连线才能工作的，合成一块。
- **boundaries**：每条隔离边界写它分开的电压域（`sides`），每一侧都要有功能块。
- **interfaces**：对外接口写名字和所属功能块。

单独运行 C6 时没有这个文件，功能块划分由任务 C6.1 从网表定。

## interfaces.json（任务 C3.3，模块 C3）

任务 C3.3 是 C3 的最后一项：核心器件选定、块文件抽出后，把每条跨块流向的接口参数定成各块设计时要遵守的数。`architecture.json` 不动。

```json
{"schema_version": 1,
 "flows": [{"name": "+3V3→MCU",
            "provides": {"voltage": [3.2, 3.4], "current_max": 0.5},
            "accepts": {"voltage": [3.0, 3.6], "current_max": 0.2, "sequence": "先于 VDDA 上电", "source": "U201 手册 p.12"}},
           {"name": "PG",
            "provides": {"voh_min": 2.4, "vol_max": 0.4, "voh_max": 3.45, "drive": "push-pull"},
            "accepts": {"vih_min": 2.0, "vil_max": 0.8, "abs_max": 3.6, "source": "U201 手册 p.9"}},
           {"name": "ISENSE",
            "provides": {"level": "0～2.5 V，源阻抗 1 kΩ"},
            "accepts": {"level": "量程 0～3 V，输入阻抗 > 100 kΩ", "source": "U201 手册 p.31"}}]}
```

- 每条 `architecture.json` 的流向一行，用 `name` 对应。`provides` 是源块（`from`）要保证的范围，`accepts` 是负载块（`to`）能接受的范围。
- `accepts.source` 写数值的来源：核心器件手册页码，或写明沿用任务 C2.1 的预算。
- **电源轨**（`kind: power`）：两头都写 `voltage`（`[下限, 上限]`，V）和 `current_max`（A）；上电时序要求写 `sequence`。
  - 源端电压要落在负载接受的范围内；
  - `accepts` 的电压不能超出负载块核心器件在该网络上的端口限值（块文件的 `port_limits`）；
  - 同一个源块、同一组网络的几条流向是一条轨：`provides` 写得相同，电流能力不小于各负载 `current_max` 之和。
- **逻辑信号**：`provides` 写 `voh_min`、`vol_max`（可加 `voh_max`、`drive`），`accepts` 写 `vih_min`、`vil_max`（可加 `abs_max`）。输出高电平不低于输入门限（`drive` 为 `open-drain` 时不查），输出低电平不高于输入门限，输出最高不超过输入耐压。
- **模拟量、差分对**：两头各写 `level`（文字）。这类流向的相容性不做机械核对，关卡列为提示。
- 交集为空或电流超出源块的块规格时，先看能否回任务 C3.2 换核心器件解决；要改架构或块规格的回到任务 C2.1。两种都记 `returns`，不在这里凑数。
- C4 设计某一块时只看它自己这一头：作源块的看 `provides`，作负载的看 `accepts`。

## requirements.json（任务 C1.1，模块 C1）

```json
{"schema_version": 1,
 "evidence": [{"id": "E-REQ", "path": "需求/需求规格.md", "sha256": "<SHA256>", "locator": "§3"}],
 "requirements": [{"id": "R1", "text": "24 V 输入，输出 3.3 V 1 A，隔离 1500 Vrms", "evidence": ["E-REQ"]}],
 "clarifications": [],
 "derating": {"level": "II", "source": "req:R1"},
 "guideline_version": 1,
 "guideline_scope": {"library_version": "<版本>", "baseline": "industrial_telecom", "circuit_types": [], "device_kinds": [], "not_applicable": []}}
```

- **requirements**：每条写 `id`、可验收的 `text` 和来源 `evidence`（本文件 `evidence` 里的编号）；并入的澄清写 `clarifications`。不写设计决定。
- **clarifications**、**derating**、**guideline_scope**：字段见 [需求澄清](requirement-clarifications.md) 和 [设计待办记录](design-closure.md)。用户暂缓的澄清（`DEFERRED`）就是按建议条文设计的假设。
- 每条需求由哪些器件实现、状态、依赖哪些待办，是需求追溯，归 C5，写在 `design-closure.json` 的 `traceability`，用需求编号引用（见 [设计待办记录](design-closure.md)）。

## block-circuits/<块>.json（任务 C3.2，模块 C3）

C3 照旧手写工作记录 `scheme-criteria.json` 和 `selection.json`，每块方案和每个核心角色写 `block_id`（`architecture.json` 的 `blocks[].id`）。
每个核心角色的选定候选写 `port_limits`：它在本块各端口上的限值，每项写 `net`（与本块相连的流向的整板网络名）、`page`（手册页码）和数值（供电写 `voltage: [下限, 上限]`、`current_max`，数字口写 `vih_min`、`vil_max`、`voh_min`、`vol_max`、`abs_max`）；不接端口的器件写空列表。
`python3 scripts/block_circuits.py <设计目录>` 从这两份记录确定性地抽出每块一个文件，不手写：

```json
{"schema_version": 1, "block": "PSU", "name": "隔离电源", "library_root": "~/Documents/知识库/HardwareWiki",
 "schemes": [{"name": "隔离反激电源", "circuit_types": ["POWER_CONVERTER"], "device_kinds": [], "ports": false,
              "selected": {"name": "QR 反激", "circuit": "qr-flyback#…", "reason": "…", "source": ["…"]},
              "decisive": [{"condition": "输入电压", "value": "18～36 V"}],
              "deferred": [{"rule": "G03-001", "values": ["占空比"]}]}],
 "core_parts": [{"role": "反激控制器", "refs": ["U1"], "mpn": "…", "vendor": "…", "datasheet": "…",
                 "decisive": [{"param": "输入电压范围", "op": "covers", "limit": [18, 36], "unit": "V"}],
                 "values": {"输入电压范围": {"value": [9, 40], "page": 1}},
                 "port_limits": [{"net": "VIN", "voltage": [9, 40], "current_max": 0.3, "page": 1}],
                 "external_dependencies": []}]}
```

- 每个功能块都有一个文件；没有关键方案和核心器件的块，`schemes`、`core_parts` 为空。
- 内容是选定方案、决定条件的本板取值（`decisive`）、核心器件与角色、核心器件的端口限值（`port_limits`，任务 C3.3 用）、留给任务 C4.2 核算的数值（`deferred`）；不含落选候选、外围器件和数值。
- C3 的关卡先抽取，再核对：每个功能块一个文件；每块方案、每个核心角色都在自己块的文件里，选定方案、选定型号和位号与工作记录相同。手改过的块文件与重新抽取的结果不同，报错。
- C4、C6 和任务 C3.3 只读块文件，不读 C3 的工作记录。

## blocks/<块>.json（任务 C4.4，模块 C4；整板层块 BOARD.json 归 C5）

```json
{"schema_version": 1, "block": "PSU", "component_requirements_version": 1,
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
- 本块网络的 `net_roles`、`net_voltages`、`high_voltage_nets` 跟着网络写，共享网络的标注各块写得要一致；`external_supply`、`filtered_supply`、`reviewed_circuit_supply` 写在 `pin`（或 `via`）所在的块。
- 引脚处置（`design-closure.json` 的 `pin_dispositions`）归 C4：块设计写完时每个引脚就要有着落。
- **BOARD.json**：C5 只差接口件（上拉、电平转换、隔直）时写的整板层块，格式相同，位号不受编号段限制，端口可用任何流向的网络名；可写 `header`（`revision`、`title` 等整板表头）。

`python3 scripts/blocks.py merge <设计目录>` 读 `record/blocks/` 和 `record/architecture.json`，按网络名合并，写出 `record/electrical-intent.json`。块内网络重名、端口没有对端、位号重复、同一网络各块的角色或电压不一致都报错，按原因回到 C4 或 C2。
`blocks.py roundtrip <整板网表> --plan <分页方案>` 把已有整板网表按分页方案的功能块拆开再合回去逐脚比对，只用来验证块格式。

## modules.json 与过期判定

```json
{"schema_version": 1,
 "modules": {"C3": {"gate": "PASS", "checked": "2026-11-09",
                    "inputs": {"C1:requirements.json": "<sha256>",
                               "C2:architecture.json": "<sha256>",
                               "given:/path/需求.md": "<sha256>"},
                    "outputs": {"scheme-criteria.json": "<sha256>", "selection.json": "<sha256>", "block-circuits/": "<sha256>",
                                "interfaces.json": "<sha256>"}}},
 "returns": [{"date": "2026-11-09", "from": "C4.2", "to": "C3.3", "reason": "+3V3 的电流预算不够", "evidence": "calc:C-3V3"}]}
```

- **inputs**：上游模块产出的指纹，加上用 `--given` 给定的文件。
- **outputs**：本模块产出的指纹。`design-closure.json#a,b` 表示只取这几个顶层区段。design-closure.json 由 C4、C5 分区段写，两者共用的 evidence、work_items 和版本字段不属于任何模块。`block-circuits/` 表示该目录下的全部块文件；`blocks/` 是 C4 的块设计，不含 C5 的 `blocks/BOARD.json`。

各模块的上游如下：

| 模块 | 上游 |
|---|---|
| C2 | C1 |
| C3 | C1、C2 |
| C4 | C1、C2、C3 |
| C5 | C1、C2、C4；C3 的 `interfaces.json` |
| C6 | C2、C5；C3 的 `block-circuits/` |

上游缺失时，记为 `absent`。上游只按 C1→C6 单向，没有互为上游的模块。

`check_module.py status <设计目录>` 逐个列出已记录模块的状态：

| 状态 | 含义 | 怎么处理 |
|---|---|---|
| OK | 输入和产出都没变 | — |
| STALE | 上游变了 | 按新的上游重做本模块并重跑关卡 |
| MODIFIED | 本模块的产出在关卡之后又改过 | 重跑关卡 |

## 单独运行

任务书 `modules` 写 `{from, to, given}`（见 [任务书](workflow-handoff.md)）。按以下步骤做：

1. 把 `given` 的文件原样复制到 `record/`，同时把 `task.json` 复制成 `record/task.json`。块文件的键写 `block-circuits/<块>.json`。
2. 从 `from` 做到 `to`，每个模块做完都跑一次 `check_module.py <模块>`。
   关卡会核对给定输入有没有被改动。design-closure.json 这类几个模块共写的文件，只比对上游模块拥有的区段。
3. `check_module.py report <交付目录>` 写出 `模块报告.md`，内容是范围、给定输入、各模块关卡、产出和待办。
4. `check_module.py pack <交付目录>` 核对交付目录。

**只给网表时（单独运行 C6）**：用 `import_netlist.py <netlist.xml> --out record/electrical-intent.json --source-schematic <根图> --library-dir 设计资料/symbols` 把 KiCad XML 网表转成设计网表。
- 源工程里内嵌的符号会抽成项目符号库，画图时用 `--symbol-dir` 指向这个目录。
- 引脚号里带“.”的网表无法用“位号.引脚”表达，导入时会报 FAIL。
- 子页局部标签的网络名去掉页路径（`/09_CH12/IN_D1` 写成 `IN_D1`；两页同名时写成 `页_名字`），原名记在 `source_netlist.net_names`。重画可以自由分页，画图时按这些名字标注。
- 源工程的器件字段原样带入，包括器件性能字段。性能记录不是给定输入，自动总检查对导入的网表不要求它，这一项记 NOT_CHECKED。
- 网表里没有电源轨角色和网络电压，任务 C6.1 按需要补写。

## 给定输入有问题

单独运行时，给定输入只读。发现给定输入本身有问题（方案在某工况下不可行、需求自相矛盾），登记一件 `stage: "input"` 的待办：
- `upstream` 写出问题的上游模块，`given` 写给定的文件；
- `action` 写证据和建议改法，`owner` 写任务书的提供方；
- 不改上游。

整板流程中登记 `input` 待办，审计会报 `input_item_in_whole_flow`。

串联运行时，回到上游模块重做，下游按指纹重跑。每次回到上游都记一条：

```bash
python3 scripts/check_module.py return <设计目录> --from C4.2 --to C3.3 --reason "+3V3 的电流预算不够" --evidence "calc:C-3V3"
```

它写进 `record/modules.json` 的 `returns`：日期、发现问题的任务、回到的任务、原因和依据。交付时 `knowledge_gaps.py` 把它们抽进知识缺口清单（见 [交付与设计报告](delivery-report.md)）；查知识包的记录在同一文件的 `knowledge_lookups`，没查到的也抽进清单（见 [知识包](knowledge-package.md)）。
