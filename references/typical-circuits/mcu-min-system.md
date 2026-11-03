# MCU 最小系统

功能：Cortex-M MCU 的供电去耦、复位、启动脚、外部晶体与未用脚处置。

适用范围：3.3 V 单电源 Cortex-M3 级 MCU，LQFP48。

电路类型：STARTUP、CLOCK

## 实现方案

### STM32F1 LQFP48：去耦 + NRST RC + BOOT 下拉 + HSE 晶体

- **适用范围**：通用工业控制板，外部 8 MHz 晶体、SWD 下载
- **核心器件类**：01 32位ARM_Cortex-M_MCU、无源晶体、陶瓷电容、22 电阻
- **必需外围**：每个 VDD 一颗 100 nF + 一颗大电容；VDDA 单独去耦；NRST 对地电容；BOOT0、BOOT1 下拉；晶体负载电容
- **必算项**：
  - 晶体负载电容按晶体 CL 与杂散电容算，起振增益裕量
  - 上电时序留够晶体起振时间
  - 复位期间关键输出（驱动、使能）由外部上下拉定在安全态
  - GPIO 灌拉电流不超手册（指示灯等）
- **落实规则**：G04-010、G04-078、G04-079、G04-082、G04-084
- **已知坑**：
  - 自建符号把未用 GPIO（PC13～15、PA1～3、PA7、PA15、PB4）写成 NC、VBAT/VDDA/VSSA 写成 VDD/VSS；按手册引脚名命名（review:calibration/industrial-io-rs485-can/F02）
  - SR 的电路候选不为 MCU 晶体自动出 CLOCK 候选，要手工 add（review:calibration/industrial-io-rs485-can/M03）
  - 未用 I/O 复位后为浮空输入，固件配置为模拟输入（datasheet:Datasheet/01_微控制器与处理器/32位ARM_Cortex-M_MCU/ST - STM32F103C8.pdf#p28）
- **来源**：
  - raw/Datasheet/01_微控制器与处理器/32位ARM_Cortex-M_MCU/ST - STM32F103C8.pdf（p28 表 5 引脚定义、p52 HSE 特性、p64 I/O 电平、p66 NRST）

