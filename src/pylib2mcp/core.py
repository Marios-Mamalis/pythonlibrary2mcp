import importlib
import inspect
from pydantic.errors import PydanticSchemaGenerationError
from types import BuiltinFunctionType
from typing import Callable, List, Dict, Literal, Union
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
def wfunc({params}):
    return ({params})
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
        warnings.warn(
            f'Failed to add function "{func.__name__}" as MCP tool: {e}', UserWarning
        )
        return


def run(
    libraries_and_funcs: Dict[str, Union[str, List[str], None]],
    transport: Literal["stdio", "streamable-http", "sse"],
    host: Union[str, None] = "127.0.0.1",
    port: Union[int, None] = 8000,
    server_name: str = "Function Server",
) -> None:
    """
    Starts the FastMCP server with the specified library functions as MCP tools.
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
    :param transport: The transport protocol to be used for the server. Can be "stdio", "streamable-http", or "sse".
    :param host: In case transport is not "stdio", specify the host.
    :param port: In case transport is not "stdio", specify the port.
    :param server_name: The name of the server. Defaults to "Function Server".
    :return: None
    """

    if transport not in ["stdio", "sse", "streamable-http"]:
        raise ValueError(
            f'Transport protocol must be one of "stdio", "sse", "streamable-http". "{transport}" is not a valid choice.'
        )

    mcp = FastMCP(server_name)

    for lib_name, func_name in libraries_and_funcs.items():
        if func_name is None:
            funcs_names = discover_all_functions_of_module(lib_name)
            print(funcs_names)
        elif isinstance(func_name, list):
            funcs_names = func_name
        elif isinstance(func_name, str):
            funcs_names = [func_name]
        else:
            raise TypeError(
                f"Function names must be list, str or None, not {type(func_name).__name__}"
            )

        for func_name_ in funcs_names:
            f = import_function_from_module(lib_name, func_name_)
            add_function_as_mcp_tool(func=f, mcp_server=mcp)

    if transport in ["sse", "streamable-http"]:
        mcp.run(host=host, port=port, transport=transport)
    elif transport == "stdio":
        mcp.run(transport=transport)
