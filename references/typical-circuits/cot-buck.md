# COT Buck（宽输入同步降压）

功能：宽输入恒定导通时间同步降压，24 V 母线降到 5 V 逻辑电源。

适用范围：输入 4.5～65 V 级，输出 5 V/1 A 级，无外部补偿网络。

电路类型：POWER_CONVERTER

## 实现方案

### COT 同步 Buck + Type 3 纹波注入

- **适用范围**：输出纹波要小、输出电容用 MLCC（ESR 太低）时；比 Type 1/2 不依赖输出电容 ESR
- **核心器件类**：08 DC-DC 降压转换器 (Buck)（COT，内部同步管）、24 功率电感、陶瓷电容
- **必需外围**：RON 定频率；VCC、BST 电容；SS 电容；反馈分压；RA/CA 从 SW 取斜坡、CB 耦合到 FB
- **必算项**：
  - 输出电压上下限按 VREF 与分压电阻容差不利方向取，对照下游供电范围
  - 开关频率与最小导通时间（最高输入下）
  - 电感峰值电流低于限流下限（不误触发）
  - 软启动期间充电电流加负载低于限流下限
  - 输出电容有效值（直流偏压降容）用于动态计算；电解电容纹波电流
  - Type 3 纹波注入：FB 注入斜坡最小幅值（VIN 最低、TON 保证下限、CA 容差上限、分压泄放）对手册最小纹波 25 mV，即 RA·CA ≤ (VIN,min − VOUT)×TON(VIN,min)/25 mV；CB 交流耦合：CB×(RFB2∥RFB1) ≫ 开关周期、CB 为 CA 的 3 倍以上（datasheet:Datasheet/08_电源管理/DC-DC 降压转换器 (Buck)/TI - LM5160.pdf#p16）
  - 结温
- **落实规则**：G03-010、G03-021、G03-039
- **已知坑**：
  - Type 3 纹波注入元件要按手册纹波方程核注入幅值；手册 SNVSA03E 的方程在 8.1.1 Table 3 式 8（p16），只给 RA·CA 上限，不给 CB 取值式，CB 按 TI AN-1481（SNVA166A p8）取积分电容的 3～4 倍。校准板先按参考值取、留了设计待办，后按式 8 核过（datasheet:Datasheet/08_电源管理/DC-DC 降压转换器 (Buck)/TI - LM5160.pdf#p16）
  - 自建符号把散热焊盘写成 PGND，官方引脚名是 EP；连接对，符号引脚名与手册不一致（review:calibration/industrial-io-rs485-can/F03）
- **来源**：
  - raw/Datasheet/08_电源管理/DC-DC 降压转换器 (Buck)/TI - LM5160.pdf（p4 VIN、p6 VREF 与 ILIM、p7 TON 保证范围、p16 Type 3 式 8、p17 纹波方式）

