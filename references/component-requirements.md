# 器件性能要求：从计算到图纸

任务 2.2–2.4、3.2、4.1、5.3 共用这份记录。新设计和采用本次流程的改版在设计网表写
`component_requirements_version: 1`，并交付 `record/component-requirements.json`。旧记录没有版本标记时显示
`NOT_CHECKED`，不补造历史通过结论。重画旧项目不强制改变其电气定义；新增电气设计采用新流程。

## 先按用途筛选，再计算

`screening` 按功能块分组覆盖每个位号一次，写 `refs`、`decision: standard/contract` 和具体 `reason`。
普通上拉、已核实适用工况的标准去耦可以分组采用受控标准规格；不要为每个普通件增加全参数计算或两家候选的形式要求。
实际依赖耗能、脉冲、温漂、偏压后有效容量等性能的，写 `contract`，在 `components` 建对应性能记录。
先从用途/电路工况决定 `required_parameters`，再填计算结果，不能反过来只列现成手册容易找到的参数。

放电电阻仍要先算实际电流/功率波形及实际电阻耗能，给出起止电压、时间、重复间隔、累计次数、温度与漂移要求。
计算仍由 `design-closure.json` 审计；这里引用计算文件及定位，把结果变为采购约束，不代替电路分析。
`complete` 需要覆盖全部已识别参数；可以自己完成而尚未完成的计算写 `pending` 和 `gaps`，显示“待计算”。

## 数据格式

顶层 `schema_version: 1`、`screening`、`components`。每个性能记录包含：

| 字段 | 含义 |
|---|---|
| `ref`, `kind`, `purpose` | 位号、实际器件类型、在本电路中的用途；类型必须与符号/真实器件一致 |
| `definition_status` | `complete` 或 `pending`；缺计算不能写完整 |
| `required_parameters` | 工况分析识别出的参数名；完整定义逐项覆盖 |
| `requirements[]` | `parameter`, `op: eq/le/ge`, 有限数值 `value`, `unit`, `conditions`, `basis`, `source` |
| `procurement` | `mode: spec/mpn/design_sheet` 与 `reason`；由物理引脚、行为、认证或不可替代曲线决定绑定时列 `binding_dependencies`，必须选 `mpn`；`design_sheet` 只用于带 `fields.DesignSheet` 的定制磁件 |
| `selection` | `status: not_selected/candidate/qualified/by_spec/by_bom_spec/by_design_sheet`；候选与型号已核准时附 `mpn` 和选料途径 `route`；已核准另有 `properties[]`；受控规格核实用 `by_spec`；按 BOM 规格转交采购用 `by_bom_spec`；定制磁件按设计单核实用 `by_design_sheet` |
| `display` | `inline`：完整要求显示在元件旁；`note`：元件旁显示“要求见 CR-位号”，同页生成完整技术注释 |

比较对象是采购性能：`power ge 3 W` 表示额定功率至少 3 W；`tolerance le 5 %` 表示容差不得大于 5%。
要求值、实际工作应力、额定值和降额后的可用值不能互相覆盖。共享应力规范的“超降额未超额定列风险”判法不变。

**只写起约束作用的要求，数值取 2–3 位有效数字**（R10：110 颗器件都写了工作电压，有 R503 ≥ 0.063125 V 这样的值；
用户 2026-10-28：先改前四条）。电压、脉冲等参数只在最坏值超过最弱常用件额定的降额值时才写，判据同
[design-closure.md](design-closure.md) 的“电阻写额定功率”：电阻的工作电压要求不超过封装最弱常用件耐压 × 降额规范 RES-SMD-V 的 `unset_level`（I 级，最严）取值
（0201 15 V、0402 25 V、0603 50 V、0805 100 V、1206 150 V、1210/2010/2512 200 V；没写封装按 0402，与 schematic-review 一致）
时不起约束作用，审核结果 `hints` 给提示。`le`/`ge` 的数值超过 3 位有效数字记错，按保守方向取整：下限向上、上限向下
（`conservative(value, op)`，如 0.063125 → 0.0632、466.69 → 467）。同一句波形或漂移条件出现在 3 颗以上器件时 `hints` 给提示：
按各自工况写，确实相同的保留。提示不挡交付，报告结论一节每类一行。

`conditions` 为非空的“条件名: 具体条件字符串”对象，不能用 TBD/待确认表示完整定义。脉冲参数名以 `pulse_` 开头，
条件至少包括 `waveform`、`duration`、`repetition`、`temperature`、`drift`，漂移条件同时写累计次数。
这不是要求所有器件都计算这些参数；只在脉冲工况实际适用时使用。需要以曲线或多点包络描述时，保留源计算/包络文件，
将决定性约束按不同参数名逐条登记，不能只写“耐脉冲”。

`basis` 可为 `calculation/requirement/standard/model`；工程估计会保持有条件状态，不能变成厂家保证。
每个 `source` 写 `path`、文件内容 `sha256`、`locator`（页码、表/图、计算项或条款）。
路径相对交付目录；也可写 `input:datasheets/子目录/手册.pdf` 引用已声明输入。
输入通过 `--input NAME=PATH` 或 `record/deliver.json.inputs` 登记，不能读取未声明的任意文件冒充证据。
保留原始手册在外部资料目录，不为这项流程把整份手册重复塞进交付包；必要摘页可以在 `record/evidence/`。

核准器件的 `selection.properties[]` 按要求参数逐项给出 `parameter/value/unit/conditions/basis/source`。
`basis` 必须为 `guaranteed`，来源 `kind` 必须是 `manufacturer` 或 `controlled_standard`，附能在源文检索到的 `quote`。
选料途径要写清“受控标准料库”“原厂系列手册和订货编码”“供应商目录找到候选后回原厂核对”等真实过程。
工具核对文件哈希、引文存在、引文中的数值/单位、数值比较和条件一致；工程师/agent仍须核对引文实际对应这个订货变体、参数与保证性质，
不能把机械一致性当作对厂家文件语义的自动证明。典型值/模型值不可作为核准保证，条件不同先保留候选，补推导或厂家证据。
初版工具不自动换算不同单位或证明跨温度/波形的等效性；先统一单位及适用条件，再登记保证。

示例（数值仅示范格式，不能作为真实器件设计或选型依据）：

```json
{
  "schema_version": 1,
  "screening": [{"refs": ["R604"], "decision": "contract", "reason": "电容经该电阻重复放电，需核实际耗能"}],
  "components": [{
    "ref": "R604", "kind": "resistor", "purpose": "脉冲放电限流",
    "definition_status": "complete", "required_parameters": ["pulse_energy"],
    "requirements": [{"parameter": "pulse_energy", "op": "ge", "value": 1.2, "unit": "J",
      "conditions": {"waveform": "指数衰减，波形见计算项C1", "duration": "10 ms",
        "repetition": "间隔不短于60 s", "temperature": "初始70 degC", "drift": "1000次后<=1%"},
      "basis": "calculation", "source": {"path": "record/calculations/discharge.md",
        "sha256": "填写该计算文件的实际SHA256", "locator": "C1电阻实际耗能，不是电容总储能"}}],
    "procurement": {"mode": "spec", "reason": "采用完整可替代性能约束，尚未限定供应商"},
    "selection": {"status": "not_selected"}, "display": "note"
  }]
}
```

真实记录还须列出工况分析得到的阻值、容差、连续功率、工作/过载电压等适用项；上例刻意只展示一项结构，不是参数清单。
标准件可以直接引用受控规格，不要求每颗重新搜索两家供应商。多个可替代来源先分别核实；初版 `selection` 保存当前被采用的
来源，其余来源留在引用的受控标准/AVL及证据中。没有核实来源时可带完整规格继续条件出图，报告仍列选型未关闭。
受控标准料已有经核实的保证和可采购来源时，`selection.status: by_spec`，写 `standard_id` 与 `route`，
逐项 `properties` 引用 `kind: controlled_standard` 的受控保证文件，保持 MPN 为空。这样可完成规格采购核实，
不会因为未绑定某一家订货号永远判未完成。

没有企业受控标准料号的常规件（`procurement.mode: spec`，性能定义完整），算出的要求写进 BOM 规格就是给采购的约束
（用户 2026-10-27：功率等级作为给以后的约束；2026-10-28：先改前四条），写 `selection.status: by_bom_spec`（BOM规格已写全），
不写 `mpn`、`standard_id`、`properties`。原生核对时，每条要求的参数、方向和数值都要在本次导出 BOM 与 XML 的
`RequirementSpec` 里找到（缺了记错），满足即选型关闭。采购按规格找料、核对保证值是转交事项：审核结果 `procurement` 列出这些位号，
报告结论一节只写一行总数，不挡交付；没有本次 BOM/XML 时合并成一条未关闭项。`not_selected` 留给要求还没写进 BOM、
或要靠具体型号保证的件。

定制磁件（变压器、PFC 电感、共模扼流圈等，设计网表写 `fields.DesignSheet`）由自己的磁件设计单定义，`procurement.mode: design_sheet`。
设计单还没写到能逐项回答性能要求时是 `not_selected`；核实后写 `selection.status: by_design_sheet`、`sheet_id`（设计单编号），
逐项 `properties` 写 `basis: design_sheet`、数值、单位、条件和 `acceptance`（样件验收的测试方法与条件），来源 `kind: design_sheet`，
路径就是该器件的 `fields.DesignSheet`，`quote` 必须落在标题写着本位号或设计单编号的那一节（一份 `磁件设计单.md` 写几颗磁件时，
不能引到别的器件的数）。工具核对哈希、分节引文、数值单位、条件一致和大小关系；典型值不能当验收限。
设计单是我方下给厂家的要求，不冒充厂家保证：核实后选型关闭，`project` 把 `sheet_id` 写成正式 MPN、设计单路径写进 Datasheet，
审核结果另列 `acceptance`（样件按设计单验收），报告单列为外部项，不挡交付，也不宣布定型（用户 2026-10-28：按 A 实施）。
拿到厂家承认书后，可改为 `mpn` 方式按厂家保证 `qualified`，MPN 换成厂家料号。

## 固定执行位置

1. **2.2** 计算并写上述单一记录，检查 `required_parameters` 与用途匹配。
2. **2.3** 填采购方式及来源/候选，要求与保证值分开；只有逐项核实后才能写 `qualified`。
3. **2.4** 准备脚本调用 `project(intent, record, artifact_root)` 后写 IR，再用 `write_bom(intent, path)` 写统一 BOM。
   或使用下面的 CLI。图纸脚本/BOM脚本不得重新手抄要求或填默认 1%。
4. **3.1/3.2** 规划技术注释的空白区域；`Sheet.performance_notes(at, refs=None, font=1.27, width=82)` 从本页合同快照生成注释。
   这是文字锚点，电路连接仍使用引脚几何配方。注释参加现有几何、重叠、可读性与逐页视觉审阅。
5. **4.1** 原生 KiCad 导出后自动核对源记录、IR、BOM、XML字段、可见字段、同页注释及对应 PDF 页。
6. **5.1/5.3** 报告重新计算这些结果；`pack_design.py` 随报告复核，`deliver.py` 出图前预检、导出后复检、再生成新鲜度证据。

```bash
asg_skill_dir=/path/to/autonomous-schematic-generation
cd /绝对路径/交付目录
python3 -B "$asg_skill_dir/scripts/audit_component_requirements.py" record/component-requirements.json \
  --intent record/electrical-intent.json --artifact-root /绝对路径/交付目录 \
  --project-intent record/electrical-intent.json --write-bom 原理图/BOM.csv \
  --out record/component-requirements-prepare.json
```

Python API 位于 `scripts/schematic_layout/component_requirements.py`。准备动作显式执行；审核不会自动改写过期输出。
`project` 增加版本标记、每个位号的合同快照和 `RequirementSpec/ProcurementMode/SelectionStatus/SelectedSpec/RequirementsSHA256/Performance` 字段。
未核准候选只留在合同中，不投影到正式 `MPN`/`Datasheet`；已核准 MPN 才写入，具体手册可通过 `selection.datasheet` 同步。
`by_spec` 的受控保证保留在记录中，正式MPN保持空，图面明确标为“受控规格采购已核实”。
`Performance` 是可见属性，其余是供 XML 比对的结构字段。候选原厂手册即使只用于了解性能，也保留来源而不强制绑定该料号。
`Value` 对合同器件保留标称值，容差/功率等要求写在可见性能标注中；旧无合同器件仍执行原有值/规格规则。
合同以 `eq` 定义 `resistance/capacitance/inductance` 时，`project` 同时生成对应阻值/容量/电感量的 `Value`，审核检查它与合同一致；
有效容量下限或脉冲能力等性能边界不改写标称值。没有在合同中定义精确标称值的，沿用设计网表的标称定义。
连续功率统一使用参数 `power`、`rated_power` 或 `continuous_power`，单位 W/mW；原有功率应力审计读取这个最低采购额定，
不会把脉冲峰值功率误当连续额定。BOM同时保留Footprint与实际Kind/Category，不能从R前缀给MOV套电阻分类。
图面只印“参数 比较符 数值 单位”（如“单次脉冲耐受能量 >= 1 J”）和“型号未定/候选待核/型号已核准/BOM规格已写全”等状态；
条件留在记录和 BOM 的 `RequirementSpec` 里（R10：整段条件印在图上，被旁边 PWR_FLAG 的文字插断后核对误报）。
PDF 核对逐条短标签进行，不要求整段注释连续出现；没找到时写明页号和标签。
不要再增加含义不明的 `Tolerance` 列；明确区分 `RequirementSpec` 的上限和 `SelectedSpec` 的已核准实际值。

`verify_schematic.py --artifact-root <交付目录>` 自动读取源记录，BOM默认为根图同目录 `BOM.csv`，也可显式 `--bom`。
检查结果为 `component-requirements-check.json`。隐藏字段、丢失/错误同页注释、过期规格、候选冒充 MPN 判 `FAIL`。
没有可读取 PDF 文字或无法绑定页码时为 `INSUFFICIENT`，必须继续实际图面复核，不能凭一个“已显示”布尔值判通过。
完整定义但候选未核实为 `INCOMPLETE` 并明确列未关闭项；这允许审阅/条件设计交付，不代表定型、生产或放行。
任一输入计算/要求变化，重新准备 IR/BOM、重画、重新导出/核对、重新图面审阅和打包；不复用先前的通过记录。
