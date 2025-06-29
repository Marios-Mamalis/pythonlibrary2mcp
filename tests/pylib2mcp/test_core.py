import pytest
from core import import_function_from_module


class TestImportFunctionFromModule:

    def test_import_function_of_built_in_library(self):
        import math

        assert (
            import_function_from_module(module_name="math", func_name="sqrt")
            == math.sqrt
        ), "Import of built-in library function failed."

    def test_import_external_library(self):
        from _pytest.config import filename_arg

        assert (
            import_function_from_module(
                module_name="_pytest.config", func_name="filename_arg"
            )
            == filename_arg
        ), "Import of built-in library function failed."

    def test_raise_function_name_not_found_in_library(self):
        with pytest.raises(AttributeError):
            import_function_from_module(module_name="math", func_name="sqrt1")

    def test_raise_library_not_found(self):
        with pytest.raises(ModuleNotFoundError):
            import_function_from_module(module_name="math1", func_name="sqrt")
