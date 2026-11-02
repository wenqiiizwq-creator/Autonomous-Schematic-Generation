# 功能电路模式库

`references/part-roles.md` 回答"这类器件干什么"；本库回答"这个功能通常怎么实现、有几种做法、各自的适用条件和已知坑"。
ASG 画不同类型的板子时复用的是这一层，不是具体型号。模式文件在 `references/circuit-patterns/<功能>.md`，
用 `scripts/find_parts.py --patterns <关键词>` 检索（匹配文件名、标题、功能和做法名）。

说明：知识库 HardwareWiki 的 wiki 结构（schema.md）没有"电路模式"这种页面类型，所以模式先放在技能里；
要共享给其它技能时整体搬到知识库并改一处路径（`find_parts.py` 的 `PATTERNS_DIR`）。

## 文件格式

```
# <功能标题>
功能：一句话。
适用范围：功率/电压/频率/隔离等级。
电路类型：规则库词表的电路类型名（`references/shared/vocabulary.json`，多个用、分隔；没有对应类型写 无）
## 做法
### <做法名>
- 适用范围：这种做法在什么条件下优于别的做法
- 核心器件类：指向 part-roles.md 的二级类
- 必需外围：没有它电路不工作的元件
- 必算项：任务 2.2 必须做的计算（对应 calculation-preflight 的类型）
- 落实规则：这种做法落实的共用规范规则编号（`references/shared/guideline-rules.md`，只写 active、按本模式电路类型/器件类别/全板触发、且做法正文确实做到了其 asg_action 的；没有写 无，可括注原因）
- 已知坑：每条引用审查待办（review:<目录>/<编号>）或手册页码；没有来源的坑不写
- 来源：参考设计板名（raw/Designexample/…）或手册路径
```

## 规则

- 每种做法必须有来源；没有来源的做法不写。"已知坑"每条引用审查待办或手册页，这是规则 5（知识有来源）的落实。
- 任务 3.1 写分页方案时，`page-plan.json` 每个功能块标注所用模式与做法：
  `"patterns": {"<块名>": "<模式文件名>#<做法名>"}`；分页方案第一页是架构页，免标。
  没有合适模式的功能块，在 `lessons.json` 登记 `knowledge_missing`、`change` 指向将要新增的 `references/circuit-patterns/<功能>.md`，
  设计完成后补写模式文件。`render_design_report.py` 核对：模式文件和做法标题存在，或 lessons.json 里有这条登记。
- 每块新板子至少新增或修订一个模式；审查意见归因为 `knowledge_missing` 且涉及电路做法时，改的就是这里的"已知坑"或"必算项"。
- 模式里不写具体型号的参数值；型号的比较在 `selection.json`。
- 模式→规则映射（2026-11-02，与 SR `catalog.BASIS` 对称）：`scripts/circuit_patterns.py` 读每个模式的电路类型和每种做法的落实规则；
  `tests/test_circuit_patterns.py` 守编号存在、active、不被基线排除、与声明的电路类型相容。分页方案标注了某做法，设计完成核对就要求
  `guideline_scope.circuit_types` 含它声明的类型、它落实的规则按范围适用（否则 `guideline_scope_pattern`），再按普通覆盖要求被引用（`guideline_uncovered`）。
  新增或修订做法时同时改落实规则行；规则只有部分被做法覆盖（如只算了相位裕量没算增益裕量）时不引用，补齐必算项后再加。

## 现有模式

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
