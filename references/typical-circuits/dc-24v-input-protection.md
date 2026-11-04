# 24 V 工业入口保护（保险+压敏+电感+TVS）

功能：正 24 V 直流入口的过流断开与浪涌分级吸收，挡在反接与过压控制器之前。

适用范围：正 24 V 工业直流口，连续 20.4～28.8 V，按长距离线路归类的线-地 ±1 kV、线-线 ±0.5 kV 浪涌；故障电流十安级。

电路类型：DC_24V、POWER_PROTECTION

## 实现方案

### 慢断保险 + 压敏 + 串联电感 + 双向 TVS 分级

- **适用范围**：入口要承受反接（双向器件）、浪涌能量大于单颗 TVS 的 8/20 额定，后级有有源过压切断
- **核心器件类**：28 保险丝（慢断，直流额定）、28 压敏电阻 (MOV)、28 TVS_ESD保护器件（双向，1500 W 级）、21 功率电感
- **必需外围**：保险在最前；MOV 跨线；电感把 MOV 与 TVS 隔开；TVS 在电感后；MOV、TVS 都是双向以承受反接
- **必算项**：
  - 保险：额定电压与直流分断覆盖源故障电流；温度折减后额定电流高于最大输入电流；开机浪涌 I²t 低于熔断积分的降额值
  - TVS 与 MOV 的工作电压高于输入窗上限，且双向器件在反接幅值下不导通
  - 浪涌分流：MOV 残压减 TVS 钳位后经电感的电流，在 TVS 8/20 额定内；MOV 单次能量在额定内
  - TVS 钳位低于后级（控制器输入脚、MOSFET VDS）绝对最大值
  - MOV/TVS 短路失效时保险能断开
- **落实规则**：G01-051、G01-054、G05-030、G05-031、G05-032、G05-033、G05-035、G05-045、G05-046、G05-047、G05-048
- **已知坑**：
  - 库内没有 8/20 µs 额定大于 156 A 的 TVS，残压只能目视外推 MOV 曲线，参数标 model（test:ASG-calibration/industrial-io-rs485-can#12）
  - MOV 残压按 V/I 曲线读，只给典型线（datasheet:Datasheet/28_保护器件/压敏电阻 (MOV)/TDK - SIOV Leaded StandarD.pdf#p3）
  - TVS 的 VRWM 与击穿下限按料号后缀查，SM15T36CA 的 VRM 30.8 V 是双向型的值（datasheet:Datasheet/28_保护器件/TVS_ESD保护器件/ST - SM15T33A.pdf#p3）
- **来源**：
  - raw/Datasheet/28_保护器件/TVS_ESD保护器件/ST - SM15T33A.pdf（p1 IPP、p3 VRM/VBR/VC）
  - raw/Datasheet/28_保护器件/压敏电阻 (MOV)/TDK - SIOV Leaded StandarD.pdf（p3 S14K30 VDC 与冲击电流）
  - raw/Datasheet/28_保护器件/保险丝/Schurter - UMT-H.pdf（p1 直流额定与分断）

