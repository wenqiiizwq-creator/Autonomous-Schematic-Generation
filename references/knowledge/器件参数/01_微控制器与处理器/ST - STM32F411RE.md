# ST STM32F411RE

类别：器件参数。
器件：STM32F411RE；本条限定 R=64脚、E=512 KB 的 LQFP64；同册其他封装的引脚、散热不混用
手册：DS10314 Rev 8，January 2024。

## 来源

- S1：Datasheet/01_微控制器与处理器/32位ARM_Cortex-M_MCU/ST - STM32F411RE.pdf

页码均为 PDF 文件页序。

## 绝对最大值

| 参数 | 符号 | 条件 | 最小 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| 电源电压 | VDD−VSS | 包括 VDDA、VBAT | −0.3 | 4.0 | V | S1 p61 |
| 容限引脚输入电压 | VIN | FT、TC 引脚 | VSS−0.3 | VDD+4.0 | V | S1 p61 |
| 其他引脚输入电压 | VIN | 除 BOOT0 | VSS−0.3 | 4.0 | V | S1 p61 |
| 启动脚电压 | VIN | BOOT0 | VSS | 9.0 | V | S1 p61 |
| 不同电源脚间电压差 | ΔVDD | 所有 VDD |  | 50 | mV | S1 p61 |
| 不同地脚间电压差 | ΔVSS | 所有 VSS |  | 50 | mV | S1 p61 |
| 总电源电流 | ΣIVDD | 注入值按绝对值求和；单脚限制见脚注 |  | 160 | mA | S1 p62 |
| 总地电流 | ΣIVSS | 注入值按绝对值求和；单脚限制见脚注 | −160 |  | mA | S1 p62 |
| 单电源脚电流 | IVDD | 注入值按绝对值求和；单脚限制见脚注 |  | 100 | mA | S1 p62 |
| 单地脚电流 | IVSS | 注入值按绝对值求和；单脚限制见脚注 | −100 |  | mA | S1 p62 |
| 单脚灌电流 | IIO | 注入值按绝对值求和；单脚限制见脚注 |  | 25 | mA | S1 p62 |
| 单脚拉电流 | IIO | 注入值按绝对值求和；单脚限制见脚注 | −25 |  | mA | S1 p62 |
| 总灌电流 | ΣIIO | 注入值按绝对值求和；单脚限制见脚注 |  | 120 | mA | S1 p62 |
| 总拉电流 | ΣIIO | 注入值按绝对值求和；单脚限制见脚注 | −120 |  | mA | S1 p62 |
| 单脚注入电流 | IINJ(PIN) | 注入值按绝对值求和；单脚限制见脚注 | −5 | 0 | mA | S1 p62 |
| 总注入电流 | ΣIINJ(PIN) | 注入值按绝对值求和；单脚限制见脚注 | −25 | 25 | mA | S1 p62 |
| 储存温度 | TSTG |  | −65 | 150 | °C | S1 p62 |
| 结温 | TJ |  |  | 130 | °C | S1 p62 |

## 推荐工作条件

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 内核时钟 | fHCLK | 电压档 3 | 0 |  | 64 | MHz | S1 p63 |
| 内核时钟 | fHCLK | 电压档 2 | 0 |  | 84 | MHz | S1 p63 |
| 内核时钟 | fHCLK | 电压档 1 | 0 |  | 100 | MHz | S1 p63 |
| 外设时钟 | fPCLK1 |  | 0 |  | 50 | MHz | S1 p63 |
| 外设时钟 | fPCLK2 |  | 0 |  | 100 | MHz | S1 p63 |
| 供电电压 | VDD | 1.7 V 须使用外部电源监控器 | 1.7 |  | 3.6 | V | S1 p63 |
| 模拟电源 | VDDA | ADC 最高 1.2 Msps；与 VDD 同电位 | 1.7 |  | 2.4 | V | S1 p63 |
| 模拟电源 | VDDA | ADC 最高 2.4 Msps；与 VDD 同电位 | 2.4 |  | 3.6 | V | S1 p63 |
| 备用电源 | VBAT |  | 1.65 |  | 3.6 | V | S1 p63 |
| 内核稳压输出 | V12 | 内部稳压器开启；电压档 3 | 1.08 | 1.14 | 1.20 | V | S1 p63 |
| 内核稳压输出 | V12 | 内部稳压器开启；电压档 2 | 1.20 | 1.26 | 1.32 | V | S1 p63 |
| 内核稳压输出 | V12 | 内部稳压器开启；电压档 1 | 1.26 | 1.32 | 1.38 | V | S1 p63 |
| 数字输入电压 | VIN | FT/TC/NRST；VDD≥2 V | −0.3 |  | 5.5 | V | S1 p63 |
| 数字输入电压 | VIN | FT/TC/NRST；VDD≤2 V | −0.3 |  | 5.2 | V | S1 p63 |
| 启动脚电压 | VIN | BOOT0 | 0 |  | 9 | V | S1 p63 |
| 环境温度 | TA | 温度后缀 6；最大功耗 | −40 |  | 85 | °C | S1 p64 |
| 环境温度 | TA | 温度后缀 6；低功耗 | −40 |  | 105 | °C | S1 p64 |
| 结温 | TJ | 温度后缀 6 | −40 |  | 105 | °C | S1 p64 |
| 环境温度 | TA | 温度后缀 7；最大功耗 | −40 |  | 105 | °C | S1 p64 |
| 环境温度 | TA | 温度后缀 7；低功耗 | −40 |  | 125 | °C | S1 p64 |
| 结温 | TJ | 温度后缀 7 | −40 |  | 125 | °C | S1 p64 |
| 环境温度 | TA | 温度后缀 3；最大功耗 | −40 |  | 110 | °C | S1 p64 |
| 环境温度 | TA | 温度后缀 3；低功耗 | −40 |  | 130 | °C | S1 p64 |
| 结温 | TJ | 温度后缀 3 | −40 |  | 130 | °C | S1 p64 |
| 模拟/数字电源上电偏差 | ΔV | 上电阶段 |  |  | 300 | mV | S1 p64 |
| LQFP64 功耗 | PD | TA=85°C（档6）或105°C（档7） |  |  | 425 | mW | S1 p63 |
| LQFP64 功耗 | PD | TA=125°C（档3） |  |  | 106 | mW | S1 p64 |
| 电源升降时间 | tVDD | 内部稳压器开启 | 20 |  |  | µs/V | S1 p66 |

## 电气特性

除特别注明外按各表的电压、温度与负载；表征保证与生产测试区别保留在注意事项。SRAM/Flash运行电流的典型列为25°C；最大值按各温度单列。

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 可编程电压门限 | VPVD | PLS=000；上升 | 2.09 | 2.14 | 2.19 | V | S1 p67 |
| 可编程电压门限 | VPVD | PLS=000；下降 | 1.98 | 2.04 | 2.08 | V | S1 p67 |
| 可编程电压门限 | VPVD | PLS=001；上升 | 2.23 | 2.30 | 2.37 | V | S1 p67 |
| 可编程电压门限 | VPVD | PLS=001；下降 | 2.13 | 2.19 | 2.25 | V | S1 p67 |
| 可编程电压门限 | VPVD | PLS=010；上升 | 2.39 | 2.45 | 2.51 | V | S1 p67 |
| 可编程电压门限 | VPVD | PLS=010；下降 | 2.29 | 2.35 | 2.39 | V | S1 p67 |
| 可编程电压门限 | VPVD | PLS=011；上升 | 2.54 | 2.60 | 2.65 | V | S1 p67 |
| 可编程电压门限 | VPVD | PLS=011；下降 | 2.44 | 2.51 | 2.56 | V | S1 p67 |
| 可编程电压门限 | VPVD | PLS=100；上升 | 2.70 | 2.76 | 2.82 | V | S1 p67 |
| 可编程电压门限 | VPVD | PLS=100；下降 | 2.59 | 2.66 | 2.71 | V | S1 p67 |
| 可编程电压门限 | VPVD | PLS=101；上升 | 2.86 | 2.93 | 2.99 | V | S1 p67 |
| 可编程电压门限 | VPVD | PLS=101；下降 | 2.77 | 2.82 | 2.89 | V | S1 p67 |
| 可编程电压门限 | VPVD | PLS=110；上升 | 2.96 | 3.03 | 3.10 | V | S1 p67 |
| 可编程电压门限 | VPVD | PLS=110；下降 | 2.85 | 2.93 | 2.99 | V | S1 p67 |
| 可编程电压门限 | VPVD | PLS=111；上升 | 3.07 | 3.14 | 3.21 | V | S1 p67 |
| 可编程电压门限 | VPVD | PLS=111；下降 | 2.95 | 3.03 | 3.09 | V | S1 p67 |
| 掉电门限 | VPOR/PDR |  | 1.60 | 1.68 | 1.76 | V | S1 p67 |
| 上电门限 | VPOR/PDR |  | 1.64 | 1.72 | 1.80 | V | S1 p67 |
| 欠压复位门限 | VBOR1 | 下降 | 2.13 | 2.19 | 2.24 | V | S1 p67 |
| 欠压复位门限 | VBOR1 | 上升 | 2.23 | 2.29 | 2.33 | V | S1 p67 |
| 欠压复位门限 | VBOR2 | 下降 | 2.44 | 2.50 | 2.56 | V | S1 p67 |
| 欠压复位门限 | VBOR2 | 上升 | 2.53 | 2.59 | 2.63 | V | S1 p67 |
| 欠压复位门限 | VBOR3 | 下降 | 2.75 | 2.83 | 2.88 | V | S1 p67 |
| 欠压复位门限 | VBOR3 | 上升 | 2.85 | 2.92 | 2.97 | V | S1 p67 |
| PVD迟滞 | VPVDhyst |  |  | 100 |  | mV | S1 p67 |
| POR迟滞 | VPDRhyst |  |  | 40 |  | mV | S1 p67 |
| BOR迟滞 | VBORhyst |  |  | 100 |  | mV | S1 p67 |
| 复位持续时间 | TRSTTEMPO | 表征保证，非生产测试 | 0.5 | 1.5 | 3.0 | ms | S1 p67 |
| 启动浪涌峰值 | IRUSH | VDD=1.7 V、TA=125°C |  | 160 | 200 | mA | S1 p68 |
| 启动电荷 | ERUSH | 启动电流 17131 µs |  |  | 5.4 | µC | S1 p68 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=100 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 21.4 | 23.0 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=100 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 23.6 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=100 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 24.0 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=100 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 25.0 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=84 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 17.2 | 18.9 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=84 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 19.1 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=84 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 19.2 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=84 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 20.2 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=64 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 11.9 | 12.9 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=64 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 13.2 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=64 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 13.7 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=64 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 14.6 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=50 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 9.4 | 10.1 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=50 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 10.4 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=50 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 11.0 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=50 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 11.9 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=20 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 4.3 | 4.8 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=20 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 5.0 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=20 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 5.6 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=20 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 6.5 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=16 MHz；外设全开；HSI、PLL关闭；TA=25°C |  | 3.0 | 3.3 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=16 MHz；外设全开；HSI、PLL关闭；TA=85°C |  |  | 3.6 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=16 MHz；外设全开；HSI、PLL关闭；TA=105°C |  |  | 4.3 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=16 MHz；外设全开；HSI、PLL关闭；TA=125°C |  |  | 5.2 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=1 MHz；外设全开；HSI、PLL关闭；TA=25°C |  | 0.5 | 0.7 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=1 MHz；外设全开；HSI、PLL关闭；TA=85°C |  |  | 1.0 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=1 MHz；外设全开；HSI、PLL关闭；TA=105°C |  |  | 1.7 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=1 MHz；外设全开；HSI、PLL关闭；TA=125°C |  |  | 2.6 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=100 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 12.7 | 14.0 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=100 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 14.4 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=100 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 14.8 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=100 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 15.8 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=84 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 10.2 | 11.6 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=84 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 11.8 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=84 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 12.0 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=84 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 13.0 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=64 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 7.1 | 7.9 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=64 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 8.2 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=64 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 8.7 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=64 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 9.7 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=50 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 5.6 | 6.3 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=50 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 6.5 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=50 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 7.1 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=50 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 8.0 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=20 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 2.5 | 3.0 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=20 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 3.3 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=20 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 3.9 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=20 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 4.8 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=16 MHz；外设全关；HSI、PLL关闭；TA=25°C |  | 1.9 | 2.1 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=16 MHz；外设全关；HSI、PLL关闭；TA=85°C |  |  | 2.4 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=16 MHz；外设全关；HSI、PLL关闭；TA=105°C |  |  | 3.0 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=16 MHz；外设全关；HSI、PLL关闭；TA=125°C |  |  | 3.9 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=1 MHz；外设全关；HSI、PLL关闭；TA=25°C |  | 0.4 | 0.5 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=1 MHz；外设全关；HSI、PLL关闭；TA=85°C |  |  | 0.9 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=1 MHz；外设全关；HSI、PLL关闭；TA=105°C |  |  | 1.6 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=1.7 V；fHCLK=1 MHz；外设全关；HSI、PLL关闭；TA=125°C |  |  | 2.5 | mA | S1 p69 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=100 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 21.7 | 23.3 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=100 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 23.9 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=100 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 24.3 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=100 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 25.3 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=84 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 17.5 | 19.2 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=84 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 19.4 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=84 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 19.5 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=84 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 20.5 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=64 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 12.2 | 13.2 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=64 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 13.5 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=64 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 14.0 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=64 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 14.9 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=50 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 9.6 | 10.4 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=50 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 10.7 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=50 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 11.2 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=50 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 12.1 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=20 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 4.5 | 5.0 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=20 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 5.3 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=20 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 5.9 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=20 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 6.8 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=16 MHz；外设全开；HSI、PLL关闭；TA=25°C |  | 3.0 | 3.3 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=16 MHz；外设全开；HSI、PLL关闭；TA=85°C |  |  | 3.6 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=16 MHz；外设全开；HSI、PLL关闭；TA=105°C |  |  | 4.3 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=16 MHz；外设全开；HSI、PLL关闭；TA=125°C |  |  | 5.2 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=1 MHz；外设全开；HSI、PLL关闭；TA=25°C |  | 0.5 | 0.7 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=1 MHz；外设全开；HSI、PLL关闭；TA=85°C |  |  | 1.0 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=1 MHz；外设全开；HSI、PLL关闭；TA=105°C |  |  | 1.7 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=1 MHz；外设全开；HSI、PLL关闭；TA=125°C |  |  | 2.6 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=100 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 13.0 | 14.6 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=100 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 14.6 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=100 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 14.9 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=100 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 16.0 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=84 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 10.5 | 11.9 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=84 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 12.1 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=84 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 12.2 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=84 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 13.2 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=64 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 7.4 | 8.4 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=64 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 8.8 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=64 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 8.9 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=64 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 9.9 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=50 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 5.9 | 6.6 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=50 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 6.8 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=50 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 7.3 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=50 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 8.2 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=20 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 2.8 | 3.3 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=20 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 3.5 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=20 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 4.2 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=20 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 5.1 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=16 MHz；外设全关；HSI、PLL关闭；TA=25°C |  | 1.9 | 2.1 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=16 MHz；外设全关；HSI、PLL关闭；TA=85°C |  |  | 2.4 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=16 MHz；外设全关；HSI、PLL关闭；TA=105°C |  |  | 3.1 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=16 MHz；外设全关；HSI、PLL关闭；TA=125°C |  |  | 4.0 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=1 MHz；外设全关；HSI、PLL关闭；TA=25°C |  | 0.4 | 0.5 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=1 MHz；外设全关；HSI、PLL关闭；TA=85°C |  |  | 0.9 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=1 MHz；外设全关；HSI、PLL关闭；TA=105°C |  |  | 1.6 | mA | S1 p70 |
| 电源电流 | IDD | SRAM，ART关闭，VDD=3.6 V；fHCLK=1 MHz；外设全关；HSI、PLL关闭；TA=125°C |  |  | 2.5 | mA | S1 p70 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=100 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 20.4 | 21.8 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=100 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 22.1 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=100 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 22.8 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=100 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 23.8 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=84 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 16.5 | 17.6 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=84 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 17.8 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=84 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 18.6 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=84 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 19.6 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=64 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 11.4 | 12.3 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=64 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 12.5 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=64 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 13.1 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=64 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 14.1 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=50 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 9.0 | 9.7 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=50 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 10.0 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=50 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 10.6 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=50 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 11.6 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=20 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 4.6 | 5.0 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=20 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 5.3 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=20 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 6.0 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=20 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 7.0 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=16 MHz；外设全开；HSI、PLL关闭；TA=25°C |  | 2.9 | 3.2 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=16 MHz；外设全开；HSI、PLL关闭；TA=85°C |  |  | 3.6 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=16 MHz；外设全开；HSI、PLL关闭；TA=105°C |  |  | 4.3 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=16 MHz；外设全开；HSI、PLL关闭；TA=125°C |  |  | 5.3 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=1 MHz；外设全开；HSI、PLL关闭；TA=25°C |  | 0.7 | 0.8 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=1 MHz；外设全开；HSI、PLL关闭；TA=85°C |  |  | 1.3 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=1 MHz；外设全开；HSI、PLL关闭；TA=105°C |  |  | 1.9 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=1 MHz；外设全开；HSI、PLL关闭；TA=125°C |  |  | 2.9 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=100 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 11.2 | 12.2 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=100 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 12.4 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=100 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 13.2 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=100 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 14.2 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=84 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 9.1 | 9.9 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=84 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 10.1 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=84 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 10.9 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=84 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 11.9 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=64 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 6.4 | 7.0 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=64 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 7.3 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=64 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 7.9 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=64 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 8.9 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=50 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 5.1 | 5.6 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=50 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 5.9 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=50 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 6.6 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=50 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 7.6 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=20 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 2.6 | 3.0 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=20 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 3.3 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=20 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 4.0 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=20 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 5.0 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=16 MHz；外设全关；HSI、PLL关闭；TA=25°C |  | 1.8 | 2.0 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=16 MHz；外设全关；HSI、PLL关闭；TA=85°C |  |  | 2.4 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=16 MHz；外设全关；HSI、PLL关闭；TA=105°C |  |  | 3.0 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=16 MHz；外设全关；HSI、PLL关闭；TA=125°C |  |  | 4.0 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=1 MHz；外设全关；HSI、PLL关闭；TA=25°C |  | 0.6 | 0.7 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=1 MHz；外设全关；HSI、PLL关闭；TA=85°C |  |  | 1.2 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=1 MHz；外设全关；HSI、PLL关闭；TA=105°C |  |  | 1.9 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=1.7 V；fHCLK=1 MHz；外设全关；HSI、PLL关闭；TA=125°C |  |  | 2.9 | mA | S1 p71 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=100 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 20.7 | 22.2 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=100 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 22.5 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=100 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 23.2 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=100 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 24.4 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=84 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 16.8 | 18.0 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=84 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 18.3 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=84 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 19.0 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=84 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 20.1 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=64 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 11.8 | 12.7 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=64 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 12.9 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=64 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 13.6 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=64 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 14.6 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=50 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 9.3 | 10.2 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=50 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 10.4 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=50 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 11.1 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=50 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 12.0 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=20 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 4.8 | 5.5 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=20 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 5.8 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=20 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 6.5 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=20 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 7.4 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=16 MHz；外设全开；HSI、PLL关闭；TA=25°C |  | 3.0 | 3.3 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=16 MHz；外设全开；HSI、PLL关闭；TA=85°C |  |  | 3.8 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=16 MHz；外设全开；HSI、PLL关闭；TA=105°C |  |  | 4.5 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=16 MHz；外设全开；HSI、PLL关闭；TA=125°C |  |  | 5.4 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=1 MHz；外设全开；HSI、PLL关闭；TA=25°C |  | 0.7 | 1.0 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=1 MHz；外设全开；HSI、PLL关闭；TA=85°C |  |  | 1.4 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=1 MHz；外设全开；HSI、PLL关闭；TA=105°C |  |  | 2.1 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=1 MHz；外设全开；HSI、PLL关闭；TA=125°C |  |  | 3.0 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=100 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 11.6 | 12.6 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=100 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 12.9 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=100 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 13.6 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=100 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 14.8 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=84 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 9.7 | 10.2 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=84 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 11.1 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=84 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 11.3 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=84 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 12.5 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=64 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 6.7 | 7.4 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=64 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 7.7 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=64 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 8.3 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=64 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 9.4 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=50 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 5.4 | 6.0 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=50 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 6.3 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=50 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 7.0 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=50 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 8.0 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=20 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 2.9 | 3.4 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=20 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 3.7 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=20 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 4.4 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=20 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 5.4 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=16 MHz；外设全关；HSI、PLL关闭；TA=25°C |  | 1.9 | 2.2 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=16 MHz；外设全关；HSI、PLL关闭；TA=85°C |  |  | 2.6 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=16 MHz；外设全关；HSI、PLL关闭；TA=105°C |  |  | 3.3 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=16 MHz；外设全关；HSI、PLL关闭；TA=125°C |  |  | 4.3 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=1 MHz；外设全关；HSI、PLL关闭；TA=25°C |  | 0.7 | 0.9 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=1 MHz；外设全关；HSI、PLL关闭；TA=85°C |  |  | 1.3 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=1 MHz；外设全关；HSI、PLL关闭；TA=105°C |  |  | 2.1 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART开启、无预取，VDD=3.6 V；fHCLK=1 MHz；外设全关；HSI、PLL关闭；TA=125°C |  |  | 3.1 | mA | S1 p72 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=100 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 29.5 | 31.5 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=100 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 32.3 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=100 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 33.3 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=100 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 34.7 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=84 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 25.5 | 27.1 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=84 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 27.9 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=84 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 28.9 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=84 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 30.2 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=64 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 18.6 | 19.8 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=64 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 20.4 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=64 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 21.2 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=64 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 22.4 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=50 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 15.2 | 16.4 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=50 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 16.9 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=50 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 17.7 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=50 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 18.7 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=20 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 7.6 | 8.4 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=20 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 8.8 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=20 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 9.5 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=20 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 10.5 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=16 MHz；外设全开；HSI、PLL关闭；TA=25°C |  | 4.8 | 5.2 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=16 MHz；外设全开；HSI、PLL关闭；TA=85°C |  |  | 5.7 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=16 MHz；外设全开；HSI、PLL关闭；TA=105°C |  |  | 6.5 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=16 MHz；外设全开；HSI、PLL关闭；TA=125°C |  |  | 7.5 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=1 MHz；外设全开；HSI、PLL关闭；TA=25°C |  | 0.9 | 1.3 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=1 MHz；外设全开；HSI、PLL关闭；TA=85°C |  |  | 1.6 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=1 MHz；外设全开；HSI、PLL关闭；TA=105°C |  |  | 2.4 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=1 MHz；外设全开；HSI、PLL关闭；TA=125°C |  |  | 3.4 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=100 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 20.4 | 21.8 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=100 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 22.7 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=100 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 23.8 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=100 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 25.1 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=84 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 18.4 | 19.2 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=84 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 20.9 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=84 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 21.1 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=84 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 22.4 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=64 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 13.5 | 14.5 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=64 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 15.2 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=64 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 15.9 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=64 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 17.2 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=50 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 11.3 | 12.2 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=50 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 12.8 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=50 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 13.6 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=50 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 14.7 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=20 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 5.6 | 6.4 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=20 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 6.7 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=20 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 7.4 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=20 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 8.5 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=16 MHz；外设全关；HSI、PLL关闭；TA=25°C |  | 3.6 | 4.1 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=16 MHz；外设全关；HSI、PLL关闭；TA=85°C |  |  | 4.5 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=16 MHz；外设全关；HSI、PLL关闭；TA=105°C |  |  | 5.2 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=16 MHz；外设全关；HSI、PLL关闭；TA=125°C |  |  | 6.3 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=1 MHz；外设全关；HSI、PLL关闭；TA=25°C |  | 0.9 | 1.2 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=1 MHz；外设全关；HSI、PLL关闭；TA=85°C |  |  | 1.6 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=1 MHz；外设全关；HSI、PLL关闭；TA=105°C |  |  | 2.3 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART关闭，VDD=3.6 V；fHCLK=1 MHz；外设全关；HSI、PLL关闭；TA=125°C |  |  | 3.4 | mA | S1 p73 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=100 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 31.7 | 33.6 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=100 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 34.5 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=100 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 35.5 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=100 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 37.0 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=84 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 26.9 | 28.6 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=84 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 29.4 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=84 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 30.3 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=84 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 31.6 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=64 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 19.6 | 20.9 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=64 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 21.5 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=64 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 22.3 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=64 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 23.5 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=50 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 15.6 | 16.7 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=50 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 17.2 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=50 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 18.0 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=50 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 19.1 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=20 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 7.6 | 8.4 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=20 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 8.8 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=20 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 9.5 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=20 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 10.6 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=16 MHz；外设全开；HSI、PLL关闭；TA=25°C |  | 5.1 | 5.6 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=16 MHz；外设全开；HSI、PLL关闭；TA=85°C |  |  | 6.1 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=16 MHz；外设全开；HSI、PLL关闭；TA=105°C |  |  | 6.8 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=16 MHz；外设全开；HSI、PLL关闭；TA=125°C |  |  | 7.9 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=1 MHz；外设全开；HSI、PLL关闭；TA=25°C |  | 1.0 | 1.3 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=1 MHz；外设全开；HSI、PLL关闭；TA=85°C |  |  | 1.7 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=1 MHz；外设全开；HSI、PLL关闭；TA=105°C |  |  | 2.3 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=1 MHz；外设全开；HSI、PLL关闭；TA=125°C |  |  | 3.4 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=100 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 22.5 | 24.2 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=100 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 24.9 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=100 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 26.0 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=100 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 27.3 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=84 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 19.5 | 21.1 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=84 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 21.8 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=84 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 22.8 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=84 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 24.1 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=64 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 14.5 | 15.7 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=64 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 16.3 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=64 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 17.1 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=64 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 18.3 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=50 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 11.7 | 12.7 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=50 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 13.2 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=50 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 14.0 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=50 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 15.1 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=20 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 5.6 | 6.4 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=20 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 6.8 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=20 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 7.4 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=20 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 8.5 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=16 MHz；外设全关；HSI、PLL关闭；TA=25°C |  | 4.0 | 4.5 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=16 MHz；外设全关；HSI、PLL关闭；TA=85°C |  |  | 4.9 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=16 MHz；外设全关；HSI、PLL关闭；TA=105°C |  |  | 5.6 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=16 MHz；外设全关；HSI、PLL关闭；TA=125°C |  |  | 6.7 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=1 MHz；外设全关；HSI、PLL关闭；TA=25°C |  | 0.9 | 1.2 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=1 MHz；外设全关；HSI、PLL关闭；TA=85°C |  |  | 1.6 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=1 MHz；外设全关；HSI、PLL关闭；TA=105°C |  |  | 2.2 | mA | S1 p74 |
| 电源电流 | IDD | Flash，ART开启并预取，VDD=3.6 V；fHCLK=1 MHz；外设全关；HSI、PLL关闭；TA=125°C |  |  | 3.3 | mA | S1 p74 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=100 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 12.2 | 13.2 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=100 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 13.4 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=100 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 14.1 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=100 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 15.3 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=84 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 9.8 | 10.6 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=84 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 10.9 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=84 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 11.6 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=84 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 12.8 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=64 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 6.9 | 7.4 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=64 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 7.7 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=64 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 8.3 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=64 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 9.5 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=50 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 5.4 | 5.9 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=50 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 6.2 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=50 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 6.8 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=50 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 8.0 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=20 MHz；外设全开；外部时钟、PLL配置按表注；TA=25°C |  | 2.8 | 3.2 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=20 MHz；外设全开；外部时钟、PLL配置按表注；TA=85°C |  |  | 3.5 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=20 MHz；外设全开；外部时钟、PLL配置按表注；TA=105°C |  |  | 4.1 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=20 MHz；外设全开；外部时钟、PLL配置按表注；TA=125°C |  |  | 5.3 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=16 MHz；外设全开；HSI、PLL关闭；TA=25°C |  | 1.3 | 1.7 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=16 MHz；外设全开；HSI、PLL关闭；TA=85°C |  |  | 2.2 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=16 MHz；外设全开；HSI、PLL关闭；TA=105°C |  |  | 2.8 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=16 MHz；外设全开；HSI、PLL关闭；TA=125°C |  |  | 4.0 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=1 MHz；外设全开；HSI、PLL关闭；TA=25°C |  | 0.4 | 0.5 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=1 MHz；外设全开；HSI、PLL关闭；TA=85°C |  |  | 0.9 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=1 MHz；外设全开；HSI、PLL关闭；TA=105°C |  |  | 1.6 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=1 MHz；外设全开；HSI、PLL关闭；TA=125°C |  |  | 2.8 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=100 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 3.0 | 3.6 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=100 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 3.9 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=100 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 4.5 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=100 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 5.7 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=84 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 2.5 | 3.0 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=84 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 3.2 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=84 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 3.9 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=84 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 5.1 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=64 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 1.9 | 2.2 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=64 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 2.5 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=64 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 3.0 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=64 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 4.2 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=50 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 1.6 | 1.9 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=50 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 2.1 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=50 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 2.7 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=50 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 3.9 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=20 MHz；外设全关；外部时钟、PLL配置按表注；TA=25°C |  | 1.1 | 1.4 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=20 MHz；外设全关；外部时钟、PLL配置按表注；TA=85°C |  |  | 1.7 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=20 MHz；外设全关；外部时钟、PLL配置按表注；TA=105°C |  |  | 2.3 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=20 MHz；外设全关；外部时钟、PLL配置按表注；TA=125°C |  |  | 3.5 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=16 MHz；外设全关；HSI、PLL关闭；TA=25°C |  | 0.4 | 0.5 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=16 MHz；外设全关；HSI、PLL关闭；TA=85°C |  |  | 0.9 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=16 MHz；外设全关；HSI、PLL关闭；TA=105°C |  |  | 1.6 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=16 MHz；外设全关；HSI、PLL关闭；TA=125°C |  |  | 2.8 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=1 MHz；外设全关；HSI、PLL关闭；TA=25°C |  | 0.3 | 0.4 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=1 MHz；外设全关；HSI、PLL关闭；TA=85°C |  |  | 0.8 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=1 MHz；外设全关；HSI、PLL关闭；TA=105°C |  |  | 1.5 | mA | S1 p75 |
| 电源电流 | IDD | Sleep，VDD=3.6 V；fHCLK=1 MHz；外设全关；HSI、PLL关闭；TA=125°C |  |  | 2.7 | mA | S1 p75 |
| 停止电流 | IDD | Flash Stop、主稳压器；VDD=1.7 V；TA=25°C |  | 112 | 142 | µA | S1 p75 |
| 停止电流 | IDD | Flash Stop、主稳压器；VDD=1.7 V；TA=85°C |  |  | 400 | µA | S1 p75 |
| 停止电流 | IDD | Flash Stop、主稳压器；VDD=1.7 V；TA=105°C |  |  | 710 | µA | S1 p75 |
| 停止电流 | IDD | Flash Stop、主稳压器；VDD=1.7 V；TA=125°C |  |  | 1200 | µA | S1 p75 |
| 停止电流 | IDD | Flash Stop、低功耗稳压器；VDD=1.7 V；TA=25°C |  | 42.6 | 67 | µA | S1 p75 |
| 停止电流 | IDD | Flash Stop、低功耗稳压器；VDD=1.7 V；TA=85°C |  |  | 300 | µA | S1 p75 |
| 停止电流 | IDD | Flash Stop、低功耗稳压器；VDD=1.7 V；TA=105°C |  |  | 580 | µA | S1 p75 |
| 停止电流 | IDD | Flash Stop、低功耗稳压器；VDD=1.7 V；TA=125°C |  |  | 1044 | µA | S1 p75 |
| 停止电流 | IDD | Flash深度掉电、主稳压器；VDD=1.7 V；TA=25°C |  | 75 | 99 | µA | S1 p75 |
| 停止电流 | IDD | Flash深度掉电、主稳压器；VDD=1.7 V；TA=85°C |  |  | 310 | µA | S1 p75 |
| 停止电流 | IDD | Flash深度掉电、主稳压器；VDD=1.7 V；TA=105°C |  |  | 580 | µA | S1 p75 |
| 停止电流 | IDD | Flash深度掉电、主稳压器；VDD=1.7 V；TA=125°C |  |  | 993 | µA | S1 p75 |
| 停止电流 | IDD | Flash深度掉电、低功耗稳压器；VDD=1.7 V；TA=25°C |  | 13.6 | 37 | µA | S1 p75 |
| 停止电流 | IDD | Flash深度掉电、低功耗稳压器；VDD=1.7 V；TA=85°C |  |  | 265 | µA | S1 p75 |
| 停止电流 | IDD | Flash深度掉电、低功耗稳压器；VDD=1.7 V；TA=105°C |  |  | 550 | µA | S1 p75 |
| 停止电流 | IDD | Flash深度掉电、低功耗稳压器；VDD=1.7 V；TA=125°C |  |  | 1007 | µA | S1 p75 |
| 停止电流 | IDD | Flash深度掉电、低功耗低压模式；VDD=1.7 V；TA=25°C |  | 9 | 28 | µA | S1 p75 |
| 停止电流 | IDD | Flash深度掉电、低功耗低压模式；VDD=1.7 V；TA=85°C |  |  | 230 | µA | S1 p75 |
| 停止电流 | IDD | Flash深度掉电、低功耗低压模式；VDD=1.7 V；TA=105°C |  |  | 500 | µA | S1 p75 |
| 停止电流 | IDD | Flash深度掉电、低功耗低压模式；VDD=1.7 V；TA=125°C |  |  | 910 | µA | S1 p75 |
| 停止电流 | IDD | Flash Stop、主稳压器；VDD=3.6 V；TA=25°C |  | 113.7 | 145 | µA | S1 p76 |
| 停止电流 | IDD | Flash Stop、主稳压器；VDD=3.6 V；TA=85°C |  |  | 410 | µA | S1 p76 |
| 停止电流 | IDD | Flash Stop、主稳压器；VDD=3.6 V；TA=105°C |  |  | 720 | µA | S1 p76 |
| 停止电流 | IDD | Flash Stop、主稳压器；VDD=3.6 V；TA=125°C |  |  | 1217 | µA | S1 p76 |
| 停止电流 | IDD | Flash Stop、低功耗稳压器；VDD=3.6 V；TA=25°C |  | 43.1 | 68 | µA | S1 p76 |
| 停止电流 | IDD | Flash Stop、低功耗稳压器；VDD=3.6 V；TA=85°C |  |  | 310 | µA | S1 p76 |
| 停止电流 | IDD | Flash Stop、低功耗稳压器；VDD=3.6 V；TA=105°C |  |  | 600 | µA | S1 p76 |
| 停止电流 | IDD | Flash Stop、低功耗稳压器；VDD=3.6 V；TA=125°C |  |  | 1073 | µA | S1 p76 |
| 停止电流 | IDD | Flash深度掉电、主稳压器；VDD=3.6 V；TA=25°C |  | 76.2 | 105 | µA | S1 p76 |
| 停止电流 | IDD | Flash深度掉电、主稳压器；VDD=3.6 V；TA=85°C |  |  | 320 | µA | S1 p76 |
| 停止电流 | IDD | Flash深度掉电、主稳压器；VDD=3.6 V；TA=105°C |  |  | 600 | µA | S1 p76 |
| 停止电流 | IDD | Flash深度掉电、主稳压器；VDD=3.6 V；TA=125°C |  |  | 1019 | µA | S1 p76 |
| 停止电流 | IDD | Flash深度掉电、低功耗稳压器；VDD=3.6 V；TA=25°C |  | 14 | 38 | µA | S1 p76 |
| 停止电流 | IDD | Flash深度掉电、低功耗稳压器；VDD=3.6 V；TA=85°C |  |  | 275 | µA | S1 p76 |
| 停止电流 | IDD | Flash深度掉电、低功耗稳压器；VDD=3.6 V；TA=105°C |  |  | 560 | µA | S1 p76 |
| 停止电流 | IDD | Flash深度掉电、低功耗稳压器；VDD=3.6 V；TA=125°C |  |  | 1025 | µA | S1 p76 |
| 停止电流 | IDD | Flash深度掉电、低功耗低压模式；VDD=3.6 V；TA=25°C |  | 10 | 30 | µA | S1 p76 |
| 停止电流 | IDD | Flash深度掉电、低功耗低压模式；VDD=3.6 V；TA=85°C |  |  | 235 | µA | S1 p76 |
| 停止电流 | IDD | Flash深度掉电、低功耗低压模式；VDD=3.6 V；TA=105°C |  |  | 510 | µA | S1 p76 |
| 停止电流 | IDD | Flash深度掉电、低功耗低压模式；VDD=3.6 V；TA=125°C |  |  | 928 | µA | S1 p76 |
| 待机电流 | IDD | VDD=1.7 V；LSE及RTC开启；TA=25°C |  | 2.4 | 4 | µA | S1 p76 |
| 待机电流 | IDD | VDD=1.7 V；LSE及RTC开启；TA=85°C |  |  | 12 | µA | S1 p76 |
| 待机电流 | IDD | VDD=1.7 V；LSE及RTC开启；TA=105°C |  |  | 25 | µA | S1 p76 |
| 待机电流 | IDD | VDD=1.7 V；LSE及RTC开启；TA=125°C |  |  | 50 | µA | S1 p76 |
| 待机电流 | IDD | VDD=1.7 V；LSE及RTC关闭；TA=25°C |  | 1.8 | 3 | µA | S1 p76 |
| 待机电流 | IDD | VDD=1.7 V；LSE及RTC关闭；TA=85°C |  |  | 11 | µA | S1 p76 |
| 待机电流 | IDD | VDD=1.7 V；LSE及RTC关闭；TA=105°C |  |  | 24 | µA | S1 p76 |
| 待机电流 | IDD | VDD=1.7 V；LSE及RTC关闭；TA=125°C |  |  | 49 | µA | S1 p76 |
| 待机电流 | IDD | VDD=3.6 V；LSE及RTC开启；TA=25°C |  | 2.8 | 5 | µA | S1 p76 |
| 待机电流 | IDD | VDD=3.6 V；LSE及RTC开启；TA=85°C |  |  | 14 | µA | S1 p76 |
| 待机电流 | IDD | VDD=3.6 V；LSE及RTC开启；TA=105°C |  |  | 29 | µA | S1 p76 |
| 待机电流 | IDD | VDD=3.6 V；LSE及RTC开启；TA=125°C |  |  | 59 | µA | S1 p76 |
| 待机电流 | IDD | VDD=3.6 V；LSE及RTC关闭；TA=25°C |  | 2.1 | 4 | µA | S1 p76 |
| 待机电流 | IDD | VDD=3.6 V；LSE及RTC关闭；TA=85°C |  |  | 13.5 | µA | S1 p76 |
| 待机电流 | IDD | VDD=3.6 V；LSE及RTC关闭；TA=105°C |  |  | 28 | µA | S1 p76 |
| 待机电流 | IDD | VDD=3.6 V；LSE及RTC关闭；TA=125°C |  |  | 58 | µA | S1 p76 |
| 备用域电流 | IBAT | LSE低驱动、RTC开启；VBAT=1.7 V；TA=25°C |  | 0.7 |  | µA | S1 p77 |
| 备用域电流 | IBAT | LSE低驱动、RTC开启；VBAT=2.4 V；TA=25°C |  | 0.8 |  | µA | S1 p77 |
| 备用域电流 | IBAT | LSE低驱动、RTC开启；VBAT=3.3 V；TA=25°C |  | 1.0 |  | µA | S1 p77 |
| 备用域电流 | IBAT | LSE低驱动、RTC开启；VBAT=3.6 V；TA=85°C |  |  | 3 | µA | S1 p77 |
| 备用域电流 | IBAT | LSE低驱动、RTC开启；VBAT=3.6 V；TA=105°C |  |  | 5 | µA | S1 p77 |
| 备用域电流 | IBAT | LSE低驱动、RTC开启；VBAT=3.6 V；TA=125°C |  |  | 6.8 | µA | S1 p77 |
| 备用域电流 | IBAT | LSE高驱动、RTC开启；VBAT=1.7 V；TA=25°C |  | 1.5 |  | µA | S1 p77 |
| 备用域电流 | IBAT | LSE高驱动、RTC开启；VBAT=2.4 V；TA=25°C |  | 1.6 |  | µA | S1 p77 |
| 备用域电流 | IBAT | LSE高驱动、RTC开启；VBAT=3.3 V；TA=25°C |  | 1.9 |  | µA | S1 p77 |
| 备用域电流 | IBAT | LSE高驱动、RTC开启；VBAT=3.6 V；TA=85°C |  |  | 3.8 | µA | S1 p77 |
| 备用域电流 | IBAT | LSE高驱动、RTC开启；VBAT=3.6 V；TA=105°C |  |  | 5.8 | µA | S1 p77 |
| 备用域电流 | IBAT | LSE高驱动、RTC开启；VBAT=3.6 V；TA=125°C |  |  | 8.6 | µA | S1 p77 |
| 备用域电流 | IBAT | RTC关闭；VBAT=1.7 V；TA=25°C |  | 0.1 |  | µA | S1 p77 |
| 备用域电流 | IBAT | RTC关闭；VBAT=2.4 V；TA=25°C |  | 0.1 |  | µA | S1 p77 |
| 备用域电流 | IBAT | RTC关闭；VBAT=3.3 V；TA=25°C |  | 0.1 |  | µA | S1 p77 |
| 备用域电流 | IBAT | RTC关闭；VBAT=3.6 V；TA=85°C |  |  | 2 | µA | S1 p77 |
| 备用域电流 | IBAT | RTC关闭；VBAT=3.6 V；TA=105°C |  |  | 4 | µA | S1 p77 |
| 备用域电流 | IBAT | RTC关闭；VBAT=3.6 V；TA=125°C |  |  | 5.8 | µA | S1 p77 |
| 睡眠唤醒 | tWUSLEEP |  | 4 |  | 6 | CPU周期 | S1 p83 |
| Stop唤醒 | tWUSTOP | 主稳压器；Flash Stop |  | 13.5 | 14.5 | µs | S1 p83 |
| Stop唤醒 | tWUSTOP | 主稳压器；Flash深度掉电 |  | 105 | 111 | µs | S1 p83 |
| Stop唤醒 | tWUSTOP | 低功耗稳压器；Flash Stop |  | 21 | 33 | µs | S1 p83 |
| Stop唤醒 | tWUSTOP | 低功耗稳压器；Flash深度掉电 |  | 113 | 130 | µs | S1 p83 |
| 待机唤醒 | tWUSTDBY |  |  | 314 | 407 | µs | S1 p83 |
| Flash唤醒 | tWUFLASH | Stop |  |  | 8 | µs | S1 p83 |
| Flash唤醒 | tWUFLASH | 深度掉电 |  |  | 100 | µs | S1 p83 |
| 外部时钟频率 | fHSE | HSE旁路 | 1 |  | 50 | MHz | S1 p83 |
| 输入高电平 | VIH | HSE旁路 | 0.7 VDD |  | VDD | V | S1 p83 |
| 输入低电平 | VIL | HSE旁路 | VSS |  | 0.3 VDD | V | S1 p83 |
| 时钟高低脉宽 | tw | HSE旁路 | 5 |  |  | ns | S1 p83 |
| 时钟上升下降时间 | tr/tf | HSE旁路 |  |  | 10 | ns | S1 p83 |
| 占空比 | DuCy | HSE旁路 | 45 |  | 55 | % | S1 p83 |
| 漏电流 | Ilkg | HSE旁路 | −1 |  | 1 | µA | S1 p83 |
| 输入电容 | Cin | HSE旁路 |  | 5 |  | pF | S1 p83 |
| 外部时钟频率 | fLSE | LSE旁路 |  | 32.768 | 1000 | kHz | S1 p84 |
| 输入高电平 | VIH | LSE旁路 | 0.7 VDD |  | VDD | V | S1 p84 |
| 输入低电平 | VIL | LSE旁路 | VSS |  | 0.3 VDD | V | S1 p84 |
| 时钟高低脉宽 | tw | LSE旁路 | 450 |  |  | ns | S1 p84 |
| 时钟上升下降时间 | tr/tf | LSE旁路 |  |  | 50 | ns | S1 p84 |
| 占空比 | DuCy | LSE旁路 | 30 |  | 70 | % | S1 p84 |
| 漏电流 | Ilkg | LSE旁路 | −1 |  | 1 | µA | S1 p84 |
| 输入电容 | Cin | LSE旁路 |  | 5 |  | pF | S1 p84 |
| 晶体频率 | fHSE | HSE晶体 | 4 |  | 26 | MHz | S1 p85 |
| 临界跨导 | gmcrit | HSE |  |  | 1 | mA/V | S1 p85 |
| HSE启动 | tSU(HSE) | 标准8 MHz谐振器；取决于晶体 |  | 2 |  | ms | S1 p85 |
| LSE电流 | IDD(LSE) | 低驱动 |  |  | 1 | µA | S1 p86 |
| LSE临界跨导 | gmcrit | 低驱动 |  |  | 0.56 | µA/V | S1 p86 |
| LSE电流 | IDD(LSE) | 高驱动 |  |  | 3 | µA | S1 p86 |
| LSE临界跨导 | gmcrit | 高驱动 |  |  | 1.50 | µA/V | S1 p86 |
| LSE启动 | tSU(LSE) | 取决于晶体 |  | 2 |  | s | S1 p86 |
| 内部高速振荡频率 | fHSI |  |  | 16 |  | MHz | S1 p87 |
| HSI频差 | ACCHSI | 用户修调；全温 | −1 |  | 1 | % | S1 p87 |
| HSI频差 | ACCHSI | 工厂校准；−40～125°C | −8 |  | 5.5 | % | S1 p87 |
| HSI频差 | ACCHSI | 工厂校准；−40～105°C | −8 |  | 4.5 | % | S1 p87 |
| HSI频差 | ACCHSI | 工厂校准；−10～85°C | −4 |  | 4 | % | S1 p87 |
| HSI频差 | ACCHSI | 工厂校准；25°C、未焊接 | −1 |  | 1 | % | S1 p87 |
| HSI启动 | tSU(HSI) |  |  | 2.2 | 4 | µs | S1 p87 |
| HSI电流 | IDD(HSI) | VDD=3.3 V |  | 60 | 80 | µA | S1 p87 |
| LSI频率 | fLSI |  | 17 | 32 | 47 | kHz | S1 p88 |
| LSI启动 | tSU(LSI) |  |  | 15 | 40 | µs | S1 p88 |
| LSI电流 | IDD(LSI) | VDD=3 V |  | 0.4 | 0.6 | µA | S1 p88 |
| 锁相环输入频率 | fPLL_IN | PLL | 0.95 | 1 | 2.10 | MHz | S1 p89 |
| 锁相环输出频率 | fPLL_OUT | PLL | 24 |  | 100 | MHz | S1 p89 |
| VCO频率 | fVCO_OUT | PLL | 100 |  | 432 | MHz | S1 p89 |
| 锁相时间 | tLOCK | PLL；VCO=100 MHz | 75 |  | 200 | µs | S1 p89 |
| 锁相时间 | tLOCK | PLL；VCO=432 MHz | 100 |  | 300 | µs | S1 p89 |
| 锁相环输入频率 | fPLL_IN | PLLI2S | 0.95 | 1 | 2.10 | MHz | S1 p90 |
| 锁相环输出频率 | fPLL_OUT | PLLI2S |  |  | 216 | MHz | S1 p90 |
| VCO频率 | fVCO_OUT | PLLI2S | 100 |  | 432 | MHz | S1 p90 |
| 锁相时间 | tLOCK | PLLI2S；VCO=100 MHz | 75 |  | 200 | µs | S1 p90 |
| 锁相时间 | tLOCK | PLLI2S；VCO=432 MHz | 100 |  | 300 | µs | S1 p90 |
| USB等时钟频率 | fPLL48_OUT | 主PLL |  | 48 | 75 | MHz | S1 p89 |
| 锁相环电流 | IDD | PLL；VCO=100 MHz |  | 0.15 | 0.40 | mA | S1 p90 |
| 锁相环电流 | IDDA | PLL；VCO=100 MHz |  | 0.30 | 0.40 | mA | S1 p90 |
| 锁相环电流 | IDD | PLL；VCO=432 MHz |  | 0.45 | 0.75 | mA | S1 p90 |
| 锁相环电流 | IDDA | PLL；VCO=432 MHz |  | 0.55 | 0.85 | mA | S1 p90 |
| 锁相环电流 | IDD | PLLI2S；VCO=100 MHz |  | 0.15 | 0.40 | mA | S1 p90 |
| 锁相环电流 | IDDA | PLLI2S；VCO=100 MHz |  | 0.30 | 0.40 | mA | S1 p90 |
| 锁相环电流 | IDD | PLLI2S；VCO=432 MHz |  | 0.45 | 0.75 | mA | S1 p90 |
| 锁相环电流 | IDDA | PLLI2S；VCO=432 MHz |  | 0.55 | 0.85 | mA | S1 p90 |
| 扩频调制频率 | fMod |  |  |  | 10 | kHz | S1 p91 |
| 扩频深度 | md |  | 0.25 |  | 2 | % | S1 p91 |
| Flash编程电压 | Vprog | PSIZE=8 | 1.7 |  | 3.6 | V | S1 p93 |
| Flash编程电压 | Vprog | PSIZE=16 | 2.1 |  | 3.6 | V | S1 p93 |
| Flash编程电压 | Vprog | PSIZE=32 | 2.7 |  | 3.6 | V | S1 p93 |
| Flash单元编程时间 | tprog | 100 K次擦除后 |  | 16 | 100 | µs | S1 p93 |
| Flash擦除时间 | tERASE | 16 KB；PSIZE=8 |  | 400 | 800 | ms | S1 p93 |
| Flash擦除时间 | tERASE | 16 KB；PSIZE=16 |  | 300 | 600 | ms | S1 p93 |
| Flash擦除时间 | tERASE | 16 KB；PSIZE=32 |  | 250 | 500 | ms | S1 p93 |
| Flash擦除时间 | tERASE | 64 KB；PSIZE=8 |  | 1200 | 2400 | ms | S1 p93 |
| Flash擦除时间 | tERASE | 64 KB；PSIZE=16 |  | 700 | 1400 | ms | S1 p93 |
| Flash擦除时间 | tERASE | 64 KB；PSIZE=32 |  | 550 | 1100 | ms | S1 p93 |
| Flash擦除时间 | tERASE | 128 KB；PSIZE=8 |  | 2 | 4 | s | S1 p93 |
| Flash擦除时间 | tERASE | 128 KB；PSIZE=16 |  | 1.3 | 2.6 | s | S1 p93 |
| Flash擦除时间 | tERASE | 128 KB；PSIZE=32 |  | 1 | 2 | s | S1 p93 |
| Flash擦除时间 | tERASE | 全片 KB；PSIZE=8 |  | 8 | 16 | s | S1 p93 |
| Flash擦除时间 | tERASE | 全片 KB；PSIZE=16 |  | 5.5 | 11 | s | S1 p93 |
| Flash擦除时间 | tERASE | 全片 KB；PSIZE=32 |  | 4 | 8 | s | S1 p93 |
| 外部VPP编程时间 | tprog | 双字；TA=0～40°C、VDD=3.3 V、VPP=8.5 V |  | 16 | 100 | µs | S1 p93 |
| 外部编程电压 | VPP |  | 7 |  | 9 | V | S1 p94 |
| 编程电流 | IPP |  | 10 |  |  | mA | S1 p94 |
| 外部VPP累计时间 | tVPP | 只在编程擦除时施加 |  |  | 1 | hour | S1 p94 |
| 擦写寿命 | NEND | 对应温度范围6/7/3；见表注 | 10 |  |  | kcycles | S1 p94 |
| 数据保持 | tRET | 1 k次擦写；TA=85°C | 30 |  |  | 年 | S1 p94 |
| 数据保持 | tRET | 1 k次擦写；TA=105°C | 10 |  |  | 年 | S1 p94 |
| 数据保持 | tRET | 1 k次擦写；TA=125°C | 3 |  |  | 年 | S1 p94 |
| 数据保持 | tRET | 10 k次擦写；TA=55°C | 20 |  |  | 年 | S1 p94 |
| 数字高电平 | VIH | FT/TC/NRST；VDD=1.7～3.6 V | 0.7 VDD |  |  | V | S1 p98 |
| 数字低电平 | VIL | FT/TC/NRST；VDD=1.7～3.6 V |  |  | 0.3 VDD | V | S1 p98 |
| 启动低电平 | VIL | BOOT0；VDD=1.75～3.6 V全温，或1.7～3.6 V且TA≥0°C |  |  | 0.1 VDD+0.1 | V | S1 p98 |
| 启动高电平 | VIH | 同上 | 0.17 VDD+0.7 |  |  | V | S1 p98 |
| 输入迟滞 | Vhys | 数字输入 | 200 | 10% VDD |  | mV | S1 p98、p99 |
| 启动输入迟滞 | Vhys | BOOT0 |  | 100 |  | mV | S1 p98 |
| 输入漏电流 | Ilkg | VSS≤VIN≤VDD | −1 |  | 1 | µA | S1 p98 |
| 容限脚漏电流 | Ilkg | FT/TC、VIN=5 V |  |  | 3 | µA | S1 p98 |
| 内部上拉或下拉电阻 | RPU | 除PA10 | 30 | 40 | 50 | kΩ | S1 p99 |
| 内部上拉或下拉电阻 | RPD | 除PA10 | 30 | 40 | 50 | kΩ | S1 p99 |
| 内部上拉或下拉电阻 | RPU | PA10 | 7 | 10 | 14 | kΩ | S1 p99 |
| 内部上拉或下拉电阻 | RPD | PA10 | 7 | 10 | 14 | kΩ | S1 p99 |
| 输入电容 | CIO |  |  | 5 |  | pF | S1 p99 |
| 输出低电平 | VOL | CMOS；8 mA、VDD=2.7～3.6 V |  |  | 0.4 | V | S1 p101 |
| 输出高电平 | VOH | CMOS；8 mA、VDD=2.7～3.6 V | VDD−0.4 |  |  | V | S1 p101 |
| 输出低电平 | VOL | TTL；8 mA、VDD=2.7～3.6 V |  |  | 0.4 | V | S1 p101 |
| 输出高电平 | VOH | TTL；8 mA、VDD=2.7～3.6 V | 2.4 |  |  | V | S1 p101 |
| 输出低电平 | VOL | 20 mA、VDD=2.7～3.6 V |  |  | 1.3 | V | S1 p101 |
| 输出高电平 | VOH | 20 mA、VDD=2.7～3.6 V | VDD−1.3 |  |  | V | S1 p101 |
| 输出低电平 | VOL | 6 mA、VDD=1.8～3.6 V |  |  | 0.4 | V | S1 p101 |
| 输出高电平 | VOH | 6 mA、VDD=1.8～3.6 V | VDD−0.4 |  |  | V | S1 p101 |
| 输出低电平 | VOL | 4 mA、VDD=1.7～3.6 V |  |  | 0.4 | V | S1 p101 |
| 输出高电平 | VOH | 4 mA、VDD=1.7～3.6 V | VDD−0.4 |  |  | V | S1 p101 |
| I/O最高频率 | fmax | OSPEED=00；CL=50 pF；VDD=2.7～3.6 V |  |  | 4 | MHz | S1 p102 |
| I/O最高频率 | fmax | OSPEED=00；CL=50 pF；VDD=1.7～3.6 V |  |  | 2 | MHz | S1 p102 |
| I/O最高频率 | fmax | OSPEED=00；CL=10 pF；VDD=2.7～3.6 V |  |  | 8 | MHz | S1 p102 |
| I/O最高频率 | fmax | OSPEED=00；CL=10 pF；VDD=1.7～3.6 V |  |  | 4 | MHz | S1 p102 |
| I/O最高频率 | fmax | OSPEED=01；CL=50 pF；VDD=2.7～3.6 V |  |  | 25 | MHz | S1 p102 |
| I/O最高频率 | fmax | OSPEED=01；CL=50 pF；VDD=1.7～3.6 V |  |  | 12.5 | MHz | S1 p102 |
| I/O最高频率 | fmax | OSPEED=01；CL=10 pF；VDD=2.7～3.6 V |  |  | 50 | MHz | S1 p102 |
| I/O最高频率 | fmax | OSPEED=01；CL=10 pF；VDD=1.7～3.6 V |  |  | 20 | MHz | S1 p102 |
| I/O最高频率 | fmax | OSPEED=10；CL=40 pF；VDD=2.7～3.6 V |  |  | 50 | MHz | S1 p102 |
| I/O最高频率 | fmax | OSPEED=10；CL=40 pF；VDD=1.7～3.6 V |  |  | 25 | MHz | S1 p102 |
| I/O最高频率 | fmax | OSPEED=10；CL=10 pF；VDD=2.7～3.6 V |  |  | 100 | MHz | S1 p102 |
| I/O最高频率 | fmax | OSPEED=10；CL=10 pF；VDD=1.7～3.6 V |  |  | 50 | MHz | S1 p102 |
| I/O最高频率 | fmax | OSPEED=11；CL=30 pF；VDD=2.7～3.6 V |  |  | 100 | MHz | S1 p103 |
| I/O最高频率 | fmax | OSPEED=11；CL=30 pF；VDD=1.7～3.6 V |  |  | 50 | MHz | S1 p103 |
| I/O上升下降时间 | tr/tf | OSPEED=00；CL=50 pF；VDD=1.7～3.6 V |  |  | 100 | ns | S1 p102 |
| I/O上升下降时间 | tr/tf | OSPEED=01；CL=50 pF；VDD=2.7～3.6 V |  |  | 10 | ns | S1 p102 |
| I/O上升下降时间 | tr/tf | OSPEED=01；CL=50 pF；VDD=1.7～3.6 V |  |  | 20 | ns | S1 p102 |
| I/O上升下降时间 | tr/tf | OSPEED=01；CL=10 pF；VDD=2.7～3.6 V |  |  | 6 | ns | S1 p102 |
| I/O上升下降时间 | tr/tf | OSPEED=01；CL=10 pF；VDD=1.7～3.6 V |  |  | 10 | ns | S1 p102 |
| I/O上升下降时间 | tr/tf | OSPEED=10；CL=40 pF；VDD=2.7～3.6 V |  |  | 6 | ns | S1 p102 |
| I/O上升下降时间 | tr/tf | OSPEED=10；CL=40 pF；VDD=1.7～3.6 V |  |  | 10 | ns | S1 p102 |
| I/O上升下降时间 | tr/tf | OSPEED=10；CL=10 pF；VDD=2.7～3.6 V |  |  | 4 | ns | S1 p102 |
| I/O上升下降时间 | tr/tf | OSPEED=10；CL=10 pF；VDD=1.7～3.6 V |  |  | 6 | ns | S1 p102 |
| I/O上升下降时间 | tr/tf | OSPEED=11；CL=30 pF；VDD=2.7～3.6 V |  |  | 4 | ns | S1 p103 |
| I/O上升下降时间 | tr/tf | OSPEED=11；CL=30 pF；VDD=1.7～3.6 V |  |  | 6 | ns | S1 p103 |
| I/O上升下降时间 | tr/tf | OSPEED=11；CL=10 pF；VDD=2.7～3.6 V |  |  | 2.5 | ns | S1 p103 |
| I/O上升下降时间 | tr/tf | OSPEED=11；CL=10 pF；VDD=1.7～3.6 V |  |  | 4 | ns | S1 p103 |
| 外部中断脉宽 | tEXTIpw |  | 10 |  |  | ns | S1 p103 |
| 复位上拉 | RPU | NRST | 30 | 40 | 50 | kΩ | S1 p104 |
| 被滤除复位脉宽 | VF(NRST) |  |  |  | 100 | ns | S1 p104 |
| 不被滤除复位脉宽 | VNF(NRST) | VDD>2.7 V | 300 |  |  | ns | S1 p104 |
| 生成复位脉宽 | tNRST_OUT |  | 20 |  |  | µs | S1 p104 |
| 定时器分辨率 | tres(TIM) | 手册100 MHz示例 | 11.9 |  |  | ns | S1 p105 |
| 定时器外部时钟 | fEXT | 输入滤波关闭 | 0 |  | 50 | MHz | S1 p105 |
| 计数器周期 | tCOUNTER | 100 MHz | 0.0119 |  | 780 | µs | S1 p105 |
| 最大计数 | tMAX_COUNT | 100 MHz |  |  | 51.1 | s | S1 p105 |
| I²C SCL低 | tLOW | 标准模式；保持上限仅适用无SCL延长条件 | 4.7 |  |  | µs | S1 p106 |
| I²C SCL高 | tHIGH | 标准模式；保持上限仅适用无SCL延长条件 | 4 |  |  | µs | S1 p106 |
| I²C SDA建立 | tSU;DAT | 标准模式；保持上限仅适用无SCL延长条件 | 250 |  |  | ns | S1 p106 |
| I²C SDA保持 | tHD;DAT | 标准模式；保持上限仅适用无SCL延长条件 | 0 |  | 3450 | ns | S1 p106 |
| I²C 上升 | tr | 标准模式；保持上限仅适用无SCL延长条件 |  |  | 1000 | ns | S1 p106 |
| I²C 下降 | tf | 标准模式；保持上限仅适用无SCL延长条件 |  |  | 300 | ns | S1 p106 |
| I²C 启动保持 | tHD;STA | 标准模式；保持上限仅适用无SCL延长条件 | 4 |  |  | µs | S1 p106 |
| I²C 重复启动建立 | tSU;STA | 标准模式；保持上限仅适用无SCL延长条件 | 4.7 |  |  | µs | S1 p106 |
| I²C 停止建立 | tSU;STO | 标准模式；保持上限仅适用无SCL延长条件 | 4 |  |  | µs | S1 p106 |
| I²C 总线空闲 | tBUF | 标准模式；保持上限仅适用无SCL延长条件 | 4.7 |  |  | µs | S1 p106 |
| I²C SCL低 | tLOW | 快速模式；保持上限仅适用无SCL延长条件 | 1.3 |  |  | µs | S1 p106 |
| I²C SCL高 | tHIGH | 快速模式；保持上限仅适用无SCL延长条件 | 0.6 |  |  | µs | S1 p106 |
| I²C SDA建立 | tSU;DAT | 快速模式；保持上限仅适用无SCL延长条件 | 100 |  |  | ns | S1 p106 |
| I²C SDA保持 | tHD;DAT | 快速模式；保持上限仅适用无SCL延长条件 | 0 |  | 900 | ns | S1 p106 |
| I²C 上升 | tr | 快速模式；保持上限仅适用无SCL延长条件 |  |  | 300 | ns | S1 p106 |
| I²C 下降 | tf | 快速模式；保持上限仅适用无SCL延长条件 |  |  | 300 | ns | S1 p106 |
| I²C 启动保持 | tHD;STA | 快速模式；保持上限仅适用无SCL延长条件 | 0.6 |  |  | µs | S1 p106 |
| I²C 重复启动建立 | tSU;STA | 快速模式；保持上限仅适用无SCL延长条件 | 0.6 |  |  | µs | S1 p106 |
| I²C 停止建立 | tSU;STO | 快速模式；保持上限仅适用无SCL延长条件 | 0.6 |  |  | µs | S1 p106 |
| I²C 总线空闲 | tBUF | 快速模式；保持上限仅适用无SCL延长条件 | 1.3 |  |  | µs | S1 p106 |
| I²C滤除毛刺 | tSP | 模拟滤波开启 | 0 |  | 50 | ns | S1 p106 |
| I²C总线电容 | Cb |  |  |  | 400 | pF | S1 p106 |
| SPI最高时钟 | fSCK | SPI1/4/5主接收、全双工；2.7<VDD<3.6 V |  |  | 42 | MHz | S1 p108 |
| SPI最高时钟 | fSCK | SPI1/4/5主接收、全双工；3<VDD<3.6 V |  |  | 50 | MHz | S1 p108 |
| SPI最高时钟 | fSCK | SPI1/4/5主发送；VDD≥1.7 V |  |  | 50 | MHz | S1 p108 |
| SPI最高时钟 | fSCK | 所有SPI主模式；VDD≥1.7 V |  |  | 25 | MHz | S1 p108 |
| SPI最高时钟 | fSCK | SPI1/4/5从发送、全双工；VDD>2.7 V；主机建立0、占空50% |  |  | 38 | MHz | S1 p108 |
| SPI最高时钟 | fSCK | SPI1/4/5从接收；VDD≥1.8 V |  |  | 50 | MHz | S1 p108 |
| SPI最高时钟 | fSCK | 所有SPI从模式；VDD≥1.8 V |  |  | 25 | MHz | S1 p108 |
| SPI占空比 | DuCy | 从模式 | 30 | 50 | 70 | % | S1 p108 |
| SPI NSS建立 | tSU(NSS) | 从模式 | 3 TPCLK |  |  | ns | S1 p108 |
| SPI NSS保持 | tH(NSS) | 从模式 | 2 TPCLK |  |  | ns | S1 p108 |
| SPI 输入建立 | tSU(MI) | 主模式 | 4 |  |  | ns | S1 p108 |
| SPI 输入建立 | tSU(SI) | 从模式 | 2.5 |  |  | ns | S1 p108 |
| SPI 输入保持 | tH(MI) | 主模式 | 7.5 |  |  | ns | S1 p108 |
| SPI 输入保持 | tH(SI) | 从模式 | 3.5 |  |  | ns | S1 p108 |
| SPI主时钟高低时间 | tw(SCK) | 分频2 | TPCLK−1.5 | TPCLK | TPCLK+1.5 | ns | S1 p108 |
| SPI从输出访问 | ta(SO) |  | 7 |  | 21 | ns | S1 p109 |
| SPI从输出禁止 | tdis(SO) |  | 5 |  | 12 | ns | S1 p109 |
| SPI数据有效 | tv | 从输出、VDD≥2.7 V |  | 11 | 13 | ns | S1 p109 |
| SPI数据有效 | tv | 从输出、VDD≥1.7 V |  |  | 18.5 | ns | S1 p109 |
| SPI数据有效 | tv | 主输出 |  | 4 | 6 | ns | S1 p109 |
| SPI从输出保持 | th(SO) | VDD≥1.7 V | 8 |  |  | ns | S1 p109 |
| SPI主输出保持 | th(MO) |  | 0 |  |  | ns | S1 p109 |
| I²S主时钟 | fMCK |  | 256×8 K |  | 256×Fs | Hz | S1 p111 |
| I²S位时钟 | fCK | 32 bit |  |  | 64×Fs | Hz | S1 p111 |
| I²S从接收占空比 | DuCy | 从接收 | 30 |  | 70 | % | S1 p111 |
| I²S WS有效 | tv(WS) | 主模式 | 0 |  | 7 | ns | S1 p111 |
| I²S WS保持 | th(WS) | 主模式 | 1.5 |  |  | ns | S1 p111 |
| I²S WS建立 | tsu(WS) | 从模式 | 1.5 |  |  | ns | S1 p111 |
| I²S WS保持 | th(WS) | 从模式 | 3 |  |  | ns | S1 p111 |
| I²S 数据建立 | tsu(MR) | 主接收 | 1 |  |  | ns | S1 p111 |
| I²S 数据建立 | tsu(SR) | 从接收 | 2.5 |  |  | ns | S1 p111 |
| I²S 数据保持 | th(MR) | 主接收 | 7 |  |  | ns | S1 p111 |
| I²S 数据保持 | th(SR) | 从接收 | 2.5 |  |  | ns | S1 p111 |
| I²S 数据有效 | tv(SD_ST) | 从发送 |  |  | 20 | ns | S1 p111 |
| I²S 数据有效 | tv(SD_MT) | 主发送 |  |  | 6 | ns | S1 p111 |
| I²S 数据保持 | th(SD_ST) | 从发送 | 8 |  |  | ns | S1 p111 |
| I²S 数据保持 | th(SD_MT) | 主发送 | 2 |  |  | ns | S1 p111 |
| USB启动 | tSTARTUP |  |  |  | 1 | µs | S1 p113 |
| USB供电 | VDDUSB | 2.7 V可工作但性能退化 | 3 |  | 3.6 | V | S1 p113 |
| USB 差分输入灵敏度 | VDI | 输出测试负载见表64 | 0.2 |  |  | V | S1 p113 |
| USB 差分共模 | VCM | 输出测试负载见表64 | 0.8 |  | 2.5 | V | S1 p113 |
| USB 单端阈值 | VSE | 输出测试负载见表64 | 1.3 |  | 2 | V | S1 p113 |
| USB 输出低 | VOL | 输出测试负载见表64 |  |  | 0.3 | V | S1 p113 |
| USB 输出高 | VOH | 输出测试负载见表64 | 2.8 |  | 3.6 | V | S1 p113 |
| USB 下拉 | RPD | DM/DP | 17 | 21 | 24 | kΩ | S1 p113 |
| USB 下拉 | RPD | PA9 | 0.65 | 1.1 | 2 | kΩ | S1 p113 |
| USB 上拉 | RPU | DM/DP | 1.5 | 1.8 | 2.1 | kΩ | S1 p113 |
| USB 上拉 | RPU | PA9 | 0.25 | 0.37 | 0.55 | kΩ | S1 p113 |
| USB上升下降时间 | tr/tf | CL=50 pF | 4 |  | 20 | ns | S1 p114 |
| USB上升下降匹配 | tr/tf |  | 90 |  | 110 | % | S1 p114 |
| USB交叉电压 | VCRS |  | 1.3 |  | 2 | V | S1 p114 |
| ADC模拟供电 | VDDA |  | 1.7 |  | 3.6 | V | S1 p114 |
| ADC参考 | VREF+ | VDDA−VREF+<1.2 V | 1.7 |  | VDDA | V | S1 p114 |
| ADC时钟 | fADC | VDDA=1.7～2.4 V | 0.6 | 15 | 18 | MHz | S1 p114 |
| ADC时钟 | fADC | VDDA=2.4～3.6 V | 0.6 | 30 | 36 | MHz | S1 p114 |
| ADC外部触发频率 | fTRIG | 12 bit，fADC=30 MHz |  |  | 1764 | kHz | S1 p114 |
| ADC输入范围 | VAIN |  | 0 |  | VREF+ | V | S1 p114 |
| ADC外部阻抗 | RAIN | 还须满足采样时间计算公式 |  |  | 50 | kΩ | S1 p114 |
| ADC采样开关电阻 | RADC |  |  |  | 6 | kΩ | S1 p114 |
| ADC采样电容 | CADC |  |  | 4 | 7 | pF | S1 p114 |
| ADC注入延迟 | tlat | fADC=30 MHz |  |  | 0.100 | µs | S1 p115 |
| ADC规则延迟 | tlat | fADC=30 MHz |  |  | 0.067 | µs | S1 p115 |
| ADC采样时间 | tS | fADC=30 MHz | 0.100 |  | 16 | µs | S1 p115 |
| ADC启动时间 | tSTAB |  |  | 2 | 3 | µs | S1 p115 |
| ADC总转换时间 | tCONV | 12 bit、30 MHz | 0.50 |  | 16.40 | µs | S1 p115 |
| ADC总转换时间 | tCONV | 10 bit、30 MHz | 0.43 |  | 16.34 | µs | S1 p115 |
| ADC总转换时间 | tCONV | 8 bit、30 MHz | 0.37 |  | 16.27 | µs | S1 p115 |
| ADC总转换时间 | tCONV | 6 bit、30 MHz | 0.30 |  | 16.20 | µs | S1 p115 |
| ADC参考电流 | IVREF+ |  |  | 300 | 500 | µA | S1 p115 |
| ADC模拟电流 | IVDDA |  |  | 1.6 | 1.8 | mA | S1 p115 |
| ADC 总误差 | ET | 18 MHz、VDDA=1.7～3.6 V；VREF+=1.7～3.6 V、VDDA−VREF+<1.2 V；数值为±幅度 |  | 3 | 4 | LSB | S1 p116 |
| ADC 偏移误差 | EO | 18 MHz、VDDA=1.7～3.6 V；VREF+=1.7～3.6 V、VDDA−VREF+<1.2 V；数值为±幅度 |  | 2 | 3 | LSB | S1 p116 |
| ADC 增益误差 | EG | 18 MHz、VDDA=1.7～3.6 V；VREF+=1.7～3.6 V、VDDA−VREF+<1.2 V；数值为±幅度 |  | 1 | 3 | LSB | S1 p116 |
| ADC 微分非线性 | ED | 18 MHz、VDDA=1.7～3.6 V；VREF+=1.7～3.6 V、VDDA−VREF+<1.2 V；数值为±幅度 |  | 1 | 2 | LSB | S1 p116 |
| ADC 积分非线性 | EL | 18 MHz、VDDA=1.7～3.6 V；VREF+=1.7～3.6 V、VDDA−VREF+<1.2 V；数值为±幅度 |  | 2 | 3 | LSB | S1 p116 |
| ADC 总误差 | ET | 30 MHz、VDDA=2.4～3.6 V、RAIN<10 kΩ；VREF+=1.7～3.6 V、VDDA−VREF+<1.2 V；数值为±幅度 |  | 2 | 5 | LSB | S1 p116 |
| ADC 偏移误差 | EO | 30 MHz、VDDA=2.4～3.6 V、RAIN<10 kΩ；VREF+=1.7～3.6 V、VDDA−VREF+<1.2 V；数值为±幅度 |  | 1.5 | 2.5 | LSB | S1 p116 |
| ADC 增益误差 | EG | 30 MHz、VDDA=2.4～3.6 V、RAIN<10 kΩ；VREF+=1.7～3.6 V、VDDA−VREF+<1.2 V；数值为±幅度 |  | 1.5 | 4 | LSB | S1 p116 |
| ADC 微分非线性 | ED | 30 MHz、VDDA=2.4～3.6 V、RAIN<10 kΩ；VREF+=1.7～3.6 V、VDDA−VREF+<1.2 V；数值为±幅度 |  | 1 | 2 | LSB | S1 p116 |
| ADC 积分非线性 | EL | 30 MHz、VDDA=2.4～3.6 V、RAIN<10 kΩ；VREF+=1.7～3.6 V、VDDA−VREF+<1.2 V；数值为±幅度 |  | 1.5 | 3 | LSB | S1 p116 |
| ADC 总误差 | ET | 36 MHz、VDDA=2.4～3.6 V；VREF+=1.7～3.6 V、VDDA−VREF+<1.2 V；数值为±幅度 |  | 4 | 7 | LSB | S1 p116 |
| ADC 偏移误差 | EO | 36 MHz、VDDA=2.4～3.6 V；VREF+=1.7～3.6 V、VDDA−VREF+<1.2 V；数值为±幅度 |  | 2 | 3 | LSB | S1 p116 |
| ADC 增益误差 | EG | 36 MHz、VDDA=2.4～3.6 V；VREF+=1.7～3.6 V、VDDA−VREF+<1.2 V；数值为±幅度 |  | 3 | 6 | LSB | S1 p116 |
| ADC 微分非线性 | ED | 36 MHz、VDDA=2.4～3.6 V；VREF+=1.7～3.6 V、VDDA−VREF+<1.2 V；数值为±幅度 |  | 2 | 3 | LSB | S1 p116 |
| ADC 积分非线性 | EL | 36 MHz、VDDA=2.4～3.6 V；VREF+=1.7～3.6 V、VDDA−VREF+<1.2 V；数值为±幅度 |  | 3 | 6 | LSB | S1 p116 |
| ADC 有效位数 | ENOB | 18 MHz、VDDA=VREF+=1.7 V；输入20 kHz、25°C；表征、非生产测试 | 10.3 | 10.4 |  | bits | S1 p117 |
| ADC 信噪失真比 | SINAD | 18 MHz、VDDA=VREF+=1.7 V；输入20 kHz、25°C；表征、非生产测试 | 64 | 64.2 |  | dB | S1 p117 |
| ADC 信噪比 | SNR | 18 MHz、VDDA=VREF+=1.7 V；输入20 kHz、25°C；表征、非生产测试 | 64 | 65 |  | dB | S1 p117 |
| ADC 总谐波失真 | THD | 18 MHz、VDDA=VREF+=1.7 V；输入20 kHz、25°C；表征、非生产测试 |  | −72 | −67 | dB | S1 p117 |
| ADC 有效位数 | ENOB | 36 MHz、VDDA=VREF+=3.3 V；输入20 kHz、25°C；表征、非生产测试 | 10.6 | 10.8 |  | bits | S1 p117 |
| ADC 信噪失真比 | SINAD | 36 MHz、VDDA=VREF+=3.3 V；输入20 kHz、25°C；表征、非生产测试 | 66 | 67 |  | dB | S1 p117 |
| ADC 信噪比 | SNR | 36 MHz、VDDA=VREF+=3.3 V；输入20 kHz、25°C；表征、非生产测试 | 64 | 68 |  | dB | S1 p117 |
| ADC 总谐波失真 | THD | 36 MHz、VDDA=VREF+=3.3 V；输入20 kHz、25°C；表征、非生产测试 |  | −72 | −70 | dB | S1 p117 |
| 温度传感器线性度 | TL | 幅度 |  | 1 | 2 | °C | S1 p120 |
| 温度传感器斜率 | Avg_Slope |  |  | 2.5 |  | mV/°C | S1 p120 |
| 温度传感器输出 | V25 | 25°C |  | 0.76 |  | V | S1 p120 |
| 温度传感器启动 | tSTART |  |  | 6 | 10 | µs | S1 p120 |
| 温度传感器采样 | tS_temp | 达到1°C精度 | 10 |  |  | µs | S1 p120 |
| VBAT采样电阻 | R | 分压桥 |  | 50 |  | kΩ | S1 p121 |
| VBAT分压比 | Q |  |  | 4 |  |  | S1 p121 |
| VBAT测量误差 | Er |  | −1 |  | 1 | % | S1 p121 |
| VBAT采样时间 | tS_vbat | 达到1 mV精度 | 5 |  |  | µs | S1 p121 |
| 内部参考电压 | VREFINT | −40<TA<125°C | 1.18 | 1.21 | 1.24 | V | S1 p121 |
| 内部参考采样 | tS_vrefint |  | 10 |  |  | µs | S1 p121 |
| 内部参考温漂幅度 | VRERINT_SPREAD | VDD=3 V±0.01 V |  | 3 | 5 | mV | S1 p121 |
| 内部参考温度系数 | TCoeff |  |  | 30 | 50 | ppm/°C | S1 p121 |
| 内部参考启动 | tSTART |  |  | 6 | 10 | µs | S1 p121 |
| SDIO时钟 | fPP | SDIO高速、2.7～3.6 V、CL=30 pF | 0 |  | 50 | MHz | S1 p123 |
| SDIO与APB时钟比 | SDIO_CK/PCLK2 | SDIO高速、2.7～3.6 V、CL=30 pF |  |  | 8/3 |  | S1 p123 |
| SDIO时钟低 | tw(CK) | SDIO高速、2.7～3.6 V、CL=30 pF | 10.5 | 11 |  | ns | S1 p123 |
| SDIO时钟高 | tw(CK) | SDIO高速、2.7～3.6 V、CL=30 pF | 8.5 | 9 |  | ns | S1 p123 |
| SDIO输入建立 | tISU | SDIO高速、2.7～3.6 V、CL=30 pF | 2.5 |  |  | ns | S1 p123 |
| SDIO输入保持 | tIH | SDIO高速、2.7～3.6 V、CL=30 pF | 5 |  |  | ns | S1 p123 |
| SDIO输出有效 | tOV | SDIO高速、2.7～3.6 V、CL=30 pF |  | 3.5 | 4 | ns | S1 p123 |
| SDIO输出保持 | tOH | SDIO高速、2.7～3.6 V、CL=30 pF | 2 |  |  | ns | S1 p123 |
| SDIO时钟 | fPP | eMMC高速、1.7～1.9 V、CL=20 pF | 0 |  | 50 | MHz | S1 p124 |
| SDIO与APB时钟比 | SDIO_CK/PCLK2 | eMMC高速、1.7～1.9 V、CL=20 pF |  |  | 8/3 |  | S1 p124 |
| SDIO时钟低 | tw(CK) | eMMC高速、1.7～1.9 V、CL=20 pF | 10 | 10.5 |  | ns | S1 p124 |
| SDIO时钟高 | tw(CK) | eMMC高速、1.7～1.9 V、CL=20 pF | 9 | 9.5 |  | ns | S1 p124 |
| SDIO输入建立 | tISU | eMMC高速、1.7～1.9 V、CL=20 pF | 0 |  |  | ns | S1 p124 |
| SDIO输入保持 | tIH | eMMC高速、1.7～1.9 V、CL=20 pF | 6 |  |  | ns | S1 p124 |
| SDIO输出有效 | tOV | eMMC高速、1.7～1.9 V、CL=20 pF |  | 3.5 | 5 | ns | S1 p124 |
| SDIO输出保持 | tOH | eMMC高速、1.7～1.9 V、CL=20 pF | 2 |  |  | ns | S1 p124 |
| SDIO输入保持 | tIH | SDIO高速、仅−40～85°C | 2.5 |  |  | ns | S1 p123 |
| SDIO默认模式输入建立 | tISU | 25 MHz | 3 |  |  | ns | S1 p123 |
| SDIO默认模式输入保持 | tIH | 25 MHz | 4 |  |  | ns | S1 p123 |
| SDIO默认模式输出有效 | tOV | 25 MHz |  | 5 | 5.5 | ns | S1 p123 |
| SDIO默认模式输出保持 | tOH | 25 MHz | 4.5 |  |  | ns | S1 p123 |
| RTC寄存器访问时钟比 | fPCLK1/fRTCCLK |  | 4 |  |  |  | S1 p124 |

用这些数时要注意：

- 电源连接图给VDDA的100 nF+1 µF，而ADC设计指南给10 nF+1 µF；两处原文值均保留，不能混称一致（S1 p60、p119–p120）。

- 运行/睡眠/停止/待机多数最大电流来自表征，未逐个生产测试；仅指定的84 MHz最大值有生产测试脚注。测试时I/O静态、不带负载；ADC开启还需加模拟部分电流；电压档与时钟配置按表注，不能跨条件套用（S1 p68–p81）。
- 1.7 V工作须外部电源监控；低供电的Flash编程位宽、等待周期、ADC速度与I/O补偿功能受限制（S1 p63、p93、p142）。
- HSE/LSE启动、温度传感器斜率、25°C电压、VBAT分压阻抗和比例只有典型值。Flash编程/擦除最大时间、温度传感器及ADC精度等表征项目须按表脚注理解（S1 p85–p94、p114–p121）。
- FT/TC 5 V容限取决于VDD、脚型、复用功能和内部上下拉；模拟输入不得因此接受5 V。电压高于VDD+0.3 V时须禁用内部上下拉。注入负电流会降低其他ADC通道精度，可能需要外部肖特基钳位（S1 p63、p97–p99、p117）。
- ADC表66列出双/三ADC采样率，但器件首页仅有1个ADC；不将这些表行当作本型号的多ADC能力。首页停止电流65 µA与详细表的67/68 µA不一致，以明确条件的详细表分别记录（S1 p1、p75–p76、p115）。
- 定时器表的100 MHz示例同时写11.9 ns、0.0119 µs；本条保留原数，不自行重算。SDIO高速保持时间随温度条件改变；SPI高频还受电压、模式与SPI实例限制（S1 p105、p108、p123）。
- 超过50 MHz且VDD>2.4 V的I/O应启用补偿单元。SPI/I²S/SDIO时序的OSPEED、CL、测量电平必须满足原表条件；不能以典型延迟作为最大延迟（S1 p103、p108–p111、p123–p124）。

## 热特性

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- |
| 结到环境热阻 | ΘJA | LQFP64；JESD51-2 自然对流 | 47 | °C/W | S1 p140 |

## 静电额定

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- |
| 人体模型 | VESD(HBM) | TA=25°C；JESD22-A114 | 2000 | V | S1 p96 |
| 充电器件模型 | VESD(CDM) | LQFP64；ANSI/ESD STM5.3.1 | 250 | V | S1 p96 |

手册未给出单独的静电敏感警告。

## 引脚与处置

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
| --- | --- | --- | --- | --- |
| 1 VBAT | 电源/地/稳压器输出 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 2 PC13 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 3 PC14-OSC32_IN | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 4 PC15-OSC32_OUT | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 5 PH0-OSC_IN | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 6 PH1-OSC_OUT | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 7 NRST | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 8 PC0 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 9 PC1 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 10 PC2 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 11 PC3 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 12 VSSA/VREF- | 电源/地/稳压器输出 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 13 VDDA/VREF+ | 电源/地/稳压器输出 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 14 PA0 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 15 PA1 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 16 PA2 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 17 PA3 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 18 VSS | 电源/地/稳压器输出 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 19 VDD | 电源/地/稳压器输出 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 20 PA4 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 21 PA5 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 22 PA6 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 23 PA7 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 24 PC4 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 25 PC5 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 26 PB0 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 27 PB1 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 28 PB2 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 29 PB10 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 30 VCAP_1 | 电源/地/稳压器输出 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 31 VSS | 电源/地/稳压器输出 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 32 VDD | 电源/地/稳压器输出 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 33 PB12 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 34 PB13 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 35 PB14 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 36 PB15 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 37 PC6 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 38 PC7 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 39 PC8 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 40 PC9 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 41 PA8 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 42 PA9 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 43 PA10 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 44 PA11 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 45 PA12 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 46 PA13 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 47 VSS | 电源/地/稳压器输出 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 48 VDD | 电源/地/稳压器输出 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 49 PA14 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 50 PA15 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 51 PC10 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 52 PC11 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 53 PC12 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 54 PD2 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 55 PB3 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 56 PB4 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 57 PB5 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 58 PB6 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 59 PB7 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 60 BOOT0 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 61 PB8 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 62 PB9 | 复用I/O或专用输入，复用映射见手册引脚表 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 63 VSS | 电源/地/稳压器输出 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |
| 64 VDD | 电源/地/稳压器输出 | 按推荐条件及引脚类型；不能统一当作5 V容限 | 按下述处置 | S1 p36、p39–p47 |

散热焊盘：LQFP64 封装图未给出底部散热焊盘（S1 p129–p130）。
LQFP64 引脚表单独列出。VDDA/VSSA 必须接电源/地；没有独立 VREF± 引脚。未用 VBAT 接 VDD；未用普通I/O按低功耗配置及复位态处置，手册未逐脚规定固定接法。BOOT0 应固定为所需启动模式。晶振不用时改用内部时钟；VCAP_1 不作电源输出（S1 p26–p32、p39–p47）。

## 必需外围

- 每个 VDD 脚配 100 nF 去耦，供电配 4.7 µF；VDDA 配 1 µF 与 10 nF 并联，靠近引脚；没有独立 VREF 引脚时内部接 VDDA/VSSA（S1 p60、p119–p120）。
- 单 VCAP_1 配 4.7 µF，ESR<1 Ω，靠近引脚；不能把双 VCAP 封装的每脚2.2 µF直接套用（S1 p65–p66）。
- NRST 推荐接 0.1 µF 对地，外部复位驱动必须满足低电平门限（S1 p104）。
- HSE/LSE 电容由晶体负载要求选择，启动时间典型值不能用作保证上限（S1 p85–p86）。
- I²C外部上拉按总线电容选择；PCLK1 标准模式至少2 MHz、快速模式至少4 MHz，400 kHz要求时钟为10 MHz的整数倍（S1 p106–p107）。

## 订货型号与封装

手册列出的型号与封装如下；空格表示手册未给出，不从型号自行推算。

| 订货型号或后缀 | 封装 | 脚数 | 电压或功能档 | 温度范围 | 引脚镀层 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| STM32F411RE；T；6/7/3；可选TR | LQFP | 64 | E=512 Kbytes Flash | 6：−40～85°C；7：−40～105°C；3：−40～125°C |  | S1 p141 |



## 核对记录

- 2026-11-10：工具核对通过，核对了 1347 个数。
