# 86 块开源板的真缺陷落到 ASG 生成侧防线（2026-11-02）

来源：`~/.cache/sr-boards/_summary/findings-all.json`。共 201 条真缺陷，按 SR 规则归类；
引用写成 `review:sr-boards-2026-11-02/<板>/<编号>`。本文回答“ASG 画图时怎样保证不犯这个错”。
用户事件：`user:2026-11-02`（把这个86块板子上找到的问题，在规则库、ASG和SR技能中进行改进）。

本次没有改 `SKILL.md`、共用层（`references/shared/`、`scripts/guideline_criteria.py`、`scripts/stress_check.py`）和设计准则库条款。
第 2 节的纲要改动只是草案，要人确认后才能写入。

## 1. 缺陷类 → ASG 防线对照

状态：**已有**表示改动前已经拦得住；**新增**表示本次加的审计或要求；**做不到**写明原因和替代做法。

### 1.1 料号、封装、手册不一致，符号脚类型不对（DEV-D04/D01/D02，60 条）

| 缺陷类（例） | 状态 | 防线 |
|---|---|---|
| 值与料号是两个型号（greenmobi-bms U3 LM5163DDA 对 LM5164DDA；U4 TPS70933 对 TPS79333；batdatunit01 SN74HC164P 对 …D） | 新增 | `binding_version 1`：`part_value_contradicts_mpn`，值要等于料号或是它的前段 |
| 手册不是这个料号的（protocentral U6 TCR2EF33 挂 AP2112；jetson-nano U6 SiC477 挂 SiC471～474；hv-flyback D3 MMSZ5258B 挂 BZT52） | 新增 | `part_datasheet_contradicts_mpn`：关键/特殊器件的手册文件名要能匹配料号（小写 x 当通配，`_` 分隔多型号），或手册正文里有这个料号 |
| 晶体值与订货码频率不同（reference-hardware Y3 16 MHz 对 ABM8-24.000MHZ） | 新增 | `crystal_frequency_contradicts_mpn` |
| 料号含通配（greenmobi-bms D1 BZT52Bxx，U5 BQ769x2） | 新增 | `placeholder_value`（不分记录版本）：料号或型号里的小写 x、`?`、`*` |
| 引脚表按 SO8 读、实物是 HWSON（hdmi-mipi-bridge U3/U6）；变体脚名不同（zigbee U1 RESET# 对 HOLD#） | 已有 + 新增 | 已有：`reference-input.json` 的引脚表逐脚核名字与类型、`identity` 核料号/封装字符串。新增：`pin_map_datasheet_mismatch`，引脚表读的手册要与设计网表 `datasheet` 是同一份 |
| 输出声明为输入（flatmcu U3 开漏/输出写成 IN；gnss U2 TXD1/1PPS 写成输入） | 新增 | 引脚表每脚写 `datasheet_type`（照手册 I/O/IO/OD/PWR…），`types` 只能取相符的 KiCad 类型：`pin_map_without_datasheet_type`、`pin_type_contradicts_datasheet` |
| 关键器件缺料号、手册或类型声明 | 已有 | `part_classes.audit_identity`（报告问题，`pack_design.py` 拒绝打包） |
| 订货后缀缺失（breadboard-psu U2 SE5218 没给电压档；io-expander U3 输出档） | 部分做不到 | 判不出一个系列有哪些订货后缀：手册订货表的格式各不相同，SE5218 本身也出现在正文里。已有防线：值/料号一致、通配检测、引脚表 `identity.mpn` 与 KiCad 一致；靠任务 2.1 按订货变体读手册（纲要已写“确切变体”）。建议纲要改动 2.3 把它写进做完的标志 |
| 封装字段与订货封装不符（isolated-flyback D1 DFLS1100 写 D_SMA；driverino C4 0603 对 0402） | 做不到 | 原理图阶段封装可以留空，焊盘与封装库属于 PCB 环节；没有可机读的料号→封装库。已有：引脚表 `identity.footprint` 与 KiCad 一致，选定变体与物理脚号由任务 2.1 核 |
| BOM 采购码与图上值冲突（nixie C18/C19 100 nF 0805 对 470 nF 1812） | 已有 | ASG 的 BOM 由设计网表/性能记录生成（`write_bom`），`component_requirements.audit` 逐位号比较 BOM、XML 与设计网表 |

### 1.2 BOM、占位值、页码、文字重叠、图注（DOC-Q01/D01/D02/V01/V02，29 条）

| 缺陷类（例） | 状态 | 防线 |
|---|---|---|
| 占位值进交付（chlinknet R_Small、C、Crystal_GND24；solarmini R2 无值；bms-can C3–C6 无容量） | 新增 | `placeholder_value`：库默认名、等于符号名的值、`-`/`?`/`xx`/`TBD` 不分记录版本都拦；`binding_version 1` 下空值也拦 |
| 位号未编号（gnss 天线座 K?） | 新增 | `unannotated_reference` |
| BOM 与原理图不一致（qfhmix01、batdatunit01 R71、jetson-ai-cam 漏 4 件） | 已有 | `component_requirements.audit` 核 BOM 每个位号一次、字段等于设计网表；`verify_schematic.py` 逐字段核 KiCad 与设计网表 |
| 页码错（tpa3116d2 6/5、7/5） | 已有 | `Root` 按页顺序写 `sheet_instances` 页号 |
| 文字重叠（usb2_hub、fastlogic、eegfrontier、protocentral） | 已有 | `check_schematic_readability.py`、字段摆放与几何检查，任务 4.2 图面审阅 |
| 图注与网表不符（sparkfun Imax 1.5 A；neotron 地址 0x6F；xerxes UART 标成 JTAG） | 部分做不到 | 自由文字的语义没法机械核。已有：性能标注由性能记录生成并核到 PDF（`drawing_errors`）；其余自由注释靠任务 4.2 审阅 |

### 1.3 未用脚、RSVD/NC、CC 下拉、AUX 接法（NET-A07/A01/A06、DEV-D05，41 条）

| 缺陷类（例） | 状态 | 防线 |
|---|---|---|
| 脚没有网络也没标 NC（amiga U108.1–4） | 已有 | `generate.py` 要求每个物理脚在网络里或在 `no_connect` |
| 未用 CMOS 输入悬空（nixie SN74HC595 10 脚；eegfrontier DAISY_IN、GPIO1–4；inkplate 4A2/4A3） | 新增 | `pin_dispositions`：连接器以外每个 NC 脚写手册规定的处置和手册页，`no_connect_without_disposition`、`disposition_without_source` |
| RSVD/保留脚接法不按手册（fastlogic W5500 RSVD 悬空；eegfrontier RESV1 接 SPI；hdmi PFIL 处置错） | 新增 | 同上，处置为 `tie_low`/`tie_high`/`pull_*`/`per_datasheet` 时核设计网表真的这样接：`disposition_contradicts_netlist` |
| CC 挂单节点伪网、没有 Rd（rs485-spy J4.A5/B5） | 新增 | `single_endpoint_net`；Type-C 典型电路必需外围写明每根 CC 独立 Rd |
| AUX 未接 VSS、AGND 未接、PWREN# 输出接地、预稳压接法错（poepico、driverino、m2-smart、bms-can） | 部分 | 由引脚表 `datasheet_type` + 处置表把“手册要求怎么接”写成记录；“接到哪个网才对”的语义仍靠任务 2.1 读手册，审计只核记录与网表一致 |
| 一端开路、子页断开（flyback C10、anthc J5.1） | 已有 + 新增 | 设计网表与 KiCad 逐脚一致（已有）；单端网络（新增） |

### 1.4 旁路/输出电容、额定电压与功率、TVS、USB、晶体（PWR-D02/C04/C09、DEV-C01/C05、PRO-E02、SIG-C05/D07、CLK-C01，43 条）

| 缺陷类（例） | 状态 | 防线 |
|---|---|---|
| 电容额定电压低于所在轨（neotron 25 V 对 30 V；stm32h7 10 V 对 15 V；driverino 35 V 对 36 V） | 新增 | `net_voltages`：每条电源轨写最坏最高电压和来源（`net_voltage_missing`、`net_voltage_without_source`），并接其上的电容额定低于它记 `capacitor_rating_below_net_voltage`；性能记录里完整定义的电容必须写 `working_voltage`/`rated_voltage` 下限 |
| TVS 的 VRWM 低于轨电压（jetson-nano SMBJ33A 对 36 V；hv-flyback PESD5V0 对 6 V；poepico SMAJ24A） | 新增 + 已有 | 新增：`tvs_vrwm_below_net_voltage`（按 VRWM 命名的系列从型号读，或取性能记录的 `working_voltage`），性能记录里 TVS 必须写 `working_voltage` 下限。已有：保护器件要进两侧都算的阈值计算（`audit_safety`），Type-C 与 PD 典型电路已有 G05-030 |
| 电阻功耗超额（scalenode R34 0.15 W 对 0603 0.1 W） | 已有 | 写出功耗检查的电阻必须写额定功率（`resistor_power_rating_missing`），降额检查按 `derating_version` |
| 电感额定电流小于路径电流（12v-5a L2 3 A 在 5 A 路径） | 已有 | 常规电感要写额定电流（`audit_identity`），应力计算按 `derating_version`；电流本身要写成计算才核得到 |
| 输出/旁路电容低于手册最小值（kimchi 1.22 µF 对 11 µF；batdatunit CLDO 100 nF 对 1 µF；flatmcu、inkplate 0.1 µF 对 4.7 µF） | 新增 | 性能记录新增 `basis: datasheet`（来源 `kind: manufacturer`）；同一记录的标称容量必须满足容量/有效容量下限（100 nF 配 ≥1 µF 记错）。LDO 典型电路实现方案加必算项与 G03-003/G03-004 |
| 手册规定的外接值不对（home-mini REXT 200 k 对 75 k；12v-1a 定时电阻；eegfrontier VCAP1 10 µF 对 100 µF） | 已有 + 新增 | 已有：`reference-input.json` 的 `component` 外围检查核确切值；新增：`datasheet` 依据的性能要求与标称一致性 |
| USB 串阻/上拉与 MCU 手册不符（klipper 2.2 k 对 1.5 k；cellkeeper 22 Ω 对 27 Ω） | 已有（要写出来） | `reference-input.json` 的 `component` 检查；没有 USB 设备典型电路，列入第 3 节 |
| 晶体负载/频率与采购不符（hdmi 振荡器并 47 pF 对 15 pF；reference-hardware 16/24 MHz） | 新增 + 缺 | 频率一致新增；有源振荡器输出负载无准则、无典型电路，列入第 3 节 |
| VBUS 体电容超限、拔出检测、过压（usb2_hub、anthc、feather-rak3172） | 新增 | Type-C 典型电路加必算项与 G01-026、G01-029、G01-030 |
| 推荐工作范围外（eegfrontier AVDD 3.3 V 对 4.75 V；fuel-gauge I²C 上拉到 5 V；RC 慢边沿进 CMOS） | 做不到（机械） | 需要逐脚的供电/电平表；靠 G04-003/G04-005 的计算与典型电路，慢边沿无准则，列入第 3 节 |

### 1.5 其余 28 条

`PWR-A02`（VCCADC 接地）、`RST-*`、`SIG-C08/C11/C14`、`ANA-*` 等，每类 1–2 条，本次没有单独加审计；
电源脚接错网由引脚表 `datasheet_type: PWR` 与 KiCad power_in 的 ERC 兜住一部分，其余靠任务 2.1。

## 2. 建议的纲要（SKILL.md）文字改动（草案，待人确认）

共 4 条。确认后写入，台账带 `Approved` 与 `Outline` 哈希。

**改动 1：任务 2.1 做完的标志**（第 179–180 行）

- 原文：做完的标志：每个核心器件在外围电路核对表 `reference-input.json` 里有引脚表与外围检查，核对通过或列出资料不足的项；
  分立器件的符号含义与料号一致；新数据手册已入库（`pack_design.py` 的入库检查通过）。
- 新文：做完的标志：每个核心器件在外围电路核对表 `reference-input.json` 里有引脚表与外围检查，核对通过或列出资料不足的项；
  引脚表读的是所选订货变体的手册（与设计网表的 `datasheet` 同一份），每个脚写了手册引脚类型，符号脚类型与它相符；
  分立器件的符号含义与料号一致；新数据手册已入库（`pack_design.py` 的入库检查通过）。
- 理由：DEV-D02 8 条（HWSON 按 SO8 接、输出声明为输入），DEV-D04 中引脚表与手册不是同一型号。

**改动 2：任务 2.3 做完的标志**（第 235 行）

- 原文：做完的标志：每项性能要求都有采购定义方式和来源/候选处置；无已知不满足被当成满足，无未核实候选被当成已核准。尚缺外部数据的可有条件进入出图，但报告不能宣布其型号核实或设计定型已完成。
- 新文：做完的标志：每项性能要求都有采购定义方式和来源/候选处置；无已知不满足被当成满足，无未核实候选被当成已核准；
  按型号采购的器件，值、料号与数据手册指同一订货变体，料号写全订货码；电容额定电压与 TVS 工作电压不低于所在电源轨的最坏最高电压。
  尚缺外部数据的可有条件进入出图，但报告不能宣布其型号核实或设计定型已完成。
- 理由：DEV-D04/D01 52 条身份冲突与后缀缺失；DEV-C01、PRO-E02 中额定低于轨电压。

**改动 3：任务 2.4 正文**（第 244 行）

- 原文：每个物理引脚要么接入网络，要么有依据地标 NC。设计网表从需求和手册写出，不从草稿图回抄。
- 新文：每个物理引脚要么接入网络，要么有依据地标 NC；不接的脚和按手册接地、上下拉的未用脚，逐脚写手册规定的处置和页码。
  每条电源轨写最坏最高电压和来源。设计网表从需求和手册写出，不从草稿图回抄；值写设计值，不留库默认名或占位。
- 理由：NET-A07/DEV-D05 35 条未用脚与保留脚；DOC-D01 6 条占位值。

**改动 4：任务 2.4 做完的标志**（第 249–250 行）

- 原文：做完的标志：每个物理引脚接入网络或有依据地标 NC；`net_roles` 覆盖电源轨与阈值/反馈网络；
  电气改版的生成前预检为 PASS 或 CONDITIONAL。
- 新文：做完的标志：每个物理引脚接入网络或有依据地标 NC，NC 与未用脚的处置有手册页；`net_roles` 覆盖电源轨与阈值/反馈网络，
  每条电源轨写了最高电压；没有占位值和未编号位号（`audit_design_closure.py` 的 `binding_version 1` 无错误）；
  电气改版的生成前预检为 PASS 或 CONDITIONAL。

## 3. 准则缺失清单（交起草准则的任务，本次不编号）

| 缺什么 | 涉及缺陷 | 现有最近的准则与差距 |
|---|---|---|
| 器件身份一致：值、料号、订货后缀、封装与手册是同一订货变体；符号脚号与脚类型按手册脚表 | DEV-D04/D01/D02 共 60 条，均无准则引用 | 无 |
| 交付文档一致：BOM 与原理图同版、无占位值、图注与网表一致 | DOC-Q01/D01/V02 | G02-026 只管分析证据绑定原理图版本，SR 借它判 DOC-Q01 |
| 未用输入与保留脚按手册处置（CMOS 未用输入不悬空，RSVD/NC/DNC 按手册接） | NET-A07 22 条、DEV-D05 13 条 | G04-010 只管关键输出的上电默认态 |
| 手册规定的外围值（定时/基准电阻、内部稳压脚 VCAP 电容、补偿脚） | DEV-D05、DEV-C05、PWR-D02 | G03-003/G03-004 只管内补偿变换器与 LDO 的输出电容；G03-035 关闭阶段是 pcb，但去耦容值与数量是原理图项，建议拆出原理图阶段的一条 |
| USB Type-C Sink 的 CC 端接（每根 CC 独立 Rd） | NET-A01 rs485-spy 2 条 | G01-026～031 没有 CC 端接 |
| USB 设备 D+ 上拉、串联电阻按 MCU 手册取值 | SIG-D07 klipper、cellkeeper | G01-030 只管断开检测 |
| CMOS 输入的过渡时间（RC 复位/延时直接进非施密特输入） | DEV-C05 jetson-nano F003、reference-hardware F002 | G02-022 管时序配合，不管边沿速率 |
| 有源振荡器输出负载不超过规定负载 | DEV-C05 hdmi-mipi-bridge F29 | G04-078 是无源晶体的负载电容 |
| 传统 USB（Micro-B、USB-A）的电压窗、体电容与断开检测 | 14 条准则问题中 7 条指 G01-026/029/030/031 只适用 Type-C/PD | 本次只把 G01-026/029/030 加到 Type-C 受电口典型电路，未用于传统 USB |

## 4. 本次改动

- `scripts/audit_design_closure.py`：占位值与未编号位号（不分版本）；`binding_version 1` 的身份、引脚表、未用脚处置、电源轨电压核对；处置与轨电压的手册引用纳入引用核对。
- `scripts/schematic_layout/component_requirements.py`：`basis: datasheet`；电容、TVS 完整定义必须写电压下限；标称值满足同量上下界。
- `scripts/schematic_layout/reference_contract.py`：引脚表允许 `datasheet_type`。
- `scripts/render_design_report.py`：“记录版本”一行写明没有 `binding_version`。
- 典型电路：`type-c-port-protection`（CC Rd、输入电压窗、VBUS 电容、拔出检测；落实规则加 G01-026、G01-029、G01-030）；
  `reviewed-bias-and-latch#二次辅助经反向保护LDO和串联二极管供SR`（LDO 输入/输出电容按手册；加 G03-003、G03-004）。
- 文档：`references/design-closure.md`、`component-requirements.md`、`symbol-and-peripheral-contracts.md`、`requirements-to-intent.md`。
- 测试：`tests/test_board_defect_guards.py`，`tests/test_design_report.py` 加 binding 记录版本断言。
