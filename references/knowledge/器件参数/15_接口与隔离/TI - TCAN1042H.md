# TI TCAN1042H

类别：器件参数。
器件：故障保护 CAN/CAN FD 收发器，H/HG/HV/HGV
手册：SLLSES7D，2021 年 10 月修订。

## 来源

- S1：Datasheet/15_接口与隔离/CAN_LIN收发器/TI - TCAN1042H.pdf

页码均为 PDF 文件页序；原件共 41 页。

## 绝对最大值

| 参数 | 符号 | 条件 | 最小 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| 总线电源 | VCC |  | −0.3 | 7 | V | S1 p6 |
| 逻辑电源 | VIO | 仅 V 后缀 | −0.3 | 7 | V | S1 p6 |
| 总线引脚电压 | VBUS | H 后缀 CANH/CANL | −70 | 70 | V | S1 p6 |
| 逻辑输入电压 | V(Logic_Input) | TXD、S；原表同时要求 VI≤VIO+0.3 | −0.3 | 7 | V | S1 p6 |
| 逻辑输出电压 | V(Logic_Output) | RXD；原表同时要求 VI≤VIO+0.3 | −0.3 | 7 | V | S1 p6 |
| 接收输出电流 | IO(RXD) |  | −8 | 8 | mA | S1 p6 |
| 虚拟结温 | TJ |  | −55 | 150 | °C | S1 p6 |
| 储存温度 | TSTG |  | −65 | 150 | °C | S1 p6 |

## 推荐工作条件

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 总线电源 | VCC |  | 4.5 |  | 5.5 | V | S1 p8 |
| 逻辑电源 | VIO | V 后缀 | 3 |  | 5.5 | V | S1 p8 |
| 接收高输出电流 | IOH(RXD) |  | −2 |  |  | mA | S1 p8 |
| 接收低输出电流 | IOL(RXD) |  |  |  | 2 | mA | S1 p8 |

## 电气特性

推荐电源条件下 TA=−55 至 125 °C；典型值为 25 °C，VCC=5 V、VIO=5 V（适用时）、RL=60 Ω（S1 p9–p12）。“最小”“最大”为手册限值，“典型”不是保证值。

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 电源特性 | ICC | 正常显性，TXD=0，STB=0，RL=60 Ω，CL/RCM 开路 |  | 40 | 70 | mA | S1 p9 |
| 电源特性 | ICC | 正常显性，TXD=0，STB=0，RL=50 Ω，CL/RCM 开路 |  | 45 | 80 | mA | S1 p9 |
| 电源特性 | ICC | 正常显性故障，TXD=0，STB=0，CANH=−12 V，RL/CL/RCM 开路 |  |  | 180 | mA | S1 p9 |
| 电源特性 | ICC | 正常隐性，TXD=VCC 或 VIO，STB=0，RL=50 Ω，CL/RCM 开路 |  | 1.5 | 2.5 | mA | S1 p9 |
| 电源特性 | ICC | V 后缀待机，TXD=STB=VIO，RL=50 Ω，CL/RCM 开路，VCC 不必供电 |  | 0.5 | 5 | µA | S1 p9 |
| 电源特性 | ICC | 无 V 后缀待机，TXD=STB=VCC，RL=50 Ω，CL/RCM 开路 |  |  | 22 | µA | S1 p9 |
| 电源特性 | IIO | 正常模式，RXD 悬空，TXD=STB=0 或 5.5 V |  | 90 | 300 | µA | S1 p9 |
| 电源特性 | IIO | 待机模式，RXD 悬空，TXD=STB=VIO，VCC=0 或 5.5 V |  | 12 | 17 | µA | S1 p9 |
| 电源特性 | UVVCC | VCC 上升 |  | 4.2 | 4.4 | V | S1 p9 |
| 电源特性 | UVVCC | VCC 下降 | 3.8 | 4.0 | 4.25 | V | S1 p9 |
| 电源特性 | VHYS(UVVCC) | VCC 欠压迟滞 |  | 200 |  | mV | S1 p9 |
| 电源特性 | UVVIO | V 后缀，VIO 欠压 | 1.3 |  | 2.75 | V | S1 p9 |
| 电源特性 | VHYS(UVVIO) | V 后缀，VIO 欠压迟滞 |  | 80 |  | mV | S1 p9 |
| 输入高门限 | VIH | STB，V 后缀 | 0.7 × VIO |  |  | V | S1 p9 |
| 输入低门限 | VIL | STB，V 后缀 |  |  | 0.3 × VIO | V | S1 p9 |
| 输入高门限 | VIH | STB，无 V 后缀 | 2 |  |  | V | S1 p9 |
| 输入低门限 | VIL | STB，无 V 后缀 |  |  | 0.8 | V | S1 p9 |
| 输入漏电流 | IIH | STB，STB=VCC=VIO=5.5 V | −2 |  | 2 | µA | S1 p9 |
| 输入漏电流 | IIL | STB，STB=0 V，VCC=VIO=5.5 V | −20 | 0 | −2 | µA | S1 p9 |
| 断电输入漏电流 | Ilkg(OFF) | STB=5.5 V，VCC=VIO=0 V | −1 | 0 | 1 | µA | S1 p9 |
| 输入高门限 | VIH | TXD，V 后缀 | 0.7 × VIO |  |  | V | S1 p9 |
| 输入低门限 | VIL | TXD，V 后缀 |  |  | 0.3 × VIO | V | S1 p9 |
| 输入高门限 | VIH | TXD，无 V 后缀 | 2 |  |  | V | S1 p9 |
| 输入低门限 | VIL | TXD，无 V 后缀 |  |  | 0.8 | V | S1 p9 |
| 输入漏电流 | IIH | TXD，TXD=VCC=VIO=5.5 V | −2.5 | 0 | 1 | µA | S1 p9 |
| 输入漏电流 | IIL | TXD，TXD=0 V，VCC=VIO=5.5 V | −100 | −25 | −7 | µA | S1 p9 |
| 断电输入漏电流 | Ilkg(OFF) | TXD=5.5 V，VCC=VIO=0 V | −1 | 0 | 1 | µA | S1 p9 |
| TXD 输入电容 | CI | VIN=0.4×sin(2×π×2×10^6×t)+2.5 V |  | 5 |  | pF | S1 p9 |
| RXD 高电平 | VOH | V 后缀，IO=−2 mA | 0.8 × VIO |  |  | V | S1 p10 |
| RXD 高电平 | VOH | 无 V 后缀，IO=−2 mA | 4 | 4.6 |  | V | S1 p10 |
| RXD 低电平 | VOL | V 后缀，IO=2 mA |  |  | 0.2 × VIO | V | S1 p10 |
| RXD 低电平 | VOL | 无 V 后缀，IO=2 mA |  | 0.2 | 0.4 | V | S1 p10 |
| RXD 断电漏电流 | Ilkg(OFF) | RXD=5.5 V，VCC=VIO=0 V | −1 | 0 | 1 | µA | S1 p10 |
| 显性 CANH 输出 | VO(DOM) | TXD=STB=0，50 Ω≤RL≤65 Ω，CL/RCM 开路 | 2.75 |  | 4.5 | V | S1 p10 |
| 显性 CANL 输出 | VO(DOM) | 同上 | 0.5 |  | 2.25 | V | S1 p10 |
| 隐性总线输出 | VO(REC) | CANH/CANL，TXD=VCC 或 VIO，VIO=VCC，STB=0，RL/RCM 开路 | 2 | 0.5 × VCC | 3 | V | S1 p10 |
| 待机 CANH 输出 | VO(STB) | STB=VIO，RL/RCM 开路 | −0.1 | 0 | 0.1 | V | S1 p10 |
| 待机 CANL 输出 | VO(STB) | 同上 | −0.1 | 0 | 0.1 | V | S1 p10 |
| 待机差分输出 | VO(STB) | CANH−CANL，同上 | −0.2 | 0 | 0.2 | V | S1 p10 |
| 显性差分输出 | VOD(DOM) | TXD=STB=0，45 Ω≤RL<50 Ω，CL/RCM 开路 | 1.4 |  | 3 | V | S1 p10 |
| 显性差分输出 | VOD(DOM) | TXD=STB=0，50 Ω≤RL≤65 Ω，CL/RCM 开路 | 1.5 |  | 3 | V | S1 p10 |
| 显性差分输出 | VOD(DOM) | TXD=STB=0，RL=2240 Ω，CL/RCM 开路 | 1.5 |  | 5 | V | S1 p10 |
| 隐性差分输出 | VOD(REC) | TXD=VCC，STB=0，RL=60 Ω，CL/RCM 开路 | −120 |  | 12 | mV | S1 p10 |
| 隐性差分输出 | VOD(REC) | TXD=VCC，STB=0，RL/CL/RCM 开路 | −50 |  | 50 | mV | S1 p10 |
| 输出对称性 | VSYM | (CANH+CANL)/VCC，STB=0，Rterm=60 Ω，Csplit=4.7 nF，CL/RCM 开路，TXD=250 kHz、1 MHz | 0.9 |  | 1.1 | V/V | S1 p10 |
| 直流输出对称性 | VSYM_DC | VCC−CANH−CANL，STB=0，RL=60 Ω，CL/RCM 开路 | −0.4 |  | 0.4 | V | S1 p10 |
| CANH 显性短路电流 | IOS(SS_DOM) | STB=TXD=0，CANH=−5 至 40 V，CANL 开路 | −100 |  |  | mA | S1 p10 |
| CANL 显性短路电流 | IOS(SS_DOM) | STB=TXD=0，CANL=−5 至 40 V，CANH 开路 |  |  | 100 | mA | S1 p10 |
| 隐性短路电流 | IOS(SS_REC) | STB=0，TXD=VCC，CANH=CANL=VBUS，−27 V≤VBUS≤32 V | −5 |  | 5 | mA | S1 p10 |
| 正常共模范围 | VCM | STB=0 | −30 |  | 30 | V | S1 p11 |
| 正常上升门限 | VIT+ | STB=0，−20 V≤VCM≤20 V |  |  | 900 | mV | S1 p11 |
| 正常下降门限 | VIT− | STB=0，−20 V≤VCM≤20 V | 500 |  |  | mV | S1 p11 |
| 正常上升门限 | VIT+ | STB=0，−30 V≤VCM≤30 V |  |  | 1000 | mV | S1 p11 |
| 正常下降门限 | VIT− | STB=0，−30 V≤VCM≤30 V | 400 |  |  | mV | S1 p11 |
| 正常接收迟滞 | VHYS | STB=0 |  | 120 |  | mV | S1 p11 |
| 待机共模范围 | VCM | V 后缀，STB=VIO，VIO=4.5 至 5.5 V | −12 |  | 12 | V | S1 p11 |
| 待机共模范围 | VCM | V 后缀，STB=VIO，VIO=3.0 至 4.5 V | −2 |  | 7 | V | S1 p11 |
| 待机共模范围 | VCM | 无 V 后缀，STB=VCC | −12 |  | 12 | V | S1 p11 |
| 待机接收门限 | VIT(STANDBY) | STB=VCC 或 VIO | 400 |  | 1150 | mV | S1 p11 |
| 断电总线漏电流 | ILKG(IOFF) | CANH=CANL=5 V，VCC=VIO=0 V |  |  | 4.8 | µA | S1 p11 |
| 总线对地输入电容 | CI | CANH 或 CANL，TXD=VCC，VIO=VCC |  | 24 | 30 | pF | S1 p11 |
| 总线差分电容 | CID | TXD=VCC，VIO=VCC |  | 12 | 15 | pF | S1 p11 |
| 差分输入电阻 | RID | TXD=VCC=VIO=5 V，STB=0，VCM=−30 至 30 V | 30 |  | 80 | kΩ | S1 p11 |
| 对地输入电阻 | RIN | CANH 或 CANL，同上 | 15 |  | 40 | kΩ | S1 p11 |
| 输入电阻匹配 | RIN(M) | [1−RIN(CANH)/RIN(CANL)]×100%，CANH=CANL=5 V | −2 |  | 2 | % | S1 p11 |
| 隐性到显性环路延迟 | tPROP(LOOP1) | STB=0，RL=60 Ω，CL=100 pF，CL(RXD)=15 pF |  | 100 | 160 | ns | S1 p12 |
| 显性到隐性环路延迟 | tPROP(LOOP2) | 同上 |  | 110 | 175 | ns | S1 p12 |
| 模式切换时间 | tMODE | 正常与待机之间，图 8-3 |  | 9 | 45 | µs | S1 p12 |
| 有效唤醒滤波时间 | tWK_FILTER |  | 0.5 |  | 1.85 | µs | S1 p12 |
| 驱动隐性延迟 | tpHR | STB=0，RL=60 Ω，CL=100 pF，RCM 开路 |  | 75 |  | ns | S1 p12 |
| 驱动显性延迟 | tpLD | 同上 |  | 55 |  | ns | S1 p12 |
| 驱动脉冲偏差 | tsk(p) | 同上 |  | 20 |  | ns | S1 p12 |
| 差分上升时间 | tR | 同上 |  | 45 |  | ns | S1 p12 |
| 差分下降时间 | tF | 同上 |  | 45 |  | ns | S1 p12 |
| TXD 显性超时 | tTXD_DTO | STB=0，RL=60 Ω，CL 开路 | 1.2 |  | 3.8 | ms | S1 p12 |
| 接收隐性延迟 | tpRH | STB=0，CL(RXD)=15 pF |  | 65 |  | ns | S1 p12 |
| 接收显性延迟 | tpDL | 同上 |  | 50 |  | ns | S1 p12 |
| RXD 上升时间 | tR | 同上 |  | 10 |  | ns | S1 p12 |
| RXD 下降时间 | tF | 同上 |  | 10 |  | ns | S1 p12 |
| FD 位宽/接收对称性 | tBIT(BUS) | 所有型号，tBIT(TXD)=500 ns，STB=0，RL=60 Ω，CL=100 pF，CL(RXD)=15 pF | 435 |  | 530 | ns | S1 p12 |
| FD 位宽/接收对称性 | tBIT(RXD) | 所有型号，tBIT(TXD)=500 ns，STB=0，RL=60 Ω，CL=100 pF，CL(RXD)=15 pF | 400 |  | 550 | ns | S1 p12 |
| FD 位宽/接收对称性 | ΔtREC | 所有型号，tBIT(TXD)=500 ns，STB=0，RL=60 Ω，CL=100 pF，CL(RXD)=15 pF | −65 |  | 40 | ns | S1 p12 |
| FD 位宽/接收对称性 | tBIT(BUS) | 仅 G 后缀，tBIT(TXD)=200 ns，STB=0，RL=60 Ω，CL=100 pF，CL(RXD)=15 pF | 155 |  | 210 | ns | S1 p12 |
| FD 位宽/接收对称性 | tBIT(RXD) | 仅 G 后缀，tBIT(TXD)=200 ns，STB=0，RL=60 Ω，CL=100 pF，CL(RXD)=15 pF | 120 |  | 220 | ns | S1 p12 |
| FD 位宽/接收对称性 | ΔtREC | 仅 G 后缀，tBIT(TXD)=200 ns，STB=0，RL=60 Ω，CL=100 pF，CL(RXD)=15 pF | −45 |  | 15 | ns | S1 p12 |

用这些数时要注意：

- 接收迟滞、独立驱动/接收传播延迟及边沿时间只有典型值；完整环路、位宽、唤醒滤波与显性超时给出限值（S1 p11、p12）。
- 逻辑脚绝对最大值表写所有型号都要求 VI≤VIO+0.3，但无 V 型号没有 VIO，原文对无 V 型号参考电源的表达不完整；不要据此给无 V 型号虚构 VIO 脚（S1 p5、p6）。
- STB 低电平输入电流的典型 0 µA 与负数上下限不在同一代数区间，原表照录；需按输入上拉方向解释，不自行改数（S1 p9）。
- 待机共模范围比正常模式小；±70 V 是绝对最大总线故障耐受，不是正常接收共模范围（S1 p6、p11）。
- 热关断表没有给保证上下限；热特性来自规定 JEDEC 模拟板/冷板条件（S1 p8）。

## 热特性

以下为手册热特性表的单列数值，原表没有区分最小、典型、最大，不另行赋予保证边界。

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
|---|---|---|---|---|---|
| 结到环境热阻 | RθJA | D，热表单列数值；非保证边界 | 105.8 | °C/W | S1 p8 |
| 结到环境热阻 | RθJA | DRB，热表单列数值；非保证边界 | 48.3 | °C/W | S1 p8 |
| 结到板热阻 | RθJB | D，热表单列数值；非保证边界 | 46.8 | °C/W | S1 p8 |
| 结到板热阻 | RθJB | DRB，热表单列数值；非保证边界 | 17.2 | °C/W | S1 p8 |
| 结到顶壳热阻 | RθJC(TOP) | D，热表单列数值；非保证边界 | 48.3 | °C/W | S1 p8 |
| 结到顶壳热阻 | RθJC(TOP) | DRB，热表单列数值；非保证边界 | 37.6 | °C/W | S1 p8 |
| 结到顶热参数 | ΨJT | D，热表单列数值；非保证边界 | 8.7 | °C/W | S1 p8 |
| 结到顶热参数 | ΨJT | DRB，热表单列数值；非保证边界 | 1.8 | °C/W | S1 p8 |
| 结到板热参数 | ΨJB | D，热表单列数值；非保证边界 | 46.2 | °C/W | S1 p8 |
| 结到板热参数 | ΨJB | DRB，热表单列数值；非保证边界 | 17.1 | °C/W | S1 p8 |
| 热关断温度 | TTSD | D，热表单列数值；非保证边界 | 170 | °C | S1 p8 |
| 热关断温度 | TTSD | DRB，热表单列数值；非保证边界 | 170 | °C | S1 p8 |
| 热关断迟滞 | TTSD_HYS | D，热表单列数值；非保证边界 | 5 | °C | S1 p8 |
| 热关断迟滞 | TTSD_HYS | DRB，热表单列数值；非保证边界 | 5 | °C | S1 p8 |

## 静电额定

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
|---|---|---|---|---|---|
| 人体模型 |  | HBM；D（SOIC）、DRB（VSON）；所有端子 | ±6000 | V | S1 p6 |
| 人体模型 |  | HBM；D（SOIC）、DRB（VSON）；CANH、CANL 对 GND | ±16000 | V | S1 p6 |
| 带电器件模型 |  | CDM；D（SOIC）、DRB（VSON）；所有端子 | ±1500 | V | S1 p6 |

手册静电警告（译文）：本集成电路可能被静电损坏，操作时应采取适当防护；不遵守正确的操作和安装程序可能造成损坏。损害可能从轻微性能退化到完全失效；精密集成电路很小的参数变化就可能使其不再满足公布的规格（S1 p32）。

## 引脚与处置

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
| --- | --- | --- | --- | --- |
| TXD（1） | 低为显性，高为隐性 | 绝对最大 −0.3 至 7 V，另有电源轨限制 | 开漏控制器必须外接上拉；闲置不可让总线持续显性 | S1 p5、p6、p30 |
| GND（2）、DRB 热焊盘 | 地与可接地散热面 |  | GND 接地，热焊盘可接地改善散热 | S1 p5 |
| VCC（3） | 总线电源 | 推荐 4.5 至 5.5 V | 接稳定电源与旁路 | S1 p5、p8、p29 |
| RXD（4） | 接收输出 | 绝对最大 −0.3 至 7 V，另有电源轨限制 | 手册未单列 | S1 p5、p6 |
| NC/VIO（5） | 无 V 为 NC；有 V 为逻辑电源 | VIO 推荐 3 至 5.5 V | NC 可悬空或接现有网络，VIO 须供电旁路 | S1 p5、p8、p30 |
| CANL/CANH（6/7） | 总线 | H 后缀绝对最大 ±70 V | 按总线网络连接 | S1 p5、p6 |
| STB（8） | 高有效待机 | 逻辑输入限值同 TXD | 仅正常模式时可下拉至地 | S1 p5、p6、p30 |
| Thermal pad（DRB） | 可连接 GND 以优化散热；引脚说明未规定必须焊接 |  | 可接 GND | S1 p5 |

## 必需外围

- VCC 主电源附近建议 4.7 µF 储能，VCC 和适用的 VIO 各就近 0.1 µF 旁路（典型容值）（S1 p29）。
- 总线两端各用与特性阻抗相等的终端；手册典型 CAN 线为 120 Ω，因此每端 120 Ω，不能每个节点都加终端。开漏主机驱动 TXD 时上拉为必需，未给通用阻值（S1 p27、p30）。

## 订货型号与封装

D 对应 SOIC，G、V 的功能差异见本节原说明。下表为当前 S1 附录实际列出的代表行；正文另有 DRB 封装，但该附录未列对应完整订货型号（S1 p5、p33）。

| 订货型号或后缀 | 封装 | 脚数 | 电压或功能档 | 温度范围 | 引脚镀层 | 来源 |
|---|---|---|---|---|---|---|
| TCAN1042HDR | SOIC (D) | 8 |  | -55～125 °C | NIPDAU | S1 p33 |
| TCAN1042HGDR | SOIC (D) | 8 |  | -55～125 °C | NIPDAU | S1 p33 |
| TCAN1042HGVD | SOIC (D) | 8 |  | -55～125 °C | NIPDAU | S1 p33 |
| TCAN1042HVDR | SOIC (D) | 8 |  | -55～125 °C | NIPDAU | S1 p33 |

其余见 S1 p33。

G 后缀支持至 5 Mbps，非 G 支持至 2 Mbps；V 后缀带独立 VIO 并改变逻辑门限和 RXD 电平；H 后缀总线故障保护为 ±70 V。本手册标题列 H、HG、HV、HGV，不能把一般系列介绍中的非 H ±58 V 当作这些型号额定值（S1 p1、p5、p6、p9–p12）。

## 核对记录

- 2026-11-09：逐页对照原件，工具核对通过，核对 202 个数。
