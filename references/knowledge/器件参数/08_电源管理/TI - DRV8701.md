# TI DRV8701

类别：器件参数。
器件：外置 N 沟道 H 桥栅极驱动器，带检测放大器与电流斩波。
手册：SLVSCX5B，2015 年 7 月修订。

## 来源

- S1：Datasheet/08_电源管理/电机驱动/TI - DRV8701.pdf

页码是 PDF 文件的页序。

## 绝对最大值

| 参数 | 符号 | 条件 | 最小 | 最大 | 单位 | 来源 |
|---|---|---|---|---|---|---|
| 电源电压 | VM |  | −0.3 | 47 | V | S1 p5 |
| 电源斜率 | VM |  | 0 | 2 | V/µs | S1 p5 |
| 电荷泵电压 | VCP、CPH |  | −0.3 | VM + 12 | V | S1 p5 |
| 电荷泵负切换脚 | CPL |  | −0.3 | VM | V | S1 p5 |
| 内部逻辑稳压 | DVDD |  | −0.3 | 3.8 | V | S1 p5 |
| 内部模拟稳压 | AVDD |  | −0.3 | 5.75 | V | S1 p5 |
| 控制脚电压 |  | PH、EN、IN1、IN2、nSLEEP、nFAULT、VREF、IDRIVE、SNSOUT | −0.3 | 5.75 | V | S1 p5 |
| 高侧栅极 | GH1、GH2 |  | −0.3 | VM + 12 | V | S1 p5 |
| 连续相节点 | SH1、SH2 |  | −1.2 | VM + 1.2 | V | S1 p5 |
| 脉冲相节点 | SH1、SH2 | 10 µs | −2.0 | VM + 2 | V | S1 p5 |
| 低侧栅极 | GL1、GL2 |  | −0.3 | 12 | V | S1 p5 |
| 连续检测输入 | SP、SN |  | −0.5 | 1 | V | S1 p5 |
| 脉冲检测输入 | SP、SN | 10 µs | −1 | 1 | V | S1 p5 |
| 检测输出 | SO |  | −0.3 | 5.75 | V | S1 p5 |
| 开漏电流 |  | nFAULT、SNSOUT | 0 | 10 | mA | S1 p5 |
| 栅极源电流 |  | GH1/GL1/GH2/GL2 | 0 | 250 | mA | S1 p5 |
| 栅极吸电流 |  | GH1/GL1/GH2/GL2 | 0 | 500 | mA | S1 p5 |
| 检测输出电流 | SO |  | 0 | 5 | mA | S1 p5 |
| 结温 | TJ |  | −40 | 150 | °C | S1 p5 |
| 储存温度 | Tstg |  | −65 | 150 | °C | S1 p5 |

## 推荐工作条件

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
|---|---|---|---|---|---|---|---|
| 电源电压 | VM |  | 5.9 |  | 45 | V | S1 p5 |
| 逻辑输入 | VCC |  | 0 |  | 5.5 | V | S1 p5 |
| 参考电压 | VREF |  | 0.3 |  | AVDD | V | S1 p5 |
| 外加 PWM 频率 | ƒPWM |  |  |  | 100 | kHz | S1 p5 |
| 模拟稳压外载 | IAVDD | 受热限制 |  |  | 30 | mA | S1 p5 |
| 数字稳压外载 | IDVDD | 受热限制 |  |  | 30 | mA | S1 p5 |
| 检测输出负载 | ISO |  |  |  | 5 | mA | S1 p5 |
| 环境温度 | TA |  | −40 |  | 125 | °C | S1 p5 |

## 电气特性

在工作环境温区内，另注明者除外；部分参数由设计及表征保证，逐行注明（S1 p7、p8）。

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
|---|---|---|---|---|---|---|---|
| 工作电压 | VM |  | 5.9 |  | 45 | V | S1 p7 |
| 工作电流 | IVM | VM = 24 V，nSLEEP 高 |  | 6 | 9.5 | mA | S1 p7 |
| 睡眠电流 | IVMQ | VM = 24 V，nSLEEP = 0，25 °C |  | 9 | 15 | µA | S1 p7 |
| 睡眠电流 | IVMQ | VM = 24 V，nSLEEP = 0，125 °C，设计和表征 |  | 14 | 25 | µA | S1 p7 |
| 入睡时间 | tSLEEP | nSLEEP 低到睡眠 |  |  | 100 | µs | S1 p7 |
| 唤醒时间 | tWAKE | nSLEEP 高到输出变化 |  |  | 1 | ms | S1 p7 |
| 开启时间 | tON | VM > UVLO 到输出 |  |  | 1 | ms | S1 p7 |
| 数字稳压输出 | DVDD | 外载 0 到 30 mA | 3.0 | 3.3 | 3.5 | V | S1 p7 |
| 模拟稳压输出 | AVDD | 外载 0 到 30 mA | 4.4 | 4.8 | 5.2 | V | S1 p7 |
| 电荷泵电压 | VCP | VM = 12 V，IVCP = 0 到 12 mA | 20.5 | 21.5 | 22.5 | V | S1 p7 |
| 电荷泵电压 | VCP | VM = 8 V，IVCP = 0 到 10 mA | 13.5 | 14.4 | 15 | V | S1 p7 |
| 电荷泵电压 | VCP | VM = 5.9 V，IVCP = 0 到 8 mA | 9.4 | 9.9 | 10.4 | V | S1 p7 |
| 电荷泵供流能力 | IVCP | VM > 12 V | 12 |  |  | mA | S1 p7 |
| 电荷泵供流能力 | IVCP | 8 V < VM < 12 V | 10 |  |  | mA | S1 p7 |
| 电荷泵供流能力 | IVCP | 5.9 V < VM < 8 V | 8 |  |  | mA | S1 p7 |
| 电荷泵频率 | fVCP | VM > UVLO，设计和表征 | 200 | 400 | 700 | kHz | S1 p7 |
| 逻辑低电平 | VIL |  |  |  | 0.8 | V | S1 p7 |
| 逻辑高电平 | VIH |  | 1.5 |  |  | V | S1 p7 |
| 逻辑迟滞 | VHYS |  | 100 |  |  | mV | S1 p7 |
| 输入低电流 | IIL | VIN = 0 V | −5 |  | 5 | µA | S1 p7 |
| 输入高电流 | IIH | VIN = 5 V |  |  | 78 | µA | S1 p7 |
| 下拉电阻 | RPD |  | 64 | 115 | 173 | kΩ | S1 p7 |
| 传播延迟 | tPD | PH/EN、IN1/IN2 到 GHx/GLx |  | 500 |  | ns | S1 p7 |
| 输出低电平 | VOL | IO = 2 mA |  |  | 0.1 | V | S1 p7 |
| 高阻漏电 | IOZ | VIN = 5 V | −2 |  | 2 | µA | S1 p7 |
| 高侧栅源驱动 | VGHS | VM > 12 V，相对 SHx | 8.5 | 9.5 | 10.5 | V | S1 p7 |
| 高侧栅源驱动 | VGHS | VM = 8 V，相对 SHx | 5.5 | 6.4 | 7 | V | S1 p7 |
| 高侧栅源驱动 | VGHS | VM = 5.9 V，相对 SHx | 3.5 | 4.0 | 4.5 | V | S1 p7 |
| 低侧栅源驱动 | VGLS | VM > 12 V | 8.5 | 9.3 | 10.5 | V | S1 p7 |
| 低侧栅源驱动 | VGLS | VM = 5.9 V | 3.9 | 4.3 | 4.9 | V | S1 p7 |
| 输出死区 | tDEAD | 受 IDRIVE 档影响 |  | 380 |  | ns | S1 p7 |
| 栅极驱动时间 | tDRIVE |  |  | 2.5 |  | µs | S1 p7 |
| 保持源电流 | IHOLD | tDRIVE 后 |  | 6 |  | mA | S1 p8 |
| 保持吸电流 | IHOLD | tDRIVE 后 |  | 25 |  | mA | S1 p8 |
| 强下拉电流 | ISTRONG | GHx |  | 490 |  | mA | S1 p8 |
| 强下拉电流 | ISTRONG | GLx |  | 690 |  | mA | S1 p8 |
| 关断栅极电阻 | ROFF | GHx 到 SHx |  | 200 |  | kΩ | S1 p8 |
| 关断栅极电阻 | ROFF | GLx 到 GND |  | 150 |  | kΩ | S1 p8 |
| 参考输入 | VVREF | 内部斩波 | 0.3 |  | AVDD | V | S1 p8 |
| 检测放大增益 | AV | 50 < VSP < 200 mV，VSN = GND | 18 | 20 | 22 | V/V | S1 p8 |
| 检测放大增益 | AV | 10 < VSP < 50 mV，VSN = GND | 16 | 20 | 24 | V/V | S1 p8 |
| 输出失调 | VOFF | VSP = VSN = GND |  | 50 | 250 | mV | S1 p8 |
| 检测输入电流 | ISP | VSP = 100 mV，VSN = GND |  | −40 |  | µA | S1 p8 |
| 建立到 ±1% 时间 | tSET | VSP/VSN 从 GND 到 VSP = 100 mV、VSN = GND；设计和表征 |  |  | 1.5 | µs | S1 p8 |
| 输出允许电容 | CSO | 设计和表征 |  |  | 1 | nF | S1 p8 |
| 调节关断时间 | tOFF |  |  | 25 |  | µs | S1 p8 |
| 消隐时间 | tBLANK |  |  | 2 |  | µs | S1 p8 |
| 欠压锁定 | VUVLO | VM 下降 |  | 5.4 | 5.8 | V | S1 p8 |
| 欠压恢复 | VUVLO | VM 上升 |  | 5.6 | 5.9 | V | S1 p8 |
| 欠压迟滞 | VUVLO,HYS |  | 100 |  |  | mV | S1 p8 |
| 欠压去毛刺 | tUVLO | VM 下降 |  | 10 |  | µs | S1 p8 |
| 电荷泵欠压 | VCPUV |  |  | VM + 2.8 |  | V | S1 p8 |
| 外管过流门限 | VDS OCP | 高侧 VM−SHx，低侧 SHx−SP | 0.8 | 1 |  | V | S1 p8 |
| 检测放大器过流门限 | VSP OCP | VSP 对 GND | 0.8 | 1 |  | V | S1 p8 |
| 过流去毛刺 | tOCP |  |  | 4.5 |  | µs | S1 p8 |
| 过流重试 | tRETRY |  |  | 3 |  | ms | S1 p8 |
| 热关断 | TTSD | 设计和表征 | 150 |  |  | °C | S1 p8 |
| 热迟滞 | THYS | 设计和表征 |  | 20 |  | °C | S1 p8 |
| 正向栅极钳位 | VGS CLAMP |  | 10.5 |  | 13 | V | S1 p8 |
| 负向栅极钳位 | VGS CLAMP |  | −1 | −0.7 | −0.5 | V | S1 p8 |
| 峰值源电流 | IDRIVE,SRC | RIDRIVE <1 kΩ 接 GND |  | 6 |  | mA | S1 p7 |
| 峰值吸电流 | IDRIVE,SNK | RIDRIVE <1 kΩ 接 GND |  | 12.5 |  | mA | S1 p8 |
| 峰值源电流 | IDRIVE,SRC | RIDRIVE 33 kΩ ±5% 接 GND |  | 12.5 |  | mA | S1 p7 |
| 峰值吸电流 | IDRIVE,SNK | RIDRIVE 33 kΩ ±5% 接 GND |  | 25 |  | mA | S1 p8 |
| 峰值源电流 | IDRIVE,SRC | RIDRIVE 200 kΩ ±5% 接 GND，或 <1 kΩ 接 AVDD |  | 25 |  | mA | S1 p7 |
| 峰值吸电流 | IDRIVE,SNK | RIDRIVE 200 kΩ ±5% 接 GND，或 <1 kΩ 接 AVDD |  | 50 |  | mA | S1 p8 |
| 峰值源电流 | IDRIVE,SRC | RIDRIVE >500 kΩ ±5% 接 GND |  | 100 |  | mA | S1 p7 |
| 峰值吸电流 | IDRIVE,SNK | RIDRIVE >500 kΩ ±5% 接 GND |  | 200 |  | mA | S1 p8 |
| 峰值源电流 | IDRIVE,SRC | RIDRIVE 68 kΩ ±5% 接 AVDD |  | 150 |  | mA | S1 p7 |
| 峰值吸电流 | IDRIVE,SNK | RIDRIVE 68 kΩ ±5% 接 AVDD |  | 300 |  | mA | S1 p8 |

用这些数时要注意：

- VREF 低于 0.3 V 可工作但精度下降。大多数栅极电流、死区、驱动持续时间、关断电阻、过流重试等仅典型；热关断只保证最小值，不能当成精确温控点（S1 p7、p8）。
- 125 °C 睡眠电流、泵频率、建立时间、允许输出电容和热保护由设计及表征给出，不代表逐颗测试（S1 p7、p8）。

## 热特性

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
|---|---|---|---|---|---|
| 结到环境热阻 | RθJA | 封装列顺序见下文 | 34.8 | °C/W | S1 p6 |
| 结到壳顶热阻 | RθJC(top) | 封装列顺序见下文 | 37.1 | °C/W | S1 p6 |
| 结到板热阻 | RθJB | 封装列顺序见下文 | 12.2 | °C/W | S1 p6 |
| 结到顶热特性参数 | ψJT | 封装列顺序见下文 | 0.6 | °C/W | S1 p6 |
| 结到板热特性参数 | ψJB | 封装列顺序见下文 | 12.2 | °C/W | S1 p6 |
| 结到壳底热阻 | RθJC(bot) | 封装列顺序见下文 | 3.7 | °C/W | S1 p6 |

## 静电额定

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
|---|---|---|---|---|---|
| 人体模型 | V(ESD) | 原件 HBM 应力电压 | ±2000 | V | S1 p5 |
| 带电器件模型 | V(ESD) | 原件 CDM 应力电压 | ±500 | V | S1 p5 |

## 引脚与处置

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
|---|---|---|---|---|
| 1 VM | Power，电机电源 | 5.9 到 45 V（工作） |  | S1 p3、p5 |
| 2 VCP | Power，电荷泵输出 | 见绝对最大值 |  | S1 p3 |
| 3 CPH；4 CPL | Power，电荷泵切换节点 | 见绝对最大值 |  | S1 p3 |
| 5、16 GND | Power，地 |  | 必须接地 | S1 p3 |
| 6 VREF | Input，电流参考 | 0.3 V 到 AVDD（工作） |  | S1 p4、p5 |
| 7 AVDD；8 DVDD | Power，内部稳压输出 | 见绝对最大值 | 各接旁路 | S1 p3 |
| 9 nFAULT；10 SNSOUT | Open Drain，故障及斩波指示 | 0 到 5.5 V（工作） | 使用时外接上拉 | S1 p4、p5 |
| 11 SO | Output，检测放大器输出 | 见绝对最大值 | 电容不得超过 1 nF | S1 p4 |
| 12 IDRIVE | Input，栅极电流设定 | 0 到 5.5 V（工作） | 按档位配置 | S1 p3、p5 |
| 13 nSLEEP | Input，低电平睡眠，内置下拉 | 0 到 5.5 V（工作） |  | S1 p3、p5 |
| 17 GH1；24 GH2 | Output，高侧栅极 | 见绝对最大值 | 接外管 | S1 p4 |
| 18 SH1；23 SH2 | Input，相节点 | 见绝对最大值 | 接高侧源极和低侧漏极 | S1 p4 |
| 19 GL1；22 GL2 | Output，低侧栅极 | 见绝对最大值 | 接外管 | S1 p4 |
| 20 SN；21 SP | Input，检测放大器输入 | 见绝对最大值 | SN 接地端，SP 接低侧源极端 | S1 p4 |
| 散热焊盘 PPAD | Power，GND，必须接地；未明示内部连接与必须焊接 |  | 接地 | S1 p3 |

DRV8701E 控制脚：

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
|---|---|---|---|---|
| 14 EN | Input，桥使能；低为制动 | 0 到 5.5 V（工作） |  | S1 p3、p5 |
| 15 PH | Input，方向 | 0 到 5.5 V（工作） |  | S1 p3、p5 |

DRV8701P 控制脚：

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
|---|---|---|---|---|
| 15 IN1；14 IN2 | Input，PWM 桥控制 | 0 到 5.5 V（工作） |  | S1 p3、p5 |

## 必需外围

- 必须外接四颗 N 沟道 FET；VM 对地 0.1 µF 陶瓷加至少 10 µF 大电容，外桥还需额外大电容。VCP–VM 为 1 µF/16 V；CPH–CPL 为 0.1 µF X7R、耐压按 VM；DVDD、AVDD 各对地 1 µF/6.3 V。nFAULT、SNSOUT 使用时上拉 ≥10 kΩ 到合法逻辑电源；IDRIVE 按档选择；低侧检测电阻按电流需求（S1 p3、p4、p32）。

## 订货型号与封装

E 为 PH/EN 接口，P 为 IN1/IN2 PWM 接口；RGE 为二十四脚 VQFN（S1 p3）。

| 订货型号或后缀 | 封装 | 脚数 | 电压或功能档 | 温度范围 | 引脚镀层 | 来源 |
|---|---|---|---|---|---|---|
| DRV8701ERGER | VQFN (RGE) | 24 |  | -40 to 125 | NIPDAU | S1 p35 |
| DRV8701ERGER.A | VQFN (RGE) | 24 |  | -40 to 125 | NIPDAU | S1 p35 |
| DRV8701ERGERG4 | VQFN (RGE) | 24 |  | -40 to 125 | NIPDAU | S1 p35 |
| DRV8701ERGERG4.A | VQFN (RGE) | 24 |  | -40 to 125 | NIPDAU | S1 p35 |
| DRV8701ERGET | VQFN (RGE) | 24 |  | -40 to 125 | Call TI | S1 p35 |
| DRV8701PRGER | VQFN (RGE) | 24 |  | -40 to 125 | NIPDAU | S1 p35 |
| DRV8701PRGER.A | VQFN (RGE) | 24 |  | -40 to 125 | NIPDAU | S1 p35 |
| DRV8701PRGET | VQFN (RGE) | 24 |  | -40 to 125 | Call TI | S1 p35 |

器件生命周期状态不在本条目收录，设计时查厂家网站并记录日期。

## 核对记录

- 2026-11-10：逐页对照原件抽取，工具核对通过（PASS）；核对了 236 个数，问题 0 条，没核对 0 处。
