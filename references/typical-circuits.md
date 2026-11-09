# 典型电路库

`references/part-roles.md` 回答"这类器件干什么"；本库回答"这个功能通常怎么实现、有几种实现方案、各自的适用条件和已知坑"。
ASG 画不同类型的板子时复用的是这一层，不是具体型号。典型电路文件在 `references/typical-circuits/<功能>.md`，
用 `scripts/find_parts.py --circuits <关键词>` 检索（匹配文件名、标题、功能和实现方案名）。

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
- 必算项（可选）：任务 2.2 的计算线索
- 落实规则（可选）：这种实现方案落实的共用设计准则编号（`references/shared/guideline-criteria.md`，只写 active、按本模式电路类型/器件类别/全板触发、且实现方案正文确实做到了其 asg_action 的；没有写 无，可括注原因）
- 已知坑（可选）：每条引用审查待办（review:<目录>/<编号>）或手册页码；没有来源的坑不写
- 来源：参考设计板名（raw/Designexample/…）或手册路径
```

## 规则

- 每种实现方案必须有来源；没有来源的实现方案不写。"已知坑"每条引用审查待办或手册页。
- 任务 3.1 写分页方案时，`page-plan.json` 每页用 `key_blocks: [块名]` 声明关键功能块（功率变换、保护、隔离、信号链、对外接口），关键块标注所用典型电路与实现方案：
  `"circuits": {"<块名>": "<典型电路文件名>#<实现方案名>"}`；分页方案第一页是架构页，免标。
  没有适用典型电路文件的关键功能块写 `"<块名>": "none"`；检查器按块名（`find_parts.py --circuits <块名>` 同样的检索）检索典型电路，命中的文件名要逐个出现在 `scheme-criteria.json` 该块的候选里并写明为什么不适用（整板评测基线 2026-11-07：Matrix 复位块标为库内没有，`multi-domain-reset` 正适用）。检查器对关键块核对已有文件及实现方案，常规块可不标。显式标注的文件和方案名始终核对。`scheme-criteria.json` 中的块也按关键块核对，名称与页计划一致。
- 任务 1.3 关键功能块对照的规则写进 `record/scheme-criteria.json`，格式固定，报告按它核对；本节是该文件的唯一定义：
  `guideline_scope` 含功率变换、保护、隔离、模拟或对外接口电路类型时必须有这份记录，每个这类类型至少有一块；页计划 `key_blocks` 声明的关键块也必须比较，存在页计划时选定方案须与同名块的 `circuits` 一致。`ports: true` 的块可引用端口矩阵的 G07 全板规则，其余只能引用 `select --typed-only` 选出的规则。这里的结论不代替任务 2.2 的核算，闭环时这些规则仍按原方式引用覆盖。
  每个关键块还写 `decisive: [{condition, value}]`（条件及本板取值）和 `candidates: [{name, source, status, reason, circuit?, unverified?}]`：`source` 是沿用 datasheet/review/test/user 格式的非空来源列表，`status` 为 `selected` 或 `rejected`，`reason` 写选中或淘汰的理由；恰有一个选定方案，`unverified: true` 的候选不能选定。单候选另写 `only_viable` 说明查过哪些资料及只有一种可行的原因。`circuit` 是与页计划 `circuits` 一致的 `文件名#方案名`；省略时以 `name` 与该引用或其方案名精确比较。没有页计划时跳过一致性核对。
  每块写 `block`、`circuit_types`、`device_kinds`、`ports`（有对外端口为 true）和 `criteria`；`criteria` 只列会淘汰某个候选的规则，每项写 `id`、`excludes`（排除的候选）、
  `basis`（`requirement`、`standard`、`datasheet_abs_max` 能硬排除，只来自工程推论的写 `inference`，不作硬排除）、`how`（选定方案怎样满足）、`defer`（留给 2.2 的数值名）；每个 `defer` 名要在任务 2.2 闭合：引用该规则（`guidelines` 含它）的某条计算里有一项带 `value`、`operator`、`limit` 的核对，其 `name` 含这个数值名，或其 `defer` 字段（字符串或列表）写它；否则报未闭合，规则挂在没算这一项的计算上只算形式覆盖（整板评测基线 2026-11-07：校准板“SM712 钳位对收发器总线额定”留给 2.2，CALC-RS485 没算）；
  `standard` 只用于 `nature` 为 `shall`/`should` 的规则（见设计准则库 `references/shared/guideline-criteria.json`）；`method` 是工程方法，`project` 是项目输入，按实际依据写 `requirement` 或 `inference`。
  `datasheet_abs_max` 只指器件手册 Absolute Maximum Ratings 表里的值，推荐工作条件不算。
  没有排除候选的规则不写进 `criteria`，放 `searched`。
  `criteria` 为空时 `searched` 写明查过的范围。以下仅为格式示例，test 来源不代表工程证据：

  ```json
  {"version": 1, "blocks": [{"block": "24 V 现场输出保护", "circuit_types": ["POWER_PROTECTION", "DC_24V"], "device_kinds": ["tvs"],
    "decisive": [{"condition": "现场输出口是否可能反接", "value": "可能，需在开关两态保护"}],
    "candidates": [{"name": "输出钳位并阻断反灌", "source": ["test:格式示例"], "status": "selected", "reason": "满足本板现场输出口保护需求"},
      {"name": "只在输入侧做保护", "source": ["test:格式示例"], "status": "rejected", "reason": "不能覆盖输出口"}],
    "ports": true, "searched": "select --typed-only --ports", "criteria": [{"id": "G07-023", "excludes": "只在输入侧做保护",
    "basis": "standard", "how": "输出口按开、关两种状态各设负向钳位路径", "defer": ["负向残压", "钳位器件脉冲能量"]}]}]}
  ```
- 有可复用的新实现方案、判据或已知坑时按来源补写或修订典型电路，不按篇数虚增。审查证实的问题涉及电路实现方案时，可以补入相应的“已知坑”或“必算项”，并写明来源。
- 典型电路里不写具体型号的参数值；型号的比较在 `selection.json`。
- 新增方案的必算项、已知坑和落实规则不要求填全；已有内容保留，来源要求不变。编号存在与来源格式继续核对。
- 典型电路的电路类型和落实规则只作参考，不联动 `guideline_scope`；准则适用范围只由本板的电路类型和器件类别决定，适用准则仍须按闭环要求引用覆盖。

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
| reviewed-bias-and-latch | 宽范围偏置、掉电反向、交流指示与故障锁定的复核做法 |
