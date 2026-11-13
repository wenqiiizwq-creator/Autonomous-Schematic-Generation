"""必答清单：设计用到的知识条目逐项要处置；C1、C4 关卡核对没有漏项、落实处指向存在的记录。"""
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import knowledge_checklist as k
import knowledge_source

REQUIREMENT = '''# 口

## 来源

| 条件 | 文件 |
|---|---|
| S1 | a.pdf |

## 各种用途都要问的

| 条件 | 决定什么 |
|---|---|
| 端口用途，见 [别的条目](../x.md) | 套哪组准则 |
| 线缆是否穿出外壳 | 静电等级 |

## 缺了会怎样

| 缺的 | 后果 |
|---|---|
| 用途 | 定不下来 |
'''
CIRCUIT = '''# 稳压

## 实现方案

### 方案甲

- **适用范围**：低压
- **必需外围**：
  - 输出电容
- **必算项**：
  - 压差，见 [线性稳压器](../../计算方法/电源变换/线性稳压器.md)
  - 功耗
- **已知坑**：无
### 方案乙

- **必算项**：电流
- **已知坑**：
  - 反灌
'''
METHOD = '''# 算

## 取值顺序

| 步 | 定什么 | 算式 |
|---|---|---|
| 1 | 最低输入 | a |
| 2 | 功耗 | b |

## 算完之后的核对

- 调整区：G03-034。
'''


def test_items_are_drawn_from_the_entry_text():
    assert k.requirement_items(REQUIREMENT) == [('条件', '端口用途，见 别的条目'), ('条件', '线缆是否穿出外壳')]
    assert k.scheme_items(CIRCUIT, '方案甲') == [('必需外围', '输出电容'), ('必算项', '压差，见 线性稳压器'), ('必算项', '功耗')]
    assert k.scheme_items(CIRCUIT, '方案乙') == [('必算项', '电流'), ('已知坑', '反灌')]
    assert k.scheme_items(CIRCUIT, '没有的方案') is None
    assert k.method_items(METHOD) == [('取值步骤', '第 1 步：最低输入'), ('取值步骤', '第 2 步：功耗'), ('算完核对', '调整区：G03-034。')]
    rows = k.keyed({'entry': 'x.md'}, [('必算项', '功耗'), ('必算项', '功耗'), ('已知坑', '功耗')])
    assert len({r['id'] for r in rows}) == 3 and rows[1]['id'] == rows[0]['id'] + '-2'


@pytest.fixture
def design(tmp_path, monkeypatch):
    knowledge = tmp_path / 'knowledge'
    for name, body in (('需求要素/端口/口.md', REQUIREMENT), ('典型电路/电源变换/reg.md', CIRCUIT), ('计算方法/电源变换/算.md', METHOD)):
        (knowledge / name).parent.mkdir(parents=True, exist_ok=True)
        (knowledge / name).write_text(body, encoding='utf-8')
    monkeypatch.setattr(knowledge_source, 'knowledge_dir', lambda: knowledge)
    record = tmp_path / 'design' / 'record'
    (record / 'block-circuits').mkdir(parents=True)
    (record / 'blocks').mkdir()
    write = lambda name, data: (record / name).write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    write('modules.json', {'knowledge_lookups': [
        {'task': 'C1.1', 'component': '需求要素', 'query': '口', 'found': ['需求要素/端口/口.md']},
        {'task': 'C4.2', 'component': '计算方法', 'query': '算', 'found': ['计算方法/电源变换/算.md']}]})
    write('block-circuits/PSU.json', {'schemes': [{'name': '稳压', 'selected': {'name': '甲', 'circuit': 'reg#方案甲'}}]})
    write('block-circuits/IO.json', {'schemes': [{'name': '口', 'selected': {'name': '自拟'}}]})      # no typical circuit: nothing to answer
    write('blocks/PSU.json', {'components': [{'ref': 'C101'}, {'ref': 'U101'}]})
    write('requirements.json', {'requirements': [{'id': 'REQ-001'}], 'clarifications': [{'id': 'CL-01'}]})
    write('design-closure.json', {'calculations': [{'id': 'CALC-LDO'}]})
    return record.parent


def answer(root, module, fill):
    path = root / 'record' / k.FILE
    data = json.loads(path.read_text(encoding='utf-8'))
    for row in data[module]:
        row.update(fill(row))
    path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')


def test_build_lists_every_item_and_keeps_what_was_answered(design):
    data, found = k.build(design)
    assert found == []
    assert [(r['entry'], r['kind']) for r in data['C1']] == [('需求要素/端口/口.md', '条件')] * 2
    assert [(r.get('block'), r['kind']) for r in data['C4']] == [
        ('PSU', '必需外围'), ('PSU', '必算项'), ('PSU', '必算项'), (None, '取值步骤'), (None, '取值步骤'), (None, '算完核对')]
    answer(design, 'C1', lambda row: {'disposition': 'covered', 'where': ['REQ-001']})
    again, _ = k.build(design)
    assert {r['disposition'] for r in again['C1']} == {'covered'} and {r['disposition'] for r in again['C4']} == {''}


def test_the_gate_wants_every_item_answered_with_records_that_exist(design):
    assert k.problems(design, 'C1') == ['record/knowledge-checklist.json 的 C1 缺 2 项（知识条目或选定方案变了）：重跑 knowledge_checklist.py build 后补写处置']
    k.build(design)
    assert len(k.problems(design, 'C1')) == 2 and all('还没有写处置' in p for p in k.problems(design, 'C1'))
    answer(design, 'C1', lambda row: {'disposition': 'covered', 'where': ['CL-01']} if '外壳' in row['text']
           else {'disposition': 'not_applicable', 'reason': '只有一种用途'})
    assert k.problems(design, 'C1') == []
    answer(design, 'C1', lambda row: {'where': ['REQ-999'], 'reason': ''})
    found = k.problems(design, 'C1')
    assert any('where 的 REQ-999 不是requirements.json 的需求或澄清编号' in p for p in found)
    assert any('不适用要在 reason 写理由' in p for p in found)
    answer(design, 'C4', lambda row: {'disposition': 'covered', 'where': ['C101'] if row['kind'] == '必需外围' else ['CALC-LDO']})
    assert k.problems(design, 'C4') == [] and k.problems(design, 'C4', 'PSU') == [] and k.problems(design, 'C4', 'IO') == []
    answer(design, 'C4', lambda row: {'where': ['R999']} if row['kind'] == '必需外围' else {'where': []} if row['kind'] == '算完核对' else {})
    found = k.problems(design, 'C4')
    assert any('where 的 R999 不是块设计里的位号' in p for p in found) and any('covered 要在 where 列出落实在哪' in p for p in found)
    assert len(k.problems(design, 'C4', 'PSU')) == 1          # the block gate reads only that block's scheme items


def test_a_changed_entry_voids_the_old_answer_and_a_lost_scheme_is_reported(design):
    k.build(design)
    answer(design, 'C1', lambda row: {'disposition': 'covered', 'where': ['REQ-001']})
    path = knowledge_source.knowledge_dir() / '需求要素/端口/口.md'
    path.write_text(path.read_text(encoding='utf-8').replace('线缆是否穿出外壳', '线缆是否穿出外壳或机柜'), encoding='utf-8')
    assert k.problems(design, 'C1') == ['record/knowledge-checklist.json 的 C1 缺 1 项（知识条目或选定方案变了）：重跑 knowledge_checklist.py build 后补写处置']
    block = design / 'record' / 'block-circuits' / 'PSU.json'
    block.write_text(block.read_text(encoding='utf-8').replace('方案甲', '方案丙'), encoding='utf-8')
    assert k.problems(design, 'C4') [0] == '块 PSU 选定的 reg#方案丙 在知识框架的典型电路里找不到'


def test_every_framework_entry_of_the_checked_kinds_yields_items():
    import typical_circuits
    try:
        knowledge_source.framework_root()
    except knowledge_source.KnowledgeFrameworkNotFound as exc:
        pytest.skip('没有配置知识框架：%s' % exc)
    for folder in k.REQUIREMENT_FOLDERS:
        for path in sorted((knowledge_source.knowledge_dir() / folder).glob('*.md')):
            assert path.name == 'README.md' or k.requirement_items(path.read_text(encoding='utf-8')), path.name
    for stem, info in typical_circuits.load().items():
        body = k.circuit_file(stem).read_text(encoding='utf-8')
        for name in info['implementations']:
            assert k.scheme_items(body, name), (stem, name)
