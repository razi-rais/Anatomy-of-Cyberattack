"""Combined launcher for the Anatomy of an LLM Attack labs.

Loads every exercise module and starts one web server with a dropdown so a
learner can switch between exercises in a single running process.

Run from the exercises/ directory:

    python3 serve.py

Then open http://localhost:8000.

Each exercise lives in a folder whose name is not a valid Python package name
(it starts with a digit), so we load each module.py from its own directory in
isolation. Sibling files (attacks.py, defenses.py, ...) share names across
exercises, so after loading one exercise we remove its modules from the import
cache before loading the next. The MODULE object keeps working because its
functions already hold references to what they need.
"""

from __future__ import annotations

import importlib.util
import os
import sys

from labkit.server import serve

HERE = os.path.dirname(os.path.abspath(__file__))

EXERCISE_DIRS = [
    "01-prompt-injection",
    "02-indirect-prompt-injection",
    "03-excessive-agency",
]


def load_module(dir_name: str):
    path = os.path.join(HERE, dir_name)
    sys.path.insert(0, path)
    before = set(sys.modules)
    try:
        spec = importlib.util.spec_from_file_location(
            f"exercise_{dir_name.replace('-', '_')}",
            os.path.join(path, "module.py"),
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.MODULE
    finally:
        # Drop sibling modules loaded from this directory so the next exercise
        # loads its own same-named files cleanly.
        for name in set(sys.modules) - before:
            loaded = sys.modules.get(name)
            loaded_file = getattr(loaded, "__file__", "") or ""
            if loaded_file.startswith(path):
                del sys.modules[name]
        if path in sys.path:
            sys.path.remove(path)


def main() -> None:
    modules = [load_module(d) for d in EXERCISE_DIRS]
    serve(modules)


if __name__ == "__main__":
    main()
