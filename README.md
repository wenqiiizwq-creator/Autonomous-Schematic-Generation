# Autonomous-Schematic-Generation (ASG)

> ASG：从需求文档出发，基于 KiCad 自主绘制可读、电气正确、经 KiCad 导出验证的原理图

Autonomous-Schematic-Generation（简称 **ASG**）是一套面向 Codex、Claude 等 Agent 的 Skill。
从需求文档出发，按五步完成一块板的原理图设计：需求与方案（需求追溯、系统架构、功能块方案、核心器件选型）→ 详细设计
（数据手册核对、设计计算与器件性能要求、选型符合性、设计网表）→ 原理图绘制（按绘图纲要 O1–O8 用引脚几何画法 recipes）
→ 设计检查（KiCad ERC、逐脚网表、层次、符号、可读性、几何与图面审阅）→ 设计输出（设计报告与固定交付目录）。
ASG 负责设计完成并只做自检；独立审查交给 `schematic-review`。

流程与规则见 [SKILL.md](SKILL.md)。各步的主要入口：

| 步骤 | 入口 |
|---|---|
| ① 需求与方案 | `find_parts.py`（检索本机知识库 `~/Documents/知识库/HardwareWiki/raw/` 与 `--circuits` 典型电路库）、`check_scheme_criteria.py`、`guideline_criteria.py select` |
| ② 详细设计 | `fill_pin_maps.py`、`audit_design_closure.py`、`audit_component_requirements.py` |
| ③ 原理图绘制 | `schematic_layout.recipes.Sheet`、`schematic_layout.root.Root`（见 [drawing-recipes.md](references/drawing-recipes.md)） |
| ④ 设计检查 | `verify_schematic.py`（一次运行全部自动检查）、`audit_system_block.py` |
| ⑤ 设计输出 | `deliver.py`（一次跑完出图到打包）、`render_design_report.py`、`pack_design.py`、`check_ledger.py` |

其他工作流：改版与多页核对用 `verify_design_change.py`、`audit_project.py`、`verify_reference_contract.py`（见 [project-verification.md](references/project-verification.md)）；
保持图面的 Value 修改用 `patch_schematic_values.py`（见 [value-patch.md](references/value-patch.md)）；导入与草稿用的低层生成器
`build_circuit.py` / `generate_schematic.py` 见 [circuit-ir.md](references/circuit-ir.md)、[schematic-generation.md](references/schematic-generation.md)，
它们不出交付页。上游借鉴（schematic-trace-solver、kicad-mcp-pro、SKiDL、circuit-synth）见 [采纳清单](references/upstream-integration.md)。

## 运行一个样例

```bash
python3 scripts/verify_schematic.py board.kicad_sch --intent electrical-intent.json --out runs/verify-01
python3 scripts/deliver.py <交付目录>          # 参数在 <交付目录>/record/deliver.json

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

依赖：KiCad CLI 和符号库（实测 KiCad 10.0.7；本技能文档中的 KiCad 版本以此处为准，换版本需用 KiCad 导出复跑全部合成测试）；Python 3.10+ 标准库；
PDF 目检渲染用 `pdftoppm`，完整 PDF 页数核对用 Poppler `pdfinfo`（未安装时明确返回检查不足）。

## 设计约定

以 SKILL.md 的「ASG 纲要」为核心标准（原则 P1–P7 与绘图纲要 O1–O8），修改纲要须先经人确认。

## 免责声明

本仓库为 EDA 自动化辅助工具，自动绘图结果应以 KiCad 官方输出、器件数据手册以及有资质工程师的人工复核为准。
作者不对直接用于生产投板造成的损失承担责任。

## License

MIT License

Copyright (c) 2026 wenqiii.zwq

改编部分另保留 tscircuit Inc. 和 Osman Aslan 的 MIT 声明，见
[上游许可证](references/upstream-licenses/)及[来源记录](references/upstream-sources.json)。

## 共用层

共用规范 G01–G10（G01–G09 设计准则、G10 降额与应力规范）由硬件设计规范发布，安装在 `references/shared/` 等受控文件里，技能内不得编辑。
维护源在规范的 `准则登记/`、`规范正文/G10_元器件降额与应力规范/` 和 `工具/`（含 `包说明/`），发布与安装流程只写在规范的 `README.md`；
技能内有哪些共用文件、谁读、怎样核对见 [共用层说明](references/shared/shared-layer.md)。
