# 机壳单点电容

功能：各现场地与逻辑地分别经高耐压电容单点接机壳，屏蔽层就近接机壳，不跨隔离带。

适用范围：功能绝缘 ≤60 V DC，耐压 1500 Vrms 60 s 的工业板。

电路类型：无（机壳接法不是接口类型；板上有隔离域时隔离本身由 isolated-rs485、di-digital-isolation 等典型电路声明 ISOLATION）

## 实现方案

### 每个地域一颗 1500 Vrms 电容到机壳

- **适用范围**：板上有隔离的现场域（RS-485、DI）和非隔离 24 V 域；机壳/屏蔽要泄放共模浪涌而不破坏隔离
- **核心器件类**：安规或高压瓷介电容
- **必需外围**：24 V 地、RS-485 现场地、DI 现场地各一颗到 CHASSIS；连接器屏蔽针接 CHASSIS
- **必算项**：
  - 电容耐压覆盖隔离耐压试验与工作电压
  - 共模浪涌电荷在各端口 TVS 能承受的范围（限电荷）
  - 隔离两侧的电容不经机壳形成跨隔离带的直接通路
- **落实规则**：无（G04-040 按 ISOLATION 触发，由隔离接口的典型电路落实；本电路声明 ISOLATION 会把隔离器、RS-485 的 18 条准则拉进无隔离板的适用范围）
- **已知坑**：
  - 无隔离的 24 V 板引用本电路时不要声明 ISOLATION，否则审计把隔离器、RS-485 等 18 条无关准则拉进适用范围（user:2026-11-03（Matrix R2 lessons knowledge_wrong））
  - 电容的器件性能要求同时写工作电压与耐压两项，只写耐压会被器件性能核对拒收（test:ASG-calibration/industrial-io-rs485-can#27）
- **来源**：
  - evals/calibration_boards/industrial-io-rs485-can/requirements.md（澄清 C10：功能绝缘、≥1500 Vrms、屏蔽经电容单点接现场地）
  - raw/Datasheet/15_接口与隔离/隔离 RS-485_CAN 收发器/TI - ISOW3080.pdf（p1 隔离耐压）

