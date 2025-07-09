# Code adapted from https://github.com/jlowin/fastmcp
# Licensed under the Apache License, Version 2.0

import typer
from typing import Annotated, Dict, List, Union
import pylib2mcp


def parse_library_functions(values: List[str]) -> Dict[str, Union[List[str], None]]:
    result = {}
    for item in values:
        if ":" in item:
            lib, funcs = item.split(":")
            result[lib] = funcs.split(",")
        else:
            result[item] = None
    return result


app = typer.Typer(
    name="pylib2mcp",
    help="Pylib2MCP CLI",
    add_completion=False,
    no_args_is_help=True,
)


@app.command()
def run(
    library_functions: Annotated[List[str], typer.Option(..., "--library-functions", help="Functions from python libraries to attach as tools. Format: lib1:func1,func2 or lib1:func1 or lib1")],
    server_name: Annotated[str | None, typer.Option("--name", "-n", help="The name of the server (default: 'Python function server')")] = None,
    transport: Annotated[str, typer.Option("--transport", "-t", help="Transport protocol to use (stdio, streamable-http, or sse) (default: stdio)")] = "stdio",
    host: Annotated[str | None, typer.Option("--host", help="Host to bind to when using http transport (default: 127.0.0.1)")] = None,
    port: Annotated[int | None, typer.Option("--port", "-p", help="Port to bind to when using http transport (default: 8000)")] = None,
) -> None:
    """Runs an FastMCP server with the specified Python library functions attached as tools."""

    libraries_and_funcs = parse_library_functions(library_functions)

    mcp_server = pylib2mcp.create_pylib_mcp(libraries_and_funcs=libraries_and_funcs, server_name=server_name)

    if transport == "stdio":
        mcp_server.run(transport=transport)
    else:
        mcp_server.run(transport=transport, host=host, port=port)


@app.command()
def version():
    """Show pylib2mcp version"""
    typer.echo(f"Pylib2mcp Version: {pylib2mcp.__version__}")


if __name__ == "__main__":
    app()
