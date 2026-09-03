# Colab runtime troubleshooting

## Self-programming import failure

If Colab reports:

```text
ImportError: cannot import name 'Change' from 'layers.layer_08_evolution.models'
```

pull the latest `main` revision before launching the server. `Change` and `FileEdit` are Layer 10 Execution models; Layer 8 imports them from `layers.layer_10_execution.models`. `FailureDiagnosis` and `SelfRepairResult` remain Layer 8 self-programming models.

Use:

```bash
git pull origin main
python -m pytest -q core/tests/test_self_programming_imports.py
```

Then restart the Colab Python process/kernel before starting `ui/web_app.py`, because an earlier failed import can remain cached in `sys.modules`.

## Port 5000 / ngrok error

An error such as:

```text
RuntimeError: Web server failed to start on port 5000
```

is downstream when `ui/web_app.py` crashes during import. Fix the Python traceback first, restart the process, and then launch the web server again. The ngrok layer cannot create a working tunnel to an application that failed before binding the port.

Do not hardcode a GitHub token or ngrok token in the notebook. Use environment variables or interactive configuration instead.

## Authorized automatic Evolution

Automatic Evolution is default-deny. Enable it only in a deliberate controlled environment:

```bash
export SPS_CA_AUTO_EVOLVE=true
export SPS_CA_AUTO_EVOLVE_MAX_ACTIONS=1
```

The normal Layer 8 pipeline remains candidate generation -> tests -> Software DNA -> Governance -> registration/promotion or rollback. Colab should be restarted after source-level self-repair so the next interpreter loads the repaired module.
