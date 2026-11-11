# TI ISOW3080

类别：器件参数。
器件：集成隔离 DC-DC 的全双工 RS-485/RS-422 收发器，含 ISOW3080/P、ISOW3086/P
手册：SLLSG02A，2026 年 3 月修订；ADVANCE INFORMATION，预生产资料、可变更。

## 来源

- S1：Datasheet/15_接口与隔离/隔离 RS-485_CAN 收发器/TI - ISOW3080.pdf

页码均为 PDF 文件页序；原件共 40 页。

## 绝对最大值

| 参数 | 符号 | 条件 | 最小 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| 功率转换器电源 | VDD | 对 GND1 | −0.5 | 6 | V | S1 p6 |
| 隔离电源输出 | VISOOUT | 所有版本，对 GND2 | −0.5 | 6 | V | S1 p6 |
| 逻辑电源 | VDDL | 对 GND1 | −0.5 | 6 | V | S1 p6 |
| 总线脚电压 | VBUS | A/B/Y/Z 对 GND2 | −12 | 15 | V | S1 p6 |
| 逻辑 I/O 电压 | VLOGIC_IO | D/DE/RE/R 对 GND1 | −0.5 | 6 | V | S1 p6 |
| 接收输出电流 | IO | R 脚 | −15 | 15 | mA | S1 p6 |
| 结温 | TJ |  | −55 | 150 | °C | S1 p6 |
| 储存温度 | Tstg |  | −65 | 150 | °C | S1 p6 |

## 推荐工作条件

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 逻辑电源 | VDDL |  | 2.25 |  | 5.5 | V | S1 p7 |
| 转换器电源 | VDD | 无 P | 3 |  | 5.5 | V | S1 p7 |
| 转换器电源 | VDD | P | 4.5 |  | 5.5 | V | S1 p7 |
| 功率电源欠压上升 | VDD(UVLO+) |  |  | 2.65 | 2.86 | V | S1 p7 |
| 功率电源欠压下降 | VDD(UVLO−) |  | 2.44 | 2.56 |  | V | S1 p7 |
| 功率电源欠压迟滞 | VHYS1(UVLO) |  | 78 |  |  | mV | S1 p7 |
| 逻辑电源欠压上升 | VDDL(UVLO+) |  |  | 1.95 | 2.24 | V | S1 p7 |
| 逻辑电源欠压下降 | VDDL(UVLO−) |  | 1.6 | 1.78 |  | V | S1 p7 |
| 逻辑电源欠压迟滞 | VHYS2(UVLO) |  | 100 |  |  | mV | S1 p7 |
| 总线输入电压 | VBUS | 单脚或共模，对 GND2 | −7 |  | 12 | V | S1 p7 |
| 输入高电平 | VIH | D/DE/RE | 0.7 × VDDL |  | VDDL | V | S1 p7 |
| 输入低电平 | VIL | D/DE/RE | 0 |  | 0.3 × VDDL | V | S1 p7 |
| 差分接收输入 | VID | A 对 B | −12 |  | 12 | V | S1 p7 |
| 驱动输出电流 | IO(DRV) | Y/Z | −60 |  | 60 | mA | S1 p7 |
| 接收输出电流 | IO | VDDL=4.5 至 5.5 V | −4 |  | 4 | mA | S1 p7 |
| 接收输出电流 | IO | VDDL=3 至 3.6 V | −2 |  | 2 | mA | S1 p7 |
| 接收输出电流 | IO | VDDL=2.25 至 2.75 V | −1 |  | 1 | mA | S1 p7 |
| 差分负载电阻 | RL |  | 54 |  |  | Ω | S1 p7 |
| 信号速率 | 1/tUI | ISOW3080/P |  |  | 500 | kbps | S1 p7 |
| 信号速率 | 1/tUI | ISOW3086/P |  |  | 12 | Mbps | S1 p7 |
| 上电时间 | tpwrup | 隔离输出达设定值 90%，之后可传数据 |  | 2.2 |  | ms | S1 p7 |
| 环境温度 | TA | 无 P，VDD=3 至 3.3 V，无额外输出电流 | −55 |  | 125 | °C | S1 p7 |
| 环境温度 | TA | 无 P，VDD=4.5 至 5.5 V，额外输出 20 mA | −55 |  | 105 | °C | S1 p7 |
| 环境温度 | TA | P，VDD=4.5 至 5.5 V，无额外输出电流 | −55 |  | 105 | °C | S1 p7 |
| 环境温度 | TA | P，VDD=4.5 至 5.5 V，额外输出 20 mA | −55 |  | 85 | °C | S1 p7 |

## 电气特性

按推荐工作条件；电气典型值 VDD=VDDL=3.3 V、TA=25 °C，P 版本时序典型值为 VDD=VDDL=5 V、TA=25 °C；供电电流表另有条件（S1 p11–p17）。“最小”“最大”为手册限值，“典型”不是保证值。

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 隔离电源输出 | VISOOUT | 无 P，DE=GND1，D/RE 悬空 | 3 | 3.3 | 3.6 | V | S1 p11 |
| 隔离电源输出 | VISOOUT | P，DE=GND1，D/RE 悬空 | 4.5 | 5 | 5.5 | V | S1 p11 |
| 接收高电平 | VOH | VDDL=5 V ±10%，IOH=−4 mA，IN=VISOIN（原文符号） | VDDL − 0.4 |  |  | V | S1 p11 |
| 接收低电平 | VOL | VDDL=5 V ±10%，IOL=4 mA，IN=GND2（原文符号） |  |  | 0.4 | V | S1 p11 |
| 接收高电平 | VOH | VDDL=3.3 V ±10%，IOH=−2 mA，IN=VISOIN（原文符号） | VDDL − 0.3 |  |  | V | S1 p11 |
| 接收低电平 | VOL | VDDL=3.3 V ±10%，IOL=2 mA，IN=GND2（原文符号） |  |  | 0.3 | V | S1 p11 |
| 接收高电平 | VOH | VDDL=2.5 V ±10%，IOH=−1 mA，IN=VISOIN（原文符号） | VDDL − 0.2 |  |  | V | S1 p11 |
| 接收低电平 | VOL | VDDL=2.5 V ±10%，IOL=1 mA，IN=GND2（原文符号） |  |  | 0.2 | V | S1 p11 |
| 接收高电平 | VOH | VDDL=5 V ±10%，IOH=−4 mA，VID≥200 mV | VDDL − 0.4 |  |  | V | S1 p12 |
| 接收低电平 | VOL | VDDL=5 V ±10%，IOL=4 mA，VID≤−200 mV |  |  | 0.4 | V | S1 p12 |
| 接收高电平 | VOH | VDDL=3.3 V ±10%，IOH=−2 mA，VID≥200 mV | VDDL − 0.3 |  |  | V | S1 p12 |
| 接收低电平 | VOL | VDDL=3.3 V ±10%，IOL=2 mA，VID≤−200 mV |  |  | 0.3 | V | S1 p12 |
| 接收高电平 | VOH | VDDL=2.5 V ±10%，IOH=−1 mA，VID≥200 mV | VDDL − 0.2 |  |  | V | S1 p12 |
| 接收低电平 | VOL | VDDL=2.5 V ±10%，IOL=1 mA，VID≤−200 mV |  |  | 0.2 | V | S1 p12 |
| 差分输出幅值 | VOD | 无 P：VDD=3 至 3.6 V；P：VDD=4.5 至 5.5 V，空载 | 1.5 |  | VISOOUT | V | S1 p11 |
| 差分输出幅值 | VOD | 无 P，VDD=3 至 3.6 V，RL=60 Ω，−7 V≤VTEST≤12 V，图 7-1 | 1.5 |  | VISOOUT | V | S1 p11 |
| 差分输出幅值 | VOD | 无 P，VDD=3 至 3.6 V，RL=100 Ω，图 7-2 | 2 |  | VISOOUT | V | S1 p11 |
| 差分输出幅值 | VOD | 无 P，VDD=3 至 3.6 V，RL=54 Ω，图 7-2 | 1.5 |  | VISOOUT | V | S1 p11 |
| 差分输出幅值 | VOD | P，VDD=4.5 至 5.5 V，RL=54 Ω，图 7-2 | 2.1 |  | VISOOUT | V | S1 p11 |
| 差分输出幅值 | VOD | P，VDD=4.5 至 5.5 V，RL=100 Ω，图 7-2 | 2.1 |  | VISOOUT | V | S1 p11 |
| 差分输出幅值 | VOD | P，VDD=4.5 至 5.5 V，RL=60 Ω，−7 V≤VTEST≤12 V，图 7-1 | 2.1 |  | VISOOUT | V | S1 p11 |
| 差分输出变化 | ΔVOD | RL=54 Ω 或 100 Ω，图 7-2 | −200 |  | 200 | mV | S1 p11 |
| 输出共模电压 | VOC | RL=54 Ω 或 100 Ω，图 7-2 | 1 | 0.5 × VISOOUT | 3 | V | S1 p11 |
| 稳态共模变化 | ΔVOC(SS) | RL=54 Ω 或 100 Ω，图 7-2 | −200 |  | 200 | mV | S1 p11 |
| 峰峰共模电压 | VOC(PP) | 无 P，RL=54 Ω 或 100 Ω，图 7-2 |  | 400 |  | mV | S1 p11 |
| 驱动短路电流 | IOS | VDE=VDDL，VD=VDDL 或 GND1，Y/Z=−7 至 12 V 或 Y 短 Z，图 7-10 |  | 150 |  | mA | S1 p11 |
| D/DE 输入电流 | II | VD/VDE=0 V 或 VDDL | −25 |  | 25 | µA | S1 p11 |
| 总线输入电流 | II1 | VDE=0，VISOIN=0/3.3/5 V，VA 或 VB=−7 至 12 V，另一个输入=0 V | −100 |  | 125 | µA | S1 p11 |
| 接收上升门限 | VTH+ | VCM=−7 至 12 V，下界参照迟滞脚注 |  | −78 | −20 | mV | S1 p11 |
| 接收下降门限 | VTH− | VCM=−7 至 12 V，上界参照迟滞脚注 | −200 | −141 |  | mV | S1 p11 |
| 接收迟滞 | Vhys | VCM=−7 至 12 V |  | 49 |  | mV | S1 p11 |
| 接收高阻漏电流 | IOZ | VR=0 V 或 VDDL，VRE=VDDL | −1.5 |  | 1.5 | µA | S1 p12 |
| RE 输入电流 | II(RE) | VRE=0 V 或 VDDL | −25 |  | 25 | µA | S1 p12 |
| 转换器电源电流 | IDD | 无 P，VDE=VRE=VD=VDDL，RL=120 Ω，A/B 悬空，VDD=5 V ±10% |  | 51 | 68.5 | mA | S1 p13 |
| 转换器电源电流 | IDD | 无 P，VDE=VRE=VD=VDDL，RL=120 Ω，A/B 悬空，VDD=3.3 V ±10% |  | 67 | 103.5 | mA | S1 p13 |
| 转换器电源电流 | IDD | ISOW3080，VDE=VRE=VDDL，负载 120 Ω 并联 50 pF，D=500 kbps、50% 方波，VDD=5 V ±10% |  | 55 | 82.5 | mA | S1 p13 |
| 转换器电源电流 | IDD | ISOW3080，VDE=VRE=VDDL，负载 100 Ω 并联 50 pF，D=500 kbps、50% 方波，VDD=5 V ±10% |  | 60 | 88 | mA | S1 p13 |
| 转换器电源电流 | IDD | ISOW3080，VDE=VRE=VDDL，负载 54 Ω 并联 50 pF，D=500 kbps、50% 方波，VDD=5 V ±10% |  | 80 | 114.5 | mA | S1 p13 |
| 转换器电源电流 | IDD | ISOW3080，VDE=VRE=VDDL，负载 120 Ω 并联 50 pF，D=500 kbps、50% 方波，VDD=3.3 V ±10% |  | 72 | 124 | mA | S1 p13 |
| 转换器电源电流 | IDD | ISOW3080，VDE=VRE=VDDL，负载 100 Ω 并联 50 pF，D=500 kbps、50% 方波，VDD=3.3 V ±10% |  | 79 | 133 | mA | S1 p13 |
| 转换器电源电流 | IDD | ISOW3080，VDE=VRE=VDDL，负载 54 Ω 并联 50 pF，D=500 kbps、50% 方波，VDD=3.3 V ±10% |  | 107 | 173 | mA | S1 p13 |
| 转换器电源电流 | IDD | ISOW3086，VDE=VRE=VDDL，负载 120 Ω 并联 50 pF，D=12 Mbps、50% 方波，VDD=5 V ±10% |  | 60 | 86 | mA | S1 p13 |
| 转换器电源电流 | IDD | ISOW3086，VDE=VRE=VDDL，负载 100 Ω 并联 50 pF，D=12 Mbps、50% 方波，VDD=5 V ±10% |  | 65 | 92.5 | mA | S1 p13 |
| 转换器电源电流 | IDD | ISOW3086，VDE=VRE=VDDL，负载 54 Ω 并联 50 pF，D=12 Mbps、50% 方波，VDD=5 V ±10% |  | 87 | 120 | mA | S1 p13 |
| 转换器电源电流 | IDD | ISOW3086，VDE=VRE=VDDL，负载 120 Ω 并联 50 pF，D=12 Mbps、50% 方波，VDD=3.3 V ±10% |  | 80 | 130 | mA | S1 p13 |
| 转换器电源电流 | IDD | ISOW3086，VDE=VRE=VDDL，负载 100 Ω 并联 50 pF，D=12 Mbps、50% 方波，VDD=3.3 V ±10% |  | 87 | 140 | mA | S1 p13 |
| 转换器电源电流 | IDD | ISOW3086，VDE=VRE=VDDL，负载 54 Ω 并联 50 pF，D=12 Mbps、50% 方波，VDD=3.3 V ±10% |  | 116 | 182 | mA | S1 p13 |
| 转换器电源电流 | IDD | ISOW3080，VDE=VRE=VD=GND1，Y/Z 带载或空载，A−B=500 kbps、50% 方波，VDD=5 V ±10%，R 负载 15 pF |  | 12 | 19 | mA | S1 p13 |
| 转换器电源电流 | IDD | ISOW3080，VDE=VRE=VD=GND1，Y/Z 带载或空载，A−B=500 kbps、50% 方波，VDD=3.3 V ±10%，R 负载 15 pF |  | 15 | 27.5 | mA | S1 p13 |
| 转换器电源电流 | IDD | ISOW3086，VDE=VRE=VD=GND1，Y/Z 带载或空载，A−B=12 Mbps、50% 方波，VDD=5 V ±10%，R 负载 15 pF |  | 13 | 21.5 | mA | S1 p13 |
| 转换器电源电流 | IDD | ISOW3086，VDE=VRE=VD=GND1，Y/Z 带载或空载，A−B=12 Mbps、50% 方波，VDD=3.3 V ±10%，R 负载 15 pF |  | 17 | 31.5 | mA | S1 p13 |
| 转换器电源电流 | IDD | ISOW3080，VDE=VDDL，VRE=GND1，Y/Z 120 Ω 并联 50 pF，回环，D=500 kbps、50%，VDD=5 V ±10%，R 负载 15 pF |  | 56 | 84.5 | mA | S1 p13 |
| 转换器电源电流 | IDD | ISOW3080，VDE=VDDL，VRE=GND1，Y/Z 120 Ω 并联 50 pF，回环，D=500 kbps、50%，VDD=3.3 V ±10%，R 负载 15 pF |  | 76 | 127.5 | mA | S1 p13 |
| 转换器电源电流 | IDD | ISOW3086，VDE=VDDL，VRE=GND1，Y/Z 120 Ω 并联 50 pF，回环，D=12 Mbps、50%，VDD=5 V ±10%，R 负载 15 pF |  | 63 | 90.5 | mA | S1 p14 |
| 转换器电源电流 | IDD | ISOW3086，VDE=VDDL，VRE=GND1，Y/Z 120 Ω 并联 50 pF，回环，D=12 Mbps、50%，VDD=3.3 V ±10%，R 负载 15 pF |  | 84 | 137 | mA | S1 p14 |
| 逻辑电源电流 | IDDL | 无 P，VDDL=3.3 V ±10%，驱动关闭、接收关闭，VDE=GND1，VRE=VD=VDDL |  | 3.3 | 4.6 | mA | S1 p14 |
| 逻辑电源电流 | IDDL | 无 P，VDDL=3.3 V ±10%，驱动/接收开启，VDE=VD=VDDL，VRE=GND1，回环静态 |  | 5.3 | 6.6 | mA | S1 p14 |
| 逻辑电源电流 | IDDL | 无 P，VDDL=3.3 V ±10%，ISOW3080，VDE=VDDL，VRE=GND1，回环，D=500 kbps、50% 方波 |  | 6.1 | 7.6 | mA | S1 p14 |
| 逻辑电源电流 | IDDL | 无 P，VDDL=3.3 V ±10%，ISOW3086，VDE=VDDL，VRE=GND1，回环，D=12 Mbps、50% 方波 |  | 6.2 | 8 | mA | S1 p14 |
| 转换器电源电流 | IDD | P，VDE=VRE=VD=VDDL，RL=120 Ω，A/B 悬空，VDD=5 V ±10% |  | 93 | 137 | mA | S1 p15 |
| 转换器电源电流 | IDD | ISOW3080P，VDE=VRE=VDDL，负载 120 Ω 并联 50 pF，D=500 kbps、50% 方波，VDD=5 V ±10% |  | 113 | 188 | mA | S1 p15 |
| 转换器电源电流 | IDD | ISOW3080P，VDE=VRE=VDDL，负载 100 Ω 并联 50 pF，D=500 kbps、50% 方波，VDD=5 V ±10% |  | 124 | 201 | mA | S1 p15 |
| 转换器电源电流 | IDD | ISOW3080P，VDE=VRE=VDDL，负载 54 Ω 并联 50 pF，D=500 kbps、50% 方波，VDD=5 V ±10% |  | 167 | 257 | mA | S1 p15 |
| 转换器电源电流 | IDD | ISOW3086P，VDE=VRE=VDDL，负载 120 Ω 并联 50 pF，D=12 Mbps、50% 方波，VDD=5 V ±10% |  | 110 | 169 | mA | S1 p15 |
| 转换器电源电流 | IDD | ISOW3086P，VDE=VRE=VDDL，负载 100 Ω 并联 50 pF，D=12 Mbps、50% 方波，VDD=5 V ±10% |  | 121 | 185 | mA | S1 p15 |
| 转换器电源电流 | IDD | ISOW3086P，VDE=VRE=VDDL，负载 54 Ω 并联 50 pF，D=12 Mbps、50% 方波，VDD=5 V ±10% |  | 168 | 250 | mA | S1 p15 |
| 转换器电源电流 | IDD | ISOW3080P，VDE=VRE=VD=GND1，Y/Z 带载或空载，A−B=500 kbps、50% 方波，VDD=5 V ±10%，R 负载 15 pF |  | 14 | 26 | mA | S1 p15 |
| 转换器电源电流 | IDD | ISOW3086P，VDE=VRE=VD=GND1，Y/Z 带载或空载，A−B=12 Mbps、50% 方波，VDD=5 V ±10%，R 负载 15 pF |  | 18 | 31.5 | mA | S1 p15 |
| 转换器电源电流 | IDD | ISOW3080P，VDE=VDDL，VRE=GND1，Y/Z 120 Ω 并联 50 pF，回环，D=500 kbps、50%，VDD=5 V ±10%，R 负载 15 pF |  | 115 | 191 | mA | S1 p15 |
| 转换器电源电流 | IDD | ISOW3086P，VDE=VDDL，VRE=GND1，Y/Z 120 Ω 并联 50 pF，回环，D=12 Mbps、50%，VDD=5 V ±10%，R 负载 15 pF |  | 115 | 178 | mA | S1 p15 |
| 逻辑电源电流 | IDDL | P，VDDL=3.3 V ±10%（原表如此），驱动关闭、接收关闭，VDE=GND1，VRE=VD=VDDL |  | 3.1 | 4.6 | mA | S1 p15 |
| 逻辑电源电流 | IDDL | P，VDDL=3.3 V ±10%（原表如此），驱动/接收开启，VDE=VD=VDDL，VRE=GND1，回环静态 |  | 4.9 | 6.6 | mA | S1 p15 |
| 逻辑电源电流 | IDDL | P，VDDL=3.3 V ±10%（原表如此），ISOW3080P，VDE=VDDL，VRE=GND1，回环，D=500 kbps、50% 方波 |  | 5.8 | 7.6 | mA | S1 p15 |
| 逻辑电源电流 | IDDL | P，VDDL=3.3 V ±10%（原表如此），ISOW3086P，VDE=VDDL，VRE=GND1，回环，D=12 Mbps、50% 方波 |  | 6.2 | 8 | mA | S1 p15 |
| 驱动上升/下降时间 | tr,tf | ISOW3080，RL=54 Ω，CL=50 pF，图 7-3 | 190 | 270 | 600 | ns | S1 p16 |
| 驱动传播延迟 | tPHL,tPLH | ISOW3080，RL=54 Ω，CL=50 pF，图 7-3 |  | 400 | 610 | ns | S1 p16 |
| 驱动脉宽畸变 | PWD | ISOW3080，RL=54 Ω，CL=50 pF，图 7-3 |  | 6.5 | 40 | ns | S1 p16 |
| 驱动禁止时间 | tPHZ,tPLZ | ISOW3080，RL=110 Ω，CL=50 pF，图 7-5/6 |  | 57 | 200 | ns | S1 p16 |
| 驱动使能时间 | tPZH,tPZL | ISOW3080，RL=110 Ω，CL=50 pF，图 7-5/6 |  | 220 | 600 | ns | S1 p16 |
| 接收上升/下降时间 | tr,tf | ISOW3080，CL=15 pF，图 7-7 |  |  | 5.6 | ns | S1 p16 |
| 接收传播延迟 | tPHL,tPLH | ISOW3080，CL=15 pF，图 7-7 |  | 80 | 175 | ns | S1 p16 |
| 接收脉宽畸变 | PWD | ISOW3080，CL=15 pF，图 7-7 |  | 1.5 | 15 | ns | S1 p16 |
| 接收禁止时间 | tPHZ,tPLZ | ISOW3080，CL=15 pF，1 kΩ，图 7-8/9 |  | 8 | 30 | ns | S1 p16 |
| 接收使能时间 | tPZH,tPZL | ISOW3080，CL=15 pF，1 kΩ，图 7-8/9 |  | 6 | 30 | ns | S1 p16 |
| 驱动上升/下降时间 | tr,tf | ISOW3086，RL=54 Ω，CL=50 pF，图 7-3 | 6 | 15 | 25 | ns | S1 p16 |
| 驱动传播延迟 | tPHL,tPLH | ISOW3086，RL=54 Ω，CL=50 pF，图 7-3 |  | 51 | 125 | ns | S1 p16 |
| 驱动脉宽畸变 | PWD | ISOW3086，RL=54 Ω，CL=50 pF，图 7-3 |  | 2 | 12 | ns | S1 p16 |
| 驱动禁止时间 | tPHZ,tPLZ | ISOW3086，RL=110 Ω，CL=50 pF，图 7-5/6 |  | 31 | 125 | ns | S1 p16 |
| 驱动使能时间 | tPZH,tPZL | ISOW3086，RL=110 Ω，CL=50 pF，图 7-5/6 |  | 34 | 110 | ns | S1 p16 |
| 接收上升/下降时间 | tr,tf | ISOW3086，CL=15 pF，图 7-7 |  |  | 6 | ns | S1 p16 |
| 接收传播延迟 | tPHL,tPLH | ISOW3086，CL=15 pF，图 7-7 |  | 80 | 160 | ns | S1 p16 |
| 接收脉宽畸变 | PWD | ISOW3086，CL=15 pF，图 7-7 |  | 2 | 10 | ns | S1 p16 |
| 接收禁止时间 | tPHZ,tPLZ | ISOW3086，CL=15 pF，1 kΩ，图 7-8/9 |  | 8 | 30 | ns | S1 p16 |
| 接收使能时间 | tPZH,tPZL | ISOW3086，CL=15 pF，1 kΩ，图 7-8/9 |  | 6 | 30 | ns | S1 p16 |
| 驱动上升/下降时间 | tr,tf | ISOW3080P，RL=54 Ω，CL=50 pF，图 7-3 | 200 | 300 | 600 | ns | S1 p17 |
| 驱动传播延迟 | tPHL,tPLH | ISOW3080P，RL=54 Ω，CL=50 pF，图 7-3 |  | 350 | 610 | ns | S1 p17 |
| 驱动脉宽畸变 | PWD | ISOW3080P，RL=54 Ω，CL=50 pF，图 7-3 |  | 4.5 | 40 | ns | S1 p17 |
| 驱动禁止时间 | tPHZ,tPLZ | ISOW3080P，RL=110 Ω，CL=50 pF，图 7-5/6 |  | 54 | 200 | ns | S1 p17 |
| 驱动使能时间 | tPZH,tPZL | ISOW3080P，RL=110 Ω，CL=50 pF，图 7-5/6 |  | 160 | 600 | ns | S1 p17 |
| 接收上升/下降时间 | tr,tf | ISOW3080P，CL=15 pF，图 7-7 |  |  | 6 | ns | S1 p17 |
| 接收传播延迟 | tPHL,tPLH | ISOW3080P，CL=15 pF，图 7-7 |  | 80 | 175 | ns | S1 p17 |
| 接收脉宽畸变 | PWD | ISOW3080P，CL=15 pF，图 7-7 |  | 2.5 | 20 | ns | S1 p17 |
| 接收禁止时间 | tPHZ,tPLZ | ISOW3080P，CL=15 pF，1 kΩ，图 7-8/9 |  | 8 | 30 | ns | S1 p17 |
| 接收使能时间 | tPZH,tPZL | ISOW3080P，CL=15 pF，1 kΩ，图 7-8/9 |  | 6 | 30 | ns | S1 p17 |
| 驱动上升/下降时间 | tr,tf | ISOW3086P，RL=54 Ω，CL=50 pF，图 7-3 | 4 | 8.5 | 18 | ns | S1 p17 |
| 驱动传播延迟 | tPHL,tPLH | ISOW3086P，RL=54 Ω，CL=50 pF，图 7-3 |  | 37 | 125 | ns | S1 p17 |
| 驱动脉宽畸变 | PWD | ISOW3086P，RL=54 Ω，CL=50 pF，图 7-3 |  | 1.5 | 10 | ns | S1 p17 |
| 驱动禁止时间 | tPHZ,tPLZ | ISOW3086P，RL=110 Ω，CL=50 pF，图 7-5/6 |  | 26 | 125 | ns | S1 p17 |
| 驱动使能时间 | tPZH,tPZL | ISOW3086P，RL=110 Ω，CL=50 pF，图 7-5/6 |  | 33 | 150 | ns | S1 p17 |
| 接收上升/下降时间 | tr,tf | ISOW3086P，CL=15 pF，图 7-7 |  |  | 6 | ns | S1 p17 |
| 接收传播延迟 | tPHL,tPLH | ISOW3086P，CL=15 pF，图 7-7 |  | 80 | 160 | ns | S1 p17 |
| 接收脉宽畸变 | PWD | ISOW3086P，CL=15 pF，图 7-7 |  | 2.5 | 10 | ns | S1 p17 |
| 接收禁止时间 | tPHZ,tPLZ | ISOW3086P，CL=15 pF，1 kΩ，图 7-8/9 |  | 8 | 30 | ns | S1 p17 |
| 接收使能时间 | tPZH,tPZL | ISOW3086P，CL=15 pF，1 kΩ，图 7-8/9 |  | 6 | 30 | ns | S1 p17 |
| 最大功耗 | PD | ISOW3080，VDD=3.6 V，VDDL=5.5 V，TJ=150 °C，Y/Z 54 Ω 并联 50 pF，Y→A、Z→B 回环，R 15 pF，D=250 kHz、50% 方波，DE=VDDL，RE=GND1 |  |  | 624 | mW | S1 p8 |
| 最大功耗 | PD1 | ISOW3080，VDD=3.6 V，VDDL=5.5 V，TJ=150 °C，Y/Z 54 Ω 并联 50 pF，Y→A、Z→B 回环，R 15 pF，D=250 kHz、50% 方波，DE=VDDL，RE=GND1 |  |  | 339 | mW | S1 p8 |
| 最大功耗 | PD2 | ISOW3080，VDD=3.6 V，VDDL=5.5 V，TJ=150 °C，Y/Z 54 Ω 并联 50 pF，Y→A、Z→B 回环，R 15 pF，D=250 kHz、50% 方波，DE=VDDL，RE=GND1 |  |  | 285 | mW | S1 p8 |
| 最大功耗 | PD | ISOW3086，VDD=3.6 V，VDDL=5.5 V，TJ=150 °C，Y/Z 54 Ω 并联 50 pF，Y→A、Z→B 回环，R 15 pF，D=6 MHz、50% 方波，DE=VDDL，RE=GND1 |  |  | 624 | mW | S1 p8 |
| 最大功耗 | PD1 | ISOW3086，VDD=3.6 V，VDDL=5.5 V，TJ=150 °C，Y/Z 54 Ω 并联 50 pF，Y→A、Z→B 回环，R 15 pF，D=6 MHz、50% 方波，DE=VDDL，RE=GND1 |  |  | 339 | mW | S1 p8 |
| 最大功耗 | PD2 | ISOW3086，VDD=3.6 V，VDDL=5.5 V，TJ=150 °C，Y/Z 54 Ω 并联 50 pF，Y→A、Z→B 回环，R 15 pF，D=6 MHz、50% 方波，DE=VDDL，RE=GND1 |  |  | 285 | mW | S1 p8 |
| 最大功耗 | PD | ISOW3080P，VDD=VDDL=5.5 V，TJ=150 °C，Y/Z 54 Ω 并联 50 pF，Y→A、Z→B 回环，R 15 pF，D=250 kHz、50% 方波，DE=VDDL，RE=GND1 |  |  | 1420 | mW | S1 p8 |
| 最大功耗 | PD1 | ISOW3080P，VDD=VDDL=5.5 V，TJ=150 °C，Y/Z 54 Ω 并联 50 pF，Y→A、Z→B 回环，R 15 pF，D=250 kHz、50% 方波，DE=VDDL，RE=GND1 |  |  | 710 | mW | S1 p8 |
| 最大功耗 | PD2 | ISOW3080P，VDD=VDDL=5.5 V，TJ=150 °C，Y/Z 54 Ω 并联 50 pF，Y→A、Z→B 回环，R 15 pF，D=250 kHz、50% 方波，DE=VDDL，RE=GND1 |  |  | 710 | mW | S1 p8 |
| 最大功耗 | PD | ISOW3086P，VDD=VDDL=5.5 V，TJ=150 °C，Y/Z 54 Ω 并联 50 pF，Y→A、Z→B 回环，R 15 pF，D=6 MHz、50% 方波，DE=VDDL，RE=GND1 |  |  | 1420 | mW | S1 p8 |
| 最大功耗 | PD1 | ISOW3086P，VDD=VDDL=5.5 V，TJ=150 °C，Y/Z 54 Ω 并联 50 pF，Y→A、Z→B 回环，R 15 pF，D=6 MHz、50% 方波，DE=VDDL，RE=GND1 |  |  | 710 | mW | S1 p8 |
| 最大功耗 | PD2 | ISOW3086P，VDD=VDDL=5.5 V，TJ=150 °C，Y/Z 54 Ω 并联 50 pF，Y→A、Z→B 回环，R 15 pF，D=6 MHz、50% 方波，DE=VDDL，RE=GND1 |  |  | 710 | mW | S1 p8 |
| 间隙 | CLR | 两侧最短空气距离 | >8 |  |  | mm | S1 p9 |
| 爬电 | CPG | 两侧最短表面距离 | >8 |  |  | mm | S1 p9 |
| 内部绝缘距离 | DTI | 电容信号隔离 | >17 |  |  | µm | S1 p9 |
| 内部绝缘距离 | DTI | 变压器电源隔离 | >100 |  |  | µm | S1 p9 |
| 耐电痕指数 | CTI | IEC60112 | >600 |  |  | V | S1 p9 |
| 重复峰值隔离电压 | VIORM | 双极性交流 |  |  | 1500 | VPK | S1 p9 |
| 隔离工作电压 | VIOWM | 正弦交流，TDDB |  |  | 1061 | VRMS | S1 p9 |
| 隔离工作电压 | VIOWM | 直流 |  |  | 1500 | VDC | S1 p9 |
| 瞬态隔离电压 | VIOTM | VTEST=VIOTM，60 s 资格；1.2×VIOTM，1 s 生产测试 |  |  | 7071 | VPK | S1 p9 |
| 冲击电压 | VIMP | 空气中，1.2/50 µs |  |  | 8000 | VPK | S1 p9 |
| 浪涌隔离电压 | VIOSM | 油中，1.2/50 µs，≥1.3×VIMP |  |  | 10400 | VPK | S1 p9 |
| 隔离耐压 | VISO | 5000 VRMS、60 s 资格；6000 VRMS、1 s 生产测试 |  |  | 5000 | VRMS | S1 p9 |
| 绝缘电阻 | RIO | VIO=500 V，TA=25 °C，两侧分别短接所有脚 | >10¹² |  |  | Ω | S1 p9 |
| 绝缘电阻 | RIO | VIO=500 V，TA=100 至 125 °C，两侧分别短接所有脚 | >10¹¹ |  |  | Ω | S1 p9 |
| 绝缘电阻 | RIO | VIO=500 V，TS=150 °C，两侧分别短接所有脚 | >10⁹ |  |  | Ω | S1 p9 |
| 局部放电视在电荷 | qpd | 方法 a，安全测试分组 2/3 后，Vini=VIOTM、60 s，Vpd=1.2×VIORM、10 s |  |  | ≤5 | pC | S1 p9 |
| 局部放电视在电荷 | qpd | 方法 a，环境测试分组 1 后，Vini=VIOTM、60 s，Vpd=1.6×VIORM、10 s |  |  | ≤5 | pC | S1 p9 |
| 局部放电视在电荷 | qpd | 方法 b1 生产/预处理，Vini=1.2×VIOTM、1 s，Vpd=1.875×VIORM、1 s |  |  | ≤5 | pC | S1 p9 |
| 安全电流 | IS | RθJA=65.5 °C/W，VI=5.5 V，TJ=150 °C，TA=25 °C |  |  | 345 | mA | S1 p10 |
| 安全电流 | IS | RθJA=65.5 °C/W，VI=3.6 V，TJ=150 °C，TA=25 °C |  |  | 525 | mA | S1 p10 |
| 安全功耗 | PS | RθJA=65.5 °C/W，TJ=150 °C，TA=25 °C |  |  | 1900 | mW | S1 p10 |
| 安全温度 | TS |  |  |  | 150 | °C | S1 p10 |
| 正文短路电流限制 | IOS | 第 8.6.2 节，外部电源误接或总线冲突，方向限值 |  |  | ±250 | mA | S1 p23 |
| 热关断温度 | TJ | 正文典型值 |  | 165 |  | °C | S1 p23 |
| 热恢复温度 | TJ | 正文典型值 |  | 155 |  | °C | S1 p23 |

隔离电容在原表只标为 Value，未区分典型或保证限值：

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
|---|---|---|---|---|---|
| 隔离电容 | CIO | VIO=0.4×sin(2πft)，f=1 MHz，两侧分别短接所有脚 | 3.5 | pF | S1 p9 |

用这些数时要注意：

- 此份原件为预生产资料；虽然首页写已获隔离资格，认证表仍写 Certificate planned，不能认定认证已完成（S1 p1、p10）。
- 上电 2.2 ms、正文 10 µF 时 2.5 ms、热关断/恢复、接收迟滞、共模输出峰峰值及规格表 IOS=150 mA 只有典型值。正文另写短路最大 ±250 mA，两者口径须区分（S1 p7、p11、p23）。
- VTH+ 下界和 VTH− 上界以脚注相互约束：同一条件 VTH+ 比 VTH− 至少高 Vhys；但 Vhys 数值列只给典型，不能把典型迟滞直接当全温下限（S1 p11、p12）。
- 规格条件沿用 VISOIN、IN 等未在引脚表定义的符号。P 版供电电流表头 VDD=VDDL=4.5 至 5.5 V，而 IDDL 行又写 VDDL=3.3 V±10%，原件条件有冲突，已原样记录（S1 p5、p11、p15）。
- 推荐环境温度随 VDD、P 后缀、是否额外供电变化，不能只用首页最高温度。额外电流仅在 VDD=5 V±10% 可用（S1 p7）。
- 隔离耐压/冲击/持续工作电压与安全限流不可互换；隔离栅参数试验把同侧所有脚短接，安全限值依赖环境温度及规定测试板（S1 p9、p10）。
- 手册有 CMTI 测试图但电气表未列 CMTI 保证数字，不从宣传或曲线推定（S1 p11、p12、p19）。
- 功耗表 ISOW3080P 条件末尾误写 ISOW3086P；参数行按所属 ISOW3080P 保留，须向厂家确认该条件（S1 p8）。

## 热特性

以下为手册热特性表的单列数值，原表没有区分最小、典型、最大，不另行赋予保证边界。

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
|---|---|---|---|---|---|
| 结到环境热阻 | RθJA | DWE | 65.5 | °C/W | S1 p8 |
| 结到顶壳热阻 | RθJC(top) | DWE | 31.7 | °C/W | S1 p8 |
| 结到板热阻 | RθJB | DWE | 36.4 | °C/W | S1 p8 |
| 结到顶热参数 | ΨJT | DWE | 20.2 | °C/W | S1 p8 |
| 结到板热参数 | ΨJB | DWE | 34.9 | °C/W | S1 p8 |

## 静电额定

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
|---|---|---|---|---|---|
| 人体模型 | V(ESD) | HBM，ANSI/ESDA/JEDEC JS-001；除总线引脚外 | ±2000 | V | S1 p6 |
| 人体模型 | V(ESD) | HBM，ANSI/ESDA/JEDEC JS-001；总线引脚对 GND2 | ±16000 | V | S1 p6 |
| 带电器件模型 | V(ESD) | CDM，JEDEC JESD22-C101 | ±1500 | V | S1 p6 |

手册静电警告（译文）：本集成电路可能被静电损坏，操作时应采取适当防护；不遵守正确的操作和安装程序可能造成损坏。损害可能从轻微性能退化到完全失效；精密集成电路很小的参数变化就可能使其不再满足公布的规格（S1 p28）。

## 引脚与处置

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
| --- | --- | --- | --- | --- |
| VDD（2） | 隔离转换器输入 | 无 P 推荐 3 至 5.5 V；P 推荐 4.5 至 5.5 V | 必须供电并去耦 | S1 p5、p7、p23 |
| VDDL（7） | 侧一逻辑电源 | 推荐 2.25 至 5.5 V | 必须供电并去耦 | S1 p5、p7、p23 |
| VISOOUT（15） | 侧二隔离电源输出 | 无 P 为 3 至 3.6 V；P 为 4.5 至 5.5 V | 接旁路电容，额外负载遵守温度限制 | S1 p5、p7、p11、p26 |
| GND1（1、8）/GND2（9、16） | 两侧地，图列两个同侧地脚 |  | 各接本侧地 | S1 p5 |
| D（6） | 驱动数据输入 | 绝对最大 −0.5 至 6 V | 手册未规定闲置接法 | S1 p5、p6 |
| DE（5） | 高有效驱动使能，内部下拉 | 绝对最大 −0.5 至 6 V | 悬空时驱动关闭 | S1 p5、p6 |
| RE（4） | 低有效接收使能，内部上拉 | 绝对最大 −0.5 至 6 V | 悬空时接收缓冲关闭 | S1 p5、p6 |
| R（3） | 接收数据输出 | 绝对最大 −0.5 至 6 V | 未单列闲置接法 | S1 p5、p6 |
| Y/Z（11/12） | 非反相/反相驱动输出 | 绝对最大 −12 至 15 V；工作总线 −7 至 12 V | 按总线接线 | S1 p5、p6、p7 |
| A/B（14/13） | 非反相/反相接收输入 | 绝对最大 −12 至 15 V；工作总线 −7 至 12 V | 开路/短路/空闲有失效安全功能 | S1 p5、p6、p7、p23 |
| NC（10） | 图示未连接 |  | 引脚表未单列处置 | S1 p5 |

## 必需外围

- VDD 与 VISOOUT 因峰值电流较高，各建议至少 10 µF 大容量旁路；图中两侧还各有 0.1 µF，就近接相应地。更大电容约 100 µF 可减小纹波，建议电容直流耐压大于 25 V 以减少偏压降容；这些是应用建议而非精度保证（S1 p26）。
- VDD 和 VDDL 必须同时有效，任一低于欠压门限会关断信号与电源转换器（S1 p23）。
- 总线两端按电缆特性阻抗匹配终端电阻，手册未规定通用唯一阻值。半双工时 Y 接 A、Z 接 B、DE 与 RE 联动，全双工使用两对线（S1 p26）。

## 订货型号与封装

附录订货型号带 X，DWE 对应 SOIC；P 等功能差异见本节原说明。镀层栏原文为“Call TI”，未给出材料（S1 p36）。

| 订货型号或后缀 | 封装 | 脚数 | 电压或功能档 | 温度范围 | 引脚镀层 | 来源 |
|---|---|---|---|---|---|---|
| XISOW3080DWER | SOIC (DWE) | 16 |  | -55～125 °C | Call TI | S1 p36 |
| XISOW3080PDWER | SOIC (DWE) | 16 |  | -55～125 °C | Call TI | S1 p36 |
| XISOW3086DWER | SOIC (DWE) | 16 |  | -55～125 °C | Call TI | S1 p36 |
| XISOW3086PDWER | SOIC (DWE) | 16 |  | -55～125 °C | Call TI | S1 p36 |

ISOW3080/P 为 500 kbps，ISOW3086/P 为 12 Mbps。无 P 隔离输出标称 3.3 V，P 为 5 V、适用 PROFIBUS，并改变 VDD 与温度条件；时序和供电电流按型号分别列出（S1 p3、p7、p13–p17）。

## 核对记录

- 2026-11-09：逐页对照原件，工具核对通过，核对 353 个数。
