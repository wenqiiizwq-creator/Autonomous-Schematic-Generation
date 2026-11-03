# SWD 调试口

功能：MCU 的 SWD 下载调试口，只在逻辑域。

适用范围：3.3 V 逻辑，10 针 1.27 mm Cortex Debug 排针。

电路类型：DEBUG

## 实现方案

### 10 针 Cortex Debug 排针，VTref 接 3.3 V

- **适用范围**：板上只有一个 MCU、调试器自带电平转换；隔离域不经过调试口
- **核心器件类**：连接器（2×5 1.27 mm）
- **必需外围**：VTref 接 MCU 电源；SWDIO、SWCLK、SWO、NRST 直连；多个 GND 针全部接地
- **必算项**：
  - 调试口只接逻辑域，不跨隔离带
  - SWD 脚复位后默认为调试功能，固件复用为 GPIO 时会失去调试
- **落实规则**：无（调试口只用 MCU 默认引脚功能，未落实需计算的接口准则）
- **已知坑**：
  - PA13/PA14 复位后默认是 JTMS/SWDIO、JTCK/SWCLK（datasheet:Datasheet/01_微控制器与处理器/32位ARM_Cortex-M_MCU/ST - STM32F103C8.pdf#p31）
- **来源**：
  - raw/Datasheet/01_微控制器与处理器/32位ARM_Cortex-M_MCU/ST - STM32F103C8.pdf（p31 PA13/PA14 默认功能）

