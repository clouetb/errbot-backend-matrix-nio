import unittest
import sys
import importlib
import asyncio
import nio


class TestImports(unittest.TestCase):
    def test_import_asyncio_error(self):
        module_svg = sys.modules["asyncio"]
        sys.modules["asyncio"] = None
        with self.assertRaises(SystemExit):
            import matrix_nio
        sys.modules["asyncio"] = module_svg

    def test_import_nio_error(self):
        module_svg = sys.modules["nio"]
        sys.modules["nio"] = None
        with self.assertRaises(SystemExit):
            import matrix_nio
        sys.modules["nio"] = module_svg


if __name__ == '__main__':
    unittest.main()
