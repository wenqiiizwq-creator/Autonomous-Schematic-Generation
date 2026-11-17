export const meta = {
  name: 'asg-design',
  description: '原理图设计（ASG）：六个能力模块和交付各用新的上下文执行，每个模块的关卡通过才进下一个',
  whenToUse: '从需求做一块板的原理图设计并交出固定的交付目录；或拿审查报告对已有设计做一次改版',
  phases: [
    { title: 'C1 需求' }, { title: 'C2 板级方案' }, { title: 'C3 块电路与接口' }, { title: 'C4 详细设计' },
    { title: 'C5 全板闭合' }, { title: 'C6 原理图' }, { title: '交付' },
  ],
}

// args: {
//   workdir: 设计目录（绝对路径；状态和各模块的产出都在这里）,
//   inputs: 一段话说明需求文件在哪里，以及任务书（澄清答复、代答授权、选型确认）在哪里（没有就写没有）,
//   delivery: 交付目录的绝对路径（改版时用原来的交付目录，设计方案/ 里 PCB 环节的板子保留）,
//   review: 可选，改版时审查报告的路径（审查工作流的产出）；有它就从受影响的最上游模块重做,
//   start: 可选，从第几个阶段开始（1–7：C1…C6、交付）,
//   mode: 可选，auto（默认：小板走快速设计，器件多的板走分块设计）、quick、blocks、full（六个模块，只在点名时走）,
//   quick_limit: 可选，小板的器件数上限，默认 40,
//   skill: 可选，技能目录，默认 ~/.agents/skills/autonomous-schematic-generation
// }
const a = args || {}
if (!a.workdir || !a.inputs || !a.delivery) throw new Error('args 需要 workdir、inputs 和 delivery')
const SKILL = a.skill || '~/.agents/skills/autonomous-schematic-generation'
const STAGES = [
  { n: 1, id: 'C1', title: 'C1 需求', file: 'module-c1-requirements.md', rounds: 2 },
  { n: 2, id: 'C2', title: 'C2 板级方案', file: 'module-c2-architecture.md', rounds: 2 },
  { n: 3, id: 'C3', title: 'C3 块电路与接口', file: 'module-c3-block-circuits.md', rounds: 4 },
  { n: 4, id: 'C4', title: 'C4 详细设计', file: 'module-c4-detailed-design.md', rounds: 12 },
  { n: 5, id: 'C5', title: 'C5 全板闭合', file: 'module-c5-board-closure.md', rounds: 3 },
  { n: 6, id: 'C6', title: 'C6 原理图', file: 'module-c6-schematic.md', rounds: 8 },
  { n: 7, id: '交付', title: '交付', file: 'module-delivery.md', rounds: 3 },
]
const WORK = {
  type: 'object', required: ['status', 'summary'],
  properties: {
    status: { type: 'string', enum: ['done', 'partial', 'needs_input', 'upstream'] },
    summary: { type: 'string' },
    questions: { type: 'array', items: { type: 'string' } },
    upstream_stage: { type: 'integer' },
  },
}
const GATE = {
  type: 'object', required: ['passed', 'details'],
  properties: { passed: { type: 'boolean' }, details: { type: 'string' } },
}
const START = { type: 'object', required: ['stage', 'reason'], properties: { stage: { type: 'integer' }, reason: { type: 'string' } } }
const common = `全程中文。技能目录 ${SKILL}（只读，不改其中任何文件）。设计目录 ${a.workdir}，各模块的产出写在这里；交付目录 ${a.delivery}（顶层只有 设计报告.md、设计方案/、设计资料/、record/；设计方案/ 是原理图和 PCB 共用的标准 KiCad 工程，其中板子文件属 PCB 环节，不改不删）。
输入：${a.inputs}`

function workPrompt(s, feedback, fromDown) {
  return `${common}
${a.review ? `这是一次改版：审查报告在 ${a.review}。按 SKILL.md“选择工作流”里“收到审查意见”一行办：每条意见找到负责的模块，从该模块重做并写明原因，下游按指纹重跑。本阶段只处置落在本模块的意见和上游重做带来的变化。\n` : ''}
你只做设计流程的 ${s.id} 这一个模块。先读 ${SKILL}/SKILL.md 和本模块细则 references/${s.file}，再读细则指到的参考文件。上游模块的产出已在设计目录里；先看设计目录里已有什么，接着做，不重做已完成且有效的部分。
只做本模块：不做下游模块的事，不改上游模块的产出。发现上游产出有错或不够，返回 upstream，在 upstream_stage 写该回到第几个阶段（1–6 对应 C1–C6），summary 写清错在哪里。
本模块做完的标志以细则为准，关卡命令自己先跑到通过。关卡输出里 PENDING 开头的是提示，不挡关卡，不为它返回 upstream；只有关卡报错且错在上游产品里才返回 upstream。${s.n === 4 ? `\n计算深度与后果相称：只核需求、接口或器件额定给了限值的量，不自拟门槛；常规件（电阻、电容、指示灯、排针、端子）的应力不单列计算，规格里写出最低额定即可；辅助功能一条计算按标称值加容差核需求给的限值。器件的 lib_id 用 KiCad 库里实有的符号名，引脚写引脚号。用 make_symbol.py 做项目符号时，同名电源脚里有要悬空的加 --no-stack。` : ''}${s.n === 6 ? `\n整板不超过约 25 个器件、一页 A4 放得下时只画一页，不设封面。` : ''}${s.n === 7 ? `\n交付用 deliver.py <交付目录> --design ${a.workdir} 跑：它先把设计目录的 record/ 和 设计资料/ 同步进交付目录，每次重跑都带 --design，不手工复制、不拿交付目录里的旧副本判。停在“图面审阅 PENDING”时按提示看这次导出的 PDF 写 visual-review.json（写在设计目录的 record/ 里）再重跑，这一步属于交付，不返回 upstream。` : ''}
需要人确认或答复的地方（需求澄清、选型确认、设计未定项的决定）：任务书里有答复或代答授权的按任务书办；没有的不要自己替人决定，返回 needs_input，把问题写进 questions（每条写清要定什么、有哪些选项、你的建议和依据）。
${s.n > 1 && s.n < 7 ? `需求条文有歧义、互相冲突或按现有电路做不到时，不在本模块停下问人，也不自己取一种读法：需求澄清记在 C1 的产品里，返回 upstream、upstream_stage 写 1，summary 写清是哪条条文、各种读法或改法的后果、你建议的条文和依据。做不到或要加器件、换方案才做得到的若是由澄清采纳成的条文（不是需求原文），建议写放宽这条条文，不先换方案或加器件。C1 登记这条澄清后按任务书的答复或代答授权处置，任务书管不到的由 C1 返回 needs_input。\n` : ''}${s.n === 1 ? `C1 的建议条文不替用户加严：需求没写的工况取与原文相容的最宽松读法；需求没给的门限、延时、精度和持续时间写成取所选器件的保证值，不把需求的容差边界当动作门限；下游报自拟的条文做不到时先放宽条文；需求没要求而你认为值得做的保护和裕量列为可选项并附代价，不写进建议条文，代答授权不采纳可选项；答哪一种都不改图的不建澄清。必答清单只问本板声明了的适用前提（清单顶层 applies）；需求没有要求、本设计不做的条件写 not_required 加一句理由，不建澄清（references/knowledge-package.md“必答清单”）。\n` : ''}${s.n === 4 ? `常规件默认按标准规格，不写性能记录；只有计算拿它标称值以外的参数当输入、且常用料不一定满足时才在 component-requirements.json 写记录，记录里只列计算实际用到的参数，screening 和 required_parameters 不用写。\n` : ''}${s.n === 4 ? `C4 一块一块做：写完一块的块设计、计算和必答清单处置，就用 check_module.py C4 <设计目录> --block <块> 跑到通过，再写下一块；不要等全部块写完才第一次跑关卡。全部块通过后再跑不带 --block 的全板关卡。块多或上下文吃紧时，做完一块返回 partial。\n` : ''}${fromDown ? `下游模块做不下去，指出本模块的产出有错或不够（本模块自己的关卡通过不等于下游够用）：\n${fromDown}\n本轮先按这些改本模块的产出，改完重跑本模块关卡。认为某条不该由本模块改的，在 summary 里逐条写明理由。\n` : ''}${feedback ? `上一轮关卡没过，原因：\n${feedback}\n先处置这些再继续。\n` : ''}
返回：status 为 done（本模块全部做完且自查关卡通过）、partial（工作量大，本轮做了一部分，进度已写进设计目录，下一轮接着做；C4 可以一轮做一块）、needs_input 或 upstream。summary 写本轮做了什么、还剩什么。`
}
function gatePrompt(s) {
  return `${common}

你是关卡检查员，不是设计者：不写、不改设计目录和交付目录里的任何设计产物，不替设计者补内容。读 ${SKILL}/SKILL.md 的“主流程”模块表和 references/${s.file}，找出 ${s.id} 做完的标志和关卡命令，在${s.n === 7 ? '交付目录' : '设计目录'}上实际运行这些命令，并核对本模块应有的产出文件都在。${s.n === 7 ? '' : '只在设计目录上判：交付目录到交付阶段才同步，里面的记录可能是旧副本，不在它上面跑关卡，也不拿它的结果判。'}
返回 passed（关卡命令全部通过且产出齐全才为 true）和 details（跑了哪些命令、各自的结果；没过时逐条列出错误原文，够设计者照着改）。`
}

// 小板快速设计：一位设计者从需求做到设计网表和设计报告，一位绘图者画图并跑自动检查；不走六个模块的记录与关卡。
// H-001 2026-11-16：13 个器件的板走六个模块 68～82 分钟、约 300 万 token，不带技能直接设计约 20 分钟。
let mode = a.mode || 'auto'
if (mode === 'auto' && !a.start && !a.review) {
  const size = await agent(`${common}\n\n只做一件事：读需求，判断这块板是不是小板——预计器件不超过约 ${a.quick_limit || 40} 个位号、单一电压域、没有隔离与安规要求、没有高速接口。返回 small（是否小板）和 reason（一句话）。不写任何文件。`,
    { label: '判规模', phase: 'C1 需求', schema: { type: 'object', required: ['small', 'reason'], properties: { small: { type: 'boolean' }, reason: { type: 'string' } } }, effort: 'low', model: 'sonnet' })
  mode = size && size.small ? 'quick' : 'blocks'
  log(`${mode === 'quick' ? '小板，走快速设计' : '器件多，走分块设计'}：${size ? size.reason : '没有判出规模'}`)
} else if (mode === 'auto') mode = 'full'
if (mode === 'quick') {
  const QUICK = { type: 'object', required: ['status', 'summary'], properties: {
    status: { type: 'string', enum: ['done', 'needs_input'] }, summary: { type: 'string' }, questions: { type: 'array', items: { type: 'string' } } } }
  phase('C4 详细设计')
  const d = await agent(`${common}

你是这块板的设计者，做小板快速设计。读 ${SKILL}/SKILL.md 的「ASG 纲要（核心标准）」一节和 ${SKILL}/references/quick-design.md，照“设计者做什么”做完第 1 到第 7 步；只读细则点到、且你确实要用的参考文件，不通读其他模块细则。
知识框架目录见 ${SKILL}/.knowledge-framework。产出写在设计目录：设计资料/需求基线.md、record/electrical-intent.json、设计报告.md。
需要人确认的地方：任务书里有答复或代答授权的按任务书办；没有且必须人定的才返回 needs_input 并把问题写进 questions。
返回 status 和 summary（方案一句话、器件数、采纳了哪几条澄清、余量最小的三项、未核实项）。`,
    { label: '快速设计', phase: 'C4 详细设计', schema: QUICK })
  if (!d) return { status: 'stopped', stage: 4, done: [] }
  if (d.status === 'needs_input') return { status: 'needs_input', stage: 4, questions: d.questions || [], summary: d.summary, done: [] }
  phase('C6 原理图')
  const g = await agent(`${common}

你是绘图者。读 ${SKILL}/references/quick-design.md 的“绘图者做什么”并照它做：设计网表在设计目录的 record/electrical-intent.json，设计报告在 设计目录/设计报告.md。
画完并通过自动检查后，把交付目录按该节写齐（设计报告.md、设计方案/、设计资料/需求基线.md、record/），并在设计报告的“自检结果”里填上 ERC、网表比对和图面检查的结果。
返回 status 和 summary（页数、ERC 违规数、网表是否逐脚一致、summary.json 里各检查项的结果、改过设计网表的地方）。`,
    { label: '绘图与自检', phase: 'C6 原理图', schema: QUICK })
  return { status: g && g.status === 'done' ? 'complete' : 'blocked', mode: 'quick', workdir: a.workdir, delivery: a.delivery, report: `${a.delivery}/设计报告.md`,
    done: [{ stage: '快速设计', summary: d.summary }, { stage: '绘图与自检', summary: g ? g.summary : '绘图没有返回结果' }] }
}

// 分块设计：器件多的板。架构师定板级方案，各功能块并行设计，整板核对者合并并走查，绘图者画图；不设接口定稿，不逐级回退。
// M-001 2026-11-17：约 100 个器件的控制板走六个模块约 8 小时、回退 14 次，独立审查指出 1 条 P0、4 条 P1；直接设计 41 分钟、1 条 P1。
if (mode === 'blocks') {
  const R = { type: 'object', required: ['status', 'summary'], properties: {
    status: { type: 'string', enum: ['done', 'needs_input'] }, summary: { type: 'string' }, questions: { type: 'array', items: { type: 'string' } } } }
  const QD = `${SKILL}/references/quick-design.md`
  const read = `读 ${SKILL}/SKILL.md 的「ASG 纲要（核心标准）」一节和 ${QD}（“设计者做什么”和“分块设计”两节）；只读细则点到、且你确实要用的参考文件，不通读各模块细则，不跑 check_module.py。知识框架目录见 ${SKILL}/.knowledge-framework。`
  phase('C2 板级方案')
  const arch = await agent(`${common}

你是这块板的架构师。${read}
照“架构师”一节做：写 设计资料/需求基线.md、设计资料/板级方案.md 和 record/architecture.json。
需要人确认的地方：任务书里有答复或代答授权的按任务书办；没有且必须人定的才返回 needs_input 并把问题写进 questions。
返回 status、summary（电源树一句话、采纳的澄清、每颗保护或切换芯片对应哪条需求、引脚余量）和 blocks（功能块的 id 列表，与 architecture.json 一致）。`,
    { label: '架构师', phase: 'C2 板级方案', schema: { ...R, required: ['status', 'summary', 'blocks'], properties: { ...R.properties, blocks: { type: 'array', items: { type: 'string' } } } } })
  if (!arch) return { status: 'stopped', stage: 2, done: [] }
  if (arch.status === 'needs_input') return { status: 'needs_input', stage: 2, questions: arch.questions || [], summary: arch.summary, done: [] }
  const done = [{ stage: '架构师', summary: arch.summary }]
  phase('C4 详细设计')
  const built = await parallel((arch.blocks || []).map(id => () => agent(`${common}

你是功能块 ${id} 的设计者，只做这一块。${read}
先读设计目录的 设计资料/需求基线.md、设计资料/板级方案.md 和 record/architecture.json，再照“块设计者”一节做：写 record/blocks/${id}.json 和 设计资料/块设计/${id}.md。
别的块同时有人在做：不改别的块的文件，不改 architecture.json 和板级方案；需要别的块配合的写进本块报告的“对其他块的要求”。项目符号写进 设计目录/symbols/${id}.kicad_sym（每块自己的库文件，免得并行写冲突）。
返回 status 和 summary（核心器件、余量最小的两项、对其他块的要求、未核实项）。`,
    { label: `块 ${id}`, phase: 'C4 详细设计', schema: R }).then(r => ({ id, r }))))
  for (const b of built.filter(Boolean)) done.push({ stage: `块 ${b.id}`, summary: b.r ? b.r.summary : '没有返回结果' })
  const missing = (arch.blocks || []).filter(id => !built.some(b => b && b.id === id && b.r))
  phase('C5 全板闭合')
  const whole = await agent(`${common}

你是整板核对者。${read}
架构师和各块设计者的产出已在设计目录（设计资料/板级方案.md、设计资料/块设计/、record/blocks/、record/architecture.json）。照“整板核对者”一节做：合并、走查、做减法、写 设计目录/设计报告.md，合并通过后 record/electrical-intent.json 就是设计网表。各块的项目符号在 设计目录/symbols/ 下，按需合成一个库。
${missing.length ? `这些块的设计者没有交出结果，由你补做：${missing.join('、')}。\n` : ''}返回 status 和 summary（器件数、合并时改了什么、走查发现并改掉的问题、减掉的器件、余量最小的三项、未核实项）。`,
    { label: '整板核对', phase: 'C5 全板闭合', schema: R })
  if (!whole) return { status: 'stopped', stage: 5, done }
  done.push({ stage: '整板核对', summary: whole.summary })
  if (whole.status === 'needs_input') return { status: 'needs_input', stage: 5, questions: whole.questions || [], summary: whole.summary, done }
  phase('C6 原理图')
  const g = await agent(`${common}

你是绘图者。读 ${QD} 的“绘图者做什么”并照它做：设计网表在设计目录的 record/electrical-intent.json，设计报告在 设计目录/设计报告.md。器件多，按功能分页。
画完并通过自动检查后，把交付目录按该节写齐（设计报告.md、设计方案/、设计资料/（需求基线.md、板级方案.md、块设计/）、record/），并在设计报告的“自检结果”里填上 ERC、网表比对和图面检查的结果。
返回 status 和 summary（页数、ERC 违规数、网表是否逐脚一致、summary.json 里各检查项的结果、改过设计网表的地方）。`,
    { label: '绘图与自检', phase: 'C6 原理图', schema: R })
  done.push({ stage: '绘图与自检', summary: g ? g.summary : '绘图没有返回结果' })
  return { status: g && g.status === 'done' ? 'complete' : 'blocked', mode: 'blocks', workdir: a.workdir, delivery: a.delivery, report: `${a.delivery}/设计报告.md`, done }
}

let from = a.start || 1
if (a.review && !a.start) {
  phase('C1 需求')
  const st = await agent(`${common}

审查报告在 ${a.review}。读 ${SKILL}/SKILL.md 的“选择工作流”和 references/modules.md，再读审查报告的每条意见，判断各条意见落在哪个模块。不改任何文件。返回 stage：受影响的最上游模块是第几个阶段（1–6 对应 C1–C6），reason：每条意见归到哪个模块、为什么。`,
    { label: '定改版起点', phase: 'C1 需求', schema: START })
  if (!st) return { status: 'stopped', done: [] }
  from = Math.min(Math.max(st.stage, 1), 6)
  log(`改版从第 ${from} 个阶段开始：${st.reason}`)
}

const done = []
let backtracks = 0, carry = ''
const pairs = {}
const finished = {}
for (let i = from - 1; i < STAGES.length; i++) {
  const s = STAGES[i]
  phase(s.title)
  let feedback = '', passed = false, back = 0
  const fromDown = carry
  carry = ''
  // 回过上游之后再走到已经做完的模块：先只跑关卡（低一档模型），过了就不再开设计子任务重读一遍细则。
  if (!fromDown && finished[s.id]) {
    const g0 = await agent(gatePrompt(s), { label: `${s.id} 复核关卡`, phase: s.title, schema: GATE, effort: 'low', model: 'sonnet' })
    if (g0 && g0.passed) { log(`${s.id} 上游改动后关卡仍通过，不重做`); continue }
    feedback = g0 ? g0.details : ''
  }
  for (let round = 1; round <= s.rounds; round++) {
    const w = await agent(workPrompt(s, feedback, fromDown), { label: `${s.id}${fromDown ? ' 回改' : ''} 第${round}轮`, phase: s.title, schema: WORK })
    if (!w) return { status: 'stopped', stage: s.n, done }
    if (w.status === 'needs_input') return { status: 'needs_input', stage: s.n, questions: w.questions || [], summary: w.summary, done }
    if (w.status === 'upstream') { back = w.upstream_stage || s.n - 1; feedback = w.summary; break }
    if (w.status === 'partial') { log(`${s.id} 未完，继续：${w.summary}`); feedback = ''; continue }
    const g = await agent(gatePrompt(s), { label: `${s.id} 关卡`, phase: s.title, schema: GATE, effort: 'low', model: 'sonnet' })
    if (g && g.passed) { passed = true; finished[s.id] = true; done.push({ stage: s.id, summary: w.summary }); break }
    feedback = g ? g.details : '关卡检查没有返回结果'
    log(`${s.id} 关卡未过，返回本模块处置`)
  }
  if (back) {
    // 同一对“从哪回到哪”超过 3 次才算原地打转；总数另设上限。条文澄清这类回退每次内容不同，不该两三次就停。
    const pair = `${s.n}>${back}`
    pairs[pair] = (pairs[pair] || 0) + 1
    if (back >= s.n || pairs[pair] > 3 || ++backtracks > 8) return { status: 'blocked', stage: s.n, reason: `需要回到上游但无法继续：${feedback}`, done }
    log(`${s.id} 发现上游问题，回到第 ${back} 个阶段：${feedback}`)
    carry = feedback
    i = back - 2
    continue
  }
  if (!passed) return { status: 'blocked', stage: s.n, reason: feedback || '本模块在限定轮数内没有做完', done }
}
return { status: 'complete', workdir: a.workdir, delivery: a.delivery, report: `${a.delivery}/设计报告.md`, done }
