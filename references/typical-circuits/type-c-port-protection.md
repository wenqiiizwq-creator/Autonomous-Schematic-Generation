# Type-C 接口与 ESD

功能：连接器脚位与 CC/VBUS/D± 的 ESD/浪涌防护。

适用范围：Type-C 受电/供电端口。

电路类型：USB

## 实现方案

### 16P 受电座 + 单向 TVS 分线保护

- **适用范围**：USB 2.0 Type-C，PD 到 21 V
- **核心器件类**：27 IO连接器(USB-C)、28 TVS_ESD保护器件（CC 线低电容、VBUS 高功率）
- **必需外围**：CC 下拉/上拉由控制器提供；没有控制器的受电口每根 CC 各接一只 5.1 kΩ Rd 到 GND（两根不能共用一只，不能只标 NC 或挂在单节点网络上）；D± 直通或 BC1.2
- **必算项**：
  - TVS 反向关断电压 ≥ 工作电压、钳位电压 ≤ 控制器引脚耐压
  - IEC 61000-4-2 等级与脉冲功率
  - CC 线电容上限
  - TVS 全温最大漏电对静态功耗与 CC 电平误差、结电容对 CC/D± 带宽与时序的影响，对照接口预算
  - 按端口角色逐节点列正常/瞬态负压与误接条件，对照 TVS 单向/双向适用范围；需防负压或误接时改双向并重核钳位
  - 受电端 VBUS 输入器件承受 24 V 不损坏（不限于协商最高电压）；不足时记录风险与处置
  - CC/D± 逐针列可能接触的相邻 VBUS、对端输出与测试设备电压（含正负），算保护后引脚应力与注入电流对照耐受
  - 受电输入电压窗：源端 vSafe5V 4.75–5.5 V（协商电压按 ±0.5 V 有效带）再减线缆压降，下游器件的最低工作电压与最高耐压按此核
  - VBUS 直接电容：未进入 Attached.SNK 时合计不超过 10 µF，协商后不超过 100 µF；超过时在入口加 VBUS 浪涌限流，电容放在限流之后
  - 拔出检测：VBUS 检测分压与放电路径使断开后 40 ms 内降到 3.67 V 以下；电池或他源供电时，检测脚和 D+ 上拉不能被板上电源保持
- **落实规则**：G01-026、G01-028、G01-029、G01-030、G04-006、G05-030、G05-031、G05-032、G05-033、G05-034
- **已知坑**：
  - 信号防护与控制器引脚耐压的配合没有核（review:SR-20261019-R3-改版前独立审查-41f4ad3/W-ESD）
  - 单向 TVS 用了 KiCad 双向符号 Device:D_TVS（R1 审查，`discrete_semantics` 门禁）
  - CC 挂在单节点网络上、没有 Rd，受电口不被识别（review:sr-boards-2026-11-02/rmingon--rs485-spy-injector/S03）
  - VBUS 直接并 5×10 µF，未连接时超过 10 µF（review:sr-boards-2026-11-02/brainsmoke--usb2_hub/F25）
  - 拔出后 VBUS 检测仍为高、片内 USB 上拉由电池保持（review:sr-boards-2026-11-02/anthilla--anthc/F-USBDET、review:sr-boards-2026-11-02/teapotlaboratories--feather-rak3172/F02）
  - 热插拔 VBUS 直达充电器输入，没有按手册做输入过压处置（review:sr-boards-2026-11-02/teapotlaboratories--feather-rak3172/F01）
- **来源**：
  - raw/Datasheet/28_保护器件/TVS_ESD保护器件/
  - raw/Designexample/USB-PD/NCP1343PD100WGEVB（J 与 D）
