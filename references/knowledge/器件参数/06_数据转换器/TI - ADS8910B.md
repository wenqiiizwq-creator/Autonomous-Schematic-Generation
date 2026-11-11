# TI ADS8910B

类别：器件参数。
器件：全差分 SAR ADC，内置参考缓冲和 LDO；同册含 ADS8912B/14B。
手册：SBAS707B，2018 年1月修订。

## 来源

- S1：Datasheet/06_数据转换器/精密ADC/TI - ADS8910B.pdf

页码是 PDF 文件的页序。

## 绝对最大值

| 参数 | 符号 | 条件 | 最小 | 最大 | 单位 | 来源 |
|---|---|---|---|---|---|---|
| 模拟/数字供电 |  | RVDD、DVDD 对 GND | −0.3 | 7 | V | S1 p6 |
| 参考输入 |  | REFIN 对 REFM | −0.3 | RVDD+0.3 | V | S1 p6 |
| 参考地 |  | REFM 对 GND | −0.1 | 0.1 | V | S1 p6 |
| 模拟输入 |  | AINP/AINM 对 GND | −0.3 | VREF+0.3 | V | S1 p6 |
| 数字输入输出 |  | 对 GND | −0.3 | DVDD+0.3 | V | S1 p6 |
| 模拟输入电流 |  | 到 RVDD 和 GND | −130 | 130 | mA | S1 p6 |
| 环境温度 | TA |  | −40 | 125 | °C | S1 p6 |
| 储存温度 | Tstg |  | −65 | 150 | °C | S1 p6 |

## 推荐工作条件

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
|---|---|---|---|---|---|---|---|
| 模拟供电 | RVDD |  | 3 | 5 | 5.5 | V | S1 p6 |
| 数字供电 | DVDD | 可工作 | 1.65 | 3 | 5.5 | V | S1 p6 |
| 数字供电 | DVDD | 规定吞吐率 | 2.35 | 3 | 5.5 | V | S1 p6 |
| 参考输入 | VREF |  | 2.5 |  | RVDD−0.3 | V | S1 p6 |
| 缓冲电容 | CREFBUF |  | 10 | 22 |  | µF | S1 p6 |
| 缓冲串阻 | RESR |  | 0 | 1 | 1.3 | Ω | S1 p6 |
| 工作环境温度 | TA |  | −40 | 25 | 125 | °C | S1 p6 |

## 电气特性

RVDD=5.5 V，DVDD=1.65 到5.5 V，VREF=5 V，最高吞吐率；上下限全温，典型25 °C；DC/AC 精度在内部参考缓冲/LDO 下且 CREFBUF=22 µF、RESR=1 Ω（S1 p7、p8）。

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
|---|---|---|---|---|---|---|---|
| 差分满量程 | FSR | AINP−AINM | −VREF |  | VREF | V | S1 p7 |
| 绝对输入 | VIN | AINP/AINM 对 REFM | 0 |  | VREF | V | S1 p7 |
| 共模输入 | VCM | (AINP+AINM)/2 | VREF/2 − 0.1 | VREF/2 | VREF/2 + 0.1 | V | S1 p7 |
| 参考电流 | IREF | VREF =5 V |  | 0.1 | 1 | µA | S1 p7 |
| 参考缓冲失调 | V(RO) | EN_MARG=0，25 °C，参考选择校准按寄存器 | −250 |  | 250 | µV | S1 p7 |
| 参考缓冲电容 | CREFBUF |  | 10 | 22 |  | µF | S1 p7 |
| 参考缓冲串阻 | RESR |  | 0 | 1 | 1.3 | Ω | S1 p7 |
| 无失码 | NMC |  | 18 |  |  | Bits | S1 p7 |
| 积分非线性 | INL |  | −1.5 | ±0.5 | 1.5 | LSB | S1 p7 |
| 微分非线性 | DNL |  | −0.5 | ±0.2 | 0.5 | LSB | S1 p7 |
| 输入失调 | E(IO) | 25 °C；参考选择校准 | −3 | ±0.5 | 3 | LSB | S1 p7 |
| 输入失调 | E(IO) | 全温；参考选择校准 | −20 | ±3 | 20 | LSB | S1 p7 |
| 增益误差 | GE | EN_MARG=0，含参考缓冲误差 | −0.02 | ±0.005 | 0.02 | %FSR | S1 p7 |
| 突发首码偏离 |  | 按参考缓冲规定 | −3 |  | 3 | TNS | S1 p7 |
| 信噪失真比 | SINAD | fIN=2 kHz，输入−0.1 dBFS | 100 | 102.48 |  | dB | S1 p8 |
| 信噪比 | SNR | fIN=2 kHz，输入−0.1 dBFS | 101 | 102.5 |  | dB | S1 p8 |
| LDO 去耦 | CLDO | DECAP | 1 |  |  | µF | S1 p8 |
| 数字输入高电平 | VIH | 1.65 < DVDD <2.3 V | 0.8 × DVDD |  | DVDD+0.3 | V | S1 p8 |
| 数字输入高电平 | VIH | 2.3 < DVDD <5.5 V | 0.7 × DVDD |  | DVDD+0.3 | V | S1 p8 |
| 数字输入低电平 | VIL | 1.65 < DVDD <2.3 V | −0.3 |  | 0.2 × DVDD | V | S1 p8 |
| 数字输入低电平 | VIL | 2.3 < DVDD <5.5 V | −0.3 |  | 0.3 × DVDD | V | S1 p8 |
| 数字输入电流 |  |  |  | ±0.01 | 0.1 | µA | S1 p8 |
| 数字输出高电平 | VOH | 源电流500 µA | 0.8 × DVDD |  | DVDD | V | S1 p8 |
| 数字输出低电平 | VOL | 吸电流500 µA | 0 |  | 0.2 × DVDD | V | S1 p8 |
| 采样时钟高脉宽 | twh_CONVST |  | 30 |  |  | ns | S1 p9 |
| 采样时钟低脉宽 | twl_CONVST |  | 30 |  |  | ns | S1 p9 |
| 采集时间 | tacq |  | 300 |  |  | ns | S1 p9 |
| 安静采集时间 | tqt_acq |  | 30 |  |  | ns | S1 p9 |
| 安静孔径时间 | td_cnvcap |  | 20 |  |  | ns | S1 p9 |
| 复位低脉宽 | twl_RST |  | 100 |  |  | ns | S1 p9 |
| SPI 频率 | fCLK | 2.35 ≤DVDD ≤5.5 V，全温，高>0.7DVDD、低<0.3DVDD |  |  | 70 | MHz | S1 p9 |
| SPI 频率 | fCLK | 1.65 ≤DVDD <2.35 V，全温，高>0.8DVDD、低<0.2DVDD |  |  | 20 | MHz | S1 p9 |
| SPI 频率 | fCLK | 同低压逻辑，0 到60 °C |  |  | 57 | MHz | S1 p9 |
| SPI 频率 | fCLK | 同低压，全温，高>0.9DVDD、低<0.1DVDD |  |  | 68 | MHz | S1 p9 |
| 串行时钟周期 | tCLK |  | 1/fCLK |  |  | ns | S1 p9 |
| 串行时钟高时间 | tph_CK |  | 0.45 |  | 0.55 | tCLK | S1 p9 |
| 串行时钟低时间 | tpl_CK |  | 0.45 |  | 0.55 | tCLK | S1 p9 |
| 片选至时钟建立 | tsu_CSCK |  | 12 |  |  | ns | S1 p9 |
| 数据至时钟建立 | tsu_CKDI |  | 1.5 |  |  | ns | S1 p9 |
| 时钟至数据保持 | tht_CKDI |  | 1 |  |  | ns | S1 p9 |
| 最后时钟至片选释放 | tht_CKCS |  | 7 |  |  | ns | S1 p9 |
| 源同步外部时钟频率 | fCLK | 2.35 ≤DVDD ≤5.5 V，SDR |  |  | 70 | MHz | S1 p9 |
| 源同步外部时钟频率 | fCLK | 2.35 ≤DVDD ≤5.5 V，DDR |  |  | 35 | MHz | S1 p9 |
| 复位释放到 RVS | td_rst |  |  |  | 3 | ms | S1 p10 |
| ADC 上电等待 | tPU_ADC | 原表 MIN 栏 | 1 |  |  | ms | S1 p10 |
| 参考缓冲上电等待 | tPU_REFBUF | CREFBUF=22 µF，原表 MIN 栏 | 10 |  |  | ms | S1 p10 |
| 器件上电等待 | tPU_Device | CLDO=1 µF，CREFBUF=22 µF | 10 |  |  | ms | S1 p10 |
| 片选至输出使能 | tden_CSDO |  |  |  | 9 | ns | S1 p10 |
| 片选释放至高阻 | tdz_CSDO |  |  |  | 10 | ns | S1 p10 |
| 时钟至数据有效 | td_CKDO |  |  |  | 13 | ns | S1 p10 |
| 片选下降至 RVS 下降 | td_CSRDY_f |  |  |  | 12 | ns | S1 p10 |
| 片选上升至 RVS 上升 | td_CSRDY_r | NOP 后 |  |  | 30 | ns | S1 p10 |
| 片选上升至 RVS 上升 | td_CSRDY_r | WR/RD 后 |  |  | 120 | ns | S1 p10 |
| 外部时钟到选通上升 | td_CKSTR_r |  |  |  | 13 | ns | S1 p10 |
| 外部时钟到选通下降 | td_CKSTR_f |  |  |  | 13 | ns | S1 p10 |
| 选通下降数据偏移 | toff_STRDO_f | 外部时钟 | −2 |  | 2 | ns | S1 p10 |
| 选通上升数据偏移 | toff_STRDO_r | 外部时钟 | −2 |  | 2 | ns | S1 p10 |
| 选通高时间 | tph_STR | 外/内部时钟，外部要求 DVDD≥2.35 V | 0.45 |  | 0.55 | tSTR | S1 p10 |
| 选通低时间 | tpl_STR | 同上 | 0.45 |  | 0.55 | tSTR | S1 p10 |
| 内部时钟片选至选通 | td_CSSTR |  | 15 |  | 50 | ns | S1 p10 |
| 模拟供电电流 | IRVDD | ADS8910B，RVDD=5 V，最高采样率 |  | 4.2 | 5.8 | mA | S1 p8 |
| 模拟功耗 | PRVDD | ADS8910B，RVDD=5 V，最高采样率 |  | 21 | 29 | mW | S1 p8 |
| 采样频率 | fcycle | ADS8910B |  |  | 1000 | kHz | S1 p9 |
| 转换周期 | tcycle | ADS8910B | 1 |  |  | µs | S1 p9 |
| 转换时间 | tconv | ADS8910B | 580 |  | 640 | ns | S1 p10 |
| 模拟供电电流 | IRVDD | ADS8912B，RVDD=5 V，最高采样率 |  | 3.2 | 4 | mA | S1 p8 |
| 模拟功耗 | PRVDD | ADS8912B，RVDD=5 V，最高采样率 |  | 16 | 20 | mW | S1 p8 |
| 采样频率 | fcycle | ADS8912B |  |  | 500 | kHz | S1 p9 |
| 转换周期 | tcycle | ADS8912B | 2 |  |  | µs | S1 p9 |
| 转换时间 | tconv | ADS8912B | 1100 |  | 1200 | ns | S1 p10 |
| 模拟供电电流 | IRVDD | ADS8914B，RVDD=5 V，最高采样率 |  | 2.8 | 3.6 | mA | S1 p8 |
| 模拟功耗 | PRVDD | ADS8914B，RVDD=5 V，最高采样率 |  | 14 | 18 | mW | S1 p8 |
| 采样频率 | fcycle | ADS8914B |  |  | 250 | kHz | S1 p9 |
| 转换周期 | tcycle | ADS8914B | 4 |  |  | µs | S1 p9 |
| 转换时间 | tconv | ADS8914B | 2400 |  | 2500 | ns | S1 p10 |

用这些数时要注意：

- 噪声、温漂、100 kHz 信噪比、THD/SFDR、孔径抖动、带宽、LDO 电压/启动、内部选通周期只有典型值。参考缓冲失调仅保证室温（S1 p7、p8、p10）。
- 精度和失调要把 REF_SEL 设到最接近实际 VREF；增益指标包含内部缓冲误差/漂移。低 DVDD 的外时钟源同步不推荐，SPI 最高频率需按电压、逻辑摆幅和温度区分（S1 p7、p9、p10、p20）。
- RVDD 跌破最低工作值后需先降至 ≤0.7 V 再上电，上电必须单调（S1 p64）。

## 热特性

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
|---|---|---|---|---|---|
| 结到环境热阻 | RθJA | 封装列顺序见下文 | 31.9 | °C/W | S1 p6 |
| 结到壳顶热阻 | RθJC(top) | 封装列顺序见下文 | 29.9 | °C/W | S1 p6 |
| 结到板热阻 | RθJB | 封装列顺序见下文 | 8.9 | °C/W | S1 p6 |
| 结到顶热特性参数 | ψJT | 封装列顺序见下文 | 0.3 | °C/W | S1 p6 |
| 结到板热特性参数 | ψJB | 封装列顺序见下文 | 8.9 | °C/W | S1 p6 |
| 结到壳底热阻 | RθJC(bot) | 封装列顺序见下文 | 2.0 | °C/W | S1 p6 |

## 静电额定

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
|---|---|---|---|---|---|
| 人体模型 | V(ESD) | JS-001 | ±2000 | V | S1 p6 |
| 带电器件模型 | V(ESD) | JESD22-C101 | ±500 | V | S1 p6 |

## 引脚与处置

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
|---|---|---|---|---|
| 1 CONVST | Digital input，上升沿启动转换 | 见数字额定 |  | S1 p4 |
| 2 RST | Digital input，低有效异步复位 | 见数字额定 |  | S1 p4 |
| 3 REFIN | Analog input，基准输入 | 见参考范围 |  | S1 p4 |
| 4、8 REFM | Analog input，参考地 | 见参考地额定 | 两脚外部短接到 GND | S1 p4、p21 |
| 5、7 REFBUFOUT | Analog input/output，缓冲输出/外参考输入 | 按参考模式 | 两脚必须短接 | S1 p4、p21 |
| 6 NC | No connection |  | 必须悬空 | S1 p4 |
| 9 AINP；10 AINM | Analog input，正负差分 | 见模拟范围 |  | S1 p4 |
| 11、15 GND | Power supply，地 |  | 接地 | S1 p4 |
| 12 RVDD | Power supply，模拟供电 | 3 到5.5 V（工作） |  | S1 p4、p6 |
| 13、14 DECAP | Power supply，内部 LDO 去耦 |  | 两脚短接，外接去耦 | S1 p4 |
| 16 DVDD | Power supply，接口供电 | 见数字工作范围 |  | S1 p4 |
| 17 SDO-3；18 SDO-2；19 SDO-1；20 SDO-0 | Digital output，数据 | 见数字输出额定 |  | S1 p4、p5 |
| 21 RVS | Digital output，状态/选通 | 见数字输出额定 |  | S1 p4 |
| 22 SDI；23 SCLK；24 CS | Digital input，数据/时钟/低有效片选 | 见数字额定 |  | S1 p4 |
| 散热焊盘 | Supply，要求接 GND；未明示内部连接和必须焊接 |  | 接 GND | S1 p5 |

## 必需外围

- RVDD、DVDD 各对地10 µF；DECAP 至少1 µF，两脚短接。参考缓冲两输出短接，REFM 两脚接地，之间就近接至少10 µF（典型22 µF）串0到1.3 Ω（典型1 Ω）网络。外部参考是必需输入，滤波RC按源噪声设计（S1 p6、p7、p21、p64）。

## 订货型号与封装

ADS8910B/12B/14B 最高吞吐率不同，封装脚序相同；数字供电低压模式可工作不代表可达到额定吞吐率（S1 p6、p9）。

| 订货型号或后缀 | 封装 | 脚数 | 电压或功能档 | 温度范围 | 引脚镀层 | 来源 |
|---|---|---|---|---|---|---|
| ADS8910BRGER | VQFN (RGE) | 24 |  | -40 to 125 | NIPDAU | S1 p69 |
| ADS8910BRGER.B | VQFN (RGE) | 24 |  | -40 to 125 | NIPDAU | S1 p69 |
| ADS8910BRGET | VQFN (RGE) | 24 |  | -40 to 125 | NIPDAU | S1 p69 |
| ADS8910BRGET.B | VQFN (RGE) | 24 |  | -40 to 125 | NIPDAU | S1 p69 |
| ADS8912BRGER | VQFN (RGE) | 24 |  | -40 to 125 | NIPDAU | S1 p69 |
| ADS8912BRGER.B | VQFN (RGE) | 24 |  | -40 to 125 | NIPDAU | S1 p69 |
| ADS8912BRGET | VQFN (RGE) | 24 |  | -40 to 125 | NIPDAU | S1 p69 |
| ADS8912BRGET.B | VQFN (RGE) | 24 |  | -40 to 125 | NIPDAU | S1 p69 |
| ADS8914BRGER | VQFN (RGE) | 24 |  | -40 to 125 | NIPDAU | S1 p69 |
| ADS8914BRGER.B | VQFN (RGE) | 24 |  | -40 to 125 | NIPDAU | S1 p69 |
| ADS8914BRGET | VQFN (RGE) | 24 |  | -40 to 125 | NIPDAU | S1 p69 |
| ADS8914BRGET.B | VQFN (RGE) | 24 |  | -40 to 125 | NIPDAU | S1 p69 |

器件生命周期状态不在本条目收录，设计时查厂家网站并记录日期。

## 核对记录

- 2026-11-10：逐页对照原件抽取，工具核对通过（PASS）；核对了 227 个数，问题 0 条，没核对 0 处。
