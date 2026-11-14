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
本模块做完的标志以细则为准，关卡命令自己先跑到通过。
需要人确认或答复的地方（需求澄清、选型确认、设计未定项的决定）：任务书里有答复或代答授权的按任务书办；没有的不要自己替人决定，返回 needs_input，把问题写进 questions（每条写清要定什么、有哪些选项、你的建议和依据）。
${fromDown ? `下游模块做不下去，指出本模块的产出有错或不够（本模块自己的关卡通过不等于下游够用）：\n${fromDown}\n本轮先按这些改本模块的产出，改完重跑本模块关卡。认为某条不该由本模块改的，在 summary 里逐条写明理由。\n` : ''}${feedback ? `上一轮关卡没过，原因：\n${feedback}\n先处置这些再继续。\n` : ''}
返回：status 为 done（本模块全部做完且自查关卡通过）、partial（工作量大，本轮做了一部分，进度已写进设计目录，下一轮接着做；C4 可以一轮做一块）、needs_input 或 upstream。summary 写本轮做了什么、还剩什么。`
}
function gatePrompt(s) {
  return `${common}

你是关卡检查员，不是设计者：不写、不改设计目录和交付目录里的任何设计产物，不替设计者补内容。读 ${SKILL}/SKILL.md 的“主流程”模块表和 references/${s.file}，找出 ${s.id} 做完的标志和关卡命令，在设计目录（交付阶段在交付目录）上实际运行这些命令，并核对本模块应有的产出文件都在。
返回 passed（关卡命令全部通过且产出齐全才为 true）和 details（跑了哪些命令、各自的结果；没过时逐条列出错误原文，够设计者照着改）。`
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
for (let i = from - 1; i < STAGES.length; i++) {
  const s = STAGES[i]
  phase(s.title)
  let feedback = '', passed = false, back = 0
  const fromDown = carry
  carry = ''
  for (let round = 1; round <= s.rounds; round++) {
    const w = await agent(workPrompt(s, feedback, fromDown), { label: `${s.id}${fromDown ? ' 回改' : ''} 第${round}轮`, phase: s.title, schema: WORK })
    if (!w) return { status: 'stopped', stage: s.n, done }
    if (w.status === 'needs_input') return { status: 'needs_input', stage: s.n, questions: w.questions || [], summary: w.summary, done }
    if (w.status === 'upstream') { back = w.upstream_stage || s.n - 1; feedback = w.summary; break }
    if (w.status === 'partial') { log(`${s.id} 未完，继续：${w.summary}`); feedback = ''; continue }
    const g = await agent(gatePrompt(s), { label: `${s.id} 关卡`, phase: s.title, schema: GATE, effort: 'low' })
    if (g && g.passed) { passed = true; done.push({ stage: s.id, summary: w.summary }); break }
    feedback = g ? g.details : '关卡检查没有返回结果'
    log(`${s.id} 关卡未过，返回本模块处置`)
  }
  if (back) {
    if (back >= s.n || ++backtracks > 3) return { status: 'blocked', stage: s.n, reason: `需要回到上游但无法继续：${feedback}`, done }
    log(`${s.id} 发现上游问题，回到第 ${back} 个阶段：${feedback}`)
    carry = feedback
    i = back - 2
    continue
  }
  if (!passed) return { status: 'blocked', stage: s.n, reason: feedback || '本模块在限定轮数内没有做完', done }
}
return { status: 'complete', workdir: a.workdir, delivery: a.delivery, report: `${a.delivery}/设计报告.md`, done }
