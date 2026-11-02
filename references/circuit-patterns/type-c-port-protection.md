# Type-C 接口与 ESD

功能：连接器脚位与 CC/VBUS/D± 的 ESD/浪涌防护。

适用范围：Type-C 受电/供电端口。

电路类型：USB

## 做法

### 16P 受电座 + 单向 TVS 分线保护

- **适用范围**：USB 2.0 Type-C，PD 到 21 V
- **核心器件类**：27 IO连接器(USB-C)、28 TVS_ESD保护器件（CC 线低电容、VBUS 高功率）
- **必需外围**：CC 下拉/上拉由控制器提供；D± 直通或 BC1.2
- **必算项**：
  - TVS 反向关断电压 ≥ 工作电压、钳位电压 ≤ 控制器引脚耐压
  - IEC 61000-4-2 等级与脉冲功率
  - CC 线电容上限
- **落实规则**：G05-030、G05-031、G05-032
- **已知坑**：
  - 信号防护与控制器引脚耐压的配合没有核（review:SR-20261019-R3-改版前独立审查-41f4ad3/W-ESD）
  - 单向 TVS 用了 KiCad 双向符号 Device:D_TVS（R1 审查，`discrete_semantics` 门禁）
- **来源**：
  - raw/Datasheet/28_保护器件/TVS_ESD保护器件/
  - raw/Designexample/USB-PD/NCP1343PD100WGEVB（J 与 D）
