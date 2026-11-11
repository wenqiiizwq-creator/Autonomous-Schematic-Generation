# TI ADS124S06

类别：器件参数。
器件：带 PGA、基准、IDAC 和多路输入的 ΔΣ ADC；同册含 ADS124S08。
手册：SBAS660C，2017 年6月修订。

## 来源

- S1：Datasheet/06_数据转换器/精密ADC/TI - ADS124S06.pdf

页码是 PDF 文件的页序。

## 绝对最大值

| 参数 | 符号 | 条件 | 最小 | 最大 | 单位 | 来源 |
|---|---|---|---|---|---|---|
| 模拟供电差 |  | AVDD−AVSS | −0.3 | 5.5 | V | S1 p7 |
| 模拟负电源对数字地 |  | AVSS−DGND | −2.8 | 0.3 | V | S1 p7 |
| 核心供电 |  | DVDD−DGND | −0.3 | 3.9 | V | S1 p7 |
| 接口供电 |  | IOVDD−DGND | −0.3 | 5.5 | V | S1 p7 |
| 模拟/参考脚 |  | AINx/GPIOx/REFPx/REFNx/REFCOM | AVSS−0.3 | AVDD+0.3 | V | S1 p7 |
| 数字脚 |  | CS/SCLK/DIN/DOUT/DRDY/START/RESET/CLK | DGND−0.3 | IOVDD+0.3 | V | S1 p7 |
| 连续脚电流 |  | AVSS-SW/REFN0/REFOUT | −100 | 100 | mA | S1 p7 |
| 其他非供电脚电流 |  |  | −10 | 10 | mA | S1 p7 |
| 结温 | TJ |  |  | 150 | °C | S1 p7 |
| 储存温度 | Tstg |  | −60 | 150 | °C | S1 p7 |

## 推荐工作条件

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
|---|---|---|---|---|---|---|---|
| 模拟供电差 |  | AVDD−AVSS | 2.7 |  | 5.25 | V | S1 p8 |
| 模拟负供电 |  | AVSS−DGND | −2.625 | 0 | 0.05 | V | S1 p8 |
| 模拟正供电 |  | AVDD−DGND | 1.5 |  | 5.25 | V | S1 p8 |
| 核心供电 |  | DVDD−DGND | 2.7 |  | 3.6 | V | S1 p8 |
| 接口供电 |  | IOVDD−DGND | DVDD |  | 5.25 | V | S1 p8 |
| 绝对模拟输入 | V(AINx) | PGA旁路 | AVSS−0.05 |  | AVDD+0.05 | V | S1 p8 |
| 绝对模拟输入 | V(AINx) | PGA增益1到16 | AVSS+0.15+绝对值(VINMAX)×(Gain−1)/2 |  | AVDD−0.15−绝对值(VINMAX)×(Gain−1)/2 | V | S1 p8 |
| 绝对模拟输入 | V(AINx) | PGA增益32到128 | AVSS+0.15+15.5×绝对值(VINMAX) |  | AVDD−0.15−15.5×绝对值(VINMAX) | V | S1 p8 |
| 差分输入 | VIN | AINP−AINN | −VREF/Gain |  | VREF/Gain | V | S1 p8 |
| 差分参考 | VREF | REFPx−REFNx | 0.5 |  | AVDD−AVSS | V | S1 p8 |
| 负参考电压 | V(REFNx) | 缓冲关闭 | AVSS−0.05 |  | V(REFPx)−0.5 | V | S1 p8 |
| 负参考电压 | V(REFNx) | 缓冲开启 | AVSS |  | V(REFPx)−0.5 | V | S1 p8 |
| 正参考电压 | V(REFPx) | 缓冲关闭 | V(REFNx)+0.5 |  | AVDD+0.05 | V | S1 p8 |
| 正参考电压 | V(REFPx) | 缓冲开启 | V(REFNx)+0.5 |  | AVDD | V | S1 p8 |
| 外部时钟 | fCLK |  | 2 | 4.096 | 4.5 | MHz | S1 p8 |
| 外部时钟占空比 |  |  | 40 | 50 | 60 | % | S1 p8 |
| GPIO输入 |  |  | AVSS−0.05 |  | AVDD+0.05 | V | S1 p8 |
| 其他数字输入 |  |  | DGND |  | IOVDD | V | S1 p8 |
| 环境温度 | TA |  | −50 |  | 125 | °C | S1 p8 |

## 电气特性

上下限−50到125 °C，典型25 °C；AVDD=2.7到5.25 V、AVSS=0、DVDD=IOVDD=3.3 V，全部增益/数据率，内部参考/振荡器，全局斩波禁用，另注明者除外。基础模拟电流另在AVDD=3.3 V、外参考、内参考/缓冲/IDAC/VBIAS/标志禁用、VIN=0；附加功能电流需另计。时序负载20 pF并100 kΩ到DGND（S1 p9、p10、p11、p12、p13、p14）。

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
|---|---|---|---|---|---|---|---|
| 绝对输入电流 |  | PGA开启，全部增益，输入在规定范围 | −2 | 0.1 | 2 | nA | S1 p9 |
| 差分输入电流 |  | PGA开启，VCM=AVDD/2，差分在±VREF/Gain内 | −1 | 0.02 | 1 | nA | S1 p9 |
| 无失码分辨率 |  |  | 24 |  |  | Bits | S1 p9 |
| 积分非线性 | INL | 最佳拟合，PGA旁路，VCM=AVDD/2 |  | 1 | 10 | ppmFSR | S1 p9 |
| 积分非线性 | INL | PGA增益1到8，VCM=AVDD/2 |  | 2 | 15 | ppmFSR | S1 p9 |
| 积分非线性 | INL | PGA增益16到128，VCM=AVDD/2，−40到85 °C |  | 3 | 15 | ppmFSR | S1 p9 |
| 输入失调 | VIO | 25 °C，PGA旁路 | −120 | 20 | 120 | µV | S1 p9 |
| 输入失调 | VIO | 25 °C，PGA增益1到8 | −120/Gain | 20/Gain | 120/Gain | µV | S1 p9 |
| 输入失调 | VIO | 25 °C，PGA增益16到128 | −15 | 2 | 15 | µV | S1 p9 |
| 输入失调 | VIO | 25 °C，PGA旁路，全局斩波 | −2 | 0.2 | 2 | µV | S1 p9 |
| 输入失调 | VIO | 25 °C，PGA增益1到128，全局斩波 | −2 | 0.2 | 2 | µV | S1 p9 |
| 输入失调 | VIO | −40到85 °C，PGA旁路 | −75 | 10 | 75 | µV | S1 p9 |
| 输入失调 | VIO | −40到85 °C，PGA增益1到128 | −100 | 15 | 100 | µV | S1 p9 |
| 失调温漂 |  | PGA旁路 | −75 | 10 | 75 | nV/°C | S1 p9 |
| 失调温漂 |  | PGA增益1到8 | −200 | 15 | 200 | nV/°C | S1 p9 |
| 失调温漂 |  | PGA增益16到128 | −150 | 15 | 150 | nV/°C | S1 p9 |
| 失调温漂 |  | PGA旁路，全局斩波 | −10 | 2 | 10 | nV/°C | S1 p9 |
| 失调温漂 |  | PGA增益1到128，全局斩波 | −10 | 2 | 10 | nV/°C | S1 p9 |
| 增益误差 |  | 25 °C，PGA旁路，排除参考误差 |  | 40 | 120 | ppm | S1 p10 |
| 增益误差 |  | 25 °C，PGA增益1到32，排除参考误差 |  | 40 | 120 | ppm | S1 p10 |
| 增益误差 |  | 25 °C，PGA增益64/128，排除参考误差 |  | 40 | 200 | ppm | S1 p10 |
| 增益温漂 |  | PGA旁路，−40到85 °C，排除参考误差 |  | 0.5 | 1 | ppm/°C | S1 p10 |
| 增益温漂 |  | PGA开启，−40到85 °C，排除参考误差 |  | 0.5 | 2 | ppm/°C | S1 p10 |
| 增益温漂 |  | PGA旁路，全温，排除参考误差 |  | 0.5 | 1 | ppm/°C | S1 p10 |
| 增益温漂 |  | PGA开启，全温，排除参考误差 |  | 1 | 4 | ppm/°C | S1 p10 |
| 参考输入电流 |  | 外部2.5 V，REFP1/REFN1，缓冲关闭 | −6 | 4 | 6 | µA/V | S1 p11 |
| 参考输入电流 |  | 外部2.5 V，REFP1/REFN1，缓冲开启 | −15 | 5 | 15 | nA | S1 p11 |
| 内部参考精度 |  | 25 °C，TQFP | −0.05 | ±0.01 | 0.05 | % | S1 p11 |
| 内部参考精度 |  | 25 °C，VQFN | −0.1 | ±0.01 | 0.1 | % | S1 p11 |
| 内部参考温漂 |  | −40到85 °C |  | 2.5 | 8 | ppm/°C | S1 p11 |
| 内部参考温漂 |  | −50到125 °C |  | 3 | 10 | ppm/°C | S1 p11 |
| 内部参考输出电流 |  | AVDD=2.7到3.3 V，源或吸 | −5 |  | 5 | mA | S1 p11 |
| 内部参考输出电流 |  | AVDD=3.3到5.25 V，源或吸 | −10 |  | 10 | mA | S1 p11 |
| 内部参考短路限流 |  | 源或吸 |  | 70 | 100 | mA | S1 p11 |
| 内部参考稳定电容 |  | REFOUT | 1 |  | 47 | µF | S1 p11 |
| 内部时钟精度 |  |  | −1.5 |  | 1.5 | % | S1 p11 |
| IDAC顺从电压 |  | 10到750 µA，偏离标称不超过0.1% | AVSS |  | AVDD−0.4 | V | S1 p11 |
| IDAC顺从电压 |  | 1到2 mA，偏离标称不超过0.1% | AVSS |  | AVDD−0.6 | V | S1 p11 |
| IDAC单路精度 |  | 25 °C，10到100 µA | −5 | ±0.7 | 5 | % | S1 p11 |
| IDAC单路精度 |  | 25 °C，250 µA到2 mA | −3 | ±0.5 | 3 | % | S1 p11 |
| 两路IDAC失配 |  | 25 °C，10到100 µA |  | 0.15 | 0.8 | % | S1 p11 |
| 两路IDAC失配 |  | 25 °C，250到750 µA |  | 0.10 | 0.6 | % | S1 p11 |
| 两路IDAC失配 |  | 25 °C，1到2 mA |  | 0.07 | 0.4 | % | S1 p11 |
| IDAC温漂 |  | 10到750 µA |  | 20 | 120 | ppm/°C | S1 p11 |
| IDAC温漂 |  | 1到2 mA |  | 10 | 80 | ppm/°C | S1 p11 |
| 两路IDAC温漂匹配 |  | 10到100 µA |  | 3 | 25 | ppm/°C | S1 p11 |
| 两路IDAC温漂匹配 |  | 250 µA到2 mA |  | 2 | 15 | ppm/°C | S1 p11 |
| 参考检测二档精度 |  |  | −3 | ±1 | 3 | % | S1 p12 |
| 低侧开关导通电阻 | RON |  |  | 1 | 3 | Ω | S1 p12 |
| 低侧开关电流 |  |  |  |  | 75 | mA | S1 p12 |
| GPIO输入低 | VIL |  | AVSS−0.05 |  | 0.3 × AVDD | V | S1 p12 |
| GPIO输入高 | VIH |  | 0.7 × AVDD |  | AVDD+0.05 | V | S1 p12 |
| GPIO输出低 | VOL | IOL=1 mA | AVSS |  | 0.2 × AVDD | V | S1 p12 |
| GPIO输出高 | VOH | IOH=1 mA | 0.8 × AVDD |  | AVDD | V | S1 p12 |
| 数字输入低 | VIL |  | DGND |  | 0.3 × IOVDD | V | S1 p12 |
| 数字输入高 | VIH |  | 0.7 × IOVDD |  | IOVDD | V | S1 p12 |
| 数字输出低 | VOL | IOL=1 mA | DGND |  | 0.2 × IOVDD | V | S1 p12 |
| 数字输出高 | VOH | IOH=1 mA | 0.8 × IOVDD |  | IOVDD | V | S1 p12 |
| 数字输入电流 |  | 输入在DGND到IOVDD | −1 |  | 1 | µA | S1 p12 |
| 模拟掉电电流 | IAVDD | 规定基础电流条件 |  | 0.1 | 1.5 | µA | S1 p13 |
| 模拟转换电流 | IAVDD | PGA增益1/2，规定基础电流条件 |  | 120 | 135 | µA | S1 p13 |
| 模拟转换电流 | IAVDD | PGA增益4/8，规定基础电流条件 |  | 140 | 155 | µA | S1 p13 |
| 模拟转换电流 | IAVDD | PGA增益16/32，规定基础电流条件 |  | 165 | 180 | µA | S1 p13 |
| 内部参考附加电流 | IAVDD | AVDD=3.3 V，2.5 V参考空载 |  | 185 | 280 | µA | S1 p13 |
| 正参考缓冲附加电流 | IAVDD | AVDD=3.3 V |  | 35 | 60 | µA | S1 p13 |
| 负参考缓冲附加电流 | IAVDD | AVDD=3.3 V |  | 25 | 40 | µA | S1 p13 |
| IDAC开销附加电流 | IAVDD | AVDD=3.3 V，10到250 µA，不含源电流本身 |  | 20 | 35 | µA | S1 p13 |
| 数字转换电流 | IDVDD+IIOVDD | 3.3 V，内时钟，所有速率，SPI不活动 |  | 225 | 300 | µA | S1 p13 |
| 常模抑制 | NMRR | 50/60 Hz ±1 Hz，10 SPS，sinc3，内部时钟 | 88 |  |  | dB | S1 p10 |
| 常模抑制 | NMRR | 50/60 Hz ±1 Hz，10 SPS，sinc3，外4.096 MHz | 102 |  |  | dB | S1 p10 |
| 常模抑制 | NMRR | 50/60 Hz ±1 Hz，20 SPS，低延迟，内部时钟 | 79 |  |  | dB | S1 p10 |
| 常模抑制 | NMRR | 50/60 Hz ±1 Hz，20 SPS，低延迟，外4.096 MHz | 95 |  |  | dB | S1 p10 |
| 常模抑制 | NMRR | 50 Hz ±1 Hz，50 SPS，sinc3，内部时钟 | 87 |  |  | dB | S1 p10 |
| 常模抑制 | NMRR | 50 Hz ±1 Hz，50 SPS，sinc3，外4.096 MHz | 101 |  |  | dB | S1 p10 |
| 常模抑制 | NMRR | 60 Hz ±1 Hz，60 SPS，sinc3，内部时钟 | 89 |  |  | dB | S1 p10 |
| 常模抑制 | NMRR | 60 Hz ±1 Hz，60 SPS，sinc3，外4.096 MHz | 105 |  |  | dB | S1 p10 |
| 共模抑制 | CMRR | 直流 | 110 | 120 |  | dB | S1 p10 |
| 共模抑制 | CMRR | 50/60 Hz ±1 Hz，2.5到10 SPS，sinc3 | 120 | 130 |  | dB | S1 p10 |
| 共模抑制 | CMRR | 50/60 Hz ±1 Hz，2.5/5/10/20 SPS，低延迟 | 115 | 125 |  | dB | S1 p10 |
| 供电抑制 | PSRR | AVDD直流 | 90 | 105 |  | dB | S1 p10 |
| 供电抑制 | PSRR | AVDD 50/60 Hz | 100 | 115 |  | dB | S1 p10 |
| 供电抑制 | PSRR | DVDD直流 | 100 | 115 |  | dB | S1 p10 |
| 片选至首时钟 | td(CSSC) | 时序定义及特殊条件见原表；tCLK=1/fCLK | 20 |  |  | ns | S1 p14 |
| 末时钟至片选 | td(SCCS) | 时序定义及特殊条件见原表；tCLK=1/fCLK | 20 |  |  | ns | S1 p14 |
| 片选高脉宽 | tw(CSH) | 时序定义及特殊条件见原表；tCLK=1/fCLK | 30 |  |  | ns | S1 p14 |
| 串行周期 | tc(SC) | 时序定义及特殊条件见原表；tCLK=1/fCLK | 100 |  |  | ns | S1 p14 |
| 时钟高脉宽 | tw(SCH) | 时序定义及特殊条件见原表；tCLK=1/fCLK | 40 |  |  | ns | S1 p14 |
| 时钟低脉宽 | tw(SCL) | 时序定义及特殊条件见原表；tCLK=1/fCLK | 40 |  |  | ns | S1 p14 |
| 数据建立 | tsu(DI) | 时序定义及特殊条件见原表；tCLK=1/fCLK | 15 |  |  | ns | S1 p14 |
| 数据保持 | th(DI) | 时序定义及特殊条件见原表；tCLK=1/fCLK | 20 |  |  | ns | S1 p14 |
| 命令间延迟 | td(CMD) | 时序定义及特殊条件见原表；tCLK=1/fCLK | 0 |  |  | ns | S1 p14 |
| 复位低脉宽 | tw(RSL) | 时序定义及特殊条件见原表；tCLK=1/fCLK | 4 |  |  | tCLK | S1 p14 |
| 复位释放等待 | td(RSSC) | 时序定义及特殊条件见原表；tCLK=1/fCLK | 4096 |  |  | tCLK | S1 p14 |
| 开始高脉宽 | tw(STH) | 时序定义及特殊条件见原表；tCLK=1/fCLK | 4 |  |  | tCLK | S1 p14 |
| 开始低脉宽 | tw(STL) | 时序定义及特殊条件见原表；tCLK=1/fCLK | 4 |  |  | tCLK | S1 p14 |
| 停止转换建立 | tsu(STDR) | 时序定义及特殊条件见原表；tCLK=1/fCLK | 32 |  |  | tCLK | S1 p14 |
| 无RDATA读取保持 | th(SCDR) | 时序定义及特殊条件见原表；tCLK=1/fCLK | 28 |  |  | tCLK | S1 p14 |
| 无RDATA读取等待 | td(DRSC) | 时序定义及特殊条件见原表；tCLK=1/fCLK | 4 |  |  | tCLK | S1 p14 |
| 片选使能输出 | tp(CSDO) | 时序定义及特殊条件见原表；tCLK=1/fCLK | 0 |  | 25 | ns | S1 p14 |
| 时钟至新数据 | tp(SCDO) | 时序定义及特殊条件见原表；tCLK=1/fCLK | 3 |  | 30 | ns | S1 p14 |
| 片选释放高阻 | tp(CSDOZ) | 时序定义及特殊条件见原表；tCLK=1/fCLK | 0 |  | 25 | ns | S1 p14 |
| 开始至就绪上升 | tp(STDR) | 时序定义及特殊条件见原表；tCLK=1/fCLK |  |  | 2 | tCLK | S1 p14 |
| 就绪高脉宽 | tw(DRH) | 时序定义及特殊条件见原表；tCLK=1/fCLK | 24 |  |  | tCLK | S1 p14 |
| GPIO更新 | tp(GPIO) | 时序定义及特殊条件见原表；tCLK=1/fCLK | 3 |  | 100 | ns | S1 p14 |
| 每字节SPI超时 |  | 时序定义及特殊条件见原表；tCLK=1/fCLK | 215 |  |  | tCLK | S1 p14 |

用这些数时要注意：

- PGA旁路输入电流、PGA开启时间、噪声、参考输出电压/负载调整/启动/噪声、BOCS、偏置、温度传感器和许多功能电流仅典型。内部偏移校准后的残差仅描述为噪声量级，未给数值限值，不补数（S1 p9、p10、p11、p12、p13）。
- 增益误差与温漂排除参考误差。高增益INL只给−40到85 °C；部分失调、参考/IDAC精度只室温。GPIO逻辑基于模拟电源，不是IOVDD（S1 p9、p10、p11、p12）。
- AVDD/DVDD上电可任意，但IOVDD建议先于或同时DVDD，否则可能需复位；未用数字输入不可悬空。REFN0存在低侧开关短路风险，未用只悬空或接AVSS（S1 p89、p98）。

## 热特性

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
|---|---|---|---|---|---|
| 结到环境热阻 | RθJA | 封装列顺序见下文 | 45.2 / 75.5 | °C/W | S1 p8 |
| 结到壳顶热阻 | RθJC(top) | 封装列顺序见下文 | 28.3 / 17.1 | °C/W | S1 p8 |
| 结到板热阻 | RθJB | 封装列顺序见下文 | 15.8 / 28.5 | °C/W | S1 p8 |
| 结到顶热特性参数 | ψJT | 封装列顺序见下文 | 0.4 / 0.4 | °C/W | S1 p8 |
| 结到板热特性参数 | ψJB | 封装列顺序见下文 | 15.7 / 28.3 | °C/W | S1 p8 |
| 结到壳底热阻 | RθJC(bot) | 封装列顺序见下文 | 2.3 | °C/W | S1 p8 |

封装顺序RHB、PBS；壳底热阻仅RHB，PBS为n/a（S1 p8）。

## 静电额定

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
|---|---|---|---|---|---|
| 人体模型 | V(ESD) | JS-001 | ±2500 | V | S1 p7 |
| 带电器件模型 | V(ESD) | JESD22-C101 | ±1000 | V | S1 p7 |

## 引脚与处置

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
|---|---|---|---|---|
| 1 AINCOM | Analog input，单端公共输入 | 见模拟范围 | 未用可悬空/接中点/AVDD | S1 p6、p89 |
| 2 AIN5；3 AIN4；4 AIN3；5 AIN2；6 AIN1；7 AIN0 | Analog input，模拟输入 | 见模拟范围 | 未用可悬空/接中点/AVDD | S1 p6、p89 |
| 8 START/SYNC | Digital input，转换/同步 | 见数字范围 | 不用接DGND | S1 p6、p89 |
| 9 CS | Digital input，低有效片选 | 见数字范围 | 不用接DGND | S1 p6、p89 |
| 10 DIN；11 SCLK | Digital input，数据/时钟 | 见数字范围 | 未用须接明确逻辑电平 | S1 p6、p89 |
| 12 DOUT/DRDY | Digital output，数据/低有效就绪 | 见数字范围 |  | S1 p6 |
| 13 DRDY | Digital output，低有效就绪 | 见数字范围 | 可不接或弱上拉IOVDD | S1 p6、p89 |
| 14 DGND | Digital ground |  | 接数字地 | S1 p6 |
| 15 IOVDD | Digital supply，接口供电 | DVDD到5.25 V | 非共DVDD时须旁路 | S1 p6、p8 |
| 16 DVDD | Digital supply，核心供电 | 2.7到3.6 V | 须旁路 | S1 p6、p8 |
| 17 CLK | Digital input，外部时钟 | 见数字范围 | 用内部时钟时接DGND | S1 p6 |
| 18 RESET | Digital input，低有效复位 | 见数字范围 | 不用接IOVDD | S1 p6、p89 |
| 19 GPIO3/AIN11；20 GPIO2/AIN10；21 GPIO1/AIN9；22 GPIO0/AIN8 | Analog input/output，GPIO；AIN功能仅S08 | 按模拟供电逻辑 | 数字输入不可浮空；未用数字输出经下拉到AVSS并输出零；S06默认配置按未用模拟脚接 | S1 p6、p89 |
| 23 REFOUT | Analog output，内部正参考 |  | 使能时接稳定电容 | S1 p6 |
| 24 REFCOM | Analog output，负参考 |  | 接AVSS | S1 p6 |
| 25 NC | —，无连接 |  | 可不接或接AVSS | S1 p6 |
| 26 AVDD | Analog supply，正供电 | 见模拟供电范围 | 须旁路 | S1 p6 |
| 27 AVSS | Analog supply，负供电 | 见模拟供电范围 |  | S1 p6 |
| 28 AVSS-SW | Analog supply，低侧开关端 |  | 接AVSS | S1 p6、p55 |
| 29 REFN0 | Analog input，外部参考负端 | 见参考范围 | 未用仅悬空或接AVSS，避免内部开关意外短路 | S1 p6、p89 |
| 30 REFP0 | Analog input，外部参考正端 | 见参考范围 | 未用可悬空/接中点/AVDD | S1 p6、p89 |
| 31 REFN1/AIN7；32 REFP1/AIN6 | Analog input，第二参考；AIN功能仅S08 | 见参考/模拟范围 | 未用按模拟输入处置 | S1 p6、p89 |
| 散热焊盘 | 仅RHB有，接AVSS；未明示内部连接及必须焊接；PBS无此焊盘 |  | 接AVSS | S1 p6 |

## 必需外围

- AVDD–AVSS至少330 nF，DVDD–DGND至少100 nF，IOVDD未与DVDD相连时同样至少100 nF；内部参考开启时REFOUT–REFCOM为1到47 µF，REFCOM接AVSS。AVSS-SW接AVSS；外时钟可省，省略时CLK接DGND。差分模拟输入布局建议差分电容，未给通用容量（S1 p6、p11、p55、p98、p99）。

## 订货型号与封装

S06为六路、S08为十二路模拟输入，某些共用脚在S06仅为GPIO/参考；RHB/PBS脚序相同，但只有RHB有热焊盘，参考精度和热数据按封装区分（S1 p5、p6、p8、p11）。

| 订货型号或后缀 | 封装 | 脚数 | 电压或功能档 | 温度范围 | 引脚镀层 | 来源 |
|---|---|---|---|---|---|---|
| ADS124S06IPBS | TQFP (PBS) | 32 |  | -50 to 125 | NIPDAU | S1 p103 |
| ADS124S06IPBS.A | TQFP (PBS) | 32 |  | -50 to 125 | NIPDAU | S1 p103 |
| ADS124S06IPBS.B | TQFP (PBS) | 32 |  | -50 to 125 | NIPDAU | S1 p103 |
| ADS124S06IPBSG4 | TQFP (PBS) | 32 |  | -50 to 125 | NIPDAU | S1 p103 |
| ADS124S06IPBSG4.A | TQFP (PBS) | 32 |  | -50 to 125 | NIPDAU | S1 p103 |
| ADS124S06IPBSG4.B | TQFP (PBS) | 32 |  | -50 to 125 | NIPDAU | S1 p103 |
| ADS124S06IPBSR | TQFP (PBS) | 32 |  | -50 to 125 | NIPDAU | S1 p103 |
| ADS124S06IPBSR.A | TQFP (PBS) | 32 |  | -50 to 125 | NIPDAU | S1 p103 |
| ADS124S06IPBSR.B | TQFP (PBS) | 32 |  | -50 to 125 | NIPDAU | S1 p103 |
| ADS124S06IRHBR | VQFN (RHB) | 32 |  | -50 to 125 | NIPDAU | S1 p103 |
| ADS124S06IRHBR.A | VQFN (RHB) | 32 |  | -50 to 125 | NIPDAU | S1 p103 |
| ADS124S06IRHBR.B | VQFN (RHB) | 32 |  | -50 to 125 | NIPDAU | S1 p103 |
| ADS124S06IRHBT | VQFN (RHB) | 32 |  | -50 to 125 | NIPDAU | S1 p103 |
| ADS124S06IRHBT.A | VQFN (RHB) | 32 |  | -50 to 125 | NIPDAU | S1 p103 |
| ADS124S06IRHBT.B | VQFN (RHB) | 32 |  | -50 to 125 | NIPDAU | S1 p103 |
| ADS124S08IPBS | TQFP (PBS) | 32 |  | -50 to 125 | NIPDAU | S1 p103 |
| ADS124S08IPBS.A | TQFP (PBS) | 32 |  | -50 to 125 | NIPDAU | S1 p103 |
| ADS124S08IPBS.B | TQFP (PBS) | 32 |  | -50 to 125 | NIPDAU | S1 p103 |
| ADS124S08IPBSR | TQFP (PBS) | 32 |  | -50 to 125 | NIPDAU | S1 p104 |
| ADS124S08IPBSR.A | TQFP (PBS) | 32 |  | -50 to 125 | NIPDAU | S1 p104 |
| ADS124S08IPBSR.B | TQFP (PBS) | 32 |  | -50 to 125 | NIPDAU | S1 p104 |
| ADS124S08IPBSRG4 | TQFP (PBS) | 32 |  | -50 to 125 | NIPDAU | S1 p104 |
| ADS124S08IPBSRG4.A | TQFP (PBS) | 32 |  | -50 to 125 | NIPDAU | S1 p104 |
| ADS124S08IPBSRG4.B | TQFP (PBS) | 32 |  | -50 to 125 | NIPDAU | S1 p104 |
| ADS124S08IRHBR | VQFN (RHB) | 32 |  | -50 to 125 | NIPDAU | S1 p104 |
| ADS124S08IRHBR.A | VQFN (RHB) | 32 |  | -50 to 125 | NIPDAU | S1 p104 |
| ADS124S08IRHBR.B | VQFN (RHB) | 32 |  | -50 to 125 | NIPDAU | S1 p104 |
| ADS124S08IRHBRG4 | VQFN (RHB) | 32 |  | -50 to 125 | NIPDAU | S1 p104 |
| ADS124S08IRHBRG4.A | VQFN (RHB) | 32 |  | -50 to 125 | NIPDAU | S1 p104 |
| ADS124S08IRHBRG4.B | VQFN (RHB) | 32 |  | -50 to 125 | NIPDAU | S1 p104 |
| ADS124S08IRHBT | VQFN (RHB) | 32 |  | -50 to 125 | NIPDAU | S1 p104 |
| ADS124S08IRHBT.A | VQFN (RHB) | 32 |  | -50 to 125 | NIPDAU | S1 p104 |
| ADS124S08IRHBT.B | VQFN (RHB) | 32 |  | -50 to 125 | NIPDAU | S1 p104 |

器件生命周期状态不在本条目收录，设计时查厂家网站并记录日期。

## 核对记录

- 2026-11-10：逐页对照原件抽取，工具核对通过（PASS）；核对了 399 个数，问题 0 条，没核对 0 处。
