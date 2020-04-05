import unittest
from unittest import TestCase
import builtins
import importlib


class TestMatrixNioModuleImports(TestCase):
    def test_import_error_asyncio(self):
        real_import = builtins.__import__

        def my_import(name, globals, locals, fromlist, level):
            if name == "asyncio":
                raise ImportError
            return real_import(name, globals, locals, fromlist, level)

        builtins.__import__ = my_import
        with self.assertRaises(ImportError):
            import matrix_nio
            importlib.reload(matrix_nio)

    def test_import_error_asyncio(self):
        real_import = builtins.__import__

        def my_import(name, globals, locals, fromlist, level):
            if name == "nio":
                raise ImportError
            return real_import(name, globals, locals, fromlist, level)

        builtins.__import__ = my_import
        with self.assertRaises(ImportError):
            import matrix_nio
            importlib.reload(matrix_nio)


if __name__ == '__main__':
    unittest.main()
