# TI LM5066I

类别：器件参数。
器件：10～80 V带PMBus监控的热插拔控制器，外接MOSFET。
手册：SNVS950C，2016-07。

## 来源

- S1：Datasheet/08_电源管理/热插拔_eFuse/TI - LM5066I.pdf

页码均为 PDF 文件页序。

## 绝对最大值

| 参数 | 符号 | 条件 | 最小 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| 输入电压 |  | VIN、VIN_K、GATE、UVLO/EN、SENSE、PGD、OUT对GND | −0.3 | 100 | V | S1 p5 |
| 低压脚 |  | OVLO、FB、TIMER、PWR | −0.3 | 7 | V | S1 p5 |
| 数字及监控脚 |  | SCL、SDAI、SDAO、CL、ADR0/1/2、VDD、VAUX、DIODE、RETRY | −0.3 | 6 | V | S1 p5 |
| 差分电压 |  | SENSE−VIN_K、VIN−VIN_K、AGND−GND | −0.3 | 0.3 | V | S1 p5 |
| 结温 |  |  |  | 150 | °C | S1 p5 |
| 贮存温度 | Tstg |  | −65 | 150 | °C | S1 p5 |

## 推荐工作条件

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 工作电压 |  | VIN、SENSE、OUT | 10 |  | 80 | V | S1 p5 |
| 结温 |  |  | −40 |  | 125 | °C | S1 p5 |

## 电气特性

VVIN=48 V，−40<TJ<125 °C，VUVLO=3 V，VOVLO=0，RPWR=20 kΩ；流出引脚电流为负（S1 p7～p9）。

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 使能电流 | IIN-EN | VUVLO=3 V、VOVLO=2 V |  | 5.6 | 7 | mA | S1 p7 |
| 插入定时复位门限 | PORIT | VIN上升 |  | 7.8 | 9.0 | V | S1 p7 |
| 全功能复位门限 | POREN | VIN上升 |  | 8.6 | 9.9 | V | S1 p7 |
| 复位迟滞 | PORHYS | VIN下降 |  | 100 |  | mV | S1 p7 |
| VDD稳压 | VDD | 空载 | 4.60 | 4.90 | 5.15 | V | S1 p7 |
| VDD稳压 | VDD | 10 mA | 4.60 | 4.85 | 5.15 | V | S1 p7 |
| VDD限流 | VDDILIM |  | −50 | −30 | −15 | mA | S1 p7 |
| VDD复位 | VDDPOR | 上升 |  | 4.1 |  | V | S1 p7 |
| 欠压门限 | UVLOTH | VUVLO下降 | 2.41 | 2.48 | 2.55 | V | S1 p7 |
| 欠压迟滞电流 | UVLOHYS | VUVLO=1 V | 16 | 20 | 24 | µA | S1 p7 |
| 欠压偏置电流 | UVLOBIAS | VUVLO=3 V |  |  | 1 | µA | S1 p7 |
| 过压门限 | OVLOTH | VOVLO上升 | 2.39 | 2.46 | 2.53 | V | S1 p7 |
| 过压迟滞电流 | OVLOHYS | VOVLO=1 V | −24 | −21 | −16 | µA | S1 p7 |
| 过压偏置电流 | OVLOBIAS | VOVLO=1 V |  |  | 1 | µA | S1 p7 |
| PG低电压 | PGDVOL | 吸收2 mA |  | 100 | 400 | mV | S1 p7 |
| PG关断漏电 | PGDIOH | VPGD=80 V |  |  | 1 | µA | S1 p7 |
| 反馈门限 | FBTH | VUVLO=3 V、VOVLO=2 V | 2.41 | 2.46 | 2.52 | V | S1 p7 |
| 反馈迟滞电流 | FBHYS |  | −25 | −20 | −15 | µA | S1 p7 |
| 反馈漏电 | FBLEAK | VFB=2.3 V |  |  | 1 | µA | S1 p7 |
| 功率脚电流 | IPWR | VPWR=2.5 V |  | −20 |  | µA | S1 p7 |
| 功率脚关闭阻抗 | RSAT(PWR) | VUVLO=2 V |  | 120 |  | Ω | S1 p7 |
| 栅极源出电流 | IGATE | 正常工作 | −40 | −20 | −7.5 | µA | S1 p7 |
| 栅极故障吸收电流 | IGATE | VUVLO=2 V | 3.4 | 4.2 | 5.3 | mA | S1 p7 |
| 复位断路吸收电流 | IGATE | VIN_K−VSENSE=60 mV或VIN<PORIT；VGATE=5 V，OUT=0，CB/CL=0，CL=1 | 90 | 160 | 230 | mA | S1 p7 |
| 栅极齐纳电压 | VGATEZ | VGATE−VOUT，IZ=−100 µA | 12 | 16.5 | 18 | V | S1 p7 |
| 栅极电荷泵电压 | VGATECP | 正常VIN=VOUT | 11 | 13 | 15 | V | S1 p7 |
| 输出使能偏置 | IOUT-EN | VIN=VOUT，正常 | 60 | 80 | 100 | µA | S1 p7 |
| 输出关闭偏置 | IOUT-DIS | OUT=0，VIN_K=SENSE | −65 | −50 | −35 | µA | S1 p7 |
| 限流采样门限 | VCL | CL=VDD | 23.4 | 26 | 28.6 | mV | S1 p8 |
| 限流采样门限 | VCL | CL=GND | 45 | 50 | 55 | mV | S1 p8 |
| 采样脚电流 | ISENSE | 使能，SENSE=OUT | 20 | 25 | 35 | µA | S1 p8 |
| 采样脚电流 | ISENSE | 关闭，OUT=0 |  | 66 |  | µA | S1 p8 |
| 采样脚电流 | ISENSE | 使能，OUT=0 | 190 | 220 | 250 | µA | S1 p8 |
| 定时上门限 | VTMRH |  | 3.74 | 3.9 | 4.07 | V | S1 p8 |
| 定时下门限 | VTMRL | 重启周期 | 1 | 1.2 | 1.4 | V | S1 p8 |
| 定时重使能门限 | VTMRL | 第八周期结束 |  | 0.3 |  | V | S1 p8 |
| 插入定时电流 | ITIMER |  | −5.9 | −4.8 | −3.3 | µA | S1 p8 |
| 插入结束吸收电流 | ITIMER |  | 0.9 | 1.5 | 2.1 | mA | S1 p8 |
| 故障检测电流 | ITIMER | TIMER=2 V | −90 | −75 | −60 | µA | S1 p8 |
| 故障吸收电流 | ITIMER |  | 1.7 | 2.5 | 3.2 | µA | S1 p8 |
| 故障重启占空比 | DCFAULT |  |  | 0.5 |  | % | S1 p8 |
| 内部基准 | VREF |  | 2.93 | 2.97 | 3.02 | V | S1 p8 |
| ADC分辨率 |  | 仅ADC |  | 12 |  | bit | S1 p8 |
| 积分非线性 | INL | 仅ADC |  |  | ±4 | LSB | S1 p8 |
| 采集转换时间 | tACQUIRE | 任意通道 |  | 100 |  | µs | S1 p8 |
| 轮询周期 | tRR | 全部通道 |  | 1 |  | ms | S1 p8 |
| 电流满量程 | IINFSR | CL=GND | 50 | 54.4 | 58 | mV | S1 p8 |
| 电流满量程 | IINFSR | CL=VDD | 26 | 27.0 | 29 | mV | S1 p8 |
| 电流量化步长 | IINLSB | CL=GND |  | 13.30 |  | µV | S1 p8 |
| 电流量化步长 | IINLSB | CL=VDD |  | 6.70 |  | µV | S1 p8 |
| 辅助满量程 | VAUXFSR |  | 2.93 | 2.97 | 3.01 | V | S1 p8 |
| 辅助量化步长 | VAUXLSB |  |  | 725 |  | µV | S1 p8 |
| 输入、输出满量程 | VINFSR、VOUTFSR |  | 86 | 88.9 | 91 | V | S1 p8 |
| 输入、输出量化步长 | VINLSB、VOUTLSB |  |  | 21.7 |  | mV | S1 p8 |
| 电流精度 | IINACC | 压差22 mV、CL=VDD | −1.75 |  | 1.75 | % | S1 p8 |
| 电流精度 | IINACC | 压差5 mV、CL=VDD | −6.0 |  | 6.0 | % | S1 p8 |
| 电流精度 | IINACC | 压差44 mV、CL=GND | −3.5 |  | 3.5 | % | S1 p8 |
| 电压精度 | VACC | VIN或VOUT=48/80 V | −1.25 |  | 1.25 | % | S1 p9 |
| 电压精度 | VACC | VIN或VOUT=10 V | −2.5 |  | 2.5 | % | S1 p9 |
| 辅助电压精度 | VACC | VAUX=2.8 V | −1.25 |  | 1.25 | % | S1 p9 |
| 功率精度 | PINACC | VIN=48 V，压差22 mV，CL=VDD | −2.5 |  | 2.5 | % | S1 p9 |
| 功率精度 | PINACC | VIN=48 V，压差5 mV，CL=VDD | −6.5 |  | 6.5 | % | S1 p9 |
| 功率精度 | PINACC | VIN=48 V，压差44 mV，CL=GND | −4.5 |  | 4.5 | % | S1 p9 |
| 温度精度 | TACC | 本地二极管，25～85 °C |  | 2 | 10 | °C | S1 p9 |
| 远程温度分辨率 | TACC |  |  | 9 |  | bit | S1 p9 |
| 二极管高电流 | IDIODE |  |  | 250 | 325 | µA | S1 p9 |
| 二极管低电流 | IDIODE |  |  | 9.4 |  | µA | S1 p9 |
| 二极管电流比 |  |  |  | 25.9 |  | µA | S1 p9 |
| 总线低电平 | VIL | SMBA、SDA、SCL |  |  | 0.9 | V | S1 p9 |
| 总线高电平 | VIH | SMBA、SDA、SCL | 2.1 |  | 5.5 | V | S1 p9 |
| 总线输出低电压 | VOL | 吸收3 mA | 0 |  | 0.4 | V | S1 p9 |
| 总线漏电 | ILEAK | SDAI、SMBA、SCL=5 V |  |  | 1 | µA | S1 p9 |
| 配置高门限 | VIH | CL、RETRY | 3 |  |  | V | S1 p9 |
| 配置漏电 | ILEAK | CL、RETRY=5 V |  |  | 5 | µA | S1 p9 |
| 功率限制采样电压 | VVIN_K−VSENSE | VSENSE−VOUT及RPWR依次为48 V，60 kΩ | 7.4 | 9.4 | 11.4 | mV | S1 p7 |
| 功率限制采样电压 | VVIN_K−VSENSE | VSENSE−VOUT及RPWR依次为48 V，20 kΩ | 1.5 | 3.5 | 5.7 | mV | S1 p7 |
| 功率限制采样电压 | VVIN_K−VSENSE | VSENSE−VOUT及RPWR依次为48 V，20 kΩ，0～85 °C | 1.85 | 3.5 | 5.02 | mV | S1 p7 |
| 功率限制采样电压 | VVIN_K−VSENSE | VSENSE−VOUT及RPWR依次为24 V，60 kΩ | 15 | 18.75 | 22.5 | mV | S1 p7 |
| 功率限制采样电压 | VVIN_K−VSENSE | VSENSE−VOUT及RPWR依次为24 V，20 kΩ | 5 | 7.23 | 10 | mV | S1 p7 |
| 断路限流比 | RTCB | CB/CL位=0，ILIM=50 mV | 1.64 | 1.94 | 2.23 | V/V | S1 p8 |
| 断路门限 | VCB | 同上 | 76 | 96 | 116 | mV | S1 p8 |
| 断路限流比 | RTCB | CB/CL位=1，ILIM=50 mV | 3.28 | 3.87 | 4.45 | V/V | S1 p8 |
| 断路门限 | VCB | 同上 | 155 | 193 | 235 | mV | S1 p8 |
| 断路限流比 | RTCB | CB/CL位=0，ILIM=26 mV | 1.5 | 1.88 | 2.3 | V/V | S1 p8 |
| 断路门限 | VCB | 同上 | 38 | 48 | 58 | mV | S1 p8 |
| 断路限流比 | RTCB | CB/CL位=1，ILIM=26 mV | 3.1 | 3.75 | 4.45 | V/V | S1 p8 |
| 断路门限 | VCB | 同上 | 76 | 96 | 116 | mV | S1 p8 |
| 总线频率 | ƒSMB | SMBus，按图1测量 | 10 |  | 400 | kHz | S1 p10 |
| 总线空闲 | tBUF | SMBus，按图1测量 | 1.3 |  |  | µs | S1 p10 |
| 启动保持 | tHD:STA | SMBus，按图1测量 | 0.6 |  |  | µs | S1 p10 |
| 启动建立 | tSU:STA | SMBus，按图1测量 | 0.6 |  |  | µs | S1 p10 |
| 停止建立 | tSU:STO | SMBus，按图1测量 | 0.6 |  |  | µs | S1 p10 |
| 数据保持 | tHD:DAT | SMBus，按图1测量 | 85 |  |  | ns | S1 p10 |
| 数据建立 | tSU:DAT | SMBus，按图1测量 | 100 |  |  | ns | S1 p10 |
| 低电平超时 | tTIMEOUT | SMBus，按图1测量 | 25 |  | 35 | ms | S1 p10 |
| 时钟低周期 | tLOW | SMBus，按图1测量 | 1.5 |  |  | µs | S1 p10 |
| 时钟高周期 | tHIGH | SMBus，按图1测量 | 0.6 |  |  | µs | S1 p10 |
| 从机累计延长 | tLOW:SEXT | SMBus，按图1测量 |  |  | 25 | ms | S1 p10 |
| 主机累计延长 | tLOW:MEXT | SMBus，按图1测量 |  |  | 10 | ms | S1 p10 |
| 下降时间 | tF | SMBus，按图1测量 | 20 |  | 300 | ns | S1 p10 |
| 上升时间 | tR | SMBus，按图1测量 | 20 |  | 300 | ns | S1 p10 |

用这些数时要注意：

- VIN的100 V绝对最大只适用于关闭或瞬时浪涌：开启时GATE比VIN高，GATE本身也受100 V限制（S1 p5）。
- 电流和功率精度随CL档及采样压差显著变化，不能把最佳档精度用于全量程（S1 p8、p9）。
- 复位、ADC时间、部分漏电只有典型值；温度传感电流比一行的单位原文是µA，按原文保留，不改成无量纲（S1 p7～p9）。
- 超时25 ms触发、35 ms内必须复位通信；主从累计拉低延时分别有独立限制（S1 p10）。

## 热特性

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- |
| 结到环境 | RθJA | PWP 28脚 | 35.6 | °C/W | S1 p6 |
| 结到壳顶 | RθJC(top) | PWP 28脚 | 19.9 | °C/W | S1 p6 |
| 结到板 | RθJB | PWP 28脚 | 16.8 | °C/W | S1 p6 |
| 结到顶特征参数 | ψJT | PWP 28脚 | 0.5 | °C/W | S1 p6 |
| 结到板特征参数 | ψJB | PWP 28脚 | 16.7 | °C/W | S1 p6 |
| 结到壳底 | RθJC(bot) | PWP 28脚 | 2.9 | °C/W | S1 p6 |

## 静电额定

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- |
| 人体模型 | VESD | JS-001，除GATE | ±2000 | V | S1 p5 |
| 人体模型 | VESD | GATE，脚注1 | 1 | kV | S1 p5 |
| 带电器件模型 | VESD | JESD22-C101，全部脚 | ±500 | V | S1 p5 |

内置ESD保护有限；储存/搬运时短接引脚或置导电泡棉，避免MOS栅极静电损坏（S1 p63）。

## 引脚与处置

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
| --- | --- | --- | --- | --- |
| 1 OUT | 输出反馈 | 见绝对最大值 | 接外部MOS源极 | S1 p3～p5 |
| 2 GATE | 栅极驱动输出 | 见绝对最大值 | 接MOS栅极 | S1 p3～p5 |
| 3 SENSE | 电流采样输入 | 见绝对最大值 | 接采样电阻低侧 | S1 p3～p5 |
| 4 VIN_K | 开尔文电源输入 | 见绝对最大值 | 接采样电阻高侧 | S1 p3～p5 |
| 5 VIN | 电源输入 | 见绝对最大值 | 必须供电 | S1 p3～p5 |
| 6 NC | 未连接 | 见绝对最大值 | 悬空 | S1 p3～p5 |
| 7 UVLO/EN | 欠压使能输入 | 见绝对最大值 | 外部分压 | S1 p3～p5 |
| 8 OVLO | 过压输入 | 见绝对最大值 | 外部分压 | S1 p3～p5 |
| 9 AGND | 模拟地 | 见绝对最大值 | 在引脚接GND | S1 p3～p5 |
| 10 GND | 地 | 见绝对最大值 | 接地 | S1 p3～p5 |
| 11 SDAI | 总线输入 | 见绝对最大值 | 无单向隔离时接SDAO | S1 p3～p5 |
| 12 SDAO | 总线输出 | 见绝对最大值 | 无单向隔离时接SDAI | S1 p3～p5 |
| 13 SCL | 总线时钟输入 | 见绝对最大值 | 按总线连接 | S1 p3～p5 |
| 14 SMBA | 低有效报警输出 | 见绝对最大值 | 手册未规定 | S1 p3～p5 |
| 15 VREF | 基准输出 | 见绝对最大值 | 1 µF旁路 | S1 p3～p5 |
| 16 DIODE | 远程温度输入 | 见绝对最大值 | 接二极管接法MMBT3904 | S1 p3～p5 |
| 17 VAUX | 辅助输入 | 见绝对最大值 | 手册未规定 | S1 p3～p5 |
| 18 ADR2 | 地址输入 | 见绝对最大值 | 接GND/VDD/浮空之一 | S1 p3～p5 |
| 19 ADR1 | 地址输入 | 见绝对最大值 | 接GND/VDD/浮空之一 | S1 p3～p5 |
| 20 ADR0 | 地址输入 | 见绝对最大值 | 接GND/VDD/浮空之一 | S1 p3～p5 |
| 21 VDD | 内部稳压输出 | 见绝对最大值 | 1 µF旁路 | S1 p3～p5 |
| 22 CL | 限流选择输入 | 见绝对最大值 | 接GND或浮空50 mV档；VDD为26 mV档 | S1 p3～p5 |
| 23 FB | PG反馈输入 | 见绝对最大值 | 外部分压 | S1 p3～p5 |
| 24 RETRY | 重试选择输入 | 见绝对最大值 | GND或浮空持续重试，VDD锁断 | S1 p3～p5 |
| 25 TIMER | 定时输入 | 见绝对最大值 | 接定时电容 | S1 p3～p5 |
| 26 PWR | 功率限制输入 | 见绝对最大值 | 接设定电阻 | S1 p3～p5 |
| 27 NC | 未连接 | 见绝对最大值 | 悬空 | S1 p3～p5 |
| 28 PGD | 开漏状态输出 | 见绝对最大值 | 手册未规定 | S1 p3～p5 |

散热焊盘：裸露焊盘必须焊接地平面，以降低热阻；手册没有声明内部接地脚关系（S1 p3）。


## 必需外围

- 外接串联N沟道MOSFET、采样电阻、PWR电阻及TIMER电容，需结合负载和MOS安全工作区选值（S1 p3、p4）。
- VREF和VDD各用1 µF对地旁路；远程测温用二极管接法MMBT3904（S1 p4）。

## 订货型号与封装

手册列出的型号与封装如下；空格表示手册未给出，不从型号自行推算。

| 订货型号或后缀 | 封装 | 脚数 | 电压或功能档 | 温度范围 | 引脚镀层 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| LM5066IPMHE/NOPB | HTSSOP (PWP) | 28 |  | -40～125 °C | SN | S1 p64 |
| LM5066IPMHE/NOPB.A | HTSSOP (PWP) | 28 |  | -40～125 °C | SN | S1 p64 |
| LM5066IPMHX/NOPB | HTSSOP (PWP) | 28 |  | -40～125 °C | SN | S1 p64 |
| LM5066IPMHX/NOPB.A | HTSSOP (PWP) | 28 |  | -40～125 °C | SN | S1 p64 |



## 核对记录

- 2026-11-10：工具核对通过，核对了 278 个数。
