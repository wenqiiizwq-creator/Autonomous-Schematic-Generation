# 典型电路必算项与设计准则缺口处理（2026-11-02）

以 `docs/proposals/typical-circuits-criteria-draft-2026-11-02.json` 的 48 处 `uncertain` 为逐项清单，对照当前共用库 1.4.1（340 条）的 `status`、`asg_action` 与 `applies_when`。结果：已补并引用 37 处、准则侧待办 10 处、不该引用 1 处，合计 48 处；修改 14 个典型电路文件。每处计数按“典型电路 + 实现方案 + 准则编号”，不同实现方案引用同一编号分别计数。

仅扩充必算项及 `落实规则` 后的编号列表，保留标签、既有来源和已知坑。`SKILL.md`、`references/shared/`、`scripts/guideline_criteria.py`、`scripts/stress_check.py` 均不改。新增引用均为 active、未被 industrial_telecom 基线排除，且按文件声明的电路类型、全板或本方案核心器件类别触发；适用文本另行逐项核对。输入草案随提交保留，以便追溯前值。

## 已补并引用（37 处）

| 典型电路 | 实现方案 | 准则编号 | 处理 | 一句理由 |
|---|---|---|---|---|
| [市电输入：整流、浪涌与 EMI](../../references/typical-circuits/ac-input-protection.md) | 保险丝 + NTC + MOV + 共模扼流圈 + 桥式整流 | G05-045 | 补必算项并引用 | 补额定电压、瞬态钳位电压与 AC/DC 类型对照。 |
| [市电输入：整流、浪涌与 EMI](../../references/typical-circuits/ac-input-protection.md) | 保险丝 + NTC + MOV + 共模扼流圈 + 桥式整流 | G05-046 | 补必算项并引用 | 补局部温度折减与电流降额的叠加判据。 |
| [市电输入：整流、浪涌与 EMI](../../references/typical-circuits/ac-input-protection.md) | 保险丝 + NTC + MOV + 共模扼流圈 + 桥式整流 | G05-021 | 补必算项并引用 | 补动作点低端对正常电流及瞬态持续时间的不误动作比较。 |
| [市电输入：整流、浪涌与 EMI](../../references/typical-circuits/ac-input-protection.md) | 保险丝 + NTC + MOV + 共模扼流圈 + 桥式整流 | G05-020 | 补必算项并引用 | 补从源到负载的动作点、时间、恢复方式及耐受协调表。 |
| [市电输入：整流、浪涌与 EMI](../../references/typical-circuits/ac-input-protection.md) | 保险丝 + NTC + MOV + 共模扼流圈 + 桥式整流 | G05-035 | 补必算项并引用 | 补 MOV 短路/灾难性击穿后的清除时间、能量和后果判定。 |
| [市电输入：整流、浪涌与 EMI](../../references/typical-circuits/ac-input-protection.md) | 保险丝 + NTC + MOV + 共模扼流圈 + 桥式整流 | G05-031 | 补必算项并引用 | 补实际浪涌波形及温度下钳位电压对后级绝对最大值。 |
| [市电输入：整流、浪涌与 EMI](../../references/typical-circuits/ac-input-protection.md) | 保险丝 + NTC + MOV + 共模扼流圈 + 桥式整流 | G03-011 | 补必算项并引用 | 补差模等效滤波模型及全频段输入阻抗比判据。 |
| [辅助/偏置电源](../../references/typical-circuits/aux-bias-supply.md) | 辅助绕组整流 + 源极跟随线性预稳压 | G03-034 | 补必算项并引用 | 补带载保证压差与输入纹波谷值的调整区判据。 |
| [辅助绕组过压锁定](../../references/typical-circuits/aux-overvoltage-latch.md) | 齐纳 + 电阻进 FAULT 引脚 | G05-060 | 补必算项并引用 | 适用文本确实覆盖锁存保护，补复位路径、复位时间及持续故障重试检查。 |
| [辅助绕组过压锁定](../../references/typical-circuits/aux-overvoltage-latch.md) | 齐纳 + 电阻进 FAULT 引脚 | G02-005 | 补必算项并引用 | 补装配、老化、接口及负载变化的阈值上下界合成。 |
| [电流检测与校准](../../references/typical-circuits/current-sensing.md) | 低边分流电阻进控制器 CS 引脚 | G02-018 | 补必算项并引用 | 补校准功能、位号、方法与验收限值交生产/测试。 |
| [隔离反馈与隔离信号](../../references/typical-circuits/isolated-feedback.md) | PD 控制器直驱光耦（无外置误差放大器） | G05-006 | 补必算项并引用 | 补反馈链单点失效关键项清单及对应控制措施。 |
| [隔离反馈与隔离信号](../../references/typical-circuits/isolated-feedback.md) | 光耦 + 并联基准（TL431 类） | G03-008 | 补必算项并引用 | 补外接补偿环的 CTR 两端及最坏输入/负载/电容/ESR 相位裕量。 |
| [隔离反馈与隔离信号](../../references/typical-circuits/isolated-feedback.md) | 光耦 + 并联基准（TL431 类） | G03-026 | 补必算项并引用 | 补静态精度加动态跃变偏差对负载允许窗。 |
| [隔离反馈与隔离信号](../../references/typical-circuits/isolated-feedback.md) | 故障/许可信号光耦 | G04-010 | 补必算项并引用 | 补控制器未运行时关键控制输出的默认状态、电平与安全门限。 |
| [隔离反馈与隔离信号](../../references/typical-circuits/isolated-feedback.md) | 故障/许可信号光耦 | G02-003 | 补必算项并引用 | 补驱动参数原表条件及 MIN/TYP/MAX 记录，限用保证工作值。 |
| [NTC 温度检测](../../references/typical-circuits/ntc-temperature-sensing.md) | NTC 分压进 ADC | G04-052 | 补必算项并引用 | 补 ADC、基准和分压前端全链误差与精度预算。 |
| [输出储能与滤波](../../references/typical-circuits/output-filter-storage.md) | 电解/聚合物 + MLCC 并联 | G03-038 | 补必算项并引用 | 补电解直流加纹波峰值对额定及降额耐压。 |
| [输出储能与滤波](../../references/typical-circuits/output-filter-storage.md) | 电解/聚合物 + MLCC 并联 | G03-037 | 补必算项并引用 | 补掉电、反灌及切换场景逐颗电容反压检查。 |
| [USB PD 输出控制](../../references/typical-circuits/pd-output-control.md) | PD 控制器直驱外部 N-MOS VBUS 开关 + 放电 | G01-031 | 补必算项并引用 | 补未连接时 VBUS 电压与端口电容对规范表 4-2。 |
| [USB PD 输出控制](../../references/typical-circuits/pd-output-control.md) | PD 控制器直驱外部 N-MOS VBUS 开关 + 放电 | G02-017 | 补必算项并引用 | 补逐设定点校准后的残差、漂移及失配预算。 |
| [USB PD 输出控制](../../references/typical-circuits/pd-output-control.md) | PD 控制器直驱外部 N-MOS VBUS 开关 + 放电 | G04-010 | 补必算项并引用 | 补控制器未运行时关键控制输出的默认状态、电平与安全门限。 |
| [USB PD 输出控制](../../references/typical-circuits/pd-output-control.md) | PD 控制器直驱外部 N-MOS VBUS 开关 + 放电 | G05-030 | 补必算项并引用 | 补 VRWM 对最高工作电压及 TVS 降额，禁止以 VBR 代替。 |
| [PFC 升压级](../../references/typical-circuits/pfc-boost.md) | CrM/多模 PFC 控制器 + 外置 MOSFET + 升压二极管 | G03-009 | 补必算项并引用 | 补 PFC 最坏组合下增益裕量对 g03_loop_gm_min。 |
| [PFC 升压级](../../references/typical-circuits/pfc-boost.md) | CrM/多模 PFC 控制器 + 外置 MOSFET + 升压二极管 | G03-039 | 补必算项并引用 | 补母线电解合成 RMS 纹波电流及温度/频率修正后的允许值。 |
| [生产测试点与编程焊盘](../../references/typical-circuits/production-test-points.md) | 裸焊盘测试点 | G02-018 | 补必算项并引用 | 补校准功能、位号、方法与验收限值交生产/测试。 |
| [宽范围偏置与故障锁定的复核做法](../../references/typical-circuits/reviewed-bias-and-latch.md) | 辅助整流加高压Buck与纹波注入 | G03-018 | 补必算项并引用 | 补供电谷值扣压降后对 UVLO 开启门限上限。 |
| [宽范围偏置与故障锁定的复核做法](../../references/typical-circuits/reviewed-bias-and-latch.md) | 一次VCC供电的低电流交流指示 | G02-027 | 补必算项并引用 | 补 LED/电阻最坏可实现组合下应力表及额定/降额对照。 |
| [宽范围偏置与故障锁定的复核做法](../../references/typical-circuits/reviewed-bias-and-latch.md) | 比较器经高侧晶体管驱动高有效FAULT | G05-009 | 补必算项并引用 | 补检测、处理和动作总延迟对不可逆损坏时间。 |
| [宽范围偏置与故障锁定的复核做法](../../references/typical-circuits/reviewed-bias-and-latch.md) | 二次辅助经反向保护LDO和串联二极管供SR | G03-031 | 补必算项并引用 | 补多储能与反灌逐场景清单、限值及处置对应。 |
| [二次侧同步整流](../../references/typical-circuits/synchronous-rectification.md) | VDS 检测 SR 控制器 + 低 Rds(on) MOSFET | G03-018 | 补必算项并引用 | 补供电谷值扣压降后对 UVLO 开启门限上限。 |
| [二次侧同步整流](../../references/typical-circuits/synchronous-rectification.md) | VDS 检测 SR 控制器 + 低 Rds(on) MOSFET | G03-033 | 补必算项并引用 | 补输出预偏置时的手册支持或时序调整与反向吸电流检查。 |
| [Type-C 接口与 ESD](../../references/typical-circuits/type-c-port-protection.md) | 16P 受电座 + 单向 TVS 分线保护 | G05-034 | 补必算项并引用 | 补 TVS 漏电功耗/电平误差及结电容带宽预算。 |
| [Type-C 接口与 ESD](../../references/typical-circuits/type-c-port-protection.md) | 16P 受电座 + 单向 TVS 分线保护 | G05-033 | 补必算项并引用 | 补正负电压与误接条件对 TVS 单双向适用性。 |
| [Type-C 接口与 ESD](../../references/typical-circuits/type-c-port-protection.md) | 16P 受电座 + 单向 TVS 分线保护 | G01-028 | 补必算项并引用 | 补 Sink 端 VBUS 输入器件的 24 V 不损坏检查。 |
| [Type-C 接口与 ESD](../../references/typical-circuits/type-c-port-protection.md) | 16P 受电座 + 单向 TVS 分线保护 | G04-006 | 补必算项并引用 | 补逐针可能接触的正负电压对引脚及保护耐受。 |
| [过零/退磁检测](../../references/typical-circuits/zcd-sensing.md) | 辅助绕组分压 + 小信号晶体管钳位 | G02-004 | 补必算项并引用 | 补低电流 hFE 等测试条件匹配、保证定界及估算边界。 |

## 准则侧待办（10 处）

| 典型电路 | 实现方案 | 准则编号 | 处理 | 一句理由 |
|---|---|---|---|---|
| [市电输入：整流、浪涌与 EMI](../../references/typical-circuits/ac-input-protection.md) | 保险丝 + NTC + MOV + 共模扼流圈 + 桥式整流 | G03-017 | 不引用，留待准则明确/放宽 | 适用文本列热插拔/eFuse/负载开关/缓启动/限流 LDO，未含被动 NTC 入口；正文却有“无主动限流”，需准则侧明确是否覆盖。 |
| [辅助绕组过压锁定](../../references/typical-circuits/aux-overvoltage-latch.md) | 齐纳 + 电阻进 FAULT 引脚 | G05-036 | 不引用，留待准则明确/放宽 | 齐纳驱动 FAULT 不属于适用文本限定的热插拔/eFuse/带限流负载开关。 |
| [辅助绕组过压锁定](../../references/typical-circuits/aux-overvoltage-latch.md) | 齐纳 + 电阻进 FAULT 引脚 | G05-037 | 不引用，留待准则明确/放宽 | 辅助绕组过压锁定不属于适用文本限定的热插拔/eFuse/带限流负载开关。 |
| [隔离反馈与隔离信号](../../references/typical-circuits/isolated-feedback.md) | PD 控制器直驱光耦（无外置误差放大器） | G03-009 | 不引用，留待准则明确/放宽 | 本方案明确为控制器内置补偿；准则适用文本仅列补偿网络外接的变换器，需先明确可配置内补偿环路的适用性。 |
| [USB PD 输出控制](../../references/typical-circuits/pd-output-control.md) | PD 控制器直驱外部 N-MOS VBUS 开关 + 放电 | G05-041 | 不引用，留待准则明确/放宽 | 本方案为 PD 控制器关断 VBUS 开关，未声明热插拔或限流器驱动；虽有 MOSFET 触发类别，适用文本仍不覆盖。 |
| [QR 反激主级](../../references/typical-circuits/qr-flyback.md) | QR 控制器 + 外置高压 MOSFET + RCD/TVS 钳位 + 光耦反馈 | G03-007 | 不引用，留待准则明确/放宽 | 现有方案把 CV/CC 补偿交 PD 固件配置，未声明外接补偿网络；准则限外补偿，不由“反激”二字推定适用。 |
| [QR 反激主级](../../references/typical-circuits/qr-flyback.md) | QR 控制器 + 外置高压 MOSFET + RCD/TVS 钳位 + 光耦反馈 | G03-008 | 不引用，留待准则明确/放宽 | 现有 CV/CC 固件补偿不能直接当作外接补偿网络，需先明确该准则对这种闭环实现的适用范围。 |
| [宽范围偏置与故障锁定的复核做法](../../references/typical-circuits/reviewed-bias-and-latch.md) | 一次VCC供电的低电流交流指示 | G05-060 | 不引用，留待准则明确/放宽 | 该处实现方案是 VCC 交流指示，文件只声明 POWER_CONVERTER；G05-060 只命名 POWER_PROTECTION，无全板或器件触发。 |
| [宽范围偏置与故障锁定的复核做法](../../references/typical-circuits/reviewed-bias-and-latch.md) | 比较器经高侧晶体管驱动高有效FAULT | G05-036 | 不引用，留待准则明确/放宽 | 比较器/PNP 驱动 FAULT 不属热插拔/eFuse/带限流负载开关，文件也未声明 POWER_PROTECTION。 |
| [安规跨接（Y 电容）](../../references/typical-circuits/safety-bridging.md) | Y1/Y2 电容跨初次级 | G04-040 | 不引用，留待准则明确/放宽 | 本方案为安规 Y 电容有意跨接，适用文本要求数字隔离器或隔离接口；安规绝缘边界需准则侧明确，不能仅凭 ISOLATION 引用。 |

## 不该引用（1 处）

| 典型电路 | 实现方案 | 准则编号 | 处理 | 一句理由 |
|---|---|---|---|---|
| [输出储能与滤波](../../references/typical-circuits/output-filter-storage.md) | 电解/聚合物 + MLCC 并联 | G03-024 | 不引用 | 现有放电针对 PD 档位切换；本实现方案不负责输入中断等级、恢复再浪涌及系统自动恢复，不能以放电时间替代该判据。 |

## 判断边界

草案中“故障/许可信号光耦不能引用 G04-010”的前提已失效：当前文件声明 POWER_CONVERTER、ISOLATION 两种类型，且本方案确实传送跨隔离控制信号，故补默认状态后引用。草案对辅助过压锁定的 G05-060 也不能套用热插拔限制：该条文本只有“使用锁存型保护时”，因此补复位路径后引用。

仍有三组需准则维护方明确的判断：被动 NTC 的 G03-017（适用文本和“无主动限流”正文边界不一致）；PD 内置/固件补偿与 G03-007/008/009 的“补偿网络外接”边界；安规 Y 电容与 G04-040 的数字隔离接口边界。本轮均保守不新增引用。PD 直驱光耦原有 G03-008 引用也存在同一内补偿适用文本疑点，本轮保留原引用并在此显式提示，未把它当作新增 G03-009 的依据；QR 方案也未为了引用而改成外接补偿架构。

G03-034 用于分立源极跟随预稳压时，压差由带载 VGS、齐纳偏置及调节余量推导；不能套用 VGS(th) 或虚构集成 LDO 的压差保证。G03-033 仅在输出可能预偏置时执行，若无此场景须在实际设计中给出不适用依据。

## 验证

指定五组测试：`python3 -m pytest tests/test_typical_circuits.py tests/test_design_report.py tests/test_find_parts.py tests/test_terminology.py tests/test_ledger.py -q`，103 passed；`python3 scripts/check_ledger.py` 为 PASS；`git diff --check` 通过。运行时将已安装 Poppler 所在 `/opt/homebrew/bin` 加入 PATH，临时文件及 pytest 缓存放 `/tmp/codex-work/asg-criteria-gap/`。另逐项核对 48 处报告处置与解析引用一致、11 个受保护文件哈希未变、必算项及引用段以外的典型电路正文未变。

## 按电路类型统计的前后对比

沿用草案 `_summary` 口径：可引用数为 active、基线允许且 `applies_when.circuit_types` 明确命名该类型的准则去重数；已引用数为声明该类型的文件所有实现方案所引编号与该集合的交集。全板及仅器件触发的准则不进入此表分母；这不是所有实现方案的适用项完成率。前值直接取草案，后值由当前库与典型电路解析结果重算，未改变电路类型声明。

| 电路类型 | 前：可引用准则数 / 已引用数 | 后：可引用准则数 / 已引用数 | 已引用净增 |
|---|---:|---:|---:|
| ANALOG | 17 / 2 | 17 / 2 | +0 |
| ISOLATION | 19 / 0 | 19 / 1 | +1 |
| POWER_CONVERTER | 38 / 8 | 38 / 13 | +5 |
| POWER_PROTECTION | 56 / 1 | 56 / 5 | +4 |
| USB | 17 / 0 | 17 / 4 | +4 |

ANALOG 的 G04-052 原已被电流检测引用，本轮 NTC 新增同编号不会增加该类型去重数；ISOLATION 与 USB 可同时计入 G04-010，各类型数不能相加当成全库唯一准则总数。无类型的生产测试点新增全板 G02-018，不另造电路类型分母。
