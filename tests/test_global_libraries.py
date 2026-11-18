"""User 2026-11-13 (AD9361 board): symbols come from the user's global library (Hardware-Library) by nickname; a
project keeps only a frozen copy in 库快照/, whose rows in sym-lib-table are not schematic evidence."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from schematic_layout import generate  # noqa: E402

LIB = '(kicad_symbol_lib (version 20241209) (generator "t") (symbol "User__X" (property "Reference" "U" (at 0 0 0)) ' \
      '(symbol "User__X_1_1" (pin passive line (at 0 0 0) (length 2.54) (name "A") (number "1")))))\n'


class GlobalLibraryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        generate.global_symbol_dirs.cache_clear()
        self.addCleanup(generate.global_symbol_dirs.cache_clear)

    def test_a_library_in_the_global_table_is_found_by_nickname(self):
        lib = self.base / 'HW' / 'symbols'
        lib.mkdir(parents=True)
        (lib / 'Hardware-Library.kicad_sym').write_text(LIB)
        config = self.base / 'config' / '10.0'  # KiCad reads KICAD_CONFIG_HOME/<major.minor>
        config.mkdir(parents=True)
        (config / 'sym-lib-table').write_text(
            '(sym_lib_table\n (version 7)\n'
            ' (lib (name "KiCad") (type "Table") (uri "/nowhere/sym-lib-table") (options "") (descr ""))\n'
            ' (lib (name "Hardware-Library") (type "KiCad") (uri "${HW_LIB_ROOT}/symbols/Hardware-Library.kicad_sym") (options "") (descr ""))\n)\n')
        (config / 'kicad_common.json').write_text(json.dumps({'environment': {'vars': {'HW_LIB_ROOT': str(self.base / 'HW')}}}))
        with mock.patch.dict(os.environ, {'KICAD_CONFIG_HOME': str(config.parent)}), \
                mock.patch.object(generate, 'kicad_version', return_value='10.0'):
            self.assertEqual((str(lib),), generate.global_symbol_dirs())
            libraries = generate.Libraries(generate.library_dirs())
            libraries.load('Hardware-Library:User__X')
            self.assertEqual((lib / 'Hardware-Library.kicad_sym').resolve(), Path(libraries.sources['Hardware-Library']['path']))

    def test_no_global_table_adds_nothing(self):
        with mock.patch.dict(os.environ, {'KICAD_CONFIG_HOME': str(self.base / 'missing')}):
            self.assertEqual((), generate.global_symbol_dirs())


if __name__ == '__main__':
    unittest.main()
