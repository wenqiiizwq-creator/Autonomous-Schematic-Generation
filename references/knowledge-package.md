# 知识包

`references/part-roles.md` 回答"这类器件干什么"；知识包回答"这个功能通常怎么实现、需求要给什么、块之间交代哪些参数、元件值怎么算、器件保证值是多少、器件怎样失效"。
ASG 画不同类型的板子时复用的是这一层，不是具体型号。

知识包由硬件设计知识框架发布，装在 `references/knowledge/`（各组件回答什么见那里的 `README.md`），版本、指纹和逐文件哈希在技能根目录的 `knowledge-release.json`。
知识包只读：不在这里改条目，补写或修订在知识框架里做，重新发布后整包安装。`python3 scripts/knowledge_package.py verify-installed` 核对装的包与清单一致；运行时只读本技能里的包，不读知识框架目录。
准则不在知识包里，在共用层 `references/shared/`；条目里指向 `设计准则/` 的链接在包内无效，按准则编号查 `references/shared/guideline-criteria.md`。条目里的来源路径相对知识库的 `HardwareWiki/raw/`。

## 各模块查什么

| 任务 | 查 | 怎么用 |
|---|---|---|
| C1.1 需求追溯 | `需求要素/` | 按板上的对外端口逐个查对应条目，再查全板条目（板内负载、环境与寿命、安全与电磁兼容的前提），逐行看需求有没有给；没给又定不下来的按[需求澄清](requirement-clarifications.md)问 |
| C2.1 系统架构 | `板级架构模式/` | 电源树、电压域、隔离、接地、保护分层、复位时钟等结构选择 |
| C2.1、C3.3 接口参数 | `接口约定/参数模板/`、`接口约定/总线与电平/` | 跨块流向的 `params` 按参数模板写；总线和电平按总线与电平的条目 |
| C3.1 功能块实现方案 | `典型电路/` | 见下文“典型电路” |
| C4.2 设计计算 | `计算方法/` | 按取值步骤算：每步写了输入取哪一端、算完要满足哪条准则 |
| C4.1、C4.3 器件保证值 | `器件参数/` | 先查这里的保证值和页码，没有的再读手册；用 onsemi 等原件时查 `原件勘误.md` 的“文字层把‘微’抽成‘毫’的原件”一节，名单里的原件（onsemi 的一律算）单位看页面图像，不信文字层 |
| C5.2 FMEA 与异常工况 | `失效与异常工况/` | `器件失效方式/` 查每类器件怎样失效，`分析步骤/` 查 FMEA、故障树、共因失效怎么做 |
| 任意 | `准则支撑表.md`、`条目总表.md` | 从准则编号反查支撑它的条目；全部条目一览 |

## 查阅记录

C1、C2、C4、C5 每次查知识包后记一条，查到没查到都记：

```bash
python3 scripts/check_module.py lookup <设计目录> --task C4.2 --component 计算方法 --query "降压电感取值" \
  --found 计算方法/<条目>.md [更多条目 ...] [--detail "补充说明"]
```

没查到就不写 `--found`。它写进 `record/modules.json` 的 `knowledge_lookups`：日期、任务、组件、查的什么、查到的条目（相对 `references/knowledge/`）。
命令当场核对组件和条目在知识包里。各模块关卡再核一遍，并要求该模块每个该查的组件至少有一条记录：
C1 `需求要素`，C2 `板级架构模式`、`接口约定`，C4 `计算方法`、`器件参数`，C5 `失效与异常工况`（`check_module.py C4 --block` 不核）。关卡不判查得对不对、用没用上。
C3 不用这条命令：选了哪个典型电路的哪种方案记在 `scheme-criteria.json`，没有适用方案由块文件抽出。

没查到的记录由 `knowledge_gaps.py` 抽进知识缺口清单（见[交付与设计报告](delivery-report.md)）。知识包条目日后勘误时，按 `found` 可以找出用过它的设计。

## 典型电路

典型电路文件在 `references/knowledge/典型电路/<功能>.md`，条目格式见那里的 `README.md`：头部是功能、适用范围、电路类型（设计准则库词表的电路类型名，`references/shared/vocabulary.json`），
`## 来源清单` 给来源编号（S1、S2……，正文写 `S1 p4`），`## 选方案时比较的量` 是几种方案的比较表，`## 实现方案` 下每个 `### ` 是一个实现方案（适用范围、核心器件类、必需外围、必算项、落实规则、已知坑、来源）。
只有 `## 实现方案` 一节下的 `### ` 算实现方案；其他节里的三级标题不算。只有指路、没有实现方案的条目（如 `reviewed-bias-and-latch`）不作候选。
用 `scripts/find_parts.py --circuits <关键词>` 检索（匹配文件名、标题、功能和实现方案名）；全部条目见 `references/knowledge/条目总表.md`。

## 规则

- 任务 C6.1 写分页方案时，`page-plan.json` 每页用 `key_blocks: [块名]` 声明关键功能块（功率变换、保护、隔离、信号链、对外接口），关键块标注所用典型电路与实现方案：
  `"circuits": {"<块名>": "<典型电路文件名>#<实现方案名>"}`；分页方案第一页是架构页，免标。
  没有适用典型电路文件的关键功能块写 `"<块名>": "none"`；检查器按块名（`find_parts.py --circuits <块名>` 同样的检索）检索典型电路，命中的文件名要逐个出现在 `scheme-criteria.json` 该块的候选里并写明为什么不适用（整板评测基线 2026-11-07：Matrix 复位块标为库内没有，`multi-domain-reset` 正适用）。检查器对关键块核对已有文件及实现方案，常规块可不标。显式标注的文件和方案名始终核对。`scheme-criteria.json` 中的块也按关键块核对，名称与页计划一致。
- 任务 C3.1 关键功能块对照的规则写进 `record/scheme-criteria.json`，格式固定，报告按它核对；本节是该文件的唯一定义：
  `guideline_scope` 含功率变换、保护、隔离、模拟或对外接口电路类型时必须有这份记录，每个这类类型至少有一块；页计划 `key_blocks` 声明的关键块也必须比较，存在页计划时选定方案须与同名块的 `circuits` 一致。`ports: true` 的块可引用端口矩阵的 G07 全板规则，其余只能引用 `select --typed-only` 选出的规则。这里的结论不代替任务 C4.2 的核算，闭环时这些规则仍按原方式引用覆盖。
  每个关键块还写 `decisive: [{condition, value}]`（条件及本板取值）和 `candidates: [{name, source, status, reason, circuit?, unverified?}]`：`source` 是沿用 datasheet/review/test/user 格式的非空来源列表，`status` 为 `selected` 或 `rejected`，`reason` 写选中或淘汰的理由；恰有一个选定方案，`unverified: true` 的候选不能选定。单候选另写 `only_viable` 说明查过哪些资料及只有一种可行的原因。`circuit` 是与页计划 `circuits` 一致的 `文件名#方案名`；省略时以 `name` 与该引用或其方案名精确比较。没有页计划时跳过一致性核对。
  每块写 `block`、`block_id`（所属功能块，`architecture.json` 的 `blocks[].id`；`block_circuits.py` 按它把方案抽进块文件）、`circuit_types`、`device_kinds`、`ports`（有对外端口为 true）和 `criteria`；`criteria` 只列会淘汰某个候选的规则，每项写 `id`、`excludes`（排除的候选）、
  `basis`（`requirement`、`standard`、`datasheet_abs_max` 能硬排除，只来自工程推论的写 `inference`，不作硬排除）、`how`（选定方案怎样满足）、`defer`（留给 2.2 的数值名）；每个 `defer` 名要在任务 C4.2 闭合：引用该规则（`guidelines` 含它）的某条计算里有一项带 `value`、`operator`、`limit` 的核对，其 `name` 含这个数值名，或其 `defer` 字段（字符串或列表）写它；否则报未闭合，规则挂在没算这一项的计算上只算形式覆盖（整板评测基线 2026-11-07：校准板“SM712 钳位对收发器总线额定”留给 2.2，CALC-RS485 没算）；
  `standard` 只用于 `nature` 为 `shall`/`should` 的规则（见设计准则库 `references/shared/guideline-criteria.json`）；`method` 是工程方法，`project` 是项目输入，按实际依据写 `requirement` 或 `inference`。
  `datasheet_abs_max` 只指器件手册 Absolute Maximum Ratings 表里的值，推荐工作条件不算。
  没有排除候选的规则不写进 `criteria`，放 `searched`。
  `criteria` 为空时 `searched` 写明查过的范围。以下仅为格式示例，test 来源不代表工程证据：

  ```json
  {"version": 1, "blocks": [{"block": "24 V 现场输出保护", "block_id": "OUT", "circuit_types": ["POWER_PROTECTION", "DC_24V"], "device_kinds": ["tvs"],
    "decisive": [{"condition": "现场输出口是否可能反接", "value": "可能，需在开关两态保护"}],
    "candidates": [{"name": "输出钳位并阻断反灌", "source": ["test:格式示例"], "status": "selected", "reason": "满足本板现场输出口保护需求"},
      {"name": "只在输入侧做保护", "source": ["test:格式示例"], "status": "rejected", "reason": "不能覆盖输出口"}],
    "ports": true, "searched": "select --typed-only --ports", "criteria": [{"id": "G07-023", "excludes": "只在输入侧做保护",
    "basis": "standard", "how": "输出口按开、关两种状态各设负向钳位路径", "defer": ["负向残压", "钳位器件脉冲能量"]}]}]}
  ```
- 典型电路的电路类型和落实规则只作参考，不联动 `guideline_scope`；准则适用范围只由本板的电路类型和器件类别决定，适用准则仍须按闭环要求引用覆盖。
- 典型电路里的必算项指到 `计算方法/` 的条目，按其取值步骤在任务 C4.2 算；落实规则只是参考。
