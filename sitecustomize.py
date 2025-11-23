"""
Ensure custom PipeFunc implementations are registered before Pipelex CLI runs.

Python automatically imports `sitecustomize` at startup if it is on `sys.path`.
Placing this file at the project root guarantees our stub pipeline helpers are
registered in `func_registry` for `uv run pipelex validate`.
"""

# Ensure project source is importable when invoked via `uv run`.
import sys
from pathlib import Path

# Force UTF-8 streams on Windows consoles to avoid Rich logging crashes when emitting emoji icons.
for stream_name in ("stdout", "stderr"):
    stream = getattr(sys, stream_name, None)
    if stream and hasattr(stream, "reconfigure"):
        try:
            stream.reconfigure(encoding="utf-8")
        except OSError:
            # Non-IOBase stream (e.g., redirected); ignore.
            pass

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Import side-effects register the functions.
import lunii_cyoa.pipe_funcs  # noqa: F401
