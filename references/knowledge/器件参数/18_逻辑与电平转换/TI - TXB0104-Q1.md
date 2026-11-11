# TI TXB0104-Q1

类别：器件参数。
器件：四通道自动方向推挽电平转换器。
手册：SCES727D，2025-05修订；订货附录2025-11-07。

## 来源

- S1：Datasheet/18_逻辑与电平转换/电平转换器_电压翻译器/TI - TXB0104-Q1.pdf

页码均为 PDF 文件页序，共 38 页。

## 绝对最大值

| 参数 | 符号 | 条件 | 最小 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| A 电源/输入/高阻或断电输出 | VCCA、VI、VO |  | −0.5 | 4.6 | V | S1 p5 |
| B 电源/输入/高阻或断电输出 | VCCB、VI、VO |  | −0.5 | 6.5 | V | S1 p5 |
| 有效输出电压 | VO | A端 | −0.5 | VCCA + 0.5 | V | S1 p5 |
| 有效输出电压 | VO | B端 | −0.5 | VCCB + 0.5 | V | S1 p5 |
| 输入钳位电流 | IIK | VI<0 |  | −50 | mA | S1 p5 |
| 输出钳位电流 | IOK | VO<0 |  | −50 | mA | S1 p5 |
| 连续输出电流 | IO |  |  | ±50 | mA | S1 p5 |
| 电源/地连续电流 |  |  |  | ±100 | mA | S1 p5 |
| 储存温度 | Tstg |  | −65 | 150 | °C | S1 p5 |

## 推荐工作条件

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A 侧电源 | VCCA | VCCA≤VCCB | 1.2 |  | 3.6 | V | S1 p5 |
| B 侧电源 | VCCB |  | 1.65 |  | 5.5 | V | S1 p5 |
| 数据高输入 | VIH | VCCI为输入端电源 | VCCI × 0.65 |  | VCCI | V | S1 p5 |
| OE 高输入 | VIH |  | VCCA × 0.65 |  | 5.5 | V | S1 p5 |
| 数据低输入 | VIL |  | 0 |  | VCCI × 0.35 | V | S1 p5 |
| OE 低输入 | VIL |  | 0 |  | VCCA × 0.35 | V | S1 p5 |
| 高阻/断电A输出 | VO |  | 0 |  | 3.6 | V | S1 p5 |
| 高阻/断电B输出 | VO |  | 0 |  | 5.5 | V | S1 p5 |
| A 输入上升/下降速率 | Δt/Δv |  |  |  | 40 | ns/V | S1 p5 |
| B 输入上升/下降速率 | Δt/Δv | VCCB=1.65～3.6 V |  |  | 40 | ns/V | S1 p5 |
| B 输入上升/下降速率 | Δt/Δv | VCCB=4.5～5.5 V |  |  | 30 | ns/V | S1 p5 |
| 环境温度 | TA |  | −40 |  | 125 | °C | S1 p6 |

## 电气特性

除明确室温典型值外，DC及时序限值为TA=−40～125 °C；VCCI/VCCO分别指输入/输出端电源。开关测量负载15 pF，见S1 p14。

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A高输出 | VOHA | BQA；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；VCCA=1.2 V，IOH=−20 µA，TA=25 °C |  | 1.1 |  | V | S1 p6 |
| A低输出 | VOLA | BQA；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；VCCA=1.2 V，IOL=20 µA，TA=25 °C |  | 0.9 |  | V | S1 p6 |
| A高输出 | VOHA | BQA；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；VCCA=1.4～3.6 V，IOH=−20 µA | VCCA − 0.4 |  |  | V | S1 p6 |
| A低输出 | VOLA | BQA；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；VCCA=1.4～3.6 V，IOL=20 µA |  |  | 0.4 | V | S1 p6 |
| B高输出 | VOHB | BQA；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；IOH=−20 µA | VCCB − 0.4 |  |  | V | S1 p6 |
| B低输出 | VOLB | BQA；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；IOL=20 µA |  |  | 0.4 | V | S1 p6 |
| OE输入电流 | II | BQA；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；VI=VCCI或GND；TA=25 °C |  |  | ±1 | µA | S1 p6 |
| OE输入电流 | II | BQA；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；VI=VCCI或GND；TA=−40～125 °C |  |  | ±5 | µA | S1 p6 |
| 断电A漏电 | Ioff | BQA；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；VCCA=0 V，VCCB=0～5.5 V，VI/VO=0～3.6 V；TA=25 °C |  |  | ±1 | µA | S1 p6 |
| 断电A漏电 | Ioff | BQA；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；VCCA=0 V，VCCB=0～5.5 V，VI/VO=0～3.6 V；TA=−40～125 °C |  |  | ±10 | µA | S1 p6 |
| 断电B漏电 | Ioff | BQA；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；VCCB=0 V，VCCA=0～3.6 V，VI/VO=0～5.5 V；TA=25 °C |  |  | ±1 | µA | S1 p6 |
| 断电B漏电 | Ioff | BQA；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；VCCB=0 V，VCCA=0～3.6 V，VI/VO=0～5.5 V；TA=−40～125 °C |  |  | ±10 | µA | S1 p6 |
| 高阻电流 | IOZ | BQA；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；OE=GND；TA=25 °C |  |  | ±1 | µA | S1 p6 |
| 高阻电流 | IOZ | BQA；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；OE=GND；TA=−40～125 °C |  |  | ±10 | µA | S1 p6 |
| 电源电流 | ICCA | BQA；VCCA=1.2 V，VCCB=1.65～5.5 V，VI=VCCI或GND，IO=0，TA=25 °C |  | 0.4 |  | µA | S1 p6 |
| 电源电流 | ICCA | BQA；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；VCCA=1.4～3.6 V，VI=VCCI或GND，IO=0 |  |  | 20 | µA | S1 p6 |
| 电源电流 | ICCB | BQA；VCCA=1.2 V，VCCB=1.65～5.5 V，VI=VCCI或GND，IO=0，TA=25 °C |  | 3.4 |  | µA | S1 p6 |
| 电源电流 | ICCB | BQA；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；VCCA=1.4～3.6 V，VI=VCCI或GND，IO=0 |  |  | 20 | µA | S1 p6 |
| 电源电流 | ICCA + ICCB | BQA；VCCA=1.2 V，VCCB=1.65～5.5 V，VI=VCCI或GND，IO=0，TA=25 °C |  | 3.5 |  | µA | S1 p6 |
| 电源电流 | ICCA + ICCB | BQA；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；VCCA=1.4～3.6 V，VI=VCCI或GND，IO=0 |  |  | 40 | µA | S1 p6 |
| 单侧掉电电源电流 | ICCA | BQA；VCCA=3.6 V，VCCB=0 V，VI=VCCI或GND，IO=0 |  |  | 15 | µA | S1 p6 |
| 单侧掉电电源电流 | ICCA | BQA；VCCA=0 V，VCCB=5.5 V，VI=VCCI或GND，IO=0 |  |  | −15 | µA | S1 p6 |
| 单侧掉电电源电流 | ICCB | BQA；VCCA=3.6 V，VCCB=0 V，VI=VCCI或GND，IO=0 |  |  | −15 | µA | S1 p6 |
| 单侧掉电电源电流 | ICCB | BQA；VCCA=0 V，VCCB=5.5 V，VI=VCCI或GND，IO=0 |  |  | 15 | µA | S1 p6 |
| 禁用电源电流 | ICCZA | BQA；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；OE=GND，IO=0，VI=VCCI或GND，VCCA=1.2 V，TA=25 °C |  | 0.4 |  | µA | S1 p7 |
| 禁用电源电流 | ICCZA | BQA；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；OE=GND，IO=0，VI=VCCI或GND，VCCA=1.4～3.6 V |  |  | 15 | µA | S1 p7 |
| 禁用电源电流 | ICCZB | BQA；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；OE=GND，IO=0，VI=VCCI或GND，VCCA=1.2 V，TA=25 °C |  | 3.3 |  | µA | S1 p7 |
| 禁用电源电流 | ICCZB | BQA；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；OE=GND，IO=0，VI=VCCI或GND，VCCA=1.4～3.6 V |  |  | 15 | µA | S1 p7 |
| A高输出 | VOHA | 其他封装；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；VCCA=1.2 V，IOH=−20 µA，TA=25 °C |  | 1.1 |  | V | S1 p7 |
| A低输出 | VOLA | 其他封装；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；VCCA=1.2 V，IOL=20 µA，TA=25 °C |  | 0.9 |  | V | S1 p7 |
| A高输出 | VOHA | 其他封装；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；VCCA=1.4～3.6 V，IOH=−20 µA | VCCA − 0.4 |  |  | V | S1 p7 |
| A低输出 | VOLA | 其他封装；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；VCCA=1.4～3.6 V，IOL=20 µA |  |  | 0.4 | V | S1 p7 |
| B高输出 | VOHB | 其他封装；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；IOH=−20 µA | VCCB − 0.4 |  |  | V | S1 p7 |
| B低输出 | VOLB | 其他封装；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；IOL=20 µA |  |  | 0.4 | V | S1 p7 |
| OE输入电流 | II | 其他封装；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；VI=VCCI或GND；TA=25 °C |  |  | ±1 | µA | S1 p7 |
| OE输入电流 | II | 其他封装；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；VI=VCCI或GND；TA=−40～125 °C |  |  | ±5 | µA | S1 p7 |
| 断电A漏电 | Ioff | 其他封装；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；VCCA=0 V，VCCB=0～5.5 V，VI/VO=0～3.6 V；TA=25 °C |  |  | ±1 | µA | S1 p7 |
| 断电A漏电 | Ioff | 其他封装；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；VCCA=0 V，VCCB=0～5.5 V，VI/VO=0～3.6 V；TA=−40～125 °C |  |  | ±10 | µA | S1 p7 |
| 断电B漏电 | Ioff | 其他封装；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；VCCB=0 V，VCCA=0～3.6 V，VI/VO=0～5.5 V；TA=25 °C |  |  | ±1 | µA | S1 p7 |
| 断电B漏电 | Ioff | 其他封装；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；VCCB=0 V，VCCA=0～3.6 V，VI/VO=0～5.5 V；TA=−40～125 °C |  |  | ±10 | µA | S1 p7 |
| 高阻电流 | IOZ | 其他封装；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；OE=GND；TA=25 °C |  |  | ±1 | µA | S1 p7 |
| 高阻电流 | IOZ | 其他封装；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；OE=GND；TA=−40～125 °C |  |  | ±10 | µA | S1 p7 |
| 电源电流 | ICCA | 其他封装；VCCA=1.2 V，VCCB=1.65～5.5 V，VI=VCCI或GND，IO=0，TA=25 °C |  | 0.06 |  | µA | S1 p7 |
| 电源电流 | ICCA | 其他封装；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；VCCA=1.4～3.6 V，VI=VCCI或GND，IO=0 |  |  | 20 | µA | S1 p7 |
| 电源电流 | ICCB | 其他封装；VCCA=1.2 V，VCCB=1.65～5.5 V，VI=VCCI或GND，IO=0，TA=25 °C |  | 3.4 |  | µA | S1 p7 |
| 电源电流 | ICCB | 其他封装；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；VCCA=1.4～3.6 V，VI=VCCI或GND，IO=0 |  |  | 20 | µA | S1 p7 |
| 电源电流 | ICCA + ICCB | 其他封装；VCCA=1.2 V，VCCB=1.65～5.5 V，VI=VCCI或GND，IO=0，TA=25 °C |  | 3.5 |  | µA | S1 p7 |
| 电源电流 | ICCA + ICCB | 其他封装；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；VCCA=1.4～3.6 V，VI=VCCI或GND，IO=0 |  |  | 40 | µA | S1 p7 |
| 单侧掉电电源电流 | ICCA | 其他封装；VCCA=3.6 V，VCCB=0 V，VI=VCCI或GND，IO=0 |  |  | 15 | µA | S1 p7 |
| 单侧掉电电源电流 | ICCA | 其他封装；VCCA=0 V，VCCB=5.5 V，VI=VCCI或GND，IO=0 |  |  | −15 | µA | S1 p7 |
| 单侧掉电电源电流 | ICCB | 其他封装；VCCA=3.6 V，VCCB=0 V，VI=VCCI或GND，IO=0 |  |  | −15 | µA | S1 p7 |
| 单侧掉电电源电流 | ICCB | 其他封装；VCCA=0 V，VCCB=5.5 V，VI=VCCI或GND，IO=0 |  |  | 15 | µA | S1 p7 |
| 禁用电源电流 | ICCZA | 其他封装；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；OE=GND，IO=0，VI=VCCI或GND，VCCA=1.2 V，TA=25 °C |  | 0.05 |  | µA | S1 p7 |
| 禁用电源电流 | ICCZA | 其他封装；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；OE=GND，IO=0，VI=VCCI或GND，VCCA=1.4～3.6 V |  |  | 15 | µA | S1 p7 |
| 禁用电源电流 | ICCZB | 其他封装；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；OE=GND，IO=0，VI=VCCI或GND，VCCA=1.2 V，TA=25 °C |  | 3.3 |  | µA | S1 p7 |
| 禁用电源电流 | ICCZB | 其他封装；VCCA=1.2～3.6 V，VCCB=1.65～5.5 V；OE=GND，IO=0，VI=VCCI或GND，VCCA=1.4～3.6 V |  |  | 15 | µA | S1 p7 |
| OE输入电容 | Ci | BQA；TA=25 °C，额定供电；Ci见p7 |  | 4 |  | pF | S1 p7 |
| A端电容 | Cio | BQA；TA=25 °C，额定供电；Ci见p7 |  | 6 |  | pF | S1 p7 |
| B端电容 | Cio | BQA；TA=25 °C，额定供电；Ci见p7 |  | 13 |  | pF | S1 p7 |
| OE输入电容 | Ci | PW/RGY；TA=25 °C，额定供电；Ci见p7 |  | 3 |  | pF | S1 p7 |
| A端电容 | Cio | PW/RGY；TA=25 °C，额定供电；Ci见p7 |  | 5 |  | pF | S1 p8 |
| B端电容 | Cio | PW/RGY；TA=25 °C，额定供电；Ci见p7 |  | 11 |  | pF | S1 p8 |
| OE输入电容 | Ci | RUT；TA=25 °C，额定供电；Ci见p7 |  | 4 |  | pF | S1 p7 |
| A端电容 | Cio | RUT；TA=25 °C，额定供电；Ci见p7 |  | 6 |  | pF | S1 p8 |
| B端电容 | Cio | RUT；TA=25 °C，额定供电；Ci见p7 |  | 13 |  | pF | S1 p8 |
| 数据速率 |  | PW/RGY/BQA；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V |  |  | 40 | Mbps | S1 p8 |
| 数据脉宽 | tw | PW/RGY/BQA；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V | 25 |  |  | ns | S1 p8 |
| 数据速率 |  | PW/RGY/BQA；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V |  |  | 40 | Mbps | S1 p8 |
| 数据脉宽 | tw | PW/RGY/BQA；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V | 25 |  |  | ns | S1 p8 |
| 数据速率 |  | PW/RGY/BQA；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V |  |  | 40 | Mbps | S1 p8 |
| 数据脉宽 | tw | PW/RGY/BQA；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V | 25 |  |  | ns | S1 p8 |
| 数据速率 |  | PW/RGY/BQA；VCCA=1.5±0.1 V，VCCB=5±0.5 V |  |  | 40 | Mbps | S1 p8 |
| 数据脉宽 | tw | PW/RGY/BQA；VCCA=1.5±0.1 V，VCCB=5±0.5 V | 25 |  |  | ns | S1 p8 |
| 数据速率 |  | RUT；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V |  |  | 37 | Mbps | S1 p8 |
| 数据脉宽 | tw | RUT；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V | 27 |  |  | ns | S1 p8 |
| 数据速率 |  | RUT；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V |  |  | 37 | Mbps | S1 p8 |
| 数据脉宽 | tw | RUT；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V | 27 |  |  | ns | S1 p8 |
| 数据速率 |  | RUT；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V |  |  | 40 | Mbps | S1 p8 |
| 数据脉宽 | tw | RUT；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V | 25 |  |  | ns | S1 p8 |
| 数据速率 |  | RUT；VCCA=1.5±0.1 V，VCCB=5±0.5 V |  |  | 40 | Mbps | S1 p8 |
| 数据脉宽 | tw | RUT；VCCA=1.5±0.1 V，VCCB=5±0.5 V | 25 |  |  | ns | S1 p8 |
| 数据速率 |  | PW/RGY/BQA；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 55 | Mbps | S1 p8 |
| 数据脉宽 | tw | PW/RGY/BQA；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V | 18 |  |  | ns | S1 p8 |
| 数据速率 |  | PW/RGY/BQA；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V |  |  | 55 | Mbps | S1 p8 |
| 数据脉宽 | tw | PW/RGY/BQA；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V | 18 |  |  | ns | S1 p8 |
| 数据速率 |  | PW/RGY/BQA；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 55 | Mbps | S1 p8 |
| 数据脉宽 | tw | PW/RGY/BQA；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V | 18 |  |  | ns | S1 p8 |
| 数据速率 |  | PW/RGY/BQA；VCCA=1.8±0.15 V，VCCB=5±0.5 V |  |  | 55 | Mbps | S1 p8 |
| 数据脉宽 | tw | PW/RGY/BQA；VCCA=1.8±0.15 V，VCCB=5±0.5 V | 18 |  |  | ns | S1 p8 |
| 数据速率 |  | RUT；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 37 | Mbps | S1 p8 |
| 数据脉宽 | tw | RUT；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V | 27 |  |  | ns | S1 p8 |
| 数据速率 |  | RUT；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V |  |  | 37 | Mbps | S1 p8 |
| 数据脉宽 | tw | RUT；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V | 27 |  |  | ns | S1 p8 |
| 数据速率 |  | RUT；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 55 | Mbps | S1 p8 |
| 数据脉宽 | tw | RUT；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V | 18 |  |  | ns | S1 p8 |
| 数据速率 |  | RUT；VCCA=1.8±0.15 V，VCCB=5±0.5 V |  |  | 55 | Mbps | S1 p8 |
| 数据脉宽 | tw | RUT；VCCA=1.8±0.15 V，VCCB=5±0.5 V | 18 |  |  | ns | S1 p8 |
| 数据速率 |  | PW/RGY/BQA；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V |  |  | 75 | Mbps | S1 p9 |
| 数据脉宽 | tw | PW/RGY/BQA；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V | 13 |  |  | ns | S1 p9 |
| 数据速率 |  | PW/RGY/BQA；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V |  |  | 80 | Mbps | S1 p9 |
| 数据脉宽 | tw | PW/RGY/BQA；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V | 12 |  |  | ns | S1 p9 |
| 数据速率 |  | PW/RGY/BQA；VCCA=2.5±0.2 V，VCCB=5±0.5 V |  |  | 100 | Mbps | S1 p9 |
| 数据脉宽 | tw | PW/RGY/BQA；VCCA=2.5±0.2 V，VCCB=5±0.5 V | 10 |  |  | ns | S1 p9 |
| 数据速率 |  | RUT；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V |  |  | 65 | Mbps | S1 p9 |
| 数据脉宽 | tw | RUT；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V | 15 |  |  | ns | S1 p9 |
| 数据速率 |  | RUT；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V |  |  | 80 | Mbps | S1 p9 |
| 数据脉宽 | tw | RUT；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V | 12 |  |  | ns | S1 p9 |
| 数据速率 |  | RUT；VCCA=2.5±0.2 V，VCCB=5±0.5 V |  |  | 85 | Mbps | S1 p9 |
| 数据脉宽 | tw | RUT；VCCA=2.5±0.2 V，VCCB=5±0.5 V | 11 |  |  | ns | S1 p9 |
| 数据速率 |  | PW/RGY/BQA；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V |  |  | 100 | Mbps | S1 p9 |
| 数据脉宽 | tw | PW/RGY/BQA；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V | 10 |  |  | ns | S1 p9 |
| 数据速率 |  | PW/RGY/BQA；VCCA=3.3±0.3 V，VCCB=5±0.5 V |  |  | 100 | Mbps | S1 p9 |
| 数据脉宽 | tw | PW/RGY/BQA；VCCA=3.3±0.3 V，VCCB=5±0.5 V | 10 |  |  | ns | S1 p9 |
| 数据速率 |  | RUT；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V |  |  | 90 | Mbps | S1 p9 |
| 数据脉宽 | tw | RUT；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V | 11 |  |  | ns | S1 p9 |
| 数据速率 |  | RUT；VCCA=3.3±0.3 V，VCCB=5±0.5 V |  |  | 90 | Mbps | S1 p9 |
| 数据脉宽 | tw | RUT；VCCA=3.3±0.3 V，VCCB=5±0.5 V | 11 |  |  | ns | S1 p9 |
| 传播延迟A→B | tpd | BQA；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V |  |  | 15.9 | ns | S1 p10 |
| 传播延迟A→B | tpd | BQA；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V |  |  | 13.1 | ns | S1 p10 |
| 传播延迟A→B | tpd | BQA；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V |  |  | 13 | ns | S1 p10 |
| 传播延迟A→B | tpd | BQA；VCCA=1.5±0.1 V，VCCB=5±0.5 V |  |  | 12.9 | ns | S1 p10 |
| 传播延迟B→A | tpd | BQA；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V |  |  | 17.2 | ns | S1 p10 |
| 传播延迟B→A | tpd | BQA；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V |  |  | 15 | ns | S1 p10 |
| 传播延迟B→A | tpd | BQA；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V |  |  | 14.7 | ns | S1 p10 |
| 传播延迟B→A | tpd | BQA；VCCA=1.5±0.1 V，VCCB=5±0.5 V |  |  | 16.7 | ns | S1 p10 |
| 使能A | ten | BQA；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V |  |  | 1 | µs | S1 p10 |
| 使能A | ten | BQA；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V |  |  | 1 | µs | S1 p10 |
| 使能A | ten | BQA；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V |  |  | 1 | µs | S1 p10 |
| 使能A | ten | BQA；VCCA=1.5±0.1 V，VCCB=5±0.5 V |  |  | 1 | µs | S1 p10 |
| 使能B | ten | BQA；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V |  |  | 1 | µs | S1 p10 |
| 使能B | ten | BQA；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V |  |  | 1 | µs | S1 p10 |
| 使能B | ten | BQA；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V |  |  | 1 | µs | S1 p10 |
| 使能B | ten | BQA；VCCA=1.5±0.1 V，VCCB=5±0.5 V |  |  | 1 | µs | S1 p10 |
| 禁止A | tdis | BQA；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V |  |  | 390 | ns | S1 p10 |
| 禁止A | tdis | BQA；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V |  |  | 305 | ns | S1 p10 |
| 禁止A | tdis | BQA；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V |  |  | 305 | ns | S1 p10 |
| 禁止A | tdis | BQA；VCCA=1.5±0.1 V，VCCB=5±0.5 V |  |  | 305 | ns | S1 p10 |
| 禁止B | tdis | BQA；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V |  |  | 390 | ns | S1 p10 |
| 禁止B | tdis | BQA；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V |  |  | 305 | ns | S1 p10 |
| 禁止B | tdis | BQA；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V |  |  | 305 | ns | S1 p10 |
| 禁止B | tdis | BQA；VCCA=1.5±0.1 V，VCCB=5±0.5 V |  |  | 305 | ns | S1 p10 |
| A上升/下降 | trA、tfA | BQA；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V |  |  | 7.1 | ns | S1 p10 |
| A上升/下降 | trA、tfA | BQA；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V |  |  | 7.1 | ns | S1 p10 |
| A上升/下降 | trA、tfA | BQA；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V |  |  | 7.1 | ns | S1 p10 |
| A上升/下降 | trA、tfA | BQA；VCCA=1.5±0.1 V，VCCB=5±0.5 V |  |  | 7.1 | ns | S1 p10 |
| B上升/下降 | trB、tfB | BQA；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V |  |  | 6.5 | ns | S1 p10 |
| B上升/下降 | trB、tfB | BQA；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V |  |  | 5.2 | ns | S1 p10 |
| B上升/下降 | trB、tfB | BQA；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V |  |  | 4.8 | ns | S1 p10 |
| B上升/下降 | trB、tfB | BQA；VCCA=1.5±0.1 V，VCCB=5±0.5 V |  |  | 4.7 | ns | S1 p10 |
| 传播延迟A→B | tpd | 其他封装；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V |  |  | 15.9 | ns | S1 p10 |
| 传播延迟A→B | tpd | 其他封装；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V |  |  | 13.1 | ns | S1 p10 |
| 传播延迟A→B | tpd | 其他封装；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V |  |  | 13 | ns | S1 p10 |
| 传播延迟A→B | tpd | 其他封装；VCCA=1.5±0.1 V，VCCB=5±0.5 V |  |  | 12.9 | ns | S1 p10 |
| 传播延迟B→A | tpd | 其他封装；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V |  |  | 17.2 | ns | S1 p10 |
| 传播延迟B→A | tpd | 其他封装；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V |  |  | 15 | ns | S1 p10 |
| 传播延迟B→A | tpd | 其他封装；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V |  |  | 14.7 | ns | S1 p10 |
| 传播延迟B→A | tpd | 其他封装；VCCA=1.5±0.1 V，VCCB=5±0.5 V |  |  | 16.7 | ns | S1 p10 |
| 使能A | ten | 其他封装；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V |  |  | 1 | µs | S1 p10 |
| 使能A | ten | 其他封装；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V |  |  | 1 | µs | S1 p10 |
| 使能A | ten | 其他封装；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V |  |  | 1 | µs | S1 p10 |
| 使能A | ten | 其他封装；VCCA=1.5±0.1 V，VCCB=5±0.5 V |  |  | 1 | µs | S1 p10 |
| 使能B | ten | 其他封装；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V |  |  | 1 | µs | S1 p10 |
| 使能B | ten | 其他封装；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V |  |  | 1 | µs | S1 p10 |
| 使能B | ten | 其他封装；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V |  |  | 1 | µs | S1 p10 |
| 使能B | ten | 其他封装；VCCA=1.5±0.1 V，VCCB=5±0.5 V |  |  | 1 | µs | S1 p10 |
| 禁止A | tdis | 其他封装；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V |  |  | 340 | ns | S1 p10 |
| 禁止A | tdis | 其他封装；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V |  |  | 280 | ns | S1 p10 |
| 禁止A | tdis | 其他封装；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V |  |  | 280 | ns | S1 p10 |
| 禁止A | tdis | 其他封装；VCCA=1.5±0.1 V，VCCB=5±0.5 V |  |  | 300 | ns | S1 p10 |
| 禁止B | tdis | 其他封装；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V |  |  | 220 | ns | S1 p10 |
| 禁止B | tdis | 其他封装；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V |  |  | 220 | ns | S1 p10 |
| 禁止B | tdis | 其他封装；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V |  |  | 220 | ns | S1 p10 |
| 禁止B | tdis | 其他封装；VCCA=1.5±0.1 V，VCCB=5±0.5 V |  |  | 220 | ns | S1 p10 |
| A上升/下降 | trA、tfA | 其他封装；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V |  |  | 7.1 | ns | S1 p10 |
| A上升/下降 | trA、tfA | 其他封装；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V |  |  | 7.1 | ns | S1 p10 |
| A上升/下降 | trA、tfA | 其他封装；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V |  |  | 7.1 | ns | S1 p10 |
| A上升/下降 | trA、tfA | 其他封装；VCCA=1.5±0.1 V，VCCB=5±0.5 V |  |  | 7.1 | ns | S1 p10 |
| B上升/下降 | trB、tfB | 其他封装；VCCA=1.5±0.1 V，VCCB=1.8±0.15 V |  |  | 6.5 | ns | S1 p10 |
| B上升/下降 | trB、tfB | 其他封装；VCCA=1.5±0.1 V，VCCB=2.5±0.2 V |  |  | 5.2 | ns | S1 p10 |
| B上升/下降 | trB、tfB | 其他封装；VCCA=1.5±0.1 V，VCCB=3.3±0.3 V |  |  | 4.8 | ns | S1 p10 |
| B上升/下降 | trB、tfB | 其他封装；VCCA=1.5±0.1 V，VCCB=5±0.5 V |  |  | 4.7 | ns | S1 p10 |
| 传播延迟A→B | tpd | BQA；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 14 | ns | S1 p10 |
| 传播延迟A→B | tpd | BQA；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V |  |  | 10.7 | ns | S1 p10 |
| 传播延迟A→B | tpd | BQA；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 9.8 | ns | S1 p10 |
| 传播延迟A→B | tpd | BQA；VCCA=1.8±0.15 V，VCCB=5±0.5 V |  |  | 9.5 | ns | S1 p10 |
| 传播延迟B→A | tpd | BQA；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 15 | ns | S1 p10 |
| 传播延迟B→A | tpd | BQA；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V |  |  | 11.4 | ns | S1 p10 |
| 传播延迟B→A | tpd | BQA；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 10.6 | ns | S1 p10 |
| 传播延迟B→A | tpd | BQA；VCCA=1.8±0.15 V，VCCB=5±0.5 V |  |  | 10.1 | ns | S1 p10 |
| 使能A | ten | BQA；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 1 | µs | S1 p10 |
| 使能A | ten | BQA；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V |  |  | 1 | µs | S1 p10 |
| 使能A | ten | BQA；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 1 | µs | S1 p10 |
| 使能A | ten | BQA；VCCA=1.8±0.15 V，VCCB=5±0.5 V |  |  | 1 | µs | S1 p10 |
| 使能B | ten | BQA；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 1 | µs | S1 p10 |
| 使能B | ten | BQA；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V |  |  | 1 | µs | S1 p10 |
| 使能B | ten | BQA；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 1 | µs | S1 p10 |
| 使能B | ten | BQA；VCCA=1.8±0.15 V，VCCB=5±0.5 V |  |  | 1 | µs | S1 p10 |
| 禁止A | tdis | BQA；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 389 | ns | S1 p10 |
| 禁止A | tdis | BQA；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V |  |  | 253 | ns | S1 p10 |
| 禁止A | tdis | BQA；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 250 | ns | S1 p10 |
| 禁止A | tdis | BQA；VCCA=1.8±0.15 V，VCCB=5±0.5 V |  |  | 250 | ns | S1 p10 |
| 禁止B | tdis | BQA；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 389 | ns | S1 p10 |
| 禁止B | tdis | BQA；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V |  |  | 253 | ns | S1 p10 |
| 禁止B | tdis | BQA；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 248 | ns | S1 p10 |
| 禁止B | tdis | BQA；VCCA=1.8±0.15 V，VCCB=5±0.5 V |  |  | 248 | ns | S1 p10 |
| A上升/下降 | trA、tfA | BQA；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 6.2 | ns | S1 p10 |
| A上升/下降 | trA、tfA | BQA；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V |  |  | 6.1 | ns | S1 p10 |
| A上升/下降 | trA、tfA | BQA；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 6.1 | ns | S1 p10 |
| A上升/下降 | trA、tfA | BQA；VCCA=1.8±0.15 V，VCCB=5±0.5 V |  |  | 6.1 | ns | S1 p10 |
| B上升/下降 | trB、tfB | BQA；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 5.8 | ns | S1 p10 |
| B上升/下降 | trB、tfB | BQA；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V |  |  | 5.2 | ns | S1 p10 |
| B上升/下降 | trB、tfB | BQA；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 4.8 | ns | S1 p10 |
| B上升/下降 | trB、tfB | BQA；VCCA=1.8±0.15 V，VCCB=5±0.5 V |  |  | 4.7 | ns | S1 p10 |
| 传播延迟A→B | tpd | 其他封装；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 14 | ns | S1 p11 |
| 传播延迟A→B | tpd | 其他封装；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V |  |  | 10.7 | ns | S1 p11 |
| 传播延迟A→B | tpd | 其他封装；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 9.8 | ns | S1 p11 |
| 传播延迟A→B | tpd | 其他封装；VCCA=1.8±0.15 V，VCCB=5±0.5 V |  |  | 9.5 | ns | S1 p11 |
| 传播延迟B→A | tpd | 其他封装；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 15 | ns | S1 p11 |
| 传播延迟B→A | tpd | 其他封装；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V |  |  | 11.4 | ns | S1 p11 |
| 传播延迟B→A | tpd | 其他封装；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 10.6 | ns | S1 p11 |
| 传播延迟B→A | tpd | 其他封装；VCCA=1.8±0.15 V，VCCB=5±0.5 V |  |  | 10.1 | ns | S1 p11 |
| 使能A | ten | 其他封装；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 1 | µs | S1 p11 |
| 使能A | ten | 其他封装；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V |  |  | 1 | µs | S1 p11 |
| 使能A | ten | 其他封装；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 1 | µs | S1 p11 |
| 使能A | ten | 其他封装；VCCA=1.8±0.15 V，VCCB=5±0.5 V |  |  | 1 | µs | S1 p11 |
| 使能B | ten | 其他封装；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 1 | µs | S1 p11 |
| 使能B | ten | 其他封装；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V |  |  | 1 | µs | S1 p11 |
| 使能B | ten | 其他封装；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 1 | µs | S1 p11 |
| 使能B | ten | 其他封装；VCCA=1.8±0.15 V，VCCB=5±0.5 V |  |  | 1 | µs | S1 p11 |
| 禁止A | tdis | 其他封装；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 280 | ns | S1 p11 |
| 禁止A | tdis | 其他封装；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V |  |  | 250 | ns | S1 p11 |
| 禁止A | tdis | 其他封装；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 250 | ns | S1 p11 |
| 禁止A | tdis | 其他封装；VCCA=1.8±0.15 V，VCCB=5±0.5 V |  |  | 250 | ns | S1 p11 |
| 禁止B | tdis | 其他封装；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 220 | ns | S1 p11 |
| 禁止B | tdis | 其他封装；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V |  |  | 220 | ns | S1 p11 |
| 禁止B | tdis | 其他封装；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 220 | ns | S1 p11 |
| 禁止B | tdis | 其他封装；VCCA=1.8±0.15 V，VCCB=5±0.5 V |  |  | 220 | ns | S1 p11 |
| A上升/下降 | trA、tfA | 其他封装；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 6.2 | ns | S1 p11 |
| A上升/下降 | trA、tfA | 其他封装；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V |  |  | 6.1 | ns | S1 p11 |
| A上升/下降 | trA、tfA | 其他封装；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 6.1 | ns | S1 p11 |
| A上升/下降 | trA、tfA | 其他封装；VCCA=1.8±0.15 V，VCCB=5±0.5 V |  |  | 6.1 | ns | S1 p11 |
| B上升/下降 | trB、tfB | 其他封装；VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 5.8 | ns | S1 p11 |
| B上升/下降 | trB、tfB | 其他封装；VCCA=1.8±0.15 V，VCCB=2.5±0.2 V |  |  | 5.2 | ns | S1 p11 |
| B上升/下降 | trB、tfB | 其他封装；VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 4.8 | ns | S1 p11 |
| B上升/下降 | trB、tfB | 其他封装；VCCA=1.8±0.15 V，VCCB=5±0.5 V |  |  | 4.7 | ns | S1 p11 |
| 传播延迟A→B | tpd | BQA；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V |  |  | 9.3 | ns | S1 p11 |
| 传播延迟A→B | tpd | BQA；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V |  |  | 8.2 | ns | S1 p11 |
| 传播延迟A→B | tpd | BQA；VCCA=2.5±0.2 V，VCCB=5±0.5 V |  |  | 7.7 | ns | S1 p11 |
| 传播延迟B→A | tpd | BQA；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V |  |  | 9.6 | ns | S1 p11 |
| 传播延迟B→A | tpd | BQA；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V |  |  | 8.1 | ns | S1 p11 |
| 传播延迟B→A | tpd | BQA；VCCA=2.5±0.2 V，VCCB=5±0.5 V |  |  | 7.4 | ns | S1 p11 |
| 使能A | ten | BQA；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V |  |  | 1 | µs | S1 p11 |
| 使能A | ten | BQA；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V |  |  | 1 | µs | S1 p11 |
| 使能A | ten | BQA；VCCA=2.5±0.2 V，VCCB=5±0.5 V |  |  | 1 | µs | S1 p11 |
| 使能B | ten | BQA；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V |  |  | 1 | µs | S1 p11 |
| 使能B | ten | BQA；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V |  |  | 1 | µs | S1 p11 |
| 使能B | ten | BQA；VCCA=2.5±0.2 V，VCCB=5±0.5 V |  |  | 1 | µs | S1 p11 |
| 禁止A | tdis | BQA；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V |  |  | 252 | ns | S1 p11 |
| 禁止A | tdis | BQA；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V |  |  | 220 | ns | S1 p11 |
| 禁止A | tdis | BQA；VCCA=2.5±0.2 V，VCCB=5±0.5 V |  |  | 220 | ns | S1 p11 |
| 禁止B | tdis | BQA；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V |  |  | 252 | ns | S1 p11 |
| 禁止B | tdis | BQA；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V |  |  | 220 | ns | S1 p11 |
| 禁止B | tdis | BQA；VCCA=2.5±0.2 V，VCCB=5±0.5 V |  |  | 220 | ns | S1 p11 |
| A上升/下降 | trA、tfA | BQA；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V |  |  | 5 | ns | S1 p11 |
| A上升/下降 | trA、tfA | BQA；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V |  |  | 5 | ns | S1 p11 |
| A上升/下降 | trA、tfA | BQA；VCCA=2.5±0.2 V，VCCB=5±0.5 V |  |  | 5 | ns | S1 p11 |
| B上升/下降 | trB、tfB | BQA；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V |  |  | 4.6 | ns | S1 p11 |
| B上升/下降 | trB、tfB | BQA；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V |  |  | 4.8 | ns | S1 p11 |
| B上升/下降 | trB、tfB | BQA；VCCA=2.5±0.2 V，VCCB=5±0.5 V |  |  | 4.7 | ns | S1 p11 |
| 传播延迟A→B | tpd | 其他封装；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V |  |  | 9.3 | ns | S1 p11 |
| 传播延迟A→B | tpd | 其他封装；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V |  |  | 8.2 | ns | S1 p11 |
| 传播延迟A→B | tpd | 其他封装；VCCA=2.5±0.2 V，VCCB=5±0.5 V |  |  | 7.7 | ns | S1 p11 |
| 传播延迟B→A | tpd | 其他封装；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V |  |  | 9.6 | ns | S1 p11 |
| 传播延迟B→A | tpd | 其他封装；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V |  |  | 8.1 | ns | S1 p11 |
| 传播延迟B→A | tpd | 其他封装；VCCA=2.5±0.2 V，VCCB=5±0.5 V |  |  | 7.4 | ns | S1 p11 |
| 使能A | ten | 其他封装；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V |  |  | 1 | µs | S1 p11 |
| 使能A | ten | 其他封装；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V |  |  | 1 | µs | S1 p11 |
| 使能A | ten | 其他封装；VCCA=2.5±0.2 V，VCCB=5±0.5 V |  |  | 1 | µs | S1 p11 |
| 使能B | ten | 其他封装；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V |  |  | 1 | µs | S1 p11 |
| 使能B | ten | 其他封装；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V |  |  | 1 | µs | S1 p11 |
| 使能B | ten | 其他封装；VCCA=2.5±0.2 V，VCCB=5±0.5 V |  |  | 1 | µs | S1 p11 |
| 禁止A | tdis | 其他封装；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V |  |  | 220 | ns | S1 p11 |
| 禁止A | tdis | 其他封装；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V |  |  | 220 | ns | S1 p11 |
| 禁止A | tdis | 其他封装；VCCA=2.5±0.2 V，VCCB=5±0.5 V |  |  | 220 | ns | S1 p11 |
| 禁止B | tdis | 其他封装；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V |  |  | 220 | ns | S1 p11 |
| 禁止B | tdis | 其他封装；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V |  |  | 220 | ns | S1 p11 |
| 禁止B | tdis | 其他封装；VCCA=2.5±0.2 V，VCCB=5±0.5 V |  |  | 220 | ns | S1 p11 |
| A上升/下降 | trA、tfA | 其他封装；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V |  |  | 5 | ns | S1 p11 |
| A上升/下降 | trA、tfA | 其他封装；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V |  |  | 5 | ns | S1 p11 |
| A上升/下降 | trA、tfA | 其他封装；VCCA=2.5±0.2 V，VCCB=5±0.5 V |  |  | 5 | ns | S1 p11 |
| B上升/下降 | trB、tfB | 其他封装；VCCA=2.5±0.2 V，VCCB=2.5±0.2 V |  |  | 4.6 | ns | S1 p11 |
| B上升/下降 | trB、tfB | 其他封装；VCCA=2.5±0.2 V，VCCB=3.3±0.3 V |  |  | 4.8 | ns | S1 p11 |
| B上升/下降 | trB、tfB | 其他封装；VCCA=2.5±0.2 V，VCCB=5±0.5 V |  |  | 4.7 | ns | S1 p11 |
| 传播延迟A→B | tpd | 全部封装；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V |  |  | 7.7 | ns | S1 p12 |
| 传播延迟A→B | tpd | 全部封装；VCCA=3.3±0.3 V，VCCB=5±0.5 V |  |  | 7 | ns | S1 p12 |
| 传播延迟B→A | tpd | 全部封装；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V |  |  | 7.9 | ns | S1 p12 |
| 传播延迟B→A | tpd | 全部封装；VCCA=3.3±0.3 V，VCCB=5±0.5 V |  |  | 6.8 | ns | S1 p12 |
| 使能A | ten | 全部封装；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V |  |  | 1 | µs | S1 p12 |
| 使能A | ten | 全部封装；VCCA=3.3±0.3 V，VCCB=5±0.5 V |  |  | 1 | µs | S1 p12 |
| 使能B | ten | 全部封装；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V |  |  | 1 | µs | S1 p12 |
| 使能B | ten | 全部封装；VCCA=3.3±0.3 V，VCCB=5±0.5 V |  |  | 1 | µs | S1 p12 |
| 禁止A | tdis | 全部封装；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V |  |  | 280 | ns | S1 p12 |
| 禁止A | tdis | 全部封装；VCCA=3.3±0.3 V，VCCB=5±0.5 V |  |  | 280 | ns | S1 p12 |
| 禁止B | tdis | 全部封装；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V |  |  | 220 | ns | S1 p12 |
| 禁止B | tdis | 全部封装；VCCA=3.3±0.3 V，VCCB=5±0.5 V |  |  | 220 | ns | S1 p12 |
| A上升/下降 | trA、tfA | 全部封装；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V |  |  | 4.5 | ns | S1 p12 |
| A上升/下降 | trA、tfA | 全部封装；VCCA=3.3±0.3 V，VCCB=5±0.5 V |  |  | 4.5 | ns | S1 p12 |
| B上升/下降 | trB、tfB | 全部封装；VCCA=3.3±0.3 V，VCCB=3.3±0.3 V |  |  | 4.1 | ns | S1 p12 |
| B上升/下降 | trB、tfB | 全部封装；VCCA=3.3±0.3 V，VCCB=5±0.5 V |  |  | 4.7 | ns | S1 p12 |

用这些数时要注意：

- VCCA=1.2 V时的输出高/低电平、供电电流、数据速率20 Mbps、脉宽50 ns及传播/使能/禁止/边沿时间都仅TA=25 °C典型值，不可套用高压档的保证值。VOLA典型值原文为0.9 V，保留原文，不能自行改为0.1 V（S1 p6～p9）。
- 输入驱动至少±2 mA，仅适合推挽CMOS，不适用于开漏总线。任何必需的外部上下拉建议大于50 kΩ（S1 p16、p18）。
- 电气表BQA的Ci/Cio典型值与“Other Packages”里仍列BQA的值不一致，分别保留；Cpd为典型，不是输入负载保证上限（S1 p7、p8、p12）。
- 不用的数据I/O对两端必须同为各自电源或同为GND；VCCA≤VCCB，供电关闭任一侧时端口高阻（S1 p6、p19）。
- 绝对最大值IIK/IOK原表将−50 mA列在MAX，不自行改写符号或保证方向（S1 p5）。

## 热特性

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- |
| 结到环境 | RθJA | PW | 121 | °C/W | S1 p6 |
| 结到环境 | RθJA | RGY | 52.8 | °C/W | S1 p6 |
| 结到环境 | RθJA | RUT | 119.8 | °C/W | S1 p6 |
| 结到环境 | RθJA | BQA | 77.1 | °C/W | S1 p6 |
| 结到壳顶 | RθJC(top) | PW | 50 | °C/W | S1 p6 |
| 结到壳顶 | RθJC(top) | RGY | 67.7 | °C/W | S1 p6 |
| 结到壳顶 | RθJC(top) | RUT | 42.6 | °C/W | S1 p6 |
| 结到壳顶 | RθJC(top) | BQA | 80.7 | °C/W | S1 p6 |
| 结到板 | RθJB | PW | 62.8 | °C/W | S1 p6 |
| 结到板 | RθJB | RGY | 28.9 | °C/W | S1 p6 |
| 结到板 | RθJB | RUT | 52.5 | °C/W | S1 p6 |
| 结到板 | RθJB | BQA | 46.9 | °C/W | S1 p6 |
| 结到顶参数 | ψJT | PW | 6.4 | °C/W | S1 p6 |
| 结到顶参数 | ψJT | RGY | 2.6 | °C/W | S1 p6 |
| 结到顶参数 | ψJT | RUT | 0.7 | °C/W | S1 p6 |
| 结到顶参数 | ψJT | BQA | 6.1 | °C/W | S1 p6 |
| 结到板参数 | ψJB | PW | 62.2 | °C/W | S1 p6 |
| 结到板参数 | ψJB | RGY | 29.0 | °C/W | S1 p6 |
| 结到板参数 | ψJB | RUT | 52.3 | °C/W | S1 p6 |
| 结到板参数 | ψJB | BQA | 46.8 | °C/W | S1 p6 |
| 结到壳底 | RθJC(bot) | RGY | 9.3 | °C/W | S1 p6 |
| 结到壳底 | RθJC(bot) | BQA | 23.3 | °C/W | S1 p6 |

## 静电额定

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- |
| 人体模型 | V(ESD) | A口，AEC Q100-002 | ±2500 | V | S1 p5 |
| 人体模型 | V(ESD) | B口，AEC Q100-002 | ±15000 | V | S1 p5 |
| 带电器件模型 | V(ESD) | A/B口，AEC Q100-011 | ±1000 | V | S1 p5 |

静电警告译文：器件可能被静电损坏，须采取适当防护；不正确操作或安装可能导致性能退化或完全失效（S1 p21）。

## 引脚与处置

PW/RGY/BQA 为14脚，以下按原脚表；RUT为12脚，见表后。

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
| --- | --- | --- | --- | --- |
| 1 VCCA | I；A端电源 | 见推荐条件 |  | S1 p4 |
| 2 A1、3 A2、4 A3、5 A4 | I/O；参考VCCA | 见绝对最大值 | 未用一对的两端同接各自电源或GND | S1 p4、p6 |
| 6、9 NC | —；无内部连接 |  | 悬空 | S1 p4 |
| 7 GND | —；地 |  | 接地 | S1 p4 |
| 8 OE | I；参考VCCA，高有效 | 见推荐条件 | 上下电用下拉保持禁止 | S1 p4、p19 |
| 10 B4、11 B3、12 B2、13 B1 | I/O；参考VCCB | 见绝对最大值 | 与对应A端保持同一逻辑状态 | S1 p4、p6 |
| 14 VCCB | I；B端电源 | 见推荐条件 |  | S1 p4 |
| 散热焊盘 | RGY 中心焊盘只可作辅助地或电气悬空；BQA有裸露焊盘；手册未给BQA内部连接，PW/RUT未列裸露焊盘 |  | RGY不得作主地；封装图要求裸露焊盘焊到PCB以达热/机械性能 | S1 p3、p30、p35 |

RUT 图中脚号：1 VCCA，2 A1，3 A2，4 A3，5 A4，6 GND，7 B4，8 B3，9 B2，10 B1，11 VCCB，12 OE（见 S1 p3 图4-1）。方向与同名信号的脚表一致。

## 必需外围

电源必须就近旁路，正文未规定统一电容量。OE下拉到地，直到两电源完全稳定才使能；最小下拉阻值由控制器拉电流能力决定（S1 p19）。

## 订货型号与封装

PW/RGY/RUT/BQA为封装代码；Q1为汽车版本。各同封装.A/.B行镀层、温区相同，合并列出。

| 订货型号或后缀 | 封装 | 脚数 | 电压或功能档 | 温度范围 | 引脚镀层 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| TXB0104QPWRQ1 / .A / .B | TSSOP (PW) | 14 |  | −40～125 °C | NIPDAU | S1 p23 |
| TXB0104QRGYRQ1 / .A / .B | VQFN (RGY) | 14 |  | −40～125 °C | NIPDAU | S1 p23 |
| TXB0104QRUTRQ1 / .A / .B | UQFN (RUT) | 12 |  | −40～125 °C | NIPDAUAG | S1 p23 |
| TXB0104QWBQARQ1 | WQFN (BQA) | 14 |  | −40～125 °C | NIPDAU | S1 p23 |
| PTXB0104QWBQARQ1 / .A | WQFN (BQA) | 14 |  | −40～125 °C |  | S1 p23 |

## 核对记录

- 2026-11-10：逐页对照原件，工具核对通过，核对 397 个数。
