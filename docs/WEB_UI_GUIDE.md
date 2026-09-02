# SPS-CA Web UI Guide

The SPS-CA web UI is a Gradio presentation layer over the existing **ten SPS layers**. It can run locally or inside Google Colab.

## Google Colab — cell by cell

### Cell 1 — Clone the development branch
```python
!git clone -b feat/sps-supervisor-loop-step1 https://github.com/muhammadnaumantahir/SPS_CA.git
%cd /content/SPS_CA
```

For a fresh experiment, start from a fresh Colab runtime so package and Ollama state are predictable.

### Cell 2 — Install Python dependencies, Ollama, and the local coding model
```python
!bash scripts/colab_setup.sh qwen2.5-coder:7b
```

The setup script installs `requirements.txt`, starts the local Ollama server, and pulls the selected model.

### Cell 3 — Verify the local model service
```python
!ollama list
!curl -s http://127.0.0.1:11434/api/tags
```

### Cell 4 — Run the full repository test suite
```python
!bash scripts/run_tests.sh
```

Do not use a failed test run as evidence for a successful research scenario. Fix the environment or code and rerun the suite.

### Cell 5 — Launch the research dashboard
```python
from ui.web_ui import launch
launch()
```

In Colab the launcher detects the notebook environment and enables a Gradio share link. SPS processing still happens inside the Colab runtime.

### Cell 6 — Run the first supervisor scenario
Open **SPS Supervisor** and provide:

1. A task/prompt, for example: `add input validation to this function`
2. A programming language
3. Pasted code or an uploaded source file
4. An optional target project directory

Click **Run SPS Supervisor**.

Review the execution summary and modified code before treating the scenario as successful.

### Cell 7 — Inspect capability growth
Open **Capabilities** to see the registry, then **Growth** to see capability introduction/reuse charts, and **Evolution** to inspect the scenario trace.

For a capability-gap experiment, look for:

`No suitable capability → Layer 8 generation → validation → governance → registration → reuse`

### Cell 8 — Repeat a scenario
Run an equivalent task again. The objective is to observe whether the system can reuse an existing capability rather than generating another one. Compare the scenario record, capability reuse count, and stage state.

## Local Windows

### 1. Clone
```powershell
git clone -b feat/sps-supervisor-loop-step1 https://github.com/muhammadnaumantahir/SPS_CA.git
cd SPS_CA
```

### 2. Create the Python environment
```powershell
python -m venv .venv
.venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Install and start Ollama
Install Ollama for Windows, then:
```powershell
ollama pull qwen2.5-coder:7b
ollama serve
```

### 4. In a second terminal, launch SPS-CA
```powershell
cd SPS_CA
.venv\\Scripts\\activate
python ui/web_ui.py
```

The local dashboard does not create a public share link by default.

## Local Linux / macOS

```bash
git clone -b feat/sps-supervisor-loop-step1 https://github.com/muhammadnaumantahir/SPS_CA.git
cd SPS_CA
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
ollama pull qwen2.5-coder:7b
ollama serve
```

Then, in the same environment:
```bash
python ui/web_ui.py
```

## Dashboard sections

### SPS Supervisor
The main research workspace for prompt + code submission and governed modification.

### Capabilities
The Layer 9 registry view. Shows capability identity, type, origin, version, reuse, coverage, and status.

### Growth
Visualizes capability creation and reuse over accumulated scenarios and displays all ten SPS layers.

### Evolution
Shows Stage N transitions and the stored WHY / WHAT / WHEN / HOW research trace for each scenario.

### Experiments
Shows the reproducible evaluation catalog, including the 25-scenario research matrix.

### Guide
This run procedure is embedded into the dashboard so the application remains self-contained for demonstrations.

## Colab GitHub persistence experiment

The dashboard currently performs SPS execution in the Colab workspace. A successful local commit is not the same thing as a GitHub push. Use a separate, explicit GitHub synchronization experiment to verify remote persistence of a generated modification.

## Security

A Gradio share link is public. Do not use it with production credentials, private repositories, secrets, or sensitive source code. Keep runtime data and credentials out of source control.
