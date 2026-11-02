# USB PD 输出控制

功能：协议协商、输出电压设定、VBUS 开关与保护。

适用范围：Type-C PD 源端充电器/适配器。

电路类型：USB

## 做法

### PD 控制器直驱外部 N-MOS VBUS 开关 + 放电

- **适用范围**：PD 3.x 源端，内置栅极驱动（USBP）和 BLD 放电
- **核心器件类**：08 USB PD 控制器、09 MOSFET（40 V 以上、5x6）、28 TVS、22 电阻
- **必需外围**：VBUS 开关栅极电阻与钳位、VBUS TVS、CC 线 ESD、NTC、生产测试点
- **必算项**：
  - VBUS 开关 VDS ≥ 最高输出 + TVS 钳位电压
  - 短路关断：开关导通期间的能量/SOA（控制器关断延时 × 短路电流）
  - 端口过压动作窗口：不误动作（21 V + 纹波）与保护有效（负载耐压）
  - 放电电阻功耗与放电时间
  - V5/VCONN 供电能力
  - NTC 全温读数与降额映射
  - PPS/AVS 每个设定点的输出电压与限流精度：DAC 端点与中间码误差、检测增益与失调、校准方式，对照 PD 规范允差
- **落实规则**：G02-028、G05-031
- **已知坑**：
  - Q701 的短路关断 SOA 没有算（review:SR-20261019-R3-改版前独立审查-41f4ad3/W-PORT-SOA）
  - 端口过压动作窗口只算一侧（review:SR-20261019-R3-改版前独立审查-41f4ad3/W-PORT-OVP）
  - 默认 5 V 的 V5 与 VCONN 能力没有核（review:SR-20261019-R3-改版前独立审查-41f4ad3/W-V5）
  - NTC 全温读数（review:SR-20261019-R3-改版前独立审查-41f4ad3/W-NTC）、GPIO 角色与保护默认态是固件配置（review:SR-20261019-R3-改版前独立审查-41f4ad3/W-APP）
  - 固件/配置工具是否可得要在选型时核，不是交付时（选型记录 U601）
  - 手册只给 CV DAC 满量程与零码误差，中间设定点的精度没有依据，也没有写校准方案（review:SR-20261023-R5-从头审查-claude-5802e8c/W-U601-CV-ACCURACY）
- **来源**：
  - raw/Datasheet/08_电源管理/USB PD 控制器/Richtek - RT7209.pdf
  - raw/Designexample/USB-PD/NCP1343PD100WGEVB（U6 PD 控制器、Q4）
  - raw/Designexample/USB-PD/TIDA-010047（TPS25750）
