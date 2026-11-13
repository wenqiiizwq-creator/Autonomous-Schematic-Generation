# Autonomous-Schematic-Generation (ASG)

> ASG：从需求文档出发，基于 KiCad 自主绘制可读、电气正确、经 KiCad 导出验证的原理图

Autonomous-Schematic-Generation（简称 **ASG**）是一套面向 Codex、Claude 等 Agent 的 Skill。
从需求文档出发，按六个能力模块（C1–C6）完成一块板的原理图设计，再生成设计报告和固定交付目录。
模块可以按给定输入单独运行，也可以串联；上游变化后按指纹重跑受影响的模块。
ASG 负责设计完成并只做自检；独立审查交给 `schematic-review`。

模块划分，各模块的任务、给定输入和产出只写在 [SKILL.md](SKILL.md) 的「架构」与「主流程」，本页不重复；
各脚本做什么见 [scripts/README.md](scripts/README.md)。

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

以 SKILL.md 的「ASG 纲要」为核心标准（核心原则与绘图纲要），修改纲要须先经人确认。

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

## 知识框架

技能直接读本机的硬件设计知识框架，不自带拷贝，也不改它。设计准则（G01–G09）、降额与应力规范（G10）和其余设计知识都在框架里维护：准则登记、词表和 G10 数据在 `知识/设计准则/`，需求要素、板级架构模式、接口约定、典型电路、计算方法、器件参数、失效与故障分析在 `知识/` 下的同名目录。

先告诉技能框架在哪里，二选一（环境变量优先）：

```bash
export HARDWARE_KNOWLEDGE_FRAMEWORK=<硬件设计知识框架的绝对路径>
# 或在技能根目录建文件 .knowledge-framework，一行写框架的绝对路径（该文件不进版本库）
python3 scripts/knowledge_source.py        # 打印框架目录、读取日期和指纹，确认配对
```

框架目录下要有 `知识/` 和 `索引/`；没配或配错时脚本报错并说明办法。各模块查哪部分见 [知识框架的用法](references/knowledge-package.md)。
框架更新后技能直接读到新内容。[知识到关卡的对照表](docs/knowledge-coverage.md) 用 `python3 scripts/knowledge_coverage.py --write` 重新生成，它列出知识框架里每类可核对的内容有多少项、关卡现在核对到哪一步，“核对到内容”为“否”的是技能还没吃进去的知识。
