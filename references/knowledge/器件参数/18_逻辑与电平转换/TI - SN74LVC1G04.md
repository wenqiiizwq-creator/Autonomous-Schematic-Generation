# TI SN74LVC1G04

类别：器件参数。
器件：单路反相器。
手册：SCES214AF，2025-10。

## 来源

- S1：Datasheet/18_逻辑与电平转换/标准逻辑门/TI - SN74LVC1G04.pdf

页码均为 PDF 文件页序。

## 绝对最大值

| 参数 | 符号 | 条件 | 最小 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| 电源/输入/掉电输出电压 | VCC、VI、VO |  | −0.5 | 6.5 | V | S1 p4 |
| 活动输出电压 | VO |  | −0.5 | VCC + 0.5 | V | S1 p4 |
| 输入/输出钳位电流 | IIK、IOK | VI或VO<0 |  | −50 | mA | S1 p4 |
| 连续输出电流 | IO |  |  | ±50 | mA | S1 p4 |
| 电源/地电流 |  |  |  | ±100 | mA | S1 p4 |
| 储存温度 | Tstg |  | −65 | 150 | °C | S1 p4 |

## 推荐工作条件

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 供电 | VCC | 正常工作 | 1.65 |  | 5.5 | V | S1 p5 |
| 保持供电 | VCC | 仅数据保持 | 1.5 |  |  | V | S1 p5 |
| 输入电压 | VI |  | 0 |  | 5.5 | V | S1 p5 |
| 输出电压 | VO |  | 0 |  | VCC | V | S1 p5 |
| 环境温度 | TA |  | −40 |  | 125 | °C | S1 p5 |
| 输入高电平 | VIH | VCC=1.65～1.95 V | 0.65 × VCC |  |  | V | S1 p5 |
| 输入低电平 | VIL | VCC=1.65～1.95 V |  |  | 0.35 × VCC | V | S1 p5 |
| 输入高电平 | VIH | VCC=2.3～2.7 V | 1.7 |  |  | V | S1 p5 |
| 输入低电平 | VIL | VCC=2.3～2.7 V |  |  | 0.7 | V | S1 p5 |
| 输入高电平 | VIH | VCC=3～3.6 V | 2 |  |  | V | S1 p5 |
| 输入低电平 | VIL | VCC=3～3.6 V |  |  | 0.8 | V | S1 p5 |
| 输入高电平 | VIH | VCC=4.5～5.5 V | 0.7 × VCC |  |  | V | S1 p5 |
| 输入低电平 | VIL | VCC=4.5～5.5 V |  |  | 0.3 × VCC | V | S1 p5 |
| 高/低输出电流 | IOH/IOL | VCC=1.65 V，绝对值 |  |  | 4 | mA | S1 p5 |
| 高/低输出电流 | IOH/IOL | VCC=2.3 V，绝对值 |  |  | 8 | mA | S1 p5 |
| 高/低输出电流 | IOH/IOL | VCC=3 V，绝对值 |  |  | 16 / 24 | mA | S1 p5 |
| 高/低输出电流 | IOH/IOL | VCC=4.5 V，绝对值 |  |  | 32 | mA | S1 p5 |
| 输入边沿速率 | Δt/Δv | VCC=1.8±0.15或2.5±0.2 V |  |  | 20 | ns/V | S1 p5 |
| 输入边沿速率 | Δt/Δv | VCC=3.3±0.3 V |  |  | 10 | ns/V | S1 p5 |
| 输入边沿速率 | Δt/Δv | VCC=5±0.5 V |  |  | 5 | ns/V | S1 p5 |

## 电气特性

测试条件按各行；最小、最大为手册限值，典型值不是保证值。

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 输出高电平 | VOH | IOH=−100 µA，VCC=1.65～5.5 V | VCC − 0.1 |  |  | V | S1 p6 |
| 输出低电平 | VOL | IOL=100 µA，VCC=1.65～5.5 V |  |  | 0.1 | V | S1 p6 |
| 输出高电平 | VOH | VCC=1.65 V，IOH=−4 mA | 1.2 |  |  | V | S1 p6 |
| 输出低电平 | VOL | VCC=1.65 V，IOL=4 mA |  |  | 0.45 | V | S1 p6 |
| 输出高电平 | VOH | VCC=2.3 V，IOH=−8 mA | 1.9 |  |  | V | S1 p6 |
| 输出低电平 | VOL | VCC=2.3 V，IOL=8 mA |  |  | 0.3 | V | S1 p6 |
| 输出高电平 | VOH | VCC=3 V，IOH=−16 mA | 2.4 |  |  | V | S1 p6 |
| 输出低电平 | VOL | VCC=3 V，IOL=16 mA |  |  | 0.4 | V | S1 p6 |
| 输出高电平 | VOH | VCC=3 V，IOH=−24 mA | 2.3 |  |  | V | S1 p6 |
| 输出低电平 | VOL | VCC=3 V，IOL=24 mA |  |  | 0.55 | V | S1 p6 |
| 输出高电平 | VOH | VCC=4.5 V，IOH=−32 mA | 3.8 |  |  | V | S1 p6 |
| 输出低电平 | VOL | VCC=4.5 V，IOL=32 mA |  |  | 0.55 | V | S1 p6 |
| 输入漏电 | II | VI=5.5 V或地，VCC=0～5.5 V |  |  | ±5 | µA | S1 p6 |
| 掉电漏电 | Ioff | VI或VO=5.5 V，VCC=0 |  |  | ±10 | µA | S1 p6 |
| 静态电流 | ICC | VI=5.5 V或地，IO=0，VCC=1.65～5.5 V |  |  | 10 | µA | S1 p6 |
| 增量电流 | ΔICC | 一个输入VCC−0.6 V，其余VCC或地，VCC=3～5.5 V |  |  | 500 | µA | S1 p6 |
| 输入电容 | Ci | VCC=3.3 V，VI=VCC或地 |  | 3.5 |  | pF | S1 p6 |
| 传播延时 | tpd | VCC=1.8±0.15 V，CL=15 pF，负载按图6-1/6-2；两温度档相同 | 2 |  | 6.4 | ns | S1 p6、p7 |
| 传播延时 | tpd | VCC=2.5±0.2 V，CL=15 pF，负载按图6-1/6-2；两温度档相同 | 1 |  | 4.2 | ns | S1 p6、p7 |
| 传播延时 | tpd | VCC=3.3±0.3 V，CL=15 pF，负载按图6-1/6-2；两温度档相同 | 0.7 |  | 3.3 | ns | S1 p6、p7 |
| 传播延时 | tpd | VCC=5±0.5 V，CL=15 pF，负载按图6-1/6-2；两温度档相同 | 0.7 |  | 3.1 | ns | S1 p6、p7 |
| 传播延时 | tpd | VCC=1.8±0.15 V，CL=30或50 pF，负载按图6-1/6-2；两温度档相同 | 3 |  | 7.5 | ns | S1 p6、p7 |
| 传播延时 | tpd | VCC=2.5±0.2 V，CL=30或50 pF，负载按图6-1/6-2；两温度档相同 | 1.4 |  | 5.2 | ns | S1 p6、p7 |
| 传播延时 | tpd | VCC=3.3±0.3 V，CL=30或50 pF，负载按图6-1/6-2；两温度档相同 | 1 |  | 4.2 | ns | S1 p6、p7 |
| 传播延时 | tpd | VCC=5±0.5 V，CL=30或50 pF，负载按图6-1/6-2；两温度档相同 | 1 |  | 3.7 | ns | S1 p6、p7 |

用这些数时要注意：

- 电气表−40～85 °C及−40～125 °C限值相同。输入电容、功耗电容只有典型值（S1 p6、p7）。
- DPW脚表/订货附录写5脚，热表写4脚；YZP图把A1标为DNU而脚表写NC，B2的图标也不完整。保留各自来源，不将DNU当作可用连接（S1 p3、p5、p16）。

## 热特性

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- |
| 结到环境热阻 | RθJA | DBV / DCK / DRL / DRY / YZP / DPW | 357.1 / 371.0 / 243 / 439 / 130 / 340 | °C/W | S1 p5 |
| 结到壳顶热阻 | RθJC(top) | DBV / DCK / DRL / DRY / YZP / DPW | 263.7 / 297.5 / 78 / 277 / 54 / 215 | °C/W | S1 p5 |
| 结到板热阻 | RθJB | DBV / DCK / DRL / DRY / YZP / DPW | 264.4 / 258.6 / 78 / 271 / 51 / 294 | °C/W | S1 p5 |
| 结到顶热参数 | ψJT | DBV / DCK / DRL / DRY / YZP / DPW | 195.6 / 195.6 / 10 / 84 / 1 / 41 | °C/W | S1 p5 |
| 结到板热参数 | ψJB | DBV / DCK / DRL / DRY / YZP / DPW | 262.2 / 256.2 / 77 / 271 / 50 / 294 | °C/W | S1 p5 |
| 结到壳底热阻 | RθJC(bot) | DBV / DCK / DRL / DRY / YZP / DPW |  / / / / /250 | °C/W | S1 p5 |

## 静电额定

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- |
| 人体模型 | V(ESD) | HBM JS-001 | ±2000 | V | S1 p4 |
| 带电器件模型 | V(ESD) | JESD22-C101 | ±1000 | V | S1 p4 |

手册未给出单独的静电敏感警告。

## 引脚与处置

### DBV / DCK / DRL / DPW

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
| --- | --- | --- | --- | --- |
| 1 NC | 无内部连接 |  |  | S1 p3、p5 |
| 2 A | I，输入 |  | 不用的输入接有效逻辑电平 | S1 p3、p5 |
| 3 GND | 地 |  |  | S1 p3、p5 |
| 4 Y | O，输出 |  |  | S1 p3、p5 |
| 5 VCC | 电源 |  |  | S1 p3、p5 |

### DSF / DRY

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
| --- | --- | --- | --- | --- |
| 1 NC | 无内部连接 |  |  | S1 p3、p5 |
| 2 A | I，输入 |  | 不用的输入接有效逻辑电平 | S1 p3、p5 |
| 3 GND | 地 |  |  | S1 p3、p5 |
| 4 Y | O，输出 |  |  | S1 p3、p5 |
| 5 NC | 无内部连接 |  |  | S1 p3、p5 |
| 6 VCC | 电源 |  |  | S1 p3、p5 |

### YZP

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
| --- | --- | --- | --- | --- |
| A1 NC/DNU | 图中DNU，脚表NC |  | 不得使用 | S1 p3、p5 |
| A2 VCC | 电源 |  |  | S1 p3、p5 |
| B1 A | I，输入 |  | 不用的输入接有效逻辑电平 | S1 p3、p5 |
| B2 NC | 无内部连接 |  |  | S1 p3、p5 |
| C1 GND | 地 |  |  | S1 p3、p5 |
| C2 Y | O，输出 |  |  | S1 p3、p5 |

### YZV

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
| --- | --- | --- | --- | --- |
| A1 A | I，输入 |  | 不用的输入接有效逻辑电平 | S1 p3、p5 |
| A2 VCC | 电源 |  |  | S1 p3、p5 |
| B1 GND | 地 |  |  | S1 p3、p5 |
| B2 Y | O，输出 |  |  | S1 p3、p5 |

散热焊盘：手册未给出散热焊盘及其内部连接、焊接规定。


## 必需外围

- 电源旁路0.1 µF，可与1 µF并联，靠近供电脚（S1 p12）。

## 订货型号与封装

手册列出的型号与封装如下；空格表示手册未给出，不从型号自行推算。

| 订货型号或后缀 | 封装 | 脚数 | 电压或功能档 | 温度范围 | 引脚镀层 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| SN74LVC1G04DBVR | SOT-23 (DBV) | 5 |  | -40～125 °C | SN | S1 p15 |
| SN74LVC1G04DBVR.A | SOT-23 (DBV) | 5 |  | -40～125 °C | SN | S1 p15 |
| SN74LVC1G04DBVR.B | SOT-23 (DBV) | 5 |  | -40～125 °C | SN | S1 p15 |
| SN74LVC1G04DBVRE4 | SOT-23 (DBV) | 5 |  | -40～125 °C | SN | S1 p15 |
| SN74LVC1G04DBVRG4.A | SOT-23 (DBV) | 5 |  | -40～125 °C | SN | S1 p15 |
| SN74LVC1G04DBVRG4.B | SOT-23 (DBV) | 5 |  | -40～125 °C | SN | S1 p15 |
| SN74LVC1G04DBVT | SOT-23 (DBV) | 5 |  | -40～125 °C | SN | S1 p15 |
| SN74LVC1G04DBVT.B | SOT-23 (DBV) | 5 |  | -40～125 °C | SN | S1 p15 |
| SN74LVC1G04DBVTE4 | SOT-23 (DBV) | 5 |  | -40～125 °C | SN | S1 p15 |
| SN74LVC1G04DBVTG4 | SOT-23 (DBV) | 5 |  | -40～125 °C | SN | S1 p15 |
| SN74LVC1G04DBVTG4.B | SOT-23 (DBV) | 5 |  | -40～125 °C | SN | S1 p15 |
| SN74LVC1G04DCKR | SC70 (DCK) | 5 |  | -40～125 °C | SN | S1 p16 |
| SN74LVC1G04DCKR.A | SC70 (DCK) | 5 |  | -40～125 °C | SN | S1 p16 |
| SN74LVC1G04DCKR.B | SC70 (DCK) | 5 |  | -40～125 °C | SN | S1 p16 |
| SN74LVC1G04DCKRE4 | SC70 (DCK) | 5 |  | -40～125 °C | SN | S1 p16 |
| SN74LVC1G04DCKRE4.B | SC70 (DCK) | 5 |  | -40～125 °C | SN | S1 p16 |
| SN74LVC1G04DCKRG4 | SC70 (DCK) | 5 |  | -40～125 °C | SN | S1 p16 |
| SN74LVC1G04DCKRG4.B | SC70 (DCK) | 5 |  | -40～125 °C | SN | S1 p16 |
| SN74LVC1G04DCKT | SC70 (DCK) | 5 |  | -40～125 °C | SN | S1 p16 |
| SN74LVC1G04DCKT.B | SC70 (DCK) | 5 |  | -40～125 °C | SN | S1 p16 |
| SN74LVC1G04DCKTE4 | SC70 (DCK) | 5 |  | -40～125 °C | SN | S1 p16 |
| SN74LVC1G04DCKTE4.B | SC70 (DCK) | 5 |  | -40～125 °C | SN | S1 p16 |
| SN74LVC1G04DCKTG4 | SC70 (DCK) | 5 |  | -40～125 °C | SN | S1 p16 |
| SN74LVC1G04DCKTG4.B | SC70 (DCK) | 5 |  | -40～125 °C | SN | S1 p16 |
| SN74LVC1G04DPWR | X2SON (DPW) | 5 |  | -40～125 °C | SN | S1 p16 |
| SN74LVC1G04DPWR.B | X2SON (DPW) | 5 |  | -40～125 °C | SN | S1 p16 |
| SN74LVC1G04DRLR | SOT-5X3 (DRL) | 5 |  | -40～125 °C | SN | S1 p16 |
| SN74LVC1G04DRLR.B | SOT-5X3 (DRL) | 5 |  | -40～125 °C | SN | S1 p17 |
| SN74LVC1G04DRY2 | SON (DRY) | 6 |  | -40～125 °C | SN | S1 p17 |
| SN74LVC1G04DRY2.B | SON (DRY) | 6 |  | -40～125 °C | SN | S1 p17 |
| SN74LVC1G04DRYR | SON (DRY) | 6 |  | -40～125 °C | SN | S1 p17 |
| SN74LVC1G04DRYR.B | SON (DRY) | 6 |  | -40～125 °C | SN | S1 p17 |
| SN74LVC1G04DRYRG4 | SON (DRY) | 6 |  | -40～125 °C | SN | S1 p17 |
| SN74LVC1G04DSF2 | SON (DSF) | 6 |  | -40～125 °C | SN | S1 p17 |
| SN74LVC1G04DSF2.B | SON (DSF) | 6 |  | -40～125 °C | SN | S1 p17 |
| SN74LVC1G04DSF2G4 | SON (DSF) | 6 |  | -40～125 °C | SN | S1 p17 |
| SN74LVC1G04DSF2G4.B | SON (DSF) | 6 |  | -40～125 °C | SN | S1 p17 |
| SN74LVC1G04DSFR | SON (DSF) | 6 |  | -40～125 °C | SN | S1 p17 |
| SN74LVC1G04DSFR.B | SON (DSF) | 6 |  | -40～125 °C | SN | S1 p17 |
| SN74LVC1G04YZPR | DSBGA (YZP) | 5 |  | -40～85 °C | SN | S1 p17 |
| SN74LVC1G04YZPR.B | DSBGA (YZP) | 5 |  | -40～85 °C | SN | S1 p17 |
| SN74LVC1G04YZVR | DSBGA (YZV) | 4 |  | -40～85 °C | SN | S1 p17 |
| SN74LVC1G04YZVR.B | DSBGA (YZV) | 4 |  | -40～85 °C | SN | S1 p17 |



## 核对记录

- 2026-11-10：工具核对通过，核对了 252 个数。
