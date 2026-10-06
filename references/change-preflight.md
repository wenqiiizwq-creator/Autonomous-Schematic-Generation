# 电气改版：先核影响，再出图，最后核对当前事实

## 出图前

在独立 design-change contract 之外建立 `design-preflight.json`。它不是从候选图差异
反推出来的“预期变化”。根据需求、SR 当前规则下的修改建议和原厂资料先确定：

- changed_objects：改动器件/参数/模型的稳定标识，与 contract 的增删器件、值及连线变化核对。
  新增/删除器件只是挂上或离开已有网络时，该网络上其他未改器件不算 changed，列入 affected_objects；
  引脚之间连接关系真正改变（拆分、合并、改接）的器件才必须作为 changed_objects。
- 每个 trigger 的 affected_objects：包含电气依赖的未改器件，例如偏置绕组变化影响
  控制器供电、驱动幅度、栅极电荷预算、整流二极管反压、电容耐压、稳压支路功耗。
- 每个 trigger 都分类 supply、drive、voltage_stress、current_power、protection、
  temperature、documentation 七个域。CALCULATED 指向 calculation_ids；不适用给理由与证据；
  未解决给 OPEN 和 closure。不要为凑全覆盖编造计算，也不要把七类当作所有电路的完整检查表。
- 计算条件合同见 [calculation-preflight.md](calculation-preflight.md)。不能将 SR 建议直接当作
  数值保证；必须先复核原厂参数的电流、温度、模式等前提。NTC 曲线外推、固件切换能力等
  未决条件明确保留。电气损耗可核算，PCB/结构完成后的实际热验证移交，不要求 SR 代验。

```sh
python3 scripts/verify_design_preflight.py design-preflight.json \
  --contract design-change.json --before-generation --out preflight-before.json
```

PASS 只表示声明的预检查通过。CONDITIONAL 允许在用户已授权的方案范围内继续制作
明确标为条件设计的候选图；必须列出未关闭假设，不宣称可冻结/可投板。结构或算术错误 FAIL
先修正；保证条件覆盖下算得不满足门槛（计算状态 FAIL）是已算出的违规，预检查同样 FAIL。工具不能自动证明 affected_objects 已穷尽，仍需工程师复核耦合链。

## 出图后：一份当前事实核对所有产物

facts 是本版位号、参数和协议/约束的唯一受控值映射，每项 value 为规范字符串并附 evidence。
BOM、图面注释、设计说明、约束清单应从它取值；难以直接生成的现有产物用 artifact_bindings
逐项核对。修改产物以后重跑，不用宽泛全文替换去改未知字段。

支持 CSV 的 key_column/key/column、JSON pointer、文本的单捕获 pattern：定位必须恰好命中
一次；找不到或重复均报错。不同格式需各自声明规范值，不能把 `4T` 与 `4` 随意自动归一化。
对 `.kicad_sch` 注释可用限定具体说明字段的 pattern；PDF 仍进行目检，不能仅凭源文本替代渲染验证。
对本轮修改过的事实，必须列出其在 BOM、图面、说明、移交约束中的所有有效引用；脚本只检查
声明的引用，不会自动理解任意自然语言旧数值。每个事实至少有一个可核对的产物绑定。

```sh
python3 scripts/verify_design_preflight.py design-preflight.json \
  --contract design-change.json --root <工程根目录> --out preflight-delivery.json
python3 scripts/verify_design_change.py baseline.xml candidate.xml design-change.json \
  --preflight design-preflight.json --artifact-root <工程根目录> --out change-verification.json
```

电气改版交付必须使用带 `--preflight` 的组合验证；旧 CLI 无此参数仍可用于单独原生网表差异审计，
不能声称完成电气改版预检查。保留原 ERC、物理脚/器件身份、几何及完整项目 PDF 检查。
输出记录实际产物 SHA256。若 preflight 为 CONDITIONAL，组合结果也不会是 PASS。

## Manifest 结构

```json
{
  "schema_version": 1,
  "revision": "<当前设计版本>",
  "baseline_sha256": "<与 design-change contract 相同的 baseline XML SHA256>",
  "changed_objects": ["T1"],
  "calculations": ["<按计算条件合同填写的对象，不是字符串>"],
  "impacts": [{
    "trigger": "T1", "affected_objects": ["T1", "C1", "D1", "Q1", "U1"],
    "checks": {
      "supply": {"disposition": "CALCULATED", "calculation_ids": ["BIAS"], "reason": "供电极限改变"},
      "drive": {"disposition": "OPEN", "reason": "重新计算栅极驱动预算", "closure": "取得实际驱动条件下 Qg"},
      "voltage_stress": {"disposition": "OPEN", "reason": "电容及反向电压应力", "closure": "计算全部状态下峰值"},
      "current_power": {"disposition": "OPEN", "reason": "偏置稳压功耗", "closure": "计算低/高输出与容差组合"},
      "protection": {"disposition": "OPEN", "reason": "供电变化影响保护门槛", "closure": "核对欠压与保护时序"},
      "temperature": {"disposition": "OPEN", "reason": "保证条件与散热约束", "closure": "核温度范围并更新下游损耗约束"},
      "documentation": {"disposition": "DOCUMENTED", "reason": "统一匝数", "evidence": [{"source":"facts", "locator":"bias_turns"}]}
    }
  }],
  "facts": {"bias_turns": {"value": "4", "evidence": [{"source":"design-intent", "locator":"T1 approved candidate"}]}},
  "artifact_bindings": [{"fact":"bias_turns", "path":"notes.txt", "format":"text", "pattern":"^T1 bias turns=(\\d+)$"}]
}
```

这是字段说明模板，须填写真实 calculations 和产物；不是已通过的生产设计。
