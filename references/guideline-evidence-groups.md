# 准则证据分组

> 读者：ASG 运行者与维护者。数据在 [guideline-evidence-groups.json](guideline-evidence-groups.json)，`audit_design_closure.py` 按它核对。

适用的共用设计准则（[共用设计准则库](shared/guideline-criteria.md)）里，`coverage` 为 `item` 的按证据分三组（用户 2026-11-07 确认，改进 8）：

| 组 | 怎样算覆盖 | 运行者做什么 |
|---|---|---|
| 自动检查组（`checks`） | 本次审计里这项检查跑过（`requires` 的记录版本都有），且没有它列出的错误代码，审计记为 `check:<检查名>` | 不手写 |
| 文档组（`carriers`） | 一份或几份设计文档登记为证据，证据条目写 `carrier: <组名>`；审计读这些文件，必备章节都在且非空、该出现的对象都出现，记为 `carrier:<证据编号>` | 按下面的模板写文档，登记一条证据 |
| 逐条组（其余） | 计算、待办、器件性能记录或证据条目的 `guidelines` 写编号 | 挂到落实它的那一处 |

分组表只由维护者改，改动要经用户确认。准则库升级后新出现的编号不在表里，就是逐条组。

## 自动检查组

| 准则 | 检查 | 需要的记录版本 | 不能出现的错误 |
|---|---|---|---|
| G01-003 每条需求有唯一编号 | 需求编号唯一 | — | `requirements:` 下的 `duplicate_id` |
| G01-005 需求与设计、验证双向追溯 | 需求双向追溯 | `parameter_version: 3` | `missing_requirements`、`unknown_requirements`、`missing_implementation`、`missing_evidence`、`unlinked_dependency`、`requirement_without_check` |
| G02-038 器件值不得为占位值 | 占位值与未编号位号 | `binding_version: 1` | `placeholder_value`、`unannotated_reference` |
| G04-102 未用脚按手册处置 | 未用脚处置 | `binding_version: 1` | `no_connect_without_disposition`、`disposition_without_source`、`disposition_contradicts_netlist`、`single_endpoint_net` |
| G09-018 选配位用独立字段 | 装配状态独立字段 | — | `dnp_in_value` |

草案里列过的 G02-003、G02-024、G02-026 并入了 WCA 组。G02-036、G02-037、G04-101 退回逐条组：现有检查只核了一部分，比如料号后缀与封装、BOM 与发布图对齐、符号脚集合差集，都不能由设计完成核对完整证明。

## 文档组

章节核对：文件里某个标题行（`#` 开头），或某个表格的表头格，含 `match` 中任一词，就算有这一节。标题下到下一个同级或更高级标题之间要有正文，表格要有数据行，否则算空。
对象核对：每个对象的编号或位号都要在这些文件里以独立词出现（`J1` 不算出现在 `J10` 里，`J1～J4` 也不算写了 J2）。

| 对象 | 取自 |
|---|---|
| `requirements` | `design-closure.json` 的需求编号 |
| `calculations` | 计算编号 |
| `connectors` | 设计网表里的连接器位号（不含测试点、机械件） |
| `isolators` | 器件类别为 `opto`、`transformer` 的位号（数字隔离器归 `ic`，要自己写进边界表） |
| `thermal_refs` | 引用了任一 G08 准则的计算所涉及的位号 |
| `rails` | `net_voltages` 的网络名 |

一个组可以由几条证据共同承担，几份文件合起来核。

只要声明了某个组，这个组的准则就只认文档核对的结果，别处的逐条引用不再算。没有声明的组，旧记录里的逐条引用照旧算覆盖。
核对不过时，审计记 `guideline_carrier_incomplete`，列出缺的章节、空的章节和缺的对象。这一组的准则同时记为 `guideline_uncovered`。
`carrier` 写了表里没有的组名，记 `guideline_carrier_unknown`。设计确实没有某类内容（如无隔离边界）的，在 `guideline_scope.not_applicable` 写理由，或者在相应章节里写明“无”及理由。

各组的准则、必备章节和对象见 JSON。写文档时按 `sections` 的 `name` 起标题，一节对一项，不必写准则编号。

| 组 | 文档 | 准则数 | 对象 |
|---|---|---|---|
| REQ | 需求追溯 | 8 | 需求 |
| OPM | 工况矩阵 | 3 | — |
| IF | 接口定义 | 7 | 连接器 |
| WCA | 最坏工况分析说明 | 27 | 计算 |
| FMEA | FMEA | 15 | 连接器 |
| SAFE | 隔离与绝缘 | 9 | 隔离器件 |
| EMC | EMC 端口矩阵 | 10 | 连接器 |
| THERM | 热分析说明 | 17 | 热计算位号 |
| TEST | 可测试性与生产 | 4 | 电源轨 |

## 刻意留在逐条组的

凡是要对全部对象逐个核对的准则，都不放进文档组整组覆盖，例如 G02-022/023（时序、电平）、G02-027/028（应力组合）、G03-025（复位门限对每个负载）、G08-006/007（工作与贮存温度）、G08-023～025（逐器件结温）、G07-019（浪涌电流定界）。它们挂在做这项核对的计算上。

## 局限

章节与对象核对只能证明写了、对象写全了，不能证明写得对；写得对不对，靠 SR 审查。
