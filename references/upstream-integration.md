# 四个上游项目的源码学习与融合

下载时间：2026-09-10。源码保存在项目 `upstream/`，由
`.gitignore` 排除；运行 skill 不依赖该目录，也不自动更新上游。
许可证均为 MIT，原始许可证保存在 [upstream-licenses](upstream-licenses/)。
精确 commit 和文件指纹见 [upstream-sources.json](upstream-sources.json)。

## 下载及复现

| 项目 | 固定版本 | 本地目录 |
| --- | --- | --- |
| [tscircuit/schematic-trace-solver](https://github.com/tscircuit/schematic-trace-solver) | `1c6fff647502591b15eb491e01a8f989c73123c7`，package 0.0.192 | `upstream/schematic-trace-solver` |
| [oaslananka/kicad-mcp-pro](https://github.com/oaslananka/kicad-mcp-pro) | `19dc85611c892166003edf54a1c2b68e7a4db527` | `upstream/kicad-mcp-pro` |
| [devbisme/skidl](https://devbisme.github.io/skidl/#generating-a-schematic) | `4372de59bdc5d37c83c0870a0a25d8152ef75359` | `upstream/skidl`，浅克隆，稀疏检出核心对象/生成源码 |
| [circuit-synth/circuit-synth](https://github.com/circuit-synth/circuit-synth) | `3aaff18c056de7cbe8f5b0a3e1e6e7e7895f544e` | `upstream/circuit-synth`，完整克隆 |

没有安装/启用新的 MCP server，也没有修改全局 KiCad 设置或上游源码。
后续重新下载时，clone 后 checkout 上表 commit，再运行源码比较探针。
SKiDL 的 Git 稀疏检出配置仅用于缩小本地研究下载；隔离 `.venv` 安装其固定
源码以执行对象桥探针，缓存/数据目录指向研究输出，不作为 skill 运行依赖。

## 源码结构与采用决策

| 来源与具体模块 | 学到的机制 | 本项目落地 | 边界/取舍 |
| --- | --- | --- | --- |
| tscircuit `lib/types/InputProblem.ts` | 稳定 pin/net ID；器件与文本障碍分开；直连与标签连接分开 | intent/layout JSON，真实 `ref.pin`，`mode=wire/labels` | 不把 tscircuit 坐标/方向和 SVG label 当作 KiCad 原生语义 |
| `MspConnectionPairSolver/getMspConnectionPairsFromPins.ts` | Manhattan Prim MST，稳定 ID 打破距离平局 | `routing.py::manhattan_mst` 的 Python 改编 | 按 net 单独调用；20 组输入与原始 TS 比较 |
| `SchematicTracePipelineSolver` / `SchematicTraceSingleLineSolver2` | 分阶段路由、引脚朝向、文本障碍、可观察的失败连接 | 字段→障碍→配对→A*→标签→导线归一化→独立 QA | 没有搬入几十个 TS 清理求解器，也未宣称完整上游等价 |
| tscircuit `tests/repros/` 和 debug runner | 保存具体坏图/输入，按视觉失败建回归 | 几何缺陷测试、旋转镜像原生测试、JSON fixture/失败记录 | 未运行完整 Bun/SVG 测试集 |
| kicad-mcp-pro `utils/geometry.py` | 本体、字段边界和可见范围分开 | 改编为 `schematic_layout/geometry.py` | 改进多行/CJK宽度、旋转锚点；文字仍为估计值 |
| `utils/field_placer.py` | 四边字段候选，避让引脚侧 | 改编为 `schematic_layout/field_placer.py` | 碰撞为硬约束；新增边界/已放字段/针脚/keepout；无解报错 |
| `utils/schematic_router.py` | 网格 A* 与拐弯成本 | 重写本地有界 A* | 状态含方向；检查整条边；拒绝离栅格端点和障碍中的终点 |
| `models/visual_qa.py` | 从 native 文件做几何检查 | 独立 `scene.py` + `qa.py`，回读序列化文件 | 未复制正则解析/固定框兜底；新增穿芯、同器件字段、标题区检查 |
| `tools/schematic.py` 字段写回/原生验证 | 字段变更与输出分离，原生检查不可省 | 新目录、文件哈希、local sym-lib-table、ERC/XML/PDF | 不引入大型 MCP server 及其部署/制造流程 |
| SKiDL `Circuit/Part/Pin/Net/Node/Bus/Interface` | 对象图、模块接口、稳定 tag、层次实例、标量总线 | Circuit IR v2、模块编译、SKiDL 对象桥、稳定 UUID | 显式实库映射；不运行输入源码或隐式重编号 |
| SKiDL `tools/kicad9/gen_schematic.py` | 分块布局、重试、可选 stubbing 与 ERC 循环 | 采用分块与有界重排，保留每次失败证据 | 不采用失败后标签化或通过改电气数据清理 ERC |
| circuit-synth `core/netlist_exporter.py::to_dict` | 组件字典、递归子电路、list/nodes 两种网络连接及属性 | JSON 适配器、源数据审计、真实脚号编译 | 源码明确不区分 local/external net，跨块同名必须显式定范围 |
| `core/simple_pin_access.py` | 精确号码和名字查找；重名返回 PinGroup | 精确名字解析并要求显式 all:true | 不静默将多个 GND/电源脚选成一个或全部 |
| `connection_aware_collision_manager.py` | 按连接安排邻近器件 | functional 遍历、真实总占用、模块拼排 | 未把简单邻接布局宣称成已解决全局最优/多页/任意非平面布线 |

## 实测发现的上游适配风险

`tests/probe_upstream.py` 直接加载固定 commit 的纯 Python 模块，并通过
Node TypeScript stripping 执行上游 MST 函数；不是从 README 推断结果。

- 字段四边被大障碍覆盖时，原始 field placer 仍返回相交位置；本地拒绝。
- 原始 `detect_text_overlap` 跳过同一器件两个字段；同点 Reference/Value
  探针返回 0 条，本地几何检查可以检出。
- 原始简易路由器把 `(0.1,0)` 吸附到 `(0,0)`；本地拒绝离栅格端点。
- 原始路由器在网格 1 mm、障碍 `x=0.4..0.6,y=-0.1..0.1` 时返回穿过
  障碍的 `(0,0)→(2,0)`；本地检查完整线段并绕行。
- 原始 TS MST 与本地改编对 20 组固定随机输入的无向边集合一致。

这些是指定纯模块的边界，不代表上游完整流水线必然输出同样缺陷；其其他
阶段可能检测或修复。未经执行的完整能力仍仅属于源码理解范围。

## KiCad 原生适配与证据

原生测试覆盖 RC 可见连线、显式远端地标签、12 组旋转/镜像器件、真实
`reference.pin` 集合，以及无标签直连/未分段 T。所有 ERC 与网表证据均
绑定运行时 KiCad 版本，不能推广为已验证全部 KiCad 版本。

本次适配特别修正了两个由目检/原生网表发现的问题：

1. 旋转 90/270° 的器件必须写入对应字段角度才能保持 Reference/Value
   在 native render 中水平；仅给字段写 0° 会留下竖排。
2. 镜像必须作用于旋转后的放置坐标轴。错误次序在 ERC 0/0 时仍可能把
   引脚号互换；原生测试用 24 个真实引脚、12 个标签网络逐一核对。

进一步的原生目检发现侧边文字对齐会被镜像/180°旋转翻转，因此最终写入
统一使用居中字段锚点；本地标签仅输出已验证的 0°样式，向左的标签用更长
短桩避开引脚。回归会在有 `pdftotext` 时读取 native PDF 的文字包围框，
检查字段方向及镜像后穿入本体，避免只检验代码自己的坐标假设。

生成器产生 native PDF，但不会自动声称视觉审查完成。精确字形、引脚
名称/编号独立边界及自定义图框仍必须看原生渲染。各次机器验证结果见
`verification.json`；样例不构成复杂板级生成能力证明。

## 已实现范围与维护

已融合可运行的单页生成后端、字段摆放、正交避障、真实符号适配、独立
几何门禁和原生回归，`SKILL.md` 已接入正式绘图流程。

进一步实现了 Circuit IR v2、自动功能块放置、字段空间预算、单页拼排、
有界重排、多单元视图、属性/装配回读、稳定身份和受保护的再生成。
格式及命令见 [circuit-ir.md](circuit-ir.md)，逐项闭环见
[improvement-ledger.md](improvement-ledger.md)。原生多页/图形总线、隐藏/叠加
引脚、任意复杂跨网图和手工工程原位增量编辑仍需专用 writer。

`tests/probe_structured_upstream.py` 读取真实 SKiDL Circuit/Node/Part/Net 并
验证源对象不变、网分区一致；还在隔离命名空间执行 circuit-synth 原始
`NetlistExporter.to_dict` 方法，验证递归子电路和两种 net JSON 形式。
这是对象/序列化层的执行证据，不是两个上游整套生成器的同题性能评测。

- Python 改编保留来源声明，完整 MIT 许可证随 skill 分发。
- `geometry.py` / `field_placer.py` 源自 kicad-mcp-pro；MST 改编源自
  tscircuit；路由/原生文件适配/QA/CLI 为本地实现或按已注明机制重写。
- 上游不自动覆盖本地改编。升级先固定 commit/指纹，再执行纯模块比较、
  本地反例、原生网表/ERC和全页/区域渲染。
- KiCad 符号库来源与哈希进入每次 manifest；示例的空封装/测试值不得
  冒充已完成选型的硬件设计。
