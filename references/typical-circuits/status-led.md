# 状态指示 LED

功能：电源指示与 MCU 驱动的运行/故障指示灯。

适用范围：3.3 V 逻辑，LED 电流毫安级。

电路类型：无

## 实现方案

### 电源常亮 LED + MCU GPIO 灌电流驱动两颗 LED

- **适用范围**：只需目视指示；GPIO 能直接带动毫安级 LED
- **核心器件类**：LED、22 电阻
- **必需外围**：每颗 LED 串限流电阻；电源 LED 接 3.3 V，状态 LED 接 GPIO
- **必算项**：
  - LED 电流按电源电压、LED 正向压降上限与电阻下限算，不超 GPIO 灌电流
  - 限流电阻功耗
- **落实规则**：无（常规件指示电路，未落实需单列的准则）
- **已知坑**：
  - GPIO 灌拉 ±8 mA 内保证 VOL ≤0.4 V，PC13～15 只有 ±3 mA（datasheet:Datasheet/01_微控制器与处理器/32位ARM_Cortex-M_MCU/ST - STM32F103C8.pdf#p64）
  - LED 是常规件，库里没有具体型号手册，SR 的物理脚核对会留资料不足（review:calibration/industrial-io-rs485-can/F22）
- **来源**：
  - raw/Datasheet/01_微控制器与处理器/32位ARM_Cortex-M_MCU/ST - STM32F103C8.pdf（p64 I/O 电平与灌拉电流）

