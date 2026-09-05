# Autonomous-Schematic-Generation

KiCad 原理图自主生成 / 分析与评审 Skill（KiCad Project Analysis &
Schematic Creation Skill）。

该 Skill 让 Codex / Claude / GLM 等 Agent 能够：

- 读取并分析 KiCad 工程与 PDF 原理图（.kicad_sch / .kicad_pcb /
  Gerber / 网表 / BOM），做 ERC/DRC、电源树、信号链路、DFM 等检查；
- 按可读的 LM5013 风格排版标准**自主创建/重画原理图**：从左到右的连续
  功率母线、底部 GND 母线、可见分支线、关键网络标签、基于数据手册的元件值；
- 每次出图强制经过验证门：`kicad-cli sch erc`、网表逐脚核对、
  分析器复核、几何检查、PDF 渲染目检。

## 目录结构

```text
SKILL.md                      Skill 入口（含绘图/评审流程）
agents/openai.yaml            Agent 接口描述
references/                   评审方法论与绘图规范
  schematic-drawing-standards.md   LM5013 风格原理图排版规范（必读）
scripts/                      KiCad 分析器与工具脚本
```

## 安装

将本仓库内容放入 Agent 的 skills 目录（例如 Codex：
`~/.codex/skills/kicad/`），或按你所用 Agent 的 skill 安装方式注册。

## License

MIT
