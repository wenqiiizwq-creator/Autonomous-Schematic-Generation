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
