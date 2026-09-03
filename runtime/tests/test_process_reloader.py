from __future__ import annotations

import os
import sys

from runtime.process_reloader import is_web_app_process, schedule_restart


def test_is_web_app_process(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["ui/web_app.py"])
    assert is_web_app_process() is True

    monkeypatch.setattr(sys, "argv", ["pytest"])
    assert is_web_app_process() is False


def test_schedule_restart_is_disabled_for_non_web_process(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["pytest"])
    assert schedule_restart() is False


def test_schedule_restart_can_be_disabled(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["ui/web_app.py"])
    monkeypatch.setenv("SPS_CA_DISABLE_RESTART", "1")
    assert schedule_restart() is False
