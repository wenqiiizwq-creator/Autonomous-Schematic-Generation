# TI TPS281C30 - SLVSGD3C

类别：器件参数。
器件：单路智能高侧开关，含 A/B/C/D/E 版本
手册：SLVSGD3C，2026 年 10 月修订。

## 来源

- S1：Datasheet/08_电源管理/负载开关与高低侧驱动/TI - TPS281C30 - SLVSGD3C.pdf

页码均为 PDF 文件页序；原件共 57 页。

## 绝对最大值

| 参数 | 符号 | 条件 | 最小 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| 电源连续电压 | VS | A/B，对器件地 | −0.7 | 64 | V | S1 p6 |
| 输出连续电压 | VOUT | A/B，对器件地 | −60 | 64 | V | S1 p6 |
| 电源瞬态电压 | VS | A/B，<100 µs | −0.7 | 81 | V | S1 p6 |
| 电源连续电压 | VS | C/D/E，对器件地 | −0.7 | 83 | V | S1 p6 |
| 输出连续电压 | VOUT | C/D/E，对器件地 | −60 | 83 | V | S1 p6 |
| 开关两端连续电压 | VS−VOUT | C/D/E | −0.7 | 83 | V | S1 p6 |
| 反向地电流 | IGND | VS<0 V，负向额定值 |  | −50 | mA | S1 p6 |
| 结温 | TJ |  |  | 150 | °C | S1 p6 |
| 储存温度 | Tstg |  | −65 | 150 | °C | S1 p6 |
| 引脚电压 | VEN | 对器件地 | −1 | 6 | V | S1 p6 |
| 引脚电压 | VOL_ON | 对器件地 | −1 | 6 | V | S1 p6 |
| 引脚电压 | VDIAG_EN | 对器件地 | −1 | 6 | V | S1 p6 |
| 引脚电压 | VSNS | 对器件地 | −1 | 6 | V | S1 p6 |
| 引脚电压 | VFAULT | 对器件地 | −1 | 6 | V | S1 p6 |

## 推荐工作条件

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 标称电源电压 | VS_OP_NOM |  | 6.0 |  | 36 | V | S1 p6 |
| 扩展电源电压 | VS_OP_MAX | 部分参数不适用 | 6.0 |  | 48 | V | S1 p6、p7 |
| 环境温度 | TA |  | −40 |  | 125 | °C | S1 p7 |
| 引脚电压 | VEN | 对器件地 | −1 |  | 5.5 | V | S1 p7 |
| 引脚电压 | VOL_ON | 对器件地 | −1 |  | 5.5 | V | S1 p7 |
| 引脚电压 | VDIAG_EN | 对器件地 | −1 |  | 5.5 | V | S1 p7 |
| 引脚电压 | VSNS | 对器件地 | −1 |  | 5.5 | V | S1 p7 |
| 引脚电压 | VFAULT | 对器件地 | −1 |  | 5.5 | V | S1 p7 |

## 电气特性

除另有说明，VS=6 至 36 V，TA=−40 至 125 °C；开关表另用 TJ 与 COUT 条件，逐行注明（S1 p7–p14）。SNS 时序定义：tSNSION1–4 从对应控制输入上升的 50% 到 ISNS 稳定值的 90%；tSNSION5/6 从负载越过 IKSNS2_EN/IKSNS2_DIS 到稳定值的 90%；tSETTLEH/L 分别到稳定值的 90%/10%；tTIMEOUT 从控制输入 50% 到 VSNSFH 上升 50%（S1 p13）。“最小”“最大”为手册限值，“典型”不是保证值。

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 连续负载电流 | ILNOM | VEN=HI，TAMB=85 °C |  | 6 |  | A | S1 p7 |
| 待机电流 | ISTBY,VS | A/B/C/D，VS≤36 V，VEN=VDIAG_EN=LO，VOUT=0 V，TJ=−40 至 85 °C |  | 0.25 | 0.7 | µA | S1 p7 |
| 待机电流 | ISTBY,VS | A/B/C/D，VS≤36 V，VEN=VDIAG_EN=LO，VOUT=0 V，TJ=150 °C |  | 0.63 | 6 | µA | S1 p7 |
| 诊断待机电流 | ISTBY,VS_DIAG | A/B/C/D，VS≤36 V，VEN=LO，VDIAG_EN=HI，VOUT=0 V |  | 1.2 | 1.5 | mA | S1 p7 |
| 关断静态电流 | IQ(OFF),VS | E，VS≤60 V，VEN=0 V，VOUT=24 V，VDIAG=0 V，TJ=−40 至 85 °C |  |  | 0.95 | mA | S1 p7 |
| 关断静态电流 | IQ(OFF),VS | E，VS≤60 V，VEN=0 V，VOUT=24 V，VDIAG=0 V，TJ=125 °C |  |  | 0.98 | mA | S1 p7 |
| 开启静态电流 | IQ,VS | VEN=HI，IOUT=0 A，VDIAG_EN=LO |  | 0.98 | 1.3 | mA | S1 p7 |
| 开启静态电流 | IQ,VS_DIAG | VEN=HI，IOUT=0 A，VDIAG_EN=HI |  | 1.0 | 1.5 | mA | S1 p7 |
| 进入待机延迟 | tSTBY | A/B/C/D，VEN=VDIAG_EN=0 V 到待机 |  | 20 |  | ms | S1 p7 |
| 关断输出漏电流 | IOUT(OFF) | A/B/C/D，VS≤36 V，VEN=VDIAG_EN=0 V，VOUT=0 V，TJ=85 °C |  |  | 0.4 | µA | S1 p8 |
| 关断输出漏电流 | IOUT(OFF) | A/B/C/D，VS≤36 V，VEN=VDIAG_EN=0 V，VOUT=0 V，TJ=125 °C |  | 0.5 | 6 | µA | S1 p8 |
| 关断输出漏电流 | IOUT(OFF) | E，VS≤36 V，VEN=VDIAG_EN=0 V，VOUT=0 V，TJ=−40 至 85 °C |  |  | 28 | µA | S1 p8 |
| 关断输出漏电流 | IOUT(OFF) | E，VS≤36 V，VEN=VDIAG_EN=0 V，VOUT=0 V，TJ=125 °C |  |  | 28 | µA | S1 p8 |
| 关断输出漏电流 | IOUT(OFF) | E，VS≤36 V，VEN=VDIAG_EN=0 V，VOUT=10 V，TJ=−40 至 85 °C | −6 |  | 9 | µA | S1 p8 |
| 关断输出漏电流 | IOUT(OFF) | E，VS≤36 V，VEN=VDIAG_EN=0 V，VOUT=10 V，TJ=125 °C | −10 |  | 10 | µA | S1 p8 |
| 关断后 EFT 保护延迟 | tEFT_DELAY | E，VS≤60 V，VEN=VDIAG=0 V，VOUT 悬空，TJ=−40 至 125 °C |  |  | 270 | µs | S1 p8 |
| 欠压上升门限 | VS,UVLOR | 对器件地 | 5.0 | 5.4 | 5.75 | V | S1 p8 |
| 欠压下降门限 | VS,UVLOF | 对器件地 | 4.1 | 4.5 | 4.85 | V | S1 p8 |
| 过压上升门限 | VS,OVPR | A/B/C/D，VEN=5 V | 51 | 54 | 57 | V | S1 p8 |
| 过压上升门限 | VS,OVPR | E，VEN=5 V | 50 | 54 | 57 | V | S1 p8 |
| 过压恢复下降门限 | VS,OVPF | VEN=5 V | 49 | 52 | 56 | V | S1 p8 |
| 过压迟滞 | VS,OVPH | VEN=5 V |  | 1.5 |  | V | S1 p8 |
| 漏源钳位电压 | VDS,Clamp | 仅 A/B，FET 电流=10 mA，VS=24 V | 65 | 72.5 | 80 | V | S1 p8 |
| 漏源钳位电压 | VDS,Clamp | 仅 A/B，FET 电流=10 mA，VS=6 V | 48 | 53 | 58 | V | S1 p8 |
| 过压去毛刺 | tVS,OVP | 触发 OVP 到 FET 关闭 |  | 110 | 160 | µs | S1 p8 |
| 导通/限流特性 | RON | VS=24 V，B/D/E：0.5 A≤IOUT≤6 A，A/C：0.5 A≤IOUT≤3 A，TJ=25 °C |  | 29 |  | mΩ | S1 p8 |
| 导通/限流特性 | RON | 同上，TJ=125 °C |  |  | 55 | mΩ | S1 p8 |
| 导通/限流特性 | RON(REV) | VS=−24 V，B/D/E：0.5 A≤IOUT≤6 A，A/C：0.5 A≤IOUT≤3 A，TJ=−40 至 125 °C |  | 30 | 60 | mΩ | S1 p8 |
| 导通/限流特性 | RON_AUXFET | VS=24 V，IOUT=40 mA，OL_ON=DIAG_EN=5 V，TJ=−40 至 125 °C |  | 5.2 | 12 | Ω | S1 p8 |
| 导通/限流特性 | KCL | A/C，RILIM=10 至 50 kΩ | 40 | 50 | 60 | A·kΩ | S1 p8 |
| 导通/限流特性 | KCL | B/D/E，RILIM=10 至 50 kΩ | 80 | 100 | 120 | A·kΩ | S1 p8 |
| 导通/限流特性 | ILIM_STARTUP | A/C，开启，RILIM=10 至 50 kΩ |  | 2 × ICL | 6.5 | A | S1 p8 |
| 导通/限流特性 | ILIM_STARTUP | B/D/E，开启，RILIM=10 至 50 kΩ |  | 2 × ICL | 14 | A | S1 p8 |
| 导通/限流特性 | tLIM_STARTUP_DELAY | 开启前调节峰值延迟 | 7 |  | 12 | ms | S1 p8 |
| 短路限流 | ICL | A/C，RILIM=50 kΩ | 0.8 | 1 | 1.2 | A | S1 p9 |
| 短路限流 | ICL | A/C，RILIM=25 kΩ | 1.8 | 2 | 2.2 | A | S1 p9 |
| 短路限流 | ICL | A/C，RILIM=16.7 kΩ | 2.7 | 3 | 3.3 | A | S1 p9 |
| 短路限流 | ICL | A/C，RILIM=12.5 kΩ | 3.6 | 4 | 4.4 | A | S1 p9 |
| 短路限流 | ICL | A/C，RILIM=10 kΩ | 4.5 | 5 | 5.5 | A | S1 p9 |
| 短路限流 | ICL | B/D，RILIM=50 kΩ | 1.85 | 2 | 2.15 | A | S1 p9 |
| 短路限流 | ICL | B/D，RILIM=25 kΩ | 3.7 | 4 | 4.3 | A | S1 p9 |
| 短路限流 | ICL | B/D，RILIM=16.7 kΩ | 5.6 | 6 | 6.4 | A | S1 p9 |
| 短路限流 | ICL | B/D，RILIM=12.5 kΩ | 7.2 | 8 | 8.6 | A | S1 p9 |
| 短路限流 | ICL | B/D，RILIM=10 kΩ | 9 | 10 | 10.7 | A | S1 p9 |
| 短路限流 | ICL | E，RILIM=50 kΩ | 1.7 | 2 | 2.3 | A | S1 p9 |
| 短路限流 | ICL | E，RILIM=25 kΩ | 3.6 | 4 | 4.4 | A | S1 p9 |
| 短路限流 | ICL | E，RILIM=16.7 kΩ | 5.4 | 6 | 6.6 | A | S1 p9 |
| 短路限流 | ICL | E，RILIM=12.5 kΩ | 7.1 | 8 | 8.9 | A | S1 p9 |
| 短路限流 | ICL | E，RILIM=10 kΩ | 8.8 | 10 | 11.2 | A | S1 p9 |
| 默认短路限流 | ICL | A/C，ILIM 接地/开路或电阻<9 kΩ、>100 kΩ |  | 0.5 | 0.8 | A | S1 p9 |
| 默认短路限流 | ICL | B/D，ILIM 接地/开路或电阻<9 kΩ、>100 kΩ | 0.2 | 0.5 | 1 | A | S1 p9 |
| 默认短路限流 | ICL | E，ILIM 接地/开路或电阻<9 kΩ、>100 kΩ | 0.3 | 0.5 | 0.8 | A | S1 p9 |
| 过载峰值 | ICL_LINPK | 过载，RILIM=10 至 50 kΩ |  |  | 1.3 × ICL | A | S1 p9 |
| 永久短路开启峰值 | IILIM_ENPS | RILIM=10 kΩ |  |  | 2 × ICL | A | S1 p9 |
| 永久短路启动峰值 | IILIM_ENPS2 | RILIM=10 kΩ，t<tLIM_STARTUP_DELAY |  |  | ILIM_STARTUP | A | S1 p9 |
| 过压限流切换门限 | VILIM_OVP | 上升 | 37 | 40 | 43 | V | S1 p9 |
| 过压限流迟滞 | VILIM_OVP | 迟滞 |  | 2 |  | V | S1 p9 |
| 过压限流 | IILIM_OVP | 过载，RILIM=X，VVS≥VILIM_OVP | 0 | 0.552 | 1.5 | A | S1 p9 |
| 短路响应 | tIOS | VS=24 V |  | 0.5 |  | µs | S1 p9 |
| 扩展电压过载限流 | IILIM_OVERVOLTAGE | RILIM=X，48 V≥VS≥36 V |  |  | 5.25 | A | S1 p9 |
| 绝对热关断 | TABS |  | 175 | 185 | 195 | °C | S1 p9 |
| 相对热关断 | TREL |  |  | 77 |  | °C | S1 p9 |
| 热关断重试 | tRETRY | 故障关断到重新开启 | 1.4 | 2.1 | 3 | ms | S1 p9 |
| 绝对热关断迟滞 | THYS |  |  | 10 |  | °C | S1 p9 |
| 限流故障置位 | ICL_FAULT_R | A/B/C/D，VDIAG_EN=5 V，VOL_ON=0 V，上升 | 0.90 × ICL | 0.95 × ICL |  | A | S1 p10 |
| 限流故障撤销 | ICL_FAULT_F | A/B/C/D，VDIAG_EN=5 V，VOL_ON=0 V，下降 | 0.85 × ICL | 0.90 × ICL |  | A | S1 p10 |
| 限流故障置位 | ICL_FAULT_R | E，VDIAG_EN=5 V，VOL_ON=0 V，上升 | 0.77 × ICL | 0.92 × ICL |  | A | S1 p10 |
| 限流故障撤销 | ICL_FAULT_F | E，VDIAG_EN=5 V，VOL_ON=0 V，下降 | 0.72 × ICL | 0.86 × ICL |  | A | S1 p10 |
| 故障输出低电压 | VFAULT | IFAULT=2.5 mA |  |  | 0.5 | V | S1 p10 |
| 启动故障屏蔽 | tFAULT_BLANKING | VDIAG_EN=5 V，VEN=0 至 5 V |  |  | 12 | ms | S1 p10 |
| 故障指示延迟 | tFAULT_FLT | 故障到 FAULT 置位 |  |  | 75 | µs | S1 p10 |
| 故障检测输出延迟 | tFAULT_SNS | A/B/C/D，VDIAG_EN=5 V，故障到 ISNS 达 VSNSFH |  |  | 95 | µs | S1 p10 |
| 故障检测输出延迟 | tFAULT_SNS | E，同上 |  |  | 98 | µs | S1 p10 |
| 进入高精度检测负载 | IKSNS2_EN | A/B/C/D，VEN=VDIAG_EN=5 V，VOL_ON=GND | 42 | 50 | 70 | mA | S1 p10 |
| 进入高精度检测负载 | IKSNS2_EN | E，同上 | 39 | 50 | 70 | mA | S1 p10 |
| 退出高精度检测负载 | IKSNS2_DIS | A/B/C/D，VEN=VDIAG_EN=5 V，VOL_ON=GND | 75 | 85 | 105 | mA | S1 p10 |
| 退出高精度检测负载 | IKSNS2_DIS | E，同上 | 74 | 85 | 96 | mA | S1 p10 |
| 标准检测比例 | KSNS | IOUT=2 A，VOL_ON=GND |  | 1300 |  | A/A | S1 p10 |
| 高精度检测比例 | KSNS2 | IOUT=30 mA，VOL_ON=5 V |  | 24.6 |  | A/A | S1 p10 |
| 检测输出电流 | ISNS | VEN=VDIAG_EN=5 V，VOL_ON=GND，IOUT=7 A |  | 5.38 |  | mA | S1 p11 |
| 检测精度 | ISNS | VEN=VDIAG_EN=5 V，VOL_ON=GND，IOUT=7 A | −6 |  | 6 | % | S1 p11 |
| 检测输出电流 | ISNS | VEN=VDIAG_EN=5 V，VOL_ON=GND，IOUT=6 A |  | 4.61 |  | mA | S1 p11 |
| 检测精度 | ISNS | VEN=VDIAG_EN=5 V，VOL_ON=GND，IOUT=6 A | −6 |  | 6 | % | S1 p11 |
| 检测输出电流 | ISNS | VEN=VDIAG_EN=5 V，VOL_ON=GND，IOUT=4 A |  | 3.0 |  | mA | S1 p11 |
| 检测精度 | ISNS | VEN=VDIAG_EN=5 V，VOL_ON=GND，IOUT=4 A | −4 |  | 4 | % | S1 p11 |
| 检测输出电流 | ISNS | VEN=VDIAG_EN=5 V，VOL_ON=GND，IOUT=2 A |  | 1.533 |  | mA | S1 p11 |
| 检测精度 | ISNS | VEN=VDIAG_EN=5 V，VOL_ON=GND，IOUT=2 A | −4 |  | 4 | % | S1 p11 |
| 检测输出电流 | ISNS | VEN=VDIAG_EN=5 V，VOL_ON=GND，IOUT=1 A |  | 0.764 |  | mA | S1 p11 |
| 检测精度 | ISNS | VEN=VDIAG_EN=5 V，VOL_ON=GND，IOUT=1 A | −4 |  | 4 | % | S1 p11 |
| 检测输出电流 | ISNS | VEN=VDIAG_EN=5 V，VOL_ON=GND，IOUT=500 mA |  | 0.380 |  | mA | S1 p11 |
| 检测精度 | ISNS | VEN=VDIAG_EN=5 V，VOL_ON=GND，IOUT=500 mA | −6 |  | 6 | % | S1 p11 |
| 检测输出电流 | ISNS | VEN=VDIAG_EN=5 V，VOL_ON=GND，IOUT=200 mA |  | 0.150 |  | mA | S1 p11 |
| 检测精度 | ISNS | VEN=VDIAG_EN=5 V，VOL_ON=GND，IOUT=200 mA | −10 |  | 10 | % | S1 p11 |
| 检测输出电流 | ISNS | VEN=VDIAG_EN=5 V，VOL_ON=GND，IOUT=100 mA |  | 0.073 |  | mA | S1 p11 |
| 检测精度 | ISNS | VEN=VDIAG_EN=5 V，VOL_ON=GND，IOUT=100 mA | −15 |  | 15 | % | S1 p11 |
| 检测输出电流 | ISNS | VEN=VDIAG_EN=5 V，VOL_ON=GND，IOUT=50 mA |  | 0.034 |  | mA | S1 p11 |
| 检测精度 | ISNS | VEN=VDIAG_EN=5 V，VOL_ON=GND，IOUT=50 mA | −25 |  | 25 | % | S1 p11 |
| 检测输出电流 | ISNS2 | VEN=VDIAG_EN=5 V，VOL_ON=5 V，IOUT=40 mA |  | 1.62 |  | mA | S1 p11 |
| 检测精度 | ISNS2 | VEN=VDIAG_EN=5 V，VOL_ON=5 V，IOUT=40 mA | −6 |  | 6 | % | S1 p11 |
| 检测输出电流 | ISNS2 | VEN=VDIAG_EN=5 V，VOL_ON=5 V，IOUT=20 mA |  | 0.833 |  | mA | S1 p11 |
| 检测精度 | ISNS2 | VEN=VDIAG_EN=5 V，VOL_ON=5 V，IOUT=20 mA | −6 |  | 6 | % | S1 p11 |
| 检测输出电流 | ISNS2 | VEN=VDIAG_EN=5 V，VOL_ON=5 V，IOUT=10 mA |  | 0.404 |  | mA | S1 p11 |
| 检测精度 | ISNS2 | VEN=VDIAG_EN=5 V，VOL_ON=5 V，IOUT=10 mA | −10 |  | 10 | % | S1 p11 |
| 检测输出电流 | ISNS2 | VEN=VDIAG_EN=5 V，VOL_ON=5 V，IOUT=4 mA |  | 0.161 |  | mA | S1 p11 |
| 检测精度 | ISNS2 | VEN=VDIAG_EN=5 V，VOL_ON=5 V，IOUT=4 mA | −12.5 |  | 12.5 | % | S1 p11 |
| 检测输出电流 | ISNS2 | VEN=VDIAG_EN=5 V，VOL_ON=5 V，IOUT=2 mA |  | 0.0800 |  | mA | S1 p11 |
| 检测精度 | ISNS2 | VEN=VDIAG_EN=5 V，VOL_ON=5 V，IOUT=2 mA | −15 |  | 15 | % | S1 p11 |
| 检测输出电流 | ISNS2 | VEN=VDIAG_EN=5 V，VOL_ON=5 V，IOUT=1 mA |  | 0.0395 |  | mA | S1 p11 |
| 检测精度 | ISNS2 | VEN=VDIAG_EN=5 V，VOL_ON=5 V，IOUT=1 mA | −20 |  | 20 | % | S1 p11 |
| 故障高电平 | VSNSFH | VDIAG_EN=5 V | 4.5 | 5 | 5.77 | V | S1 p11 |
| 故障高电平 | VSNSFH | VDIAG_EN=3.3 V，RSNS 开路 | 3.5 | 3.95 | 4.4 | V | S1 p11 |
| 故障高电平 | VSNSFH | VDIAG_EN=VIH | 2.8 | 3.66 | 3.8 | V | S1 p11 |
| 故障高电流 | ISNSFLT | 非 E，VDIAG_EN>VIH,DIAG_EN | 5.8 | 6.4 |  | mA | S1 p11 |
| 故障高电流 | ISNSFLT | E，VDIAG_EN>VIH,DIAG_EN | 5.3 | 6.4 |  | mA | S1 p11 |
| 检测漏电流 | ISNSleak | VDIAG_EN=5 V，IL=0 mA |  |  | 1.3 | µA | S1 p11 |
| 完整检测/故障所需电源 | VS_ISNS | A/B/C/D，VDIAG_EN=3.3 V | 5.8 |  |  | V | S1 p11 |
| 完整检测/故障所需电源 | VS_ISNS | VDIAG_EN=5 V | 6.5 |  |  | V | S1 p11 |
| 完整检测/故障所需电源 | VS_ISNS | E，VDIAG_EN=3.3 V | 6 |  |  | V | S1 p12 |
| 关断开路门限 | VOL_OFF | VEN=0 V，VDIAG_EN=5 V | 1.5 | 2 | 2.5 | V | S1 p12 |
| 关断开路上拉 | ROL_OFF | VEN=0 V，VDIAG_EN=5 V | 120 | 150 | 180 | kΩ | S1 p12 |
| 关断开路去毛刺 | tOL_OFF | VEN=0 V，VDIAG_EN=5 V，VS−VOUT<VOL 持续超过 tOL |  | 480 | 700 | µs | S1 p12 |
| EN 下降至开路/短电源指示 | tOL_OFF_1 | VEN=5 至 0 V，VDIAG_EN=5 V，IOUT=0 mA，VOUT=VS−VOL |  | 310 | 700 | µs | S1 p12 |
| DIAG_EN 上升至开路/短电源指示 | tOL_OFF_2 | VEN=0 V，VDIAG_EN=0 至 5 V，IOUT=0 mA，VOUT=VS−VOL |  |  | 700 | µs | S1 p12 |
| 输入低门限 | VIL,OL_ON | EN/DIAG_EN 无地网络 |  |  | 0.8 | V | S1 p12 |
| 输入高门限 | VIH,OL_ON | EN/DIAG_EN 无地网络 | 1.5 |  |  | V | S1 p12 |
| 输入迟滞 | VIHYS,OL_ON |  |  | 282 |  | mV | S1 p12 |
| 输入低门限 | VIL,DIAG_EN | EN/DIAG_EN 无地网络 |  |  | 0.8 | V | S1 p12 |
| 输入高门限 | VIH,DIAG_EN | EN/DIAG_EN 无地网络 | 1.5 |  |  | V | S1 p12 |
| 输入迟滞 | VIHYS,DIAG_EN |  |  | 270 |  | mV | S1 p12 |
| 输入低门限 | VIL,EN | EN/DIAG_EN 无地网络 |  |  | 0.8 | V | S1 p12 |
| 输入高门限 | VIH,EN | EN/DIAG_EN 无地网络 | 1.5 |  |  | V | S1 p12 |
| 输入迟滞 | VIHYS,EN |  |  | 280 |  | mV | S1 p12 |
| 内部下拉 | ROL_ON |  | 0.7 | 1 | 1.3 | MΩ | S1 p12 |
| 输入低电流 | IIL_OL_ON | VOL_ON=−1 V | −25 |  | 0 | µA | S1 p12 |
| 输入低电流 | IIL,OL_ON | VOL_ON=0.8 V | 0.6 | 0.8 | 1.2 | µA | S1 p12 |
| 输入高电流 | IIH,OL_ON | VOL_ON=5 V | 3 | 5 | 7 | µA | S1 p12 |
| 内部下拉 | RDIAG_EN |  | 200 | 350 | 500 | kΩ | S1 p12 |
| 输入低电流 | IIL,DIAG_EN | A/B/C/D，VDIAG_EN=0.8 V，VEN=0 V |  | 0.8 |  | µA | S1 p12 |
| 输入低电流 | IIL,DIAG_EN | E，VDIAG_EN=0.8 V，VEN=0 V |  | 2.9 | 3.8 | µA | S1 p12 |
| 输入高电流 | IIH,DIAG_EN | VDIAG_EN=5 V |  | 14 |  | µA | S1 p12 |
| 内部下拉 | REN |  | 200 | 350 | 500 | kΩ | S1 p12 |
| 输入低电流 | IIL,EN | VEN=0.8 V |  | 2.2 |  | µA | S1 p12 |
| 输入高电流 | IIH,EN | VEN=5 V |  | 14 |  | µA | S1 p12 |
| 检测稳定/切换时间 | tSNSION1 | VEN=5 V，VDIAG_EN=0 至 5 V，VOL_ON=0 V，RSNS=1 kΩ，IL=1 A |  |  | 15 | µs | S1 p13 |
| 检测稳定/切换时间 | tSNSION1 | 同上，IL=50 mA |  |  | 80 | µs | S1 p13 |
| 检测稳定/切换时间 | tSNSION2 | VEN=VDIAG_EN=0 至 5 V，VS=24 V，RSNS=1 kΩ，IL=1 A |  |  | 150 | µs | S1 p13 |
| 检测稳定/切换时间 | tSNSION3 | VEN=0 至 5 V，VDIAG_EN=5 V，RSNS=1 kΩ，IL=1 A |  |  | 150 | µs | S1 p13 |
| 检测稳定/切换时间 | tSNSION4 | VOL_ON=0 至 5 V，VEN=VDIAG_EN=5 V，RSNS=1 kΩ，IL=6 mA |  |  | 60 | µs | S1 p13 |
| 检测稳定/切换时间 | tSNSION5 | VOL_ON=VEN=VDIAG_EN=5 V，RSNS=1 kΩ，IL=100 至 10 mA |  |  | 60 | µs | S1 p13 |
| 检测稳定/切换时间 | tSNSION6 | 同上，IL=10 至 100 mA |  |  | 60 | µs | S1 p13 |
| 检测稳定/切换时间 | tKSNS2_DIS_DGL | 同上，IL=10 至 100 mA，去毛刺 |  |  | 30 | µs | S1 p13 |
| 检测稳定/切换时间 | tSNSIOFF | VEN=5 V，VDIAG_EN=5 至 0 V，RSNS=1 kΩ，RL=48 Ω |  |  | 20 | µs | S1 p13 |
| 检测稳定/切换时间 | tSETTLEH | VEN=VDIAG_EN=5 V，RSNS=1 kΩ，IOUT=0.5 至 3 A |  |  | 20 | µs | S1 p13 |
| 检测稳定/切换时间 | tSETTLEL | 同上，IOUT=3 至 0.5 A |  |  | 20 | µs | S1 p13 |
| 检测超时 | tTIMEOUT | VDIAG_EN=VEN=VOL_ON=0 至 5 V，RSNS=1 kΩ，IOUT=5 mA，COUT=50 µF，VS−VOUT>2 V，至 VSNSFH 上升 50% |  | 245 |  | µs | S1 p13 |
| 开关延迟 | tDR | VS=24 V，TJ=−40 至 125 °C，COUT=22 nF，RL=48 Ω，A/B/C/D，从待机，EN 50% 至输出 20% |  | 35 | 55 | µs | S1 p13 |
| 开关延迟 | tDR | VS=24 V，TJ=−40 至 125 °C，COUT=22 nF，RL=48 Ω，A/B/C/D，从延迟或诊断模式，EN 50% 至输出 20% |  | 25 | 45 | µs | S1 p13 |
| 开关延迟 | tDR | VS=24 V，TJ=−40 至 125 °C，COUT=22 nF，RL=48 Ω，E，从延迟或诊断模式，EN 50% 至输出 20% |  | 49 | 60 | µs | S1 p13 |
| 开关延迟 | tDF | VS=24 V，TJ=−40 至 125 °C，COUT=22 nF，RL=48 Ω，A/B/C/D，EN 50% 至输出 80% |  | 35 | 50 | µs | S1 p13 |
| 开关延迟 | tDF | VS=24 V，TJ=−40 至 125 °C，COUT=22 nF，RL=48 Ω，E，EN 50% 至输出 80% |  | 40 | 55 | µs | S1 p13 |
| 输出上升斜率 | SRR | VS=24 V，TJ=−40 至 125 °C，COUT=22 nF，RL=48 Ω，输出 20% 至 80% | 0.4 | 0.7 | 0.95 | V/µs | S1 p14 |
| 输出下降斜率 | SRF | VS=24 V，TJ=−40 至 125 °C，COUT=22 nF，RL=48 Ω，输出 80% 至 20% | 0.4 | 0.8 | 1.2 | V/µs | S1 p14 |
| 最大 PWM 频率 | fmax | VS=24 V，TJ=−40 至 125 °C，COUT=22 nF， |  |  | 1 | kHz | S1 p14 |
| 开启时间 | tON | VS=24 V，TJ=−40 至 125 °C，COUT=22 nF，A/B/C/D，RL=48 Ω，EN 50% 至输出 80% |  | 55 | 75 | µs | S1 p14 |
| 开启时间 | tON | VS=24 V，TJ=−40 至 125 °C，COUT=22 nF，E，同上 |  | 69 | 96 | µs | S1 p14 |
| 关闭时间 | tOFF | VS=24 V，TJ=−40 至 125 °C，COUT=22 nF，A/B/C/D，RL=48 Ω，EN 50% 至输出 20% |  | 60 | 70 | µs | S1 p14 |
| 关闭时间 | tOFF | VS=24 V，TJ=−40 至 125 °C，COUT=22 nF，E，同上 |  | 60 | 80 | µs | S1 p14 |
| 开关时间差 | tON−tOFF | VS=24 V，TJ=−40 至 125 °C，COUT=22 nF，A/B/C/D，1 ms 开启脉冲，RL=48 Ω | −25 |  | 45 | µs | S1 p14 |
| 开关时间差 | tON−tOFF | VS=24 V，TJ=−40 至 125 °C，COUT=22 nF，E，100 µs 开启脉冲，RL=48 Ω，F=fmax | 5 |  | 68 | µs | S1 p14 |
| PWM 平均电流精度 | ΔPWM | VS=24 V，TJ=−40 至 125 °C，COUT=22 nF，200 µs 脉冲，RL=48 Ω，F=fmax | −15 |  | 15 | % | S1 p14 |
| 开启损耗 | EON | VS=24 V，TJ=−40 至 125 °C，COUT=22 nF，RL=8 Ω，1 ms 脉冲，输出从 VS 的 20% 至 80% |  | 0.5 |  | mJ | S1 p14 |
| 关闭损耗 | EOFF | VS=24 V，TJ=−40 至 125 °C，COUT=22 nF，RL=8 Ω，1 ms 脉冲，输出从 VS 的 80% 至 20% |  | 0.25 |  | mJ | S1 p14 |

用这些数时要注意：

- 连续负载电流 ILNOM、KSNS 比例、相对热关断、迟滞、短路响应、损耗和部分输入电流只有典型值。检测精度限值只在各指定负载点成立（S1 p7–p14）。
- SNS 时序和 ICL_FAULT_R/F 不逐件生产测试；峰值启动限流不是持续限流（S1 p9、p12、p13）。
- 6 至 48 V 扩展范围不保证全部电气参数；SNS 在 DIAG_EN=5 V 时完整功能需要 VS≥6.5 V（S1 p6、p7、p11）。
- 推荐工作温度到 125 °C，热关断门限高于结温绝对最大值，不能拿热关断作正常结温限制（S1 p6、p7、p9）。
- 应用表 RILIM 写 7.5 至 50 kΩ，规格保证用 10 至 50 kΩ；示例又取 9.09 kΩ，不应将示例范围替代保证范围。应用计算中 KSNS=1300、1200 及高精度 24、规格 24.6 的数值不一致；表 9-2 的电流/电压算例亦与所列比例不一致，不能当作保证值（S1 p8、p10、p44、p45）。
- E 的待机行为和 EFT 条件不同；EFT 额定依赖指定输出/耦合电容和测试电路，不等于任意外围下抗扰保证（S1 p6、p41、p42）。

## 热特性

以下为手册热特性表的单列数值，原表没有区分最小、典型、最大，不另行赋予保证边界。

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
|---|---|---|---|---|---|
| 结到环境热阻 | RθJA | RGW，JESD51-5/7 四层板 | 28.9 | °C/W | S1 p7 |
| 结到顶壳热阻 | RθJC(top) | 同上 | 19.7 | °C/W | S1 p7 |
| 结到板热阻 | RθJB | 同上 | 7.5 | °C/W | S1 p7 |
| 结到顶热参数 | ψJT | 同上 | 0.2 | °C/W | S1 p7 |
| 结到板热参数 | ψJB | 同上 | 7.5 | °C/W | S1 p7 |
| 结到底壳热阻 | RθJC(bot) | 同上 | 0.8 | °C/W | S1 p7 |

## 静电额定

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
|---|---|---|---|---|---|
| 人体模型 | VESD | HBM，ANSI/ESDA/JEDEC JS-001；除 VS、VOUT 外的所有引脚 | ±2000 | V | S1 p6 |
| 人体模型 | VESD | HBM，ANSI/ESDA/JEDEC JS-001；VS、VOUT 对 GND | ±4000 | V | S1 p6 |
| 带电器件模型 | VESD | CDM，JEDEC JESD22-C101；所有引脚 | ±750 | V | S1 p6 |

手册静电警告（译文）：本集成电路可能被静电损坏，操作时应采取适当防护；不遵守正确的操作和安装程序可能造成损坏。损害可能从轻微性能退化到完全失效；精密集成电路很小的参数变化就可能使其不再满足公布的规格（S1 p48）。

## 引脚与处置

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
| --- | --- | --- | --- | --- |
| VS（10–13） | 电源输入 | A/B 连续 −0.7 至 64 V；C/D/E −0.7 至 83 V，绝对最大 | 接电源 | S1 p4、p6 |
| VOUT（3–6） | 高侧输出 | A/B −60 至 64 V；C/D/E −60 至 83 V，绝对最大 | 接负载，按应用选择钳位 | S1 p4、p6 |
| GND（18）、Pad | 器件地，Pad 内部接地 |  | 接器件地/保护地网络 | S1 p4 |
| EN（15） | 高有效使能，内部下拉 | 绝对最大 −1 至 6 V | 手册未列闲置连接 | S1 p4、p6 |
| DIAG_EN（16） | 诊断使能，内部下拉 | 绝对最大 −1 至 6 V | 悬空或通过 RPROT 接地 | S1 p4、p6 |
| OL_ON（19） | 高精度检测使能 | 绝对最大 −1 至 6 V | 通过 RPROT 接地 | S1 p4、p5、p6 |
| SNS（20） | 检测电流输出 | 绝对最大 −1 至 6 V | 通过 10 kΩ 接地 | S1 p4、p6 |
| FAULT（17） | 全局开漏故障输出 | 绝对最大 −1 至 6 V | 悬空；使用时外部上拉 | S1 p4、p6、p22 |
| ILIM（1） | 电阻设定限流 | 未单列电压范围 | 可悬空进入默认限流，但被视作故障；也可接地 | S1 p4 |
| NC（2、7–9、14） | 内部未连 |  | 建议悬空，或接器件地 | S1 p4、p38 |
| Pad | 散热焊盘内部短接地，必须焊到板上 |  | 接地 | S1 p4、p54 |

## 必需外围

- 可调限流电阻接 ILIM 与器件 GND；规格表给出 10 至 50 kΩ。电流采样需 SNS 到 GND 的电阻，使用 FAULT 需外部上拉（S1 p4、p8、p22、p28）。
- C/D/E 驱动感性负载必须外加跨 VS–VOUT 或输出钳位；A/B 有内部 VDS 钳位（S1 p22、p32、p44）。
- 为负浪涌或感性负载失地时保护 MCU，手册要求 MCU 与开关 I/O 串联电阻，建议 RPROT=10 kΩ。采用地网络反接保护时，限流电阻必须接器件地，感性负载不能只用单二极管地网络；建议 1.5 kΩ 并联 IF>100 mA 的二极管（S1 p38、p39）。
- 电源建议就近 0.1 µF，慢响应电源/大电流阶跃可能还需大容量电容；示例外围不是统一保证范围（S1 p44、p45）。

## 订货型号与封装

RGW 对应 VQFN；字母版本的功能差异见本节原说明。

| 订货型号或后缀 | 封装 | 脚数 | 电压或功能档 | 温度范围 | 引脚镀层 | 来源 |
|---|---|---|---|---|---|---|
| TPS281C30ARGWR | VQFN (RGW) | 20 | 限流 1～5 A；有感性负载钳位 | -40～125 °C | NIPDAU | S1 p49、p3 |
| TPS281C30BRGWR | VQFN (RGW) | 20 | 限流 2～10 A；有感性负载钳位 | -40～125 °C | NIPDAU | S1 p49、p3 |
| TPS281C30CRGWR | VQFN (RGW) | 20 | 限流 1～5 A；无感性负载钳位 | -40～125 °C | NIPDAU | S1 p49、p3 |
| TPS281C30DRGWR | VQFN (RGW) | 20 | 限流 2～10 A；无感性负载钳位 | -40～125 °C | NIPDAU | S1 p49、p3 |
| TPS281C30ERGWR | VQFN (RGW) | 20 | 限流 2～10 A；增强抗电快速瞬变能力 | -40～125 °C | NIPDAU | S1 p49、p3 |

其余见 S1 p49。

A/C 为较低限流档，B/D/E 为较高档；A/B 有内部 VDS 钳位，C/D/E 驱动感性负载需外部钳位；E 无低功耗待机模式并增强 EFT。各版本故障电流比例、限流精度、漏电、检测切换门限和时序差异均在上表分别列出（S1 p6–p14、p22、p24、p32）。


## 核对记录

- 2026-11-09：逐页对照原件，工具核对通过，核对 397 个数。
