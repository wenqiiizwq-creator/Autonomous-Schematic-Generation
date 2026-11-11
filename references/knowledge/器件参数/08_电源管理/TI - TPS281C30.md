# TI TPS281C30

类别：器件参数。
器件：6～36 V智能高侧开关，含电流监测及保护。
手册：SLVSGD3B，2024-08。

## 来源

- S1：Datasheet/08_电源管理/负载开关与高低侧驱动/TI - TPS281C30.pdf

页码均为 PDF 文件页序。

## 绝对最大值

| 参数 | 符号 | 条件 | 最小 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| 输入电压 | VS | A/B | −0.7 | 64 | V | S1 p6 |
| 输出电压 | VOUT | A/B | −60 | 64 | V | S1 p6 |
| 瞬态输入 | VS | A/B，小于100 µs | −0.7 | 81 | V | S1 p6 |
| 输入电压 | VS | C/D/E | −0.7 | 83 | V | S1 p6 |
| 输出电压 | VOUT | C/D/E | −60 | 83 | V | S1 p6 |
| 漏源电压 | VS−VOUT | C/D/E | −0.7 | 83 | V | S1 p6 |
| 控制脚 |  | EN、OL_ON、DIAG_EN、SNS、FAULT | −1 | 6 | V | S1 p6 |
| 反地电流 | IGND | VS<0 | −50 |  | mA | S1 p6 |
| 结温 | TJ |  |  | 150 | °C | S1 p6 |
| 贮存温度 | Tstg |  | −65 | 150 | °C | S1 p6 |

## 推荐工作条件

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 正常电源 | VS_OP_NOM |  | 6.0 |  | 36 | V | S1 p6 |
| 扩展电源 | VS_OP_MAX | 部分参数不适用 | 6.0 |  | 48 | V | S1 p6 |
| 控制电压 |  | EN、OL_ON、DIAG_EN、FAULT、SNS | −1 |  | 5.5 | V | S1 p6、p7 |
| 环境温度 | TA |  | −40 |  | 125 | °C | S1 p7 |

## 电气特性

VS=6～36 V，TA=−40～125 °C；切换特性VS=24 V，TJ=−40～125 °C，COUT=22 nF。各行按具体版本及条件区分（S1 p7～p14）。

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 持续负载电流 | ILNOM | VEN高，环境85 °C |  |  | 6 | A | S1 p7 |
| 待机电流 | ISTBY,VS | A/B/C/D，VS≤36 V，EN=DIAG_EN低，VOUT=0，TJ=−40～85 °C |  | 0.25 | 0.7 | µA | S1 p7 |
| 待机电流 | ISTBY,VS | 同上，TJ=150 °C |  | 0.63 | 6 | µA | S1 p7 |
| 诊断待机电流 | ISTBY,VS_DIAG | A/B/C/D，VS≤36 V，EN低，DIAG_EN高，VOUT=0 |  | 1.2 | 1.5 | mA | S1 p7 |
| 关断静态电流 | IQ(OFF),VS | E，VS≤60 V，EN=DIAG=0，VOUT=24 V，TJ=−40～85 °C |  | 0.95 |  | mA | S1 p7 |
| 关断静态电流 | IQ(OFF),VS | 同上，TJ=125 °C |  | 0.98 |  | mA | S1 p7 |
| 静态电流 | IQ,VS | EN高，DIAG_EN低，IOUT=0 |  | 0.98 | 1.3 | mA | S1 p7 |
| 诊断静态电流 | IQ,VS_DIAG | EN=DIAG_EN高，IOUT=0 |  | 1.0 | 1.5 | mA | S1 p7 |
| 进入待机延迟 | tSTBY | A/B/C/D，EN=DIAG_EN=0 |  | 20 |  | ms | S1 p7 |
| 输出漏电 | IOUT(OFF) | A/B/C/D，VS≤36 V，EN=DIAG_EN=VOUT=0，TJ=85 °C |  |  | 0.4 | µA | S1 p7 |
| 输出漏电 | IOUT(OFF) | 同上，TJ=125 °C |  | 0.5 | 6 | µA | S1 p7 |
| 输出漏电 | IOUT(OFF) | E，VS≤36 V，EN=DIAG_EN=VOUT=0，TJ=−40～125 °C |  | 28 |  | µA | S1 p8 |
| 输出漏电 | IOUT(OFF) | E，VS≤36 V，EN=DIAG_EN=0，VOUT=10 V，TJ=−40～85 °C | −6 |  | 9 | µA | S1 p8 |
| 输出漏电 | IOUT(OFF) | 同上，TJ=125 °C | −10 |  | 10 | µA | S1 p8 |
| EFT保护恢复延迟 | tEFT_DELAY | E，VS≤60 V，EN=DIAG=0，VOUT浮空，−40～125 °C |  | 270 |  | µs | S1 p8 |
| 欠压上升门限 | VS,UVLOR |  | 5.0 | 5.4 | 5.75 | V | S1 p8 |
| 欠压下降门限 | VS,UVLOF |  | 4.1 | 4.5 | 4.85 | V | S1 p8 |
| 过压上升门限 | VS,OVPR | A/B/C/D，VEN=5 V | 51 | 54 | 57 | V | S1 p8 |
| 过压上升门限 | VS,OVPR | E，VEN=5 V | 50 | 54 | 57 | V | S1 p8 |
| 过压下降门限 | VS,OVPF | VEN=5 V | 49 | 52 | 56 | V | S1 p8 |
| 过压迟滞 | VS,OVPH | VEN=5 V |  | 1.5 |  | V | S1 p8 |
| 过压滤波时间 | tVS,OVP | 触发到FET关闭 |  | 110 | 160 | µs | S1 p8 |
| 漏源钳位 | VDS,Clamp | A/B，10 mA，VS=24 V | 65 | 72.5 | 80 | V | S1 p8 |
| 漏源钳位 | VDS,Clamp | A/B，10 mA，VS=6 V | 48 | 53 | 58 | V | S1 p8 |
| 导通电阻 | RON | VS=24 V，B/D/E为0.5～6 A，A/C为0.5～3 A，25 °C |  | 29 |  | mΩ | S1 p8 |
| 导通电阻 | RON | 同上，125 °C |  |  | 55 | mΩ | S1 p8 |
| 反极性导通电阻 | RON(REV) | VS=−24 V，电流档同上，−40～125 °C |  | 30 | 60 | mΩ | S1 p8 |
| 高精度模式导通电阻 | RON_AUXFET | 24 V，40 mA，OL_ON=DIAG_EN=5 V |  | 5.2 | 12 | Ω | S1 p8 |
| 限流比例 | KCL | A/C，RILIM=10～50 kΩ | 40 | 50 | 60 | A·kΩ | S1 p8 |
| 限流比例 | KCL | B/D/E，RILIM=10～50 kΩ | 80 | 100 | 120 | A·kΩ | S1 p8 |
| 启动峰值 | ILIM_STARTUP | A/C，RILIM=10～50 kΩ |  | 2×ICL | 6.5 | A | S1 p8 |
| 启动峰值 | ILIM_STARTUP | B/D/E，RILIM=10～50 kΩ |  | 2×ICL | 14 | A | S1 p8 |
| 启动峰值持续 | tLIM_STARTUP_DELAY |  |  | 7 | 12 | ms | S1 p8 |
| 过载峰值 | ICL_LINPK | RILIM=10～50 kΩ |  |  | 1.3×ICL | A | S1 p9 |
| 短路使能峰值 | IILIM_ENPS | RILIM=10 kΩ |  |  | 2×ICL | A | S1 p9 |
| 启动短路峰值 | IILIM_ENPS2 | RILIM=10 kΩ，t<启动延迟 |  |  | ILIM_STARTUP | A | S1 p9 |
| 过压限流切换门限 | VILIM_OVP | 上升 | 37 | 40 | 43 | V | S1 p9 |
| 过压切换迟滞 | VILIM_OVP |  |  | 2 |  | V | S1 p9 |
| 过压限流 | IILIM_OVP | 过载，VS≥VILIM_OVP | 0 | 0.552 | 1.5 | A | S1 p9 |
| 短路响应 | tIOS | VS=24 V |  | 0.5 |  | µs | S1 p9 |
| 扩展电压限流 | IILIM_OVERVOLTAGE | 过载，36<VS≤48 V |  |  | 5.25 | A | S1 p9 |
| 绝对热关断 | TABS |  | 175 | 185 | 195 | °C | S1 p9 |
| 相对热关断 | TREL |  |  | 77 |  | °C | S1 p9 |
| 热故障重试 | tRETRY |  | 1.4 | 2.1 | 3 | ms | S1 p9 |
| 热迟滞 | THYS |  |  | 10 |  | °C | S1 p9 |
| 故障低电压 | VFAULT | IFAULT=2.5 mA |  |  | 0.5 | V | S1 p10 |
| 启动故障屏蔽 | tFAULT_BLANKING | DIAG_EN=5 V，EN=0到5 V |  | 12 |  | ms | S1 p10 |
| 故障指示时间 | tFAULT_FLT | 故障到FAULT有效 |  | 75 |  | µs | S1 p10 |
| 故障SNS时间 | tFAULT_SNS | A/B/C/D，DIAG_EN=5 V，故障到SNS稳定于VSNSFH |  | 95 |  | µs | S1 p10 |
| 故障SNS时间 | tFAULT_SNS | E，同上 |  | 98 |  | µs | S1 p10 |
| 高精度启用电流 | IKSNS2_EN | A/B/C/D，EN=DIAG_EN=5 V，OL_ON=GND | 42 | 50 | 70 | mA | S1 p10 |
| 高精度启用电流 | IKSNS2_EN | E，同上 | 39 | 50 | 70 | mA | S1 p10 |
| 高精度停用电流 | IKSNS2_DIS | A/B/C/D，同上 | 75 | 85 | 105 | mA | S1 p10 |
| 高精度停用电流 | IKSNS2_DIS | E，同上 | 74 | 85 | 96 | mA | S1 p10 |
| 普通采样比 | KSNS | IOUT=2 A，OL_ON=GND |  | 1300 |  | A/A | S1 p10 |
| 精密采样比 | KSNS2 | IOUT=30 mA，OL_ON=5 V |  | 24.6 |  | A/A | S1 p10 |
| SNS故障高电流 | ISNSFLT | A/B/C/D，DIAG_EN>VIH | 5.8 |  | 6.4 | mA | S1 p11 |
| SNS故障高电流 | ISNSFLT | E，同上 | 5.3 |  | 6.4 | mA | S1 p11 |
| SNS漏电 | ISNSleak | DIAG_EN=5 V，负载0 |  | 1.3 |  | µA | S1 p11 |
| 采样最低电源 | VS_ISNS | A/B/C/D，DIAG_EN=3.3 V | 5.8 |  |  | V | S1 p11 |
| 采样最低电源 | VS_ISNS | DIAG_EN=5 V | 6.5 |  |  | V | S1 p11 |
| 采样最低电源 | VS_ISNS | E，DIAG_EN=3.3 V | 6 |  |  | V | S1 p11 |
| 关断开路检测门限 | VOL_OFF | EN=0，DIAG_EN=5 V | 1.5 | 2 | 2.5 | V | S1 p12 |
| 关断检测上拉 | ROL_OFF | 同上 | 120 | 150 | 180 | kΩ | S1 p12 |
| 关断检测滤波 | tOL_OFF | EN=0，DIAG_EN=5 V，VS−VOUT<VOL持续 |  | 480 | 700 | µs | S1 p12 |
| EN下降检测延迟 | tOL_OFF_1 | EN=5到0 V，DIAG_EN=5 V，IOUT=0，VOUT=VS−VOL |  | 310 | 700 | µs | S1 p12 |
| DIAG上升检测延迟 | tOL_OFF_2 | EN=0，DIAG_EN=0到5 V，IOUT=0，VOUT=VS−VOL |  |  | 700 | µs | S1 p12 |
| PWM频率 | fmax |  |  |  | 1 | kHz | S1 p13 |
| 上升斜率 | SRR | 24 V，48 Ω，输出20%～80%，22 nF | 0.4 | 0.7 | 0.95 | V/µs | S1 p13 |
| 下降斜率 | SRF | 24 V，48 Ω，输出80%～20%，22 nF | 0.4 | 0.8 | 1.2 | V/µs | S1 p13 |
| PWM平均电流精度 | ΔPWM | 24 V，48 Ω，200 µs使能，fmax，22 nF | −15 |  | 15 | % | S1 p14 |
| 限流门限 | ICL | A/C，短路，RILIM=50 kΩ | 0.8 | 1 | 1.2 | A | S1 p9 |
| 限流门限 | ICL | A/C，短路，RILIM=25 kΩ | 1.8 | 2 | 2.2 | A | S1 p9 |
| 限流门限 | ICL | A/C，短路，RILIM=16.7 kΩ | 2.7 | 3 | 3.3 | A | S1 p9 |
| 限流门限 | ICL | A/C，短路，RILIM=12.5 kΩ | 3.6 | 4 | 4.4 | A | S1 p9 |
| 限流门限 | ICL | A/C，短路，RILIM=10 kΩ | 4.5 | 5 | 5.5 | A | S1 p9 |
| 限流门限 | ICL | A/C，短路，RILIM=开路/短地或小于9、大于100 kΩ |  | 0.5 | 0.8 | A | S1 p9 |
| 限流门限 | ICL | B/D，短路，RILIM=50 kΩ | 1.85 | 2 | 2.5 | A | S1 p9 |
| 限流门限 | ICL | B/D，短路，RILIM=25 kΩ | 3.7 | 4 | 4.6 | A | S1 p9 |
| 限流门限 | ICL | B/D，短路，RILIM=16.7 kΩ | 5.6 | 6 | 6.6 | A | S1 p9 |
| 限流门限 | ICL | B/D，短路，RILIM=12.5 kΩ | 7.2 | 8 | 8.8 | A | S1 p9 |
| 限流门限 | ICL | B/D，短路，RILIM=10 kΩ | 9 | 10 | 11 | A | S1 p9 |
| 限流门限 | ICL | B/D，短路，RILIM=开路/短地或小于9、大于100 kΩ | 0.2 | 0.5 | 1 | A | S1 p9 |
| 限流门限 | ICL | E，短路，RILIM=50 kΩ | 1.7 | 2 | 2.3 | A | S1 p9 |
| 限流门限 | ICL | E，短路，RILIM=25 kΩ | 3.6 | 4 | 4.4 | A | S1 p9 |
| 限流门限 | ICL | E，短路，RILIM=16.7 kΩ | 5.4 | 6 | 6.6 | A | S1 p9 |
| 限流门限 | ICL | E，短路，RILIM=12.5 kΩ | 7.1 | 8 | 8.9 | A | S1 p9 |
| 限流门限 | ICL | E，短路，RILIM=10 kΩ | 8.8 | 10 | 11.2 | A | S1 p9 |
| 限流门限 | ICL | E，短路，RILIM=开路/短地或小于9、大于100 kΩ | 0.3 | 0.5 | 0.8 | A | S1 p9 |
| 故障电流门限 | ICL_FAULT_R | A/B/C/D，DIAG_EN=5 V、OL_ON=0，非生产测试 | 0.90×ICL | 0.95×ICL |  | A | S1 p10 |
| 故障电流门限 | ICL_FAULT_R | E，DIAG_EN=5 V、OL_ON=0，非生产测试 | 0.77×ICL | 0.92×ICL |  | A | S1 p10 |
| 故障电流门限 | ICL_FAULT_F | A/B/C/D，DIAG_EN=5 V、OL_ON=0，非生产测试 | 0.85×ICL | 0.90×ICL |  | A | S1 p10 |
| 故障电流门限 | ICL_FAULT_F | E，DIAG_EN=5 V、OL_ON=0，非生产测试 | 0.72×ICL | 0.86×ICL |  | A | S1 p10 |
| 采样电流 | ISNS | EN=DIAG_EN=5 V，OL_ON=0 V，IOUT=7 A |  | 5.38 |  | mA | S1 p11 |
| 采样精度 | ISNS | EN=DIAG_EN=5 V，OL_ON=0 V，IOUT=7 A | −6 |  | 6 | % | S1 p11 |
| 采样电流 | ISNS | EN=DIAG_EN=5 V，OL_ON=0 V，IOUT=6 A |  | 4.61 |  | mA | S1 p11 |
| 采样精度 | ISNS | EN=DIAG_EN=5 V，OL_ON=0 V，IOUT=6 A | −6 |  | 6 | % | S1 p11 |
| 采样电流 | ISNS | EN=DIAG_EN=5 V，OL_ON=0 V，IOUT=4 A |  | 3.0 |  | mA | S1 p11 |
| 采样精度 | ISNS | EN=DIAG_EN=5 V，OL_ON=0 V，IOUT=4 A | −4 |  | 4 | % | S1 p11 |
| 采样电流 | ISNS | EN=DIAG_EN=5 V，OL_ON=0 V，IOUT=2 A |  | 1.533 |  | mA | S1 p11 |
| 采样精度 | ISNS | EN=DIAG_EN=5 V，OL_ON=0 V，IOUT=2 A | −4 |  | 4 | % | S1 p11 |
| 采样电流 | ISNS | EN=DIAG_EN=5 V，OL_ON=0 V，IOUT=1 A |  | 0.764 |  | mA | S1 p11 |
| 采样精度 | ISNS | EN=DIAG_EN=5 V，OL_ON=0 V，IOUT=1 A | −4 |  | 4 | % | S1 p11 |
| 采样电流 | ISNS | EN=DIAG_EN=5 V，OL_ON=0 V，IOUT=500 mA |  | 0.380 |  | mA | S1 p11 |
| 采样精度 | ISNS | EN=DIAG_EN=5 V，OL_ON=0 V，IOUT=500 mA | −6 |  | 6 | % | S1 p11 |
| 采样电流 | ISNS | EN=DIAG_EN=5 V，OL_ON=0 V，IOUT=200 mA |  | 0.150 |  | mA | S1 p11 |
| 采样精度 | ISNS | EN=DIAG_EN=5 V，OL_ON=0 V，IOUT=200 mA | −10 |  | 10 | % | S1 p11 |
| 采样电流 | ISNS | EN=DIAG_EN=5 V，OL_ON=0 V，IOUT=100 mA |  | 0.073 |  | mA | S1 p11 |
| 采样精度 | ISNS | EN=DIAG_EN=5 V，OL_ON=0 V，IOUT=100 mA | −15 |  | 15 | % | S1 p11 |
| 采样电流 | ISNS | EN=DIAG_EN=5 V，OL_ON=0 V，IOUT=50 mA |  | 0.034 |  | mA | S1 p11 |
| 采样精度 | ISNS | EN=DIAG_EN=5 V，OL_ON=0 V，IOUT=50 mA | −25 |  | 25 | % | S1 p11 |
| 采样电流 | ISNS2 | EN=DIAG_EN=5 V，OL_ON=5 V，IOUT=40 mA |  | 1.62 |  | mA | S1 p11 |
| 采样精度 | ISNS2 | EN=DIAG_EN=5 V，OL_ON=5 V，IOUT=40 mA | −6 |  | 6 | % | S1 p11 |
| 采样电流 | ISNS2 | EN=DIAG_EN=5 V，OL_ON=5 V，IOUT=20 mA |  | 0.833 |  | mA | S1 p11 |
| 采样精度 | ISNS2 | EN=DIAG_EN=5 V，OL_ON=5 V，IOUT=20 mA | −6 |  | 6 | % | S1 p11 |
| 采样电流 | ISNS2 | EN=DIAG_EN=5 V，OL_ON=5 V，IOUT=10 mA |  | 0.404 |  | mA | S1 p11 |
| 采样精度 | ISNS2 | EN=DIAG_EN=5 V，OL_ON=5 V，IOUT=10 mA | −10 |  | 10 | % | S1 p11 |
| 采样电流 | ISNS2 | EN=DIAG_EN=5 V，OL_ON=5 V，IOUT=4 mA |  | 0.161 |  | mA | S1 p11 |
| 采样精度 | ISNS2 | EN=DIAG_EN=5 V，OL_ON=5 V，IOUT=4 mA | −12.5 |  | 12.5 | % | S1 p11 |
| 采样电流 | ISNS2 | EN=DIAG_EN=5 V，OL_ON=5 V，IOUT=2 mA |  | 0.0800 |  | mA | S1 p11 |
| 采样精度 | ISNS2 | EN=DIAG_EN=5 V，OL_ON=5 V，IOUT=2 mA | −15 |  | 15 | % | S1 p11 |
| 采样电流 | ISNS2 | EN=DIAG_EN=5 V，OL_ON=5 V，IOUT=1 mA |  | 0.0395 |  | mA | S1 p11 |
| 采样精度 | ISNS2 | EN=DIAG_EN=5 V，OL_ON=5 V，IOUT=1 mA | −20 |  | 20 | % | S1 p11 |
| SNS故障高电平 | VSNSFH | DIAG_EN=5 V，RSNS开路 | 4.5 | 5 | 5.77 | V | S1 p11 |
| SNS故障高电平 | VSNSFH | DIAG_EN=3.3 V，RSNS开路 | 3.5 | 3.95 | 4.4 | V | S1 p11 |
| SNS故障高电平 | VSNSFH | DIAG_EN=VIH V，RSNS开路 | 2.8 | 3.66 | 3.8 | V | S1 p11 |
| 低电平输入 | VIL,OL_ON | 无GND网络 |  |  | 0.8 | V | S1 p12 |
| 高电平输入 | VIH,OL_ON | 无GND网络 | 1.5 |  |  | V | S1 p12 |
| 输入迟滞 | VIHYS,OL_ON |  |  | 282 |  | mV | S1 p12 |
| 内部下拉 | ROL_ON |  | 0.7 | 1 | 1.3 | MΩ | S1 p12 |
| 低电平输入 | VIL,DIAG_EN | 无GND网络 |  |  | 0.8 | V | S1 p12 |
| 高电平输入 | VIH,DIAG_EN | 无GND网络 | 1.5 |  |  | V | S1 p12 |
| 输入迟滞 | VIHYS,DIAG_EN |  |  | 270 |  | mV | S1 p12 |
| 内部下拉 | RDIAG_EN |  | 200 | 350 | 500 | kΩ | S1 p12 |
| 低电平输入 | VIL,EN | 无GND网络 |  |  | 0.8 | V | S1 p12 |
| 高电平输入 | VIH,EN | 无GND网络 | 1.5 |  |  | V | S1 p12 |
| 输入迟滞 | VIHYS,EN |  |  | 280 |  | mV | S1 p12 |
| 内部下拉 | REN |  | 200 | 350 | 500 | kΩ | S1 p12 |
| 输入负压电流 | IIL_OL_ON | VOL_ON=−1 V | −25 |  | 0 | µA | S1 p12 |
| 输入低电流 | IIL,OL_ON | VOL_ON=0.8 V | 0.6 | 0.8 | 1.2 | µA | S1 p12 |
| 输入高电流 | IIH,OL_ON | VOL_ON=5 V | 3 | 5 | 7 | µA | S1 p12 |
| 输入低电流 | IIL,DIAG_EN | A/B/C/D，DIAG_EN=0.8 V、EN=0 |  |  | 0.8 | µA | S1 p12 |
| 输入低电流 | IIL,DIAG_EN | E，同上 |  | 2.9 | 3.8 | µA | S1 p12 |
| 输入高电流 | IIH,DIAG_EN | DIAG_EN=5 V |  |  | 14 | µA | S1 p12 |
| 输入低电流 | IIL,EN | EN=0.8 V |  |  | 2.2 | µA | S1 p12 |
| 输入高电流 | IIH,EN | EN=5 V |  |  | 14 | µA | S1 p12 |
| 使能延迟 | tDR | A/B/C/D，从待机，24 V，48 Ω，22 nF；图示50%EN至20%/80%输出 |  | 35 | 55 | µs | S1 p13 |
| 使能延迟 | tDR | A/B/C/D，从延迟或诊断，24 V，48 Ω，22 nF；图示50%EN至20%/80%输出 |  | 25 | 45 | µs | S1 p13 |
| 使能延迟 | tDR | E，24 V，48 Ω，22 nF；图示50%EN至20%/80%输出 |  | 49 | 60 | µs | S1 p13 |
| 关闭延迟 | tDF | A/B/C/D，24 V，48 Ω，22 nF；图示50%EN至20%/80%输出 |  | 35 | 50 | µs | S1 p13 |
| 关闭延迟 | tDF | E，24 V，48 Ω，22 nF；图示50%EN至20%/80%输出 |  | 40 | 55 | µs | S1 p13 |
| 开启时间 | tON | A/B/C/D，24 V，48 Ω，22 nF；图示50%EN至20%/80%输出 |  | 55 | 75 | µs | S1 p14 |
| 开启时间 | tON | E，24 V，48 Ω，22 nF；图示50%EN至20%/80%输出 |  | 69 | 96 | µs | S1 p14 |
| 关闭时间 | tOFF | A/B/C/D，24 V，48 Ω，22 nF；图示50%EN至20%/80%输出 |  | 60 | 70 | µs | S1 p14 |
| 关闭时间 | tOFF | E，24 V，48 Ω，22 nF；图示50%EN至20%/80%输出 |  | 60 | 80 | µs | S1 p14 |
| 开关时间匹配 | tON−tOFF | A/B/C/D，1 ms使能，24 V，48 Ω | −25 |  | 45 | µs | S1 p14 |
| 开关时间匹配 | tON−tOFF | E，100 µs使能，24 V，48 Ω，fmax | 5 |  | 68 | µs | S1 p14 |

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DIAG_EN建立 | tSNSION1 | VEN=5 V，DIAG_EN 0→5 V，OL_ON=0 V，RSNS=1 kΩ，IL=1 A |  |  | 15 | µs | S1 p13 |
| DIAG_EN建立 | tSNSION1 | VEN=5 V，DIAG_EN 0→5 V，OL_ON=0 V，RSNS=1 kΩ，IL=50 mA |  |  | 80 | µs | S1 p13 |
| EN和DIAG_EN建立 | tSNSION2 | EN/DIAG_EN 0→5 V，VS=24 V，RSNS=1 kΩ，IL=1 A |  |  | 150 | µs | S1 p13 |
| EN建立 | tSNSION3 | EN 0→5 V，DIAG_EN=5 V，RSNS=1 kΩ，IL=1 A |  |  | 150 | µs | S1 p13 |
| OL_ON建立 | tSNSION4 | OL_ON 0→5 V，EN=DIAG_EN=5 V，RSNS=1 kΩ，IL=6 mA |  |  | 60 | µs | S1 p13 |
| 小电流切换建立 | tSNSION5 | OL_ON=EN=DIAG_EN=5 V，RSNS=1 kΩ，IL 100→10 mA |  |  | 60 | µs | S1 p13 |
| 大电流切换建立 | tSNSION6 | OL_ON=EN=DIAG_EN=5 V，RSNS=1 kΩ，IL 10→100 mA |  |  | 60 | µs | S1 p13 |
| 大电流切换去毛刺 | tKSNS2_DIS_DGL | OL_ON=EN=DIAG_EN=5 V，RSNS=1 kΩ，IL 10→100 mA |  |  | 30 | µs | S1 p13 |
| 检测关闭 | tSNSIOFF | EN=5 V，DIAG_EN 5→0 V，RSNS=1 kΩ，RL=48 Ω |  |  | 20 | µs | S1 p13 |
| 电流上跳稳定 | tSETTLEH | EN=DIAG_EN=5 V，RSNS=1 kΩ，IOUT 0.5→3 A |  |  | 20 | µs | S1 p13 |
| 电流下跳稳定 | tSETTLEL | EN=DIAG_EN=5 V，RSNS=1 kΩ，IOUT 3→0.5 A |  |  | 20 | µs | S1 p13 |

用这些数时要注意：

- A/C为1～5 A限流档，B/D/E为2～10 A档；A/B有感性钳位，E增强EFT但无关断开路检测/待机功能（S1 p3）。
- SNS时序参数不做生产测试；温度相对关断、短路响应、部分漏电和延迟只有典型值（S1 p9、p12、p13）。
- 热关断门限高于最大允许结温，不能据此提高允许结温（S1 p6、p9）。
- 全部输入额定均相对器件GND，外接反极性地网络会影响系统地参考的控制条件（S1 p6、p7）。

## 热特性

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- |
| 结到环境 | RθJA | 四层板，RGW/PWP | 28.9 / 31.5 | °C/W | S1 p7 |
| 结到壳顶 | RθJC(top) | 四层板，RGW/PWP | 19.7 / 23.8 | °C/W | S1 p7 |
| 结到板 | RθJB | 四层板，RGW/PWP | 7.5 / 7.4 | °C/W | S1 p7 |
| 结到顶特征参数 | ψJT | 四层板，RGW/PWP | 0.2 / 0.2 | °C/W | S1 p7 |
| 结到板特征参数 | ψJB | 四层板，RGW/PWP | 7.5 / 7.3 | °C/W | S1 p7 |
| 结到壳底 | RθJC(bot) | 四层板，RGW/PWP | 0.8 / 1.5 | °C/W | S1 p7 |

## 静电额定

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- |
| 人体模型 | VESD | JS-001，除VS/VOUT | ±2000 | V | S1 p6 |
| 人体模型 | VESD | VS/VOUT对GND | ±4000 | V | S1 p6 |
| 带电器件模型 | VESD | JESD22-C101，全部脚 | ±750 | V | S1 p6 |
| 接触放电 | V(ESD4) | IEC61000-4-2，VS/VOUT，24 V应用电路 | ±8000 | V | S1 p6 |

手册未给出单独的静电敏感警告。

## 引脚与处置

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
| --- | --- | --- | --- | --- |
| 1 GND | 电源地 | 见额定 | 反极性保护接电阻二极管地网络 | S1 p4、p5 |
| 2 EN | 使能输入，内部下拉 | 见额定 | 未规定 | S1 p4、p5 |
| 3 DIAG_EN | 诊断输入，内部下拉 | 见额定 | 悬空或经RPROT接地 | S1 p4、p5 |
| 4 FAULT | 开漏输出 | 见额定 | 悬空 | S1 p4、p5 |
| 5 OL_ON | 精密采样输入，内部下拉 | 见额定 | 经RPROT接地 | S1 p4、p5 |
| 6 SNS | 模拟电流输出 | 见额定 | 经10 kΩ接地 | S1 p4、p5 |
| 7 ILIM | 限流输出 | 见额定 | 浮空为默认限流，但视为故障状态 | S1 p4、p5 |
| 11 NC | 未连接 | 见额定 | 悬空 | S1 p4、p5 |
| 8/9/10 VOUT | 功率输出 | 见额定 | 接负载 | S1 p4、p5 |
| 12/13/14 VS | 电源输入 | 见额定 | 必须供电 | S1 p4、p5 |

散热焊盘：内部短接GND；手册本页未另写必须焊接措辞（S1 p4）。

### RGW封装

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
| --- | --- | --- | --- | --- |
| 18 GND | 电源地 | 见额定 | 反极性保护接电阻二极管地网络 | S1 p4、p5 |
| 15 EN | 使能输入，内部下拉 | 见额定 | 未规定 | S1 p4、p5 |
| 16 DIAG_EN | 诊断输入，内部下拉 | 见额定 | 悬空或经RPROT接地 | S1 p4、p5 |
| 17 FAULT | 开漏输出 | 见额定 | 悬空 | S1 p4、p5 |
| 19 OL_ON | 精密采样输入，内部下拉 | 见额定 | 经RPROT接地 | S1 p4、p5 |
| 20 SNS | 模拟电流输出 | 见额定 | 经10 kΩ接地 | S1 p4、p5 |
| 1 ILIM | 限流输出 | 见额定 | 浮空为默认限流，但视为故障状态 | S1 p4、p5 |
| 2/7/8/9/14 NC | 未连接 | 见额定 | 悬空 | S1 p4、p5 |
| 3/4/5/6 VOUT | 功率输出 | 见额定 | 接负载 | S1 p4、p5 |
| 10/11/12/13 VS | 电源输入 | 见额定 | 必须供电 | S1 p4、p5 |


## 必需外围

- 感性负载的C/D/E必须外接钳位；A/B可用内部钳位。应用推荐输入TVS SMBJ60CA、输出SMBJ36CA（A/B可选），需满足额定电压及能量（S1 p3、p45）。
- RILIM应用表列7.5～50 kΩ，而保证特性以10～50 kΩ给出；不可把较宽示例范围自动当全规格保证（S1 p8、p45）。
- E版EFT±2.5 kV是在24 V、100 pF耦合和输出10 nF下测试，换电容会改变等级；不是裸芯片无条件耐受（S1 p6、p43）。

## 订货型号与封装

手册列出的型号与封装如下；空格表示手册未给出，不从型号自行推算。

| 订货型号或后缀 | 封装 | 脚数 | 电压或功能档 | 温度范围 | 引脚镀层 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| TPS281C30ARGWR | VQFN (RGW) | 20 |  | -40～125 °C | NIPDAU | S1 p51 |
| TPS281C30ARGWR.A | VQFN (RGW) | 20 |  | -40～125 °C | NIPDAU | S1 p51 |
| TPS281C30BRGWR | VQFN (RGW) | 20 |  | -40～125 °C | NIPDAU | S1 p51 |
| TPS281C30BRGWR.A | VQFN (RGW) | 20 |  | -40～125 °C | NIPDAU | S1 p51 |
| TPS281C30BRGWRG4 | VQFN (RGW) | 20 |  | -40～125 °C | NIPDAU | S1 p51 |
| TPS281C30BRGWRG4.A | VQFN (RGW) | 20 |  | -40～125 °C | NIPDAU | S1 p51 |
| TPS281C30CRGWR | VQFN (RGW) | 20 |  | -40～125 °C | NIPDAU | S1 p51 |
| TPS281C30CRGWR.A | VQFN (RGW) | 20 |  | -40～125 °C | NIPDAU | S1 p51 |
| TPS281C30DRGWR | VQFN (RGW) | 20 |  | -40～125 °C | NIPDAU | S1 p51 |
| TPS281C30DRGWR.A | VQFN (RGW) | 20 |  | -40～125 °C | NIPDAU | S1 p51 |
| TPS281C30ERGWR | VQFN (RGW) | 20 |  | -40～125 °C | NIPDAU | S1 p51 |
| TPS281C30ERGWR.A | VQFN (RGW) | 20 |  | -40～125 °C | NIPDAU | S1 p51 |



## 核对记录

- 2026-11-10：工具核对通过，核对了 425 个数。
