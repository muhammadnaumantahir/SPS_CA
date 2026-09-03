"""Controlled process reloader for successful SPS-CA self-repairs.

This is runtime/application plumbing, not a ninth or eleventh SPS layer. The
existing ten layer model remains unchanged. A restart is only scheduled after
a successful self-repair of Python code and is disabled outside the web app
process unless explicitly requested.
"""
from __future__ import annotations

import os
import sys
import threading
from pathlib import Path
from typing import Sequence


def is_web_app_process() -> bool:
    """Return True when the current process was launched as the SPS-CA web app."""
    try:
        return Path(sys.argv[0]).name == "web_app.py"
    except (IndexError, TypeError):
        return False


def schedule_restart(delay_seconds: float = 0.35, *, argv: Sequence[str] | None = None) -> bool:
    """Schedule a same-command interpreter replacement and return immediately.

    The replacement is deliberately deferred so the current HTTP response can
    finish before the old process exits. Setting ``SPS_CA_DISABLE_RESTART=1``
    prevents automatic restart for development/testing.
    """
    if os.environ.get("SPS_CA_DISABLE_RESTART", "").strip() == "1":
        return False
    if not is_web_app_process():
        return False

    command = [sys.executable, *(list(argv) if argv is not None else list(sys.argv))]

    def _replace() -> None:
        os.execv(command[0], command)

    timer = threading.Timer(max(0.05, float(delay_seconds)), _replace)
    timer.daemon = True
    timer.start()
    return True
