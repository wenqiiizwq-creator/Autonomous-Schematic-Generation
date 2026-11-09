"""Key functional blocks name a typical circuit and approach, or none; a none block's scheme comparison covers the library hits."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import render_design_report as report


def library(tmp_path):
    circuits = tmp_path / 'references/typical-circuits'; circuits.mkdir(parents=True)
    (circuits / 'multi-domain-reset.md').write_text('# 多域复位监督\n功能：MCU 复位与网络复位分域\n## 实现方案\n### 每域一颗监督器\n')
    (circuits / 'ldo.md').write_text('# 线性稳压\n功能：LDO 稳压\n## 实现方案\n### 固定输出\n')
    return circuits


def test_a_key_block_must_be_marked(tmp_path):
    circuits = library(tmp_path)
    blocks = {'关键': ['U1'], '常规': ['R1']}
    errors = report.check_block_circuits('a.kicad_sch', blocks, {}, {}, key_blocks=['关键'], circuits_dir=circuits)
    assert len(errors) == 1 and '关键' in errors[0] and 'none' in errors[0]
    assert report.check_block_circuits('a.kicad_sch', blocks, {'常规': 'bad#x'}, {}, circuits_dir=circuits)


def test_scheme_blocks_are_key_even_without_page_key_declaration():
    plan = {'schema_version': 1, 'pages': [{'file': 'a.kicad_sch', 'reader_tasks': ['跟随电源'],
            'blocks': {'关键': ['U1'], '常规': ['R1']}}]}
    intent = {'components': [{'ref': 'U1'}, {'ref': 'R1'}]}
    visual = {'pages': [{'file': 'a.kicad_sch', 'paths': ['电源路径']}]}
    problems = report.check_page_plan(plan, intent, visual, scheme={'blocks': [{'block': '关键'}]})
    assert len(problems) == 1 and '关键' in problems[0]


# A5 (whole-board baseline 2026-11-07): Matrix said its reset block U702 had no typical circuit while
# multi-domain-reset covers MCU reset split from network reset.
def test_a_none_block_compares_each_typical_circuit_the_search_finds(tmp_path):
    circuits = library(tmp_path)
    assert report.library_hits('复位', circuits) == ['multi-domain-reset']
    blocks = {'复位': ['U702']}
    errors = report.check_block_circuits('a.kicad_sch', blocks, {'复位': 'none'}, {}, key_blocks=['复位'], circuits_dir=circuits)
    assert len(errors) == 1 and 'multi-domain-reset' in errors[0]
    scheme = {'blocks': [{'block': '复位', 'candidates': [
        {'name': '单监督器', 'status': 'selected'},
        {'name': 'multi-domain-reset', 'status': 'rejected', 'reason': '本板只有 MCU 一个复位域'}]}]}
    assert report.check_block_circuits('a.kicad_sch', blocks, {'复位': 'none'}, {}, key_blocks=['复位'],
                                       scheme=scheme, circuits_dir=circuits) == []


def test_a_none_block_with_no_hit_passes(tmp_path):
    circuits = library(tmp_path)
    assert report.library_hits('看门狗', circuits) == []
    assert report.check_block_circuits('a.kicad_sch', {'看门狗': ['U9']}, {'看门狗': 'none'}, {},
                                       key_blocks=['看门狗'], circuits_dir=circuits) == []
