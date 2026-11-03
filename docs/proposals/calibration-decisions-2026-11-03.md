# 工业 I/O 校准板：SR 四件取舍落地、引脚表自动填（2026-11-03）

> 读者：ASG 维护者、用户。用户 2026-11-03：按建议执行。
> 校准板目录 `~/Documents/ASG-calibration/industrial-io-rs485-can/`（不在仓库）；需求 v0.4（C17、C18）。SR 只读。

## 1. 四件处置（W-SR-DECIDE 关闭）

| # | SR 发现 | 处置 | 落在哪里 |
|---|---|---|---|
| 1 | F06：D102 击穿下限 34 V 落在 U101 OV 动作窗 33.5～36.1 V 内 | 保留现设计。需求 C17：持续过压只保证到 28.8 V，过压保护只针对瞬态 | `CALC-UV-OV` 加“持续输入上限（C17）vs D102 击穿下限 28.8 ≤ 34 V”（TVS3300 p6）；FMEA 加“输入持续过压 34～36 V（已知边界）”行、保护链过压行注明；工况矩阵加“持续过压（已知边界）”行，引用 IIO-002/C17 |
| 2 | F10：FIELD+ 是否按直流电源口核浪涌 | 判适用（C18）。新计算 `CALC-FIELD-SURGE` 发现原设计不够，改器件 | 见第 2 节 |
| 3 | F11：DI 输入 TVS 钳位对 IPx 绝对最大 36 V | 保留 SMAJ30CA。新计算 `CALC-DI-PIN-SURGE`：手册无内部钳位，每路加稳压管 | 见第 3 节 |
| 4 | F07：U401 订货码只有预量产 | 保留。料号改写订货表里真有的 XISOW3080PDWER；新增交接待办 `W-U401-PRODUCTION`（validation/handoff，采购/产品方）：SLLSG02A p32 订货表状态 Pre-Production，投产前换已量产料，候选 ISOW1432（脚表需重核，不在本板做） | `board_iio.py`、`records_iio.py`（selection）、`closure_iio.py` |

`W-SR-DECIDE` 改为 closed，`action` 逐件指到 C17、CALC-FIELD-SURGE、CALC-DI-PIN-SURGE、W-U401-PRODUCTION。

## 2. CALC-FIELD-SURGE（现场电源口，需求 IIO-029/C18）

取值依据：IEC 61000-4-5 直流电源口（GB/T 17799.2—2023 表 3 按此施加），线-线 0.5 kV 经发生器 2 Ω（18 µF 耦合），线-地 1 kV 经 2 Ω + 10 Ω（9 µF）。
线-地也按全部电流走 D602 差模计（不依赖 C607 限电荷），偏保守。D602 用手册注 3 的线性模型 VCL(I) = VCL − RD×(IPP − I)（SMAJ33CA 8/20：69.7 V@33 A，RD 0.884 Ω，p3）。
V24 支路电荷上界：D602 峰值残压按导通全程保持，导通时间取 1.2/50 开路电压（半峰 50 µs 指数衰减）降到 V0 为止（model，±30 %）。

**改前**：D602 直接在端子上，线-线时 D602 电流约 160～215 A，是 IPP 33 A 的 5 倍以上，钳位前 D602 先坏；V24 只有 10 µF 陶瓷电容。

**改动**（常规做法：TVS 前串电阻限流、储能电容吸收浪涌电荷）：
- 新增 R602 22 Ω 抗浪涌电阻（端子与 D602 之间；按值加规格：单次 8/20 浪涌能量 ≥0.5 J，MELF 0207 或 2512 抗浪涌型）。
- C601 10 µF/50 V 陶瓷 → 100 µF/50 V 铝电解（容量下限按 −20 % 计）。
- R601 22 Ω 不变，加脉冲能量规格 ≥0.05 J。

**改后结果**：

| 检查 | 值 | 门槛 | 依据 |
|---|---|---|---|
| D602 线-地电流（全按差模） | 27.5 A | ≤ IPP 33 A | SMAJ p3，TVS-SURGE |
| D602 线-线电流 / 残压 | 18.5 A / 56.9 V | ≤ 33 A | 同上 |
| D602 峰值功率 | 1783 W | ≤ 2.3 kW（8/20） | SMAJ p1 |
| D602 I²t（∫i²≈I²×14 µs） | 0.0106 A²s | ≤ 33²×14 µs = 0.0153 A²s | 同上 |
| V24 脚峰值（线-地 / 线-线） | 33.5 V / 31.7 V | ≤ 36 V 绝对最大 | SN65HVS883 p4 |
| D601 浪涌峰值电流 | 1.64 A | ≤ 30 A×0.9 | 1N4007 p1 IFSM |
| R602 单次浪涌能量 | 0.233 J | ≤ 0.5 J（采购规格） | 自定门槛 |
| R601 单次浪涌能量上界 | 13.7 mJ | ≤ 0.05 J（采购规格） | 自定门槛 |

V24 脚峰值余量（2.5 V）小于模型不确定度 30 %，按审计写了 improvement（C601 加到 220 µF 或 R601 加到 33 Ω）。
`CALC-DI-SUPPLY` 随之更新：V24 最低 = 20.4 − 0.9 − 20 mA×(22+22) Ω = 18.62 V ≥ 18 V（p5 门限保证条件）；带电插入 C601 经 44 Ω 充电峰值 0.65 A ≤ 27 A，R601 吸收 20.7 mJ ≤ 0.05 J。

## 3. CALC-DI-PIN-SURGE（DI 输入脚，需求 IIO-019/029）

手册 SN65HVS883：IPx 绝对最大 −0.3～36 V（p4）；输入级是受控电流沉，图 13 只有限流器（p11），没有内部钳位；IIP-LIM 3.15～4 mA 只在 10 V < VIPx < 34 V 保证（p5）。
TVS 钳位取 SMAJ30CA 8/20 额定点 64.3 V@36 A（p3）。注意：任务说明写的“48 V（8/20、36 A）”在手册里是 10/1000 µs、8.3 A 的值（48.4 V），8/20 µs、36 A 的额定钳位是 64.3 V，本计算按 64.3 V。

**改前**：IPx ≈ 64.3 − 4 mA×1.14 kΩ = 59.7 V，远超 36 V。

**改动**：每路 IPx 脚侧加 D631～D638，30 V ±2 % 稳压管（BZT52H-B30 档，NXP BZT52H p6：VZ 29.4～30.6 V@2 mA，rdif ≤40 Ω@5 mA，SZ ≤29.4 mV/K，IZSM 1.0 A）。
任务说“按常规选件，不必料号”；ASG 器件分类把稳压管列为关键件（`part_classes.KEY_KINDS`），审计要料号，所以写了库里有手册的 BZT52H-B30。R61x 1.2 kΩ 不变。

| 检查 | 值 | 门槛 |
|---|---|---|
| IPx 浪涌峰值（VZ 上限 + 70 ℃ 温漂 + rdif×30.6 mA） | 33.1 V | ≤ 36 V 绝对最大；≤ 34 V 限流保证区（IPx 电流 ≤4 mA） |
| D63x 浪涌电流 / 功率 | 30.6 mA / 1.0 W | ≤ IZSM 1.0 A / PZSM 40 W |
| DI 持续 30 V 时 IPx 最高 | 26.4 V | ≤ D63x VZ 最低（−40 ℃）27.5 V，正常与持续过压下稳压管不导通 |
| D63x 漏电（VR 21 V） | 0.05 µA | ≤ 门限电流 1 % |
| D611 线-地浪涌电流（1 kV/42 Ω，全按差模） | 22.5 A | ≤ IPP 36 A |

rdif 由 5 mA 外推到 30 mA 标 model（±50 %），传播到 IPx 约 ±0.6 V，已写进检查的不确定度。R61x 的浪涌脉冲能量（约 0.3 mJ）普通电阻无额定数据，转 W-EMC 实测。

## 4. 器件与图面改动

- 新增：R602（22 Ω 抗浪涌）、D631～D638（BZT52H-B30）。改值：C601 10 µF 陶瓷 → 100 µF/50 V 铝电解；U401 料号 ISOW3080PDWER → XISOW3080PDWER（值 XISOW3080P）。
- 网表：FIELD_P = J601.1–R602.1；新网 FIELD_S = R602.2、D601.A、D602；IPn 加 D63n.K，FGND 加 D63n.A。
- `draw_iio.py` 07_DI：R602 在端子与 D602 之间；每路 R61n 后接 D63n 下拉到 FGND；D62n–R61n 间距加大让 R61n 字段有位置。分页方案块、供电路径复核、FMEA、工况矩阵同步更新。
- 画图时发现 ASG `recipes.Sheet` 把一页上所有“重复支路”放在一起比排法（J601 侧 TVS+二极管、U601 侧电阻+稳压管两组），八路全报不一致；已改为按锚点分组比较（`scripts/schematic_layout/recipes.py`，测试 `test_lane_groups_are_compared_within_their_anchor`）。

## 5. 引脚表自动填（纲要建议 1 的工具侧）

新脚本 `scripts/fill_pin_maps.py`：按设计网表每个器件的 `datasheet` 找引脚表页，用 `pdftotext -layout` 读表行，只从 TYPE/I/O 标题下的格读类型、
多封装/多型号并列时选与符号编号对得上的列、引脚图里的脚名只补名字，写 `datasheet_name`/`datasheet_type`/`datasheet_page` 并把引脚表来源改指手册；
填不上的按原因列出（`not_in_table`、`type_not_given`、`rows_disagree`），不写 `name_note`、不从符号抄。
`reference_contract.py` 的引脚条目允许可选 `datasheet_page`；用法写进 `references/symbol-and-peripheral-contracts.md`，`design-closure.md` 加一句指引。测试 `tests/test_fill_pin_maps.py` 9 条。
校准板 `records_iio.py` 带网表重写引脚表合同后自动调用它，报告写 `record/pin-map-fill.json`。

**校准板结果**（14 张引脚表、239 个脚）：165 脚名字与类型都从手册读出；74 脚未填——

| 原因 | 脚数 | 器件 |
|---|---|---|
| 手册没有引脚表（分立件只有封装图） | 21 | Q101、Q102（STL110N10F7）18，D401（SM712）3 |
| 表里没有这个脚 | 8 | D102 GND 1–3（SON 列空白）、U401.10（NC 未列）、U601 EP 等 4 |
| 手册类型列为空或“—”/“--” | 42 | U601 全表无类型列 25，U401 电源/地 7，U602 电源/地 6，U101 RTN、U201 AGND/EP、U202 GND |
| 几行说法不一 | 3 | U301 PC13～15（表内名字折行，引脚图给的是别的封装） |

**`binding_version 1` 试跑**（不放宽审计；校准板记录本身仍不写 `binding_version`）：505 → 199 条。

| 类别 | 改前 | 改后 | 说明 |
|---|---|---|---|
| 缺 `datasheet_name` / `datasheet_type` | 239 / 239 | 32 / 74 | 上表的未填脚 |
| 引脚表来源不是这份手册 | 14 | 3 | Q101、Q102、D401 无引脚表 |
| 符号类型与手册不符（新暴露） | — | 47 | 符号里堆叠脚的隐藏副本写 passive（U301 VSS/VDD、U701 OUT、U201 SW）；未用 GPIO 写 no_connect（U301）；STM32 OSC_IN/OSC_OUT/NRST、IPS4140 STAT 开漏、LM74910 A/C/OUT/TMR/ILIM、TLV743 IN/OUT 等手册类型与符号不同；TI “P” 不分输入输出，SW/BST 与 power_out/passive 冲突 |
| 手册名与符号名不同（新暴露） | — | 30 | STM32 符号带复用功能名（PA9/USART1_TX）、合并的 VDD/VSS（手册 VDD_1…）；IPS4140 STATUSn 对手册 STATn；ESD2CAN IO1/IO2 对 IO；TVS3300 K 对 IN；LM74910 EP 写 NC（手册 RTN） |
| 电源轨最高电压未写 | 8 | 8 | 记录未写 `net_voltages` |
| 值与料号前段不符 | 5 | 5 | F101、RV101、U101、D401、D501 |

后两类新暴露的是真实差异，要人判：改符号（类型、名字）或写 `name_note`；TI “P”类冲突属于审计词表比手册粗，不改词表放过。

## 6. 运行状态

- 校准板全程 `deliver.py`（2026-11-03）：准备 1～6、出图、生成报告、交付证据 DONE；证据新鲜度 FRESH；打包 PASS（`record/sr-review/` 已收）；`设计报告.md` 重出。
- 自动检查：ERC、网表、层次、符号完整性、分立件语义、可读性、几何、外部供电、引用合同均 PASS。几何首次重跑因同期其他作业改动 KiCad 配置报 "renderer configuration changed during job"，等其他作业结束后重跑 PASS。
- 器件性能预检 INCOMPLETE：0 错误，3 条待定、21 条采购项（含 U401 预量产交接）。待办审计 INCOMPLETE：0 错误，余下为交接/采购状态的待办。
- 图面审阅：按新版 `原理图/schematic.pdf` 重写 `record/visual-review.json`（8 页）。
- ASG：`python3 -m pytest tests -q` 1108 passed；`check_ledger.py` PASS。

## 7. 纲要建议（只写不改）

1. 任务 2.4 的做完标志可补一句“引脚表可用 `scripts/fill_pin_maps.py` 从手册填，填不上的脚按原因人工补”，并说明手册类型码比审计词表粗时（TI “P”）冲突由人判。
2. 任务 5.1 可写明：独立审查（SR）的“需人判”项由设计方定下后，处置逐件落到需求澄清、计算或交接待办，不留成一件笼统的设计待办。
