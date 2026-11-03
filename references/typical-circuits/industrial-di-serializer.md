# 工业 DI 串行器

功能：八路 24 V 数字输入经集成限流与门限的串行器读入，SPI 移位输出。

适用范围：IEC 61131-2 型 1/3 正逻辑吸收电流输入，现场电源 20.4～28.8 V，八路共用现场参考端。

电路类型：INDUSTRIAL_DI

## 实现方案

### 8 路串行化 DI 芯片 + 输入电阻 + 反接二极管 + 每路 TVS

- **适用范围**：通道多、要节省 MCU 引脚与隔离通道；输入类型由芯片内部限流与外部输入电阻决定
- **核心器件类**：15 工业接口(IO-Link_数字IO)（8 路串行器，内置 5 V 稳压）、28 TVS_ESD保护器件（每路）、23 整流二极管（反接）、22 电阻（门限）
- **必需外围**：每路串联反接二极管与输入电阻；RLIM 设限流；V24 去耦与 5VOP 电容；DB0/DB1 选去抖；现场电源反接二极管
- **必算项**：
  - ON/OFF 门限：输入电阻容差与二极管压降下的开关点落在需求的 ON 下界与 OFF 上界之间
  - 输入电流与传感器类型（三线源型）相符
  - TVS 工作电压高于现场电源上限；钳位对芯片输入脚绝对最大值（经输入电阻）
  - 去抖与 SPI 读取时序
- **落实规则**：G01-032、G01-033
- **已知坑**：
  - TVS 钳位（约 48 V）高于输入脚绝对最大值 36 V，要按输入电阻上的压降与内部限流定界；SR 只看同一网，没穿过串联电阻找到 IC 脚（review:calibration/industrial-io-rs485-can/F11）
  - DB1 悬空是手册规定的去抖选择，不是漏接（review:calibration/industrial-io-rs485-can/F13；datasheet:Datasheet/15_接口与隔离/工业接口(IO-Link_数字IO)/TI - SN65HVS883.pdf#p11）
  - 网络名带层次路径斜杠时 SR 认不出 INDUSTRIAL_DI 候选（review:calibration/industrial-io-rs485-can/M02）
  - 现场电源进线 FIELD+ 是否按直流电源口核线-线浪涌要在需求里定（review:calibration/industrial-io-rs485-can/F10）
- **来源**：
  - raw/Datasheet/15_接口与隔离/工业接口(IO-Link_数字IO)/TI - SN65HVS883.pdf（p3 引脚、p11 去抖选择）
  - raw/Datasheet/28_保护器件/TVS_ESD保护器件/ST - SMAJ5.0A.pdf（p1 VRWM、VC）
  - raw/Datasheet/23_分立半导体/整流二极管/Vishay - 1N4007.pdf（p1 VRRM）

