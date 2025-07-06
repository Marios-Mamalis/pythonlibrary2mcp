import pytest
from pylib2mcp.cli import *


class TestParseLibraryFunctions:
    def test_1_lib_1_func(self):
        assert parse_library_functions(["lib1:func1"]) == {"lib1": ["func1"]}

    def test_1_lib_2_func(self):
        assert parse_library_functions(["lib1:func1,func2"]) == {"lib1": ["func1", "func2"]}

    def test_1_lib_no_func(self):
        assert parse_library_functions(["lib1"]) == {"lib1": None}

    def test_3_lib_one_of_each_type(self):
        assert parse_library_functions(["lib1:func1", "lib2:func2,func3", "lib3"]) == {"lib1": ["func1"], "lib2": ["func2", "func3"], "lib3": None}
