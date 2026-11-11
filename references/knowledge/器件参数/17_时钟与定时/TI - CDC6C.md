# TI CDC6C

类别：器件参数。
器件：固定订货频率 BAW LVCMOS 振荡器。
手册：SNAS843D，2026 年 1 月修订。

## 来源

- S1：Datasheet/17_时钟与定时/振荡器/TI - CDC6C.pdf

页码是 PDF 文件的页序。

## 绝对最大值

| 参数 | 符号 | 条件 | 最小 | 最大 | 单位 | 来源 |
|---|---|---|---|---|---|---|
| 电源电压 | VDD | 各电压档共用绝对最大 | -0.3 | 3.63 | V | S1 p5 |
| 逻辑输入电压 | EN |  | -0.3 | 3.63 | V | S1 p5 |
| 时钟输出 | CLK |  | -0.3 | 3.63 | V | S1 p5 |
| 结温 | TJ |  |  | 130 | °C | S1 p5 |
| 储存温度 | TSTG |  | -65 | 150 | °C | S1 p5 |

## 推荐工作条件

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
|---|---|---|---|---|---|---|---|
| 电源电压 | VDD | 对应 1.8、2.5、3.3 V ±10% 订货档，非任意连续电压档 | 1.62 | 1.8 / 2.5 / 3.3 | 3.63 | V | S1 p5 |
| 环境温度 | TA |  | -40 |  | 105 | °C | S1 p5 |
| 结温 | TJ |  |  |  | 130 | °C | S1 p5 |
| 上电斜坡 | tRAMP | 电源单调上升到标称 95% | 0.1 |  | 100 | ms | S1 p5 |

## 电气特性

推荐工作范围，VDD 为所选 1.8/2.5/3.3 V ±10%；典型值在 25 °C，另注明者除外（S1 p6、p7、p8）。

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
|---|---|---|---|---|---|---|---|
| 供电电流 | IDD | 不含负载；-40 到 85 °C，20 MHz，VDD = 1.8 V ±10% |  | 4.22 | 6.7 | mA | S1 p6 |
| 供电电流 | IDD | 不含负载；-40 到 85 °C，20 MHz，VDD = 3.3 V ±10% |  | 4.41 | 6.7 | mA | S1 p6 |
| 供电电流 | IDD | 不含负载；-40 到 105 °C，20 MHz，VDD = 1.8 V ±10% |  | 4.22 | 7.3 | mA | S1 p6 |
| 供电电流 | IDD | 不含负载；-40 到 105 °C，20 MHz，VDD = 3.3 V ±10% |  | 4.41 | 7.3 | mA | S1 p6 |
| 供电电流 | IDD | 不含负载；-40 到 85 °C，25 MHz，VDD = 1.8 V ±10% |  | 4.32 | 6.8 | mA | S1 p6 |
| 供电电流 | IDD | 不含负载；-40 到 85 °C，25 MHz，VDD = 3.3 V ±10% |  | 4.57 | 6.9 | mA | S1 p6 |
| 供电电流 | IDD | 不含负载；-40 到 105 °C，25 MHz，VDD = 1.8 V ±10% |  | 4.32 | 7.4 | mA | S1 p6 |
| 供电电流 | IDD | 不含负载；-40 到 105 °C，25 MHz，VDD = 3.3 V ±10% |  | 4.57 | 7.5 | mA | S1 p6 |
| 供电电流 | IDD | 不含负载；-40 到 85 °C，50 MHz，VDD = 1.8 V ±10% |  | 4.84 | 7.1 | mA | S1 p6 |
| 供电电流 | IDD | 不含负载；-40 到 85 °C，50 MHz，VDD = 3.3 V ±10% |  | 5.33 | 7.2 | mA | S1 p6 |
| 供电电流 | IDD | 不含负载；-40 到 105 °C，50 MHz，VDD = 1.8 V ±10% |  | 4.84 | 7.6 | mA | S1 p6 |
| 供电电流 | IDD | 不含负载；-40 到 105 °C，50 MHz，VDD = 3.3 V ±10% |  | 5.33 | 7.8 | mA | S1 p6 |
| 供电电流 | IDD | 不含负载；-40 到 85 °C，100 MHz，VDD = 1.8 V ±10% |  | 5.86 | 7.6 | mA | S1 p6 |
| 供电电流 | IDD | 不含负载；-40 到 85 °C，100 MHz，VDD = 3.3 V ±10% |  | 6.77 | 9.0 | mA | S1 p6 |
| 供电电流 | IDD | 不含负载；-40 到 105 °C，100 MHz，VDD = 1.8 V ±10% |  | 5.86 | 8.2 | mA | S1 p6 |
| 供电电流 | IDD | 不含负载；-40 到 105 °C，100 MHz，VDD = 3.3 V ±10% |  | 6.77 | 9.0 | mA | S1 p6 |
| 供电电流 | IDD | 不含负载；-40 到 85 °C，150 MHz，VDD = 1.8 V ±10% |  | 7.14 | 9.5 | mA | S1 p6 |
| 供电电流 | IDD | 不含负载；-40 到 85 °C，150 MHz，VDD = 3.3 V ±10% |  | 8.72 | 11.0 | mA | S1 p6 |
| 供电电流 | IDD | 不含负载；-40 到 105 °C，150 MHz，VDD = 1.8 V ±10% |  | 7.14 | 9.5 | mA | S1 p6 |
| 供电电流 | IDD | 不含负载；-40 到 105 °C，150 MHz，VDD = 3.3 V ±10% |  | 8.72 | 11.0 | mA | S1 p6 |
| 待机电流 | IDD_stdby | -40 到 85 °C，ST 接地，VDD = 1.8 V ±10% |  | 1.5 |  | µA | S1 p6 |
| 待机电流 | IDD_stdby | -40 到 85 °C，ST 接地，VDD = 2.5 V ±10% |  | 2 |  | µA | S1 p6 |
| 待机电流 | IDD_stdby | -40 到 85 °C，ST 接地，VDD = 3.3 V ±10% |  | 2.7 |  | µA | S1 p6 |
| 待机电流 | IDD_stdby | -40 到 105 °C，ST 接地，VDD = 1.8 V ±10% |  | 1.5 |  | µA | S1 p6 |
| 待机电流 | IDD_stdby | -40 到 105 °C，ST 接地，VDD = 2.5 V ±10% |  | 2 |  | µA | S1 p6 |
| 待机电流 | IDD_stdby | -40 到 105 °C，ST 接地，VDD = 3.3 V ±10% |  | 2.7 |  | µA | S1 p6 |
| 输出禁用电流 | IDD-OD | -40 到 85 °C，25 MHz，VDD = 1.8 V ±10% |  | 3.75 | 6.4 | mA | S1 p6 |
| 输出禁用电流 | IDD-OD | -40 到 85 °C，25 MHz，VDD = 3.3 V ±10% |  | 3.76 | 6.5 | mA | S1 p6 |
| 输出禁用电流 | IDD-OD | -40 到 105 °C，25 MHz，VDD = 1.8 V ±10% |  | 3.75 | 7 | mA | S1 p6 |
| 输出禁用电流 | IDD-OD | -40 到 105 °C，25 MHz，VDD = 3.3 V ±10% |  | 3.76 | 7.1 | mA | S1 p6 |
| 输出频率 | Fout |  | 0.25 |  | 200 | MHz | S1 p7 |
| 输出低电平 | VOL | VDD = 1.8 V，IOL = 3.6 mA |  |  | 0.36 | V | S1 p7 |
| 输出高电平 | VOH | VDD = 1.8 V，IOH = 3.6 mA | VDD × 0.88 |  |  | V | S1 p7 |
| 输入低电平 | VIL | VDD = 1.8 V |  |  | 0.45 | V | S1 p7 |
| 输出低电平 | VOL | VDD = 2.5 V，IOL = 5.0 mA |  |  | 0.5 | V | S1 p7 |
| 输出高电平 | VOH | VDD = 2.5 V，IOH = 5.0 mA | VDD × 0.85 |  |  | V | S1 p7 |
| 输入低电平 | VIL | VDD = 2.5 V |  |  | 0.475 | V | S1 p7 |
| 输出低电平 | VOL | VDD = 3.3 V，IOL = 6.6 mA |  |  | 0.66 | V | S1 p7 |
| 输出高电平 | VOH | VDD = 3.3 V，IOH = 6.6 mA | VDD × 0.85 |  |  | V | S1 p7 |
| 输入低电平 | VIL | VDD = 3.3 V |  |  | 0.5 | V | S1 p7 |
| 输出上升/下降时间 | tR/tF | VOH-VOL 的 20% 到 80%，CL = 2 pF，正常，25 MHz |  | 0.28 | 0.65 | ns | S1 p7 |
| 输出上升/下降时间 | tR/tF | VOH-VOL 的 20% 到 80%，CL = 2 pF，慢模式一，25 MHz |  | 0.42 | 0.75 | ns | S1 p7 |
| 输出上升/下降时间 | tR/tF | VOH-VOL 的 20% 到 80%，CL = 5 pF，正常，25 MHz |  | 0.33 | 0.8 | ns | S1 p7 |
| 输出上升/下降时间 | tR/tF | VOH-VOL 的 20% 到 80%，CL = 5 pF，慢模式二，25 MHz |  | 1.11 | 2.0 | ns | S1 p7 |
| 输出上升/下降时间 | tR/tF | VOH-VOL 的 20% 到 80%，CL = 10 pF，正常，25 MHz |  | 0.44 | 1.7 | ns | S1 p7 |
| 输出上升/下降时间 | tR/tF | VOH-VOL 的 20% 到 80%，CL = 10 pF，慢模式三，25 MHz |  | 1.85 | 3.1 | ns | S1 p7 |
| 输出上升/下降时间 | tR/tF | VOH-VOL 的 20% 到 80%，CL = 15 pF，正常，25 MHz |  | 0.87 | 2.2 | ns | S1 p7 |
| 输出上升/下降时间 | tR/tF | VOH-VOL 的 20% 到 80%，CL = 15 pF，慢模式四，25 MHz |  | 2.7 | 4.0 | ns | S1 p7 |
| 输出上升/下降时间 | tR/tF | 10% 到 90%，无载，正常模式，25 MHz |  | 0.42 |  | ns | S1 p7 |
| 输出上升/下降时间 | tR/tF | 10% 到 90%，15 pF，正常模式，25 MHz |  | 2.05 |  | ns | S1 p7 |
| 输出上升/下降时间 | tR/tF | 10% 到 90%，15 pF，慢模式四，25 MHz |  | 3.81 |  | ns | S1 p7 |
| 占空比 | ODC |  | 45 | 50 | 55 | % | S1 p7 |
| 相噪底 | PN-Floor | 偏移 >10 MHz，Fout = 50 MHz |  | -155 |  | dBc/Hz | S1 p7 |
| 最大容性负载 | CL | Fout <50 MHz |  |  | 30 | pF | S1 p7 |
| 最大容性负载 | CL | Fout >50 MHz |  |  | 15 | pF | S1 p7 |
| 输出高态阻抗 | Rout-high |  |  | 50 |  | Ω | S1 p7 |
| 输入高电平 | VIH |  | 1.3 |  |  | V | S1 p7 |
| 输入低电平电流 | IIL | EN = GND | -70 |  |  | µA | S1 p7 |
| 输入高电平电流 | IIH | EN = VDD |  |  | 40 | µA | S1 p7 |
| 输入电容 | CIN | 设计证明，未经表征 |  | 2 |  | pF | S1 p7 |
| 启动时间 | tSTART_UP | 从 0.95 VDD 开始，OE/ST 高，上电斜坡 200 µs |  | 1.5 | 3 | ms | S1 p8 |
| 芯片使能时间 | tST-EN | ST 到 VIH 后到输出达规格 |  |  | 3 | ms | S1 p8 |
| 芯片禁用时间 | tST-DIS | ST 到 VIL 后进入待机 |  |  | 250 | ns | S1 p8 |
| 输出使能时间 | tOE-EN | OE 到 VIH 后到输出达规格 |  |  | 250 | ns | S1 p8 |
| 输出禁用时间 | tOE-DIS | OE 到 VIL 后 |  |  | 250 | ns | S1 p8 |
| 随机相位抖动 | RJ | 10 到 40 MHz（除 25），积分 12 kHz 到 5 MHz，最高 105 °C |  | 400 | 1000 | fs | S1 p8 |
| 随机相位抖动 | RJ | 25 MHz，积分 12 kHz 到 20 MHz，最高 105 °C |  | 400 | 1000 | fs | S1 p8 |
| 随机相位抖动 | RJ | 40 < Fout ≤200 MHz，积分 12 kHz 到 20 MHz，最高 105 °C |  | 400 | 1000 | fs | S1 p8 |
| 周期均方根抖动 | RJITT,RMS | Fout ≥25 MHz |  | 3 |  | ps | S1 p8 |
| 周期峰峰抖动 | RJITT,PK | Fout ≥25 MHz |  | 26 |  | ps | S1 p8 |
| 总频率稳定度 | FT | 含焊接、初始、-40 到 105 °C、电压变化及 25 °C 下 10 年老化 |  |  | ±25 | ppm | S1 p8 |
| 总频率稳定度 | FT | 含焊接、初始、-40 到 105 °C、电压变化及 25 °C 下 1 年老化 |  |  | ±20 | ppm | S1 p8 |
| 总频率稳定度 | FT | 含焊接、初始、-40 到 85 °C、电压变化及 25 °C 下 10 年老化 |  |  | ±25 | ppm | S1 p8 |
| 总频率稳定度 | FT | 含焊接、初始、-40 到 85 °C、电压变化及 25 °C 下 1 年老化 |  |  | ±20 | ppm | S1 p8 |
| 供电纹波杂散 | PSRR | 50 mV 正弦，50 kHz，50 MHz 输出，VDD = 2.5/3.3 V，无去耦 |  | -80 |  | dBc | S1 p8 |
| 供电纹波杂散 | PSRR | 50 mV 正弦，100 kHz，50 MHz 输出，VDD = 2.5/3.3 V，无去耦 |  | -75 |  | dBc | S1 p8 |
| 供电纹波杂散 | PSRR | 50 mV 正弦，500 kHz，50 MHz 输出，VDD = 2.5/3.3 V，无去耦 |  | -63 |  | dBc | S1 p8 |
| 供电纹波杂散 | PSRR | 50 mV 正弦，1 MHz，50 MHz 输出，VDD = 2.5/3.3 V，无去耦 |  | -59 |  | dBc | S1 p8 |
| 单点相噪 | SPN | 偏移 1 kHz，Fout = 100 MHz |  | -86 |  | dBc/Hz | S1 p8 |
| 单点相噪 | SPN | 偏移 10 kHz，Fout = 100 MHz |  | -120 |  | dBc/Hz | S1 p8 |
| 单点相噪 | SPN | 偏移 100 kHz，Fout = 100 MHz |  | -138 |  | dBc/Hz | S1 p8 |
| 单点相噪 | SPN | 偏移 1 MHz，Fout = 100 MHz |  | -143 |  | dBc/Hz | S1 p8 |

用这些数时要注意：

- 待机电流、PSRR、相噪、周期抖动和输出阻抗只有典型值。输入电容仅由设计证明，未经表征（S1 p6、p7、p8）。
- 频稳限值含指定老化时长，不可再混加同类老化数。负载上限对 Fout 恰为 50 MHz 未明确归入哪侧（S1 p7、p8）。
- 电源曾高于 1.5 V 后若落入 1 到 1.5 V，再恢复可能无输出；需降至 1 V 以下再上升恢复（S1 p26）。

## 热特性

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
|---|---|---|---|---|---|
| 结到环境热阻 | RθJA | 封装列顺序见下文 | 151.8 / 151.7 / 180.3 / 189.1 | °C/W | S1 p6 |
| 结到壳顶热阻 | RθJC(top) | 封装列顺序见下文 | 99.3 / 116.2 / 137.3 | °C/W | S1 p6 |
| 结到板热阻 | RθJB | 封装列顺序见下文 | 72.2 / 64.4 / 85.5 / 85 | °C/W | S1 p6 |
| 结到顶热特性参数 | ΨJT | 封装列顺序见下文 | 11.1 / 9.2 / 8.5 / 6.2 | °C/W | S1 p6 |
| 结到板热特性参数 | ΨJB | 封装列顺序见下文 | 63.5 / 83.7 / 83.2 | °C/W | S1 p6 |

列顺序为 DLE、DLF、DLX、DLY（S1 p6）。

## 静电额定

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
|---|---|---|---|---|---|
| 人体模型 | V(ESD) | AEC Q100-002，Level 2 | ±2000 | V | S1 p5 |
| 带电器件模型 | V(ESD) | AEC Q100-011，Level C4A | ±750 | V | S1 p5 |

## 引脚与处置

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
|---|---|---|---|---|
| 1 OE/ST/NC | I/NC，依订货功能使能或待机 | -0.3 到 3.63 V（绝对最大） | NC 可悬空；OE/ST 按订货极性 | S1 p4、p5 |
| 2 GND | G，地 |  | 接地 | S1 p4 |
| 3 CLK | O，LVCMOS 时钟 | -0.3 到 3.63 V（绝对最大） |  | S1 p4、p5 |
| 4 VDD | P，电源 | 按订货电压档 |  | S1 p4、p5 |
| 散热焊盘 | 原件引脚表未给独立散热焊盘 |  |  | S1 p4 |

## 必需外围

- 建议就近使用单颗 1 µF 电源旁路电容，并用低阻抗接地；输出端接及偏置按接收器和订货边沿档配置，手册未给通用必须串联电阻（S1 p16、p21、p26）。

## 订货型号与封装

订货项绑定频率、电压、边沿、功能脚与温区。功能码及高低有效定义见原表，不能由同封装推断可互换；不同电压档、慢模式与负载条件见电气表（S1 p15、p16、p37、p38、p39、p40、p41）。

| 订货型号或后缀 | 封装 | 脚数 | 电压或功能档 | 温度范围 | 引脚镀层 | 来源 |
|---|---|---|---|---|---|---|
| CDC6CA005120ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CA008000ADLFR | VSON (DLF) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CA008000ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CA008192ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CA025000ADLER | VSON (DLE) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CA025000ADLFR | VSON (DLF) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CA025000EDLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CA050000ADLER | VSON (DLE) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CA050000ADLFR | VSON (DLF) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CE001000ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CE007056ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CE007680ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CE008000ADLER | VSON (DLE) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CE008000ADLFR | VSON (DLF) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CE008000ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CE008000ADLYR | VSON (DLY) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CE008000EDLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CE008192ADLER | VSON (DLE) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CE008192ADLFR | VSON (DLF) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CE008192ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CE008192ADLYR | VSON (DLY) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CE010000ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CE012000ADLFR | VSON (DLF) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CE012000ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CE012288ADLER | VSON (DLE) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CE012288ADLFR | VSON (DLF) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CE012288ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CE012288ADLYR | VSON (DLY) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CE016000ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p37 |
| CDC6CE019200ADLER | VSON (DLE) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE019200ADLFR | VSON (DLF) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE019200ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE019200ADLYR | VSON (DLY) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE019200EDLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE020000ADLER | VSON (DLE) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE020000ADLFR | VSON (DLF) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE020000ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE020000ADLYR | VSON (DLY) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE024000ADLER | VSON (DLE) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE024000ADLFR | VSON (DLF) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE024000ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE024000ADLYR | VSON (DLY) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE024000EDLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE024576ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE025000ADLER | VSON (DLE) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE025000ADLER.A | VSON (DLE) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE025000ADLFR | VSON (DLF) | 4 |  | -40 to 105 | NIPDAU | S1 p38 |
| CDC6CE025000ADLFR.A | VSON (DLF) | 4 |  | -40 to 105 | NIPDAU | S1 p38 |
| CDC6CE025000ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE025000ADLYR | VSON (DLY) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE025000ADLYR.A | VSON (DLY) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE025000CDLYR | VSON (DLY) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE025000EDLER | VSON (DLE) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE025000EDLFR | VSON (DLF) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE025000EDLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE026000ADLFR | VSON (DLF) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE026000ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE026000EDLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE027000ADLER | VSON (DLE) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE027000ADLFR | VSON (DLF) | 4 |  | -40 to 105 | Call TI | S1 p38 |
| CDC6CE027000ADLXR | VSON (DLX) | 4 |  | -40 to 105 | NIPDAU | S1 p39 |
| CDC6CE027000ADLXR.A | VSON (DLX) | 4 |  | -40 to 105 | NIPDAU | S1 p39 |
| CDC6CE027000ADLYR | VSON (DLY) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE032768ADLFR | VSON (DLF) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE032768ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE033333ADLER | VSON (DLE) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE033333ADLFR | VSON (DLF) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE033333ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE033333ADLYR | VSON (DLY) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE036000ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE038400EDLER | VSON (DLE) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE040000ADLER | VSON (DLE) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE040000ADLFR | VSON (DLF) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE040000ADLFR.A | VSON (DLF) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE040000ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE040000ADLYR | VSON (DLY) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE040000EDLER | VSON (DLE) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE043500EDLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE048000ADLER | VSON (DLE) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE048000ADLFR | VSON (DLF) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE048000ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE048000ADLYR | VSON (DLY) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE050000ADLER | VSON (DLE) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE050000ADLFR | VSON (DLF) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE050000ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE050000ADLYR | VSON (DLY) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE050000EDLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE066660ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE100000ADLFR | VSON (DLF) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE100000ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE125000ADLER | VSON (DLE) | 4 |  | -40 to 105 | Call TI | S1 p39 |
| CDC6CE125000ADLFR | VSON (DLF) | 4 |  | -40 to 105 | Call TI | S1 p40 |
| CDC6CE125000ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p40 |
| CDC6CE125000ADLYR | VSON (DLY) | 4 |  | -40 to 105 | Call TI | S1 p40 |
| CDC6CE156250ADLFR | VSON (DLF) | 4 |  | -40 to 105 | Call TI | S1 p40 |
| CDC6CE156250ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p40 |
| CDC6CE200000ADLXR | VSON (DLX) | 4 |  | -40 to 105 | Call TI | S1 p40 |

器件生命周期状态不在本条目收录，设计时查厂家网站并记录日期。

## 核对记录

- 2026-11-10：逐页对照原件抽取，工具核对通过（PASS）；核对了 459 个数，问题 0 条，没核对 0 处。
