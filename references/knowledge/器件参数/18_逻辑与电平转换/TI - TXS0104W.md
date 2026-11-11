# TI TXS0104W

类别：器件参数。
器件：四通道自动方向开漏/推挽电平转换器，内部上拉。
手册：SCES988B，2026-01修订；订货附录2026-01-13。

## 来源

- S1：Datasheet/18_逻辑与电平转换/电平转换器_电压翻译器/TI - TXS0104W.pdf

页码均为 PDF 文件页序，共 33 页。

## 绝对最大值

| 参数 | 符号 | 条件 | 最小 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| A 电源/输入/高阻或断电输出 | VCCA、VI、VO |  | −0.5 | 4.6 | V | S1 p6 |
| B 电源/输入/高阻或断电输出 | VCCB、VI、VO |  | −0.5 | 6.5 | V | S1 p6 |
| OE输入 | VI |  | −0.5 | 6.5 | V | S1 p6 |
| 有效A输出 | VO |  | −0.5 | VCCA + 0.5 | V | S1 p6 |
| 有效B输出 | VO |  | −0.5 | VCCB + 0.5 | V | S1 p6 |
| 输入钳位 | IIK | VI<0 | −50 |  | mA | S1 p6 |
| 输出钳位 | IOK | VO<0 | −50 |  | mA | S1 p6 |
| 连续输出电流 | IO |  | −50 | 50 | mA | S1 p6 |
| 电源/地连续电流 |  |  | −100 | 100 | mA | S1 p6 |
| 结温 | Tj |  |  | 150 | °C | S1 p6 |
| 储存温度 | Tstg |  | −65 | 150 | °C | S1 p6 |

## 推荐工作条件

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A电源 | VCCA |  | 1.2 |  | 3.6 | V | S1 p6 |
| B电源 | VCCB | 通用推荐表 | 1.65 |  | 5.5 | V | S1 p6 |
| A高输入 | VIH | VCCA=1.2～1.6 V，VCCB=1.65～5.5 V | VCCA − 0.2 |  | VCCA | V | S1 p6 |
| A高输入 | VIH | VCCA=1.65～3.6 V，VCCB=2.3～5.5 V | VCCA − 0.4 |  | VCCA | V | S1 p6 |
| B高输入 | VIH | 额定供电 | VCCB − 0.4 |  | VCCB | V | S1 p6 |
| OE高输入 | VIH |  | VCCA × 0.65 |  | 5.5 | V | S1 p6 |
| A/B低输入 | VIL | 额定供电 |  |  | 0.2 | V | S1 p7 |
| OE低输入 | VIL |  |  |  | VCCA × 0.35 | V | S1 p7 |
| 边沿加速激活门限 | VRTA | A/B端；VCCI为对应输入电源 | VCCI × 0.30 |  |  | V | S1 p7 |
| 输入上升/下降速率 | Δt/Δv | 推挽驱动 |  |  | 10 | ns/V | S1 p7 |
| 环境温度 | TA |  | −40 |  | 125 | °C | S1 p7 |

## 电气特性

DC分TA=25 °C、−40～85 °C、−40～125 °C；限值相同的合并。开关表逐供电档、推挽/开漏列出；负载与测量参考按S1 p16～p18，外部驱动输出阻抗小于50 Ω（S1 p20）。

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A高输出 | VOHA | 额定供电；IOH=−20 µA，VI(Bx)≥VCCB−0.4 V | VCCA × 0.8 |  |  | V | S1 p7 |
| B高输出 | VOHB | 额定供电；IOH=−20 µA，VI(Ax)≥VCCA−0.4 V | VCCB × 0.8 |  |  | V | S1 p7 |
| A低输出 | VOLA | 额定供电；IOL=1 mA，VI(Bx)≤0.15 V |  |  | 0.4 | V | S1 p7 |
| B低输出 | VOLB | 额定供电；IOL=1 mA，VI(Ax)≤0.15 V |  |  | 0.4 | V | S1 p8 |
| OE漏电 | II | VI=VCC或GND | −2 |  | 2 | µA | S1 p8 |
| 高阻电流 | IOZ | TA=25 °C；VI=VCCI或GND，VO=VCCO或GND，OE=GND | -1 |  | 1 | µA | S1 p8 |
| 静态电流 | ICCA | TA=25 °C；额定供电，VI=VCCI或GND，IO=0 |  |  | 2.4 | µA | S1 p8 |
| 静态电流 | ICCB | TA=25 °C；额定供电，VI=VCCI或GND，IO=0 |  |  | 12 | µA | S1 p8 |
| 静态电流 | ICCA + ICCB | TA=25 °C；额定供电，VI=VCCI或GND，IO=0 |  |  | 14.4 | µA | S1 p8 |
| 单侧断电电流 | ICCA | TA=25 °C；VCCA=0 V，VCCB=5.5 V，VI=VCCI或GND，IO=0 | -3 |  |  | µA | S1 p8 |
| 单侧断电电流 | ICCA | TA=25 °C；VCCA=3.6 V，VCCB=0 V，VI=VCCI或GND，IO=0 |  |  | 2.2 | µA | S1 p8 |
| 单侧断电电流 | ICCB | TA=25 °C；VCCA=0 V，VCCB=5.5 V，VI=VCCI或GND，IO=0 |  |  | 5 | µA | S1 p8 |
| 单侧断电电流 | ICCB | TA=25 °C；VCCA=3.6 V，VCCB=0 V，VI=VCCI或GND，IO=0 | -1 |  |  | µA | S1 p8 |
| 数据I/O电容 | Cio | TA=25 °C；VCCA=VCCB=3.3 V，OE=GND，VO=1.65 V DC+1 MHz、−16 dBm正弦 |  | 5 | 6.5 | pF | S1 p8 |
| 高阻电流 | IOZ | TA=−40～85 °C；VI=VCCI或GND，VO=VCCO或GND，OE=GND | -2 |  | 2 | µA | S1 p8 |
| 静态电流 | ICCA | TA=−40～85 °C；额定供电，VI=VCCI或GND，IO=0 |  |  | 3.3 | µA | S1 p8 |
| 静态电流 | ICCB | TA=−40～85 °C；额定供电，VI=VCCI或GND，IO=0 |  |  | 12 | µA | S1 p8 |
| 静态电流 | ICCA + ICCB | TA=−40～85 °C；额定供电，VI=VCCI或GND，IO=0 |  |  | 14.4 | µA | S1 p8 |
| 单侧断电电流 | ICCA | TA=−40～85 °C；VCCA=0 V，VCCB=5.5 V，VI=VCCI或GND，IO=0 | -3 |  |  | µA | S1 p8 |
| 单侧断电电流 | ICCA | TA=−40～85 °C；VCCA=3.6 V，VCCB=0 V，VI=VCCI或GND，IO=0 |  |  | 2.2 | µA | S1 p8 |
| 单侧断电电流 | ICCB | TA=−40～85 °C；VCCA=0 V，VCCB=5.5 V，VI=VCCI或GND，IO=0 |  |  | 5 | µA | S1 p8 |
| 单侧断电电流 | ICCB | TA=−40～85 °C；VCCA=3.6 V，VCCB=0 V，VI=VCCI或GND，IO=0 | -1 |  |  | µA | S1 p8 |
| 数据I/O电容 | Cio | TA=−40～85 °C；VCCA=VCCB=3.3 V，OE=GND，VO=1.65 V DC+1 MHz、−16 dBm正弦 |  | 12 | 16.5 | pF | S1 p8 |
| 高阻电流 | IOZ | TA=−40～125 °C；VI=VCCI或GND，VO=VCCO或GND，OE=GND | -3 |  | 3 | µA | S1 p8 |
| 静态电流 | ICCA | TA=−40～125 °C；额定供电，VI=VCCI或GND，IO=0 |  |  | 6.2 | µA | S1 p8 |
| 静态电流 | ICCB | TA=−40～125 °C；额定供电，VI=VCCI或GND，IO=0 |  |  | 21 | µA | S1 p8 |
| 静态电流 | ICCA + ICCB | TA=−40～125 °C；额定供电，VI=VCCI或GND，IO=0 |  |  | 25 | µA | S1 p8 |
| 单侧断电电流 | ICCA | TA=−40～125 °C；VCCA=0 V，VCCB=5.5 V，VI=VCCI或GND，IO=0 | -3 |  |  | µA | S1 p8 |
| 单侧断电电流 | ICCA | TA=−40～125 °C；VCCA=3.6 V，VCCB=0 V，VI=VCCI或GND，IO=0 |  |  | 2.2 | µA | S1 p8 |
| 单侧断电电流 | ICCB | TA=−40～125 °C；VCCA=0 V，VCCB=5.5 V，VI=VCCI或GND，IO=0 |  |  | 8 | µA | S1 p8 |
| 单侧断电电流 | ICCB | TA=−40～125 °C；VCCA=3.6 V，VCCB=0 V，VI=VCCI或GND，IO=0 | -1 |  |  | µA | S1 p8 |
| 数据I/O电容 | Cio | TA=−40～125 °C；VCCA=VCCB=3.3 V，OE=GND，VO=1.65 V DC+1 MHz、−16 dBm正弦 |  | 12 | 16.5 | pF | S1 p8 |
| 控制输入电容 | Ci | 全温，VCCA=VCCB=3.3 V，VI=3.3 V或GND |  |  | 6 | pF | S1 p8 |
| 下降传播A→B | tPHL | 推挽；VCCA=1.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 6.7 | ns | S1 p9 |
| 下降传播A→B | tPHL | 推挽；VCCA=1.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 7.3 | ns | S1 p9 |
| 下降传播A→B | tPHL | 推挽；VCCA=1.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 8.3 | ns | S1 p9 |
| 下降传播A→B | tPHL | 推挽；VCCA=1.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 9.8 | ns | S1 p9 |
| 下降传播A→B | tPHL | 开漏；VCCA=1.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 7.2 | ns | S1 p9 |
| 下降传播A→B | tPHL | 开漏；VCCA=1.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 8.4 | ns | S1 p9 |
| 下降传播A→B | tPHL | 开漏；VCCA=1.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 10 | ns | S1 p9 |
| 下降传播A→B | tPHL | 开漏；VCCA=1.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 12.7 | ns | S1 p9 |
| 上升传播A→B | tPLH | 推挽；VCCA=1.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 16 | ns | S1 p9 |
| 上升传播A→B | tPLH | 推挽；VCCA=1.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 13.8 | ns | S1 p9 |
| 上升传播A→B | tPLH | 推挽；VCCA=1.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 15.3 | ns | S1 p9 |
| 上升传播A→B | tPLH | 推挽；VCCA=1.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 29.5 | ns | S1 p9 |
| 上升传播A→B | tPLH | 开漏；VCCA=1.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 58.7 | ns | S1 p9 |
| 上升传播A→B | tPLH | 开漏；VCCA=1.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 53.1 | ns | S1 p9 |
| 上升传播A→B | tPLH | 开漏；VCCA=1.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 49 | ns | S1 p9 |
| 上升传播A→B | tPLH | 开漏；VCCA=1.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 55.2 | ns | S1 p9 |
| 下降传播B→A | tPHL | 推挽；VCCA=1.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 3.9 | ns | S1 p9 |
| 下降传播B→A | tPHL | 推挽；VCCA=1.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 3.9 | ns | S1 p9 |
| 下降传播B→A | tPHL | 推挽；VCCA=1.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 4.3 | ns | S1 p9 |
| 下降传播B→A | tPHL | 推挽；VCCA=1.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 5.5 | ns | S1 p9 |
| 下降传播B→A | tPHL | 开漏；VCCA=1.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 4.1 | ns | S1 p9 |
| 下降传播B→A | tPHL | 开漏；VCCA=1.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 4.3 | ns | S1 p9 |
| 下降传播B→A | tPHL | 开漏；VCCA=1.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 4.9 | ns | S1 p9 |
| 下降传播B→A | tPHL | 开漏；VCCA=1.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 6.2 | ns | S1 p9 |
| 上升传播B→A | tPLH | 推挽；VCCA=1.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 1.4 | ns | S1 p9 |
| 上升传播B→A | tPLH | 推挽；VCCA=1.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 0.6 | ns | S1 p9 |
| 上升传播B→A | tPLH | 推挽；VCCA=1.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 0.2 | ns | S1 p9 |
| 上升传播B→A | tPLH | 推挽；VCCA=1.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 0.5 | ns | S1 p9 |
| 上升传播B→A | tPLH | 开漏；VCCA=1.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 0.6 | ns | S1 p9 |
| 上升传播B→A | tPLH | 开漏；VCCA=1.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 0.5 | ns | S1 p9 |
| 上升传播B→A | tPLH | 开漏；VCCA=1.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 0.5 | ns | S1 p9 |
| 上升传播B→A | tPLH | 开漏；VCCA=1.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 0.5 | ns | S1 p9 |
| 使能 | ten | OE→A/B；VCCA=1.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 260 | ns | S1 p9 |
| 使能 | ten | OE→A/B；VCCA=1.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 179.5 | ns | S1 p9 |
| 使能 | ten | OE→A/B；VCCA=1.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 142.5 | ns | S1 p9 |
| 使能 | ten | OE→A/B；VCCA=1.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 107 | ns | S1 p9 |
| 禁止 | tdis | OE→A/B；VCCA=1.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 260 | ns | S1 p9 |
| 禁止 | tdis | OE→A/B；VCCA=1.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 200 | ns | S1 p9 |
| 禁止 | tdis | OE→A/B；VCCA=1.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 250 | ns | S1 p9 |
| 禁止 | tdis | OE→A/B；VCCA=1.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 250 | ns | S1 p9 |
| A上升 | trA | 推挽；VCCA=1.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 22.7 | ns | S1 p9 |
| A上升 | trA | 推挽；VCCA=1.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 18.4 | ns | S1 p9 |
| A上升 | trA | 推挽；VCCA=1.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 16.3 | ns | S1 p9 |
| A上升 | trA | 推挽；VCCA=1.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 14.2 | ns | S1 p9 |
| A上升 | trA | 开漏；VCCA=1.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 221.5 | ns | S1 p9 |
| A上升 | trA | 开漏；VCCA=1.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 173.3 | ns | S1 p9 |
| A上升 | trA | 开漏；VCCA=1.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 145.9 | ns | S1 p9 |
| A上升 | trA | 开漏；VCCA=1.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 119.4 | ns | S1 p9 |
| B上升 | trB | 推挽；VCCA=1.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 20.6 | ns | S1 p9 |
| B上升 | trB | 推挽；VCCA=1.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 16.8 | ns | S1 p9 |
| B上升 | trB | 推挽；VCCA=1.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 15.9 | ns | S1 p9 |
| B上升 | trB | 推挽；VCCA=1.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 22.1 | ns | S1 p9 |
| B上升 | trB | 开漏；VCCA=1.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 148.1 | ns | S1 p9 |
| B上升 | trB | 开漏；VCCA=1.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 108.4 | ns | S1 p9 |
| B上升 | trB | 开漏；VCCA=1.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 81.6 | ns | S1 p9 |
| B上升 | trB | 开漏；VCCA=1.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 55.5 | ns | S1 p9 |
| A下降 | tfA | 推挽；VCCA=1.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 5.6 | ns | S1 p9 |
| A下降 | tfA | 推挽；VCCA=1.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 4.8 | ns | S1 p9 |
| A下降 | tfA | 推挽；VCCA=1.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 4.7 | ns | S1 p9 |
| A下降 | tfA | 推挽；VCCA=1.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 5 | ns | S1 p9 |
| A下降 | tfA | 开漏；VCCA=1.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 6.1 | ns | S1 p9 |
| A下降 | tfA | 开漏；VCCA=1.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 5.5 | ns | S1 p9 |
| A下降 | tfA | 开漏；VCCA=1.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 5.8 | ns | S1 p9 |
| A下降 | tfA | 开漏；VCCA=1.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 6.4 | ns | S1 p9 |
| B下降 | tfB | 推挽；VCCA=1.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 12 | ns | S1 p9 |
| B下降 | tfB | 推挽；VCCA=1.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 13.1 | ns | S1 p9 |
| B下降 | tfB | 推挽；VCCA=1.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 15.2 | ns | S1 p9 |
| B下降 | tfB | 推挽；VCCA=1.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 19.9 | ns | S1 p9 |
| B下降 | tfB | 开漏；VCCA=1.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 13.2 | ns | S1 p9 |
| B下降 | tfB | 开漏；VCCA=1.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 15.4 | ns | S1 p9 |
| B下降 | tfB | 开漏；VCCA=1.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 19.1 | ns | S1 p9 |
| B下降 | tfB | 开漏；VCCA=1.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 26.7 | ns | S1 p9 |
| 下降传播A→B | tPHL | 推挽；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 4 | ns | S1 p10 |
| 下降传播A→B | tPHL | 推挽；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 3.9 | ns | S1 p10 |
| 下降传播A→B | tPHL | 推挽；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 4.5 | ns | S1 p10 |
| 下降传播A→B | tPHL | 推挽；VCCA=1.5±0.1 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 5.6 | ns | S1 p10 |
| 下降传播A→B | tPHL | 开漏；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 4 | ns | S1 p10 |
| 下降传播A→B | tPHL | 开漏；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 4.3 | ns | S1 p10 |
| 下降传播A→B | tPHL | 开漏；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 5 | ns | S1 p10 |
| 下降传播A→B | tPHL | 开漏；VCCA=1.5±0.1 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 6.4 | ns | S1 p10 |
| 上升传播A→B | tPLH | 推挽；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 9.1 | ns | S1 p10 |
| 上升传播A→B | tPLH | 推挽；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 6.8 | ns | S1 p10 |
| 上升传播A→B | tPLH | 推挽；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 6.2 | ns | S1 p10 |
| 上升传播A→B | tPLH | 推挽；VCCA=1.5±0.1 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 6 | ns | S1 p10 |
| 上升传播A→B | tPLH | 开漏；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 12.5 | ns | S1 p10 |
| 上升传播A→B | tPLH | 开漏；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 10.7 | ns | S1 p10 |
| 上升传播A→B | tPLH | 开漏；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 10.5 | ns | S1 p10 |
| 上升传播A→B | tPLH | 开漏；VCCA=1.5±0.1 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 10.4 | ns | S1 p10 |
| 下降传播B→A | tPHL | 推挽；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 3 | ns | S1 p10 |
| 下降传播B→A | tPHL | 推挽；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 2.9 | ns | S1 p10 |
| 下降传播B→A | tPHL | 推挽；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 3.3 | ns | S1 p10 |
| 下降传播B→A | tPHL | 推挽；VCCA=1.5±0.1 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 4.3 | ns | S1 p10 |
| 下降传播B→A | tPHL | 开漏；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 3 | ns | S1 p10 |
| 下降传播B→A | tPHL | 开漏；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 3.1 | ns | S1 p10 |
| 下降传播B→A | tPHL | 开漏；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 3.5 | ns | S1 p10 |
| 下降传播B→A | tPHL | 开漏；VCCA=1.5±0.1 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 4.7 | ns | S1 p10 |
| 上升传播B→A | tPLH | 推挽；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 1.8 | ns | S1 p10 |
| 上升传播B→A | tPLH | 推挽；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 1 | ns | S1 p10 |
| 上升传播B→A | tPLH | 推挽；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 0.3 | ns | S1 p10 |
| 上升传播B→A | tPLH | 推挽；VCCA=1.5±0.1 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 1 | ns | S1 p10 |
| 上升传播B→A | tPLH | 开漏；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 4 | ns | S1 p10 |
| 上升传播B→A | tPLH | 开漏；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 1 | ns | S1 p10 |
| 上升传播B→A | tPLH | 开漏；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 1 | ns | S1 p10 |
| 上升传播B→A | tPLH | 开漏；VCCA=1.5±0.1 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 1 | ns | S1 p10 |
| 使能 | ten | OE→A/B；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 250 | ns | S1 p10 |
| 使能 | ten | OE→A/B；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 200 | ns | S1 p10 |
| 使能 | ten | OE→A/B；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 200 | ns | S1 p10 |
| 使能 | ten | OE→A/B；VCCA=1.5±0.1 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 100 | ns | S1 p10 |
| 禁止 | tdis | OE→A/B；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 250 | ns | S1 p10 |
| 禁止 | tdis | OE→A/B；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 200 | ns | S1 p10 |
| 禁止 | tdis | OE→A/B；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 250 | ns | S1 p10 |
| 禁止 | tdis | OE→A/B；VCCA=1.5±0.1 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 160 | ns | S1 p10 |
| A上升 | trA | 推挽；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 12.5 | ns | S1 p10 |
| A上升 | trA | 推挽；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 9.5 | ns | S1 p10 |
| A上升 | trA | 推挽；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 7.9 | ns | S1 p10 |
| A上升 | trA | 推挽；VCCA=1.5±0.1 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 7 | ns | S1 p10 |
| A上升 | trA | 开漏；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 130 | ns | S1 p10 |
| A上升 | trA | 开漏；VCCA=1.5±0.1 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 73.7 | ns | S1 p10 |
| B上升 | trB | 推挽；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 14.3 | ns | S1 p10 |
| B上升 | trB | 推挽；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 10.8 | ns | S1 p10 |
| B上升 | trB | 推挽；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 9.4 | ns | S1 p10 |
| B上升 | trB | 推挽；VCCA=1.5±0.1 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 8.2 | ns | S1 p10 |
| B上升 | trB | 开漏；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 150 | ns | S1 p10 |
| B上升 | trB | 开漏；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 110 | ns | S1 p10 |
| B上升 | trB | 开漏；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 79 | ns | S1 p10 |
| B上升 | trB | 开漏；VCCA=1.5±0.1 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 43.1 | ns | S1 p10 |
| A下降 | tfA | 推挽；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 4 | ns | S1 p10 |
| A下降 | tfA | 推挽；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 3.3 | ns | S1 p10 |
| A下降 | tfA | 推挽；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 3.2 | ns | S1 p10 |
| A下降 | tfA | 推挽；VCCA=1.5±0.1 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 3.4 | ns | S1 p10 |
| A下降 | tfA | 开漏；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 4.1 | ns | S1 p10 |
| A下降 | tfA | 开漏；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 3.5 | ns | S1 p10 |
| A下降 | tfA | 开漏；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 3.5 | ns | S1 p10 |
| A下降 | tfA | 开漏；VCCA=1.5±0.1 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 3.8 | ns | S1 p10 |
| B下降 | tfB | 推挽；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 7 | ns | S1 p10 |
| B下降 | tfB | 推挽；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 6.9 | ns | S1 p10 |
| B下降 | tfB | 推挽；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 7.8 | ns | S1 p10 |
| B下降 | tfB | 推挽；VCCA=1.5±0.1 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 10 | ns | S1 p10 |
| B下降 | tfB | 开漏；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 7.2 | ns | S1 p10 |
| B下降 | tfB | 开漏；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 7.5 | ns | S1 p10 |
| B下降 | tfB | 开漏；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 8.8 | ns | S1 p10 |
| B下降 | tfB | 开漏；VCCA=1.5±0.1 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 11.5 | ns | S1 p10 |
| 下降传播A→B | tPHL | 推挽；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 6 | ns | S1 p11 |
| 下降传播A→B | tPHL | 推挽；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 6 | ns | S1 p11 |
| 下降传播A→B | tPHL | 推挽；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 5.8 | ns | S1 p11 |
| 下降传播A→B | tPHL | 推挽；VCCA=1.8±0.15 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 5.8 | ns | S1 p11 |
| 下降传播A→B | tPHL | 开漏；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 8.8 | ns | S1 p11 |
| 下降传播A→B | tPHL | 开漏；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 8.8 | ns | S1 p11 |
| 下降传播A→B | tPHL | 开漏；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 9.6 | ns | S1 p11 |
| 下降传播A→B | tPHL | 开漏；VCCA=1.8±0.15 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 10 | ns | S1 p11 |
| 上升传播A→B | tPLH | 推挽；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 8 | ns | S1 p11 |
| 上升传播A→B | tPLH | 推挽；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 7.7 | ns | S1 p11 |
| 上升传播A→B | tPLH | 推挽；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 6.8 | ns | S1 p11 |
| 上升传播A→B | tPLH | 推挽；VCCA=1.8±0.15 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 7 | ns | S1 p11 |
| 上升传播A→B | tPLH | 开漏；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 50 | ns | S1 p11 |
| 上升传播A→B | tPLH | 开漏；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 50 | ns | S1 p11 |
| 上升传播A→B | tPLH | 开漏；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 26 | ns | S1 p11 |
| 上升传播A→B | tPLH | 开漏；VCCA=1.8±0.15 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 33 | ns | S1 p11 |
| 下降传播B→A | tPHL | 推挽；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 4.4 | ns | S1 p11 |
| 下降传播B→A | tPHL | 推挽；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 4.4 | ns | S1 p11 |
| 下降传播B→A | tPHL | 推挽；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 4.5 | ns | S1 p11 |
| 下降传播B→A | tPHL | 推挽；VCCA=1.8±0.15 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 4.7 | ns | S1 p11 |
| 下降传播B→A | tPHL | 开漏；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 5.3 | ns | S1 p11 |
| 下降传播B→A | tPHL | 开漏；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 5.3 | ns | S1 p11 |
| 下降传播B→A | tPHL | 开漏；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 4.4 | ns | S1 p11 |
| 下降传播B→A | tPHL | 开漏；VCCA=1.8±0.15 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 4.5 | ns | S1 p11 |
| 上升传播B→A | tPLH | 推挽；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 5.3 | ns | S1 p11 |
| 上升传播B→A | tPLH | 推挽；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 5.3 | ns | S1 p11 |
| 上升传播B→A | tPLH | 推挽；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 4.5 | ns | S1 p11 |
| 上升传播B→A | tPLH | 推挽；VCCA=1.8±0.15 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 4.7 | ns | S1 p11 |
| 上升传播B→A | tPLH | 开漏；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 36 | ns | S1 p11 |
| 上升传播B→A | tPLH | 开漏；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 36 | ns | S1 p11 |
| 上升传播B→A | tPLH | 开漏；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 16 | ns | S1 p11 |
| 上升传播B→A | tPLH | 开漏；VCCA=1.8±0.15 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 20 | ns | S1 p11 |
| 使能 | ten | OE→A/B；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 200 | ns | S1 p11 |
| 使能 | ten | OE→A/B；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 200 | ns | S1 p11 |
| 使能 | ten | OE→A/B；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 200 | ns | S1 p11 |
| 使能 | ten | OE→A/B；VCCA=1.8±0.15 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 200 | ns | S1 p11 |
| 禁止 | tdis | OE→A/B；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 250 | ns | S1 p11 |
| 禁止 | tdis | OE→A/B；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 200 | ns | S1 p11 |
| 禁止 | tdis | OE→A/B；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 250 | ns | S1 p11 |
| 禁止 | tdis | OE→A/B；VCCA=1.8±0.15 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 200 | ns | S1 p11 |
| A上升 | trA | 推挽；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 11.4 | ns | S1 p11 |
| A上升 | trA | 推挽；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 9.5 | ns | S1 p11 |
| A上升 | trA | 推挽；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 9.3 | ns | S1 p11 |
| A上升 | trA | 推挽；VCCA=1.8±0.15 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 15 | ns | S1 p11 |
| A上升 | trA | 开漏；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 199 | ns | S1 p11 |
| A上升 | trA | 开漏；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 199 | ns | S1 p11 |
| A上升 | trA | 开漏；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 150 | ns | S1 p11 |
| A上升 | trA | 开漏；VCCA=1.8±0.15 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 109 | ns | S1 p11 |
| B上升 | trB | 推挽；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 13.3 | ns | S1 p11 |
| B上升 | trB | 推挽；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 10.8 | ns | S1 p11 |
| B上升 | trB | 推挽；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 9.1 | ns | S1 p11 |
| B上升 | trB | 推挽；VCCA=1.8±0.15 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 7.6 | ns | S1 p11 |
| B上升 | trB | 开漏；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 186 | ns | S1 p11 |
| B上升 | trB | 开漏；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 186 | ns | S1 p11 |
| B上升 | trB | 开漏；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 112 | ns | S1 p11 |
| B上升 | trB | 开漏；VCCA=1.8±0.15 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 58 | ns | S1 p11 |
| A下降 | tfA | 推挽；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 5.9 | ns | S1 p11 |
| A下降 | tfA | 推挽；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 5.9 | ns | S1 p11 |
| A下降 | tfA | 推挽；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 6 | ns | S1 p11 |
| A下降 | tfA | 推挽；VCCA=1.8±0.15 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 13.3 | ns | S1 p11 |
| A下降 | tfA | 开漏；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 6.9 | ns | S1 p11 |
| A下降 | tfA | 开漏；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 6.9 | ns | S1 p11 |
| A下降 | tfA | 开漏；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 6.4 | ns | S1 p11 |
| A下降 | tfA | 开漏；VCCA=1.8±0.15 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 6.1 | ns | S1 p11 |
| B下降 | tfB | 推挽；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 7.6 | ns | S1 p11 |
| B下降 | tfB | 推挽；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 7.6 | ns | S1 p11 |
| B下降 | tfB | 推挽；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 7.5 | ns | S1 p11 |
| B下降 | tfB | 推挽；VCCA=1.8±0.15 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 8.8 | ns | S1 p11 |
| B下降 | tfB | 开漏；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 13.8 | ns | S1 p11 |
| B下降 | tfB | 开漏；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 13.8 | ns | S1 p11 |
| B下降 | tfB | 开漏；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 16.2 | ns | S1 p11 |
| B下降 | tfB | 开漏；VCCA=1.8±0.15 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 16.2 | ns | S1 p11 |
| 下降传播A→B | tPHL | 推挽；VCCA=2.5±0.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 3.2 | ns | S1 p12 |
| 下降传播A→B | tPHL | 推挽；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 3.2 | ns | S1 p12 |
| 下降传播A→B | tPHL | 推挽；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 3.3 | ns | S1 p12 |
| 下降传播A→B | tPHL | 推挽；VCCA=2.5±0.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 3.4 | ns | S1 p12 |
| 下降传播A→B | tPHL | 开漏；VCCA=2.5±0.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 6.3 | ns | S1 p12 |
| 下降传播A→B | tPHL | 开漏；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 6.3 | ns | S1 p12 |
| 下降传播A→B | tPHL | 开漏；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 6 | ns | S1 p12 |
| 下降传播A→B | tPHL | 开漏；VCCA=2.5±0.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 5.8 | ns | S1 p12 |
| 上升传播A→B | tPLH | 推挽；VCCA=2.5±0.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 3.8 | ns | S1 p12 |
| 上升传播A→B | tPLH | 推挽；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 3.8 | ns | S1 p12 |
| 上升传播A→B | tPLH | 推挽；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 4.1 | ns | S1 p12 |
| 上升传播A→B | tPLH | 推挽；VCCA=2.5±0.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 4.4 | ns | S1 p12 |
| 上升传播A→B | tPLH | 开漏；VCCA=2.5±0.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 3.5 | ns | S1 p12 |
| 上升传播A→B | tPLH | 开漏；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 3.5 | ns | S1 p12 |
| 上升传播A→B | tPLH | 开漏；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 4.1 | ns | S1 p12 |
| 上升传播A→B | tPLH | 开漏；VCCA=2.5±0.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 4.4 | ns | S1 p12 |
| 下降传播B→A | tPHL | 推挽；VCCA=2.5±0.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 3 | ns | S1 p12 |
| 下降传播B→A | tPHL | 推挽；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 3 | ns | S1 p12 |
| 下降传播B→A | tPHL | 推挽；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 3.6 | ns | S1 p12 |
| 下降传播B→A | tPHL | 推挽；VCCA=2.5±0.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 4.3 | ns | S1 p12 |
| 下降传播B→A | tPHL | 开漏；VCCA=2.5±0.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 4.7 | ns | S1 p12 |
| 下降传播B→A | tPHL | 开漏；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 4.7 | ns | S1 p12 |
| 下降传播B→A | tPHL | 开漏；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 4.2 | ns | S1 p12 |
| 下降传播B→A | tPHL | 开漏；VCCA=2.5±0.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 4 | ns | S1 p12 |
| 上升传播B→A | tPLH | 推挽；VCCA=2.5±0.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 8.7 | ns | S1 p12 |
| 上升传播B→A | tPLH | 推挽；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 2.5 | ns | S1 p12 |
| 上升传播B→A | tPLH | 推挽；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 1.6 | ns | S1 p12 |
| 上升传播B→A | tPLH | 推挽；VCCA=2.5±0.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 0.7 | ns | S1 p12 |
| 上升传播B→A | tPLH | 开漏；VCCA=2.5±0.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 29.9 | ns | S1 p12 |
| 上升传播B→A | tPLH | 开漏；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 2.5 | ns | S1 p12 |
| 上升传播B→A | tPLH | 开漏；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 1.6 | ns | S1 p12 |
| 上升传播B→A | tPLH | 开漏；VCCA=2.5±0.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 1 | ns | S1 p12 |
| 使能 | ten | OE→A/B；VCCA=2.5±0.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 200 | ns | S1 p12 |
| 使能 | ten | OE→A/B；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 200 | ns | S1 p12 |
| 使能 | ten | OE→A/B；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 200 | ns | S1 p12 |
| 使能 | ten | OE→A/B；VCCA=2.5±0.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 200 | ns | S1 p12 |
| 禁止 | tdis | OE→A/B；VCCA=2.5±0.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 250 | ns | S1 p12 |
| 禁止 | tdis | OE→A/B；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 200 | ns | S1 p12 |
| 禁止 | tdis | OE→A/B；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 200 | ns | S1 p12 |
| 禁止 | tdis | OE→A/B；VCCA=2.5±0.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 200 | ns | S1 p12 |
| A上升 | trA | 推挽；VCCA=2.5±0.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 10.6 | ns | S1 p12 |
| A上升 | trA | 推挽；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 7.4 | ns | S1 p12 |
| A上升 | trA | 推挽；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 6.6 | ns | S1 p12 |
| A上升 | trA | 推挽；VCCA=2.5±0.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 5.6 | ns | S1 p12 |
| A上升 | trA | 开漏；VCCA=2.5±0.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 180 | ns | S1 p12 |
| A上升 | trA | 开漏；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 180 | ns | S1 p12 |
| A上升 | trA | 开漏；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 150 | ns | S1 p12 |
| A上升 | trA | 开漏；VCCA=2.5±0.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 105 | ns | S1 p12 |
| B上升 | trB | 推挽；VCCA=2.5±0.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 11.9 | ns | S1 p12 |
| B上升 | trB | 推挽；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 8.8 | ns | S1 p12 |
| B上升 | trB | 推挽；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 7.6 | ns | S1 p12 |
| B上升 | trB | 推挽；VCCA=2.5±0.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 6.6 | ns | S1 p12 |
| B上升 | trB | 开漏；VCCA=2.5±0.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 170 | ns | S1 p12 |
| B上升 | trB | 开漏；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 170 | ns | S1 p12 |
| B上升 | trB | 开漏；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 120 | ns | S1 p12 |
| B上升 | trB | 开漏；VCCA=2.5±0.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 64 | ns | S1 p12 |
| A下降 | tfA | 推挽；VCCA=2.5±0.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 5.7 | ns | S1 p12 |
| A下降 | tfA | 推挽；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 5.7 | ns | S1 p12 |
| A下降 | tfA | 推挽；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 5.5 | ns | S1 p12 |
| A下降 | tfA | 推挽；VCCA=2.5±0.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 5.3 | ns | S1 p12 |
| A下降 | tfA | 开漏；VCCA=2.5±0.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 5.8 | ns | S1 p12 |
| A下降 | tfA | 开漏；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 5.8 | ns | S1 p12 |
| A下降 | tfA | 开漏；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 5.8 | ns | S1 p12 |
| A下降 | tfA | 开漏；VCCA=2.5±0.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 5.8 | ns | S1 p12 |
| B下降 | tfB | 推挽；VCCA=2.5±0.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 7.8 | ns | S1 p12 |
| B下降 | tfB | 推挽；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 7.8 | ns | S1 p12 |
| B下降 | tfB | 推挽；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 6.7 | ns | S1 p12 |
| B下降 | tfB | 推挽；VCCA=2.5±0.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 6.6 | ns | S1 p12 |
| B下降 | tfB | 开漏；VCCA=2.5±0.2 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 8.8 | ns | S1 p12 |
| B下降 | tfB | 开漏；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 8.8 | ns | S1 p12 |
| B下降 | tfB | 开漏；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 9.4 | ns | S1 p12 |
| B下降 | tfB | 开漏；VCCA=2.5±0.2 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 10.4 | ns | S1 p12 |
| 下降传播A→B | tPHL | 推挽；VCCA=3.3±0.3 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 3.5 | ns | S1 p13 |
| 下降传播A→B | tPHL | 推挽；VCCA=3.3±0.3 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 2.8 | ns | S1 p13 |
| 下降传播A→B | tPHL | 推挽；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 2.4 | ns | S1 p13 |
| 下降传播A→B | tPHL | 推挽；VCCA=3.3±0.3 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 3.1 | ns | S1 p13 |
| 下降传播A→B | tPHL | 开漏；VCCA=3.3±0.3 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 4.2 | ns | S1 p13 |
| 下降传播A→B | tPHL | 开漏；VCCA=3.3±0.3 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 4.2 | ns | S1 p13 |
| 下降传播A→B | tPHL | 开漏；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 4.2 | ns | S1 p13 |
| 下降传播A→B | tPHL | 开漏；VCCA=3.3±0.3 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 4.6 | ns | S1 p13 |
| 上升传播A→B | tPLH | 推挽；VCCA=3.3±0.3 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 4.2 | ns | S1 p13 |
| 上升传播A→B | tPLH | 推挽；VCCA=3.3±0.3 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 4.2 | ns | S1 p13 |
| 上升传播A→B | tPLH | 推挽；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 4.2 | ns | S1 p13 |
| 上升传播A→B | tPLH | 推挽；VCCA=3.3±0.3 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 4.4 | ns | S1 p13 |
| 上升传播A→B | tPLH | 开漏；VCCA=3.3±0.3 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 4.2 | ns | S1 p13 |
| 上升传播A→B | tPLH | 开漏；VCCA=3.3±0.3 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 4.2 | ns | S1 p13 |
| 上升传播A→B | tPLH | 开漏；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 4.2 | ns | S1 p13 |
| 上升传播A→B | tPLH | 开漏；VCCA=3.3±0.3 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 4.4 | ns | S1 p13 |
| 下降传播B→A | tPHL | 推挽；VCCA=3.3±0.3 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 2.9 | ns | S1 p13 |
| 下降传播B→A | tPHL | 推挽；VCCA=3.3±0.3 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 2.5 | ns | S1 p13 |
| 下降传播B→A | tPHL | 推挽；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 2.5 | ns | S1 p13 |
| 下降传播B→A | tPHL | 推挽；VCCA=3.3±0.3 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 3.3 | ns | S1 p13 |
| 下降传播B→A | tPHL | 开漏；VCCA=3.3±0.3 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 124 | ns | S1 p13 |
| 下降传播B→A | tPHL | 开漏；VCCA=3.3±0.3 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 124 | ns | S1 p13 |
| 下降传播B→A | tPHL | 开漏；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 124 | ns | S1 p13 |
| 下降传播B→A | tPHL | 开漏；VCCA=3.3±0.3 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 97 | ns | S1 p13 |
| 上升传播B→A | tPLH | 推挽；VCCA=3.3±0.3 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 10 | ns | S1 p13 |
| 上升传播B→A | tPLH | 推挽；VCCA=3.3±0.3 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 5 | ns | S1 p13 |
| 上升传播B→A | tPLH | 推挽；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 2.5 | ns | S1 p13 |
| 上升传播B→A | tPLH | 推挽；VCCA=3.3±0.3 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 2.6 | ns | S1 p13 |
| 上升传播B→A | tPLH | 开漏；VCCA=3.3±0.3 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 27.5 | ns | S1 p13 |
| 上升传播B→A | tPLH | 开漏；VCCA=3.3±0.3 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 15 | ns | S1 p13 |
| 上升传播B→A | tPLH | 开漏；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 2.5 | ns | S1 p13 |
| 上升传播B→A | tPLH | 开漏；VCCA=3.3±0.3 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 3.3 | ns | S1 p13 |
| 使能 | ten | OE→A/B；VCCA=3.3±0.3 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 200 | ns | S1 p13 |
| 使能 | ten | OE→A/B；VCCA=3.3±0.3 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 200 | ns | S1 p13 |
| 使能 | ten | OE→A/B；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 200 | ns | S1 p13 |
| 使能 | ten | OE→A/B；VCCA=3.3±0.3 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 200 | ns | S1 p13 |
| 禁止 | tdis | OE→A/B；VCCA=3.3±0.3 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 250 | ns | S1 p13 |
| 禁止 | tdis | OE→A/B；VCCA=3.3±0.3 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 200 | ns | S1 p13 |
| 禁止 | tdis | OE→A/B；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 250 | ns | S1 p13 |
| 禁止 | tdis | OE→A/B；VCCA=3.3±0.3 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 200 | ns | S1 p13 |
| A上升 | trA | 推挽；VCCA=3.3±0.3 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 11.6 | ns | S1 p13 |
| A上升 | trA | 推挽；VCCA=3.3±0.3 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 6.9 | ns | S1 p13 |
| A上升 | trA | 推挽；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 5.8 | ns | S1 p13 |
| A上升 | trA | 推挽；VCCA=3.3±0.3 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 5 | ns | S1 p13 |
| A上升 | trA | 开漏；VCCA=3.3±0.3 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 140 | ns | S1 p13 |
| A上升 | trA | 开漏；VCCA=3.3±0.3 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 140 | ns | S1 p13 |
| A上升 | trA | 开漏；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 140 | ns | S1 p13 |
| A上升 | trA | 开漏；VCCA=3.3±0.3 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 102 | ns | S1 p13 |
| B上升 | trB | 推挽；VCCA=3.3±0.3 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 11.3 | ns | S1 p13 |
| B上升 | trB | 推挽；VCCA=3.3±0.3 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 8.1 | ns | S1 p13 |
| B上升 | trB | 推挽；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 6.8 | ns | S1 p13 |
| B上升 | trB | 推挽；VCCA=3.3±0.3 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 7.4 | ns | S1 p13 |
| B上升 | trB | 开漏；VCCA=3.3±0.3 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 135 | ns | S1 p13 |
| B上升 | trB | 开漏；VCCA=3.3±0.3 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 130 | ns | S1 p13 |
| B上升 | trB | 开漏；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 130 | ns | S1 p13 |
| B上升 | trB | 开漏；VCCA=3.3±0.3 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 75 | ns | S1 p13 |
| A下降 | tfA | 推挽；VCCA=3.3±0.3 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 5.4 | ns | S1 p13 |
| A下降 | tfA | 推挽；VCCA=3.3±0.3 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 5.4 | ns | S1 p13 |
| A下降 | tfA | 推挽；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 5.4 | ns | S1 p13 |
| A下降 | tfA | 推挽；VCCA=3.3±0.3 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 5 | ns | S1 p13 |
| A下降 | tfA | 开漏；VCCA=3.3±0.3 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 6.1 | ns | S1 p13 |
| A下降 | tfA | 开漏；VCCA=3.3±0.3 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 6.1 | ns | S1 p13 |
| A下降 | tfA | 开漏；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 6.1 | ns | S1 p13 |
| A下降 | tfA | 开漏；VCCA=3.3±0.3 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 5.7 | ns | S1 p13 |
| B下降 | tfB | 推挽；VCCA=3.3±0.3 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 7.4 | ns | S1 p13 |
| B下降 | tfB | 推挽；VCCA=3.3±0.3 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 7.4 | ns | S1 p13 |
| B下降 | tfB | 推挽；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 7.4 | ns | S1 p13 |
| B下降 | tfB | 推挽；VCCA=3.3±0.3 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 7.6 | ns | S1 p13 |
| B下降 | tfB | 开漏；VCCA=3.3±0.3 V，VCCB=1.8±0.15 V，TA=−40～125 °C |  |  | 7.6 | ns | S1 p13 |
| B下降 | tfB | 开漏；VCCA=3.3±0.3 V，VCCB=2.5±0.2 V，TA=−40～125 °C |  |  | 7.6 | ns | S1 p13 |
| B下降 | tfB | 开漏；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V，TA=−40～125 °C |  |  | 7.6 | ns | S1 p13 |
| B下降 | tfB | 开漏；VCCA=3.3±0.3 V，VCCB=5±0.5 V，TA=−40～125 °C |  |  | 8.3 | ns | S1 p13 |
| 最大数据率保证能力 | TMAX | 推挽；VCCA=1.2±0.1 V；VCCB各额定档；50%占空，单通道切换 | 24 |  |  | Mbps | S1 p14 |
| 最大数据率保证能力 | TMAX | 开漏；VCCA=1.2±0.1 V；VCCB各额定档；50%占空，单通道切换 | 1 |  |  | Mbps | S1 p14 |
| 最大数据率保证能力 | TMAX | 推挽；VCCA=1.5±0.1 V；VCCB各额定档；50%占空，单通道切换 | 24 |  |  | Mbps | S1 p14 |
| 最大数据率保证能力 | TMAX | 开漏；VCCA=1.5±0.1 V；VCCB各额定档；50%占空，单通道切换 | 2 |  |  | Mbps | S1 p14 |
| 最大数据率保证能力 | TMAX | 推挽；VCCA=1.8±0.15 V；VCCB各额定档；50%占空，单通道切换 | 50 |  |  | Mbps | S1 p14 |
| 最大数据率保证能力 | TMAX | 开漏；VCCA=1.8±0.15 V；VCCB各额定档；50%占空，单通道切换 | 2 |  |  | Mbps | S1 p14 |
| 最大数据率保证能力 | TMAX | 推挽；VCCA=2.5±0.2 V；VCCB各额定档；50%占空，单通道切换 | 50 |  |  | Mbps | S1 p14 |
| 最大数据率保证能力 | TMAX | 开漏；VCCA=2.5±0.2 V；VCCB各额定档；50%占空，单通道切换 | 2 |  |  | Mbps | S1 p14 |
| 最大数据率保证能力 | TMAX | 推挽；VCCA=3.3±0.3 V；VCCB各额定档；50%占空，单通道切换 | 50 |  |  | Mbps | S1 p14 |
| 最大数据率保证能力 | TMAX | 开漏；VCCA=3.3±0.3 V；VCCB各额定档；50%占空，单通道切换 | 2 |  |  | Mbps | S1 p14 |
| 输入脉宽 | tw | 推挽，表列VCCA/VCCB范围 | 41 |  |  | ns | S1 p15 |
| 输入脉宽 | tw | 开漏，表列VCCA/VCCB范围 | 500 |  |  | ns | S1 p15 |
| 同向输出偏斜 | tsk | VCCA=1.65～3.6 V、VCCB=2.3～5.5 V，推挽/开漏 |  |  | 1 | ns | S1 p15 |

用这些数时要注意：

- RUT脚表写VCCB=2.3～5.5 V，通用推荐表为1.65～5.5 V；选RUT时不能忽略差异。p4/p5允许VCCA高于或低于VCCB（S1 p4～p6）。
- p10开漏A输出上升最大值：VCCA=1.5±0.1 V，VCCB=1.8±0.15 V时166.3 ns、VCCB=3.3±0.3 V时102.1 ns。原表数值分成两行，文字工具不能抽成完整小数，保留此处（见 S1 p10 表）。
- p14的“Maximum Data Rate”数值在MIN列，表示最低保证的最大可用速率，按原列保留；p15推挽最小脉宽41 ns与高压档50 Mbps能力并列，手册未解释适用差异，不自行协调或推算（S1 p14、p15）。
- p11把A/B的上升及下降符号重复写成trA/tfA，本条按方向列名区分，未改数。p13开漏B→A下降传播为124/97 ns，虽显著大于其他档仍照抄（S1 p11、p13）。
- I/O电容只有典型及上限，室温与高温上限不同；内部10 kΩ未给容差。开关数依赖驱动阻抗和负载，不能当成任意板级布线的保证（S1 p8、p20）。

## 热特性

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- |
| 结到环境 | RθJA | RGY | 52.9 | °C/W | S1 p7 |
| 结到环境 | RθJA | BQA | 73.5 | °C/W | S1 p7 |
| 结到环境 | RθJA | RUT | 150.4 | °C/W | S1 p7 |
| 结到环境 | RθJA | D | 93.7 | °C/W | S1 p7 |
| 结到环境 | RθJA | PW | 115.2 | °C/W | S1 p7 |
| 结到壳顶 | RθJC(top) | RGY | 54.3 | °C/W | S1 p7 |
| 结到壳顶 | RθJC(top) | BQA | 76.9 | °C/W | S1 p7 |
| 结到壳顶 | RθJC(top) | RUT | 68.6 | °C/W | S1 p7 |
| 结到壳顶 | RθJC(top) | D | 53.8 | °C/W | S1 p7 |
| 结到壳顶 | RθJC(top) | PW | 46.2 | °C/W | S1 p7 |
| 结到板 | RθJB | RGY | 28.4 | °C/W | S1 p7 |
| 结到板 | RθJB | BQA | 43.0 | °C/W | S1 p7 |
| 结到板 | RθJB | RUT | 76.3 | °C/W | S1 p7 |
| 结到板 | RθJB | D | 52.0 | °C/W | S1 p7 |
| 结到板 | RθJB | PW | 70.9 | °C/W | S1 p7 |
| 结到顶参数 | ψJT | RGY | 2.7 | °C/W | S1 p7 |
| 结到顶参数 | ψJT | BQA | 4.7 | °C/W | S1 p7 |
| 结到顶参数 | ψJT | RUT | 2.4 | °C/W | S1 p7 |
| 结到顶参数 | ψJT | D | 13.4 | °C/W | S1 p7 |
| 结到顶参数 | ψJT | PW | 3.4 | °C/W | S1 p7 |
| 结到板参数 | ψJB | RGY | 28.3 | °C/W | S1 p7 |
| 结到板参数 | ψJB | BQA | 42.9 | °C/W | S1 p7 |
| 结到板参数 | ψJB | RUT | 76.2 | °C/W | S1 p7 |
| 结到板参数 | ψJB | D | 51.6 | °C/W | S1 p7 |
| 结到板参数 | ψJB | PW | 70.2 | °C/W | S1 p7 |
| 结到壳底 | RθJC(bot) | RGY | 12 | °C/W | S1 p7 |
| 结到壳底 | RθJC(bot) | BQA | 19.6 | °C/W | S1 p7 |

## 静电额定

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- |
| 人体模型 | V(ESD) | A口，JS-001 | ±2000 | V | S1 p6 |
| 人体模型 | V(ESD) | B口，JS-001 | ±8000 | V | S1 p6 |
| 带电器件模型 | V(ESD) | A/B口，JS-002 | ±1000 | V | S1 p6 |

静电警告译文：本器件可能被静电损坏，应采取适当防护；不正确操作或安装可能造成性能退化到完全失效（S1 p24）。

## 引脚与处置

### D/PW/RGY

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
| --- | --- | --- | --- | --- |
| 1 VCCA | —；A电源 | 见推荐条件 |  | S1 p4 |
| 2 A1、3 A2、4 A3、5 A4 | I/O；参考VCCA | 见推荐条件 |  | S1 p4 |
| 7 GND | —；地 |  | 接地 | S1 p4 |
| 8 OE | I；参考VCCA，低高阻 | 见推荐条件 | 上电保持低 | S1 p4 |
| 10 B4、11 B3、12 B2、13 B1 | I/O；参考VCCB | 见推荐条件 |  | S1 p4 |
| 14 VCCB | —；B电源 | 见推荐条件 |  | S1 p4 |
| 散热焊盘 | RGY裸露中心焊盘必须接地；原脚表未说明内部接脚；封装图要求焊接到PCB保证热机械性能 |  |  | S1 p4、p30 |

### RUT

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
| --- | --- | --- | --- | --- |
| 1 VCCA | —；A电源 | 见推荐条件 |  | S1 p5 |
| 2 A1、3 A2、4 A3、5 A4 | I/O；参考VCCA | 见推荐条件 |  | S1 p5 |
| 6 GND | —；地 |  | 接地 | S1 p5 |
| 7 B4、8 B3、9 B2、10 B1 | I/O；参考VCCB | 见推荐条件 |  | S1 p5 |
| 11 VCCB | —；B电源 | 脚表下限见注意 |  | S1 p5 |
| 12 OE | I；低高阻，参考VCCA | 见推荐条件 |  | S1 p5 |
| 散热焊盘 | RUT未列独立散热焊盘，未给内部连接或必须焊接规定 |  |  | S1 p5 |

手册热表提到BQA，但未给独立BQA引脚表，不能自行套用。

## 必需外围

内部每端10 kΩ上拉，不必统一外加上拉；确需更小上拉时可并联。电源就近旁路，典型应用各0.1 µF；OE上下电用下拉保持低，稳定后才使能（S1 p19～p23）。

## 订货型号与封装

RUT=12脚UQFN，R=卷带；所附订货表仅列以下型号，正文其他封装不自行补造订货型号。

| 订货型号或后缀 | 封装 | 脚数 | 电压或功能档 | 温度范围 | 引脚镀层 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| TXS0104WRUTR | UQFN (RUT) | 12 |  | −40～125 °C | NIPDAU | S1 p26 |

## 核对记录

- 2026-11-10：逐页对照原件，工具核对通过，核对 502 个数。
