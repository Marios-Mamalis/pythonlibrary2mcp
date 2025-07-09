<div align="center">
    <h1>
        PythonLibrary2MCP
    </h1>

![Versions](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)
![Tests](https://github.com/Marios-Mamalis/pythonlibrary2mcp/actions/workflows/ci.yml/badge.svg)
![Black](https://img.shields.io/badge/code%20style-black-000000.svg)
</div>

<br>

The purpose of this utility is to provide a simple way to quickly port functions of existing Python 
libraries (both built-in and external) as MCP (Model Context Protocol) server tools.

The utility is based on the [FastMCP](https://github.com/jlowin/fastmcp) library, and acts as an
added layer on top.


## Installation
To install the **pylib2mcp** package, simply clone the repository and install it:
```
git clone https://github.com/Marios-Mamalis/pythonlibrary2mcp
cd pythonlibrary2mcp
uv pip install .
```
`uv` is highly recommended for installation, but `pip` also works.


## Usage
The utility can attach a single function, a list of functions, or be set to automatically 
discover and attach all compatible routines from a module (except lambda functions) as MCP tools.

You can use this package as a regular Python module:
```python
import pylib2mcp

pylib2mcp.create_pylib_mcp(
    libraries_and_funcs={
        'transliterate': 'translit',  # a single function, external library
        'urllib.parse': ['quote', 'unquote'],  # a list of functions
        'math': None  # all attachable routines in that module
    },
    server_name='Python function server'
).run(
    transport='sse',
    host='0.0.0.0',
    port=8000
)
```
Or run it directly from the command line:
```bash
pylib2mcp run --library-functions transliterate:translit \
              --library-functions urllib.parse:quote,unquote \
              --library-functions math \
              --name "Python function server"
              --transport sse --host 0.0.0.0 --port 8000
```


### Behavior and limitations
The libraries containing the functions to be attached, must already be installed, if external.

Automatic attachment of Python functions as MCP tools is based on their signatures. Signatures with
unsupported I/O types are skipped. However, if a function lacks a signature, it is possible that 
it will be attached as an MCP tool but won't function correctly, so it is best to test the attached
functions for expected behavior.


## Contributing
If you want to contribute to the project, install the development requirements by syncing the
project through the lockfile instead of doing a standard install.

Contributions should follow the Black formatting style and pass the test suite.
