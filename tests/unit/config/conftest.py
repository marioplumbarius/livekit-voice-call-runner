import importlib
import sys

import pytest


@pytest.fixture
def reload_config():
    def _reload(module_path: str):
        """Reload a config module and reset its lru_cache so env changes take effect."""
        if module_path in sys.modules:
            del sys.modules[module_path]
        return importlib.import_module(module_path)

    return _reload
