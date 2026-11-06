# 共用层发布迁移验收

## M0：固定 1.9.0（2026-11-06）

依据用户批准的《ASG-SR-规范关系梳理-草案-2026-11-06》方案 A，第 4、6 节。
正式版本锚点为硬件设计规范 `发布/1.9.0/manifest.json`，规范目录不建 Git。

- 起始消费提交：ASG `f3e7afa`，SR `aee8b4b`；施工分支均为 `shared-release`，未动 main。
- 归档十个载荷文件，沿用技能内相对布局；与两边安装件 10/10 逐字节一致。
- 完整指纹：`f62f9e757234a8fd42de5c341cdd30b10b1ef94e25e7971828ad5c80fa049d4a`。
- 格式 `shared-files-sha256-lines-v1`：按清单 fingerprint_order 顺序计算各文件 SHA-256，小写十六进制摘要以 LF 连接，无末尾 LF，再求 SHA-256；保持现行算法。
- `inputs/` 持久保存九份登记、八份共用参考文件和两个脚本，共 19 文件；清单逐项保存相对路径与 SHA-256，包括词表、构建器及共用源。
- 用归档 `inputs/scripts/guideline_criteria.py` 从归档九份登记重建 1.9.0，结果与安装 JSON 逐字节一致：534 条准则、75 项工程取值。
- `evalset-identity.json` 记录评测集实际工作区 3490 个文件及符号链接内容的哈希、HEAD 和状态摘要；含未提交内容，HEAD 不代表完整快照。未改评测集。
- 全量：ASG 1273 passed（366.99 s）；SR 3004 passed（112.92 s，5 warnings）。SR 首轮 11 项 enterContext 环境失败；用显式 `/Users/skyfend/.local/bin/python3` 重跑全绿，未改代码。
- SR `mutation --changed aee8b4b --tier unit`：0 mutations（本步只有文档及台账，无运行代码变化）。两边 check_ledger.py PASS；git diff --check PASS。
- 写入规范目录前备份 `发布/` 原状态于 `/private/tmp/codex-work/rel/backup-m0/`，通过 HardwareWiki 维护锁归档。

本步只归档现状；没有修改准则、工程值、载荷、SKILL.md 或技能流程。清单与输入快照是正式锚点；临时备份和测试日志不是发布身份。

## M1：规范单向发布与安装（2026-11-06）

维护源已收回规范 `共用层/`（七份共用参考源）和 `工具/`（两个脚本）。扩展现有 `guideline_criteria.py`，提供 `release`、`verify-release`、`install` 子命令；使用标准库，技能相对路径和 import 不变。

| 草案第 6 节验收项 | 本次结果 |
|---|---|
| 当前十文件布局发布 | 保留八份 references/shared 文件和两份 scripts 文件；两个 worktree 与同一发布包 10/10 同字节 |
| 安装前后工程值不变 | 全部设计准则 JSON 除 library_version 外完整相等，content_sha256 相同；534 条准则、75 项工程取值未改；降额、最弱档、词表、应力规范及 stress_check.py 六文件同字节 |
| 两个隔离消费快照安装 | 先分别重装归档 1.9.0，10/10 与原安装前相同；再安装 1.9.1，10/10 与候选/正式包相同；其他文件不受影响 |
| 确定性与持久输入 | 两个不同输出位置全部文件同字节；从归档构建器、九份登记、显式词表重建 JSON 同字节；正式包固定 18 个输入文件及十文件清单 |
| 输入边界 | build 只读直接子登记；release 强制九份、G01–G09 各一份；重复 spec/ID、未知引用/词表值、工程取值冲突和公开预览来源拒绝 |
| 清单、安装和不覆盖 | 临时目录先核完整发布清单及指纹，再整批替换受控文件和根目录 shared-release.json；失败回滚；同版同字节幂等，同版不同字节拒绝 |
| 生产身份 | 生产默认装载已安装包；GUIDELINE_CRITERIA 替代输入须显式 GUIDELINE_CRITERIA_TESTING=1，否则报错；显式文件检查和发布构建不受测试环境替代 |

### 门禁与功能证据

- ASG 全量：1293 passed in 382.29s (0:06:22)。
- SR 全量：3024 passed, 5 warnings in 131.46s (0:02:11)。
- SR 官方 `evals/mutation/run.py --changed aee8b4b --tier unit --jobs 4`：15/15 KILLED，未变异副本先通过；不修改运行器，不跳过测试。
- 新增发布测试 20 项：归档 1.9.0 代码上 20 failed，最终代码上两边各 20 passed。
- 新增 M1631–M1638 只跑 `test_shared_release.py` 亦 8/8 KILLED，独立于跨技能字节比对：历史目录递归误读、重复 spec 覆写、输入哈希漏验、同版覆盖、安装前漏验、失败未回滚、显式词表被忽略、生产误用测试替代。
- 两边 `check_ledger.py`、`git diff --check` PASS；ASG 术语检查 PASS；SR 阅读路径检查 PASS。

### 版本、偏离与回退

正式保留 1.9.0，机制变化使用设计准则库下一补丁版 **1.9.1**，不另设 release_version。完整指纹：

`f62f9e757234a8fd42de5c341cdd30b10b1ef94e25e7971828ad5c80fa049d4a`
→ `702e9b357e13e6691c250f4fe4bbeb291dc974fcf5d0d9bf7497b850cc903706`。

指纹格式和范围仍是 `shared-files-sha256-lines-v1`，不静默重算旧记录。安装前后字节不变的验收对归档 1.9.0 回装为 10/10；最终 1.9.1 与旧版为 6/10 相同。四个有意变化是发布器、shared-layer.md、guideline-criteria.md 和 JSON 的 library_version。发布器本身在十文件指纹内，故“新增发布子命令”与“所有十文件保持安装前字节”不能同时成立；依草案 4.3 第 4 条升级而不覆盖旧版，工程内容逐项相等，未将此差异报作全部原样通过。

SKILL.md 本批未改；其中旧版时态说明按用户要求留待 M3 统一替换。原配对/分类跨仓库测试保留；SR 默认封装、元数据重复项留 M2；指纹范围及计划/审计身份兼容留 M4，评测基线留 M5。旧计划、审计仍按现行身份规则复验，本次不转移其历史 PASS。

规范 README 与维护/编制说明只更新当前维护、构建、发布入口；历史日期、状态和原记录未改，共用说明的 1.9.0 历史段落原文保留。未下载资料，未改准则正文/登记、工程数值、主流程或 main；评测集无本批写入，其状态摘要仍与 M0 相同。

规范写前备份位于 `/private/tmp/codex-work/rel/backup-m1/`，所有规范写入通过 HardwareWiki 维护锁。正式包 `发布/1.9.0/` 与 `发布/1.9.1/` 的输入和清单是持久版本锚点。回退技能时分别 revert 本步提交或用原发布工具安装固定旧包；不删除正式旧包。
