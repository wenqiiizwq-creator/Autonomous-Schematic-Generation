# TI PCA9306

类别：器件参数。
器件：双向I²C/SMBus无源电平转换开关。
手册：SCPS113O，2023-09。

## 来源

- S1：Datasheet/15_接口与隔离/I2C_SPI接口/TI - PCA9306.pdf

页码均为 PDF 文件页序。

## 绝对最大值

| 参数 | 符号 | 条件 | 最小 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| 参考电压 | VREF1、VREF2 |  | −0.5 | 7 | V | S1 p5 |
| 输入及I/O电压 | VI、VI/O |  | −0.5 | 7 | V | S1 p5 |
| 连续通道电流 |  |  |  | 128 | mA | S1 p5 |
| 输入钳位电流 | IIK | VI<0 |  | −50 | mA | S1 p5 |
| 结温 | Tj(max) |  |  | 125 | °C | S1 p5 |
| 储存温度 | Tstg |  | −65 | 150 | °C | S1 p5 |

## 推荐工作条件

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| I/O电压 | VI/O | SCL1、SDA1、SCL2、SDA2 | 0 |  | 5.5 | V | S1 p5 |
| 参考电压 | VREF1、VREF2 |  | 0 |  | 5.5 | V | S1 p5 |
| 使能电压 | EN |  | 0 |  | 5.5 | V | S1 p5 |
| 导通电流 | IPASS |  |  |  | 64 | mA | S1 p5 |
| 环境温度 | TA |  | −40 |  | 85 | °C | S1 p5 |

## 电气特性

测试条件按各行；最小、最大为手册限值，典型值不是保证值。

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 输入钳位电压 | VIK | II=−18 mA，EN=0 | −1.2 |  | 0 | V | S1 p6 |
| 输入漏电 | IIH | VI=5 V，EN=0 |  |  | 5 | µA | S1 p6 |
| 使能输入电容 | Ci(EN) | VI=3 V或0 |  | 11 |  | pF | S1 p6 |
| 关断电容 | Cio(off) | SCLn、SDAn，VO=3 V或0，EN=0 |  | 4 | 6 | pF | S1 p6 |
| 导通电容 | Cio(on) | SCLn、SDAn，VO=3 V或0，EN=3 V |  | 10.5 | 12.5 | pF | S1 p6 |
| 导通电阻 | RON | SCLn、SDAn，VI=0，IO=64 mA，EN=4.5 V |  | 3.5 | 5.5 | Ω | S1 p6 |
| 导通电阻 | RON | SCLn、SDAn，VI=0，IO=64 mA，EN=3 V |  | 4.7 | 7 | Ω | S1 p6 |
| 导通电阻 | RON | SCLn、SDAn，VI=0，IO=64 mA，EN=2.3 V |  | 6.3 | 9.5 | Ω | S1 p6 |
| 导通电阻 | RON | SCLn、SDAn，VI=0，IO=15 mA，EN=1.5 V |  | 25.5 | 32 | Ω | S1 p6 |
| 导通电阻 | RON | SCLn、SDAn，VI=2.4 V，IO=15 mA，EN=4.5 V | 1 | 6 | 15 | Ω | S1 p6 |
| 导通电阻 | RON | SCLn、SDAn，VI=2.4 V，IO=15 mA，EN=3 V | 20 | 60 | 140 | Ω | S1 p6 |
| 导通电阻 | RON | SCLn、SDAn，VI=1.7 V，IO=15 mA，EN=2.3 V | 20 | 60 | 140 | Ω | S1 p6 |
| 上升传播延时 | tPLH | EN=3.3 V，降压，CL=50 pF，VIL=0，VM=1.15 V，VIH=3.3 V | 0 |  | 0.8 | ns | S1 p7 |
| 下降传播延时 | tPHL | EN=3.3 V，降压，CL=50 pF，VIL=0，VM=1.15 V，VIH=3.3 V，YZT、DQE | 0 |  | 1.2 | ns | S1 p7 |
| 下降传播延时 | tPHL | EN=3.3 V，降压，CL=50 pF，VIL=0，VM=1.15 V，VIH=3.3 V，DCU、DCT | 0 |  | 1.2 | ns | S1 p7 |
| 上升传播延时 | tPLH | EN=3.3 V，降压，CL=30 pF，VIL=0，VM=1.15 V，VIH=3.3 V | 0 |  | 0.6 | ns | S1 p7 |
| 下降传播延时 | tPHL | EN=3.3 V，降压，CL=30 pF，VIL=0，VM=1.15 V，VIH=3.3 V，YZT、DQE | 0 |  | 1 | ns | S1 p7 |
| 下降传播延时 | tPHL | EN=3.3 V，降压，CL=30 pF，VIL=0，VM=1.15 V，VIH=3.3 V，DCU、DCT | 0 |  | 1 | ns | S1 p7 |
| 上升传播延时 | tPLH | EN=3.3 V，降压，CL=15 pF，VIL=0，VM=1.15 V，VIH=3.3 V | 0 |  | 0.3 | ns | S1 p7 |
| 下降传播延时 | tPHL | EN=3.3 V，降压，CL=15 pF，VIL=0，VM=1.15 V，VIH=3.3 V，YZT、DQE | 0 |  | 0.5 | ns | S1 p7 |
| 下降传播延时 | tPHL | EN=3.3 V，降压，CL=15 pF，VIL=0，VM=1.15 V，VIH=3.3 V，DCU、DCT | 0 |  | 0.75 | ns | S1 p7 |
| 上升传播延时 | tPLH | EN=2.5 V，降压，CL=50 pF，VIL=0，VM=0.75 V，VIH=3.3 V | 0 |  | 1 | ns | S1 p7 |
| 下降传播延时 | tPHL | EN=2.5 V，降压，CL=50 pF，VIL=0，VM=0.75 V，VIH=3.3 V，YZT、DQE | 0 |  | 1.3 | ns | S1 p7 |
| 下降传播延时 | tPHL | EN=2.5 V，降压，CL=50 pF，VIL=0，VM=0.75 V，VIH=3.3 V，DCU、DCT | 0 |  | 1.3 | ns | S1 p7 |
| 上升传播延时 | tPLH | EN=2.5 V，降压，CL=30 pF，VIL=0，VM=0.75 V，VIH=3.3 V | 0 |  | 0.7 | ns | S1 p7 |
| 下降传播延时 | tPHL | EN=2.5 V，降压，CL=30 pF，VIL=0，VM=0.75 V，VIH=3.3 V，YZT、DQE | 0 |  | 1 | ns | S1 p7 |
| 下降传播延时 | tPHL | EN=2.5 V，降压，CL=30 pF，VIL=0，VM=0.75 V，VIH=3.3 V，DCU、DCT | 0 |  | 1 | ns | S1 p7 |
| 上升传播延时 | tPLH | EN=2.5 V，降压，CL=15 pF，VIL=0，VM=0.75 V，VIH=3.3 V | 0 |  | 0.4 | ns | S1 p7 |
| 下降传播延时 | tPHL | EN=2.5 V，降压，CL=15 pF，VIL=0，VM=0.75 V，VIH=3.3 V，YZT、DQE | 0 |  | 0.6 | ns | S1 p7 |
| 下降传播延时 | tPHL | EN=2.5 V，降压，CL=15 pF，VIL=0，VM=0.75 V，VIH=3.3 V，DCU、DCT | 0 |  | 0.75 | ns | S1 p7 |
| 上升传播延时 | tPLH | EN=3.3 V，升压，CL=50 pF，VIL=0，VM=1.15 V，VIH=2.3 V，VT=3.3 V，RL=300 Ω | 0 |  | 0.9 | ns | S1 p7 |
| 下降传播延时 | tPHL | EN=3.3 V，升压，CL=50 pF，VIL=0，VM=1.15 V，VIH=2.3 V，VT=3.3 V，RL=300 Ω，YZT、DQE | 0 |  | 1.4 | ns | S1 p7 |
| 下降传播延时 | tPHL | EN=3.3 V，升压，CL=50 pF，VIL=0，VM=1.15 V，VIH=2.3 V，VT=3.3 V，RL=300 Ω，DCU、DCT | 0 |  | 1.7 | ns | S1 p7 |
| 上升传播延时 | tPLH | EN=3.3 V，升压，CL=30 pF，VIL=0，VM=1.15 V，VIH=2.3 V，VT=3.3 V，RL=300 Ω | 0 |  | 0.6 | ns | S1 p7 |
| 下降传播延时 | tPHL | EN=3.3 V，升压，CL=30 pF，VIL=0，VM=1.15 V，VIH=2.3 V，VT=3.3 V，RL=300 Ω，YZT、DQE | 0 |  | 1.1 | ns | S1 p7 |
| 下降传播延时 | tPHL | EN=3.3 V，升压，CL=30 pF，VIL=0，VM=1.15 V，VIH=2.3 V，VT=3.3 V，RL=300 Ω，DCU、DCT | 0 |  | 1.4 | ns | S1 p7 |
| 上升传播延时 | tPLH | EN=3.3 V，升压，CL=15 pF，VIL=0，VM=1.15 V，VIH=2.3 V，VT=3.3 V，RL=300 Ω | 0 |  | 0.4 | ns | S1 p7 |
| 下降传播延时 | tPHL | EN=3.3 V，升压，CL=15 pF，VIL=0，VM=1.15 V，VIH=2.3 V，VT=3.3 V，RL=300 Ω，YZT、DQE | 0 |  | 0.7 | ns | S1 p7 |
| 下降传播延时 | tPHL | EN=3.3 V，升压，CL=15 pF，VIL=0，VM=1.15 V，VIH=2.3 V，VT=3.3 V，RL=300 Ω，DCU、DCT | 0 |  | 1.0 | ns | S1 p7 |
| 上升传播延时 | tPLH | EN=2.5 V，升压，CL=50 pF，VIL=0，VM=0.75 V，VIH=2.3 V，VT=3.3 V，RL=300 Ω | 0 |  | 1 | ns | S1 p7 |
| 下降传播延时 | tPHL | EN=2.5 V，升压，CL=50 pF，VIL=0，VM=0.75 V，VIH=2.3 V，VT=3.3 V，RL=300 Ω，YZT、DQE | 0 |  | 1.3 | ns | S1 p7 |
| 下降传播延时 | tPHL | EN=2.5 V，升压，CL=50 pF，VIL=0，VM=0.75 V，VIH=2.3 V，VT=3.3 V，RL=300 Ω，DCU、DCT | 0 |  | 2.1 | ns | S1 p7 |
| 上升传播延时 | tPLH | EN=2.5 V，升压，CL=30 pF，VIL=0，VM=0.75 V，VIH=2.3 V，VT=3.3 V，RL=300 Ω | 0 |  | 0.6 | ns | S1 p7 |
| 下降传播延时 | tPHL | EN=2.5 V，升压，CL=30 pF，VIL=0，VM=0.75 V，VIH=2.3 V，VT=3.3 V，RL=300 Ω，YZT、DQE | 0 |  | 1.3 | ns | S1 p7 |
| 下降传播延时 | tPHL | EN=2.5 V，升压，CL=30 pF，VIL=0，VM=0.75 V，VIH=2.3 V，VT=3.3 V，RL=300 Ω，DCU、DCT | 0 |  | 1.7 | ns | S1 p7 |
| 上升传播延时 | tPLH | EN=2.5 V，升压，CL=15 pF，VIL=0，VM=0.75 V，VIH=2.3 V，VT=3.3 V，RL=300 Ω | 0 |  | 0.4 | ns | S1 p7 |
| 下降传播延时 | tPHL | EN=2.5 V，升压，CL=15 pF，VIL=0，VM=0.75 V，VIH=2.3 V，VT=3.3 V，RL=300 Ω，YZT、DQE | 0 |  | 0.8 | ns | S1 p7 |
| 下降传播延时 | tPHL | EN=2.5 V，升压，CL=15 pF，VIL=0，VM=0.75 V，VIH=2.3 V，VT=3.3 V，RL=300 Ω，DCU、DCT | 0 |  | 1.3 | ns | S1 p7 |

用这些数时要注意：

- 典型值在25 °C。导通电阻与端电压有关，VI=2.4/1.7 V的值仅按灌电流配置测量（S1 p6）。
- 推荐表中的0～5.5 V不表示任意参考组合均能转换。脚注要求VREF1至少1.2 V、至VREF2−0.6 V，VREF2至少VREF1+0.6 V（S1 p5）。应用设计表另列更窄的参考范围与6 mA导通电流，不能混成绝对额定（S1 p18）。
- 静电表CDM标准写JS-0011，照原文记录（S1 p5）。

## 热特性

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- |
| 结到环境热阻 | RθJA | DCT / DCU / DQE / YZT | 254.1 / 275.5 / 299.3 / 125.5 | °C/W | S1 p6 |
| 结到壳顶热阻 | RθJC(top) | DCT / DCU / DQE / YZT | 148.6 / 127.1 / 166.9 / 1 | °C/W | S1 p6 |
| 结到板热阻 | RθJB | DCT / DCU / DQE / YZT | 168.8 / 186.9 / 188.30 / 62.7 | °C/W | S1 p6 |
| 结到顶热参数 | ψJT | DCT / DCU / DQE / YZT | 70.1 / 65.7 / 18.0 / 3.4 | °C/W | S1 p6 |
| 结到板热参数 | ψJB | DCT / DCU / DQE / YZT | 167.4 / 185.9 / 187.4 / 62.7 | °C/W | S1 p6 |

## 静电额定

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- |
| 人体模型 | V(ESD) | HBM JS-001 | ±2000 | V | S1 p5 |
| 带电器件模型 | V(ESD) | 原表写JS-0011 | ±1000 | V | S1 p5 |

手册未给出单独的静电敏感警告。

## 引脚与处置

### DCT / DCU / DQE（脚号相同）

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
| --- | --- | --- | --- | --- |
| 1 GND | —，地 |  | 接地 | S1 p4 |
| 2 VREF1 | I，低侧参考电源 |  |  | S1 p4 |
| 3 SCL1 | I/O，低侧时钟 |  |  | S1 p4 |
| 4 SDA1 | I/O，低侧数据 |  |  | S1 p4 |
| 5 SDA2 | I/O，高侧数据 |  |  | S1 p4 |
| 6 SCL2 | I/O，高侧时钟 |  |  | S1 p4 |
| 7 VREF2 | I，高侧参考偏置 |  |  | S1 p4 |
| 8 EN | I，使能 |  |  | S1 p4 |

### YZT

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
| --- | --- | --- | --- | --- |
| A1 GND | —，地 |  | 接地 | S1 p4 |
| B1 VREF1 | I，低侧参考电源 |  |  | S1 p4 |
| C1 SCL1 | I/O，低侧时钟 |  |  | S1 p4 |
| D1 SDA1 | I/O，低侧数据 |  |  | S1 p4 |
| D2 SDA2 | I/O，高侧数据 |  |  | S1 p4 |
| C2 SCL2 | I/O，高侧时钟 |  |  | S1 p4 |
| B2 VREF2 | I，高侧参考偏置 |  |  | S1 p4 |
| A2 EN | I，使能 |  |  | S1 p4 |

散热焊盘：手册未给出散热焊盘及其内部连接、焊接规定。


## 必需外围

- 总线两侧各需上拉。双向转换时EN与VREF2短接，再经200 kΩ接高侧VDPU；不能把VREF2直接连高侧电源，否则电流过大且不可靠。推荐VREF2接100 pF滤波电容（S1 p17、p18、p21）。

## 订货型号与封装

手册列出的型号与封装如下；空格表示手册未给出，不从型号自行推算。

| 订货型号或后缀 | 封装 | 脚数 | 电压或功能档 | 温度范围 | 引脚镀层 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| PCA9306DCTR | SSOP (DCT) | 8 |  | -40～85 °C | NIPDAU | S1 p24 |
| PCA9306DCTR.A | SSOP (DCT) | 8 |  | -40～85 °C | NIPDAU | S1 p24 |
| PCA9306DCTT | SSOP (DCT) | 8 |  | -40～85 °C | NIPDAU | S1 p24 |
| PCA9306DCTT.A | SSOP (DCT) | 8 |  | -40～85 °C | NIPDAU | S1 p24 |
| PCA9306DCUR | VSSOP (DCU) | 8 |  | -40～85 °C | NIPDAU  /  SN / NIPDAUAG | S1 p24 |
| PCA9306DCUR.A | VSSOP (DCU) | 8 |  | -40～85 °C | NIPDAU | S1 p24 |
| PCA9306DCUT | VSSOP (DCU) | 8 |  | -40～85 °C | NIPDAU  /  SN / NIPDAUAG | S1 p24 |
| PCA9306DCUT.A | VSSOP (DCU) | 8 |  | -40～85 °C | NIPDAU | S1 p24 |
| PCA9306DQER | X2SON (DQE) | 8 |  | -40～85 °C | NIPDAU  /  NIPDAUAG | S1 p24 |
| PCA9306DQER.A | X2SON (DQE) | 8 |  | -40～85 °C | NIPDAUAG | S1 p24 |
| PCA9306DQER.B | X2SON (DQE) | 8 |  | -40～85 °C | NIPDAUAG | S1 p24 |
| PCA9306YZTR | DSBGA (YZT) | 8 |  | -40～85 °C | SN | S1 p24 |
| PCA9306YZTR.B | DSBGA (YZT) | 8 |  | -40～85 °C | SN | S1 p24 |



## 核对记录

- 2026-11-10：工具核对通过，核对了 184 个数。
