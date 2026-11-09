# 上游来源

`scripts/schematic_layout/` 里有几处机制改写自下面四个 MIT 许可的项目（2026-09-10 学习，固定版本见括号里的提交号）。
本技能运行不依赖这些仓库。按 MIT 许可，原始许可证随技能分发，就是本目录的四个文件。

| 项目 | 借鉴的机制 | 在本技能的位置 |
|---|---|---|
| tscircuit/schematic-trace-solver（`1c6fff6`） | 稳定 pin/net ID、曼哈顿 Prim MST | `routing.py::manhattan_mst` |
| oaslananka/kicad-mcp-pro（`19dc856`） | 本体/字段/可见范围分开、四边字段候选、网格 A*、从文件做几何检查 | `geometry.py`、`field_placer.py`、`scene.py`、`qa.py` |
| devbisme/skidl（`4372de5`） | 器件/引脚/网络对象图、子电路与稳定标签、分块布局 | `circuit_ir.py`、`placement.py` |
| circuit-synth/circuit-synth（`3aaff18`） | 精确引脚名查找、按连接安排邻近器件 | `circuit_ir.py`、`placement.py` |

这些机制只属于低层后端，交付页一律按 SKILL.md 任务 3.2 用 recipes 画。
