import pytest
from fastmcp import FastMCP
import inspect
import asyncio
from pylib2mcp.core import *


class TestImportFunctionFromModule:

    def test_import_function_of_built_in_library(self):
        import math

        assert import_function_from_module(module_name="math", func_name="sqrt") == math.sqrt, "Import of built-in library function failed."

    def test_import_external_library(self):
        from _pytest.config import filename_arg

        assert import_function_from_module(module_name="_pytest.config", func_name="filename_arg") == filename_arg, "Import of built-in library function failed."

    def test_raise_function_name_not_found_in_library(self):
        with pytest.raises(AttributeError):
            import_function_from_module(module_name="math", func_name="sqrt1")

    def test_raise_library_not_found(self):
        with pytest.raises(ModuleNotFoundError):
            import_function_from_module(module_name="math1", func_name="sqrt")


class TestDiscoverAllFunctionsOfModule:

    def test_get_function_names_for_built_in_library(self):
        assert discover_all_functions_of_module(module_name="token") == [
            "ISEOF",
            "ISNONTERMINAL",
            "ISTERMINAL",
        ], "Discovery of built-in library functions was not complete."

    def test_get_function_names_for_external_library(self):
        assert discover_all_functions_of_module(module_name="pytest") == [
            "approx",
            "console_main",
            "deprecated_call",
            "exit",
            "fail",
            "fixture",
            "freeze_includes",
            "importorskip",
            "main",
            "param",
            "raises",
            "register_assert_rewrite",
            "set_trace",
            "skip",
            "warns",
            "xfail",
            "yield_fixture",
        ], "Discovery of external library functions was not complete."


class TestWrapBuiltInFuncAsUserDefinedFunc:
    def test_zero_param_function(self):
        func = wrap_built_in_func_as_user_defined_func(input)
        assert func.__name__ == "input", "Name not copied exactly"
        assert (
            func.__doc__
            == """Read a string from standard input.  The trailing newline is stripped.

The prompt string, if given, is printed to standard output without a
trailing newline before reading input.

If the user hits EOF (*nix: Ctrl-D, Windows: Ctrl-Z+Return), raise EOFError.
On *nix systems, readline is used if available."""
        ), "Docstring not copied exactly"

        assert list(inspect.signature(input).parameters) == list(inspect.signature(func).parameters), "Parameter names not copied exactly"

    def test_one_param_function(self):
        func = wrap_built_in_func_as_user_defined_func(len)
        assert func.__name__ == "len", "Name not copied exactly"
        assert func.__doc__ == """Return the number of items in a container.""", "Docstring not copied exactly"

        assert list(inspect.signature(len).parameters) == list(inspect.signature(func).parameters), "Parameter names not copied exactly"

    def test_more_than_one_param_function(self):
        func = wrap_built_in_func_as_user_defined_func(pow)
        assert func.__name__ == "pow", "Name not copied exactly"
        assert (
            func.__doc__
            == """Equivalent to base**exp with 2 arguments or base**exp % mod with 3 arguments

Some types, such as ints, are able to use a more efficient algorithm when
invoked using the three argument form."""
        ), "Docstring not copied exactly"

        assert list(inspect.signature(pow).parameters) == list(inspect.signature(func).parameters), "Parameter names not copied exactly"


class TestAddFunctionAsMcpTool:
    @pytest.mark.asyncio
    async def test_add_user_defined_function(self):
        def f(n):
            return n + 1

        mcp = FastMCP()
        add_function_as_mcp_tool(func=f, mcp_server=mcp)
        tools = await mcp._mcp_list_tools()
        assert len(tools) == 1, "Adding user defined function as MCP tool failed"

        sample_tool_call = await mcp._call_tool("f", {"n": 5})
        assert int(sample_tool_call[0].text) == 6, "Function not working correctly."

    @pytest.mark.asyncio
    async def test_dont_add_lambda_function(self):
        f = lambda x: x

        mcp = FastMCP()
        add_function_as_mcp_tool(func=f, mcp_server=mcp)
        tools = await mcp._mcp_list_tools()
        assert len(tools) == 0, "Lambda function was not omitted"

    @pytest.mark.asyncio
    async def test_add_async_function(self):
        async def f(n):
            return n + 1

        mcp = FastMCP()
        add_function_as_mcp_tool(func=f, mcp_server=mcp)
        tools = await mcp._mcp_list_tools()
        assert len(tools) == 1, "Adding async user defined function as MCP tool failed"

        sample_tool_call = await mcp._call_tool("f", {"n": 5})
        assert int(sample_tool_call[0].text) == 6, "Function not working correctly."

    @pytest.mark.asyncio
    async def test_add_built_in_function(self):
        from xml.sax.saxutils import escape

        f = escape

        mcp = FastMCP()
        add_function_as_mcp_tool(func=f, mcp_server=mcp)
        tools = await mcp._mcp_list_tools()
        assert len(tools) == 1, "Adding built-in function as MCP tool failed"

        sample_tool_call = await mcp._call_tool("escape", {"data": "test>"})
        assert sample_tool_call[0].text == "test&gt;", "Function not working correctly."

    @pytest.mark.asyncio
    async def test_failed_import_is_not_fatal_with_warning(self):
        class UnsupportedType:
            pass

        def f(x: UnsupportedType):
            pass

        mcp = FastMCP()
        with pytest.warns(UserWarning):
            add_function_as_mcp_tool(func=f, mcp_server=mcp)


class TestCreatePylibMcp:

    def test_raise_if_wrong_library_function_dictionary_format(self):
        with pytest.raises(TypeError):
            create_pylib_mcp(libraries_and_funcs={"math": 1})

    def test_add_single_func(self):
        mcp = create_pylib_mcp(libraries_and_funcs={"math": "sqrt"})
        tools = asyncio.run(mcp._mcp_list_tools())
        tool_names = [i.name for i in tools]
        assert tool_names == ["sqrt"]

    def test_add_list_of_funcs(self):
        mcp = create_pylib_mcp(libraries_and_funcs={"math": ["sqrt", "exp"]})
        tools = asyncio.run(mcp._mcp_list_tools())
        tool_names = [i.name for i in tools]
        assert tool_names == ["sqrt", "exp"]

    def test_add_all_library_funcs(self):
        mcp = create_pylib_mcp(libraries_and_funcs={"token": None})
        tools = asyncio.run(mcp._mcp_list_tools())
        tool_names = [i.name for i in tools]
        assert tool_names == ["ISEOF", "ISNONTERMINAL", "ISTERMINAL"]

    def test_add_from_two_modules(self):
        mcp = create_pylib_mcp(libraries_and_funcs={"math": "sqrt", "token": "ISEOF"})
        tools = asyncio.run(mcp._mcp_list_tools())
        tool_names = [i.name for i in tools]
        assert tool_names == ["sqrt", "ISEOF"]

    def test_raise_empty_server(self):
        with pytest.raises(ValueError):
            create_pylib_mcp(libraries_and_funcs={})
