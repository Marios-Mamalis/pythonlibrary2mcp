import importlib
from typing import Callable
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)


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
