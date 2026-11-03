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
  没有合适典型电路的功能块，在 `lessons.json` 登记 `knowledge_missing`、`change` 指向将要新增的 `references/typical-circuits/<功能>.md`，
  设计完成后补写典型电路文件。`render_design_report.py` 核对：典型电路文件和实现方案标题存在，或 lessons.json 里有这条登记。
- 每块新板子至少新增或修订一个典型电路；审查意见归因为 `knowledge_missing` 且涉及电路实现方案时，改的就是这里的"已知坑"或"必算项"。
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
