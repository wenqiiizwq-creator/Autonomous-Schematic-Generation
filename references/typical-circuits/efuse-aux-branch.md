# eFuse 保护的常供辅助支路

功能：在主负载开关之前取电，经集成 eFuse（UV/OV 切断、限流、故障后自动重试）给常供辅助降压变换器供电，eFuse 的 PGOOD 使能下游；主路锁定时辅助域与维护网络仍工作。

适用范围：24 V 级直流输入，辅助支路数百毫安～1 A 级；辅助自身故障要求不靠人工自动恢复；下游为宽输入降压变换器（见 internal-comp-buck）。

电路类型：POWER_PROTECTION、POWER_CONVERTER

## 实现方案

### 集成 eFuse（MODE 接地自动重试）+ PGOOD 使能下游 Buck + 局部平钳位 TVS

- **适用范围**：辅助功率小、要求独立于主路的支路保护与自恢复；比外置 MOS 热插拔控制器外围少、集成管短路行为由器件规定；比只靠 Buck 自身 UVLO/限流多了 OV 切断与支路过流隔离
- **核心器件类**：08 热插拔_eFuse（集成 FET，可调 UVLO/OVP/ILIM/dVdT，PGOOD/PGTH，MODE 选重试或锁存）、28 TVS_ESD保护器件（平钳位）、08 DC-DC 降压转换器 (Buck)（下游）
- **必需外围**：UVLO、OVP 分压；PGTH 分压从 OUT 取；dVdT 电容；ILIM 电阻；MODE 接 GND（自动重试）；PGOOD 上拉并接下游 Buck EN；OUT 侧局部 TVS；IN 去耦；UVLO 脚不得悬空
- **必算项**：
  - UV/OV/PG 门限（阈值窗口，两侧都算）：按上升/下降门限上下限与分压容差算各端点；UV 开启上端低于输入窗下限（扣上游压降）；OV 动作下端高于输入窗上限，OV 释放（下降）下端也高于输入窗上限，过压后回到窗内能自动恢复；OV 动作上端低于下游 Buck VIN 推荐最大（降额后）与局部 TVS 击穿下限
  - PG：PG 开启上端低于输入窗下限，最低输入下下游 EN 有效
  - 限流：I(OL) 下限高于辅助最大输入电流（含下游启动）；I(OL) 上限下通路器件不超额定
  - 启动：dVdT 浪涌（下游输入电容取有效值上限）加启动期负载低于 I(OL) 下限
  - 局部 TVS：工作电压不低于支路最高工作电压，钳位低于下游 Buck VIN 绝对最大值
  - 持续短路：限流持续时间、重试间隔与实际布局热阻算平均结温；输入电压、ILIM 设定、输出电容在手册给定的短路条件内
  - 恢复：MODE 接法与料号后缀符合“自动恢复”；过压为截止型，持续过压期间输出中断、回到窗内恢复
- **落实规则**：G03-018、G03-021、G03-022、G05-019、G05-021、G05-022、G05-030、G05-031、G05-036、G05-037、G05-043、G05-044、G05-059、G05-061、G05-092
- **已知坑**：
  - 只核 OV 动作门限不够：早期分压的 OV 释放门限下端低于输入窗上限，过压后在额定窗内可能不再开启；改分压使释放门限下端高于输入窗上限（user:2026-11-03（综合控制板方案设计 §59 辅助恢复窗口修正，R2 CALC-AUX 复核））
  - MODE 接地自动重试时，辅助输出持续短路按限流持续时间与重试间隔算的平均结温约 120 ℃，超过 II 级降额 95 ℃（未超结温上限）；要回到降额内只能把重试交固件或改锁存，代价是维护通路需人工恢复（user:2026-11-03（R2 CALC-AUX 改进项））
  - I(OL) 只在少数几个 R(ILIM) 取值点有保证上下限，中间取值按反比插值属模型值，不是保证值（datasheet:Datasheet/08_电源管理/热插拔_eFuse/TI - TPS2663.pdf#p7）
  - MODE 开路为锁存、接地为自动重试；锁存只能由 SHDN 或 UVLO 低到高、或 IN_SYS 断电复位，接错就与恢复要求相反（datasheet:Datasheet/08_电源管理/热插拔_eFuse/TI - TPS2663.pdf#p28）
  - UVLO 脚不得悬空；前级没有反接阻断时 UVLO 到 IN_SYS 要串手册规定的最小电阻（datasheet:Datasheet/08_电源管理/热插拔_eFuse/TI - TPS2663.pdf#p20）
- **来源**：
  - raw/Datasheet/08_电源管理/热插拔_eFuse/TI - TPS2663.pdf（p6 UVLO/OVP 门限与热阻、p7 I(OL)、p8 PGTH、p9 tCB、tCL_PLIM 与 t(TSD_retry)、p19 PGOOD 使能下游、p20 UVLO 接法、p28 MODE 表）
  - raw/Datasheet/28_保护器件/TVS_ESD保护器件/TI - TVS3300.pdf（p1 8/20 钳位、p5 VRWM、p6 VBR）
  - raw/Datasheet/08_电源管理/DC-DC 降压转换器 (Buck)/TI - LMR60430-Q1.pdf（p5 VIN 推荐与绝对最大）
  - Matrix 综合控制板电源与保护 R2 第 04 页（/Users/skyfend/Project/Matrix网络交换板/方案设计/电源与保护_R2/record/design-closure.json）
