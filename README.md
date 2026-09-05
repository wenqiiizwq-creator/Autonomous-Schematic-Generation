# Autonomous-Schematic-Generation

> KiCad 原理图自主生成 / 分析评审 Skill
> （KiCad Project Analysis & Schematic Creation Skill）

一个面向 **Codex / Claude / GLM 等 Agent** 的 KiCad Skill：既能按可读的
LM5013 风格排版**自主创建、新增、重画原理图**，也能对原理图 / PCB /
Gerber / PDF 原理图做结构化分析与设计评审，并在每次出图后强制执行
ERC → 网表 → 渲染的验证门，避免“画出来但连不上 / 没法看”的结果。

---

## 项目简介

原理图自动生成最大的问题不是“连上了”，而是**排版不可读**：器件堆叠、
走线穿电容、引脚挤在一起、功率路径不直观。本 Skill 把绘图排版做成一套
可机械执行的规范（见 `references/schematic-drawing-standards.md`），并
要求生成后必须通过 KiCad 自身的 ERC、网表逐脚核对和 PDF 渲染目检。

该 Skill 由两部分能力组成：

1. **原理图创建 / 重画（Drawing）**
   以数据手册为真值计算元件值，按 LM5013 风格排版标准落图：
   - 从左到右的连续功率母线：`输入 → IC → SW → L → 输出`
   - 底部公共 GND 母线，GND 符号 + PWR_FLAG 支路
   - 控制网络（EN / FB / COMP / SS / PG …）一列一功能，整齐排在
     功率母线与 GND 母线之间
   - 只有关键网络命名（VIN / VOUT / SW / FB / EN …），标签落在导线端点
   - 所有坐标严格落在 1.27mm 栅格；导线在接点处分段
   - 禁止 pin-to-pin 单线、禁止走线穿过器件体、禁止器件重叠
2. **原理图 / PCB 分析评审（Analysis & Review）**
   结构化抽取网络、器件、BOM、引脚拓扑，检测电源、滤波、保护等子电路，
   输出带证据来源和置信度标签的评审结论。

---

## 核心特性

- **LM5013 风格可读排版**：以验收过的 LM5013 33.6V→12V 工程为范本，
  连续功率路径 + 底部 GND 母线 + 控制带，杜绝“器件堆叠”。
- **数据手册驱动**：VREF、开关频率、反馈分压、电感/电容均按数据手册
  公式计算并给出公式依据，不使用“看起来合理”的占位值。
- **强制验证门**：ERC 0/0、网表逐脚核对、分析器复核、几何检查、
  PDF/PNG 渲染目检——任一不通过不交付。
- **KiCad 官方工具闭环**：直接读写 `.kicad_sch`，用
  `kicad-cli sch erc / export netlist / export pdf` 做最终判定，
  不信任第三方解析器的“看似连通”。
- **分析器脚本集**：原理图、PCB、Gerber、跨域一致性、温升、生命周期、
  what-if 参数扫描等 20+ 脚本。
- **兼容范围**：KiCad 5–10（S-expr `.kicad_sch` 与旧版 `.sch`），
  本仓库在 KiCad 9.0.9 上验证。

---

## 排版规范摘要

> 完整规范见 [`references/schematic-drawing-standards.md`](references/schematic-drawing-standards.md)，
> 创建或重画任何原理图之前必须先读它。

### 1. 功率路径优先

- 电源路径必须让读者一眼看懂：`输入 → IC → 开关 → 电感 → 输出`；
- 输入/输出电容用可见分支线挂在母线上；
- 二极管 K 在上、短竖线接 SW、A 接 GND；
- BOOT 电容从 IC 上方走短轨；测试点挂在被测母线上。

### 2. 器件摆放

- IC 锚定模块：输入脚朝左、输出脚朝右、GND/散热焊盘朝下；
- 功率无源件（输入/输出电容、电感）紧贴功率母线；
- 控制无源件（分压、RT、COMP）在功率母线与 GND 母线之间一列一功能；
- 器件体之间至少 1.27mm 净距，标签不得压进 IC 体；
- 连接器：输入左、输出右，pin1 为电源。

### 3. 标签策略

- 电源轨按电压命名：`VIN_33V6`、`VOUT_12V`、`VOUT_5V`、`GND`；
- 功能网按角色命名：`SW`、`FB`、`EN`、`COMP`、`BOOT`…；
- 同一页多模块加后缀：`SW_5V`、`FB_5V`，避免短路；
- 只给关键网命名，标签必须落在导线端点或接点上。

### 4. KiCad 9 布线硬规则（实测）

- 每条导线两端都必须终止在 **引脚 / 接点 / 标签 / 电源符号**；
- **pin-to-pin 单线会被 KiCad 9 整根丢弃**——必须在中间拆接点；
- 拐角 / T 点要显式接点，母线在每个分支 x 处分段；
- **整条网络没有任何标签时会被整网丢弃**（控制网必须命名）；
- 坐标必须是 1.27mm 整数倍，差 0.001mm 都算断开。

---

## 验证门（交付前强制）

生成的原理图必须全部通过：

1. `kicad-cli sch erc` → **0 错误 0 警告**（或列出并解释残余项）；
2. `kicad-cli sch export netlist` → 每个新引脚与设计意图逐脚一致；
3. 分析器复核：调节器/分压检测正常，Vout 按数据手册 VREF 校正；
4. 几何检查：无悬空线、无离栅格点、无器件重叠、无线穿器件体；
5. PDF/PNG 渲染目检：功率母线连续、控制带可读、无堆叠；
6. 元件值给出数据手册公式与计算过程。

> 仅凭 ERC 通过、分析器 JSON 或 API 成功，都不能视为完成。

---

## 安装

### Codex

将本仓库内容放入 Codex skills 目录：

```bash
git clone https://github.com/wenqiiizwq-creator/Autonomous-Schematic-Generation.git \
  ~/.codex/skills/kicad
```

或直接复制 `SKILL.md`、`agents/`、`references/`、`scripts/` 到
`~/.codex/skills/kicad/`。

### 其他 Agent（Claude / GLM 等）

按对应平台的 skill 安装方式注册即可；仓库结构遵循通用 skill 布局：
`SKILL.md` 为入口，frontmatter 中的 `name` 为 `kicad`。

### 依赖

- KiCad CLI：`kicad-cli`（KiCad ≥ 6 推荐 9.x；本仓库在 9.0.9 验证）
- Python 3（分析脚本）；PDF 分析建议安装 `pdftotext` / `pdfplumber`
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
│   ├── schematic-drawing-standards.md   # LM5013 风格排版规范（绘图必读）
│   ├── schematic-analysis.md            # 原理图深审方法论
│   ├── pcb-layout-analysis.md           # PCB 布局分析
│   ├── report-generation.md             # 评审报告模板
│   └── ...                              # 文件格式 / Gerber / PDF 抽取等
└── scripts/
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
