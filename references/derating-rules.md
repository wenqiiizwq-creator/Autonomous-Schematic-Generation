# 元器件降额规范

> 读者：审查员（ASG 设计与 SR 审查共用此文件，两仓逐字相同）。

本规范给出器件应力的降额要求，分 I、II、III 三级。ASG 设计和 SR 审查都按项目定下的降额等级取对应一列的值。
机器可读的同一份数据在 `references/derating-rules.json`，本文件的表格与它逐条对应（编号相同）。
两个文件在 autonomous-schematic-generation 和 schematic-review 两个仓库里逐字相同，由两边的对齐测试核对；改动要两边同时改。

## 来源

| 代号 | 文件（知识库 `raw/Standard/`） | 分级 |
|---|---|---|
| 1013 | T/CPSS 1013—2021 开关电源电子元器件降额技术规范（2026-08-20 改号 T/CPSS 40-2021，技术内容未变） | I/II/III |
| GJB | GJB/Z 35—93 元器件降额准则 | I/II/III |
| 1006 | T/CPSS 1006—2024 通信用开关电源的元器件降额准则（改号 T/CPSS 69-2024） | 只有一级，三级取同值，表中注“三级同值” |
| NB/T | NB/T 10297—2019 交流-直流开关电源电子组件降额技术规范 | I/II/III；只作对照，不进默认取值（见“NB/T 10297 的差异”） |

页码是 PDF 页码。IPC-9592B 只有官方目录，降额表（附录 A 表 A-1～A-6）不在库内，未收录。

## 降额等级从哪来

降额等级是项目需求的一部分，写在设计记录里并注明来源（需求条目或用户答复）。需求没有写时，ASG 当场问用户，
SR 按需求澄清处理；问的时候附上建议等级：

| 等级 | 1013 §5.1（p5） | GJB 4.1、表1（p5–6） |
|---|---|---|
| I 级（最大降额） | 产品失效给人员带来安全危险或使应用系统严重破坏；采用新技术、新工艺；连续工作、长寿命（推荐服务器电源） | 失效导致人员伤亡或装备严重破坏；失效后无法或不宜维修；航天器与运载火箭 |
| II 级（中等降额） | 高可靠性要求且采用了专门设计；失效可能引起应用系统损坏；连续工作、中等寿命（推荐商业用途电源） | 失效可能引起装备损坏；维修费用较高 |
| III 级（最小降额） | 成熟的标准设计；失效对应用系统造成破坏的风险很低；间歇工作、低寿命（推荐消费类电源） | 失效不会造成人员和设施的伤亡和破坏；故障可迅速、经济地修复 |

GJB 表1 的应用范围：战略导弹 I～II 级，战术导弹、飞机与舰船、通信电子系统 I～III 级，地面保障设备 II～III 级。

## 取值规则

- **R1 来源优先**：每个“器件类型 × 参数 × 工况”按 1013 → GJB → 1006 的顺序，取第一份给出数值的来源；表中只列被采用的那一条。
  GJB 给范围的，取保守端（表中注明原文范围）。1013 已用绕组温度和磁饱和控制电感时，不再叠加 GJB 表29 的工作电流系数。
- **R2 稳态与瞬态**（1013 表3、表4 注）：稳态是电源连续稳定工作，每个开关周期都出现的尖峰也算稳态；瞬态是开机、关机、
  输出短路等瞬间。分列稳态与瞬态的参数分别比较。
- **R3 只给一个系数**（工况 `worst`）：直流、交流和瞬态的最坏组合不得超过降额后的值（GJB 表7 注1、5.2.2.2；电容的直流加交流峰值
  见 GJB 5.8.x.2.1）。手册单列的冲击或脉冲额定（工况 `pulse`）按表中比例与该额定比较，不再套稳态系数。
- **R4 额定值**取最坏工作温度下的保证值：手册给温度折减曲线的，先按曲线修正再乘降额系数；不重复折减。
  典型值和手册没给的参数不能当额定。
- **R5 结温**：`tj_percent` 按 1013 附录 A（p15）T(n%) = (Tjmax − 25 °C) × n% + 25 °C；`max_c` 是绝对温度上限。
  功率器件结温由壳温推算：Tj = Tc + Pd × Rth(j-c)（1013 6.1.4）。
- **R7 选规则**：先按器件类型（`kinds`），再按技术子类（`subtype`：`mosfet` 分硅 MOS `si`、`igbt`、`gan`、`sic`，
  `crystal` 分无源晶体 `crystal` 和有源晶振 `oscillator`，以手册写明的器件技术为准），再按被比较的参数、工况（`condition`）
  和额定值口径（R4：同条件、最坏温度下的保证值）选。类型对、子类或参数口径不对的规则不能用，例如硅 MOSFET 不套 GaN 的栅压规则。
- **R8 负向额定按幅值比较**：额定值为负（如关断负栅压 −10 V）时，比较的是幅值：允许幅值 = |额定| × 取值，
  |最坏应力| ≤ 允许幅值才满足。例：GaN 关断负栅压额定 −10 V、取值 50%，允许 −5 V 以内；−8 V 的幅值 8 V 超过 5 V，
  降额不足。不能把 −8 V 与 −5 V 按带符号的 ≤ 比较判满足。
- **R9 冲击与脉冲**（工况 `pulse`）：与手册同波形、同时宽、同温度（冷机、热机分别）和同次数口径（单次或重复）的额定比较。
  I²t（A²s）按实测波形积分；只有峰值和时宽时按 1006 6.5.3（p15–16）的波形式计算：尖波 Ip²t/3、梯形波 (Ia²+Ia·Ib+Ib²)t/3、
  矩形波 Ip²t、脉冲波 Ip²t/5、拱形波 Ip²t/2；交流输入取 0°、90°、180°、270° 开机的最大值。不能只比峰值，也不能套用别的波形的式子。
  手册给温度或脉宽修正曲线的，先按曲线修正额定（R4），不再叠加 `per_c_above_25` 之类的通用温度系数。
- **R10 寿命口径**：`ctr_drop`（OPTO-CTR）是寿命期 CTR 下降的设计容限：电路在 CTR 比设计取值低 15% 时仍要正常工作，
  不是厂家保证的最大老化量。设计取值取工作温度范围内最低处的 CTR（分档下限 × 温度曲线最低点；按典型曲线估算时另有估算倍数，
  如 SR 定界表的 ÷2，那是曲线的不确定度，不算寿命）。核法二选一：设计取值乘 0.85 再核；或算出这条链寿命末所需的
  CTR 保留比例（所需 CTR ÷ 设计取值），不高于 85% 即满足。厂家给了 CTR 随时间的曲线时按曲线，不另编系数。
- **R12 余量不叠加，同时成立的条件照叠**：一个量只取一份人为余量（降额系数、估算倍数、设计容限），不在同一个量上连乘几份；
  物理上同时成立的条件照叠，例如寿命末与最高工作温度、浪涌叠在电网峰值上；互相独立的偶发事件不叠，例如浪涌与输出短路。
- **R11 已有计算方法**：MOS 高温 SOA（按持续时间选曲线、按开始壳温降额）、电位器局部轨段与滑臂、电解电容寿命、开关次数类寿命，
  按各自的计算方法得出应力或允许值后再套本表（SR：`references/bounding-table.md`、`references/wca-formulas.md`、
  `references/commodity-floors.md`），不在本表之外另乘系数，也不重复降额。
- **R6 判定**：按 [器件应力规范](stress-spec.md)：超过额定值为不成立；在额定值内但超过降额值为合格但有风险（应力），
  不挡定稿（1013 5.1、GJB 4.4 允许经评估偏离降额值）；只审写出来的应力余量，不要求逐器件全覆盖。

## 判据与工况

| 判据（`measure`） | 含义 |
|---|---|
| ratio | 最坏应力 / 同条件下的额定值 ≤ 取值；负向额定按幅值比较（R8） |
| pulse_ratio | 冲击或脉冲应力 / 手册单列的冲击或脉冲额定值 ≤ 取值 |
| min_ratio | 实际值 / 额定值 ≥ 取值 |
| margin_c | 额定最高温度 − 最坏工作温度 ≥ 取值（°C） |
| max_c | 最坏工作温度 ≤ 取值（°C） |
| max_rise_k | 温升 ≤ 取值（K） |
| tj_percent | 结温 ≤ (Tjmax − 25 °C) × 取值 + 25 °C |
| max_v | 残压 ≤ 取值（V） |
| min_hours / min_years | 寿命 ≥ 取值（h / 年） |
| flux_margin_t | 最大磁通密度 ≤ Bmax − 取值（T） |
| max_dvdt | dv/dt ≤ 取值（V/ns） |
| per_c_above_25 | 环境温度高于 25 °C 时每升高 1 °C 附加降额取值 |
| ctr_drop | 寿命期内 CTR 下降取值后电路仍正常工作 |
| text | 按文字要求 |

工况（`condition`）：`worst` 稳态与瞬态的最坏组合，`steady` 稳态，`transient` 瞬态，`pulse` 对手册单列的冲击或脉冲额定，
`temperature` 温度，`life` 寿命。

## 没有收录的

- 压敏电阻“工作电压/最大限制电压 ≤30%”（1006 表1）含义不明，未收录；压敏电阻的连续工作电压按手册额定校核。
- Y 电容漏电流、NTC 浪涌限流器的冲击能力：三份标准都没有降额值，只校核手册额定。
- 断路器、风扇、电机、灯泡、电真空、声表面波、激光与光纤器件：本规范不收录，用到时按 GJB/Z 35 原文补。

## NB/T 10297 的差异

NB/T 10297 不进默认取值（R1 的顺序不变），也不并进上面的表：同一参数两份标准的数值不同，不能当成同一要求的另一个出处。
项目需求点名 NB/T 10297 时，按它的条款逐条核对，不用本表数值代替。已核对的差异举例（NB/T p7 表1，对 1013 p5 表1）：

| 参数 | 本表（1013）I / II / III | NB/T I / II / III |
|---|---|---|
| 贴片电阻温度（低于 PCB 最高温度） | 10 / 5 / 5 °C | >30 / >20 / >10 °C |
| 贴片电阻电压 | 75% / 80% / 90% | <70% / <75% / <75% |
| 贴片电阻功率 | 70% / 75% / 80% | <65%（三级同值） |
| 碳膜、金属膜电阻电压 | 75% / 85% / 90% | <70% / <80% / <80% |
| 金属氧化膜电阻温度 | 35 / 30 / 25 °C | >50 / >40 / >40 °C |

其余器件的差异未逐条列出；用 NB/T 时以原文为准。

## 降额值

### 电阻

| 编号 | 类型 | 参数 | 工况 | 判据 | I / II / III | 出处 |
|---|---|---|---|---|---|---|
| RES-FILM-V | 碳膜、金属膜电阻 | 电压 | worst | ratio | 75% / 85% / 90% | 1013 p5 表1 |
| RES-FILM-P | 碳膜、金属膜电阻 | 功率 | worst | ratio | 70% / 75% / 80% | 1013 p5 表1 |
| RES-FILM-T | 碳膜、金属膜电阻 | 温度 | temperature | margin_c | 30 / 25 / 20；卧式平贴 PCB 安装时还要比 PCB 额定温度低 10 °C（表1 注） | 1013 p5 表1 |
| RES-OXIDE-V | 金属氧化膜电阻 | 电压 | worst | ratio | 75% / 85% / 90% | 1013 p5 表1 |
| RES-OXIDE-P | 金属氧化膜电阻 | 功率 | worst | ratio | 70% / 75% / 80% | 1013 p5 表1 |
| RES-OXIDE-T | 金属氧化膜电阻 | 温度 | temperature | margin_c | 35 / 30 / 25；卧式平贴 PCB 安装时还要比 PCB 额定温度低 10 °C（表1 注） | 1013 p5 表1 |
| RES-WW-V | 线绕电阻 | 电压 | worst | ratio | 75% / 80% / 90% | 1013 p5 表1 |
| RES-WW-P | 线绕电阻 | 功率 | worst | ratio | 70% / 70% / 80% | 1013 p5 表1 |
| RES-WW-T | 线绕电阻 | 温度 | temperature | margin_c | 20 / 15 / 10；卧式平贴 PCB 安装时还要比 PCB 额定温度低 10 °C（表1 注） | 1013 p5 表1 |
| RES-SMD-V | 表面贴装电阻 | 电压 | worst | ratio | 75% / 80% / 90% | 1013 p5 表1 |
| RES-SMD-P | 表面贴装电阻 | 功率 | worst | ratio | 70% / 75% / 80% | 1013 p5 表1 |
| RES-SMD-T | 表面贴装电阻 | 温度 | temperature | margin_c | 10 / 5 / 5；对 PCB 最高温度 | 1013 p5 表1 |
| RES-VAR-P | 可变电阻 | 功率 | worst | ratio | 60% / 65% / 65% | 1013 p5 表1 |
| RES-VAR-T | 可变电阻（非线绕） | 温度 | temperature | margin_c | 20 / 20 / 10 | 1013 p5 表1 |
| RES-VARWW-T | 可变电阻（线绕） | 温度 | temperature | margin_c | 10 / 10 / 5 | 1013 p5 表1 |
| RES-NET-V | 电阻网络 | 电压 | worst | ratio | 75%（三级同值） | GJB p16 表18 |
| RES-NET-P | 电阻网络 | 功率 | worst | ratio | 50% / 60% / 70% | GJB p16 表18 |
| RES-NET-T | 电阻网络 | 温度 | temperature | margin_c | 24（三级同值）；GJB/Z 35 表18 只写“按负荷特性曲线降额”，取 T/CPSS 1006 | 1006 p6 表1 |
| RES-FILM-PULSE | 膜式电阻 | 脉冲功率 | pulse | pulse_ratio | 100%（三级同值） | 1006 p5 表1 |
| RES-WW-PULSE | 线绕电阻 | 脉冲功率 | pulse | pulse_ratio | 100%（三级同值） | 1006 p6 表1 |
| RES-ZERO-I | 零欧电阻 | 电流 | worst | ratio | 85%（三级同值） | 1006 p5 表1 |

### 热敏电阻

| 编号 | 类型 | 参数 | 工况 | 判据 | I / II / III | 出处 |
|---|---|---|---|---|---|---|
| NTC-P | 热敏电阻 | 功率 | worst | ratio | 70% / 80% / 90% | 1013 p5 表1 |
| NTC-T | 热敏电阻 | 温度 | temperature | margin_c | 20 / 15 / 10 | 1013 p5 表1 |

### 压敏电阻

| 编号 | 类型 | 参数 | 工况 | 判据 | I / II / III | 出处 |
|---|---|---|---|---|---|---|
| MOV-SURGE | 压敏电阻 | 最大冲击电流（8/20 µs） | pulse | pulse_ratio | 100%（三级同值） | 1013 p5 表1 |
| MOV-T | 压敏电阻 | 温度 | temperature | margin_c | 30 / 20 / 10 | 1013 p5 表1 |
| MOV-E | 压敏电阻 | 最大能量 | pulse | pulse_ratio | 90%（三级同值） | 1006 p6 表1 |

### 电容

| 编号 | 类型 | 参数 | 工况 | 判据 | I / II / III | 出处 |
|---|---|---|---|---|---|---|
| CAP-MLCC-LEAD-V | 引线陶瓷电容 | 直流电压（直流加交流峰值） | worst | ratio | 75% / 80% / 85% | 1013 p6 表2 |
| CAP-MLCC-LEAD-T | 引线陶瓷电容 | 温度 | temperature | margin_c | 10 / 7 / 5 | 1013 p6 表2 |
| CAP-MLCC-CHIP-V | 片状陶瓷电容 | 直流电压（直流加交流峰值） | worst | ratio | 80% / 90% / 95% | 1013 p6 表2 |
| CAP-MLCC-CHIP-T | 片状陶瓷电容 | 温度 | temperature | margin_c | 10（三级同值） | 1013 p6 表2 |
| CAP-FILM-V | 塑胶膜电容 | 直流电压（直流加交流峰值） | worst | ratio | 80% / 85% / 90% | 1013 p6 表2 |
| CAP-FILM-T | 塑胶膜电容 | 温度 | temperature | margin_c | 10 / 7 / 5 | 1013 p6 表2 |
| CAP-AL-V-LOW | 铝电解电容（额定 ≤200 V） | 直流电压（直流加交流峰值） | worst | ratio | 90% / 93% / 95% | 1013 p6 表2 |
| CAP-AL-V-HIGH | 铝电解电容（额定 >200 V） | 直流电压（直流加交流峰值） | worst | ratio | 95% / 98% / 100%；原表两行写 ≤200 V 与 ≥200 V，额定正好 200 V 的取较严的上一行 | 1013 p6 表2 |
| CAP-AL-SURGE | 铝电解电容 | 直流电压（冲击） | pulse | pulse_ratio | 100%（三级同值） | 1013 p6 表2 |
| CAP-AL-RIPPLE | 铝电解电容 | 纹波电流 | steady | ratio | 80% / 100% / 100% | 1013 p6 表2 |
| CAP-AL-LIFE | 铝电解电容 | 常温 25 °C 下工作寿命 | life | min_hours | 50000 / 30000 / 20000 | 1013 p6 表2 |
| CAP-AL-RESIDUAL | 铝电解电容（交流-直流电源输入回路） | 浪涌或振铃波抗扰度残压 | transient | max_v | 600 / 800 / 1000；只适用于交流-直流开关电源输入回路上的铝电解电容；试验按 GB/T 17626.5、17626.12（1013 6.6） | 1013 p6 表2 |
| CAP-AL-T | 铝电解电容 | 温度 | temperature | margin_c | 10 / 7 / 5 | 1013 p6 表2 |
| CAP-TA-V | 固体钽电容 | 直流电压（直流加交流峰值） | worst | ratio | 50% / 60% / 70%；电路中应有不小于每伏 3 Ω 的等效串联阻抗（GJB/Z 35 5.8.5.2.3） | 1013 p6 表2 |
| CAP-TA-RIPPLE | 固体钽电容 | 纹波电流 | steady | ratio | 70% / 80% / 100% | 1013 p6 表2 |
| CAP-TA-REV | 固体钽电容 | 反向电压（峰值） | worst | ratio | 2%（三级同值） | 1013 p6 表2 |
| CAP-TA-T | 固体钽电容 | 温度 | temperature | margin_c | 15 / 13 / 10 | 1013 p6 表2 |
| CAP-XY-V | 抑制电源电磁干扰电容（X、Y） | 交流电压 | worst | ratio | 100%（三级同值） | 1013 p6 表2 |
| CAP-XY-T | 抑制电源电磁干扰电容（X、Y） | 温度 | temperature | margin_c | 10 / 10 / 5 | 1013 p6 表2 |
| CAP-POLY-V | 导电聚合物铝或钽电解电容 | 直流电压 | worst | ratio | 70%（三级同值） | 1006 p7 表2 |
| CAP-POLY-RIPPLE | 导电聚合物铝或钽电解电容 | 纹波电流 | steady | ratio | 80%（三级同值） | 1006 p7 表2 |
| CAP-POLY-T | 导电聚合物铝或钽电解电容 | 温度 | temperature | margin_c | 10（三级同值） | 1006 p7 表2 |
| CAP-POLY-LIFE | 导电聚合物铝或钽电解电容 | 寿命 | life | min_years | 10（三级同值）；40 °C、80% 负载 | 1006 p7 表2 |
| CAP-OS-V | 有机半导体电解电容 | 直流电压 | worst | ratio | 80%（三级同值） | 1006 p7 表2 |
| CAP-OS-RIPPLE | 有机半导体电解电容 | 纹波电流 | steady | ratio | 80%（三级同值） | 1006 p7 表2 |
| CAP-OS-T | 有机半导体电解电容 | 温度 | temperature | margin_c | 20（三级同值） | 1006 p7 表2 |
| CAP-OS-LIFE | 有机半导体电解电容 | 寿命 | life | min_years | 10（三级同值）；40 °C、80% 负载 | 1006 p7 表2 |

### 二极管与 LED

| 编号 | 类型 | 参数 | 工况 | 判据 | I / II / III | 出处 |
|---|---|---|---|---|---|---|
| DIO-GEN-IF | 普通二极管（信号或开关用） | 正向导通电流 | steady | ratio | 80% / 85% / 90% | 1013 p6 表3 |
| DIO-GEN-SURGE | 普通二极管（信号或开关用） | 冲击电流 | pulse | pulse_ratio | 80% / 85% / 90% | 1013 p6 表3 |
| DIO-GEN-VR-S | 普通二极管（信号或开关用） | 反向电压 | steady | ratio | 80% / 90% / 95% | 1013 p6 表3 |
| DIO-GEN-VR-T | 普通二极管（信号或开关用） | 反向电压 | transient | ratio | 90% / 95% / 100% | 1013 p6 表3 |
| DIO-GEN-TJ | 普通二极管（信号或开关用） | 最高结温 | temperature | tj_percent | 70% / 80% / 90% | 1013 p6 表3 |
| DIO-GEN-P | 普通二极管（信号或开关用） | 功率 | worst | ratio | 50% / 65% / 80% | GJB p12 表10 |
| DIO-REC-IF | 功率整流二极管、整流桥 | 正向导通电流 | steady | ratio | 80% / 85% / 90% | 1013 p6 表3 |
| DIO-REC-SURGE | 功率整流二极管、整流桥 | 冲击电流 | pulse | pulse_ratio | 90%（三级同值） | 1013 p6 表3 |
| DIO-REC-I2T | 功率整流二极管、整流桥 | 开机浪涌电流能量（I²t） | pulse | pulse_ratio | 25% / 30% / 35% | 1013 p6 表3 |
| DIO-REC-VR-S | 功率整流二极管、整流桥 | 反向电压 | steady | ratio | 80% / 90% / 95% | 1013 p6 表3 |
| DIO-REC-VR-T | 功率整流二极管、整流桥 | 反向电压 | transient | ratio | 95% / 98% / 100% | 1013 p6 表3 |
| DIO-REC-TJ | 功率整流二极管、整流桥 | 最高结温 | temperature | tj_percent | 70% / 80% / 90% | 1013 p6 表3 |
| DIO-REC-RESIDUAL | 功率整流二极管、整流桥 | 浪涌或振铃波抗扰度残压 | transient | max_v | 600 / 800 / 1000 | 1013 p6 表3 |
| DIO-REC-P | 功率整流二极管、整流桥 | 功率 | worst | ratio | 50% / 65% / 80% | GJB p12 表10 |
| DIO-SIC-IF | SiC 功率二极管 | 正向电流 | steady | ratio | 80%（三级同值） | 1006 p7 表3 |
| DIO-SIC-VR | SiC 功率二极管 | 反向电压 | worst | ratio | 80%（三级同值） | 1006 p7 表3 |
| DIO-SIC-TJ | SiC 功率二极管 | 结温 | temperature | margin_c | 25（三级同值） | 1006 p8 表3 |
| LED-IF | 发光二极管（LED） | 正向导通电流 | steady | ratio | 75% / 80% / 85% | 1013 p8 表6 |
| LED-T | 发光二极管（LED） | 外壳温度 | temperature | margin_c | 10 / 8 / 6；对最高外壳工作温度 Topr；原表 II 级误印为 Tsec | 1013 p8 表6 |
| LED-VR | 发光二极管（LED） | 反向峰值电压 | worst | ratio | 80%（三级同值） | 1006 p10 表7 |
| LED-P | 发光二极管（LED） | 功率 | worst | ratio | 70%（三级同值） | 1006 p10 表7 |

### TVS

| 编号 | 类型 | 参数 | 工况 | 判据 | I / II / III | 出处 |
|---|---|---|---|---|---|---|
| TVS-IF | 瞬态吸收二极管（TVS） | 正向导通电流 | steady | ratio | 80% / 85% / 90% | 1013 p6 表3 |
| TVS-SURGE | 瞬态吸收二极管（TVS） | 冲击电流 | pulse | pulse_ratio | 100%（三级同值）；冲击额定按手册的脉宽与温度曲线修正后再比 | 1013 p6 表3 |
| TVS-VR-S | 瞬态吸收二极管（TVS） | 反向电压 | steady | ratio | 80% / 90% / 95% | 1013 p6 表3 |
| TVS-VR-T | 瞬态吸收二极管（TVS） | 反向电压 | transient | ratio | 95% / 98% / 100% | 1013 p6 表3 |
| TVS-TJ | 瞬态吸收二极管（TVS） | 最高结温 | temperature | tj_percent | 70% / 80% / 90% | 1013 p6 表3 |

### 稳压管

| 编号 | 类型 | 参数 | 工况 | 判据 | I / II / III | 出处 |
|---|---|---|---|---|---|---|
| ZD-P | 稳压二极管 | 功率 | worst | ratio | 70% / 80% / 85% | 1013 p7 表3 |
| ZD-TJ | 稳压二极管 | 最高结温 | temperature | tj_percent | 70% / 80% / 90% | 1013 p7 表3 |

### 三极管

| 编号 | 类型 | 参数 | 工况 | 判据 | I / II / III | 出处 |
|---|---|---|---|---|---|---|
| BJT-VCE-S | 三极管 | 集电极-发射极电压 | steady | ratio | 85% / 90% / 95% | 1013 p7 表4 |
| BJT-VCE-T | 三极管 | 集电极-发射极电压 | transient | ratio | 95% / 98% / 100% | 1013 p7 表4 |
| BJT-VEB-S | 三极管 | 发射极-基极电压 | steady | ratio | 85% / 90% / 95% | 1013 p7 表4 |
| BJT-VEB-T | 三极管 | 发射极-基极电压 | transient | ratio | 95% / 98% / 100% | 1013 p7 表4 |
| BJT-IC | 三极管 | 集电极电流 | worst | ratio | 80%（三级同值） | 1013 p7 表4 |
| BJT-TJ | 三极管 | 最高结温 | temperature | tj_percent | 70% / 80% / 90% | 1013 p7 表4 |
| BJT-P | 三极管 | 功率 | worst | ratio | 50% / 65% / 75% | GJB p10 表7 |
| BJT-SOA-V | 功率三极管 | 安全工作区：集电极-发射极电压 | worst | ratio | 70% / 80% / 90% | GJB p11 表9 |
| BJT-SOA-I | 功率三极管 | 安全工作区：集电极最大允许电流 | worst | ratio | 60% / 70% / 80% | GJB p11 表9 |

### MOSFET、IGBT、GaN、SiC

机器数据同属 `mosfet`，按 `subtype` 分：MOS-* 为 `si`，IGBT-* 为 `igbt`，GAN-* 为 `gan`，SIC-* 为 `sic`（R7）。

| 编号 | 类型 | 参数 | 工况 | 判据 | I / II / III | 出处 |
|---|---|---|---|---|---|---|
| MOS-VDS-S | 硅 MOSFET | 漏-源极电压 | steady | ratio | 70% / 80% / 90% | 1013 p7 表4 |
| MOS-VDS-T | 硅 MOSFET | 漏-源极电压 | transient | ratio | 80% / 90% / 100% | 1013 p7 表4 |
| MOS-VGS-S | 硅 MOSFET | 栅-源极电压 | steady | ratio | 80% / 85% / 90% | 1013 p7 表4 |
| MOS-VGS-T | 硅 MOSFET | 栅-源极电压 | transient | ratio | 90% / 95% / 100% | 1013 p7 表4 |
| MOS-ID | 硅 MOSFET | 漏极电流 | steady | ratio | 80% / 85% / 90% | 1013 p7 表4 |
| MOS-IDM | 硅 MOSFET | 漏极电流脉冲 | pulse | pulse_ratio | 90% / 95% / 100% | 1013 p7 表4 |
| MOS-TJ | 硅 MOSFET | 最高结温 | temperature | tj_percent | 70% / 80% / 90% | 1013 p7 表4 |
| MOS-P | 硅 MOSFET | 功率 | worst | ratio | 50% / 65% / 75% | GJB p10 表7 |
| MOS-DVDT | 硅 MOSFET | 漏-源极电压上升率（体二极管反向恢复） | transient | max_dvdt | 5（三级同值） | 1006 p8 表4 |
| IGBT-VCE-LV | IGBT（额定 <200 V） | 集电极-发射极电压 | worst | ratio | 90%（三级同值） | 1006 p8 表4 |
| IGBT-VCE-S | IGBT（额定 ≥200 V） | 集电极-发射极电压（平台及重复尖峰） | steady | ratio | 80%（三级同值） | 1006 p8 表4 |
| IGBT-VCE-T | IGBT（额定 ≥200 V） | 集电极-发射极电压（单次尖峰） | transient | ratio | 95%（三级同值） | 1006 p8 表4 |
| IGBT-VGE | IGBT | 栅-发射极电压 | worst | ratio | 80%（三级同值） | 1006 p8 表4 |
| IGBT-IC | IGBT | 集电极电流 | worst | ratio | 90%（三级同值） | 1006 p8 表4 |
| IGBT-P | IGBT | 功耗 | worst | ratio | 80%（三级同值） | 1006 p8 表4 |
| IGBT-TJ | IGBT | 结温 | temperature | margin_c | 25（三级同值） | 1006 p8 表4 |
| GAN-VDS | GaN HFET（增强型） | 漏-源极电压 | worst | ratio | 80%（三级同值） | 1006 p8 表4 |
| GAN-VGS-ON | GaN HFET（增强型） | 栅-源极电压（开通正压） | worst | ratio | 90%（三级同值） | 1006 p9 表4 |
| GAN-VGS-OFF | GaN HFET（增强型） | 栅-源极电压（关断负压） | worst | ratio | 50%（三级同值） | 1006 p9 表4 |
| GAN-ID | GaN HFET（增强型） | 漏极电流 | worst | ratio | 80%（三级同值） | 1006 p9 表4 |
| GAN-P | GaN HFET（增强型） | 功耗 | worst | ratio | 80%（三级同值） | 1006 p9 表4 |
| GAN-TJ | GaN HFET（增强型） | 结温 | temperature | margin_c | 25（三级同值） | 1006 p9 表4 |
| SIC-VDS | SiC MOSFET（增强型） | 漏-源极电压 | worst | ratio | 90%（三级同值） | 1006 p9 表4 |
| SIC-VGS-ON | SiC MOSFET（增强型） | 栅-源极电压（开通正压） | worst | ratio | 80%（三级同值） | 1006 p9 表4 |
| SIC-VGS-OFF | SiC MOSFET（增强型） | 栅-源极电压（关断负压） | worst | ratio | 50%（三级同值） | 1006 p9 表4 |
| SIC-ID | SiC MOSFET（增强型） | 漏极电流 | worst | ratio | 80%（三级同值） | 1006 p9 表4 |
| SIC-P | SiC MOSFET（增强型） | 功耗 | worst | ratio | 80%（三级同值） | 1006 p9 表4 |
| SIC-TJ | SiC MOSFET（增强型） | 结温 | temperature | margin_c | 20（三级同值） | 1006 p9 表4 |

### 可控硅

| 编号 | 类型 | 参数 | 工况 | 判据 | I / II / III | 出处 |
|---|---|---|---|---|---|---|
| SCR-I | 可控硅 | 导通电流 | steady | ratio | 80% / 80% / 90% | 1013 p7 表4 |
| SCR-SURGE | 可控硅 | 冲击电流 | pulse | pulse_ratio | 80% / 90% / 95% | 1013 p7 表4 |
| SCR-V | 可控硅 | 关闭电压 | worst | ratio | 80% / 80% / 90% | 1013 p7 表4 |
| SCR-TJ | 可控硅 | 最高结温 | temperature | tj_percent | 70% / 80% / 90% | 1013 p7 表4 |

### 集成电路

| 编号 | 类型 | 参数 | 工况 | 判据 | I / II / III | 出处 |
|---|---|---|---|---|---|---|
| IC-DRV-VCC | 驱动、PWM 控制、运算放大器、比较器 | 供电电压 | worst | ratio | 90% / 93% / 95%；且不低于最小工作电压 | 1013 p7 表5 |
| IC-DRV-TJ | 驱动、PWM 控制、运算放大器、比较器 | 最高结温 | temperature | tj_percent | 75% / 75% / 80% | 1013 p7 表5 |
| IC-LDO-VIN | 三端稳压器 | 供电电压 | worst | ratio | 75% / 80% / 90% | 1013 p7 表5 |
| IC-LDO-I | 三端稳压器 | 电流 | worst | ratio | 75% / 80% / 90% | 1013 p7 表5 |
| IC-LDO-TJ | 三端稳压器 | 最高结温 | temperature | tj_percent | 80% / 80% / 90% | 1013 p7 表5 |
| IC-LDO-VDIFF | 三端稳压器 | 输入输出电压差 | worst | ratio | 70% / 80% / 85% | GJB p8 表3 |
| IC-LDO-P | 三端稳压器 | 功率 | worst | ratio | 70% / 75% / 80% | GJB p8 表3 |
| IC-AMP-VIN | 运算放大器 | 输入电压 | worst | ratio | 60% / 70% / 70%；输入电压在任何情况下不得超过电源电压 | GJB p8 表3 |
| IC-AMP-IOUT | 运算放大器 | 输出电流 | worst | ratio | 70% / 80% / 80% | GJB p8 表3 |
| IC-AMP-P | 运算放大器 | 功率 | worst | ratio | 70% / 75% / 80% | GJB p8 表3 |
| IC-CMP-VIN | 比较器 | 输入电压 | worst | ratio | 70% / 80% / 80%；输入电压在任何情况下不得超过电源电压 | GJB p8 表3 |
| IC-CMP-IOUT | 比较器 | 输出电流 | worst | ratio | 70% / 80% / 80% | GJB p8 表3 |
| IC-CMP-P | 比较器 | 功率 | worst | ratio | 70% / 75% / 80% | GJB p8 表3 |
| IC-SW-VCC | 模拟开关 | 电源电压 | worst | ratio | 70% / 80% / 85%；降额后不应小于推荐的正常工作电压 | GJB p8 表3 |
| IC-SW-VIN | 模拟开关 | 输入电压 | worst | ratio | 80% / 85% / 90% | GJB p8 表3 |
| IC-SW-IOUT | 模拟开关 | 输出电流 | worst | ratio | 75% / 80% / 85% | GJB p8 表3 |
| IC-SW-P | 模拟开关 | 功率 | worst | ratio | 70% / 75% / 80% | GJB p8 表3 |
| IC-SW-TJ | 模拟开关 | 最高结温 | temperature | max_c | 80 / 95 / 105 | GJB p8 表3 |
| IC-MOS-VCC | MOS 型数字电路（含 MCU） | 电源电压 | worst | ratio | 70% / 80% / 80%；降额后不应小于推荐的正常工作电压；输入电压任何情况下不得超过电源电压 | GJB p9 表5 |
| IC-MOS-IOUT | MOS 型数字电路（含 MCU） | 输出电流 | worst | ratio | 80% / 90% / 90%；仅适用于缓冲器和触发器 | GJB p9 表5 |
| IC-MOS-F | MOS 型数字电路（含 MCU） | 频率 | worst | ratio | 80% / 80% / 90% | GJB p9 表5 |
| IC-MOS-TJ | MOS 型数字电路（含 MCU） | 最高结温 | temperature | max_c | 85 / 100 / 115 | GJB p9 表5 |
| IC-BIP-F | 双极型数字电路 | 频率 | worst | ratio | 80% / 90% / 90% | GJB p8 表4 |
| IC-BIP-IOUT | 双极型数字电路 | 输出电流 | worst | ratio | 80% / 90% / 90% | GJB p8 表4 |
| IC-BIP-TJ | 双极型数字电路 | 最高结温 | temperature | max_c | 85 / 100 / 115 | GJB p8 表4 |
| IC-OTH-VMAX | 其他模拟、混合信号集成电路 | 电源电压上限 | worst | ratio | 90%（三级同值）；对额定最大工作电压 | 1006 p10 表6 |
| IC-OTH-VMIN | 其他模拟、混合信号集成电路 | 电源电压下限 | worst | min_ratio | 105%（三级同值）；对额定最小工作电压 | 1006 p10 表6 |
| IC-OTH-VIN | 其他模拟、混合信号集成电路 | 输入电压 | worst | ratio | 85%（三级同值） | 1006 p10 表6 |
| IC-OTH-IOUT | 其他模拟、混合信号集成电路 | 输出电流 | worst | ratio | 80%（三级同值） | 1006 p10 表6 |
| IC-OTH-TJ | 其他模拟、混合信号集成电路 | 结温 | temperature | margin_c | 25（三级同值） | 1006 p10 表6 |

### 光耦

| 编号 | 类型 | 参数 | 工况 | 判据 | I / II / III | 出处 |
|---|---|---|---|---|---|---|
| OPTO-IF | 光电耦合器 | 输入正向导通电流 | steady | ratio | 75% / 80% / 85% | 1013 p8 表6 |
| OPTO-VR | 光电耦合器 | 输入反向电压 | worst | ratio | 75% / 80% / 85% | 1013 p8 表6 |
| OPTO-VO | 光电耦合器 | 输出电压 | worst | ratio | 80% / 85% / 90% | 1013 p8 表6 |
| OPTO-IO | 光电耦合器 | 输出集电极电流 | worst | ratio | 80% / 85% / 90% | 1013 p8 表6 |
| OPTO-TC-FAN | 光电耦合器（带风扇散热产品） | 外壳温度 | temperature | margin_c | 20 / 15 / 10 | 1013 p8 表6 |
| OPTO-TC | 光电耦合器（无风扇散热产品） | 外壳温度 | temperature | margin_c | 15 / 10 / 5 | 1013 p8 表6 |
| OPTO-TJ | 光电耦合器 | 最高结温 | temperature | tj_percent | 60% / 70% / 80% | 1013 p8 表6 |
| OPTO-CTR | 光电耦合器 | 电流传输比 | life | ctr_drop | 0.15（三级同值） | GJB p14 5.5.2.3 |

### 变压器

| 编号 | 类型 | 参数 | 工况 | 判据 | I / II / III | 出处 |
|---|---|---|---|---|---|---|
| XFMR-WIND-B | 变压器绕组（B 级 130 °C） | 最高温度 | temperature | max_c | 105 / 108 / 110 | 1013 p8 表7 |
| XFMR-WIND-F | 变压器绕组（F 级 155 °C） | 最高温度 | temperature | max_c | 125 / 128 / 130 | 1013 p8 表7 |
| XFMR-BSAT | 变压器 | 磁饱和度 | worst | flux_margin_t | 0.05（三级同值） | 1013 p8 表7 |

### 电感与磁芯

| 编号 | 类型 | 参数 | 工况 | 判据 | I / II / III | 出处 |
|---|---|---|---|---|---|---|
| IND-WIND-B | 电感绕组（B 级 130 °C） | 最高温度 | temperature | max_c | 110 / 120 / 130 | 1013 p8 表7 |
| IND-WIND-F | 电感绕组（F 级 155 °C） | 最高温度 | temperature | max_c | 135 / 145 / 155 | 1013 p8 表7 |
| IND-BSAT | 电感 | 磁饱和度（峰值电流 / 最高温度下的饱和电流） | worst | ratio | 100%（三级同值） | 1013 p8 表7 |
| CORE-FE-POWDER | 铁粉芯磁芯 | 最高温度 | temperature | max_c | 125（三级同值）；IPC-9592 不推荐铁粉芯，限 Buck 输出滤波电感（表7 注2） | 1013 p8 表7 |
| CORE-FERRITE | 铁氧体磁芯 | 最高温度 | temperature | max_c | 115 / 118 / 120 | 1013 p8 表7 |
| CORE-ALLOY | 钼坡莫合金粉末、高磁通密度铁镍磁粉芯、非晶态磁芯 | 最高温度 | temperature | max_c | 115 / 118 / 120 | 1013 p8 表7 |
| MAG-TRANSIENT | 电感元件 | 瞬态电压/电流 | transient | ratio | 90%（三级同值） | GJB p23 表29 |
| MAG-DIELECTRIC | 电感元件 | 介质耐压 | worst | ratio | 50%（三级同值）；原文范围 0.5~0.6，取保守端 | GJB p23 表29 |
| MAG-CHOKE-V | 扼流线圈 | 电压 | worst | ratio | 70%（三级同值） | GJB p23 表29 |

### 保险丝

| 编号 | 类型 | 参数 | 工况 | 判据 | I / II / III | 出处 |
|---|---|---|---|---|---|---|
| FUSE-V | 熔断体 | 电压 | worst | ratio | 100%（三级同值） | 1013 p9 表8 |
| FUSE-I | 熔断体 | 电流 | steady | ratio | 75%（三级同值）；额定电流先按手册的温度折减曲线修正 | 1013 p9 表8 |
| FUSE-I2T | 熔断体 | 开机浪涌电流能量（I²t） | pulse | pulse_ratio | 25% / 30% / 35% | 1013 p9 表8 |
| FUSE-TEMP | 熔断体 | 电流的温度附加降额 | temperature | per_c_above_25 | 0.005（三级同值） | GJB p29 表36 |
| PPTC-I | 自恢复保险丝 | 工作电流 | steady | ratio | 50%（三级同值） | 1006 p11 表8 |
| PPTC-IFAULT | 自恢复保险丝 | 故障电流 | transient | ratio | 50%（三级同值） | 1006 p11 表8 |
| PPTC-V | 自恢复保险丝 | 工作电压 | worst | ratio | 70%（三级同值） | 1006 p11 表8 |

### 连接器

| 编号 | 类型 | 参数 | 工况 | 判据 | I / II / III | 出处 |
|---|---|---|---|---|---|---|
| CPLR-V | 器具耦合器 | 电压 | worst | ratio | 80% / 80% / 90% | 1013 p8 表8 |
| CPLR-I | 器具耦合器 | 电流 | worst | ratio | 80% / 80% / 100% | 1013 p8 表8 |
| CPLR-T | 器具耦合器 | 温度 | temperature | margin_c | 15 / 15 / 10 | 1013 p8 表8 |
| USB-I | USB 母座 | 电流 | worst | ratio | 80% / 80% / 90% | 1013 p9 表8 |
| USB-RISE | USB 母座 | 温升 | temperature | max_rise_k | 8 / 10 / 15 | 1013 p9 表8 |
| USB-TOUCH | USB 母座 | 最大温度（人体可触及部位） | temperature | max_c | 70（三级同值） | 1013 p9 表8 |
| USB-TMAX | USB 母座 | 最大温度 | temperature | max_c | 85（三级同值） | 1013 p9 表8 |
| CONN-V | 其他电连接器 | 工作电压（DC 或 AC） | worst | ratio | 50% / 70% / 80% | GJB p26 表32 |
| CONN-I | 其他电连接器 | 工作电流 | worst | ratio | 50% / 70% / 85%；接触对并联时，按降额后的电流再多 25% 的接触对（5.12.2.2） | GJB p26 表32 |
| CONN-T | 其他电连接器 | 温度 | temperature | margin_c | 50 / 25 / 20；对最高接触对额定温度，含自身温升 | GJB p26 表32 |

### 线材

| 编号 | 类型 | 参数 | 工况 | 判据 | I / II / III | 出处 |
|---|---|---|---|---|---|---|
| WIRE-V | 线材 | 电压 | worst | ratio | 80% / 80% / 90% | 1013 p8 表8 |
| WIRE-I | 线材 | 电流 | worst | ratio | 80% / 80% / 90%；成束导线另按 GJB/Z 35 5.13.3.2 折算 | 1013 p8 表8 |
| WIRE-T | 线材 | 温度 | temperature | margin_c | 15 / 15 / 10 | 1013 p8 表8 |

### PCB

| 编号 | 类型 | 参数 | 工况 | 判据 | I / II / III | 出处 |
|---|---|---|---|---|---|---|
| PCB-T | 印制电路板 | 温度 | temperature | margin_c | 10 / 10 / 0 | 1013 p8 表8 |

### 外壳

| 编号 | 类型 | 参数 | 工况 | 判据 | I / II / III | 出处 |
|---|---|---|---|---|---|---|
| ENC-METAL | 外壳金属表面 | 最大温度 | temperature | max_c | 67 / 70 / 70 | 1013 p9 表9 |
| ENC-PLASTIC | 外壳塑胶表面 | 最大温度 | temperature | max_c | 90（三级同值） | 1013 p9 表9 |
| ENC-CHARGER | 充电器塑胶表面 | 温升 | temperature | max_rise_k | 25（三级同值） | 1013 p9 表9 |

### 继电器

| 编号 | 类型 | 参数 | 工况 | 判据 | I / II / III | 出处 |
|---|---|---|---|---|---|---|
| RLY-R | 继电器 | 连续触点电流：电阻负载 | worst | ratio | 50% / 75% / 90%；小功率负载（<100 mW）不降额 | GJB p24 表30 |
| RLY-C | 继电器 | 连续触点电流：电容负载（最大浪涌电流） | worst | ratio | 50% / 75% / 90% | GJB p24 表30 |
| RLY-L | 继电器 | 连续触点电流：电感负载（对电感额定电流） | worst | ratio | 50% / 75% / 90% | GJB p24 表30 |
| RLY-L-R | 继电器 | 连续触点电流：电感负载（对电阻额定电流） | worst | ratio | 35% / 40% / 75% | GJB p24 表30 |
| RLY-M | 继电器 | 连续触点电流：电机负载（对电机额定电流） | worst | ratio | 50% / 75% / 90% | GJB p24 表30 |
| RLY-M-R | 继电器 | 连续触点电流：电机负载（对电阻额定电流） | worst | ratio | 15% / 20% / 75% | GJB p24 表30 |
| RLY-LAMP | 继电器 | 连续触点电流：灯丝负载（对灯泡额定电流） | worst | ratio | 50% / 75% / 90% | GJB p24 表30 |
| RLY-LAMP-R | 继电器 | 连续触点电流：灯丝负载（对电阻额定电流） | worst | ratio | 7% / 10% / 30%；原文范围 0.07~0.08，取保守端 | GJB p24 表30 |
| RLY-PWR | 继电器 | 触点功率（舌簧或水银） | worst | ratio | 40% / 50% / 70% | GJB p24 表30 |
| RLY-PWR-GEN | 继电器（舌簧、水银以外） | 触点功率 | worst | ratio | 85%（三级同值）；原文 <85% | 1006 p11 表8 |
| RLY-COIL-MAX | 继电器 | 线圈释放电压最大允许值 | worst | ratio | 110%（三级同值） | GJB p24 表30 |
| RLY-COIL-MIN | 继电器 | 线圈释放电压最小允许值 | worst | min_ratio | 90%（三级同值） | GJB p24 表30 |
| RLY-HOLD | 继电器 | 线圈维持电压（触点吸合后） | worst | min_ratio | 90%（三级同值）；最低维持电压 / 额定线圈电压，直流或交流有效值 | GJB p24 5.10.2.5 |
| RLY-PICKUP | 继电器 | 最小线圈电压（有启动特性要求时） | worst | min_ratio | 110%（三级同值）；最小线圈电压 / 额定短时启动（吸合）电压 | GJB p24 5.10.2.5 |
| RLY-DRIVE-MAX | 继电器 | 线圈驱动电压最大值 | worst | ratio | 100%（三级同值）；对额定线圈电压最大值；驱动电压最小值 ≥110% 额定最小值同 RLY-PICKUP，按 R1 取 GJB | 1006 p11 表8 |
| RLY-T | 继电器 | 温度 | temperature | margin_c | 20（三级同值） | GJB p24 表30 |
| RLY-VIB | 继电器 | 振动 | worst | ratio | 60%（三级同值） | GJB p24 表30 |
| RLY-LIFE | 继电器 | 工作寿命（循环次数） | life | ratio | 50% / 100% / 100%；II、III 级原文为“—”（不降额），取 1：所需次数不超过额定次数 | GJB p24 表30 |
| RLY-CONTACT-V | 继电器 | 触点电压 | worst | ratio | 105%（三级同值）；且不低于 12 V | 1006 p11 表8 |
| RLY-CONTACT-IMIN | 继电器 | 触点最小电流 | worst | text | ≥1% 额定电流或 ≥10 mA（三级同值） | 1006 p11 表8 |
| RLY-PARALLEL | 继电器 | 触点并联 | worst | text | 不得用触点并联增加电流：吸合、释放瞬间各触点不同时通断，全部负载电流可能流过一个触点（三级同值） | GJB p24 5.10.2.1 |

### 开关

| 编号 | 类型 | 参数 | 工况 | 判据 | I / II / III | 出处 |
|---|---|---|---|---|---|---|
| SW-R | 开关 | 连续触点电流：电阻负载 | worst | ratio | 50% / 75% / 90%；小功率负载（<100 mW）不降额 | GJB p25 表31 |
| SW-C | 开关 | 连续触点电流：电容负载（最大浪涌电流） | worst | ratio | 50% / 75% / 90% | GJB p25 表31 |
| SW-L | 开关 | 连续触点电流：电感负载（对电感额定电流） | worst | ratio | 50% / 75% / 90% | GJB p25 表31 |
| SW-L-R | 开关 | 连续触点电流：电感负载（对电阻额定电流） | worst | ratio | 35% / 40% / 50% | GJB p25 表31 |
| SW-M | 开关 | 连续触点电流：电机负载（对电机额定电流） | worst | ratio | 50% / 75% / 90% | GJB p25 表31 |
| SW-M-R | 开关 | 连续触点电流：电机负载（对电阻额定电流） | worst | ratio | 15% / 20% / 35% | GJB p25 表31 |
| SW-LAMP | 开关 | 连续触点电流：灯丝负载（对灯泡额定电流） | worst | ratio | 50% / 75% / 90% | GJB p25 表31 |
| SW-LAMP-R | 开关 | 连续触点电流：灯丝负载（对电阻额定电流） | worst | ratio | 7% / 10% / 15%；原文范围 0.07~0.08，取保守端 | GJB p25 表31 |
| SW-PWR | 开关 | 触点功率（舌簧或水银） | worst | ratio | 40% / 50% / 70% | GJB p25 表31 |
| SW-V | 开关 | 触点额定电压 | worst | ratio | 40% / 50% / 70% | GJB p25 表31 |
| SW-PARALLEL | 开关 | 触点并联 | worst | text | 触点可并联使用，但不得用并联增加触点电流（三级同值） | GJB p24 5.11.2.1 |

### 晶体与晶振

机器数据同属 `crystal`，按 `subtype` 分：XTAL-* 为无源晶体 `crystal`，OSC-* 为有源晶振 `oscillator`（R7）。

| 编号 | 类型 | 参数 | 工况 | 判据 | I / II / III | 出处 |
|---|---|---|---|---|---|---|
| XTAL-DRIVE | 晶体 | 驱动功率 | worst | text | 按额定驱动功率，不降额（三级同值） | GJB p29 5.18.3 |
| XTAL-T | 晶体 | 工作温度 | temperature | text | 比最低额定温度高 10 °C，比最高额定温度低 10 °C（三级同值） | GJB p29 5.18.3 |
| OSC-I | 有源晶振 | 工作电流 | worst | ratio | 70%（三级同值） | 1006 p11 表8 |
| OSC-V | 有源晶振 | 工作电压 | worst | text | 符合供应商规范（三级同值） | 1006 p11 表8 |
| OSC-T | 有源晶振 | 工作温度 | temperature | margin_c | 30（三级同值）；1006 表8 的“晶振 驱动功率 ≤33%”是无源晶体的激励功率，按 R1 取 GJB 的 XTAL-DRIVE | 1006 p11 表8 |
