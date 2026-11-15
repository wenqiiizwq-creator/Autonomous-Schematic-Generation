# C5 全板闭合

做本模块前读 [SKILL.md](../SKILL.md) 和本文件。各模块的总表见 [SKILL.md 的主流程](../SKILL.md#主流程)，关卡与交接文件见 [能力模块](modules.md)，单独运行时的任务书见 [任务书格式](workflow-handoff.md)。

给定输入：`architecture.json`、`interfaces.json`、各块的块设计 `record/blocks/`。产出：整板 `electrical-intent.json`、整板层块 `blocks/BOARD.json`、需求追溯、闭合矩阵、FMEA 与 EMC 端口矩阵。

## C5.1 设计网表

用 `scripts/blocks.py merge` 把各块的块设计按网络名合成整板设计网表 `electrical-intent.json`：同名端口接成一个网络，每个器件的 `fields.Circuit` 写所属块。合并报错（块内网络重名、端口没有对端、位号重复、同一网络各块的角色或电压不一致）时，按原因回到 C4 或 C2，不在 C5 改块设计。
各块之间只差接口件（上拉、电平转换、隔直）的，C5 写进整板层块 `blocks/BOARD.json` 再合并；要改块内设计的回到该块的 C4，根因在电压域或流向划分的回到 C2。
在 `design-closure.json` 的 `traceability` 为 `requirements.json` 的每条需求写追溯：功能路径、承担器件、状态和依赖的待办，用需求编号引用；不能批量挂整板位号代替追溯。

做完的标志：`blocks.py merge` 无错误，`electrical-intent.json` 由它生成；每条需求在 `traceability` 有功能路径和承担器件（或写明理由的空列表）；每条电源轨写了最高电压；
`object_matrices.py` 按本版设计网表列出的矩阵与状态表逐格有结论（审计没有 `matrix_cell_missing`、`matrix_cell_failed` 和 `matrix_*` 错误）。

## C5.2 全板闭合核对

整板设计网表写完后，按整板审计核对全板：引脚处置、网络电压、对象矩阵与状态表、跨板接口约定。有对外连接器的板写 FMEA 与 EMC 端口矩阵，每块板写下游约束表（[必写的设计文档](guideline-evidence-groups.md)）；端口矩阵里各端口的试验项目、等级和波形查知识框架 `知识/需求要素/环境与电磁等级/`，器件失效方式与分析步骤查 `失效与故障分析/`，从准则编号反查条目用 `索引/准则支撑表.md`。不满足的格改设计，不以列出缺口代替完成。

做完的标志：`audit_design_closure.py`（不带 `--module`）无错误；矩阵与状态表没有缺结论或不满足的格；有对外连接器的板 FMEA 与 EMC 端口矩阵章节与连接器齐全；适用准则里关闭阶段在原理图之后的都有一行下游约束或写明不适用；下游约束表各行写全了接收方、约束和验收。
