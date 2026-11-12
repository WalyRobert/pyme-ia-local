import ast
import os
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).with_name('app.py')

class TemporaryPdfTests(unittest.TestCase):
    def check_reader(self, fail: bool) -> None:
        namespace = {'os': os, 'tempfile': tempfile, 'Document': object}
        seen = []
        class Loader:
            def __init__(self, path: str) -> None:
                self.path = path
            def load(self) -> list:
                seen.append(self.path)
                assert Path(self.path).read_bytes() == b'%PDF-test'
                if fail:
                    raise ValueError('PDF invalido')
                return []
        namespace['PyPDFLoader'] = Loader
        tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
        reader = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'read_pdf')
        exec(compile(ast.Module(body=[reader], type_ignores=[]), str(SOURCE), 'exec'), namespace)
        if fail:
            with self.assertRaises(ValueError):
                namespace['read_pdf'](b'%PDF-test')
        else:
            self.assertEqual(namespace['read_pdf'](b'%PDF-test'), [])
        self.assertEqual(len(seen), 1)
        self.assertFalse(Path(seen[0]).exists())

    def test_delete_after_success(self) -> None:
        self.check_reader(False)

    def test_delete_after_failure(self) -> None:
        self.check_reader(True)

if __name__ == '__main__':
    unittest.main()
