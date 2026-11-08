# 上游项目的采纳清单

2026-09-10 学习了下面四个 MIT 许可的项目，部分机制改写进 `scripts/schematic_layout/`。运行本技能不依赖这些仓库、
不安装新的 MCP 服务，也不自动更新上游。原始许可证在 [upstream-licenses](../references/upstream-licenses/)，精确 commit 与文件指纹在
[upstream-sources.json](upstream-sources.json)。

| 项目与固定版本 | 采纳的机制 | 落在本技能的位置 |
| --- | --- | --- |
| [tscircuit/schematic-trace-solver](https://github.com/tscircuit/schematic-trace-solver) `1c6fff6` | 稳定 pin/net ID；曼哈顿 Prim MST；按视觉失败建回归 | `routing.py::manhattan_mst`（Python 改编，20 组输入与原 TS 比对一致）、几何缺陷测试 |
| [oaslananka/kicad-mcp-pro](https://github.com/oaslananka/kicad-mcp-pro) `19dc856` | 本体/字段/可见范围分开；四边字段候选；网格 A* 与拐弯成本；从文件做几何检查 | `geometry.py`、`field_placer.py`（改编并加硬碰撞约束）、本地重写的有界 A*、`scene.py` + `qa.py` |
| [devbisme/skidl](https://github.com/devbisme/skidl) `4372de5` | 器件/引脚/网络对象图、子电路与稳定标签、分块布局与有界重排 | Circuit IR v2、模块编译、`placement.py` 分块布局（见 [circuit-ir.md](../references/circuit-ir.md)） |
| [circuit-synth/circuit-synth](https://github.com/circuit-synth/circuit-synth) `3aaff18` | 精确引脚名查找；按连接安排邻近器件 | 精确引脚名解析、功能遍历摆放 |

这些机制只属于低层后端：交付页一律按 SKILL.md 任务 3.2 用 recipes 画，不由 MST/A* 出可读页面。

维护约定：

- Python 改编保留来源声明，完整 MIT 许可证随技能分发。
- 上游不自动覆盖本地改编。升级时先固定 commit 与指纹，再做纯模块比较、本地反例、KiCad 网表/ERC 和全页/局部渲染核对。
- 改编时已修正的上游边界（字段被大障碍覆盖仍返回相交位置、同器件两字段不查重叠、离栅格端点被吸附、线段穿过障碍）由
  `tests/` 中的合成测试守着；`tests/probe_upstream.py` 需要本地另行下载上游源码才能运行。
- 2026-11-08 起 SKiDL 对象桥与 circuit-synth JSON 导入（`importers.py`、`import_circuit_synth.py`）已从技能删除；
  `circuit_ir.py`、`placement.py` 仍有改写自这两个项目的机制，许可证照旧随技能分发。
