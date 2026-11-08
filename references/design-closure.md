# 从需求到设计完成

适用于需求驱动的新设计和电气改版。原样重画不需要重新做已设计定型的电气设计。
ASG 对其方案、选型、参数和功能实现负责；审查方只提意见，不代替 ASG 完成这些工作。

## 先做设计，再记录结论

1. **需求与架构**：每项当前需求对应可检查的功能路径、实现器件/固件和验收方法。引用历史电路时逐项说明适用条件；评测对比时，同一产品的两版应比较全流程结果，需求变化作为差异解释，不把比较缩成同网表重画。用户已选拓扑不重复投票，仍比较内部实现的成本、损耗、面积和供货证据。
2. **器件可行性**：系列宣传或物理引脚存在，不证明确切型号/固件具备所需状态、配置和启动行为。先验证架构依赖的能力，再展开外围。拿不到资料时评估独立硬件或有证据的替代方案，并继续不受影响的计算和电路；不要仅把设计工作搬到“厂家待提供”。核心/安规相关器件要确切料号与证据；通用料可先给可采购的容差、耐压、功率、温度等边界；定制磁件要受控结构/端子、材料与制造指标。不能把所有空 MPN 一律判错，也不能称其为已完成可下单 BOM。
3. **计算要完整**：损耗/能效预算须列出所有适用的主要项，无法精算的项给有来源的上下界及剩余预算。部分损耗的效率上界只能排除明显不可行方案，不能证明达标。磁件先选候选磁芯/材料/窗口并计算绕组、气隙、磁通和损耗，供应商公差及样机验证另列；不能把自由选择的工程输入无限留待供应商。保护要追触发、供电、执行、保持和恢复整条路径及容差/掉电角点，不止静态分压值。不能为补齐表格编造缺失参数或保证值。
4. **状态和可追溯性**：逐个追启动、正常工作、限流、过温、传感器故障、输出过压、掉电及恢复中适用的状态。写清触发源→判定→执行→供电/保持→恢复，映射实际位号/网络与固件责任。批量给每个需求挂上整板位号不构成功能追溯。
5. **工作分类**：`design` 是还能用现有证据完成的方案/计算/选型/连线；`external` 是确实需厂商或其他输入的能力/保证；`validation` 才是已给出设计依据和试验入口的实物/认证验证。系统级 ESD/EMC/安规试验、实物或材料承认、认证和报价都是 `validation`，不是资料缺口；手册里有的额定（IFSM、I²t、分断能力、SOA）拿来比对是 `design`（R8，2026-10-27）。`pcb` 仅指封装库、布局实现、DFM；它与 `validation` 可交给后续环节。工程假设尚未成立时不因“以后实测”而关闭设计项。审查意见的处理方式与这些阶段的对应见 [处理审查意见](review-comments.md#1-逐条登记)。

## 从审查缺口回到电路

把同一物理问题原因合并，但将可独立执行的动作拆开。例如“偏置设计、固件能力、闭壳热测”不是一个等待厂家任务。
优先处理决定可行性的预算和状态边界；在生成下一版之前，先完成足以改变方案选择的计算。

- 对损耗/裕量不足，计算主导项和剩余预算，比较保持用户要求的具体替代实现。先核决定性的启动、额定、驱动和供电条件，再为候选画外围。被排除的候选记录真正不适用的条件，继续评估可行方向。
- 区分设计自由度、原厂保证条件和后续环节测量。可选阻值、匝数、保持容量、隔离路径和通用料额定由工程先确定；不能只给“待选型”。已知应力可用有来源的保守额定包络关闭，不为每个普通器件索取无关的全温实测。
- 动态保护用电荷/能量、最大传播时间、控制电源谷值和执行元件限值建立可复算边界；不足时更换供电或执行路径。缺厂家软件状态时评估可独立实现的硬件，但不把替代方案的副作用留空。
- 本版写明实际做了什么：改了什么、哪条边界改善、代价是什么、哪些检查受影响，不和上一版比较。仅重跑旧模型、重复标INSUFFICIENT或增加报告不能算设计进展。
- **待办每版重新确认。** 本版交付的待办只列这次设计过程中确认仍需做的事项。上一版的待办不能原样搬过来：
  每一条都按本版的电路、计算和资料重新核过，仍然成立才写进来，并按本版的认识重写内容。编号不要求跨版本一致。
- 还有当前可执行设计动作时继续工作。只有实际依赖尚未取得且替代路径已评估，才报告该分支受阻；同时完成其余分支。PCB阶段才产生的实测可列为后续环节的要求，但决定拓扑、保护有效性、额定和安全间距的设计不得推迟到PCB。
- **先分类，再动图。** 收到审查意见后先按 [处理审查意见](review-comments.md) 逐条登记处理方式：
  电路错误和没做完的设计是设计工作；缺资料的按意见写明的范围补资料；只能靠样机/试验得到的
  能效、EMC、热、寿命、实际寄生写进交给后续环节的要求，不改图。
  补证或计算时发现保守参数下算不过、路径缺失或额定越限，才是需要改图的设计缺口。
- **不用加电路去关闭证据缺口。** “缺全温最大值”“缺实测波形”“只有典型值”不是电路缺陷：先用物理上限（供电轨、钳位、
  限流）或有依据的保守界限定界。不能为了让某条检查有保证值而增加隔离器、锁存、监控、独立辅助电源等新电路，
  除非用保守界限计算证明现电路确实不满足。
  **例外：工作方式本身不在手册规定范围内。** 缺一个保证值，是手册规定了这种用法、只是没给某个参数；
  而手册根本没有对应章节的用法（例如控制器 GPIO 只规定了开路电压和偏置电流档，却拿来灌电流驱动光耦）是设计缺陷，
  不是证据缺口。改用规定范围内的做法（外加小信号管缓冲、规定的电流源档位、参考电路接法）属于设计修正，
  按 SKILL.md 任务 2.1“优先手册规定的工作方式”处理，记录在 `operating_points`。
- **改图前写明代价。** 新增或替换电路前（包括采用审查意见附带的改法），在设计记录里写：预计解决哪些意见、
  新增多少器件和需要新审的状态/规则、新器件自身带来哪些新的证据需求；是否采用按设计判断并写明理由。
  新器件带来的待办按正常设计工作处理，不能以此为理由保留手册未规定的工作方式。

新设计/电气改版在现有设计待办记录增加`convergence_version: 1`；有前置工作时才写`blocked_by`（仅填真实前置工作ID，不含泛泛风险），缺省视为没有。
外部未关闭项增加`fallback_work: [可执行替代设计ID]`；若无可行替代，可省略或写空列表，并以`fallback_evidence: [证据ID]`记录已完成的评估。
外部任务与替代设计不是互相阻塞的循环：替代方案能用公开资料推进，就不应依赖正在替代的那份厂家资料。

`audit_design_closure.py`在原有结论之外返回`convergence`：`CONTINUE_DESIGN`列当前可执行动作，
`WAITING_DEPENDENCIES`列实际前置项，`NO_OPEN_DESIGN_ACTIONS`只表示声明的动作已耗尽，绝不等于电气通过。
未知ID、循环依赖和未评估的外部替代会报错；旧记录明确显示`NOT_ASSESSED`。工作依赖分类本身仍须人工复核，不能通过填虚假前置项制造停工理由。

## 电气角色与图面

在设计网表中可声明 `net_roles: {"VCC": "power", "RTN": "return", "LIMIT": "signal"}`。
新设计至少给 rails 和易混淆的阈值/反馈/检测网络明确角色。比较阈值、参考电压检测点和反馈量一般属于 signal；真正给器件供电的基准轨按用途确定，不用名字猜测。
`page_intents` 保留逐页角色，`Sheet` 和显式 `power()` 均拒绝给已声明 signal 的网络放电源符号。旧设计网表无此字段时兼容运行，表示尚无此项语义保护，不能声称已检查。

分页按完整读者任务决定，不按器件类型机械拆页，也不设每页最少器件数。保护检测→锁定→关断能同页清楚表达时优先同页；确有隔离/拥挤理由拆分时给跨页信号标目的功能和页码。扩大纸张前检查主路径折返、锚点距离、局部扇出；减少页数也不能靠缩字。System_block 将真实层次页与功能、供电、反馈/故障箭头对应，避免重复画一套无法直接对应层次的装饰方框。矩形引脚图适合芯片，但 MOS/比较器等应保留正确功能图形或单元表达，不能牺牲真实 pin map。

图面审阅记录实际追踪路径和未解决问题。零交叉、零碰撞仅是几何自动检查，不能代替上述判断。需求/元件增加时同时比较绝对阅读体验与可对照的相同功能页，不把总线长或纸张面积单独当成质量分数。

## 可执行的结论审计

`design-closure.json` 是设计审查记录的索引，不复制计算预检的数值模型。

只读现行版本：`parameter_version: 3`、`gap_version: 2`、`derating_version: 1`、`uncertainty_version: 1`、
`binding_version: 1`、`matrix_version: 1` 六个都要写。缺一个或版本更旧，审计记 `outdated_record`（FAIL），报告提出问题，
`pack_design.py` 拒绝打包：按本页的现行格式重写记录，不再逐版兼容旧记录（用户 2026-11-08）。

```json
{
  "schema_version": 1, "parameter_version": 3, "gap_version": 2, "derating_version": 1, "uncertainty_version": 1,
  "binding_version": 1, "matrix_version": 1,
  "intent_sha256": "<electrical-intent.json 的 SHA256>",
  "coverage": "complete",
  "evidence": [
    {"id": "E1", "path": "design-basis.md", "sha256": "<SHA256>", "locator": "第2节，R1功能路径和计算"}
  ],
  "requirements": [
    {"id": "R1", "status": "conditional", "implementation": "U1 输出路径；固件故障态尚待证实",
     "refs": ["U1"], "evidence": ["E1"], "depends_on": ["W1"]}
  ],
  "work_items": [
    {"id": "W1", "stage": "external", "status": "open", "requirements": ["R1"], "evidence": ["E1"],
     "consequence_class": "function", "occurrence": "fault", "owner": "厂商", "action": "取得确切固件故障态依据", "fallback": "评估独立关断实现及其供电保持"},
    {"id": "W2", "stage": "design", "status": "open", "requirements": ["R1"], "evidence": [],
     "consequence_class": "function", "occurrence": "fault", "owner": "ASG", "action": "补算故障期间辅助供电保持"}
  ],
  "calculations": [
    {"id": "C1", "requirements": ["R1"], "evidence": ["E1"], "refs": ["D403", "R408", "U402"],
     "kind": "threshold", "coverage": "partial", "conclusion": "conditional", "rests_on": "vendor_data",
     "assumptions": ["辅助绕组漏感尖峰按稳态值的10%计"],
     "omitted_terms": [{"term": "故障期间辅助供电保持", "kind": "not_calculated", "work_item": "W2"}],
     "parameters": [
       {"name": "Vz", "ref": "D403", "value": 30, "unit": "V", "basis": "typical",
        "source": "datasheet:Datasheet/.../Nexperia - BZT52H.pdf#p3", "locator": "表 7，IZ=5mA；200µA 下没有给"},
       {"name": "漏感尖峰比", "value": 0.1, "unit": "1", "basis": "model", "reason": "按稳态值的 10% 计"}],
     "checks": [
       {"name": "21V输出时AUX_DC峰值 对 动作下限(Vz最小+FAULT门限最小)", "side": "no_false_trip",
        "value": 67.6, "operator": "<", "limit": 69.5, "unit": "V"},
       {"name": "动作上限折算的输出电压 对 输出电容额定", "side": "protection",
        "value": 25.1, "operator": "<=", "limit": 35, "unit": "V"}]}
  ]
}
```

- `coverage`：全部适用需求/设计工作均已审查才填 `complete`；抽查或历史回放填 `partial`。这不是工具自动证明的完整性。
- 需求状态 `design_supported` / `conditional` / `open`；`implementation` 描述功能而非只列料号。
- 设计网表声明了 `boundary_nets`（离板网络，见 [requirements-to-intent.md](requirements-to-intent.md)）时，审计核对每条的
  `contract` 文档在交付目录或声明的输入里存在（`boundary_contract_missing`），该网络在文档的表格里有一行
  （`boundary_net_not_in_contract`）；声明本身格式错、网络不存在或重复记 `boundary_schema`。审计结果的 `boundary_nets` 列出声明的网络。
- `clarifications`：问用户的需求问题和答复，给定或采纳的以同编号、`text` 等于答复写进 `requirements`；字段与核对见 [需求澄清](requirement-clarifications.md)。
- `work_items`：阶段 `requirement`（等用户定需求）/ `design` / `external` / `validation` / `pcb`；状态 `open` / `closed` / `handoff`；`validation` 与 `pcb` 允许 `handoff`。未关闭项需 owner/action；`open` 项还需 `consequence_class`（不做的后果：`safety` 安全 / `damage` 器件损坏 / `function` 功能失效 / `margin` 性能余量 / `optimization` 优化）和 `occurrence`（何时出现：`normal` 正常工作 / `condition` 特定工况 / `fault` 仅故障时），等级由审计按规则推出，不手填：安全 P0；器件损坏 P0，仅故障时 P1；功能失效 P1，仅故障时 P2；性能余量 P2，仅故障时 P3；优化 P3。报告按等级排序；写了 `severity` 而与规则不符记 `severity_contradicts_rule`；external 的资料缺口按下面的 `gap_version 2` 写；requirement 只用于用户暂缓的需求：`clarification` 写对应的需求澄清编号，`assumption` 照抄其建议条文，依赖它的计算写进 `calculations`（见 [需求澄清](requirement-clarifications.md)）。closed 与 handoff 均需证据。`pcb` 须声明 `scope` 为 `footprint_library` / `layout_implementation` / `dfm`，并用非空 `electrical_preconditions` 指向已关闭的 design 工作；这些前提须有选定变体、物理引脚号及相关电气边界证据，不能用“已建封装”自证。该分类仍需人工检查，脚本不理解正文电气内容。
- 计算：`coverage` 为 `bounded` / `partial`；`conclusion` 为 `supported` / `conditional` / `failed`。无适用计算时提供 `no_calculations_reason`，不能用空列表绕过。
  - **结论由记录推出**（`parameter_version: 2`）：审计按下表推出结论，写的 `conclusion`/`rests_on` 与推出的不一致记
    `conclusion_not_derived`。报告按三档计数，分“依赖厂家资料的计算”“依赖工程估计的计算”两节列出每条依赖的参数或项。

    | 记录里有 | `conclusion` | `rests_on` | 报告用语 |
    |---|---|---|---|
    | 任一 `checks` 不满足 | `failed` | — | 不满足 |
    | `typical`/`unspecified` 参数，或计算 id 出现在未关闭 external 待办的 `calculations` 里 | `conditional` | `vendor_data` | 依赖厂家资料 |
    | 否则，计算 id 出现在未关闭 requirement 待办（用户暂缓的需求）的 `calculations` 里 | `conditional` | `user_deferred` | 依赖暂缓的需求 |
    | 否则，有 `model` 参数或 `not_calculated` 的遗漏项 | `conditional` | `estimate` | 依赖工程估计 |
    | 都没有 | `supported` | — | 设计成立 |

  - `omitted_terms`：每项 `{term, kind, work_item}`。`not_calculated`（影响检查结果却没算）指向一件未关闭的 `design` 待办，或它等着的未关闭 `external` 待办，
    有它时 `coverage` 是 `partial`，否则是 `bounded`（写错记 `coverage_not_derived`）；`verify_by_test`（只能靠样件或试验确认）
    指向一件 `validation` 阶段的 `handoff` 待办，不影响结论和 `coverage`。指错记 `not_calculated_without_design_item` /
    `verify_by_test_without_validation_handoff`。`missing_guarantee` 不再必填，缺的保证由审计从参数里列出。
  - 需求：挂着不是设计成立的计算时，不能记 `design_supported`（`requirement_status_not_derived`）。
  - **不满足的计算**（R10 ENERGY 三档最好情景都不满足，报告却只在待办里出现；用户 2026-10-28：先改前四条）：
    结果由几项相加（损耗、误差预算）时写 `contributors`（每项 `{name, value, unit}`），报告列最大的几项。
    检查在各项取有利端时算出的写 `scenario: "best"`（另有 `worst`、`nominal`）。最好情景也不满足，等厂家资料关不掉：
    要有一件未关闭的 `design` 待办在 `calculations` 里写这条计算，并在 `redesign` 写改设计的候选（改什么、预计效果），
    缺了记 `best_case_failed_without_redesign`。改设计本身由用户批准后实施，报告这样标注。
  - **工程估计的不确定度**（`uncertainty_version: 1`，与 `parameter_version` 2 或 3 一起；R10：96.9 对 97.6 V、0.297 对 0.3 T
    靠估计过关，余量比估计误差还小；用户 2026-10-28：判风险）：每个 `model` 参数写 `uncertainty`（相对值，0–1，0.1 即 ±10 %，
    缺记 `model_without_uncertainty`）。用到它的检查，余量占门槛的比例小于计算里最大的 `uncertainty` 时（检查可写自己传播后的
    `uncertainty` 代替），合格但有风险：结论照常推出，检查写 `improvement`（加大余量或收紧估计，缺记
    `estimate_margin_risk_without_improvement`），审计在 `estimate_margins` 列出，报告“余量不足以覆盖估计误差”一节逐条列出，
    不挡交付。降额检查的余量对额定算（R12：降额值已是这个量的那一份余量，不再叠加）；门槛为 0 或 `==` 的检查不比。
    检查写 `estimates`（它用到的 `model` 参数名，不依赖估计写 `[]`）时只按这些参数的不确定度比较；既没写 `uncertainty` 也没写 `estimates`
    时取整条计算最大的一个，`estimate_margins` 的 `uncertainty_from` 记 `calculation_max`，报错提示写 `estimates`（工业校准板，2026-11-02）。
  - **`parameter_version: 3`**（新设计；R8，2026-10-27：“20 J 采购资格”“60 V 筛查值”这类自己定的门槛和手册额定、需求指标写法一样，
    成本目标写着“在选型记录中估算”却没算）。在版本 2 之上：
    - 每条 `checks` 写门槛的依据 `limit_basis` 和出处：`requirement`（`limit_source` 写 `req:<需求编号>`）、`guaranteed`/`typical`
      （`limit_source` 写 `datasheet:<库内路径>#p<页>`，门槛数值也按引用核对）、`standard`（`limit_source` 写 `standard:<标准号 条款>`）、
      `derived`（`limit_source` 写手册页或 `calc:<计算 id>`）、`model`（ASG 自己定的筛查值，写 `limit_reason`）。
      缺依据记 `check_limit_without_basis`，出处不对记 `check_limit_without_source`。
      `model` 门槛的 `limit_reason` 要写出这个数（`model_limit_not_in_reason`）；检查名在“对”或“vs”之后写了带本检查单位的数（不是 1 W×0.75 这类算式）时，
      它要等于 `limit`（`check_name_contradicts_limit`；工业校准板：名字写 100 kbit/s，门槛填 200 kbit/s，2026-11-02）。门槛是 `model` 的，结论只能是依赖工程估计；
      门槛是 `typical` 的，结论依赖厂家资料（上表照此推出，原因写“门槛 <检查名>”）。
    - 需求里的数（输入电压范围、空载工况、电流上限、寿命小时数……）作为参数时写 `requirement`，不写成 `model`。
    - 每个 `model` 参数的 `reason` 写它自己的依据（行业常用值、厂家建议、哪段推导）；同一句理由用在 3 个以上参数上，报告列为记录问题。
    - 每条需求至少出现在一条计算的 `requirements` 里，或写 `no_check_reason`（认证范围、取舍优先级这类不对应电路的需求）；
      否则记 `requirement_without_check`。成本需求要有一条物料成本估算：单价按 `model` 写，`reason` 写价格来源和日期；
      估算超过目标，或设计要拿成本换余量时，按[需求澄清](requirement-clarifications.md)停下来问用户。
  - **`derating_version: 1`**（新设计，与 `parameter_version` 2 或 3 一起；用户 2026-10-27）：器件应力按[器件应力规范](shared/stress-spec.md)
    判，降额值取[降额规范](shared/derating-rules.md)中本项目等级那一列，规则数据在 `derating-rules.json`。
    - `derating`：`{level, source}`。`level` 是 `I`/`II`/`III`（缺记 `derating_level_missing`）；`source` 写 `req:<需求编号>`，
      或用户暂缓时 `clarification:<需求澄清编号>`（该澄清的答复是 `DEFERRED`），否则记 `derating_level_without_source`。
    - **查到什么程度**：只审写出来的应力（用户 2026-10-27：每颗器件都有降额规则过于严苛，统一到余量审核规则上来），
      不要求每颗器件、每条规则都有一条检查。一条检查写了 `ref` 和 `rating`（拿应力与额定比）却没写 `derating_rule`，
      而降额规范有这类器件的规则时，审计在 `derating.hints` 里出提示 `derating_rule_available`，不记错。
      例外（stress-spec.md，2026-10-28 起）：门槛是保证额定（`limit_basis: guaranteed`，`<=`/`<`），而降额规范对这类器件、
      这个量（按 `unit` 分电流、电压、功率）只有一条 `ratio` 规则适用时（同类几条的按型号/值/符号区分 USB 母座、器具耦合器，
      都不像的取“其他”那条），审计按本级重算降额值；应力超过降额值的与点名规则的一样列入 `derating.stress_risks`、要求写
      `improvement`。
      常规件不逐颗核对，规格写出的最低额定 = 最坏应力 ÷ 本级降额系数。
    - **电阻写额定功率**（用户 2026-10-27：设计时考虑功耗，除阻值和精度外还要写上功率等级，作为给以后的约束；与 schematic-review
      的无源应力预判同一判据）：电阻的最坏功耗 V²/R_min（R_min 取公差下限，未写公差按 ±5 %）超过按已写字段能买到的最弱件的降额值
      ——封装最弱档（[commodity-floors.json](shared/commodity-floors.json) 的片式电阻，没写封装按 0402）× 本级 RES-SMD-P 取值（[derating-rules.json](shared/derating-rules.json)；等级未定按设计准则库工程取值 `unset_level`，即 I 级）——时，功耗要考虑：
      写一条 `ref` 为该电阻、`unit` 为 `W` 或 `mW` 的功耗检查，并在设计网表的 `value` 写成 `阻值/公差/额定功率[/额定电压][/封装]`
      （如 `620/1%/0.125W`；或写在一个只含功率的字段里），额定功率取 ≥ 最坏功耗 ÷ 本级 RES-SMD-P 取值的标准档。
      写了功耗检查而没写额定功率的，审计记 `resistor_power_rating_missing`（给出最低额定）。功耗不要考虑的电阻不用写额定功率。
      审计只看得到写成检查的功耗：接在电源轨上或两端电压高的电阻，设计时都要算最坏功耗，不能靠不写检查躲过。
    - 降额检查是 `checks` 里的一项，另写 `derating_rule`（规则编号）、`ref`（位号）、`rating`（最坏温度下的保证额定）与
      `rating_source`（`datasheet:<库内路径>#p<页>`，或 `req:`、`calc:`）；`limit_basis` 写 `standard`，`limit_source` 写
      `standard:derating-rules#<规则编号>`（`derating_limit_source`）。`limit` 由规则推出：`ratio`/`pulse_ratio`/`min_ratio` 为
      额定 × 取值（额定为负时，如关断负栅压，按幅值：允许幅值 = |额定| × 取值，审计比较 |value| 与 |limit|，R8），
      `margin_c` 为额定最高温度 − 取值，`tj_percent` 为 (Tjmax − 25) × 取值 + 25，`max_c` 等为取值本身；
      写错记 `derating_limit_mismatch`，这几种判据缺 `rating` 记 `derating_rating_missing`。规则编号不存在记 `derating_rule_unknown`，
      规则的器件类型与位号不符记 `derating_rule_kind`。
    - **结论**：超过额定为 `failed`；在额定内但超过降额值为合格但有风险（应力）：计算照常推出结论（不因此 `conditional`），
      检查写 `improvement`（换额定更高的件或降低应力，缺记 `stress_risk_without_improvement`），一般不挂待办，也不要用户签认；
      审计在 `derating.stress_risks` 列出每一处，报告的“应力风险”一节逐条列出，不挡交付。降额值以内是普通的满足。
    - **应力超幅**（Matrix R2，2026-11-04：LM70880 估算结温 146 ℃，II 级降额值 95 ℃、额定 150 ℃，只报“合格但有风险”）：
      应力风险（点名规则的，或按唯一适用规则重算的）满足下面任一条时不只是降额偏离，检查另写 `work_item`，指向一件未关闭的
      `design`（`open`）或 `validation`（`open`/`handoff`）待办，该待办写 `consequence_class`/`occurrence`，推出的等级不低于要求：
      - 项目等级比最宽一级（III）严，且应力超过 III 级的降额值（降额规范任何一级都不允许）——至少 P2；
      - 离额定的余量小于估算所需的余量——P1。温度类判据（`max_c`、`tj_percent`、`margin_c`，`rating` 为最高结温）取共用层
        G02 工程取值 `est_junction_margin`（20 ℃，凭估算判器件损坏所需的结温余量）；其他应力取该检查的 `uncertainty`
        （相对额定），没写不按余量判。
      阈值都取共用层（降额表的等级取值、G02 工程取值），脚本不另设数。缺 `work_item` 记 `severe_stress_without_work_item`，
      待办阶段/状态不对记 `severe_stress_work_item_not_open`，等级不够记 `severe_stress_work_item_severity`。审计在该条
      `stress_risks` 里加 `required_severity`、`loosest_limit`、`margin_to_rating`，`derating.severe_thresholds` 写所用阈值；
      报告“应力风险”一节写明阈值并列出每处要求的等级和待办。项目等级就是 III 级时只按余量判。
      应力超幅是[器件应力规范](shared/stress-spec.md)判定表中的一档，这里是它在 ASG 设计记录里的写法。
  - **`guideline_version: 1`**（用户 2026-10-31：请开始执行这个方案）：共用设计准则（G01–G09，见[共用设计准则库](shared/guideline-criteria.md)）。
    `guideline_scope` 写 `library_version`（已装设计准则库的版本）、`baseline`（默认 `industrial_telecom`，需求写明时 `aerospace`/`military`）、
    `circuit_types` 与 `device_kinds`（取设计准则库词表：本设计有的功能电路类型和器件类别）、`not_applicable: [{id, reason}]`。
    计算、待办、`record/component-requirements.json` 的性能记录和 `evidence` 条目可写 `guidelines`（设计准则编号列表）。
    只有能淘汰候选方案（任务 1.3 的 `scheme-criteria.json`）、改变选型（性能记录）或进入计算（计算）的准则逐条落实，其余按设计动作照做，
    不要求逐条引用（用户 2026-11-08 按草案实施）。审计按范围选出适用准则，在 `guidelines` 列出适用（`applicable`）、已引用（`covered`）、
    不适用（`not_applicable`）、没引用（`uncited`）和下游规则，供审查对照；没引用的不报待办，不挡打包。
    写了的引用照样核：已关闭的待办引用准则时，`guideline_evidence` 逐条写
    `<证据编号>#<节/表/行>`（证据编号在这件待办的 `evidence` 里），缺记 `guideline_work_without_evidence`，同一处顶 3 条以上准则记
    `guideline_evidence_repeated`（工业校准板：一件已关闭的文档待办批量引用了 205 条，2026-11-02）；引用库里没有的编号记 `guideline_unknown`，引用不适用的规则记 `guideline_cited_not_applicable`
    （补范围或去掉引用）；引用了的、关闭阶段在原理图之后的规则要有待办（`handoff` 类也可以是一条交接表证据），缺了记 `guideline_downstream_without_work_item`。范围写错记 `guideline_scope`。
    有对外连接器的板必须写 FMEA 和 EMC 端口矩阵（[必写的设计文档](guideline-evidence-groups.md)）：证据条目写 `carrier: FMEA`/`carrier: EMC`，审计核必备章节齐全、非空、
    每个连接器位号都写到；没登记或不齐记 `design_document_incomplete`（INCOMPLETE，打包被拒），`carrier` 写了别的名字记 `guideline_carrier_unknown`。
    审计在 `guidelines.documents` 列出两份文档的核对结果。
    设计准则库有规则而记录没有 `guideline_version` 时记 `guideline_scope_missing`；设计准则库为空时不核对。
    [典型电路库](typical-circuits.md) 的电路类型和可选落实规则只作方案比较参考，不扩展或约束 `guideline_scope`；本板的功能电路类型和器件类别决定准则适用范围，普通引用覆盖要求不变。
  - **占位值**（不分记录版本，2026-11-02，86 块开源板 DOC-D01/DEV-D01/DOC-Q01）：设计网表的值是库默认名或占位
    （`R`、`R_Small`、`C`、`Crystal_GND24` 等 `Device:` 库符号名，`-`、`?`、`xx`、`TBD`），或料号/型号含通配符（`BZT52Bxx`、`BQ769x2` 里的小写 x、`?`、`*`），
    记 `placeholder_value`；位号带 `?` 记 `unannotated_reference`。值写设计值，料号写手册订货信息里的完整订货码。
  - **工况输入的来源**（`parameter_version` 2、3 的记录都核，不另设版本；用户 2026-11-04：Matrix R2 的 CALC-CH-START 把 1 A 启动负载写死在脚本和参数名里，
    没人给过这个数，换成需求的单路 1.5 A 结论就反了）。工况是板子外面定的量：负载、源阻抗、环境温度、输入电压窗、外部瞬态、线缆。词表与判法在 `scripts/operating_inputs.py`。
    - **`input_role`**：计算参数写 `input_role`（`startup_load`、`load_capacitance`、`load_demand`、`source_impedance`、`input_window`、`ambient_temperature`、
      `external_transient`、`cable_topology`）就声明它是工况，审计核来源，没有来源记 `operating_input_without_source`。接受的来源：
      - `requirement`（`req:<编号>`，用户答复写回的需求同样引 `req:<澄清编号>`），需求文字要写出这个数和单位：同一量纲才换算前缀（1500 µF 对 1.5 mF 算写明，对 1.5 A 不算），范围下端取上端的单位（20.4～28.8 V）；没有单位的参数（比值、个数）只比数。换算出来的写 `derived` 和 `formula`；
      - `guaranteed`、`typical` 引手册页（负载器件的手册）；
      - `derived`：`source` 指向声明了它的另一条计算，或写 `formula`，算式用到的参数自己有来源；
      - `model`、`design_choice`、`unspecified` 只有两种情况：负载在本板上，写 `load_refs`（位号，不能是开关自身或连接器）；或用户暂缓，写 `clarification: <澄清编号>`，
        答复是 `DEFERRED`，有未关闭的 `requirement` 待办在 `calculations` 里列这条计算。
    - **启动计算**：引用 G03-017 的计算，以及位号含 eFuse、热插拔、负载开关，且有启动类检查（检查名含启动、合闸、软启、缓启、预充、dV/dt，单位是电流、功率、能量或时间；
      8/20 µs 这类脉冲不算）的计算。这种计算：
      - 要有 `input_role: startup_load` 的参数（阻性/恒流/恒功率的值；后级 UVLO 开启前没有负载的，写 0 并引后级手册的 UVLO 页），否则 `startup_load_undeclared`。
        需求没给，取值又会改变选型或取值时，按[需求澄清](requirement-clarifications.md)问用户，不自定。别的计算已声明的，写 `derived`、`source: calc:<那条计算>`；
      - 名字像负载电容的参数（`model`/`design_choice`/`requirement`）同样核来源，否则 `operating_input_without_source`；
      - 浪涌检查（检查名含启动浪涌、合闸浪涌、浪涌电流、启动电流、充电电流，单位是电流）的值要是本计算的一个参数（`startup_surge_unbound`），该参数写 `formula`
        （`startup_surge_without_formula`），算式用到声明的负载（`startup_surge_ignores_load`；负载为 0 不要求）。
    - **`formula`**：`{"expr": "C*S*1e-3+I", "vars": {"C": "<参数名>", "S": "<参数名>", "I": "<参数名>"}}`，只能用四则、乘方和 sqrt、log、exp、abs、min、max。任何参数写了都复算：
      结果差 0.1 % 以上记 `formula_mismatch`；算式里写死的数记 `formula_hidden_literal`（只允许单位换算的 10 的幂、½CV² 这类 0.5/2/3/4 的系数、指数、1+R1/R2 的 1）；写法不对记 `formula_schema`。
      不要求给所有 `derived` 写算式，只有上面的浪涌参数必须写。
    - **名字里加的数**：`derived` 参数的名字、`derivation` 和检查名里写的“上限 + 1 A”“VBR＋1 V”，这个数不是本计算任何参数的值时记 `hidden_literal_in_name`
      （任何计算都查）。“+5V 轨”“共模 +7 V”是符号，不算。
    - **核对清单**（`operating_inputs.checklist`，不挡交付，报告“工况输入来源”一节列出）：
      按关键词把引用准则的 `inputs` 文字归到上面的类别，不逐条维护；列每类工况的适用准则数、需求里有没有提到、引用这些准则却没写它的计算；名字像工况、由 ASG 自定、没写 `input_role` 的参数；
      没有启动计算的 eFuse、热插拔或负载开关。脚本判不了这些是否真缺：一条计算只落实准则的一部分时，没写它不算错。
    - **有多个候选值时取不利值，理由写进参数**（`reason`）：一条需求同时写了“单路最大 1.5 A”和“预算各路 1 A”，启动计算取 1.5 A。
      审计查不出取错：声明 1 A 也通过，只在核对清单 `multiple_candidates` 和报告里列出需求写的其他值和理由，由人看。
    - **查不到的**：有来源不等于取对了，同上。
      没写成计算的工况、按比例藏在系数里的量（×1.2）只有声明后才查。
  - **`binding_version: 1`**（新设计；用户 2026-11-02：把这86块板子上找到的问题……进行改进）：料号、手册、符号脚、未用脚和电源轨电压绑在一起核。
    - 值为空也记 `placeholder_value`（机械件、测试点、连接器除外）。
    - 值像型号（字母加数字）时，值与 `mpn` 要一个是另一个的前段，否则 `part_value_contradicts_mpn`（LM5163DDA 对 LM5164DDA）；
      晶体的值与料号都写出频率时要相同，否则 `crystal_frequency_contradicts_mpn`（16 MHz 对 ABM8-24.000MHZ）。
    - 关键/特殊器件的 `datasheet` 要是这个料号的手册：文件名（`厂商 - 型号.pdf`，型号里的小写 x 当任一字符，`_` 分隔多个型号）是料号的前段，
      或手册正文里有这个料号；都不是记 `part_datasheet_contradicts_mpn`（TCR2EF33 挂 AP2112 手册）。手册找不到或读不出文字时不判，由选型身份检查报。
    - `record/reference-input.json` 的每个引脚表：来源文件与设计网表该器件的 `datasheet` 是同一份手册（`pin_map_datasheet_mismatch`）；
      每个脚写 `datasheet_type`（照手册引脚表：`I`/`O`/`IO`/`OD`/`OS`/`PWR`/`PWR_OUT`/`GND`/`A`/`NC`，缺记 `pin_map_without_datasheet_type`），
      `types` 只能取与它相符的 KiCad 类型（`O`→output/tri_state，`OD`→open_collector，`PWR`→power_in……），否则 `pin_type_contradicts_datasheet`。
      TI 的 `P` 不分输入输出：功能栏写明是器件输出的电源、开关、自举节点按 `PWR_OUT` 记，不为避开 ERC 改记 `PWR`；
      同网的几个这样的脚画成一个叠脚 `[a,b]`（[符号与外围电路要求](symbol-and-peripheral-contracts.md)），引脚表仍逐物理脚写。
      手册类型码的读法（TI 的 `P` 按 `PWR_OUT` 记等）写在该脚可选的 `type_note`（非空文字，空记 `schema`），只作说明，不放过类型不符。
      `scripts/fill_pin_maps.py` 从手册引脚表批量填这两项并列出填不上的脚（用法见 [符号与外围电路要求](symbol-and-peripheral-contracts.md)）。
      没有 `reference-input.json` 记待办 `reference_input_missing`。
    - **未用脚处置**（`pin_dispositions`）：连接器、测试点、机械件以外，每个 `no_connect` 脚写一行
      `{pin, disposition, net?, note?, source, locator}`：`disposition` 取 `open`（手册允许悬空，脚在 `no_connect`）、`tie_low`/`tie_high`
      （脚直接接 `net`）、`pull_down`/`pull_up`（脚所在网络上有电阻）、`per_datasheet`（其他手册规定的接法，写 `note`）；
      `source` 是手册里规定这个脚未用时怎么处理的页（`datasheet:<库内路径>#p<页>`，按手册引用核对）。缺行记 `no_connect_without_disposition`，
      接法与设计网表不符记 `disposition_contradicts_netlist`，没写手册页记 `disposition_without_source`。只接一个脚的网络记 `single_endpoint_net`
      （Type-C 的 CC 挂在单节点网络上、没有 Rd）。接了网络的未用脚（接地、上下拉）也可以写一行，审计同样核接法。
    - **电源轨最高电压**（`net_voltages`）：设计网表 `net_roles` 里每个 `power` 网络写 `{net, max, unit: "V", source}`，`max` 是最坏最高电压
      （含容差、纹波和需求给的输入上限），`source` 写 `req:<需求编号>`、`calc:<计算编号>` 或 `datasheet:<库内路径>#p<页>`；缺记 `net_voltage_missing`，
      来源不对记 `net_voltage_without_source`。一端在回流网络（`net_roles` 为 `return`，或名字是 GND/VSS/RTN 类）、另一端在写了最高电压的网络上的电容，
      额定电压（性能记录的 `working_voltage`/`rated_voltage` 下限，或值/规格字段里写的电压）低于它记 `capacitor_rating_below_net_voltage`；
      TVS 的 VRWM（性能记录的 `working_voltage` 下限，或按 VRWM 命名的系列 SMAJ/SMBJ/SMCJ/SMDJ/SMLJ/SMF、PESD/PTVS<a>V<b> 从型号读出）
      低于它记 `tvs_vrwm_below_net_voltage`。降额比较仍按 `derating_version` 写在计算里；这里只拦额定低于工作电压的错。
    - 审计在 `binding` 列出各网络最高电压和处置行数。
  - **`matrix_version: 1`：对全部对象核对的矩阵与保护逻辑状态表**（整板评测基线 2026-11-07：6 个漏项里 3 个是同一条判据
    只核了一个对象——复位门限只对 MCU 的 2.0 V 核、没对 YT9218 的 3.135 V；−45 ℃ 存储只写“由器件额定覆盖”；防反接只看功率路径、
    没看低边 MOS 断开地回路；另 1 个是软件正常关断时“PG 先于 FLT 失效”的固件判据会不会误置锁没有列）。
    行和格由 `scripts/object_matrices.py` 从设计网表列出，设计者不挑对象，只逐格写结论：
    `python3 <skill>/scripts/object_matrices.py skeleton --intent electrical-intent.json --closure design-closure.json --out matrices.json`
    输出全部行和格（已写的结论原样保留），每格的 `candidates` 列出名字点到这个对象、又核这条判据的现有检查，只作提示，
    不是结论。把 `matrix_version: 1` 与 `matrices` 写进 `design-closure.json`。四张表：
    - `supervised_rails`：电压监控/复位器件（库目录“Supervisor/电压监控”、TPS38xx、MAX8xx 等系列，或 `ComponentRole: supervisor`）接到的每条
      `power` 轨，连同经 `filtered_supply` 从它派生的轨，× 轨上每颗 IC/光耦负载：`{rail, cells: [{ref, calc, check}]}`。
      检查名要有门限类的词（门限、阈值、复位、欠压、UV、BOR……），否则 `matrix_check_not_about_criterion`：稳压精度“+3V3 下限 对 YT9218 3.135 V”
      不顶“复位门限 对 YT9218”。热插拔欠压门限这类别的监督可以自己加一行 `rail`，同样逐格核。
    - `temperature`：表头 `operating`、`storage` 各写 `{min, max, source}`，`source` 是 `req:<需求编号>`（需求文字要写出这个范围，
      如“−45～+70 ℃”）或 `clarification:<编号>`；`rows` 每行 `{refs, operating, storage}`，每颗器件（测试点、机械件除外）正好在一行。
      温度写 `{min, max, source}`：`source` 引手册页（`datasheet:<库内路径>#p<页>`，按手册引用核对），或写 `spec` 表示这个范围已写进
      每颗器件的规格（设计网表 `Specification`/值字段要写出不窄于它的“−55～+125 ℃”，否则 `matrix_temperature_not_in_spec`）。
      骨架给关键/特殊器件各一行、常规件按类型一行，可以再拆。器件范围不覆盖需求范围是 `matrix_cell_failed`。
    - `port_stress`：每个连接器一行。`stresses: [{id, kind, source}]`（`kind` 取 surge、esd、eft、reverse_polarity、overvoltage、short、
      miswire、hot_plug；`source` 写需求或标准），或 `no_stress_reason`（箱内、板上调试座）。格是应力 × 路径上每颗器件：端口网络上的，
      以及经保险丝、检流电阻、磁珠、电感这类串联两端器件最多三跳到的（不走进回流网络和 25 脚以上的主电源轨；电阻、磁珠、电感本身的应力由功耗和降额检查管，不进格）：
      `cells: [{stress, ref, calc, check}]`，检查名要有这类应力的词（钳位、浪涌、反接……）并点名器件。
      端口的回流网络只经开关器件（MOS、二极管、继电器；隔离器不算）接到另一回流网络时，那一侧的其他每个端口是一格
      `return_paths: [{via, port, calc, check}]`：回线被断开（低边防反接 MOS 关断）时电流是否改经这些端口的地回流，检查名要有
      地回路、回流、反接等词并点名那个端口。
    - `protection_states`：有 eFuse/热插拔/负载开关、电压监控器件，或 IC/晶体管接到故障/关断/复位网络（FLT、FAULT、LATCH、SHDN、RST、RESET……）
      的功能块（`fields.Circuit`）。`latch` 写 `hardware`、`firmware` 或 `none`；`rows` 是上电、正常开、正常关、短路、复位
      （`power_up`、`normal_on`、`normal_off`、`short`、`reset`）× 锁清除/置位（`clear`、`set`；`none` 只一列），每行
      `{state, latch, outcome, ...结论}`：`outcome` 写各输出与锁在这一状态怎样变化（缺了不算结论，记 `matrix_state_without_outcome`），
      结论引用计算检查，或 `evidence: "<证据编号>#<节/表/行>"` 加 `verdict: ok|fail`。另有的状态可以多写行。
    - 每格的结论只有三种：`calc` + `check`（结论由检查推出，降额偏离仍算满足；检查名或检查的 `ref`/`objects` 要点名这个对象，
      位号、值、料号或其前段都算，否则 `matrix_check_not_about_object`）、温度格的手册数值、`verdict: not_applicable` 加 `reason`。
      写了 `verdict` 又与检查推出的不同记 `matrix_verdict_contradicts_check`；检查或证据不存在记 `matrix_check_unknown` / `matrix_evidence_unknown`；
      对象不在矩阵里记 `matrix_unknown_object`。缺结论记 `matrix_cell_missing`、结论不满足记 `matrix_cell_failed`，两者都使审计为
      INCOMPLETE（设计没做完），审计的 `matrices` 按表列出格数、有结论数和缺的、不满足的格。
    - 工具只列对象，不判对象选得对不对：监控器件、端口路径和状态块按网表规则认，漏认的可以自己加行；格的结论对不对仍要人看。
  - `refs`：这条计算决定了哪些位号的取值，非空，且都在设计网表里。
  - `checks`：非空列表，每项是一个算出来的值和它必须满足的门槛 `{name, value, operator(<=,<,>=,>), limit, unit}`。
    核对两处数据一致的检查（寿命剖面的每日能量等于需求给的剖面、两份记录里的同一个数）写 `operator: "=="`，不写成 `≤`/`≥`：不相等就是不满足（R8 C-LIFE 写成“218 ≤ 218 Wh”）。
    **结论由数字决定**：任一项不满足，`conclusion` 只能是 `failed`；全部满足才可以是 `conditional`/`supported`。
    不能在脚本里给所有计算统一写 `conditional`，也不能只写公式和假设不给门槛——没有门槛的计算什么也没证明。
  - **阈值窗口**：保护、检测、钳位类计算填 `"kind": "threshold"`，`checks` 必须两侧都有：
    `side: "no_false_trip"`（正常工作最高点，含纹波、漏感尖峰、温漂和容差，低于动作下限）和
    `side: "protection"`（动作上限仍低于被保护对象的耐受值或需求的保护点）。只算一侧会漏掉误动作或保护无效。
  - 设计网表里的稳压管、TVS、基准源都必须出现在某条计算的 `refs` 里：按 lib_id（含 Zener/TVS/TL431/LM4040/Ref 等）、
    value 或 mpn 的系列前缀（1N47、BZX、SMBJ、PESD、TLV431、LM385 等）识别，通用符号画的其他阈值器件在 `fields.ComponentRole` 写 `threshold`；
    否则审计报 `threshold_part_uncalculated`。设计资料里写的阈值（如“对应30V包络”）必须与这条计算的数字一致。
- **参数来源**（`"parameter_version": 3`）：
  每条计算加非空 `parameters`，每项 `{name, value, unit, basis, ref, source, locator}`。`basis` 取：
  - `guaranteed`：手册保证的 MIN/MAX；`typical`：手册典型值。两者都要 `ref`（位号）和 `source`
    `datasheet:<库内路径>#p<页>` 加 `locator`（表名/参数符号/条件）。
  - 手册引用的核对（`schematic_layout/citations.py`，参数、工作点、缺口里的 `datasheet:` 都核）：文件不在知识库
    （`HARDWARE_WIKI/raw`）或声明的资料里、页码超出文档页数，记 `citation_wrong`，审计 FAIL；写成本机绝对路径
    （`/Users/…/原厂资料/X.pdf`）的记 `citation_not_in_library`：引用写知识库里的路径，不写本机副本的位置（R8）。`guaranteed`/`typical`
    的数值在所引页的文字里找不到（含 SI 前缀换算、百分数、尾随 0、Unicode 负号）时列入报告“引用待人工核对”，不拦。
    `locator` 文字不核。找不到知识库或没有 poppler（`pdfinfo`/`pdftotext`）时记为“没核对”并写明原因。
  - 引用器件手册（`datasheet:Datasheet/…`）的参数，不论依据，都要写 `ref`，且设计网表里该位号的 `datasheet` 必须是同一份手册
    （同字节，或文件名去掉厂商前缀后型号相同）；定制磁件写了 `fields.DesignSheet` 的，引用其磁芯、材料手册不受此限。
    常规件因此被引用时，按 [part-roles.md](part-roles.md) 第 1 节升为特殊器件，要写 `mpn`。
  - 保护器件（保险丝、压敏、TVS、稳压管、电源路径上的 NTC）都要进一条 `kind: threshold` 计算的 `refs`，两侧都算；
    X 电容要进放电计算、Y 电容要进接触电流计算的 `refs`（见 [part-roles.md](part-roles.md) 第 1 节“保护器件与安全防护位置”）。`render_design_report.py` 核对，不一致是记录问题。
  - `derived`：由其他值推出，写 `derivation`，`source` 是手册页或 `calc:<计算 id>`。
  - `design_choice`：本设计选定的值（电阻阻值、容差档、匝数），写 `ref`。
  - `model`：工程假设或折减（CTR 保持系数、效率包络等），写 `reason`。
  - `requirement`：来自需求的输入（额定功率、最低输入电压），`source` 写 `req:<需求编号>`，编号须在 `requirements` 里。
  - `constant`：物理常数（铜电阻率），写 `reason`。
  - `unspecified`：手册没给的器件参数。`source`/`locator` 写查过的位置，`operating_point` 指向一条 `specified: false` 的工作点；
    `value` 可留空。含 `typical` 或 `unspecified` 的计算不能是 `supported`。
- **工作点**（`operating_points`，与 `parameter_version` 一起检查）：`{id, refs, pins, mode, specified, source, locator}`。
  `specified: true` 时 `source`/`locator` 指向手册规定这种用法的位置；`specified: false` 时指向查过但没有规定的位置，
  还要 `alternatives`（每项 `{approach, specified, feasible, reason}`）和 `work_item`（external 厂家确认待办）。
  有 `specified` 且 `feasible` 的替代做法时，审计报 `unspecified_operation_with_specified_alternative`（FAIL）。
  保留下来的未规定工作点列在报告“手册未规定的工作点”一节。
  ```json
  {"id": "OP-GPIO1", "refs": ["U601"], "pins": ["GPIO1"], "mode": "开漏灌电流驱动光耦 LED", "specified": false,
   "source": "datasheet:Datasheet/.../Richtek - RT7209.pdf#p12", "locator": "GPIO1 一节只有开路电压与偏置电流档",
   "work_item": "W-OPTO",
   "alternatives": [{"approach": "小信号 MOS 缓冲", "specified": true, "feasible": false, "reason": "……"}]}
  ```
- **资料缺口**（`"gap_version": 2`）：
  每件未关闭的 external 待办写：
  - `missing`：非空列表，每项 `{source, given, needed}`。`source` 是发现缺口的位置：`datasheet:<库内路径>#p<页>`、
    `review:<审查目录>/<待办编号>` 或 `user:<日期>`；`given` 写手册给了什么（含测试条件），`needed` 写设计还需要什么。
    `source` 是器件手册（`datasheet:Datasheet/…`）时加 `refs`：缺口说的是哪些位号，它们在设计网表里的 `datasheet` 必须是这份手册；
    标准、应用笔记不写。
  - 每项 `missing` 加 `kind`，写缺的是哪一类：`unspecified`（手册没给）、`typical_only`（只有典型值）、
    `firmware`（固件或配置）、`internal`（芯片内部行为）。没写记 `gap_kind_missing`；试验、认证、承认、报价不在其中
    （记 `gap_not_external`），改记 `validation` 转交。`unspecified`、`typical_only` 还要写 `alternatives`
    （每项 `{approach, specified, feasible, reason}`，与工作点相同）：评估过的替代做法，例如换一颗手册保证该参数的器件；
    没写记 `gap_without_alternatives`，有手册保证且可行的替代仍保留缺口记 `gap_alternative_feasible`（R8：比较器只给典型延迟）。
  - `why_external`：为什么只能由这个负责方给，例如行为在芯片内部或固件里，外部推不出来；两件以上待办写同一句，
    审计报 `gap_reason_repeated`（R8：七件待办共用一句）。
  - `calculations`：依赖这项资料的计算 id，非空，且都是 `conditional`；报告在待办下列出这些计算依赖的参数，
    并在“依赖厂家资料的计算”表里反查对应待办。确实没有计算依赖它（固件行为确认、安规资格这类）时写空列表，
    并用 `no_calculation_reason` 说明为什么，不为凑字段挂不相关的计算。
  - `consequence`：资料与假设不符时具体会出什么问题，不能只写后果等级。
  - `questions`：能直接发给负责方的问题，每条独立成句；报告按 `owner` 汇总到“要向外部要的资料”一节。
  - `owner`：写到具体公司或角色（“Richtek 应用支持”），问题清单按它汇总。
  - `fallback`：本项自己的替代做法和代价，或本项为什么没有替代；两件以上待办的 `fallback` 文字相同，审计报 `gap_generic_fallback`。
  - `action`：资料到手后怎么关闭这项（重算哪条计算、核对什么）。
  其他报错：缺字段 `gap_missing_fields`，位置格式不对 `gap_bad_source`，计算不存在或不是 conditional `gap_unlinked_calculation`。
  审计只查格式；问题问得对不对、替代做法能不能用，仍要人看。
  ```json
  {"id": "W-PORT-SOA", "stage": "external", "status": "open", "consequence_class": "damage", "occurrence": "fault", "owner": "Richtek 应用支持",
   "missing": [{"source": "datasheet:Datasheet/.../Richtek - RT7209.pdf#p18", "given": "VOH_USBP=VO+8.5–12V，只在 RL=10MΩ 下规定",
                "needed": "带 120nC 栅荷时的电荷泵电流、开通与关断时间", "kind": "internal"}],
   "why_external": "电荷泵驱动能力、故障到下拉的时延和重试时序在芯片内部与固件里",
   "calculations": ["PORT-GATE"], "consequence": "Q701 短路关断或重试时超出 SOA，D-S 短路后端口无法断开",
   "questions": ["从检测到故障到 USBP 开始下拉的最大时延", "短路重试每次开通的持续时间、间隔与次数上限"],
   "fallback": "栅极加由短路检测触发的快放电，增加 3 个器件",
   "action": "按最小 ESR 与最大输出电容积分 Q701 的 VDS-ID-t，对照 SOA 与瞬态热阻核结温"}
  ```
- 待办的 `progress`：design 阶段未关闭的待办写本版做到哪（算了什么、定了什么、还差什么），不能等于 `action`；审查回复 `DESIGN` 引用的待办没有它就不算处理。
- 所有证据 path 相对于 `--artifact-root`，不得逃逸该目录；必须有哈希和页码/章节/行号定位。需求源、数据手册和计算结论都纳入相应证据。`refs` 必须存在于设计网表中；纯使用/验证条件可为空但须说明实现/交接。

```bash
python3 <skill>/scripts/audit_design_closure.py design-closure.json \
  --intent electrical-intent.json --artifact-root . --out design-closure-audit.json
# 与 KiCad 自动检查一起跑：
python3 <skill>/scripts/verify_schematic.py root.kicad_sch --intent electrical-intent.json \
  --design-closure design-closure.json --artifact-root . --out <新的空目录>
```

审计拒绝过期证据、无效位号/依赖、未关闭依赖却声称已实现、部分计算却声称支持结论等矛盾。
`INCOMPLETE` 表示如实记录的未完成设计；`FAIL` 表示记录/结论有矛盾或输入无效；`PASS` 只表示所声明范围内的证据和依赖闭合，**不证明公式正确、需求无遗漏、固件真实支持、ERC/图面审阅通过或审查通过**。人工必须检查证据正文与分类是否成立。新设计交付使用该记录；旧重画流程可不提供，汇总明确显示 NOT_CHECKED。

## 交付状态

分别报告：图纸是否已生成、ASG 设计工作是否闭合、KiCad 自动检查、图面审阅、审查意见处理、后续环节验证。设计报告由 `render_design_report.py` 按这些记录生成。
待办记录审核 PASS 不能覆盖 ERC FAIL 或图面审阅待返工；AUTOMATED_PASS 不能替代设计结论。
仍有可独立完成的设计项时继续完成，而不以“缺口已列出”作为工作结束。

## 原理图设计定型与技术转交PCB

原理图设计定型检查需求功能、确切变体与物理引脚号、启动与保护状态、参数极值、电气选型、KiCad 验证结果。封装库缺失和DFM未做本身不阻断此阶段。引脚未知、额定不足、供电未建立或保护逻辑未闭合仍属于原理图问题，不能改名为PCB待办。封装热条件影响电气额定时，当前阶段建立设计边界，后续环节验证铜面积、散热与实际温升；不得使用未满足散热条件的最大额定直接放行。

报告分别列出原理图待办、真实外部依赖、PCB实现转交和实测转交。交给PCB工作只改变工作归属，不自动关闭相关电气缺陷，也不代表生产放行。
