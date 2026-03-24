import importlib.util
import os

spec = importlib.util.spec_from_file_location(
    "app_file",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py"),
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
app = mod.app
