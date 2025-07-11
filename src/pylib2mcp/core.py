import importlib
import inspect
import asyncio
from pydantic.errors import PydanticSchemaGenerationError
from types import BuiltinFunctionType
from typing import Callable, List, Dict, Union
import warnings

from fastmcp import FastMCP
from fastmcp.tools import FunctionTool


def import_function_from_module(module_name: str, func_name: str) -> Callable:
    """
    Imports a function from a library. The library must already be installed, if external.

    :param module_name: The import name of the module to import from.
    :param func_name: Name of the function to import.
    :return: The function object from the specified module.
    """

    module = importlib.import_module(module_name)
    func = getattr(module, func_name)

    return func


def discover_all_functions_of_module(module_name: str) -> List[str]:
    """
    For a given module name, returns the names of all of its functions. The module must already be installed.

    :param module_name: The import name of the module to inspect.
    :return: A list of function names (as strings) defined in the module.
    """

    module = importlib.import_module(module_name)

    function_names = []
    for name, obj in inspect.getmembers(module):
        if inspect.isroutine(obj):
            function_names.append(name)

    return function_names


def wrap_built_in_func_as_user_defined_func(bfunc: Callable) -> Callable:
    """
    Wraps a built-in function in a user defined function, to enable attachment to a FastMCP server.
    :param bfunc: The built-in function.
    :return: The user-defined function containing the built-in.
    """

    params = ", ".join(list(inspect.signature(bfunc).parameters))
    code = f"""
from {inspect.getmodule(bfunc).__name__} import {bfunc.__name__}
def wfunc({params}):
    return {bfunc.__name__}({params})
"""

    namespace = {}
    exec(code, namespace)

    namespace["wfunc"].__name__ = bfunc.__name__
    namespace["wfunc"].__doc__ = bfunc.__doc__

    return namespace["wfunc"]


def add_function_as_mcp_tool(func: Callable, mcp_server: FastMCP) -> None:
    """
    Adds a function to an MCP Server.
    :param func: The function to be added.
    :param mcp_server: The FastMCP server to attach the function to.
    :return: None
    """
    if func.__name__ == "<lambda>":
        return

    if isinstance(func, BuiltinFunctionType):
        try:
            func = wrap_built_in_func_as_user_defined_func(bfunc=func)
        except ValueError:
            warnings.warn(
                f'Failed to add function "{func.__name__}", function signature unknown, and cannot be inferred.',
                UserWarning,
            )
            return

    try:
        t = FunctionTool.from_function(fn=func)
        mcp_server.add_tool(t)
    except PydanticSchemaGenerationError:
        warnings.warn(
            f'Failed to add function "{func.__name__}", function paramter type not supported.',
            UserWarning,
        )
        return
    except Exception as e:
        warnings.warn(f'Failed to add function "{func.__name__}" as MCP tool: {e}', UserWarning)
        return


def create_pylib_mcp(
    libraries_and_funcs: Dict[str, Union[str, List[str], None]],
    server_name: str = "Python function server",
) -> FastMCP:
    """
    Creates a FastMCP object with the specified library functions as MCP tools.
    Note that the libraries must already be installed.

    :param libraries_and_funcs: A dictionary in the format of:
        {
            'import name of library': 'function_name'
        }
        or
        {
            'import name of library': ['function1_name', 'function2_name']
        }
        or, in case you want to include all compatible functions of the library as MCP tools,
        {
            'import name of library': None
        }
    :param server_name: The name of the server. Defaults to "Python function server".
    :return: A FastMCP server instance, with the python library functions attached.
    """

    mcp = FastMCP(server_name)

    for lib_name, func_name in libraries_and_funcs.items():
        if func_name is None:
            funcs_names = discover_all_functions_of_module(lib_name)
        elif isinstance(func_name, list):
            funcs_names = func_name
        elif isinstance(func_name, str):
            funcs_names = [func_name]
        else:
            raise TypeError(f"Function names must be list, str or None, not {type(func_name).__name__}")

        for func_name_ in funcs_names:
            f = import_function_from_module(lib_name, func_name_)
            add_function_as_mcp_tool(func=f, mcp_server=mcp)

    if not asyncio.run(mcp._mcp_list_tools()):
        raise ValueError("None of the specified library functions was attached to the MCP server.")

    return mcp
