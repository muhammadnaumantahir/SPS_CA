"""Supervisor-mode CLI for the SPS ten-layer research prototype.

This presentation entrypoint intentionally delegates all behavior to
``SupervisorScenarioService`` and does not introduce an eleventh layer.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ui.supervisor_service import SupervisorScenarioService  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="SPS-CA supervisor scenario runner")
    parser.add_argument("--request", required=True, help="User coding request")
    parser.add_argument("--language", default="python", help="Source language")
    parser.add_argument("--file", dest="file_path", help="Source code file")
    parser.add_argument("--code", help="Source code text")
    parser.add_argument("--project-root", default=".", help="Execution/test root")
    args = parser.parse_args()

    if bool(args.file_path) == bool(args.code):
        parser.error("provide exactly one of --file or --code")

    code = args.code
    file_path = ""
    if args.file_path:
        path = Path(args.file_path).expanduser().resolve()
        if not path.is_file():
            parser.error(f"code file does not exist: {args.file_path}")
        try:
            code = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            parser.error(f"code file is not UTF-8 text: {path}")
        file_path = str(path)

    service = SupervisorScenarioService()
    result = service.analyze_submission(
        user_request=args.request,
        code=code or "",
        language=args.language,
        file_path=file_path,
        project_root=args.project_root,
    )

    print(f"Scenario: {result.scenario_id}")
    print(f"Stage: {result.stage}")
    print("Analysis:", result.analysis)
    print("Capability search:", result.capability_search)
    print("Capability generation:", result.capability_generation)
    print("Trace: experience/traces/evolution_history.json")


if __name__ == "__main__":
    main()
