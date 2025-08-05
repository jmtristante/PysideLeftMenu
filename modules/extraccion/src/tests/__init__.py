import os
import importlib
import inspect
import sys

from modules.extraccion.src.tests.test_base import TestExtractor
import modules.extraccion.src.tests.test_pk


def get_all_tests():
    tests = []

    test_dir = os.path.dirname(__file__)
    # Añadir el directorio de tests al sys.path para importación relativa
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)

    for filename in os.listdir(test_dir):
        if filename.startswith("test_") and filename.endswith(".py"):
            module_name = filename[:-3]  # Solo el nombre del archivo sin .py
            module = importlib.import_module(module_name)

            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, TestExtractor) and obj is not TestExtractor:
                    tests.append(obj)

    return tests
