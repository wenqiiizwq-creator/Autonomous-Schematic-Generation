# TI SN74LVC1T45

类别：器件参数。
器件：单通道双电源方向控制电平转换收发器。
手册：SCES515N，2024-06。

## 来源

- S1：Datasheet/18_逻辑与电平转换/电平转换器_电压翻译器/TI - SN74LVC1T45.pdf

页码均为 PDF 文件页序。

## 绝对最大值

| 参数 | 符号 | 条件 | 最小 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| 电源/输入/高阻或掉电输出电压 | VCCA、VCCB、VI、VO |  | −0.5 | 6.5 | V | S1 p4 |
| 活动输出电压 | VO | A/B分别以自身电源为准 | −0.5 | VCCA + 0.5 / VCCB + 0.5 | V | S1 p4 |
| 输入/输出钳位电流 | IIK、IOK | VI或VO<0 |  | −50 | mA | S1 p4 |
| 连续输出电流 | IO |  |  | ±50 | mA | S1 p4 |
| 电源或地电流 |  |  |  | ±100 | mA | S1 p4 |
| 结温 | TJ |  |  | 150 | °C | S1 p4 |
| 储存温度 | Tstg |  | −65 | 150 | °C | S1 p4 |

## 推荐工作条件

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 电源 | VCCA、VCCB |  | 1.65 |  | 5.5 | V | S1 p4 |
| 输入电压 | VI |  | 0 |  | 5.5 | V | S1 p5 |
| 输出电压 | VO |  | 0 |  | VCCO | V | S1 p5 |
| 环境温度 | TA |  | −40 |  | 85 | °C | S1 p5 |
| 输入高电平 | VIH | 数据，VCCI=1.65～1.95 V；DIR同档以VCCA为参考 | 0.65 VCCI |  |  | V | S1 p4 |
| 输入低电平 | VIL | 数据，VCCI=1.65～1.95 V；DIR同档以VCCA为参考 |  |  | 0.35 VCCI | V | S1 p4、p5 |
| 高电平输出电流 | IOH | VCCO=1.65～1.95 V |  |  | −4 | mA | S1 p5 |
| 低电平输出电流 | IOL | VCCO=1.65～1.95 V |  |  | 4 | mA | S1 p5 |
| 数据输入边沿 | Δt/Δv | VCCI=1.65～1.95 V |  |  | 20 | ns/V | S1 p5 |
| 输入高电平 | VIH | 数据，VCCI=2.3～2.7 V；DIR同档以VCCA为参考 | 1.7 |  |  | V | S1 p4 |
| 输入低电平 | VIL | 数据，VCCI=2.3～2.7 V；DIR同档以VCCA为参考 |  |  | 0.7 | V | S1 p4、p5 |
| 高电平输出电流 | IOH | VCCO=2.3～2.7 V |  |  | −8 | mA | S1 p5 |
| 低电平输出电流 | IOL | VCCO=2.3～2.7 V |  |  | 8 | mA | S1 p5 |
| 数据输入边沿 | Δt/Δv | VCCI=2.3～2.7 V |  |  | 20 | ns/V | S1 p5 |
| 输入高电平 | VIH | 数据，VCCI=3～3.6 V；DIR同档以VCCA为参考 | 2 |  |  | V | S1 p4 |
| 输入低电平 | VIL | 数据，VCCI=3～3.6 V；DIR同档以VCCA为参考 |  |  | 0.8 | V | S1 p4、p5 |
| 高电平输出电流 | IOH | VCCO=3～3.6 V |  |  | −24 | mA | S1 p5 |
| 低电平输出电流 | IOL | VCCO=3～3.6 V |  |  | 24 | mA | S1 p5 |
| 数据输入边沿 | Δt/Δv | VCCI=3～3.6 V |  |  | 10 | ns/V | S1 p5 |
| 输入高电平 | VIH | 数据，VCCI=4.5～5.5 V；DIR同档以VCCA为参考 | 0.7 VCCI |  |  | V | S1 p4 |
| 输入低电平 | VIL | 数据，VCCI=4.5～5.5 V；DIR同档以VCCA为参考 |  |  | 0.3 VCCI | V | S1 p4、p5 |
| 高电平输出电流 | IOH | VCCO=4.5～5.5 V |  |  | −32 | mA | S1 p5 |
| 低电平输出电流 | IOL | VCCO=4.5～5.5 V |  |  | 32 | mA | S1 p5 |
| 数据输入边沿 | Δt/Δv | VCCI=4.5～5.5 V |  |  | 5 | ns/V | S1 p5 |
| 控制输入边沿 | Δt/Δv | 全供电范围 |  |  | 5 | ns/V | S1 p5 |

## 电气特性

测试条件按各行；最小、最大为手册限值，典型值不是保证值。

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 输出高电平 | VOH | IOH=−100 µA，两电源1.65～4.5 V | VCCO − 0.1 |  |  | V | S1 p6 |
| 输出低电平 | VOL | IOL=100 µA，两电源1.65～4.5 V |  |  | 0.1 | V | S1 p6 |
| 输出高电平 | VOH | 两电源1.65 V，IOH=−4 mA，VI=VIH | 1.2 |  |  | V | S1 p6 |
| 输出低电平 | VOL | 两电源1.65 V，IOL=4 mA，VI=VIL |  |  | 0.45 | V | S1 p6 |
| 输出高电平 | VOH | 两电源2.3 V，IOH=−8 mA，VI=VIH | 1.9 |  |  | V | S1 p6 |
| 输出低电平 | VOL | 两电源2.3 V，IOL=8 mA，VI=VIL |  |  | 0.3 | V | S1 p6 |
| 输出高电平 | VOH | 两电源3 V，IOH=−24 mA，VI=VIH | 2.4 |  |  | V | S1 p6 |
| 输出低电平 | VOL | 两电源3 V，IOL=24 mA，VI=VIL |  |  | 0.55 | V | S1 p6 |
| 输出高电平 | VOH | 两电源4.5 V，IOH=−32 mA，VI=VIH | 3.8 |  |  | V | S1 p6 |
| 输出低电平 | VOL | 两电源4.5 V，IOL=32 mA，VI=VIL |  |  | 0.55 | V | S1 p6 |
| 控制输入电流 | II | DIR，VI=VCCA或GND，两电源1.65～5.5 V，TA=25 °C |  |  | ±1 | µA | S1 p6 |
| 控制输入电流 | II | DIR，VI=VCCA或GND，两电源1.65～5.5 V，TA=−40～85 °C |  |  | ±2 | µA | S1 p6 |
| 掉电漏电 | Ioff | VI或VO=0～5.5 V；被测端电源0，另一侧0～5.5 V，TA=25 °C |  |  | ±1 | µA | S1 p6 |
| 掉电漏电 | Ioff | VI或VO=0～5.5 V；被测端电源0，另一侧0～5.5 V，TA=−40～85 °C |  |  | ±2 | µA | S1 p6 |
| 高阻漏电 | IOZ | VO=VCCO或GND，两电源1.65～5.5 V，TA=25 °C |  |  | ±1 | µA | S1 p6 |
| 高阻漏电 | IOZ | VO=VCCO或GND，两电源1.65～5.5 V，TA=−40～85 °C |  |  | ±2 | µA | S1 p6 |
| 电源电流 | ICCA、ICCB | 两电源1.65～5.5 V，VI=VCCI或地，IO=0 |  |  | 3 | µA | S1 p6 |
| 电源电流 | ICCA | VCCA=5.5 V，VCCB=0 |  |  | 2 | µA | S1 p6 |
| 电源电流 | ICCA | VCCA=0，VCCB=5.5 V |  |  | −2 | µA | S1 p6 |
| 电源电流 | ICCB | VCCA=5.5 V，VCCB=0 |  |  | −2 | µA | S1 p6 |
| 电源电流 | ICCB | VCCA=0，VCCB=5.5 V |  |  | 2 | µA | S1 p6 |
| 总静态电流 | ICCA+ICCB | 两电源1.65～5.5 V，VI=VCCI或地，IO=0 |  |  | 4 | µA | S1 p6 |
| 增量电流 | ΔICCA | 两电源3～5.5 V；A=VCCA−0.6 V、DIR=VCCA、B开路 |  |  | 50 | µA | S1 p6 |
| 增量电流 | ΔICCA | 两电源3～5.5 V；DIR=VCCA−0.6 V、A为VCCA或地、B开路 |  |  | 50 | µA | S1 p6 |
| 增量电流 | ΔICCB | 两电源3～5.5 V；B=VCCB−0.6 V、DIR=地、A开路 |  |  | 50 | µA | S1 p6 |
| 控制输入电容 | Ci | DIR，两电源3.3 V，25 °C，VI=VCCA或地 |  | 2.5 |  | pF | S1 p6 |
| 数据I/O电容 | Cio | A或B，两电源3.3 V，25 °C，VO=各自电源或地 |  | 6 |  | pF | S1 p6 |
| 传播/使能延时 | tPLH | VCCA=1.8V ± 0.15V，VCCB=1.8±0.15 V，A→B，测量负载按图6-1 | 3 |  | 17.7 | ns | S1 p7 |
| 传播/使能延时 | tPLH | VCCA=1.8V ± 0.15V，VCCB=2.5±0.2 V，A→B，测量负载按图6-1 | 2.2 |  | 10.3 | ns | S1 p7 |
| 传播/使能延时 | tPLH | VCCA=1.8V ± 0.15V，VCCB=3.3±0.3 V，A→B，测量负载按图6-1 | 1.7 |  | 8.3 | ns | S1 p7 |
| 传播/使能延时 | tPLH | VCCA=1.8V ± 0.15V，VCCB=5±0.5 V，A→B，测量负载按图6-1 | 1.4 |  | 7.2 | ns | S1 p7 |
| 传播/使能延时 | tPHL | VCCA=1.8V ± 0.15V，VCCB=1.8±0.15 V，A→B，测量负载按图6-1 | 2.8 |  | 14.3 | ns | S1 p7 |
| 传播/使能延时 | tPHL | VCCA=1.8V ± 0.15V，VCCB=2.5±0.2 V，A→B，测量负载按图6-1 | 2.2 |  | 8.5 | ns | S1 p7 |
| 传播/使能延时 | tPHL | VCCA=1.8V ± 0.15V，VCCB=3.3±0.3 V，A→B，测量负载按图6-1 | 1.8 |  | 7.1 | ns | S1 p7 |
| 传播/使能延时 | tPHL | VCCA=1.8V ± 0.15V，VCCB=5±0.5 V，A→B，测量负载按图6-1 | 1.7 |  | 7 | ns | S1 p7 |
| 传播/使能延时 | tPLH | VCCA=1.8V ± 0.15V，VCCB=1.8±0.15 V，B→A，测量负载按图6-1 | 3 |  | 17.7 | ns | S1 p7 |
| 传播/使能延时 | tPLH | VCCA=1.8V ± 0.15V，VCCB=2.5±0.2 V，B→A，测量负载按图6-1 | 2.3 |  | 16 | ns | S1 p7 |
| 传播/使能延时 | tPLH | VCCA=1.8V ± 0.15V，VCCB=3.3±0.3 V，B→A，测量负载按图6-1 | 2.1 |  | 15.5 | ns | S1 p7 |
| 传播/使能延时 | tPLH | VCCA=1.8V ± 0.15V，VCCB=5±0.5 V，B→A，测量负载按图6-1 | 1.9 |  | 15.1 | ns | S1 p7 |
| 传播/使能延时 | tPHL | VCCA=1.8V ± 0.15V，VCCB=1.8±0.15 V，B→A，测量负载按图6-1 | 2.8 |  | 14.3 | ns | S1 p7 |
| 传播/使能延时 | tPHL | VCCA=1.8V ± 0.15V，VCCB=2.5±0.2 V，B→A，测量负载按图6-1 | 2.1 |  | 12.9 | ns | S1 p7 |
| 传播/使能延时 | tPHL | VCCA=1.8V ± 0.15V，VCCB=3.3±0.3 V，B→A，测量负载按图6-1 | 2 |  | 12.6 | ns | S1 p7 |
| 传播/使能延时 | tPHL | VCCA=1.8V ± 0.15V，VCCB=5±0.5 V，B→A，测量负载按图6-1 | 1.8 |  | 12.2 | ns | S1 p7 |
| 传播/使能延时 | tPHZ | VCCA=1.8V ± 0.15V，VCCB=1.8±0.15 V，DIR→A，测量负载按图6-1 | 5.2 |  | 19.4 | ns | S1 p7 |
| 传播/使能延时 | tPHZ | VCCA=1.8V ± 0.15V，VCCB=2.5±0.2 V，DIR→A，测量负载按图6-1 | 4.8 |  | 18.5 | ns | S1 p7 |
| 传播/使能延时 | tPHZ | VCCA=1.8V ± 0.15V，VCCB=3.3±0.3 V，DIR→A，测量负载按图6-1 | 4.7 |  | 18.4 | ns | S1 p7 |
| 传播/使能延时 | tPHZ | VCCA=1.8V ± 0.15V，VCCB=5±0.5 V，DIR→A，测量负载按图6-1 | 5.1 |  | 17.1 | ns | S1 p7 |
| 传播/使能延时 | tPLZ | VCCA=1.8V ± 0.15V，VCCB=1.8±0.15 V，DIR→A，测量负载按图6-1 | 2.3 |  | 10.5 | ns | S1 p7 |
| 传播/使能延时 | tPLZ | VCCA=1.8V ± 0.15V，VCCB=2.5±0.2 V，DIR→A，测量负载按图6-1 | 2.1 |  | 10.5 | ns | S1 p7 |
| 传播/使能延时 | tPLZ | VCCA=1.8V ± 0.15V，VCCB=3.3±0.3 V，DIR→A，测量负载按图6-1 | 2.4 |  | 10.7 | ns | S1 p7 |
| 传播/使能延时 | tPLZ | VCCA=1.8V ± 0.15V，VCCB=5±0.5 V，DIR→A，测量负载按图6-1 | 3.1 |  | 10.9 | ns | S1 p7 |
| 传播/使能延时 | tPHZ | VCCA=1.8V ± 0.15V，VCCB=1.8±0.15 V，DIR→B，测量负载按图6-1 | 5.2 |  | 21.9 | ns | S1 p7 |
| 传播/使能延时 | tPHZ | VCCA=1.8V ± 0.15V，VCCB=2.5±0.2 V，DIR→B，测量负载按图6-1 | 4.9 |  | 11.5 | ns | S1 p7 |
| 传播/使能延时 | tPHZ | VCCA=1.8V ± 0.15V，VCCB=3.3±0.3 V，DIR→B，测量负载按图6-1 | 4.6 |  | 10.3 | ns | S1 p7 |
| 传播/使能延时 | tPHZ | VCCA=1.8V ± 0.15V，VCCB=5±0.5 V，DIR→B，测量负载按图6-1 | 2.8 |  | 8.2 | ns | S1 p7 |
| 传播/使能延时 | tPLZ | VCCA=1.8V ± 0.15V，VCCB=1.8±0.15 V，DIR→B，测量负载按图6-1 | 4.2 |  | 16 | ns | S1 p7 |
| 传播/使能延时 | tPLZ | VCCA=1.8V ± 0.15V，VCCB=2.5±0.2 V，DIR→B，测量负载按图6-1 | 3.7 |  | 9.2 | ns | S1 p7 |
| 传播/使能延时 | tPLZ | VCCA=1.8V ± 0.15V，VCCB=3.3±0.3 V，DIR→B，测量负载按图6-1 | 3.3 |  | 8.4 | ns | S1 p7 |
| 传播/使能延时 | tPLZ | VCCA=1.8V ± 0.15V，VCCB=5±0.5 V，DIR→B，测量负载按图6-1 | 2.4 |  | 6.4 | ns | S1 p7 |
| 传播/使能延时 | tPZH | VCCA=1.8V ± 0.15V，VCCB=1.8±0.15 V，DIR→A，测量负载按图6-1 |  |  | 33.7 | ns | S1 p7 |
| 传播/使能延时 | tPZH | VCCA=1.8V ± 0.15V，VCCB=2.5±0.2 V，DIR→A，测量负载按图6-1 |  |  | 25.2 | ns | S1 p7 |
| 传播/使能延时 | tPZH | VCCA=1.8V ± 0.15V，VCCB=3.3±0.3 V，DIR→A，测量负载按图6-1 |  |  | 23.9 | ns | S1 p7 |
| 传播/使能延时 | tPZH | VCCA=1.8V ± 0.15V，VCCB=5±0.5 V，DIR→A，测量负载按图6-1 |  |  | 21.5 | ns | S1 p7 |
| 传播/使能延时 | tPZL | VCCA=1.8V ± 0.15V，VCCB=1.8±0.15 V，DIR→A，测量负载按图6-1 |  |  | 36.2 | ns | S1 p7 |
| 传播/使能延时 | tPZL | VCCA=1.8V ± 0.15V，VCCB=2.5±0.2 V，DIR→A，测量负载按图6-1 |  |  | 24.4 | ns | S1 p7 |
| 传播/使能延时 | tPZL | VCCA=1.8V ± 0.15V，VCCB=3.3±0.3 V，DIR→A，测量负载按图6-1 |  |  | 22.9 | ns | S1 p7 |
| 传播/使能延时 | tPZL | VCCA=1.8V ± 0.15V，VCCB=5±0.5 V，DIR→A，测量负载按图6-1 |  |  | 20.4 | ns | S1 p7 |
| 传播/使能延时 | tPZH | VCCA=1.8V ± 0.15V，VCCB=1.8±0.15 V，DIR→B，测量负载按图6-1 |  |  | 28.2 | ns | S1 p7 |
| 传播/使能延时 | tPZH | VCCA=1.8V ± 0.15V，VCCB=2.5±0.2 V，DIR→B，测量负载按图6-1 |  |  | 20.8 | ns | S1 p7 |
| 传播/使能延时 | tPZH | VCCA=1.8V ± 0.15V，VCCB=3.3±0.3 V，DIR→B，测量负载按图6-1 |  |  | 19 | ns | S1 p7 |
| 传播/使能延时 | tPZH | VCCA=1.8V ± 0.15V，VCCB=5±0.5 V，DIR→B，测量负载按图6-1 |  |  | 18.1 | ns | S1 p7 |
| 传播/使能延时 | tPZL | VCCA=1.8V ± 0.15V，VCCB=1.8±0.15 V，DIR→B，测量负载按图6-1 |  |  | 33.7 | ns | S1 p7 |
| 传播/使能延时 | tPZL | VCCA=1.8V ± 0.15V，VCCB=2.5±0.2 V，DIR→B，测量负载按图6-1 |  |  | 27 | ns | S1 p7 |
| 传播/使能延时 | tPZL | VCCA=1.8V ± 0.15V，VCCB=3.3±0.3 V，DIR→B，测量负载按图6-1 |  |  | 25.5 | ns | S1 p7 |
| 传播/使能延时 | tPZL | VCCA=1.8V ± 0.15V，VCCB=5±0.5 V，DIR→B，测量负载按图6-1 |  |  | 24.1 | ns | S1 p7 |
| 传播/使能延时 | tPLH | VCCA=2.5V ± 0.2V，VCCB=1.8±0.15 V，A→B，测量负载按图6-1 | 2.3 |  | 16 | ns | S1 p7 |
| 传播/使能延时 | tPLH | VCCA=2.5V ± 0.2V，VCCB=2.5±0.2 V，A→B，测量负载按图6-1 | 1.5 |  | 8.5 | ns | S1 p7 |
| 传播/使能延时 | tPLH | VCCA=2.5V ± 0.2V，VCCB=3.3±0.3 V，A→B，测量负载按图6-1 | 1.3 |  | 6.4 | ns | S1 p7 |
| 传播/使能延时 | tPLH | VCCA=2.5V ± 0.2V，VCCB=5±0.5 V，A→B，测量负载按图6-1 | 1.1 |  | 5.1 | ns | S1 p7 |
| 传播/使能延时 | tPHL | VCCA=2.5V ± 0.2V，VCCB=1.8±0.15 V，A→B，测量负载按图6-1 | 2.1 |  | 12.9 | ns | S1 p7 |
| 传播/使能延时 | tPHL | VCCA=2.5V ± 0.2V，VCCB=2.5±0.2 V，A→B，测量负载按图6-1 | 1.4 |  | 7.5 | ns | S1 p7 |
| 传播/使能延时 | tPHL | VCCA=2.5V ± 0.2V，VCCB=3.3±0.3 V，A→B，测量负载按图6-1 | 1.3 |  | 5.4 | ns | S1 p7 |
| 传播/使能延时 | tPHL | VCCA=2.5V ± 0.2V，VCCB=5±0.5 V，A→B，测量负载按图6-1 | 0.9 |  | 4.6 | ns | S1 p7 |
| 传播/使能延时 | tPLH | VCCA=2.5V ± 0.2V，VCCB=1.8±0.15 V，B→A，测量负载按图6-1 | 2.2 |  | 10.3 | ns | S1 p7 |
| 传播/使能延时 | tPLH | VCCA=2.5V ± 0.2V，VCCB=2.5±0.2 V，B→A，测量负载按图6-1 | 1.5 |  | 8.5 | ns | S1 p7 |
| 传播/使能延时 | tPLH | VCCA=2.5V ± 0.2V，VCCB=3.3±0.3 V，B→A，测量负载按图6-1 | 1.4 |  | 8 | ns | S1 p7 |
| 传播/使能延时 | tPLH | VCCA=2.5V ± 0.2V，VCCB=5±0.5 V，B→A，测量负载按图6-1 | 1 |  | 7.5 | ns | S1 p7 |
| 传播/使能延时 | tPHL | VCCA=2.5V ± 0.2V，VCCB=1.8±0.15 V，B→A，测量负载按图6-1 | 2.2 |  | 8.5 | ns | S1 p7 |
| 传播/使能延时 | tPHL | VCCA=2.5V ± 0.2V，VCCB=2.5±0.2 V，B→A，测量负载按图6-1 | 1.4 |  | 7.5 | ns | S1 p7 |
| 传播/使能延时 | tPHL | VCCA=2.5V ± 0.2V，VCCB=3.3±0.3 V，B→A，测量负载按图6-1 | 1.3 |  | 7 | ns | S1 p7 |
| 传播/使能延时 | tPHL | VCCA=2.5V ± 0.2V，VCCB=5±0.5 V，B→A，测量负载按图6-1 | 0.9 |  | 6.2 | ns | S1 p7 |
| 传播/使能延时 | tPHZ | VCCA=2.5V ± 0.2V，VCCB=1.8±0.15 V，DIR→A，测量负载按图6-1 | 3 |  | 8.1 | ns | S1 p7 |
| 传播/使能延时 | tPHZ | VCCA=2.5V ± 0.2V，VCCB=2.5±0.2 V，DIR→A，测量负载按图6-1 | 3.1 |  | 8.1 | ns | S1 p7 |
| 传播/使能延时 | tPHZ | VCCA=2.5V ± 0.2V，VCCB=3.3±0.3 V，DIR→A，测量负载按图6-1 | 2.8 |  | 8.1 | ns | S1 p7 |
| 传播/使能延时 | tPHZ | VCCA=2.5V ± 0.2V，VCCB=5±0.5 V，DIR→A，测量负载按图6-1 | 3.2 |  | 8.1 | ns | S1 p7 |
| 传播/使能延时 | tPLZ | VCCA=2.5V ± 0.2V，VCCB=1.8±0.15 V，DIR→A，测量负载按图6-1 | 1.3 |  | 5.9 | ns | S1 p7 |
| 传播/使能延时 | tPLZ | VCCA=2.5V ± 0.2V，VCCB=2.5±0.2 V，DIR→A，测量负载按图6-1 | 1.3 |  | 5.9 | ns | S1 p7 |
| 传播/使能延时 | tPLZ | VCCA=2.5V ± 0.2V，VCCB=3.3±0.3 V，DIR→A，测量负载按图6-1 | 1.3 |  | 5.9 | ns | S1 p7 |
| 传播/使能延时 | tPLZ | VCCA=2.5V ± 0.2V，VCCB=5±0.5 V，DIR→A，测量负载按图6-1 | 1 |  | 5.8 | ns | S1 p7 |
| 传播/使能延时 | tPHZ | VCCA=2.5V ± 0.2V，VCCB=1.8±0.15 V，DIR→B，测量负载按图6-1 | 5.2 |  | 23.7 | ns | S1 p7 |
| 传播/使能延时 | tPHZ | VCCA=2.5V ± 0.2V，VCCB=2.5±0.2 V，DIR→B，测量负载按图6-1 | 4.1 |  | 11.4 | ns | S1 p7 |
| 传播/使能延时 | tPHZ | VCCA=2.5V ± 0.2V，VCCB=3.3±0.3 V，DIR→B，测量负载按图6-1 | 3.9 |  | 10.2 | ns | S1 p7 |
| 传播/使能延时 | tPHZ | VCCA=2.5V ± 0.2V，VCCB=5±0.5 V，DIR→B，测量负载按图6-1 | 2.4 |  | 7.1 | ns | S1 p7 |
| 传播/使能延时 | tPLZ | VCCA=2.5V ± 0.2V，VCCB=1.8±0.15 V，DIR→B，测量负载按图6-1 | 3.9 |  | 18.9 | ns | S1 p7 |
| 传播/使能延时 | tPLZ | VCCA=2.5V ± 0.2V，VCCB=2.5±0.2 V，DIR→B，测量负载按图6-1 | 3.2 |  | 9.6 | ns | S1 p7 |
| 传播/使能延时 | tPLZ | VCCA=2.5V ± 0.2V，VCCB=3.3±0.3 V，DIR→B，测量负载按图6-1 | 2.8 |  | 8.4 | ns | S1 p7 |
| 传播/使能延时 | tPLZ | VCCA=2.5V ± 0.2V，VCCB=5±0.5 V，DIR→B，测量负载按图6-1 | 1.8 |  | 5.3 | ns | S1 p7 |
| 传播/使能延时 | tPZH | VCCA=2.5V ± 0.2V，VCCB=1.8±0.15 V，DIR→A，测量负载按图6-1 |  |  | 29.2 | ns | S1 p7 |
| 传播/使能延时 | tPZH | VCCA=2.5V ± 0.2V，VCCB=2.5±0.2 V，DIR→A，测量负载按图6-1 |  |  | 18.1 | ns | S1 p7 |
| 传播/使能延时 | tPZH | VCCA=2.5V ± 0.2V，VCCB=3.3±0.3 V，DIR→A，测量负载按图6-1 |  |  | 16.4 | ns | S1 p7 |
| 传播/使能延时 | tPZH | VCCA=2.5V ± 0.2V，VCCB=5±0.5 V，DIR→A，测量负载按图6-1 |  |  | 12.8 | ns | S1 p7 |
| 传播/使能延时 | tPZL | VCCA=2.5V ± 0.2V，VCCB=1.8±0.15 V，DIR→A，测量负载按图6-1 |  |  | 32.2 | ns | S1 p7 |
| 传播/使能延时 | tPZL | VCCA=2.5V ± 0.2V，VCCB=2.5±0.2 V，DIR→A，测量负载按图6-1 |  |  | 18.9 | ns | S1 p7 |
| 传播/使能延时 | tPZL | VCCA=2.5V ± 0.2V，VCCB=3.3±0.3 V，DIR→A，测量负载按图6-1 |  |  | 17.2 | ns | S1 p7 |
| 传播/使能延时 | tPZL | VCCA=2.5V ± 0.2V，VCCB=5±0.5 V，DIR→A，测量负载按图6-1 |  |  | 13.3 | ns | S1 p7 |
| 传播/使能延时 | tPZH | VCCA=2.5V ± 0.2V，VCCB=1.8±0.15 V，DIR→B，测量负载按图6-1 |  |  | 21.9 | ns | S1 p7 |
| 传播/使能延时 | tPZH | VCCA=2.5V ± 0.2V，VCCB=2.5±0.2 V，DIR→B，测量负载按图6-1 |  |  | 14.4 | ns | S1 p7 |
| 传播/使能延时 | tPZH | VCCA=2.5V ± 0.2V，VCCB=3.3±0.3 V，DIR→B，测量负载按图6-1 |  |  | 12.3 | ns | S1 p7 |
| 传播/使能延时 | tPZH | VCCA=2.5V ± 0.2V，VCCB=5±0.5 V，DIR→B，测量负载按图6-1 |  |  | 10.9 | ns | S1 p7 |
| 传播/使能延时 | tPZL | VCCA=2.5V ± 0.2V，VCCB=1.8±0.15 V，DIR→B，测量负载按图6-1 |  |  | 21 | ns | S1 p7 |
| 传播/使能延时 | tPZL | VCCA=2.5V ± 0.2V，VCCB=2.5±0.2 V，DIR→B，测量负载按图6-1 |  |  | 15.6 | ns | S1 p7 |
| 传播/使能延时 | tPZL | VCCA=2.5V ± 0.2V，VCCB=3.3±0.3 V，DIR→B，测量负载按图6-1 |  |  | 13.5 | ns | S1 p7 |
| 传播/使能延时 | tPZL | VCCA=2.5V ± 0.2V，VCCB=5±0.5 V，DIR→B，测量负载按图6-1 |  |  | 12.7 | ns | S1 p7 |
| 传播/使能延时 | tPLH | VCCA=3.3V ± 0.3V，VCCB=1.8±0.15 V，A→B，测量负载按图6-1 | 2.1 |  | 15.5 | ns | S1 p8 |
| 传播/使能延时 | tPLH | VCCA=3.3V ± 0.3V，VCCB=2.5±0.2 V，A→B，测量负载按图6-1 | 1.4 |  | 8 | ns | S1 p8 |
| 传播/使能延时 | tPLH | VCCA=3.3V ± 0.3V，VCCB=3.3±0.3 V，A→B，测量负载按图6-1 | 0.7 |  | 5.8 | ns | S1 p8 |
| 传播/使能延时 | tPLH | VCCA=3.3V ± 0.3V，VCCB=5±0.5 V，A→B，测量负载按图6-1 | 0.7 |  | 4.4 | ns | S1 p8 |
| 传播/使能延时 | tPHL | VCCA=3.3V ± 0.3V，VCCB=1.8±0.15 V，A→B，测量负载按图6-1 | 2 |  | 12.6 | ns | S1 p8 |
| 传播/使能延时 | tPHL | VCCA=3.3V ± 0.3V，VCCB=2.5±0.2 V，A→B，测量负载按图6-1 | 1.3 |  | 7 | ns | S1 p8 |
| 传播/使能延时 | tPHL | VCCA=3.3V ± 0.3V，VCCB=3.3±0.3 V，A→B，测量负载按图6-1 | 0.8 |  | 5 | ns | S1 p8 |
| 传播/使能延时 | tPHL | VCCA=3.3V ± 0.3V，VCCB=5±0.5 V，A→B，测量负载按图6-1 | 0.7 |  | 4 | ns | S1 p8 |
| 传播/使能延时 | tPLH | VCCA=3.3V ± 0.3V，VCCB=1.8±0.15 V，B→A，测量负载按图6-1 | 1.7 |  | 8.3 | ns | S1 p8 |
| 传播/使能延时 | tPLH | VCCA=3.3V ± 0.3V，VCCB=2.5±0.2 V，B→A，测量负载按图6-1 | 1.3 |  | 6.4 | ns | S1 p8 |
| 传播/使能延时 | tPLH | VCCA=3.3V ± 0.3V，VCCB=3.3±0.3 V，B→A，测量负载按图6-1 | 0.7 |  | 5.8 | ns | S1 p8 |
| 传播/使能延时 | tPLH | VCCA=3.3V ± 0.3V，VCCB=5±0.5 V，B→A，测量负载按图6-1 | 0.6 |  | 5.4 | ns | S1 p8 |
| 传播/使能延时 | tPHL | VCCA=3.3V ± 0.3V，VCCB=1.8±0.15 V，B→A，测量负载按图6-1 | 1.8 |  | 7.1 | ns | S1 p8 |
| 传播/使能延时 | tPHL | VCCA=3.3V ± 0.3V，VCCB=2.5±0.2 V，B→A，测量负载按图6-1 | 1.3 |  | 5.4 | ns | S1 p8 |
| 传播/使能延时 | tPHL | VCCA=3.3V ± 0.3V，VCCB=3.3±0.3 V，B→A，测量负载按图6-1 | 0.8 |  | 5 | ns | S1 p8 |
| 传播/使能延时 | tPHL | VCCA=3.3V ± 0.3V，VCCB=5±0.5 V，B→A，测量负载按图6-1 | 0.7 |  | 4.5 | ns | S1 p8 |
| 传播/使能延时 | tPHZ | VCCA=3.3V ± 0.3V，VCCB=1.8±0.15 V，DIR→A，测量负载按图6-1 | 2.9 |  | 7.3 | ns | S1 p8 |
| 传播/使能延时 | tPHZ | VCCA=3.3V ± 0.3V，VCCB=2.5±0.2 V，DIR→A，测量负载按图6-1 | 3 |  | 7.3 | ns | S1 p8 |
| 传播/使能延时 | tPHZ | VCCA=3.3V ± 0.3V，VCCB=3.3±0.3 V，DIR→A，测量负载按图6-1 | 2.8 |  | 7.3 | ns | S1 p8 |
| 传播/使能延时 | tPHZ | VCCA=3.3V ± 0.3V，VCCB=5±0.5 V，DIR→A，测量负载按图6-1 | 3.4 |  | 7.3 | ns | S1 p8 |
| 传播/使能延时 | tPLZ | VCCA=3.3V ± 0.3V，VCCB=1.8±0.15 V，DIR→A，测量负载按图6-1 | 1.8 |  | 5.6 | ns | S1 p8 |
| 传播/使能延时 | tPLZ | VCCA=3.3V ± 0.3V，VCCB=2.5±0.2 V，DIR→A，测量负载按图6-1 | 1.6 |  | 5.6 | ns | S1 p8 |
| 传播/使能延时 | tPLZ | VCCA=3.3V ± 0.3V，VCCB=3.3±0.3 V，DIR→A，测量负载按图6-1 | 2.2 |  | 5.7 | ns | S1 p8 |
| 传播/使能延时 | tPLZ | VCCA=3.3V ± 0.3V，VCCB=5±0.5 V，DIR→A，测量负载按图6-1 | 2.2 |  | 5.7 | ns | S1 p8 |
| 传播/使能延时 | tPHZ | VCCA=3.3V ± 0.3V，VCCB=1.8±0.15 V，DIR→B，测量负载按图6-1 | 5.4 |  | 20.5 | ns | S1 p8 |
| 传播/使能延时 | tPHZ | VCCA=3.3V ± 0.3V，VCCB=2.5±0.2 V，DIR→B，测量负载按图6-1 | 3.9 |  | 10.1 | ns | S1 p8 |
| 传播/使能延时 | tPHZ | VCCA=3.3V ± 0.3V，VCCB=3.3±0.3 V，DIR→B，测量负载按图6-1 | 2.9 |  | 8.8 | ns | S1 p8 |
| 传播/使能延时 | tPHZ | VCCA=3.3V ± 0.3V，VCCB=5±0.5 V，DIR→B，测量负载按图6-1 | 2.4 |  | 6.8 | ns | S1 p8 |
| 传播/使能延时 | tPLZ | VCCA=3.3V ± 0.3V，VCCB=1.8±0.15 V，DIR→B，测量负载按图6-1 | 3.3 |  | 14.5 | ns | S1 p8 |
| 传播/使能延时 | tPLZ | VCCA=3.3V ± 0.3V，VCCB=2.5±0.2 V，DIR→B，测量负载按图6-1 | 2.9 |  | 7.8 | ns | S1 p8 |
| 传播/使能延时 | tPLZ | VCCA=3.3V ± 0.3V，VCCB=3.3±0.3 V，DIR→B，测量负载按图6-1 | 2.4 |  | 7.1 | ns | S1 p8 |
| 传播/使能延时 | tPLZ | VCCA=3.3V ± 0.3V，VCCB=5±0.5 V，DIR→B，测量负载按图6-1 | 1.7 |  | 4.9 | ns | S1 p8 |
| 传播/使能延时 | tPZH | VCCA=3.3V ± 0.3V，VCCB=1.8±0.15 V，DIR→A，测量负载按图6-1 |  |  | 22.8 | ns | S1 p8 |
| 传播/使能延时 | tPZH | VCCA=3.3V ± 0.3V，VCCB=2.5±0.2 V，DIR→A，测量负载按图6-1 |  |  | 14.2 | ns | S1 p8 |
| 传播/使能延时 | tPZH | VCCA=3.3V ± 0.3V，VCCB=3.3±0.3 V，DIR→A，测量负载按图6-1 |  |  | 12.9 | ns | S1 p8 |
| 传播/使能延时 | tPZH | VCCA=3.3V ± 0.3V，VCCB=5±0.5 V，DIR→A，测量负载按图6-1 |  |  | 10.3 | ns | S1 p8 |
| 传播/使能延时 | tPZL | VCCA=3.3V ± 0.3V，VCCB=1.8±0.15 V，DIR→A，测量负载按图6-1 |  |  | 27.6 | ns | S1 p8 |
| 传播/使能延时 | tPZL | VCCA=3.3V ± 0.3V，VCCB=2.5±0.2 V，DIR→A，测量负载按图6-1 |  |  | 15.5 | ns | S1 p8 |
| 传播/使能延时 | tPZL | VCCA=3.3V ± 0.3V，VCCB=3.3±0.3 V，DIR→A，测量负载按图6-1 |  |  | 13.8 | ns | S1 p8 |
| 传播/使能延时 | tPZL | VCCA=3.3V ± 0.3V，VCCB=5±0.5 V，DIR→A，测量负载按图6-1 |  |  | 11.3 | ns | S1 p8 |
| 传播/使能延时 | tPZH | VCCA=3.3V ± 0.3V，VCCB=1.8±0.15 V，DIR→B，测量负载按图6-1 |  |  | 21.1 | ns | S1 p8 |
| 传播/使能延时 | tPZH | VCCA=3.3V ± 0.3V，VCCB=2.5±0.2 V，DIR→B，测量负载按图6-1 |  |  | 13.6 | ns | S1 p8 |
| 传播/使能延时 | tPZH | VCCA=3.3V ± 0.3V，VCCB=3.3±0.3 V，DIR→B，测量负载按图6-1 |  |  | 11.5 | ns | S1 p8 |
| 传播/使能延时 | tPZH | VCCA=3.3V ± 0.3V，VCCB=5±0.5 V，DIR→B，测量负载按图6-1 |  |  | 10.1 | ns | S1 p8 |
| 传播/使能延时 | tPZL | VCCA=3.3V ± 0.3V，VCCB=1.8±0.15 V，DIR→B，测量负载按图6-1 |  |  | 19.9 | ns | S1 p8 |
| 传播/使能延时 | tPZL | VCCA=3.3V ± 0.3V，VCCB=2.5±0.2 V，DIR→B，测量负载按图6-1 |  |  | 14.3 | ns | S1 p8 |
| 传播/使能延时 | tPZL | VCCA=3.3V ± 0.3V，VCCB=3.3±0.3 V，DIR→B，测量负载按图6-1 |  |  | 12.3 | ns | S1 p8 |
| 传播/使能延时 | tPZL | VCCA=3.3V ± 0.3V，VCCB=5±0.5 V，DIR→B，测量负载按图6-1 |  |  | 11.3 | ns | S1 p8 |
| 传播/使能延时 | tPLH | VCCA=5V ±0.5V，VCCB=1.8±0.15 V，A→B，测量负载按图6-1 | 1.9 |  | 15.1 | ns | S1 p8 |
| 传播/使能延时 | tPLH | VCCA=5V ±0.5V，VCCB=2.5±0.2 V，A→B，测量负载按图6-1 | 1 |  | 7.5 | ns | S1 p8 |
| 传播/使能延时 | tPLH | VCCA=5V ±0.5V，VCCB=3.3±0.3 V，A→B，测量负载按图6-1 | 0.6 |  | 5.4 | ns | S1 p8 |
| 传播/使能延时 | tPLH | VCCA=5V ±0.5V，VCCB=5±0.5 V，A→B，测量负载按图6-1 | 0.5 |  | 3.9 | ns | S1 p8 |
| 传播/使能延时 | tPHL | VCCA=5V ±0.5V，VCCB=1.8±0.15 V，A→B，测量负载按图6-1 | 1.8 |  | 12.2 | ns | S1 p8 |
| 传播/使能延时 | tPHL | VCCA=5V ±0.5V，VCCB=2.5±0.2 V，A→B，测量负载按图6-1 | 0.9 |  | 6.2 | ns | S1 p8 |
| 传播/使能延时 | tPHL | VCCA=5V ±0.5V，VCCB=3.3±0.3 V，A→B，测量负载按图6-1 | 0.7 |  | 4.5 | ns | S1 p8 |
| 传播/使能延时 | tPHL | VCCA=5V ±0.5V，VCCB=5±0.5 V，A→B，测量负载按图6-1 | 0.5 |  | 3.5 | ns | S1 p8 |
| 传播/使能延时 | tPLH | VCCA=5V ±0.5V，VCCB=1.8±0.15 V，B→A，测量负载按图6-1 | 1.4 |  | 7.2 | ns | S1 p8 |
| 传播/使能延时 | tPLH | VCCA=5V ±0.5V，VCCB=2.5±0.2 V，B→A，测量负载按图6-1 | 1 |  | 5.1 | ns | S1 p8 |
| 传播/使能延时 | tPLH | VCCA=5V ±0.5V，VCCB=3.3±0.3 V，B→A，测量负载按图6-1 | 0.7 |  | 4.4 | ns | S1 p8 |
| 传播/使能延时 | tPLH | VCCA=5V ±0.5V，VCCB=5±0.5 V，B→A，测量负载按图6-1 | 0.5 |  | 3.9 | ns | S1 p8 |
| 传播/使能延时 | tPHL | VCCA=5V ±0.5V，VCCB=1.8±0.15 V，B→A，测量负载按图6-1 | 1.7 |  | 7 | ns | S1 p8 |
| 传播/使能延时 | tPHL | VCCA=5V ±0.5V，VCCB=2.5±0.2 V，B→A，测量负载按图6-1 | 0.9 |  | 4.6 | ns | S1 p8 |
| 传播/使能延时 | tPHL | VCCA=5V ±0.5V，VCCB=3.3±0.3 V，B→A，测量负载按图6-1 | 0.7 |  | 4 | ns | S1 p8 |
| 传播/使能延时 | tPHL | VCCA=5V ±0.5V，VCCB=5±0.5 V，B→A，测量负载按图6-1 | 0.5 |  | 3.5 | ns | S1 p8 |
| 传播/使能延时 | tPHZ | VCCA=5V ±0.5V，VCCB=1.8±0.15 V，DIR→A，测量负载按图6-1 | 2.1 |  | 5.4 | ns | S1 p8 |
| 传播/使能延时 | tPHZ | VCCA=5V ±0.5V，VCCB=2.5±0.2 V，DIR→A，测量负载按图6-1 | 2.2 |  | 5.4 | ns | S1 p8 |
| 传播/使能延时 | tPHZ | VCCA=5V ±0.5V，VCCB=3.3±0.3 V，DIR→A，测量负载按图6-1 | 2.2 |  | 5.5 | ns | S1 p8 |
| 传播/使能延时 | tPHZ | VCCA=5V ±0.5V，VCCB=5±0.5 V，DIR→A，测量负载按图6-1 | 2.2 |  | 5.4 | ns | S1 p8 |
| 传播/使能延时 | tPLZ | VCCA=5V ±0.5V，VCCB=1.8±0.15 V，DIR→A，测量负载按图6-1 | 0.9 |  | 3.8 | ns | S1 p8 |
| 传播/使能延时 | tPLZ | VCCA=5V ±0.5V，VCCB=2.5±0.2 V，DIR→A，测量负载按图6-1 | 1 |  | 3.8 | ns | S1 p8 |
| 传播/使能延时 | tPLZ | VCCA=5V ±0.5V，VCCB=3.3±0.3 V，DIR→A，测量负载按图6-1 | 0.7 |  | 3.7 | ns | S1 p8 |
| 传播/使能延时 | tPLZ | VCCA=5V ±0.5V，VCCB=5±0.5 V，DIR→A，测量负载按图6-1 | 0.7 |  | 3.7 | ns | S1 p8 |
| 传播/使能延时 | tPHZ | VCCA=5V ±0.5V，VCCB=1.8±0.15 V，DIR→B，测量负载按图6-1 | 4.8 |  | 20.2 | ns | S1 p8 |
| 传播/使能延时 | tPHZ | VCCA=5V ±0.5V，VCCB=2.5±0.2 V，DIR→B，测量负载按图6-1 | 2.5 |  | 9.8 | ns | S1 p8 |
| 传播/使能延时 | tPHZ | VCCA=5V ±0.5V，VCCB=3.3±0.3 V，DIR→B，测量负载按图6-1 | 1 |  | 8.5 | ns | S1 p8 |
| 传播/使能延时 | tPHZ | VCCA=5V ±0.5V，VCCB=5±0.5 V，DIR→B，测量负载按图6-1 | 2.5 |  | 6.5 | ns | S1 p8 |
| 传播/使能延时 | tPLZ | VCCA=5V ±0.5V，VCCB=1.8±0.15 V，DIR→B，测量负载按图6-1 | 3.2 |  | 14.8 | ns | S1 p8 |
| 传播/使能延时 | tPLZ | VCCA=5V ±0.5V，VCCB=2.5±0.2 V，DIR→B，测量负载按图6-1 | 2.5 |  | 7.4 | ns | S1 p8 |
| 传播/使能延时 | tPLZ | VCCA=5V ±0.5V，VCCB=3.3±0.3 V，DIR→B，测量负载按图6-1 | 2.5 |  | 7 | ns | S1 p8 |
| 传播/使能延时 | tPLZ | VCCA=5V ±0.5V，VCCB=5±0.5 V，DIR→B，测量负载按图6-1 | 1.6 |  | 4.5 | ns | S1 p8 |
| 传播/使能延时 | tPZH | VCCA=5V ±0.5V，VCCB=1.8±0.15 V，DIR→A，测量负载按图6-1 |  |  | 22 | ns | S1 p8 |
| 传播/使能延时 | tPZH | VCCA=5V ±0.5V，VCCB=2.5±0.2 V，DIR→A，测量负载按图6-1 |  |  | 12.5 | ns | S1 p8 |
| 传播/使能延时 | tPZH | VCCA=5V ±0.5V，VCCB=3.3±0.3 V，DIR→A，测量负载按图6-1 |  |  | 11.4 | ns | S1 p8 |
| 传播/使能延时 | tPZH | VCCA=5V ±0.5V，VCCB=5±0.5 V，DIR→A，测量负载按图6-1 |  |  | 8.4 | ns | S1 p8 |
| 传播/使能延时 | tPZL | VCCA=5V ±0.5V，VCCB=1.8±0.15 V，DIR→A，测量负载按图6-1 |  |  | 27.2 | ns | S1 p8 |
| 传播/使能延时 | tPZL | VCCA=5V ±0.5V，VCCB=2.5±0.2 V，DIR→A，测量负载按图6-1 |  |  | 14.4 | ns | S1 p8 |
| 传播/使能延时 | tPZL | VCCA=5V ±0.5V，VCCB=3.3±0.3 V，DIR→A，测量负载按图6-1 |  |  | 12.5 | ns | S1 p8 |
| 传播/使能延时 | tPZL | VCCA=5V ±0.5V，VCCB=5±0.5 V，DIR→A，测量负载按图6-1 |  |  | 10 | ns | S1 p8 |
| 传播/使能延时 | tPZH | VCCA=5V ±0.5V，VCCB=1.8±0.15 V，DIR→B，测量负载按图6-1 |  |  | 18.9 | ns | S1 p8 |
| 传播/使能延时 | tPZH | VCCA=5V ±0.5V，VCCB=2.5±0.2 V，DIR→B，测量负载按图6-1 |  |  | 11.3 | ns | S1 p8 |
| 传播/使能延时 | tPZH | VCCA=5V ±0.5V，VCCB=3.3±0.3 V，DIR→B，测量负载按图6-1 |  |  | 9.1 | ns | S1 p8 |
| 传播/使能延时 | tPZH | VCCA=5V ±0.5V，VCCB=5±0.5 V，DIR→B，测量负载按图6-1 |  |  | 7.6 | ns | S1 p8 |
| 传播/使能延时 | tPZL | VCCA=5V ±0.5V，VCCB=1.8±0.15 V，DIR→B，测量负载按图6-1 |  |  | 17.6 | ns | S1 p8 |
| 传播/使能延时 | tPZL | VCCA=5V ±0.5V，VCCB=2.5±0.2 V，DIR→B，测量负载按图6-1 |  |  | 11.6 | ns | S1 p8 |
| 传播/使能延时 | tPZL | VCCA=5V ±0.5V，VCCB=3.3±0.3 V，DIR→B，测量负载按图6-1 |  |  | 10 | ns | S1 p8 |
| 传播/使能延时 | tPZL | VCCA=5V ±0.5V，VCCB=5±0.5 V，DIR→B，测量负载按图6-1 |  |  | 8.6 | ns | S1 p8 |

用这些数时要注意：

- VCCI为输入端对应电源，VCCO为输出端对应电源；未列电压档的输入门限分别为0.7/0.3倍电源。DIR总是参考VCCA（S1 p4、p5）。
- 两数据端输入电路始终活动，不用的输入必须固定电平。任一电源为地时两端高阻（S1 p1、p5）。
- 使能时间为手册已计算并列出的值，非本条推算；必须使用相应电源与图6-1负载。Ci/Cio只有典型值（S1 p6～p8）。

## 热特性

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- |
| 结到环境热阻 | RθJA | DBV / DCK / DPK / DRL / YZP | 215.1 / 210.9 / 278.3 / 223.7 / 131.0 | °C/W | S1 p5 |
| 结到壳顶热阻 | RθJC(top) | DBV / DCK / DPK / DRL / YZP | 136.5 / 139.2 / 133.4 / 88.7 / 1.3 | °C/W | S1 p5 |
| 结到板热阻 | RθJB | DBV / DCK / DPK / DRL / YZP | 96.6 / 72 / 174.1 / 58.4 / 22.6 | °C/W | S1 p5 |
| 结到顶热参数 | ψJT | DBV / DCK / DPK / DRL / YZP | 71.5 / 54.9 / 23.4 / 5.9 / 5.2 | °C/W | S1 p5 |
| 结到板热参数 | ψJB | DBV / DCK / DPK / DRL / YZP | 96.3 / 71.7 / 173.5 / 58.1 / 22.6 | °C/W | S1 p5 |

## 静电额定

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- |
| 人体模型 | V(ESD) | JS-001 | ±2000 | V | S1 p4 |
| 带电器件模型 | V(ESD) | JESD22-C101 | ±1000 | V | S1 p4 |
| 机器模型 | V(ESD) |  | ±200 | V | S1 p4 |

手册未给出单独的静电敏感警告。

## 引脚与处置

### DBV / DCK / DRL / DRY（脚号相同）

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
| --- | --- | --- | --- | --- |
| 1 VCCA | P，A侧电源 |  |  | S1 p2、p3 |
| 2 GND | G，地 |  | 接地 | S1 p2、p3 |
| 3 A | I/O，A端 |  | 不用的输入固定为VCCI或GND | S1 p2、p3、p5 |
| 4 B | I/O，B端 |  | 同上 | S1 p2、p3、p5 |
| 5 DIR | I，方向，相对VCCA |  | 固定有效逻辑 | S1 p2、p3 |
| 6 VCCB | P，B侧电源 |  |  | S1 p2、p3 |

### YZP

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
| --- | --- | --- | --- | --- |
| A1 VCCA | P，A侧电源 |  |  | S1 p2、p3 |
| B1 GND | G，地 |  | 接地 | S1 p2、p3 |
| C1 A | I/O，A端 |  | 不用的输入固定为VCCI或GND | S1 p2、p3、p5 |
| C2 B | I/O，B端 |  | 同上 | S1 p2、p3、p5 |
| B2 DIR | I，方向，相对VCCA |  | 固定有效逻辑 | S1 p2、p3 |
| A2 VCCB | P，B侧电源 |  |  | S1 p2、p3 |

散热焊盘：手册未给出散热焊盘及其内部连接、焊接规定。


## 必需外围

- 两电源均应旁路，建议0.1 µF，可靠近并联1 µF；DIR不得悬浮（S1 p17）。

## 订货型号与封装

手册列出的型号与封装如下；空格表示手册未给出，不从型号自行推算。

| 订货型号或后缀 | 封装 | 脚数 | 电压或功能档 | 温度范围 | 引脚镀层 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| SN74LVC1T45DBVR | SOT-23 (DBV) | 6 |  | -40～85 °C | SN | S1 p21 |
| SN74LVC1T45DBVR.A | SOT-23 (DBV) | 6 |  | -40～85 °C | SN | S1 p21 |
| SN74LVC1T45DBVRE4 | SOT-23 (DBV) | 6 |  | -40～85 °C | SN | S1 p21 |
| SN74LVC1T45DBVRE4.A | SOT-23 (DBV) | 6 |  | -40～85 °C | SN | S1 p21 |
| SN74LVC1T45DBVRG4 | SOT-23 (DBV) | 6 |  | -40～85 °C | SN | S1 p21 |
| SN74LVC1T45DBVRG4.A | SOT-23 (DBV) | 6 |  | -40～85 °C | SN | S1 p21 |
| SN74LVC1T45DBVRG4.B | SOT-23 (DBV) | 6 |  | -40～85 °C | SN | S1 p21 |
| SN74LVC1T45DBVT | SOT-23 (DBV) | 6 |  | -40～85 °C | SN | S1 p21 |
| SN74LVC1T45DBVT.A | SOT-23 (DBV) | 6 |  | -40～85 °C | SN | S1 p21 |
| SN74LVC1T45DBVTG4 | SOT-23 (DBV) | 6 |  | -40～85 °C | SN | S1 p21 |
| SN74LVC1T45DBVTG4.A | SOT-23 (DBV) | 6 |  | -40～85 °C | SN | S1 p21 |
| SN74LVC1T45DCKR | SC70 (DCK) | 6 |  | -40～85 °C | SN | S1 p21 |
| SN74LVC1T45DCKR.A | SC70 (DCK) | 6 |  | -40～85 °C | SN | S1 p21 |
| SN74LVC1T45DCKR.B | SC70 (DCK) | 6 |  | -40～85 °C | SN | S1 p21 |
| SN74LVC1T45DCKRE4 | SC70 (DCK) | 6 |  | -40～85 °C | SN | S1 p21 |
| SN74LVC1T45DCKRE4.A | SC70 (DCK) | 6 |  | -40～85 °C | SN | S1 p21 |
| SN74LVC1T45DCKRE4.B | SC70 (DCK) | 6 |  | -40～85 °C | SN | S1 p21 |
| SN74LVC1T45DCKRG4 | SC70 (DCK) | 6 |  | -40～85 °C | SN | S1 p21 |
| SN74LVC1T45DCKRG4.A | SC70 (DCK) | 6 |  | -40～85 °C | SN | S1 p22 |
| SN74LVC1T45DCKRG4.B | SC70 (DCK) | 6 |  | -40～85 °C | SN | S1 p22 |
| SN74LVC1T45DCKT | SC70 (DCK) | 6 |  | -40～85 °C | SN | S1 p22 |
| SN74LVC1T45DCKT.A | SC70 (DCK) | 6 |  | -40～85 °C | SN | S1 p22 |
| SN74LVC1T45DCKT.B | SC70 (DCK) | 6 |  | -40～85 °C | SN | S1 p22 |
| SN74LVC1T45DCKTE4 | SC70 (DCK) | 6 |  | -40～85 °C | SN | S1 p22 |
| SN74LVC1T45DCKTG4 | SC70 (DCK) | 6 |  | -40～85 °C | SN | S1 p22 |
| SN74LVC1T45DCKTG4.A | SC70 (DCK) | 6 |  | -40～85 °C | SN | S1 p22 |
| SN74LVC1T45DCKTG4.B | SC70 (DCK) | 6 |  | -40～85 °C | SN | S1 p22 |
| SN74LVC1T45DPKR | USON (DPK) | 6 |  | -40～85 °C | SN | S1 p22 |
| SN74LVC1T45DPKR.B | USON (DPK) | 6 |  | -40～85 °C | SN | S1 p22 |
| SN74LVC1T45DPKRG4 | USON (DPK) | 6 |  | -40～85 °C | SN | S1 p22 |
| SN74LVC1T45DPKRG4.B | USON (DPK) | 6 |  | -40～85 °C | SN | S1 p22 |
| SN74LVC1T45DRLR | SOT-5X3 (DRL) | 6 |  | -40～85 °C | SN | S1 p22 |
| SN74LVC1T45DRLR.A | SOT-5X3 (DRL) | 6 |  | -40～85 °C | SN | S1 p22 |
| SN74LVC1T45DRLR.B | SOT-5X3 (DRL) | 6 |  | -40～85 °C | SN | S1 p22 |
| SN74LVC1T45DRLRG4 | SOT-5X3 (DRL) | 6 |  | -40～85 °C | SN | S1 p22 |
| SN74LVC1T45YZPR | DSBGA (YZP) | 6 |  | -40～85 °C | SN | S1 p22 |
| SN74LVC1T45YZPR.B | DSBGA (YZP) | 6 |  | -40～85 °C | SN | S1 p22 |



## 核对记录

- 2026-11-10：工具核对通过，核对了 546 个数。
