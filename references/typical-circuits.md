# 典型电路库

`references/part-roles.md` 回答"这类器件干什么"；本库回答"这个功能通常怎么实现、有几种实现方案、各自的适用条件和已知坑"。
ASG 画不同类型的板子时复用的是这一层，不是具体型号。典型电路文件在 `references/typical-circuits/<功能>.md`，
用 `scripts/find_parts.py --circuits <关键词>` 检索（匹配文件名、标题、功能和实现方案名）。

说明：知识库 HardwareWiki 的 wiki 结构（schema.md）没有"典型电路"这种页面类型，所以模式先放在技能里；
要共享给其它技能时整体搬到知识库并改一处路径（`find_parts.py` 的 `CIRCUITS_DIR`）。

## 文件格式

```
# <功能标题>
功能：一句话。
适用范围：功率/电压/频率/隔离等级。
电路类型：设计准则库词表的电路类型名（`references/shared/vocabulary.json`，多个用、分隔；没有对应类型写 无）
## 实现方案
### <实现方案名>
- 适用范围：这种实现方案在什么条件下优于别的实现方案
- 核心器件类：指向 part-roles.md 的二级类
- 必需外围：没有它电路不工作的元件
- 必算项：任务 2.2 必须做的计算（对应 calculation-preflight 的类型）
- 落实规则：这种实现方案落实的共用设计准则编号（`references/shared/guideline-criteria.md`，只写 active、按本模式电路类型/器件类别/全板触发、且实现方案正文确实做到了其 asg_action 的；没有写 无，可括注原因）
- 已知坑：每条引用审查待办（review:<目录>/<编号>）或手册页码；没有来源的坑不写
- 来源：参考设计板名（raw/Designexample/…）或手册路径
```

## 规则

- 每种实现方案必须有来源；没有来源的实现方案不写。"已知坑"每条引用审查待办或手册页，这是规则 5（知识有来源）的落实。
- 任务 3.1 写分页方案时，`page-plan.json` 每个功能块标注所用典型电路与实现方案：
  `"circuits": {"<块名>": "<典型电路文件名>#<实现方案名>"}`；分页方案第一页是架构页，免标。
  没有适用典型电路文件的功能块，在 `lessons.json.library_gaps` 登记资料覆盖待办，说明检索与不适用理由、本版设计依据及拟补文件；分页后精确绑定图页和功能块。检查器逐块核对已有文件及实现方案，或该块的有效覆盖待办。覆盖待办不证明缺知识造成了问题，也不代替设计计算和数据手册依据；真实知识缺陷另在 `events` 中按证据归因。
- 每版核对资料覆盖待办；有可复用的新实现方案、判据或已知坑时按来源补写或修订典型电路。确无新增内容时记录核对结果，不按篇数虚增。审查证实的知识缺陷涉及电路实现方案时，补入相应的“已知坑”或“必算项”，并关联事件来源。
- 典型电路里不写具体型号的参数值；型号的比较在 `selection.json`。
- 典型电路→准则映射（2026-11-02，与 SR `catalog.BASIS` 对称）：`scripts/typical_circuits.py` 读每个典型电路的电路类型和每种实现方案的落实规则；
  `tests/test_typical_circuits.py` 守编号存在、active、不被基线排除、与声明的电路类型相容。分页方案标注了某实现方案，设计完成核对就要求
  `guideline_scope.circuit_types` 含它声明的类型、它落实的规则按范围适用（否则 `guideline_scope_circuit`），再按普通覆盖要求被引用（`guideline_uncovered`）。
  新增或修订实现方案时同时改落实规则行；规则只有部分被实现方案覆盖（如只算了相位裕量没算增益裕量）时不引用，补齐必算项后再加。

## 现有典型电路

第一批从 100 W PD（R1–R4）提取：

| 文件 | 功能 |
|---|---|
| ac-input-protection | 市电输入：整流、浪涌与 EMI |
| ac-indicator | 交流/状态指示 |
| pfc-boost | PFC 升压级 |
| qr-flyback | QR 反激主级 |
| zcd-sensing | 过零/退磁检测 |
| safety-bridging | 安规跨接（Y 电容） |
| aux-bias-supply | 辅助/偏置电源 |
| aux-overvoltage-latch | 辅助绕组过压锁定 |
| isolated-feedback | 隔离反馈与隔离信号 |
| synchronous-rectification | 二次侧同步整流 |
| output-filter-storage | 输出储能与滤波 |
| current-sensing | 电流检测与校准 |
| pd-output-control | USB PD 输出控制 |
| type-c-port-protection | Type-C 接口与 ESD |
| ntc-temperature-sensing | NTC 温度检测 |
| production-test-points | 生产测试点与编程焊盘 |

第二批从工业 I/O 校准板（industrial-io-rs485-can，2026-11-02）提取：

| 文件 | 功能 |
|---|---|
| isolated-rs485 | 隔离 RS-485（集成隔离电源收发器） |
| can-with-miswire | 非隔离 CAN（含误接保护端接） |

第三批在工业 I/O 校准板 SR 审查后补写（2026-11-02 收口），已知坑引用审查发现 `review:calibration/industrial-io-rs485-can/<编号>`
（`ASG-calibration/industrial-io-rs485-can/record/sr-review/findings.json`）：

| 文件 | 功能 |
|---|---|
| dc-24v-input-protection | 24 V 工业入口保护（保险+压敏+电感+TVS） |
| ideal-diode-hotswap | 理想二极管 + 过流切断控制器 |
| hold-up | 保持电容与防反灌 |
| cot-buck | COT Buck（宽输入同步降压） |
| ldo | LDO（5 V 转 3.3 V） |
| mcu-min-system | MCU 最小系统 |
| swd-debug | SWD 调试口 |
| industrial-di-serializer | 工业 DI 串行器 |
| di-digital-isolation | 现场组数字隔离 |
| high-side-quad | 四路高边输出 |
| chassis-y-cap | 机壳单点电容 |
| status-led | 状态指示 LED |

第四批从 Matrix 综合控制板电源与保护 R2（2026-11-04）提取，已知坑引用手册页或 R2 设计记录发现（`user:2026-11-03`，括注计算编号）：

| 文件 | 功能 |
|---|---|
| hotswap-latch-powerlimit | 带锁定与功率限的热插拔控制器（外置 N-MOS，开漏管保持 UVLO） |
| efuse-aux-branch | eFuse 保护的常供辅助支路（自动重试 + 下游 Buck） |
| internal-comp-buck | 内补偿峰值电流模式同步 Buck |
| dcs-low-voltage-buck | DCS-Control 低压 Buck |
| ext-comp-current-mode-buck | 外部 Type-II 补偿电流模式同步 Buck（混合电容输出） |
| ovp-cutoff-efuse | 独立过压切断 + 低压 eFuse 输出通道 |
| efuse-bfet-short-latch | 带 B-FET 反向阻断的 eFuse 通道与短路判据锁存 |
| fault-memory-comparator | 比较器 + 触发器的故障记忆与清锁 |
| multi-domain-reset | 多域复位监督与单向开漏组合 |
