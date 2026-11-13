"""受控修改词表，证明消费者读取；默认分类字段与原行为另由原有回归覆盖。"""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import knowledge_source


def run(code):
    subprocess.run([sys.executable, '-B', '-c', code], cwd=ROOT, check=True, capture_output=True, text=True)


def test_titles_are_consumed_from_the_framework_vocabulary(tmp_path):
    vocabulary = json.loads(knowledge_source.vocabulary_path().read_text(encoding='utf-8'))
    vocabulary['device_kinds'][0]['title'] = '受控继电器标题'
    vocabulary['circuit_types'][0]['title'] = '受控变换器标题'
    path = tmp_path / 'vocabulary.json'
    path.write_text(json.dumps(vocabulary))
    run("import sys; sys.path.insert(0, 'scripts'); import knowledge_source as ks; "
        + "ks.vocabulary_path = lambda: __import__('pathlib').Path(%r); " % str(path)
        + "from schematic_layout import part_classes as pc; assert pc.KINDS['relay'].title == '受控继电器标题'; assert pc.KINDS['mechanical'].title == '机械件'; assert pc.kind_of({'ref':'K1','lib_id':'Relay:G5V','fields':{}})[0] == 'relay'")
