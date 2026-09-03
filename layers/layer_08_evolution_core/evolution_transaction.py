"""Atomic transaction boundary for Layer-8 Evolution changes."""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Iterable


class EvolutionTransactionError(RuntimeError):
    """Raised when a transaction cannot be safely restored."""


class EvolutionTransaction:
    """Snapshot changed files and directories until commit or rollback."""

    def __init__(self, repo_root: str | Path, *, transaction_id: str, registry_path: str | Path | None = None) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.transaction_id = transaction_id
        self.registry_path = (self.repo_root / registry_path).resolve() if registry_path else None
        self.backup_root = self.repo_root / "data" / "self_programming_snapshots" / "transactions" / transaction_id
        self.file_backups: list[tuple[Path, Path, bool]] = []
        self.dir_backups: list[tuple[Path, Path]] = []
        self.registry_backup: Path | None = None
        self.active = False

    def begin(self, paths: Iterable[str | Path]) -> None:
        if self.active:
            raise EvolutionTransactionError("transaction already active")
        self.backup_root.mkdir(parents=True, exist_ok=True)
        for index, raw in enumerate(paths):
            target = self._safe_path(raw)
            if target.is_dir():
                backup = self.backup_root / f"dir_{index}"
                shutil.copytree(target, backup)
                self.dir_backups.append((target, backup))
                continue
            existed = target.exists()
            backup = self.backup_root / f"file_{index}.bak"
            if existed:
                shutil.copy2(target, backup)
            self.file_backups.append((target, backup, existed))
        if self.registry_path and self.registry_path.exists() and not any(p == self.registry_path for p, _, _ in self.file_backups):
            self.registry_backup = self.backup_root / "registry.json.bak"
            shutil.copy2(self.registry_path, self.registry_backup)
        self.active = True

    def commit(self) -> None:
        if not self.active:
            raise EvolutionTransactionError("transaction is not active")
        manifest = {
            "transaction_id": self.transaction_id,
            "status": "committed",
            "files": [str(p.relative_to(self.repo_root)).replace("\\", "/") for p, _, _ in self.file_backups],
            "directories": [str(p.relative_to(self.repo_root)).replace("\\", "/") for p, _ in self.dir_backups],
            "registry": str(self.registry_path.relative_to(self.repo_root)).replace("\\", "/") if self.registry_path else None,
        }
        (self.backup_root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        self.active = False

    def rollback(self) -> None:
        for target, backup, existed in reversed(self.file_backups):
            if existed:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup, target)
            elif target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
        for target, backup in reversed(self.dir_backups):
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(backup, target)
        if self.registry_path and self.registry_backup and self.registry_backup.exists():
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.registry_backup, self.registry_path)
        self.active = False

    def _safe_path(self, raw: str | Path) -> Path:
        candidate = Path(raw)
        resolved = candidate.resolve() if candidate.is_absolute() else (self.repo_root / candidate).resolve()
        if not resolved.is_relative_to(self.repo_root):
            raise EvolutionTransactionError(f"unsafe transaction path: {raw}")
        return resolved


__all__ = ["EvolutionTransaction", "EvolutionTransactionError"]
