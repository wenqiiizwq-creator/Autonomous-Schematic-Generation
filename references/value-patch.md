# 保持图面的 Value 局部修改

已授权且有工程依据的参数更改，例如 R1 的 `1k`→`2k`，可以用 `scripts/patch_schematic_values.py`。工具只替换放置符号的 Value 字符串，保留原来的坐标、连线、UUID、其他字段和层次文本；多单元器件每个单元一起改。不是通用属性编辑器，换型号/脚号、改网络、DNP、封装或拓扑继续走电气改版工作流。

先冻结原工程。`baseline_files` 必须完整列出根图及全部子图的 SHA256，有根图同名 `.kicad_pro` 时也包括它；可从 `schematic_layout.project_audit.audit_project` 的 `file_sha256` 取得图文件列表，用 `schematic_layout.value_patch.frozen_files` 加入项目配置。不要从候选回填旧值。

```json
{
  "schema_version": 1,
  "baseline_files": {"board.kicad_sch": "原文件 SHA256"},
  "changes": {"R1": {"before": "1k", "after": "2k"}}
}
```

```sh
python3 scripts/patch_schematic_values.py 原工程/board.kicad_sch \
  --contract value-patch.json --out 新的候选目录 [--kicad-cli /path/to/kicad-cli]
```

输出必须是原工程外部的新目录。工具拒绝过期基线、旧值不符、未知位号、重复/缺失 Value、无效层次/注释、共享子页或多项目符号的歧义修改；不碰原工程。

候选保存在 `project/`，原始 KiCad XML、PDF、ERC 在 `evidence/`，报告 `patch-report.json`。KiCad 原生 before/after 网表必须满足独立 Value 更改合同：物理脚分区和其他器件身份不变；候选层次和 PDF 页数也须通过。`PATCH_VERIFIED` 只表示局部修改及这些检查成立，**ERC 已导出不表示 ERC 零违规**；不自动声明 `AUTOMATED_PASS`。

根据变化更新独立意图、生成脚本和计算/需求文档，避免下一次生成覆盖此次 Value。继续按主流程第 6–8 步做完整门禁、渲染目检、证据新鲜度核查并交 SR 复审；图面 Value 变长可能影响文字间距，必须看实际 PDF。未通过的候选留 FAIL 报告，不写回原工程；确认基线新鲜且完成审查后再按项目约定替换版本。
