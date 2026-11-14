# 交付

做交付前读 [SKILL.md](../SKILL.md) 和本文件。各模块的总表见 [SKILL.md 的主流程](../SKILL.md#主流程)，关卡与交接文件见 [能力模块](modules.md)，单独运行时的任务书见 [任务书格式](workflow-handoff.md)。

## 设计完成核对

还有可独立完成的设计项就回到对应任务做完，不以列出缺口代替完成。待办只由本版设计过程中确认仍需做的事项决定，不与上一版比较。

同时核对性能定义与选型状态：可独立完成的性能要求计算须完成；仅有料号但关键性能未核实的，不能写“已核准”。有条件性能要求和真实外部依赖继续按现有计算依据分类，不因图纸已输出而转成保证。

做完的标志：各模块在 `record/modules.json` 都是 OK；未关闭项只剩外部资料待办、技术转交、用户暂缓的需求和已登记理由的设计待办；没有未答复的需求澄清；审计列出的可执行设计动作都已完成；淘汰候选方案、改变选型和进入计算的准则都已落实在方案比较、性能记录或计算里。

## 报告与打包

交付增加 `record/component-requirements.json`，报告分别给出性能定义完整程度、选型核实状态和未关闭项；BOM及图面的可见规格由该记录生成。打包检查性能记录和图纸/BOM是否同源、最新、一致；完整规格采购、候选待核与型号已核准各自表述，不能统一写成选型完成。

- 按 [交付证据（快照检查）](delivery-report.md#交付证据快照检查) 写 `delivery-evidence.json`，报告前运行
  `scripts/check_delivery_freshness.py`；任何导出后的修改都会使旧结果作废。
- 交付目录只有下面四样，由 [交付与设计报告](delivery-report.md) 规定，`pack_design.py` 检查：

```
<交付目录>/
  设计报告.md     唯一给人看的文件：render_design_report.py 由记录生成，notes.json 的摘要与说明和记录按同一套专业术语写
  设计方案/       一个标准 KiCad 工程：根图、各页、项目符号库与封装库、schematic.pdf、netlist.xml、BOM.csv；
                  后续 PCB 环节的板子（.kicad_pcb、.kicad_dru 及其自己的文件）放在同一目录、共用 .kicad_pro，
                  ASG 重新出图只换原理图、保留板子与工程文件里的板子设置，板子文件不算交付证据
  设计资料/       跨版本有效、每版更新的设计文档（方案与选型依据、FMEA、EMC 端口矩阵、下游约束表、磁件设计单等；其他按需求选做）
  record/         设计网表、分页方案、待办处理情况、自检结果、图面审阅、本版用到的计算、知识缺口清单、
                  图页脚本、manifest.json（需求、原厂资料按路径+SHA-256 登记，不复制；记知识框架的读取日期与指纹）
```

```bash
python3 <skill>/scripts/render_design_report.py <交付目录> [--notes notes.json] [--title 标题]
python3 <skill>/scripts/pack_design.py <交付目录> --input requirements=<需求目录> \
  --input datasheets=<资料目录>
```

`knowledge_gaps.py <交付目录>` 从各模块的产品里抽出知识缺口清单 `record/knowledge-gaps.json`，不手写：知识框架哪个组件查不到什么（典型电路没有适用方案、`modules.json` 的 `knowledge_lookups` 里没查到的）、候选来源未证实、计算依据是典型值或估计、回到上游重做、用户否定了 ASG 的建议。清单只如实列出，不拦交付；它是评测侧归纳能力缺陷的输入。
也可以用 `deliver.py <交付目录>` 按固定顺序一次跑完生成报告、写交付证据、新鲜度检查和打包，见任务 C6.4。
报告如实写出各项自检的 PASS/FAIL/INSUFFICIENT 及数量（含零）。历史版本快照、日志、仿真中间文件、
审查方的其他文件都不放进交付目录；本版独立审查的报告只放 `record/sr-review/`。

做完的标志：`deliver.py` 各步为 DONE、PASS、CONDITIONAL、INCOMPLETE 或 FRESH 且跑到打包，打包 PASS；
打包列出的 `datasheets_to_file`（本项目用到、知识库还没有的手册）在汇报里提示用户复制进知识库。
