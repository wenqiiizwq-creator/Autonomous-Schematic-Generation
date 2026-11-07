# 计算条件记录 v1

`scripts/design_preflight.py` 自成一体，独立运行，不依赖其他技能；修改后运行 `test_calculation_preflight.py`。

schematic-review 有同名的约定和脚本，两边各自维护（审查方按独立复核的要求更严格）：

| 项 | ASG | schematic-review |
|---|---|---|
| `ASSUMED`、`TYPICAL` 输入的 `conditions` | 可写可不写 | 必须写 |
| `claim` 字段 | 没有，状态只由脚本推出 | 必须写，并与推出的状态一致 |
| 表达式上限 | 不设上限（2026-10-23 起只保留服务电路正确性的检查，长表达式照常求值） | 长度 ≤2048、语法节点 ≤256 |
| CONDITIONAL | 写明假设即可，不阻塞出图 | 不作通过证据 |

在 ASG 里它用来记录设计计算的依据：CONDITIONAL 写明假设即可，不阻塞出图（见 [设计待办记录](design-closure.md)）。
但结论必须由 acceptance 比较得出，写进 design-closure 的 `checks`；不满足门槛的只能是 FAIL/`failed`。
`model`、`assumptions` 等说明文字用中文写。
它验证声明的条件、有限算术及门槛；不自动选择电路模型、证明极值方向或做量纲代数。

每个 calculation 要有 id、model、expression、inputs、output_unit、acceptance、
assumptions（无假设填 []）。expression 支持有限数、变量、括号与 `+ - * /`，
不执行函数/代码。复杂模型使用有定位的外部推导，结果作为 DERIVED_BOUND 输入，
不得用简单表达式冒充完整仿真。

inputs 按变量名索引，每项含有限数 value、unit、evidence（source/locator 数组），
basis 取 GUARANTEED / DERIVED_BOUND / ASSUMED / TYPICAL。
DERIVED_BOUND 另给 derivation，说明不利方向、区间、外推误差与证据；如果不能支撑边界，
应使用 ASSUMED。GUARANTEED 与 DERIVED_BOUND 还需下面几项（ASSUMED、TYPICAL 可写可不写）：

- conditions：来源保证条件，按工况维度给 `{min, max, unit}`。
- operating_conditions：本设计实际使用区间，必须被对应保证区间包含。
- 来源确实无其他限定时，可给空 conditions，同时写 unconditional_basis；
  不能因为未查到条件就宣称无条件保证。

acceptance 形如 `{"operator":">=","value":5,"unit":"mA"}`，unit 必须与 output_unit 相同。
各输入须预先换算到表达式一致单位；表达式中的常数不能藏起未声明的器件参数。
计算状态由脚本得出：SUPPORTED（条件覆盖且满足门槛）、FAIL（条件覆盖但不满足门槛）、
CONDITIONAL（存在假设、典型值或条件越界）。条件方案另给 closure；算术看似通过也不能
升级为保证值。条件下算得越限也不自动证明实际失效。

例如稳压管仅在 5 mA、25°C 保证某 Vz，而设计偏置仅 0.123 mA：把 IZ/T 的保证条件与
实际区间都填入，计算只能是 CONDITIONAL。不能先假定 Vz 恒定，再声称增加一匝必定修复。
NTC 的 B25/50 跨温区外推和运行时偏置切换能力也要逐项注明假设及关闭方式。

```json
{
  "id": "SYNTHETIC_MARGIN",
  "model": "仅演示格式：已推导的保守电压上界与器件保证耐压比较",
  "expression": "rating - stress",
  "output_unit": "V",
  "assumptions": [],
  "acceptance": {"operator": ">=", "value": 10, "unit": "V"},
  "inputs": {
    "rating": {
      "value": 100, "unit": "V", "basis": "GUARANTEED",
      "evidence": [{"source": "synthetic-spec", "locator": "test-only rating"}],
      "conditions": {"T": {"min": -40, "max": 105, "unit": "C"}},
      "operating_conditions": {"T": {"min": -10, "max": 85, "unit": "C"}}
    },
    "stress": {
      "value": 70, "unit": "V", "basis": "DERIVED_BOUND",
      "derivation": "测试夹具约定的全工况上界；实际设计须另给完整推导",
      "evidence": [{"source": "synthetic-model", "locator": "test-only envelope"}],
      "conditions": {}, "operating_conditions": {},
      "unconditional_basis": "该测试夹具的固定上界，无实际产品含义"
    }
  }
}
```
