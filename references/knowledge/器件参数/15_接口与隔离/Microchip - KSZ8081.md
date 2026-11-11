# Microchip KSZ8081

类别：器件参数。
器件：10/100BASE-T PHY；本手册型号是KSZ8081MNX（MII）与KSZ8081RNB（RMII）。
手册：Micrel Revision 1.4，2015-08-19。

## 来源

- S1：Datasheet/15_接口与隔离/以太网PHY/Microchip - KSZ8081.pdf

页码均为 PDF 文件页序，共 69 页。

## 绝对最大值

| 参数 | 符号 | 条件 | 最小 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| 核心电源 | VIN | VDD_1.2 | −0.5 | 1.8 | V | S1 p52 |
| 模拟/I/O电源 | VIN | VDDIO、VDDA_3.3 | −0.5 | 5.0 | V | S1 p52 |
| 全部输入电压 |  | 对地 | −0.5 | 5.0 | V | S1 p52 |
| 全部输出电压 |  | 对地 | −0.5 | 5.0 | V | S1 p52 |
| 焊接引脚温度 |  | 10 s |  | 260 | °C | S1 p52 |
| 储存温度 | TS |  | −55 | 150 | °C | S1 p52 |

## 推荐工作条件

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 模拟及3.3 V I/O电源 |  | VDDA_3.3、VDDIO_3.3 | 3.135 |  | 3.465 | V | S1 p52 |
| 2.5 V I/O电源 |  | VDDIO_2.5 | 2.375 |  | 2.625 | V | S1 p52 |
| 1.8 V I/O电源 |  | VDDIO_1.8 | 1.710 |  | 1.890 | V | S1 p52 |
| 环境温度 | TA | 商业级 | 0 |  | 70 | °C | S1 p52 |
| 环境温度 | TA | 工业级 | −40 |  | 85 | °C | S1 p52 |
| 结温 | TJ(MAX) |  |  |  | 125 | °C | S1 p52 |

## 电气特性

电气表注13明确TA=25 °C，仅封装成品；不能将该表保证扩展到全部工业温区。其他时序依各页定义。

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 输入高 | VIH | VDDIO=3.3 V；原表未给VOH/VOL负载电流 | 2 |  |  | V | S1 p52 |
| 输入低 | VIL | VDDIO=3.3 V；原表未给VOH/VOL负载电流 |  |  | 0.8 | V | S1 p52 |
| 输出高 | VOH | VDDIO=3.3 V；原表未给VOH/VOL负载电流 | 2.4 |  |  | V | S1 p52 |
| 输出低 | VOL | VDDIO=3.3 V；原表未给VOH/VOL负载电流 |  |  | 0.4 | V | S1 p52 |
| 输入高 | VIH | VDDIO=2.5 V；原表未给VOH/VOL负载电流 | 1.8 |  |  | V | S1 p52 |
| 输入低 | VIL | VDDIO=2.5 V；原表未给VOH/VOL负载电流 |  |  | 0.7 | V | S1 p52 |
| 输出高 | VOH | VDDIO=2.5 V；原表未给VOH/VOL负载电流 | 2 |  |  | V | S1 p52 |
| 输出低 | VOL | VDDIO=2.5 V；原表未给VOH/VOL负载电流 |  |  | 0.4 | V | S1 p52 |
| 输入高 | VIH | VDDIO=1.8 V；原表未给VOH/VOL负载电流 | 1.3 |  |  | V | S1 p52 |
| 输入低 | VIL | VDDIO=1.8 V；原表未给VOH/VOL负载电流 |  |  | 0.5 | V | S1 p52 |
| 输出高 | VOH | VDDIO=1.8 V；原表未给VOH/VOL负载电流 | 1.5 |  |  | V | S1 p52 |
| 输出低 | VOL | VDDIO=1.8 V；原表未给VOH/VOL负载电流 |  |  | 0.3 | V | S1 p52 |
| 输入电流 | IIN | VIN=GND～VDDIO |  |  | 10 | µA | S1 p52 |
| 三态漏电 | Ioz |  |  |  | 10 | µA | S1 p52 |
| 10BASE-T电流 | IDD1_3.3V | VDDA=VDDIO=3.3 V，满双工满载 |  | 41 |  | mA | S1 p52 |
| 100BASE-TX电流 | IDD2_3.3V | 同上 |  | 47 |  | mA | S1 p52 |
| EDPD电流 | IDD3_3.3V | 网线拔出，reg18h.11=0 |  | 20 |  | mA | S1 p52 |
| 掉电电流 | IDD4_3.3V | 软件掉电，reg0h.11=1 |  | 4 |  | mA | S1 p52 |
| LED驱动电流 | ILED | 每个LED0/LED1 |  | 8 |  | mA | S1 p52 |
| 内部上拉 | pu | 全部上下拉及strap脚，VDDIO=3.3 V | 30 | 45 | 73 | kΩ | S1 p53 |
| 内部下拉 | pd | 全部上下拉及strap脚，VDDIO=3.3 V | 26 | 43 | 79 | kΩ | S1 p53 |
| 内部上拉 | pu | 全部上下拉及strap脚，VDDIO=2.5 V | 39 | 61 | 102 | kΩ | S1 p53 |
| 内部下拉 | pd | 全部上下拉及strap脚，VDDIO=2.5 V | 34 | 59 | 113 | kΩ | S1 p53 |
| 内部上拉 | pu | 全部上下拉及strap脚，VDDIO=1.8 V | 48 | 99 | 178 | kΩ | S1 p53 |
| 内部下拉 | pd | 全部上下拉及strap脚，VDDIO=1.8 V | 53 | 99 | 200 | kΩ | S1 p53 |
| 百兆差分峰值 | VO | 1:1变压器后、差分100 Ω负载 | 0.95 |  | 1.05 | V | S1 p53 |
| 百兆输出不平衡 | VIMB | 同上 |  |  | 2 | % | S1 p53 |
| 百兆上升/下降 | tr、tf | 同上 | 3 |  | 5 | ns | S1 p53 |
| 百兆边沿不平衡 |  | 同上 | 0 |  | 0.5 | ns | S1 p53 |
| 百兆占空失真 |  | 同上 |  |  | ±0.25 | ns | S1 p53 |
| 百兆过冲 |  | 同上 |  |  | 5 | % | S1 p53 |
| 百兆输出抖动 |  | 峰峰值 |  | 0.7 |  | ns | S1 p53 |
| 十兆差分峰值 | VP | 1:1变压器后、差分100 Ω负载 | 2.2 |  | 2.8 | V | S1 p53 |
| 十兆附加抖动 |  | 峰峰值 |  |  | 3.5 | ns | S1 p53 |
| 十兆上升/下降 | tr、tf |  |  | 25 |  | ns | S1 p53 |
| 十兆静噪门限 | VSQ | 5 MHz方波 |  | 400 |  | mV | S1 p53 |
| 电流设定参考 | VSET | R(ISET)=6.49 kΩ |  | 0.65 |  | V | S1 p53 |
| RMII参考输出抖动 |  | 仅RNB的25 MHz输入/50 MHz输出，峰峰值 |  | 300 |  | ps | S1 p53 |
| XI至TXC相位延迟 |  | 仅MNX，百兆，25 MHz，均上升沿 | 15 | 20 | 25 | ns | S1 p53 |
| 链路丢失指示时间 | tllr | 百兆，LED模式00/01或INTRP指示 |  | 4.4 |  | µs | S1 p53 |
| TXC周期 | tP | MII十兆SQE；相对时钟上升沿，图示定义 |  | 400 |  | ns | S1 p54 |
| TXC低脉宽 | tWL | MII十兆SQE；相对时钟上升沿，图示定义 |  | 200 |  | ns | S1 p54 |
| TXC高脉宽 | tWH | MII十兆SQE；相对时钟上升沿，图示定义 |  | 200 |  | ns | S1 p54 |
| TXEN撤销至COL | tSQE | MII十兆SQE；相对时钟上升沿，图示定义 |  | 2.2 |  | µs | S1 p54 |
| COL脉宽 | tSQEP | MII十兆SQE；相对时钟上升沿，图示定义 |  | 1 |  | µs | S1 p54 |
| TXC周期 | tP | MII十兆发送；相对时钟上升沿，图示定义 |  | 400 |  | ns | S1 p55 |
| TXC低/高脉宽 | tWL、tWH | MII十兆发送；相对时钟上升沿，图示定义 |  | 200 |  | ns | S1 p55 |
| TXD建立 | tSU1 | MII十兆发送；相对时钟上升沿，图示定义 | 120 |  |  | ns | S1 p55 |
| TXEN建立 | tSU2 | MII十兆发送；相对时钟上升沿，图示定义 | 120 |  |  | ns | S1 p55 |
| TXD保持 | tHD1 | MII十兆发送；相对时钟上升沿，图示定义 | 0 |  |  | ns | S1 p55 |
| TXEN保持 | tHD2 | MII十兆发送；相对时钟上升沿，图示定义 | 0 |  |  | ns | S1 p55 |
| TXEN高至CRS | tCRS1 | MII十兆发送；相对时钟上升沿，图示定义 |  | 600 |  | ns | S1 p55 |
| TXEN低至CRS | tCRS2 | MII十兆发送；相对时钟上升沿，图示定义 |  | 1 |  | µs | S1 p55 |
| RXC周期 | tP | MII十兆接收；相对时钟上升沿，图示定义 |  | 400 |  | ns | S1 p56 |
| RXC低/高脉宽 | tWL、tWH | MII十兆接收；相对时钟上升沿，图示定义 |  | 200 |  | ns | S1 p56 |
| 接收数据有效/错误输出延迟 | tOD | MII十兆接收；相对时钟上升沿，图示定义 |  | 205 |  | ns | S1 p56 |
| CRS至数据延迟 | tRLAT | MII十兆接收；相对时钟上升沿，图示定义 |  | 7.2 |  | µs | S1 p56 |
| TXC周期 | tP | MII百兆发送；相对时钟上升沿，图示定义 |  | 40 |  | ns | S1 p57 |
| TXC低/高脉宽 | tWL、tWH | MII百兆发送；相对时钟上升沿，图示定义 |  | 20 |  | ns | S1 p57 |
| TXD建立 | tSU1 | MII百兆发送；相对时钟上升沿，图示定义 | 10 |  |  | ns | S1 p57 |
| TXEN建立 | tSU2 | MII百兆发送；相对时钟上升沿，图示定义 | 10 |  |  | ns | S1 p57 |
| TXD保持 | tHD1 | MII百兆发送；相对时钟上升沿，图示定义 | 0 |  |  | ns | S1 p57 |
| TXEN保持 | tHD2 | MII百兆发送；相对时钟上升沿，图示定义 | 0 |  |  | ns | S1 p57 |
| TXEN高/低至CRS | tCRS1、tCRS2 | MII百兆发送；相对时钟上升沿，图示定义 |  | 72 |  | ns | S1 p57 |
| RXC周期 | tP | MII百兆接收；相对时钟上升沿，图示定义 |  | 40 |  | ns | S1 p58 |
| RXC低/高脉宽 | tWL、tWH | MII百兆接收；相对时钟上升沿，图示定义 |  | 20 |  | ns | S1 p58 |
| 接收数据有效/错误输出延迟 | tOD | MII百兆接收；相对时钟上升沿，图示定义 | 16 | 21 | 25 | ns | S1 p58 |
| CRS至数据延迟 | tRLAT | MII百兆接收；相对时钟上升沿，图示定义 |  | 170 |  | ns | S1 p58 |
| 周期 | tCYC | RNB：25 MHz XI、50 MHz REF_CLK输出 |  | 20 |  | ns | S1 p59 |
| 建立 | t1 | RNB：25 MHz XI、50 MHz REF_CLK输出 | 4 |  |  | ns | S1 p59 |
| 保持 | t2 | RNB：25 MHz XI、50 MHz REF_CLK输出 | 2 |  |  | ns | S1 p59 |
| 输出延迟 | tOD | RNB：25 MHz XI、50 MHz REF_CLK输出 | 7 | 10 | 13 | ns | S1 p59 |
| 周期 | tCYC | RNB：50 MHz XI输入 |  | 20 |  | ns | S1 p59 |
| 建立 | t1 | RNB：50 MHz XI输入 | 4 |  |  | ns | S1 p59 |
| 保持 | t2 | RNB：50 MHz XI输入 | 2 |  |  | ns | S1 p59 |
| 输出延迟 | tOD | RNB：50 MHz XI输入 | 8 | 11 | 13 | ns | S1 p59 |
| FLP突发间隔 | tBTB | 自协商FLP | 8 | 16 | 24 | ms | S1 p60 |
| FLP突发宽度 | tFLPW | 自协商FLP |  | 2 |  | ms | S1 p60 |
| 时钟/数据脉宽 | tPW | 自协商FLP |  | 100 |  | ns | S1 p60 |
| 时钟至数据 | tCTD | 自协商FLP | 55.5 | 64 | 69.5 | µs | S1 p60 |
| 时钟至时钟 | tCTC | 自协商FLP | 111 | 128 | 139 | µs | S1 p60 |
| 每突发脉冲数 |  | 自协商FLP | 17 |  | 33 | 个 | S1 p60 |
| 管理时钟 | fc | MDC |  | 2.5 | 10 | MHz | S1 p61 |
| MDC周期 | tP |  |  | 400 |  | ns | S1 p61 |
| 管理输入建立 | tMD1 | MDIO输入至MDC上升沿 | 10 |  |  | ns | S1 p61 |
| 管理输入保持 | tMD2 | MDC上升沿后 | 4 |  |  | ns | S1 p61 |
| 管理输出延迟 | tMD3 | MDC上升沿后 | 5 | 222 |  | ns | S1 p61 |
| 供电上升时间 | tVR | VDDIO/VDDA单调上升；tVR按10%～90% | 300 |  |  | µs | S1 p62 |
| 供电稳定至释放复位 | tSR | VDDIO/VDDA单调上升；tVR按10%～90% | 10 |  |  | ms | S1 p62 |
| 绑带建立 | tCS | VDDIO/VDDA单调上升；tVR按10%～90% | 5 |  |  | ns | S1 p62 |
| 绑带保持 | tCH | VDDIO/VDDA单调上升；tVR按10%～90% | 5 |  |  | ns | S1 p62 |
| 复位至绑带脚输出 | tRC | VDDIO/VDDA单调上升；tVR按10%～90% | 6 |  |  | ns | S1 p62 |
| 热复位低脉宽 |  | VDDIO/VDDA单调上升；tVR按10%～90% | 500 |  |  | µs | S1 p62 |
| 复位后管理编程等待 |  | VDDIO/VDDA单调上升；tVR按10%～90% | 100 |  |  | µs | S1 p62 |

用这些数时要注意：

- 电流、LED驱动、输出抖动、静噪门限、ISET参考、链路丢失响应、若干MII周期/延迟仅典型。MDIO输出延迟仅给最小5 ns与典型222 ns，无最大值（S1 p52～p61）。
- 功耗电流含发送驱动及内部1.2 V稳压器；不把内部核心输出当外部电源输入。CMOS VOH/VOL没有列测试负载，不能自行补充驱动能力（S1 p9、p52）。
- 复位释放采样绑带；若MAC干扰，外加4.7 kΩ上拉或1 kΩ下拉。电源上升时间最小300 µs，不能误当最大；复位稳定后需等10 ms再释放，热复位低至少500 µs（S1 p12、p18、p62）。

## 热特性

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- |
| 结到环境 | θJA | QFN32 | 34 | °C/W | S1 p52 |
| 结到壳 | θJC | QFN32 | 6 | °C/W | S1 p52 |

## 静电额定

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- |
| 人体模型 | HBM | 首页额定，未列单独试验标准 | 6 | kV | S1 p1 |

未给CDM或单独静电敏感警告；超绝对最大值可能永久损坏（S1 p52）。

## 引脚与处置

### KSZ8081MNX

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
| --- | --- | --- | --- | --- |
| 1 GND | GND；GND | 见供电/电气限值 | 必须接地 | S1 p9 |
| 2 VDD_1.2 | P；VDD_1.2 | 见供电/电气限值 |  | S1 p9 |
| 3 VDDA_3.3 | P；VDDA_3.3 | 见供电/电气限值 |  | S1 p9 |
| 4 RXM | I/O；RXM | 见供电/电气限值 |  | S1 p9 |
| 5 RXP | I/O；RXP | 见供电/电气限值 |  | S1 p9 |
| 6 TXM | I/O；TXM | 见供电/电气限值 |  | S1 p9 |
| 7 TXP | I/O；TXP | 见供电/电气限值 |  | S1 p9 |
| 8 XO | O；XO | 见供电/电气限值 | 外部时钟时XO不连接 | S1 p9 |
| 9 XI | I；XI | 见供电/电气限值 |  | S1 p9 |
| 10 REXT | I；REXT | 见供电/电气限值 |  | S1 p9 |
| 11 MDIO | Ipu/Opu；MDIO | 见供电/电气限值 |  | S1 p9 |
| 12 MDC | Ipu；MDC | 见供电/电气限值 |  | S1 p9 |
| 13 RXD3/PHYAD0 | Ipu/O；RXD3/PHYAD0 | 见供电/电气限值 | 按绑带采样条件，不能让MAC误驱动 | S1 p9 |
| 14 RXD2/PHYAD1 | Ipd/O；RXD2/PHYAD1 | 见供电/电气限值 | 按绑带采样条件，不能让MAC误驱动 | S1 p9 |
| 15 RXD1/PHYAD2 | Ipd/O；RXD1/PHYAD2 | 见供电/电气限值 | 按绑带采样条件，不能让MAC误驱动 | S1 p9 |
| 16 RXD0/DUPLEX | Ipu/O；RXD0/DUPLEX | 见供电/电气限值 | 按绑带采样条件，不能让MAC误驱动 | S1 p10 |
| 17 VDDIO | P；VDDIO | 见供电/电气限值 |  | S1 p10 |
| 18 RXDV/CONFIG2 | Ipd/O；RXDV/CONFIG2 | 见供电/电气限值 | 按绑带采样条件，不能让MAC误驱动 | S1 p10 |
| 19 RXC/B-CAST_OFF | Ipd/O；RXC/B-CAST_OFF | 见供电/电气限值 | 按绑带采样条件，不能让MAC误驱动 | S1 p10 |
| 20 RXER/ISO | Ipd/O；RXER/ISO | 见供电/电气限值 | 按绑带采样条件，不能让MAC误驱动 | S1 p10 |
| 21 INTRP/NAND_Tree# | Ipu/Opu；INTRP/NAND_Tree# | 见供电/电气限值 | 按绑带采样条件，不能让MAC误驱动 | S1 p10 |
| 22 TXC | Ipd/O；TXC | 见供电/电气限值 |  | S1 p10 |
| 23 TXEN | I；TXEN | 见供电/电气限值 |  | S1 p10 |
| 24 TXD0 | I；TXD0 | 见供电/电气限值 |  | S1 p10 |
| 25 TXD1 | I；TXD1 | 见供电/电气限值 |  | S1 p10 |
| 26 TXD2 | I；TXD2 | 见供电/电气限值 |  | S1 p10 |
| 27 TXD3 | I；TXD3 | 见供电/电气限值 |  | S1 p10 |
| 28 COL/CONFIG0 | Ipd/O；COL/CONFIG0 | 见供电/电气限值 | 按绑带采样条件，不能让MAC误驱动 | S1 p10 |
| 29 CRS/CONFIG1 | Ipd/O；CRS/CONFIG1 | 见供电/电气限值 | 按绑带采样条件，不能让MAC误驱动 | S1 p10 |
| 30 LED0/NWAYEN | Ipu/O；LED0/NWAYEN | 见供电/电气限值 | 按绑带采样条件，不能让MAC误驱动 | S1 p11 |
| 31 LED1/SPEED | Ipu/O；LED1/SPEED | 见供电/电气限值 | 按绑带采样条件，不能让MAC误驱动 | S1 p11 |
| 32 RST# | Ipu；RST# | 见供电/电气限值 |  | S1 p11 |
| 散热焊盘 PADDLE | GND；内部接地节点；原文只列地，未明确必须焊接 |  | 接地 | S1 p11 |

### KSZ8081RNB

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
| --- | --- | --- | --- | --- |
| 1 GND | GND；GND | 见供电/电气限值 | 必须接地 | S1 p15 |
| 2 VDD_1.2 | P；VDD_1.2 | 见供电/电气限值 |  | S1 p15 |
| 3 VDDA_3.3 | P；VDDA_3.3 | 见供电/电气限值 |  | S1 p15 |
| 4 RXM | I/O；RXM | 见供电/电气限值 |  | S1 p15 |
| 5 RXP | I/O；RXP | 见供电/电气限值 |  | S1 p15 |
| 6 TXM | I/O；TXM | 见供电/电气限值 |  | S1 p15 |
| 7 TXP | I/O；TXP | 见供电/电气限值 |  | S1 p15 |
| 8 XO | O；XO | 见供电/电气限值 | 外部时钟时XO不连接 | S1 p15 |
| 9 XI | I；XI | 见供电/电气限值 |  | S1 p15 |
| 10 REXT | I；REXT | 见供电/电气限值 |  | S1 p15 |
| 11 MDIO | Ipu/Opu；MDIO | 见供电/电气限值 |  | S1 p15 |
| 12 MDC | Ipu；MDC | 见供电/电气限值 |  | S1 p15 |
| 13 PHYAD0 | Ipu/O；PHYAD0 | 见供电/电气限值 |  | S1 p15 |
| 14 PHYAD1 | Ipd/O；PHYAD1 | 见供电/电气限值 |  | S1 p15 |
| 15 RXD1/PHYAD2 | Ipd/O；RXD1/PHYAD2 | 见供电/电气限值 | 按绑带采样条件，不能让MAC误驱动 | S1 p15 |
| 16 RXD0/DUPLEX | Ipu/O；RXD0/DUPLEX | 见供电/电气限值 | 按绑带采样条件，不能让MAC误驱动 | S1 p15 |
| 17 VDDIO | P；VDDIO | 见供电/电气限值 |  | S1 p16 |
| 18 CRS_DV/CONFIG2 | Ipd/O；CRS_DV/CONFIG2 | 见供电/电气限值 | 按绑带采样条件，不能让MAC误驱动 | S1 p16 |
| 19 REF_CLK/B-CAST_OFF | Ipd/O；REF_CLK/B-CAST_OFF | 见供电/电气限值 | 按绑带采样条件，不能让MAC误驱动 | S1 p16 |
| 20 RXER/ISO | Ipd/O；RXER/ISO | 见供电/电气限值 | 按绑带采样条件，不能让MAC误驱动 | S1 p16 |
| 21 INTRP/NAND_Tree# | Ipu/Opu；INTRP/NAND_Tree# | 见供电/电气限值 | 按绑带采样条件，不能让MAC误驱动 | S1 p16 |
| 22 NC | —；NC | 见供电/电气限值 | 无绑定可悬空 | S1 p16 |
| 23 TXEN | I；TXEN | 见供电/电气限值 |  | S1 p16 |
| 24 TXD0 | I；TXD0 | 见供电/电气限值 |  | S1 p16 |
| 25 TXD1 | I；TXD1 | 见供电/电气限值 |  | S1 p16 |
| 26 NC | —；NC | 见供电/电气限值 | 无绑定可悬空 | S1 p16 |
| 27 NC | —；NC | 见供电/电气限值 | 无绑定可悬空 | S1 p16 |
| 28 CONFIG0 | Ipd/O；CONFIG0 | 见供电/电气限值 |  | S1 p16 |
| 29 CONFIG1 | Ipd/O；CONFIG1 | 见供电/电气限值 |  | S1 p16 |
| 30 LED0/NWAYEN | Ipu/O；LED0/NWAYEN | 见供电/电气限值 | 按绑带采样条件，不能让MAC误驱动 | S1 p17 |
| 31 LED1/SPEED | Ipu/O；LED1/SPEED | 见供电/电气限值 | 按绑带采样条件，不能让MAC误驱动 | S1 p17 |
| 32 RST# | Ipu；RST# | 见供电/电气限值 |  | S1 p17 |
| 散热焊盘 PADDLE | GND；内部接地节点；原文只列地，未明确必须焊接 |  | 接地 | S1 p17 |


## 必需外围

- REXT接6.49 kΩ到地；MDIO和使用的INTRP各需1.0 kΩ上拉。VDD_1.2接2.2 µF并0.1 µF到地（S1 p9、p10、p15、p16）。
- VDDA_3.3经磁珠接3.3 V，并22 µF及0.1 µF；3.3 V VDDIO例同样去耦（S1 p38）。
- 25 MHz晶体/时钟，容差最大±50 ppm，温度晶体注15为±60 ppm；晶体ESR40 Ω、负载22 pF仅典型。RNB的50 MHz模式容差±50 ppm，XO不连接（S1 p15、p65）。
- 必须用1:1隔离变压器；PHY侧两个中心抽头不得接供电，也不得互连，各自经0.1 µF接地。建议磁件最小开路电感350 µH（100 mV、100 kHz、8 mA），最小耐压1500 Vrms（S1 p66、p67）。

## 订货型号与封装

MNX=MII，RNB=RMII；CA/IA分别商业/工业档。Lead Finish原文只写Pb-Free，未列具体合金。

| 订货型号或后缀 | 封装 | 脚数 | 电压或功能档 | 温度范围 | 引脚镀层 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| KSZ8081MNXCA | QFN | 32 | MII | 0～70 °C | Pb-Free | S1 p2 |
| KSZ8081MNXIA | QFN | 32 | MII | −40～85 °C | Pb-Free | S1 p2 |
| KSZ8081RNBCA | QFN | 32 | RMII，默认25 MHz输入、50 MHz输出 | 0～70 °C | Pb-Free | S1 p2 |
| KSZ8081RNBIA | QFN | 32 | RMII，默认25 MHz输入、50 MHz输出 | −40～85 °C | Pb-Free | S1 p2 |

## 核对记录

- 2026-11-10：逐页对照原件，工具核对通过，核对 240 个数。
