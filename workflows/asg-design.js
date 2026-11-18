export const meta = {
  name: 'asg-design',
  description: '原理图设计（ASG）：小板一位设计者加一位绘图者；器件多的板由架构师、并行的块设计者、整板核对者和绘图者完成',
  whenToUse: '从需求做一块板的原理图设计并交出固定的交付目录；或拿审查报告对已有设计做一次改版',
  phases: [
    { title: '判规模' }, { title: '板级方案' }, { title: '设计' }, { title: '整板核对' }, { title: '原理图' },
  ],
}

// args: {
//   workdir: 设计目录（绝对路径；各环节的产出都在这里）,
//   inputs: 一段话说明需求文件在哪里，以及任务书（澄清答复、代答授权）在哪里（没有就写没有）,
//   delivery: 交付目录的绝对路径（改版时用原来的交付目录，设计方案/ 里 PCB 环节的板子保留）,
//   review: 可选，改版时审查报告的路径（审查工作流的产出）或一段改动说明,
//   mode: 可选，auto（默认：小板走快速设计，器件多的板走分块设计）、quick、blocks,
//   quick_limit: 可选，小板的器件数上限，默认 40,
//   skill: 可选，技能目录，默认 ~/.agents/skills/autonomous-schematic-generation
// }
const a = args || {}
if (!a.workdir || !a.inputs || !a.delivery) throw new Error('args 需要 workdir、inputs 和 delivery')
const SKILL = a.skill || '~/.agents/skills/autonomous-schematic-generation'
const common = `全程中文。技能目录 ${SKILL}（只读，不改其中任何文件）。设计目录 ${a.workdir}，各环节的产出写在这里；交付目录 ${a.delivery}（顶层只有 设计报告.md、设计方案/、设计资料/、record/；设计方案/ 是原理图和 PCB 共用的标准 KiCad 工程，其中板子文件属 PCB 环节，不改不删）。
输入：${a.inputs}`
const R = { type: 'object', required: ['status', 'summary'], properties: {
  status: { type: 'string', enum: ['done', 'needs_input'] }, summary: { type: 'string' }, questions: { type: 'array', items: { type: 'string' } } } }
const QD = `${SKILL}/references/quick-design.md`

// 改版：一位设计者逐条处置审查意见或改动要求，绘图者重画。
if (a.review) {
  phase('设计')
  const d = await agent(`${common}

这是对已有设计的一次改版。审查报告或改动说明：${a.review}。读 ${SKILL}/SKILL.md 的「ASG 纲要（核心标准）」一节和 ${QD}（“设计者做什么”和“改版”两节），照“改版”一节做：逐条处置，改设计网表和设计报告。
知识框架目录见 ${SKILL}/.knowledge-framework。需要人定的才返回 needs_input 并把问题写进 questions。
返回 status 和 summary（每条意见怎么处置的、改了哪些器件和网络、哪几条没有改及理由）。`,
    { label: '改版设计', phase: '设计', schema: R })
  if (!d) return { status: 'stopped', done: [] }
  if (d.status === 'needs_input') return { status: 'needs_input', questions: d.questions || [], summary: d.summary, done: [] }
  phase('原理图')
  const g = await agent(`${common}

你是绘图者。读 ${QD} 的“绘图者做什么”并照它做：设计网表在设计目录的 record/electrical-intent.json，设计报告在 设计目录/设计报告.md。这是改版：只重画有变化的页，交付目录的 设计方案/ 里只替换原理图文件和导出物，不清空目录。
画完并通过自动检查后更新交付目录，并在设计报告的“自检结果”里填上 ERC、网表比对和图面检查的结果。
返回 status 和 summary（重画了哪几页、ERC 违规数、网表是否逐脚一致、summary.json 里各检查项的结果）。`,
    { label: '绘图与自检', phase: '原理图', schema: R })
  return { status: g && g.status === 'done' ? 'complete' : 'blocked', mode: 'revision', workdir: a.workdir, delivery: a.delivery, report: `${a.delivery}/设计报告.md`,
    done: [{ stage: '改版设计', summary: d.summary }, { stage: '绘图与自检', summary: g ? g.summary : '绘图没有返回结果' }] }
}

// 小板快速设计：一位设计者从需求做到设计网表和设计报告，一位绘图者画图并跑自动检查。
// H-001 2026-11-16：13 个器件的板走六个模块 68～82 分钟、约 300 万 token，不带技能直接设计约 20 分钟。
let mode = a.mode || 'auto'
if (mode === 'auto') {
  const size = await agent(`${common}\n\n只做一件事：读需求，判断这块板是不是小板——预计器件不超过约 ${a.quick_limit || 40} 个位号、单一电压域、没有隔离与安规要求、没有高速接口。返回 small（是否小板）和 reason（一句话）。不写任何文件。`,
    { label: '判规模', phase: '判规模', schema: { type: 'object', required: ['small', 'reason'], properties: { small: { type: 'boolean' }, reason: { type: 'string' } } }, effort: 'low', model: 'sonnet' })
  mode = size && size.small ? 'quick' : 'blocks'
  log(`${mode === 'quick' ? '小板，走快速设计' : '器件多，走分块设计'}：${size ? size.reason : '没有判出规模'}`)
}
if (mode === 'quick') {
  phase('设计')
  const d = await agent(`${common}

你是这块板的设计者，做小板快速设计。读 ${SKILL}/SKILL.md 的「ASG 纲要（核心标准）」一节和 ${SKILL}/references/quick-design.md，照“设计者做什么”做完第 1 到第 7 步；只读细则点到、且你确实要用的参考文件，不通读其他模块细则。
知识框架目录见 ${SKILL}/.knowledge-framework。产出写在设计目录：设计资料/需求基线.md、record/electrical-intent.json、设计报告.md。
需要人确认的地方：任务书里有答复或代答授权的按任务书办；没有且必须人定的才返回 needs_input 并把问题写进 questions。
返回 status 和 summary（方案一句话、器件数、采纳了哪几条澄清、余量最小的三项、未核实项）。`,
    { label: '快速设计', phase: '设计', schema: R })
  if (!d) return { status: 'stopped', done: [] }
  if (d.status === 'needs_input') return { status: 'needs_input', questions: d.questions || [], summary: d.summary, done: [] }
  phase('原理图')
  const g = await agent(`${common}

你是绘图者。读 ${SKILL}/references/quick-design.md 的“绘图者做什么”并照它做：设计网表在设计目录的 record/electrical-intent.json，设计报告在 设计目录/设计报告.md。
画完并通过自动检查后，把交付目录按该节写齐（设计报告.md、设计方案/、设计资料/需求基线.md、record/），并在设计报告的“自检结果”里填上 ERC、网表比对和图面检查的结果。
返回 status 和 summary（页数、ERC 违规数、网表是否逐脚一致、summary.json 里各检查项的结果、改过设计网表的地方）。`,
    { label: '绘图与自检', phase: '原理图', schema: R })
  return { status: g && g.status === 'done' ? 'complete' : 'blocked', mode: 'quick', workdir: a.workdir, delivery: a.delivery, report: `${a.delivery}/设计报告.md`,
    done: [{ stage: '快速设计', summary: d.summary }, { stage: '绘图与自检', summary: g ? g.summary : '绘图没有返回结果' }] }
}

// 分块设计：器件多的板。架构师定板级方案，各功能块并行设计，整板核对者合并并走查，绘图者画图；不设接口定稿，不逐级回退。
// M-001 2026-11-17：约 100 个器件的控制板走六个模块约 8 小时、回退 14 次，独立审查指出 1 条 P0、4 条 P1；直接设计 41 分钟、1 条 P1。
{
  const read = `读 ${SKILL}/SKILL.md 的「ASG 纲要（核心标准）」一节和 ${QD}（“设计者做什么”和“分块设计”两节）；只读细则点到、且你确实要用的参考文件，不通读其他参考文件。知识框架目录见 ${SKILL}/.knowledge-framework。`
  phase('板级方案')
  const arch = await agent(`${common}

你是这块板的架构师。${read}
照“架构师”一节做：写 设计资料/需求基线.md、设计资料/板级方案.md 和 record/architecture.json。
需要人确认的地方：任务书里有答复或代答授权的按任务书办；没有且必须人定的才返回 needs_input 并把问题写进 questions。
返回 status、summary（电源树一句话、采纳的澄清、每颗保护或切换芯片对应哪条需求、引脚余量）和 blocks（功能块的 id 列表，与 architecture.json 一致）。`,
    { label: '架构师', phase: '板级方案', schema: { ...R, required: ['status', 'summary', 'blocks'], properties: { ...R.properties, blocks: { type: 'array', items: { type: 'string' } } } } })
  if (!arch) return { status: 'stopped', done: [] }
  if (arch.status === 'needs_input') return { status: 'needs_input', questions: arch.questions || [], summary: arch.summary, done: [] }
  const done = [{ stage: '架构师', summary: arch.summary }]
  phase('设计')
  const built = await parallel((arch.blocks || []).map(id => () => agent(`${common}

你是功能块 ${id} 的设计者，只做这一块。${read}
先读设计目录的 设计资料/需求基线.md、设计资料/板级方案.md 和 record/architecture.json，再照“块设计者”一节做：写 record/blocks/${id}.json 和 设计资料/块设计/${id}.md。
别的块同时有人在做：不改别的块的文件，不改 architecture.json 和板级方案；需要别的块配合的写进本块报告的“对其他块的要求”。项目符号写进 设计目录/symbols/${id}.kicad_sym（每块自己的库文件，免得并行写冲突）。
返回 status 和 summary（核心器件、余量最小的两项、对其他块的要求、未核实项）。`,
    { label: `块 ${id}`, phase: '设计', schema: R }).then(r => ({ id, r }))))
  for (const b of built.filter(Boolean)) done.push({ stage: `块 ${b.id}`, summary: b.r ? b.r.summary : '没有返回结果' })
  const missing = (arch.blocks || []).filter(id => !built.some(b => b && b.id === id && b.r))
  phase('整板核对')
  const whole = await agent(`${common}

你是整板核对者。${read}
架构师和各块设计者的产出已在设计目录（设计资料/板级方案.md、设计资料/块设计/、record/blocks/、record/architecture.json）。照“整板核对者”一节做：合并、走查、做减法、写 设计目录/设计报告.md，合并通过后 record/electrical-intent.json 就是设计网表。各块的项目符号在 设计目录/symbols/ 下，按需合成一个库。
${missing.length ? `这些块的设计者没有交出结果，由你补做：${missing.join('、')}。\n` : ''}返回 status 和 summary（器件数、合并时改了什么、走查发现并改掉的问题、减掉的器件、余量最小的三项、未核实项）。`,
    { label: '整板核对', phase: '整板核对', schema: R })
  if (!whole) return { status: 'stopped', done }
  done.push({ stage: '整板核对', summary: whole.summary })
  if (whole.status === 'needs_input') return { status: 'needs_input', questions: whole.questions || [], summary: whole.summary, done }
  phase('原理图')
  const g = await agent(`${common}

你是绘图者。读 ${QD} 的“绘图者做什么”并照它做：设计网表在设计目录的 record/electrical-intent.json，设计报告在 设计目录/设计报告.md。器件多，按功能分页。
画完并通过自动检查后，把交付目录按该节写齐（设计报告.md、设计方案/、设计资料/（需求基线.md、板级方案.md、块设计/）、record/），并在设计报告的“自检结果”里填上 ERC、网表比对和图面检查的结果。
返回 status 和 summary（页数、ERC 违规数、网表是否逐脚一致、summary.json 里各检查项的结果、改过设计网表的地方）。`,
    { label: '绘图与自检', phase: '原理图', schema: R })
  done.push({ stage: '绘图与自检', summary: g ? g.summary : '绘图没有返回结果' })
  return { status: g && g.status === 'done' ? 'complete' : 'blocked', mode: 'blocks', workdir: a.workdir, delivery: a.delivery, report: `${a.delivery}/设计报告.md`, done }
}
