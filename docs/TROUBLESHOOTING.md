# Troubleshooting

## Import errors in Colab

Pull the latest `main` revision before launching the server. Layer 8 self-programming models must stay in the Evolution core, while execution edit models belong to Layer 10.

```bash
git pull origin main
python -m pytest -q core/tests/test_self_programming_imports.py
```

Restart the Python process/kernel after source-level changes so stale modules are not reused from `sys.modules`.

## Port or ngrok failures

A web-server port failure can be a downstream symptom of a Python import or application-startup exception. Fix the traceback first, restart the application, and only then reconnect the tunnel.

Do not hardcode GitHub or ngrok tokens in notebooks. Use environment variables or interactive configuration.

## Automatic capability evolution

Automatic Evolution is default-deny. When enabled in a controlled environment, keep the action limit small and retain verification and governance checks.

```bash
export SPS_CA_AUTO_EVOLVE=true
export SPS_CA_AUTO_EVOLVE_MAX_ACTIONS=1
```

A source-level self-repair should be followed by a clean interpreter restart before evaluating the repaired module.

## Test failures

Run the smallest relevant test first, then the full suite:

```bash
pytest -q path/to/test_file.py
pytest -q
```

For growth evaluation failures, regenerate the scenario data and run the descriptive evaluation script rather than relying on an old generated dataset.
