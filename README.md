# Autonomous-Schematic-Generation (ASG)

> ASG：从需求文档出发，基于 KiCad 自主绘制可读、电气正确、经 KiCad 导出验证的原理图

Autonomous-Schematic-Generation（简称 **ASG**）是一套面向 Codex、Claude 等 Agent 的 Skill。
从已确认的需求出发，建立板级电气意图，按绘图纲要 O1–O8 用引脚几何画法（recipes）新建、新增或重画
KiCad 原理图，并用一键自动检查（`verify_schematic.py`）完成 KiCad ERC、逐脚网表、层次、符号、可读性和几何检查。
ASG 只做出图自检；严格的电气审查交给 `schematic-review`。

流程与规则见 [SKILL.md](SKILL.md)。主要工具：

- `verify_schematic.py`：一键自动检查（ERC、网表对意图、层次、系统框图、符号完整性、可读性与纸张、几何，可选参考合同与改版合同）；`audit_system_block.py` 单独检查架构页。
- `build_circuit.py` / `generate_schematic.py`：Circuit IR 编译、自动布局和 KiCad 文件生成，见 [circuit-ir.md](references/circuit-ir.md)、[schematic-generation.md](references/schematic-generation.md)。
- `verify_design_change.py`、`audit_project.py`、`verify_reference_contract.py`：改版合同、多页工程交付核对、器件与外围合同，见 [project-verification.md](references/project-verification.md)。
- `patch_schematic_values.py`：保持连线与图面的 Value 修改，见 [value-patch.md](references/value-patch.md)。
- `check_ledger.py`：检查改进台账最新条目的事件来源、归因和改动文件。改进规则见 [docs/improvement-plan.md](docs/improvement-plan.md)。
- `find_parts.py`：在本机知识库 `~/Documents/知识库/HardwareWiki/raw/` 检索器件手册、参考设计和应用笔记，见 [core-part-selection.md](references/core-part-selection.md)、[part-roles.md](references/part-roles.md)；`--circuits` 检索 [典型电路库](references/typical-circuits.md)。

上游借鉴（schematic-trace-solver、kicad-mcp-pro、SKiDL、circuit-synth）的源码路径、commit、许可证和未采用部分见
[融合说明](references/upstream-integration.md)；历次改造与发布验证记录在 [docs/](docs/)。

当前生成后端支持多功能块自动排入单页、已覆盖的多单元符号、可见局部布线及显式远端标签。
多页层次（由 Circuit IR 直接生成）、图形总线、任意隐藏/堆叠引脚、复杂跨网图和已有工程原位增量编辑尚未实现，
多页工程用 `schematic_layout.root.Root` 组装根图（层次图框、System_block 流向线与隔离边界）并通过相应自动检查。

## 运行一个样例

```bash
python3 scripts/build_circuit.py \
  tests/fixtures/generation/dual_filter.circuit.json \
  tests/fixtures/generation/dual_filter.presentation.json \
  --output-dir output/dual-filter-run-01

python3 scripts/verify_schematic.py board.kicad_sch --intent electrical-intent.json --out runs/verify-01

python3 -m unittest discover -s tests -v
```

`AUTOMATED_PASS` 仅表示自动检查通过；图面审阅和数据手册审查仍须完成。

## 安装

将本仓库放入 Agent 的 skills 目录，例如：

```bash
git clone https://github.com/wenqiiizwq-creator/Autonomous-Schematic-Generation.git \
  ~/.codex/skills/autonomous-schematic-generation
```

`SKILL.md` 为入口，frontmatter 中的 `name` 为 `autonomous-schematic-generation`。
已有旧版 `kicad` 安装时，迁移到新目录，避免保留两份可被扫描的安装。

依赖：KiCad CLI 和符号库（实测 KiCad 10.0.x，其他版本需用 KiCad 导出复跑全部合成测试）；Python 3.10+ 标准库；
PDF 目检渲染用 `pdftoppm`，完整 PDF 页数核对用 Poppler `pdfinfo`（未安装时明确返回检查不足）。

## 设计约定

以 SKILL.md 的「ASG 纲要」为核心标准（含绘图纲要 O1–O8），修改纲要须先经人确认。

- **数据手册是唯一真值**：值来自手册典型应用 / 设计公式，图纸只决定怎么摆；
- **工具行为是约束而非风格**：KiCad 的坐标精确连接规则要机械遵守；
- **可读性是交付标准**：连得对但像器件堆叠的图不算完成；
- **证据可追溯**：意图追溯到需求和手册页码，验证结果绑定文件哈希；严格审查交 `schematic-review`。

## 免责声明

本仓库为 EDA 自动化辅助工具，自动绘图结果应以 KiCad 官方输出、器件数据手册以及有资质工程师的人工复核为准。
作者不对直接用于生产投板造成的损失承担责任。

## License

MIT License

Copyright (c) 2026 wenqiii.zwq

改编部分另保留 tscircuit Inc. 和 Osman Aslan 的 MIT 声明，见
[上游许可证](references/upstream-licenses/)及[来源记录](references/upstream-sources.json)。
