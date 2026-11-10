# Autonomous-Schematic-Generation (ASG)

> ASG：从需求文档出发，基于 KiCad 自主绘制可读、电气正确、经 KiCad 导出验证的原理图

Autonomous-Schematic-Generation（简称 **ASG**）是一套面向 Codex、Claude 等 Agent 的 Skill。
从需求文档出发，按六个能力模块完成一块板的原理图设计：C1 需求理解与澄清 → C2 板级方案 → C3 块电路选择
→ C4 详细设计与器件选型（每块一次）→ C5 全板闭合 → C6 原理图绘制与检查，再生成设计报告和固定交付目录。
模块可以按给定输入单独运行，也可以串联；上游变化后按指纹重跑受影响的模块。
ASG 负责设计完成并只做自检；独立审查交给 `schematic-review`。

流程与规则见 [SKILL.md](SKILL.md)。各模块及交付的主要入口：

| 模块 | 入口 |
|---|---|
| C1 需求理解与澄清 | `check_module.py C1`（核对 `requirements.json`） |
| C2 板级方案 | `check_module.py C2`（核对 `architecture.json`，C3 做完后加 `interfaces.json`） |
| C3 块电路选择 | `find_parts.py`（检索本机知识库及典型电路）、`check_scheme_criteria.py`、`select_guidelines.py`、`block_circuits.py` |
| C4 详细设计与器件选型 | `fill_pin_maps.py`、`make_symbol.py`、`complete_pin_coverage.py`、`audit_design_closure.py`、`audit_component_requirements.py`、`check_module.py C4` |
| C5 全板闭合 | `blocks.py merge`、`audit_design_closure.py`、`check_module.py C5` |
| C6 原理图绘制与检查 | `schematic_layout.recipes.Sheet`、`schematic_layout.root.Root`、`verify_schematic.py`、`audit_system_block.py` |
| 交付 | `deliver.py`（一次跑完出图到打包）、`render_design_report.py`、`pack_design.py`、`check_ledger.py` |

其他：多页核对用 `audit_project.py`、`verify_reference_contract.py`（见 [project-verification.md](references/project-verification.md)）；
夹具与草稿用的低层生成器 `generate_schematic.py` 见 [schematic-generation.md](references/schematic-generation.md)，
它不出交付页。上游借鉴（schematic-trace-solver、kicad-mcp-pro、SKiDL、circuit-synth）见 [上游来源](references/upstream-licenses/README.md)。

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

以 SKILL.md 的「ASG 纲要」为核心标准（原则 P1–P6 与绘图纲要 O1–O8），修改纲要须先经人确认。

维护约定：

- 纲要改动先写草案交人确认，确认后在 [纲要确认记录](docs/outline-approvals.md) 最上面加一行，`python3 scripts/check_ledger.py` 核对。
- 每处改动附复现问题的合成测试，`python3 -m unittest discover -s tests` 全部通过才提交。

## 免责声明

本仓库为 EDA 自动化辅助工具，自动绘图结果应以 KiCad 官方输出、器件数据手册以及有资质工程师的人工复核为准。
作者不对直接用于生产投板造成的损失承担责任。

## License

MIT License

Copyright (c) 2026 wenqiii.zwq

改编部分另保留 tscircuit Inc. 和 Osman Aslan 的 MIT 声明，见
[上游许可证](references/upstream-licenses/)。

## 共用层

共用规范 G01–G10（G01–G09 设计准则、G10 降额与应力规范）由硬件设计规范发布，安装在 `references/shared/` 等受控文件里，技能内不得编辑。
维护源在规范的 `准则登记/`、`规范正文/G10_元器件降额与应力规范/` 和 `工具/`（含 `包说明/`），发布与安装流程只写在规范的 `README.md`；
技能内有哪些共用文件、谁读、怎样核对见 [共用层说明](references/shared/shared-layer.md)。
