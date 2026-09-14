# Autonomous-Schematic-Generation

> KiCad 原理图自主生成 / 分析评审 Skill

面向 Codex、Claude 等 Agent 的 KiCad Skill。根据已确认的电气意图创建、
新增、重画原理图，并对原理图、PCB、Gerber、PDF 做有证据的分析与评审。

绘图流程现在包含可执行后端：**可复用电路模块 → 真实引脚编译 → 自动布局 → 字段摆放 →
避障布线 → KiCad 原生文件 → ERC / 逐脚网表 / 几何 / 渲染验证**。
Agent 确定电路和功能角色；后端按真实符号/字段尺寸分配位置、拼页、布线和检查。

## 本次融合

从 [schematic-trace-solver](https://github.com/tscircuit/schematic-trace-solver)
借鉴分阶段求解、Manhattan MST 配对和坏图回归；从
[kicad-mcp-pro](https://github.com/oaslananka/kicad-mcp-pro) 改编几何与字段摆放，
加入 [SKiDL](https://devbisme.github.io/skidl/#generating-a-schematic) 的模块、接口、稳定标签思路，
以及 [circuit-synth](https://github.com/circuit-synth/circuit-synth) 的层次 JSON 和属性表示，
形成 Circuit IR v2、导入适配器和自动布局。详细源码路径、commit、许可证、
实测边界及未采用部分见 [融合说明](references/upstream-integration.md)。

- **真实引脚驱动**：器件身份/网络与几何分开，检查所有引脚分配、旋转和镜像。
- **模块复用**：参数化实例、显式端口绑定、局部网络隔离、按真实库解析重名引脚。
- **自动布局**：功能模板、字段空间预算、多块单页拼排、有限扩距重试；支持已覆盖的多单元符号。
- **改版保护**：电气差异报告与锁定模块再生成，拒绝器件/文字/导线/UUID 漂移。
- **已有工程重排流程**：先保存原层次、器件身份和网表基线，再逐页验证、回写复验；
  多页操作目前使用项目专用 writer，详见[已有工程重排](references/existing-project-redraw.md)。
- **正交避障**：器件体、可见字段、其他网络及预留区都是障碍；失败保留诊断。
- **字段摆放**：Reference/Value 保持水平，避让本体、引脚、已放字段和页边界。
- **独立几何门禁**：检出堆叠、穿芯、文字相交、标题栏侵入、悬空锚点等；
  无法覆盖的对象保留 INSUFFICIENT。
- **原生验证**：ERC、完整 `reference.pin` 网络集合、器件身份、PDF，以及文件哈希。
- **回归测试**：坏图反例、原生旋转/镜像、标签拓扑、无标签直连和未分段 T。

## 运行一个样例

```bash
python3 scripts/build_circuit.py \
  tests/fixtures/generation/dual_filter.circuit.json \
  tests/fixtures/generation/dual_filter.presentation.json \
  --output-dir output/dual-filter-run-01

python3 -m unittest discover -s tests -v
```

输出原生工程、输入快照、布局/布线记录、ERC、XML 网表、PDF和验证报告。
`AUTOMATED_PASS` 仅表示自动检查通过；原生图面目检和数据手册审查仍须完成。
输入与自动布局见 [Circuit IR v2](references/circuit-ir.md)；低层定位后端和几何覆盖见
[生成说明](references/schematic-generation.md)。此前问题的逐项闭环见
[改造清单](references/improvement-ledger.md)。

本次发布验证：**69 项回归通过，无跳过项**，并复跑四个生成入口。
独立电源/PHY 样例保留外部供电与主控连接相关 ERC 待处理项；验证范围、
结果与复现命令见[发布验证记录](references/release-validation.md)。

## 绘图范围与标准

按实际拓扑选择布局：Buck 使用连续功率路径和控制带；LDO、集成电感模块、
晶振、去耦、MCU/接口页分别组织。LM5013 是 Buck 范例，不能作为所有电路
的通用结构。连接器引脚来自接口定义，不能按视觉位置随意指定。

当前生成后端支持多功能块自动排入单页、已覆盖的多单元符号、可见局部布线及
显式远端标签。逻辑层次和标量总线有结构化记录；原生多页层次、图形总线、
任意隐藏/堆叠引脚、复杂跨网图和已有工程原位增量编辑尚未实现。
已支持同一符号、同一网络的同位置端点（含已覆盖的隐藏被动副本），
并在原生网表中保留每个物理引脚；其他情况应使用项目专用 writer 并通过相应门禁。
完整标准见
[schematic-drawing-standards.md](references/schematic-drawing-standards.md)。

原有分析能力保持：网络、BOM、信号/电源、器件风险、PCB/Gerber、跨域一致性、
温升、生命周期等。分析器的 KiCad 5–10 输入支持与新生成器的原生验证范围
分开描述；新后端本次在 **KiCad 10.0.4** 上执行验证。

## 安装

### Codex

将本仓库内容放入 Codex skills 目录：

```bash
git clone https://github.com/wenqiiizwq-creator/Autonomous-Schematic-Generation.git \
  ~/.codex/skills/kicad
```

或直接复制 `SKILL.md`、`agents/`、`references/`、`scripts/`、`examples/`、`tests/` 到
`~/.codex/skills/kicad/`。

### 其他 Agent（Claude / GLM 等）

按对应平台的 skill 安装方式注册即可；仓库结构遵循通用 skill 布局：
`SKILL.md` 为入口，frontmatter 中的 `name` 为 `kicad`。

### 依赖

- KiCad CLI 和符号库；新生成后端实测 KiCad 10.0.4，其他版本需跑原生回归
- 新生成脚本仅用 Python 3.10+ 标准库；PDF 目检渲染使用 `pdftoppm`；分析脚本沿用原依赖
- 网络（可选）：生命周期审计 / 分销商查询需对应 API Key

---

## 使用示例

### 画图 / 重画

```text
- 用 TPS54560 加一路 5V/5A 电源，按 LM5013 风格排版
- 新画一页子图：MPM3650GQW-Z 3.3V→1.15V 1.2A，注意后级低纹波
- 把这张原理图重画成可读布局，电气连接不能变
```

### 评审

```text
- review before fab
- 检查我的原理图有没有问题
- 这份 33.6V→12V 电源可以投板吗
```

### 脚本直用

```bash
python3 scripts/analyze_schematic.py your.kicad_sch --analysis-dir analysis/
python3 scripts/analyze_pcb.py your.kicad_pcb --analysis-dir analysis/
python3 scripts/cross_analysis.py analysis/
python3 scripts/summarize_findings.py analysis/ --json
```

---

## 目录结构

```text
.
├── SKILL.md                        # Skill 入口：绘图 / 评审流程与规范
├── agents/
│   └── openai.yaml                 # Agent 接口描述
├── references/
│   ├── schematic-drawing-standards.md   # 按拓扑选型的绘图规范（绘图必读）
│   ├── circuit-ir.md                    # 结构化电路、模块与自动布局
│   ├── reference-driven-board-design.md # 数据手册外围合同与工程师图面学习
│   ├── existing-project-redraw.md       # 已有多页工程重排、差异检查与回写
│   ├── schematic-analysis.md            # 原理图深审方法论
│   ├── pcb-layout-analysis.md           # PCB 布局分析
│   ├── report-generation.md             # 评审报告模板
│   └── ...                              # 文件格式 / Gerber / PDF 抽取等
├── examples/                       # 可复现的器件级绘图与外围检查样例
├── tests/                          # 几何、原生网表、改版与错误变异回归
└── scripts/
    ├── build_circuit.py            # Circuit IR 编译、布局和原生生成
    ├── generate_schematic.py       # 显式位置和局部线组的生成入口
    ├── check_schematic_geometry.py # 序列化图纸的独立几何检查
    ├── analyze_schematic.py        # 原理图分析器
    ├── analyze_pcb.py              # PCB 分析器
    ├── analyze_gerbers.py          # Gerber 分析器
    ├── cross_analysis.py           # 原理图 ↔ PCB 一致性
    ├── diff_analysis.py            # 版本差异分析
    ├── what_if.py                  # 参数扫描 / 反解
    ├── summarize_findings.py       # 结论汇总
    ├── lifecycle_audit.py          # 器件生命周期
    ├── export_issues.py            # 问题导出
    ├── fab_release_gate.py         # 投板门禁
    └── ...                         # 详见 scripts/README.md
```

---

## 设计约定

- **数据手册是唯一真值**：值来自手册典型应用 / 设计公式，图纸只决定怎么摆；
- **工具行为是约束而非风格**：KiCad/EasyEDA 的坐标精确连接规则要机械遵守；
- **可读性是交付标准**：连得对但像器件堆叠的图不算完成；
- **证据可追溯**：评审结论带 `rule_id`、严重度、证据来源与置信度。

---

## 免责声明

本仓库为 EDA 自动化辅助工具，分析脚本与自动绘图结果应以 KiCad 官方输出、
器件数据手册以及有资质工程师的人工复核为准。作者不对直接用于生产投板
造成的损失承担责任。

---

## License

MIT License

Copyright (c) 2026 wenqiii.zwq

改编部分另保留 tscircuit Inc. 和 Osman Aslan 的 MIT 声明，见
[上游许可证](references/upstream-licenses/)及[来源记录](references/upstream-sources.json)。
