# TI ATL431

类别：器件参数。
器件：低阴极电流可调分流基准；同册包括 ATL432 引脚互换版本。
手册：SLVSCV5E，2024 年 12 月修订。

## 来源

- S1：Datasheet/08_电源管理/电压基准/TI - ATL431.pdf

页码是 PDF 文件的页序。

## 绝对最大值

| 参数 | 符号 | 条件 | 最小 | 最大 | 单位 | 来源 |
|---|---|---|---|---|---|---|
| 阴极电压 | VKA | 相对 ANODE |  | 40 | V | S1 p3 |
| 连续阴极电流 | IKA |  | −100 | 150 | mA | S1 p3 |
| 参考输入电流 | II(ref) |  | −0.05 | 10 | mA | S1 p3 |
| 结温 | TJ |  | −40 | 150 | °C | S1 p3 |
| 储存温度 | Tstg |  | −65 | 150 | °C | S1 p3 |

## 推荐工作条件

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
|---|---|---|---|---|---|---|---|
| 阴极电压 | VKA |  | Vref |  | 36 | V | S1 p3 |
| 阴极电流 | IKA |  | .035 |  | 100 | mA | S1 p3 |
| 环境温度 | TA | I 档 | −40 |  | 85 | °C | S1 p3 |
| 环境温度 | TA | Q 档 | −40 |  | 125 | °C | S1 p3 |

## 电气特性

推荐工作条件内，TA = 25 °C，除非另有说明；A/B 两档共用的保证值合并列出（S1 p4）。

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
|---|---|---|---|---|---|---|---|
| 参考电压 | Vref | ATL431/ATL432 A 档，VKA = Vref，IKA = 1 mA | 2475 | 2500 | 2525 | mV | S1 p4 |
| 参考电压 | Vref | ATL431/ATL432 B 档，VKA = Vref，IKA = 1 mA | 2487 | 2500 | 2512 | mV | S1 p4 |
| 全温参考电压变化 | VI(dev) | A/B 档，I 温区 −40 到 85 °C，VKA = Vref，IKA = 1 mA |  | 5 | 15 | mV | S1 p4 |
| 全温参考电压变化 | VI(dev) | A/B 档，Q 温区 −40 到 125 °C，VKA = Vref，IKA = 1 mA |  | 6 | 34 | mV | S1 p4 |
| 参考电压对阴极电压变化比 | ΔVref/ΔVKA | A/B 档，ΔVKA = 10 V − Vref，IKA = 1 mA |  | −0.4 | −2.7 | mV/V | S1 p4 |
| 参考电压对阴极电压变化比 | ΔVref/ΔVKA | A/B 档，ΔVKA = 36 V − 10 V，IKA = 1 mA |  | −0.1 | −2 | mV/V | S1 p4 |
| 参考输入电流 | Iref | A/B 档，IKA = 1 mA，R1 = 10 kΩ，R2 = ∞ |  | 30 | 150 | nA | S1 p4 |
| 全温参考电流变化 | II(dev) | A/B 档，IKA = 1 mA，R1 = 10 kΩ，R2 = ∞ |  | 20 | 50 | nA | S1 p4 |
| 调节所需阴极电流 | Imin | VKA = Vref；所需最小电流的典型及最坏上限 |  | 20 | 35 | µA | S1 p4 |
| 关断阴极电流 | Ioff | VKA = 36 V，Vref = 0 |  | 0.05 | 0.2 | µA | S1 p4 |
| 动态阻抗 | zKA | VKA = Vref，f ≤1 kHz，IKA = 1 到 100 mA |  | 0.05 | 0.3 | Ω | S1 p4 |

用这些数时要注意：

- 参考电压初始限值为室温值；全温偏移单独给出。负的 ΔVref/ΔVKA 数字原表放 MAX 栏，保留栏位，不能按普通正数大小解释（S1 p4）。
- 空载电容时可稳定，接电容时必须核对稳定区域及 ESR；本条目不从曲线取值。稳定边界使用不小于 250 Ω 的电阻表征，不能无条件套用 TL431 的外围（S1 p18）。

## 热特性

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
|---|---|---|---|---|---|
| 结到环境热阻 | RθJA | 封装列顺序见下文 | 331.8 | °C/W | S1 p4 |
| 结到壳顶热阻 | RθJC(top) | 封装列顺序见下文 | 106.5 | °C/W | S1 p4 |
| 结到板热阻 | RθJB | 封装列顺序见下文 | 64.6 | °C/W | S1 p4 |
| 结到顶热特性参数 | ψJT | 封装列顺序见下文 | 4.9 | °C/W | S1 p4 |
| 结到板热特性参数 | ψJB | 封装列顺序见下文 | 62.9 | °C/W | S1 p4 |

## 静电额定

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
|---|---|---|---|---|---|
| 人体模型 | V(ESD) | JS-001 | ±2000 | V | S1 p3 |
| 带电器件模型 | V(ESD) | JESD22-C101 | ±1000 | V | S1 p3 |

## 引脚与处置

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
|---|---|---|---|---|
| ATL431 1 CATHODE | I/O，分流电流/电压输入 | 见绝对最大表 |  | S1 p3 |
| ATL431 2 REF | I，相对共阳极的参考输入 | 未给独立电压额定 |  | S1 p3 |
| ATL431 3 ANODE | O，共阳极 |  | 通常接地 | S1 p3 |
| 散热焊盘 | SOT-23 无独立散热焊盘 |  |  | S1 p3 |

ATL432 的引脚：

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
|---|---|---|---|---|
| 1 REF | I，参考输入 | 未给独立电压额定 | | S1 p3 |
| 2 CATHODE | I/O，分流电流/电压输入 | 见绝对最大表 | | S1 p3 |
| 3 ANODE | O，共阳极 | | 通常接地 | S1 p3 |

## 必需外围

- 可调输出需要阴极到阳极的分压桥，中点接 REF；需供给足够偏置使 IKA 满足 Imin。无需强制并联电容；负载电容可能造成不稳定，按原手册稳定性说明选取（S1 p17、p18）。

## 订货型号与封装

A/B 区分初始参考精度；I/Q 区分温区；ATL431 与 ATL432 功能相同、阴极与 REF 脚互换（S1 p3、p4）。

| 订货型号或后缀 | 封装 | 脚数 | 电压或功能档 | 温度范围 | 引脚镀层 | 来源 |
|---|---|---|---|---|---|---|
| ATL431AIDBZR | SOT-23 (DBZ) | 3 |  | (ZCKS, ZCR3) | NIPDAU 或 NIPDAUAG Level-1-260C-UNLIM | S1 p22 |
| ATL431AIDBZR.A | SOT-23 (DBZ) | 3 |  | -40 to 85 | NIPDAU | S1 p22 |
| ATL431AQDBZR | SOT-23 (DBZ) | 3 |  | (ZCLS, ZCS3) | NIPDAU 或 NIPDAUAG Level-1-260C-UNLIM | S1 p22 |
| ATL431AQDBZR.A | SOT-23 (DBZ) | 3 |  | -40 to 125 | NIPDAU | S1 p22 |
| ATL431BIDBZR | SOT-23 (DBZ) | 3 |  | (ZCMS, ZCT3) | NIPDAU 或 NIPDAUAG Level-1-260C-UNLIM | S1 p22 |
| ATL431BIDBZR.A | SOT-23 (DBZ) | 3 |  | -40 to 85 | NIPDAU | S1 p22 |
| ATL431BQDBZR | SOT-23 (DBZ) | 3 |  | (ZCJS, ZCU3) | NIPDAU 或 NIPDAUAG Level-1-260C-UNLIM | S1 p22 |
| ATL431BQDBZR.A | SOT-23 (DBZ) | 3 |  | -40 to 125 | NIPDAU | S1 p22 |
| ATL432AIDBZR | SOT-23 (DBZ) | 3 |  | (ZCNS, ZCV3) | NIPDAU 或 NIPDAUAG Level-1-260C-UNLIM | S1 p22 |
| ATL432AIDBZR.A | SOT-23 (DBZ) | 3 |  | -40 to 85 | NIPDAU | S1 p22 |
| ATL432AQDBZR | SOT-23 (DBZ) | 3 |  | (ZCOS, ZCW3) | NIPDAU 或 NIPDAUAG Level-1-260C-UNLIM | S1 p22 |
| ATL432AQDBZR.A | SOT-23 (DBZ) | 3 |  | -40 to 125 | NIPDAU | S1 p22 |
| ATL432BIDBZR | SOT-23 (DBZ) | 3 |  | (ZCPS, ZCX3) | NIPDAU 或 NIPDAUAG Level-1-260C-UNLIM | S1 p22 |
| ATL432BIDBZR.A | SOT-23 (DBZ) | 3 |  | -40 to 85 | NIPDAU | S1 p22 |
| ATL432BQDBZR | SOT-23 (DBZ) | 3 |  | (ZCQS, ZCY3) | NIPDAU 或 NIPDAUAG Level-1-260C-UNLIM | S1 p22 |
| ATL432BQDBZR.A | SOT-23 (DBZ) | 3 |  | -40 to 125 | NIPDAU | S1 p22 |

器件生命周期状态不在本条目收录，设计时查厂家网站并记录日期。

## 核对记录

- 2026-11-10：逐页对照原件抽取，工具核对通过（PASS）；核对了 117 个数，问题 0 条，没核对 0 处。
