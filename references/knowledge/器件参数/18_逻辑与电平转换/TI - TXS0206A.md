# TI TXS0206A

类别：器件参数。
器件：SD/MMC等存储卡接口六位电平转换器，含时钟缓冲、反馈及检测。
手册：SCES833B，2016-04修订；订货附录2025-11-10。

## 来源

- S1：Datasheet/18_逻辑与电平转换/电平转换器_电压翻译器/TI - TXS0206A.pdf

页码均为 PDF 文件页序，共 31 页。

## 绝对最大值

| 参数 | 符号 | 条件 | 最小 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| A/B供电 | VCCA、VCCB |  | −0.5 | 4.6 | V | S1 p4 |
| 输入 | VI | A/B I/O及控制端 | −0.5 | 4.6 | V | S1 p4 |
| 输出 | VO | 高阻、断电及高低态 | −0.5 | 4.6 | V | S1 p4 |
| 输入钳位 | IIK | VI<0 |  | −50 | mA | S1 p4 |
| 输出钳位 | IOK | VO<0 |  | −50 | mA | S1 p4 |
| 连续输出电流 | IO |  |  | ±50 | mA | S1 p4 |
| VCCA/地连续电流 |  |  |  | ±100 | mA | S1 p4 |
| 储存温度 | Tstg |  | −65 | 150 | °C | S1 p4 |

## 推荐工作条件

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A/B供电 | VCCA、VCCB |  | 1.1 |  | 3.6 | V | S1 p5 |
| CMD/DAT高输入 | VIH | 按表列端口供电条件，VCCI为输入侧电源 | VCCI − 0.2 |  | VCCI | V | S1 p5 |
| EN/CLKA高输入 | VIH |  | VCCI × 0.65 |  | VCCI | V | S1 p5 |
| CMD/DAT低输入 | VIL | 按表列供电条件 | 0 |  | 0.15 | V | S1 p5 |
| EN/CLKA低输入 | VIL |  | 0 |  | VCCI × 0.35 | V | S1 p5 |
| 有效输出电压 | VO |  | 0 |  | VCCO | V | S1 p5 |
| 三态输出电压 | VO |  | 0 |  | 3.6 | V | S1 p5 |
| 输入上升/下降速率 | Δt/Δv |  |  |  | 5 | ns/V | S1 p5 |
| 环境温度 | TA |  | −40 |  | 85 | °C | S1 p5 |
| 输出高电流 | IOH | CLK-f，VCCA=1.1～3.6 V |  |  | −100 | µA | S1 p5 |
| 输出低电流 | IOL | CLK-f，VCCA=1.1～3.6 V |  |  | 100 | µA | S1 p5 |
| 输出高电流 | IOH | CLK-f，VCCA=1.1～1.3 V；另一电源1.1～3.6 V |  |  | -0.5 | mA | S1 p5 |
| 输出低电流 | IOL | CLK-f，VCCA=1.1～1.3 V；另一电源1.1～3.6 V |  |  | 0.5 | mA | S1 p5 |
| 输出高电流 | IOH | CLK-f，VCCA=1.4～1.6 V；另一电源1.1～3.6 V |  |  | -1 | mA | S1 p5 |
| 输出低电流 | IOL | CLK-f，VCCA=1.4～1.6 V；另一电源1.1～3.6 V |  |  | 1 | mA | S1 p5 |
| 输出高电流 | IOH | CLK-f，VCCA=1.65～1.95 V；另一电源1.1～3.6 V |  |  | -2 | mA | S1 p5 |
| 输出低电流 | IOL | CLK-f，VCCA=1.65～1.95 V；另一电源1.1～3.6 V |  |  | 2 | mA | S1 p5 |
| 输出高电流 | IOH | CLK-f，VCCA=2.3～2.7 V；另一电源1.1～3.6 V |  |  | -4 | mA | S1 p5 |
| 输出低电流 | IOL | CLK-f，VCCA=2.3～2.7 V；另一电源1.1～3.6 V |  |  | 4 | mA | S1 p5 |
| 输出高电流 | IOH | CLK-f，VCCA=3～3.6 V；另一电源1.1～3.6 V |  |  | -8 | mA | S1 p5 |
| 输出低电流 | IOL | CLK-f，VCCA=3～3.6 V；另一电源1.1～3.6 V |  |  | 8 | mA | S1 p5 |
| 输出高电流 | IOH | CLK，VCCB=1.1～3.6 V |  |  | −100 | µA | S1 p5 |
| 输出低电流 | IOL | CLK，VCCB=1.1～3.6 V |  |  | 100 | µA | S1 p5 |
| 输出高电流 | IOH | CLK，VCCB=1.1～1.3 V；另一电源1.1～3.6 V |  |  | -0.5 | mA | S1 p5 |
| 输出低电流 | IOL | CLK，VCCB=1.1～1.3 V；另一电源1.1～3.6 V |  |  | 0.5 | mA | S1 p5 |
| 输出高电流 | IOH | CLK，VCCB=1.4～1.6 V；另一电源1.1～3.6 V |  |  | -1 | mA | S1 p5 |
| 输出低电流 | IOL | CLK，VCCB=1.4～1.6 V；另一电源1.1～3.6 V |  |  | 1 | mA | S1 p5 |
| 输出高电流 | IOH | CLK，VCCB=1.65～1.95 V；另一电源1.1～3.6 V |  |  | -2 | mA | S1 p5 |
| 输出低电流 | IOL | CLK，VCCB=1.65～1.95 V；另一电源1.1～3.6 V |  |  | 2 | mA | S1 p5 |
| 输出高电流 | IOH | CLK，VCCB=2.3～2.7 V；另一电源1.1～3.6 V |  |  | -4 | mA | S1 p5 |
| 输出低电流 | IOL | CLK，VCCB=2.3～2.7 V；另一电源1.1～3.6 V |  |  | 4 | mA | S1 p5 |
| 输出高电流 | IOH | CLK，VCCB=3～3.6 V；另一电源1.1～3.6 V |  |  | -8 | mA | S1 p5 |
| 输出低电流 | IOL | CLK，VCCB=3～3.6 V；另一电源1.1～3.6 V |  |  | 8 | mA | S1 p5 |

## 电气特性

TA=−40～85 °C；典型值TA=25 °C。开关测量负载15 pF，输入脉冲与参考电平按S1 p15。

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 输出高 | VOH | CLK-f，VCCA=1.1～3.6 V，VCCB=1.65～3.6 V，IOH=−100 µA | VCCA × 0.8 |  |  | V | S1 p6 |
| 输出低 | VOL | CLK-f，额定供电，IOL=100 µA |  |  | VCCA × 0.2 | V | S1 p6 |
| 输出高 | VOH | CLK-f，VCCA=1.1 V，VCCB=1.65～3.6 V，IOH=−0.5 mA | 0.8 |  |  | V | S1 p6 |
| 输出低 | VOL | CLK-f，VCCA=1.1 V，VCCB=1.65～3.6 V，IOL=0.5 mA |  |  | 0.35 | V | S1 p6 |
| 输出高 | VOH | CLK-f，VCCA=1.4 V，VCCB=1.65～3.6 V，IOH=−1 mA | 1.05 |  |  | V | S1 p6 |
| 输出低 | VOL | CLK-f，VCCA=1.4 V，VCCB=1.65～3.6 V，IOL=1 mA |  |  | 0.35 | V | S1 p6 |
| 输出高 | VOH | CLK-f，VCCA=1.65 V，VCCB=1.65～3.6 V，IOH=−2 mA | 1.2 |  |  | V | S1 p6 |
| 输出低 | VOL | CLK-f，VCCA=1.65 V，VCCB=1.65～3.6 V，IOL=2 mA |  |  | 0.45 | V | S1 p6 |
| 输出高 | VOH | CLK-f，VCCA=2.3 V，VCCB=1.65～3.6 V，IOH=−4 mA | 1.75 |  |  | V | S1 p6 |
| 输出低 | VOL | CLK-f，VCCA=2.3 V，VCCB=1.65～3.6 V，IOL=4 mA |  |  | 0.55 | V | S1 p6 |
| 输出高 | VOH | CLK-f，VCCA=3 V，VCCB=1.65～3.6 V，IOH=−8 mA | 2.3 |  |  | V | S1 p6 |
| 输出低 | VOL | CLK-f，VCCA=3 V，VCCB=1.65～3.6 V，IOL=8 mA |  |  | 0.7 | V | S1 p6 |
| 输出高 | VOH | CLK，VCCB=1.1～3.6 V，VCCA=1.1～3.6 V，IOH=−100 µA | VCCB × 0.8 |  |  | V | S1 p6 |
| 输出低 | VOL | CLK，额定供电，IOL=100 µA |  |  | VCCB × 0.2 | V | S1 p7 |
| 输出高 | VOH | CLK，VCCB=1.65 V，VCCA=1.1～3.6 V，IOH=−2 mA | 1.2 |  |  | V | S1 p6 |
| 输出低 | VOL | CLK，VCCB=1.65 V，VCCA=1.1～3.6 V，IOL=2 mA |  |  | 0.45 | V | S1 p7 |
| 输出高 | VOH | CLK，VCCB=2.3 V，VCCA=1.1～3.6 V，IOH=−4 mA | 1.75 |  |  | V | S1 p6 |
| 输出低 | VOL | CLK，VCCB=2.3 V，VCCA=1.1～3.6 V，IOL=4 mA |  |  | 0.55 | V | S1 p7 |
| 输出高 | VOH | CLK，VCCB=3 V，VCCA=1.1～3.6 V，IOH=−8 mA | 2.3 |  |  | V | S1 p6 |
| 输出低 | VOL | CLK，VCCB=3 V，VCCA=1.1～3.6 V，IOL=8 mA |  |  | 0.7 | V | S1 p7 |
| 数据/命令高输出 | VOH | A端，IOH=−20 µA，VCCA=1.1～3.6 V，VCCB=1.65～3.6 V | VCCA × 0.8 |  |  | V | S1 p6 |
| 数据/命令低输出 | VOL | A端，VCCA=1.1 V，另一侧额定供电，IOL=135 µA |  |  | 0.4 | V | S1 p6 |
| 数据/命令低输出 | VOL | A端，VCCA=1.4 V，另一侧额定供电，IOL=180 µA |  |  | 0.4 | V | S1 p6 |
| 数据/命令低输出 | VOL | A端，VCCA=1.65 V，另一侧额定供电，IOL=220 µA |  |  | 0.4 | V | S1 p6 |
| 数据/命令低输出 | VOL | A端，VCCA=2.3 V，另一侧额定供电，IOL=300 µA |  |  | 0.4 | V | S1 p6 |
| 数据/命令低输出 | VOL | A端，VCCA=3 V，另一侧额定供电，IOL=400 µA |  |  | 0.55 | V | S1 p6 |
| 数据/命令高输出 | VOH | B端，IOH=−20 µA，VCCA=1.1～3.6 V，VCCB=1.65～3.6 V | VCCB × 0.8 |  |  | V | S1 p6 |
| 数据/命令低输出 | VOL | B端，VCCB=1.1～3.6 V，另一侧额定供电，IOL=135 µA |  |  | 0.4 | V | S1 p7 |
| 数据/命令低输出 | VOL | B端，VCCB=1.65 V，另一侧额定供电，IOL=220 µA |  |  | 0.4 | V | S1 p7 |
| 数据/命令低输出 | VOL | B端，VCCB=2.3 V，另一侧额定供电，IOL=300 µA |  |  | 0.4 | V | S1 p7 |
| 数据/命令低输出 | VOL | B端，VCCB=3 V，另一侧额定供电，IOL=300 µA |  |  | 0.55 | V | S1 p7 |
| 控制输入电流 | II | VI=VCCA或GND，VCCA=1.1～3.6 V，VCCB=1.65～3.6 V |  |  | ±1 | µA | S1 p7 |
| A电源电流 | ICCA | VI=VCCI，IO=0，VCCA=1.1～3.6 V，VCCB=1.65～3.6 V |  |  | 7 | µA | S1 p7 |
| B电源电流 | ICCB | 同上 |  |  | 11 | µA | S1 p7 |
| A端电容 | Cio | 输入电容条件VI=VCCA或GND；典型TA=25 °C |  | 5.5 | 6.5 | pF | S1 p7 |
| B端电容 | Cio | 输入电容条件VI=VCCA或GND；典型TA=25 °C |  | 7 | 9.5 | pF | S1 p7 |
| 控制输入电容 | Ci | 输入电容条件VI=VCCA或GND；典型TA=25 °C |  | 3.5 | 4.5 | pF | S1 p7 |
| 时钟输入电容 | Ci | 输入电容条件VI=VCCA或GND；典型TA=25 °C |  | 3 | 4 | pF | S1 p7 |
| 命令/数据速率 |  | VCCA=1.2±0.1 V，VCCB=1.8±0.15 V；推挽 |  |  | 40 | Mbps | S1 p7 |
| 命令速率 |  | VCCA=1.2±0.1 V，VCCB=1.8±0.15 V；开漏 |  |  | 1 | Mbps | S1 p7 |
| 时钟频率 |  | VCCA=1.2±0.1 V，VCCB=1.8±0.15 V；推挽 |  |  | 40 | MHz | S1 p7 |
| 命令/数据脉宽 | tW | VCCA=1.2±0.1 V，VCCB=1.8±0.15 V；推挽 | 25 |  |  | ns | S1 p7 |
| 命令脉宽 | tW | VCCA=1.2±0.1 V，VCCB=1.8±0.15 V；开漏 | 1 |  |  | µs | S1 p7 |
| 时钟脉宽 | tW | VCCA=1.2±0.1 V，VCCB=1.8±0.15 V；推挽 | 10 |  |  | ns | S1 p7 |
| 命令/数据速率 |  | VCCA=1.2±0.1 V，VCCB=3.3±0.3 V；推挽 |  |  | 40 | Mbps | S1 p7 |
| 命令速率 |  | VCCA=1.2±0.1 V，VCCB=3.3±0.3 V；开漏 |  |  | 1 | Mbps | S1 p7 |
| 时钟频率 |  | VCCA=1.2±0.1 V，VCCB=3.3±0.3 V；推挽 |  |  | 40 | MHz | S1 p7 |
| 命令/数据脉宽 | tW | VCCA=1.2±0.1 V，VCCB=3.3±0.3 V；推挽 | 25 |  |  | ns | S1 p7 |
| 命令脉宽 | tW | VCCA=1.2±0.1 V，VCCB=3.3±0.3 V；开漏 | 1 |  |  | µs | S1 p7 |
| 时钟脉宽 | tW | VCCA=1.2±0.1 V，VCCB=3.3±0.3 V；推挽 | 8.3 |  |  | ns | S1 p7 |
| 命令/数据速率 |  | VCCA=1.8±0.15 V，VCCB=1.8±0.15 V；推挽 |  |  | 60 | Mbps | S1 p8 |
| 命令速率 |  | VCCA=1.8±0.15 V，VCCB=1.8±0.15 V；开漏 |  |  | 1 | Mbps | S1 p8 |
| 时钟频率 |  | VCCA=1.8±0.15 V，VCCB=1.8±0.15 V；推挽 |  |  | 60 | MHz | S1 p8 |
| 命令/数据脉宽 | tW | VCCA=1.8±0.15 V，VCCB=1.8±0.15 V；推挽 | 17 |  |  | ns | S1 p8 |
| 命令脉宽 | tW | VCCA=1.8±0.15 V，VCCB=1.8±0.15 V；开漏 | 1 |  |  | µs | S1 p8 |
| 时钟脉宽 | tW | VCCA=1.8±0.15 V，VCCB=1.8±0.15 V；推挽 | 8.3 |  |  | ns | S1 p8 |
| 命令/数据速率 |  | VCCA=1.8±0.15 V，VCCB=3.3±0.3 V；推挽 |  |  | 60 | Mbps | S1 p8 |
| 命令速率 |  | VCCA=1.8±0.15 V，VCCB=3.3±0.3 V；开漏 |  |  | 1 | Mbps | S1 p8 |
| 时钟频率 |  | VCCA=1.8±0.15 V，VCCB=3.3±0.3 V；推挽 |  |  | 60 | MHz | S1 p8 |
| 命令/数据脉宽 | tW | VCCA=1.8±0.15 V，VCCB=3.3±0.3 V；推挽 | 17 |  |  | ns | S1 p8 |
| 命令脉宽 | tW | VCCA=1.8±0.15 V，VCCB=3.3±0.3 V；开漏 | 1 |  |  | µs | S1 p8 |
| 时钟脉宽 | tW | VCCA=1.8±0.15 V，VCCB=3.3±0.3 V；推挽 | 8.3 |  |  | ns | S1 p8 |
| 命令/数据速率 |  | VCCA=3.3±0.3 V，VCCB=1.8±0.15 V；推挽 |  |  | 60 | Mbps | S1 p8 |
| 命令速率 |  | VCCA=3.3±0.3 V，VCCB=1.8±0.15 V；开漏 |  |  | 1 | Mbps | S1 p8 |
| 时钟频率 |  | VCCA=3.3±0.3 V，VCCB=1.8±0.15 V；推挽 |  |  | 55 | MHz | S1 p8 |
| 命令/数据脉宽 | tW | VCCA=3.3±0.3 V，VCCB=1.8±0.15 V；推挽 | 17 |  |  | ns | S1 p8 |
| 命令脉宽 | tW | VCCA=3.3±0.3 V，VCCB=1.8±0.15 V；开漏 | 1 |  |  | µs | S1 p8 |
| 时钟脉宽 | tW | VCCA=3.3±0.3 V，VCCB=1.8±0.15 V；推挽 | 9 |  |  | ns | S1 p8 |
| 命令/数据速率 |  | VCCA=3.3±0.3 V，VCCB=3.3±0.3 V；推挽 |  |  | 60 | Mbps | S1 p8 |
| 命令速率 |  | VCCA=3.3±0.3 V，VCCB=3.3±0.3 V；开漏 |  |  | 1 | Mbps | S1 p8 |
| 时钟频率 |  | VCCA=3.3±0.3 V，VCCB=3.3±0.3 V；推挽 |  |  | 55 | MHz | S1 p8 |
| 命令/数据脉宽 | tW | VCCA=3.3±0.3 V，VCCB=3.3±0.3 V；推挽 | 17 |  |  | ns | S1 p8 |
| 命令脉宽 | tW | VCCA=3.3±0.3 V，VCCB=3.3±0.3 V；开漏 | 1 |  |  | µs | S1 p8 |
| 时钟脉宽 | tW | VCCA=3.3±0.3 V，VCCB=3.3±0.3 V；推挽 | 9 |  |  | ns | S1 p8 |
| 传播延迟 | tpd | CMDA→CMDB，VCCA=1.2±0.1 V，VCCB=1.8±0.15 V |  |  | 5.7 | ns | S1 p9 |
| 传播延迟 | tpd | CMDA→CMDB，VCCA=1.2±0.1 V，VCCB=3.3±0.3 V |  |  | 4.4 | ns | S1 p9 |
| 传播延迟 | tpd | CMDB→CMDA，VCCA=1.2±0.1 V，VCCB=1.8±0.15 V |  |  | 6.7 | ns | S1 p9 |
| 传播延迟 | tpd | CMDB→CMDA，VCCA=1.2±0.1 V，VCCB=3.3±0.3 V |  |  | 5.8 | ns | S1 p9 |
| 传播延迟 | tpd | CLKA→CLKB，VCCA=1.2±0.1 V，VCCB=1.8±0.15 V |  |  | 6.2 | ns | S1 p9 |
| 传播延迟 | tpd | CLKA→CLKB，VCCA=1.2±0.1 V，VCCB=3.3±0.3 V |  |  | 4.5 | ns | S1 p9 |
| 传播延迟 | tpd | DATxA→DATxB，VCCA=1.2±0.1 V，VCCB=1.8±0.15 V |  |  | 7.6 | ns | S1 p9 |
| 传播延迟 | tpd | DATxA→DATxB，VCCA=1.2±0.1 V，VCCB=3.3±0.3 V |  |  | 7.5 | ns | S1 p9 |
| 传播延迟 | tpd | DATxB→DATxA，VCCA=1.2±0.1 V，VCCB=1.8±0.15 V |  |  | 6.3 | ns | S1 p9 |
| 传播延迟 | tpd | DATxB→DATxA，VCCA=1.2±0.1 V，VCCB=3.3±0.3 V |  |  | 4.6 | ns | S1 p9 |
| 传播延迟 | tpd | CLKA→CLK-f，VCCA=1.2±0.1 V，VCCB=1.8±0.15 V |  |  | 12 | ns | S1 p9 |
| 传播延迟 | tpd | CLKA→CLK-f，VCCA=1.2±0.1 V，VCCB=3.3±0.3 V |  |  | 7.9 | ns | S1 p9 |
| 使能时间 | ten | EN→B端，VCCA=1.2±0.1 V，VCCB=1.8±0.15 V |  |  | 1 | µs | S1 p9 |
| 禁止时间 | tdis | EN→B端，VCCA=1.2±0.1 V，VCCB=1.8±0.15 V |  |  | 412 | ns | S1 p9 |
| 使能时间 | ten | EN→B端，VCCA=1.2±0.1 V，VCCB=3.3±0.3 V |  |  | 1 | µs | S1 p9 |
| 禁止时间 | tdis | EN→B端，VCCA=1.2±0.1 V，VCCB=3.3±0.3 V |  |  | 363 | ns | S1 p9 |
| 使能时间 | ten | EN→A端，VCCA=1.2±0.1 V，VCCB=1.8±0.15 V |  |  | 1 | µs | S1 p9 |
| 禁止时间 | tdis | EN→A端，VCCA=1.2±0.1 V，VCCB=1.8±0.15 V |  |  | 423 | ns | S1 p9 |
| 使能时间 | ten | EN→A端，VCCA=1.2±0.1 V，VCCB=3.3±0.3 V |  |  | 1 | µs | S1 p9 |
| 禁止时间 | tdis | EN→A端，VCCA=1.2±0.1 V，VCCB=3.3±0.3 V |  |  | 422 | ns | S1 p9 |
| 传播延迟 | tpd | CMDA→CMDB，VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 4.9 | ns | S1 p10 |
| 传播延迟 | tpd | CMDA→CMDB，VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 3.3 | ns | S1 p10 |
| 传播延迟 | tpd | CMDB→CMDA，VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 5.6 | ns | S1 p10 |
| 传播延迟 | tpd | CMDB→CMDA，VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 3.6 | ns | S1 p10 |
| 传播延迟 | tpd | CLKA→CLKB，VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 5.4 | ns | S1 p10 |
| 传播延迟 | tpd | CLKA→CLKB，VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 3.4 | ns | S1 p10 |
| 传播延迟 | tpd | DATxA→DATxB，VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 5 | ns | S1 p10 |
| 传播延迟 | tpd | DATxA→DATxB，VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 4.4 | ns | S1 p10 |
| 传播延迟 | tpd | DATxB→DATxA，VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 5.4 | ns | S1 p10 |
| 传播延迟 | tpd | DATxB→DATxA，VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 3.5 | ns | S1 p10 |
| 传播延迟 | tpd | CLKA→CLK-f，VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 10.2 | ns | S1 p10 |
| 传播延迟 | tpd | CLKA→CLK-f，VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 5.7 | ns | S1 p10 |
| 使能时间 | ten | EN→B端，VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 1 | µs | S1 p10 |
| 禁止时间 | tdis | EN→B端，VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 411 | ns | S1 p10 |
| 使能时间 | ten | EN→B端，VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 1 | µs | S1 p10 |
| 禁止时间 | tdis | EN→B端，VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 411 | ns | S1 p10 |
| 使能时间 | ten | EN→A端，VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 1 | µs | S1 p10 |
| 禁止时间 | tdis | EN→A端，VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 413 | ns | S1 p10 |
| 使能时间 | ten | EN→A端，VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 1 | µs | S1 p10 |
| 禁止时间 | tdis | EN→A端，VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 361 | ns | S1 p10 |
| 传播延迟 | tpd | CMDA→CMDB，VCCA=3.3±0.3 V，VCCB=1.8±0.15 V |  |  | 5.3 | ns | S1 p11 |
| 传播延迟 | tpd | CMDA→CMDB，VCCA=3.3±0.3 V，VCCB=3.3±0.3 V |  |  | 3.2 | ns | S1 p11 |
| 传播延迟 | tpd | CMDB→CMDA，VCCA=3.3±0.3 V，VCCB=1.8±0.15 V |  |  | 5.1 | ns | S1 p11 |
| 传播延迟 | tpd | CMDB→CMDA，VCCA=3.3±0.3 V，VCCB=3.3±0.3 V |  |  | 3 | ns | S1 p11 |
| 传播延迟 | tpd | CLKA→CLKB，VCCA=3.3±0.3 V，VCCB=1.8±0.15 V |  |  | 4.8 | ns | S1 p11 |
| 传播延迟 | tpd | CLKA→CLKB，VCCA=3.3±0.3 V，VCCB=3.3±0.3 V |  |  | 3.1 | ns | S1 p11 |
| 传播延迟 | tpd | DATxA→DATxB，VCCA=3.3±0.3 V，VCCB=1.8±0.15 V |  |  | 5.1 | ns | S1 p11 |
| 传播延迟 | tpd | DATxA→DATxB，VCCA=3.3±0.3 V，VCCB=3.3±0.3 V |  |  | 3.2 | ns | S1 p11 |
| 传播延迟 | tpd | DATxB→DATxA，VCCA=3.3±0.3 V，VCCB=1.8±0.15 V |  |  | 9.6 | ns | S1 p11 |
| 传播延迟 | tpd | DATxB→DATxA，VCCA=3.3±0.3 V，VCCB=3.3±0.3 V |  |  | 5.1 | ns | S1 p11 |
| 传播延迟 | tpd | CLKA→CLK-f，VCCA=3.3±0.3 V，VCCB=1.8±0.15 V |  |  | 6.8 | ns | S1 p11 |
| 传播延迟 | tpd | CLKA→CLK-f，VCCA=3.3±0.3 V，VCCB=3.3±0.3 V |  |  | 4.2 | ns | S1 p11 |
| 使能时间 | ten | EN→B端，VCCA=3.3±0.3 V，VCCB=1.8±0.15 V |  |  | 1 | µs | S1 p11 |
| 禁止时间 | tdis | EN→B端，VCCA=3.3±0.3 V，VCCB=1.8±0.15 V |  |  | 410 | ns | S1 p11 |
| 使能时间 | ten | EN→B端，VCCA=3.3±0.3 V，VCCB=3.3±0.3 V |  |  | 1 | µs | S1 p11 |
| 禁止时间 | tdis | EN→B端，VCCA=3.3±0.3 V，VCCB=3.3±0.3 V |  |  | 364 | ns | S1 p11 |
| 使能时间 | ten | EN→A端，VCCA=3.3±0.3 V，VCCB=1.8±0.15 V |  |  | 1 | µs | S1 p11 |
| 禁止时间 | tdis | EN→A端，VCCA=3.3±0.3 V，VCCB=1.8±0.15 V |  |  | 396 | ns | S1 p11 |
| 使能时间 | ten | EN→A端，VCCA=3.3±0.3 V，VCCB=3.3±0.3 V |  |  | 1 | µs | S1 p11 |
| 禁止时间 | tdis | EN→A端，VCCA=3.3±0.3 V，VCCB=3.3±0.3 V |  |  | 398 | ns | S1 p11 |
| 上升时间 | trA/B | CMDA，VCCA=1.2±0.1 V，VCCB=1.8±0.15 V | 3.5 |  | 8.4 | ns | S1 p9 |
| 上升时间 | trA/B | CMDA，VCCA=1.2±0.1 V，VCCB=3.3±0.3 V | 3.4 |  | 8.1 | ns | S1 p9 |
| 上升时间 | trA/B | CLK-f，VCCA=1.2±0.1 V，VCCB=1.8±0.15 V | 1 |  | 4.7 | ns | S1 p9 |
| 上升时间 | trA/B | CLK-f，VCCA=1.2±0.1 V，VCCB=3.3±0.3 V | 1 |  | 4.1 | ns | S1 p9 |
| 上升时间 | trA/B | DATxA，VCCA=1.2±0.1 V，VCCB=1.8±0.15 V | 3.5 |  | 8.4 | ns | S1 p9 |
| 上升时间 | trA/B | DATxA，VCCA=1.2±0.1 V，VCCB=3.3±0.3 V | 3.4 |  | 8.1 | ns | S1 p9 |
| 上升时间 | trA/B | CMDB，VCCA=1.2±0.1 V，VCCB=1.8±0.15 V | 1.4 |  | 6.5 | ns | S1 p9 |
| 上升时间 | trA/B | CMDB，VCCA=1.2±0.1 V，VCCB=3.3±0.3 V | 0.6 |  | 3.1 | ns | S1 p9 |
| 上升时间 | trA/B | CLKB，VCCA=1.2±0.1 V，VCCB=1.8±0.15 V | 0.6 |  | 5.9 | ns | S1 p9 |
| 上升时间 | trA/B | CLKB，VCCA=1.2±0.1 V，VCCB=3.3±0.3 V | 0.5 |  | 4.3 | ns | S1 p9 |
| 上升时间 | trA/B | DATxB，VCCA=1.2±0.1 V，VCCB=1.8±0.15 V | 1.4 |  | 10.9 | ns | S1 p9 |
| 上升时间 | trA/B | DATxB，VCCA=1.2±0.1 V，VCCB=3.3±0.3 V | 0.6 |  | 5 | ns | S1 p9 |
| 下降时间 | tfA/B | CMDA，VCCA=1.2±0.1 V，VCCB=1.8±0.15 V | 2.4 |  | 5.7 | ns | S1 p9 |
| 下降时间 | tfA/B | CMDA，VCCA=1.2±0.1 V，VCCB=3.3±0.3 V | 2 |  | 5.1 | ns | S1 p9 |
| 下降时间 | tfA/B | CLK-f，VCCA=1.2±0.1 V，VCCB=1.8±0.15 V | 0.8 |  | 2.5 | ns | S1 p9 |
| 下降时间 | tfA/B | CLK-f，VCCA=1.2±0.1 V，VCCB=3.3±0.3 V | 0.8 |  | 3 | ns | S1 p9 |
| 下降时间 | tfA/B | DATxA，VCCA=1.2±0.1 V，VCCB=1.8±0.15 V | 2.4 |  | 5.7 | ns | S1 p9 |
| 下降时间 | tfA/B | DATxA，VCCA=1.2±0.1 V，VCCB=3.3±0.3 V | 1.9 |  | 5.1 | ns | S1 p9 |
| 下降时间 | tfA/B | CMDB，VCCA=1.2±0.1 V，VCCB=1.8±0.15 V | 1.2 |  | 5.4 | ns | S1 p9 |
| 下降时间 | tfA/B | CMDB，VCCA=1.2±0.1 V，VCCB=3.3±0.3 V | 0.6 |  | 3.6 | ns | S1 p9 |
| 下降时间 | tfA/B | CLKB，VCCA=1.2±0.1 V，VCCB=1.8±0.15 V | 0.6 |  | 6.3 | ns | S1 p9 |
| 下降时间 | tfA/B | CLKB，VCCA=1.2±0.1 V，VCCB=3.3±0.3 V | 0.5 |  | 4 | ns | S1 p9 |
| 下降时间 | tfA/B | DATxB，VCCA=1.2±0.1 V，VCCB=1.8±0.15 V | 0.6 |  | 6.3 | ns | S1 p9 |
| 下降时间 | tfA/B | DATxB，VCCA=1.2±0.1 V，VCCB=3.3±0.3 V | 0.5 |  | 3.6 | ns | S1 p9 |
| 通道输出偏斜 | tSK(O) | VCCA=1.2±0.1 V，VCCB=1.8±0.15 V |  |  | 1 | ns | S1 p9 |
| 通道输出偏斜 | tSK(O) | VCCA=1.2±0.1 V，VCCB=3.3±0.3 V |  |  | 1 | ns | S1 p9 |
| 上升时间 | trA/B | CMDA，VCCA=1.8±0.15 V，VCCB=1.8±0.15 V | 2.1 |  | 4.5 | ns | S1 p10 |
| 上升时间 | trA/B | CMDA，VCCA=1.8±0.15 V，VCCB=3.3±0.3 V | 2.1 |  | 4.1 | ns | S1 p10 |
| 上升时间 | trA/B | CLK-f，VCCA=1.8±0.15 V，VCCB=1.8±0.15 V | 0.6 |  | 2.5 | ns | S1 p10 |
| 上升时间 | trA/B | CLK-f，VCCA=1.8±0.15 V，VCCB=3.3±0.3 V | 0.6 |  | 2.3 | ns | S1 p10 |
| 上升时间 | trA/B | DATxA，VCCA=1.8±0.15 V，VCCB=1.8±0.15 V | 1.8 |  | 4.5 | ns | S1 p10 |
| 上升时间 | trA/B | DATxA，VCCA=1.8±0.15 V，VCCB=3.3±0.3 V | 1.8 |  | 4.2 | ns | S1 p10 |
| 上升时间 | trA/B | CMDB，VCCA=1.8±0.15 V，VCCB=1.8±0.15 V | 1.4 |  | 6.6 | ns | S1 p10 |
| 上升时间 | trA/B | CMDB，VCCA=1.8±0.15 V，VCCB=3.3±0.3 V | 0.7 |  | 3.8 | ns | S1 p10 |
| 上升时间 | trA/B | CLKB，VCCA=1.8±0.15 V，VCCB=1.8±0.15 V | 0.5 |  | 5.8 | ns | S1 p10 |
| 上升时间 | trA/B | CLKB，VCCA=1.8±0.15 V，VCCB=3.3±0.3 V | 0.5 |  | 4.4 | ns | S1 p10 |
| 上升时间 | trA/B | DATxB，VCCA=1.8±0.15 V，VCCB=1.8±0.15 V | 1.4 |  | 10.8 | ns | S1 p10 |
| 上升时间 | trA/B | DATxB，VCCA=1.8±0.15 V，VCCB=3.3±0.3 V | 0.7 |  | 8 | ns | S1 p10 |
| 下降时间 | tfA/B | CMDA，VCCA=1.8±0.15 V，VCCB=1.8±0.15 V | 0.4 |  | 3.4 | ns | S1 p11 |
| 下降时间 | tfA/B | CMDA，VCCA=1.8±0.15 V，VCCB=3.3±0.3 V | 0.3 |  | 2.9 | ns | S1 p11 |
| 下降时间 | tfA/B | CLK-f，VCCA=1.8±0.15 V，VCCB=1.8±0.15 V | 0.3 |  | 2.8 | ns | S1 p11 |
| 下降时间 | tfA/B | CLK-f，VCCA=1.8±0.15 V，VCCB=3.3±0.3 V | 0.3 |  | 2.8 | ns | S1 p11 |
| 下降时间 | tfA/B | DATxA，VCCA=1.8±0.15 V，VCCB=1.8±0.15 V | 0.4 |  | 3.4 | ns | S1 p11 |
| 下降时间 | tfA/B | DATxA，VCCA=1.8±0.15 V，VCCB=3.3±0.3 V | 0.3 |  | 2.9 | ns | S1 p11 |
| 下降时间 | tfA/B | CMDB，VCCA=1.8±0.15 V，VCCB=1.8±0.15 V | 1.1 |  | 6.3 | ns | S1 p11 |
| 下降时间 | tfA/B | CMDB，VCCA=1.8±0.15 V，VCCB=3.3±0.3 V | 0.6 |  | 3.7 | ns | S1 p11 |
| 下降时间 | tfA/B | CLKB，VCCA=1.8±0.15 V，VCCB=1.8±0.15 V | 0.6 |  | 8.7 | ns | S1 p11 |
| 下降时间 | tfA/B | CLKB，VCCA=1.8±0.15 V，VCCB=3.3±0.3 V | 0.5 |  | 4.1 | ns | S1 p11 |
| 下降时间 | tfA/B | DATxB，VCCA=1.8±0.15 V，VCCB=1.8±0.15 V | 1.2 |  | 7 | ns | S1 p11 |
| 下降时间 | tfA/B | DATxB，VCCA=1.8±0.15 V，VCCB=3.3±0.3 V | 0.2 |  | 4 | ns | S1 p11 |
| 通道输出偏斜 | tSK(O) | VCCA=1.8±0.15 V，VCCB=1.8±0.15 V |  |  | 1 | ns | S1 p11 |
| 通道输出偏斜 | tSK(O) | VCCA=1.8±0.15 V，VCCB=3.3±0.3 V |  |  | 1 | ns | S1 p11 |
| 上升时间 | trA/B | CMDA，VCCA=3.3±0.3 V，VCCB=1.8±0.15 V | 1.4 |  | 4.2 | ns | S1 p12 |
| 上升时间 | trA/B | CMDA，VCCA=3.3±0.3 V，VCCB=3.3±0.3 V | 1.4 |  | 4.2 | ns | S1 p12 |
| 上升时间 | trA/B | CLK-f，VCCA=3.3±0.3 V，VCCB=1.8±0.15 V | 0.5 |  | 1.5 | ns | S1 p12 |
| 上升时间 | trA/B | CLK-f，VCCA=3.3±0.3 V，VCCB=3.3±0.3 V | 0.5 |  | 1.4 | ns | S1 p12 |
| 上升时间 | trA/B | DATxA，VCCA=3.3±0.3 V，VCCB=1.8±0.15 V | 1.4 |  | 3.4 | ns | S1 p12 |
| 上升时间 | trA/B | DATxA，VCCA=3.3±0.3 V，VCCB=3.3±0.3 V | 1.3 |  | 3 | ns | S1 p12 |
| 上升时间 | trA/B | CMDB，VCCA=3.3±0.3 V，VCCB=1.8±0.15 V | 1.4 |  | 6.4 | ns | S1 p12 |
| 上升时间 | trA/B | CMDB，VCCA=3.3±0.3 V，VCCB=3.3±0.3 V | 0.9 |  | 4 | ns | S1 p12 |
| 上升时间 | trA/B | CLKB，VCCA=3.3±0.3 V，VCCB=1.8±0.15 V | 0.6 |  | 5.9 | ns | S1 p12 |
| 上升时间 | trA/B | CLKB，VCCA=3.3±0.3 V，VCCB=3.3±0.3 V | 0.5 |  | 4.4 | ns | S1 p12 |
| 上升时间 | trA/B | DATxB，VCCA=3.3±0.3 V，VCCB=1.8±0.15 V | 1.4 |  | 14 | ns | S1 p12 |
| 上升时间 | trA/B | DATxB，VCCA=3.3±0.3 V，VCCB=3.3±0.3 V | 0.9 |  | 14 | ns | S1 p12 |
| 下降时间 | tfA/B | CMDA，VCCA=3.3±0.3 V，VCCB=1.8±0.15 V | 0.8 |  | 2.3 | ns | S1 p12 |
| 下降时间 | tfA/B | CMDA，VCCA=3.3±0.3 V，VCCB=3.3±0.3 V | 0.8 |  | 2.3 | ns | S1 p12 |
| 下降时间 | tfA/B | CLK-f，VCCA=3.3±0.3 V，VCCB=1.8±0.15 V | 0.4 |  | 1.3 | ns | S1 p12 |
| 下降时间 | tfA/B | CLK-f，VCCA=3.3±0.3 V，VCCB=3.3±0.3 V | 0.4 |  | 1.3 | ns | S1 p12 |
| 下降时间 | tfA/B | DATxA，VCCA=3.3±0.3 V，VCCB=1.8±0.15 V | 0.8 |  | 2.2 | ns | S1 p12 |
| 下降时间 | tfA/B | DATxA，VCCA=3.3±0.3 V，VCCB=3.3±0.3 V | 0.7 |  | 2 | ns | S1 p12 |
| 下降时间 | tfA/B | CMDB，VCCA=3.3±0.3 V，VCCB=1.8±0.15 V | 0.8 |  | 6.2 | ns | S1 p12 |
| 下降时间 | tfA/B | CMDB，VCCA=3.3±0.3 V，VCCB=3.3±0.3 V | 0.8 |  | 5 | ns | S1 p12 |
| 下降时间 | tfA/B | CLKB，VCCA=3.3±0.3 V，VCCB=1.8±0.15 V | 0.6 |  | 7.8 | ns | S1 p12 |
| 下降时间 | tfA/B | CLKB，VCCA=3.3±0.3 V，VCCB=3.3±0.3 V | 0.5 |  | 4.3 | ns | S1 p12 |
| 下降时间 | tfA/B | DATxB，VCCA=3.3±0.3 V，VCCB=1.8±0.15 V | 0.7 |  | 6.8 | ns | S1 p12 |
| 下降时间 | tfA/B | DATxB，VCCA=3.3±0.3 V，VCCB=3.3±0.3 V | 0.6 |  | 5 | ns | S1 p12 |
| 通道输出偏斜 | tSK(O) | VCCA=3.3±0.3 V，VCCB=1.8±0.15 V |  |  | 1 | ns | S1 p12 |
| 通道输出偏斜 | tSK(O) | VCCA=3.3±0.3 V，VCCB=3.3±0.3 V |  |  | 1 | ns | S1 p12 |

用这些数时要注意：

- VCCA=1.2±0.1 V、VCCB=3.3±0.3 V时，时钟最高频率在Timing Requirements写40 MHz，在Switching Characteristics写60 MHz，不能默默合并；两处原值均保留（S1 p7、p10）。
- 原开关表p10另列该条件时钟最大60 MHz；本条时序要求表保留40 MHz。Cpd只有典型，不作为电容保证值（S1 p10、p12、p13）。
- 脚表DAT/CMD内拉为40 kΩ，WP/CD为100 kΩ±30%；应用分压说明却用4 kΩ，不自行统一这两种描述（S1 p3、p20）。
- B数据低输出最后一行原表IOL=300 µA、VCCB=3 V，保留，不改为400 µA。控制输入钳位电流−50 mA原表列MAX（S1 p4、p7）。

## 热特性

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- |
| 结到环境 | RθJA | YFP 20脚 | 71.1 | °C/W | S1 p6 |
| 结到壳顶 | RθJC(top) | YFP 20脚 | 0.5 | °C/W | S1 p6 |
| 结到板 | RθJB | YFP 20脚 | 10.4 | °C/W | S1 p6 |
| 结到顶参数 | ψJT | YFP 20脚 | 2 | °C/W | S1 p6 |
| 结到板参数 | ψJB | YFP 20脚 | 10.4 | °C/W | S1 p6 |

## 静电额定

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- |
| 人体模型 | V(ESD) | JS-001 | ±2500 | V | S1 p4 |
| 带电器件模型 | V(ESD) | JESD22-C101 | ±1500 | V | S1 p4 |
| 机器模型 | V(ESD) | MM | ±250 | V | S1 p4 |

静电警告译文：本器件可能被静电损坏，须采取适当防护；操作或安装不当可能造成性能退化到完全失效（S1 p24）。

## 引脚与处置

YFP 20脚；方向照原表。

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
| --- | --- | --- | --- | --- |
| A1 DAT2A | I/O；主机数据 | 见推荐条件 | 不用的数据输入保持电源或地 | S1 p3、p5 |
| A2 VCCA | Pwr；A端及控制电源 | 见推荐条件 |  | S1 p3、p5 |
| A3 WP | O；机械写保护 | 见推荐条件 | 不用可悬空 | S1 p3、p5 |
| A4 DAT2B | I/O；卡数据 | 见推荐条件 | 不用的数据输入保持电源或地 | S1 p3、p5 |
| B1 DAT3A | I/O；主机数据 | 见推荐条件 | 不用的数据输入保持电源或地 | S1 p3、p5 |
| B2 CD | O；机械卡检测 | 见推荐条件 | 不用可悬空 | S1 p3、p5 |
| B3 VCCB | Pwr；B端电源 | 见推荐条件 |  | S1 p3、p5 |
| B4 DAT3B | I/O；卡数据 | 见推荐条件 | 不用的数据输入保持电源或地 | S1 p3、p5 |
| C1 CMDA | I/O；主机命令 | 见推荐条件 | 不用的数据输入保持电源或地 | S1 p3、p5 |
| C2、C3 GND | —；地 | 见推荐条件 |  | S1 p3、p5 |
| C4 CMDB | I/O；卡命令 | 见推荐条件 | 不用的数据输入保持电源或地 | S1 p3、p5 |
| D1 DAT0A | I/O；主机数据 | 见推荐条件 | 不用的数据输入保持电源或地 | S1 p3、p5 |
| D2 CLKA | I；主机时钟 | 见推荐条件 |  | S1 p3、p5 |
| D3 CLKB | O；卡时钟 | 见推荐条件 |  | S1 p3、p5 |
| D4 DAT0B | I/O；卡数据 | 见推荐条件 | 不用的数据输入保持电源或地 | S1 p3、p5 |
| E1 DAT1A | I/O；主机数据 | 见推荐条件 | 不用的数据输入保持电源或地 | S1 p3、p5 |
| E2 CLK-f | O；反馈时钟 | 见推荐条件 | 不用可悬空 | S1 p3、p5 |
| E3 EN | I；低有效禁止 | 见推荐条件 |  | S1 p3、p5 |
| E4 DAT1B | I/O；卡数据 | 见推荐条件 | 不用的数据输入保持电源或地 | S1 p3、p5 |
| 散热焊盘 | DSBGA 未列独立散热焊盘，未给内部连接或焊接要求 |  |  | S1 p3 |

## 必需外围

电源必须旁路；应用图各电源0.1 µF。EN下拉保持上/掉电高阻，稳定后使能；不需高阻可短接VCCA。未用数据输入保持电源或地。卡侧任何内外下拉不得小于10 kΩ；建议总负载低于50 pF，避免单稳态超时及重触发（S1 p5、p19、p20、p22）。

## 订货型号与封装

YFP为DSBGA，R卷带。

| 订货型号或后缀 | 封装 | 脚数 | 电压或功能档 | 温度范围 | 引脚镀层 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| TXS0206AYFPR / TXS0206AYFPR.B | DSBGA (YFP) | 20 |  | −40～85 °C | SNAGCU | S1 p25 |

## 核对记录

- 2026-11-10：逐页对照原件，工具核对通过，核对 349 个数。
