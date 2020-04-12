import unittest
import sys
import importlib


class TestImports(unittest.TestCase):
    def test_import_asyncio_error(self):
        import matrix_nio
        module_svg = sys.modules["asyncio"]
        sys.modules["asyncio"] = None
        with self.assertRaises(SystemExit):
            importlib.reload(matrix_nio)
        sys.modules["asyncio"] = module_svg

    def test_import_nio_error(self):
        import matrix_nio
        module_svg = sys.modules["nio"]
        sys.modules["nio"] = None
        with self.assertRaises(SystemExit):
            importlib.reload(matrix_nio)
        sys.modules["nio"] = module_svg


if __name__ == '__main__':
    unittest.main()
