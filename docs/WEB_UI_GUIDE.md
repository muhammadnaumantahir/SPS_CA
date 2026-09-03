# SPS-CA Web UI Guide

SPS-CA provides a browser-based coding workspace backed by the local SPS runtime and Ollama.

## Start locally

Install the Python dependencies, make sure Ollama is running, and start the web application:

```bash
pip install -r requirements.txt
ollama serve
python ui/web_app.py
```

The application serves the browser workspace and the SPS backend from the same process.

## Start in Google Colab

Use the repository setup script to install dependencies and prepare Ollama, then launch the web application from the checkout:

```bash
bash scripts/colab_setup.sh qwen2.5-coder:7b
python ui/web_app.py
```

The Ollama model is discovered from the connected Ollama server. The browser does not require a hard-coded installed-model name.

## Chat workspace

The Chat view is the primary workspace. Enter a request such as:

```text
Add input validation to this function
```

Paste source into the working-code panel when source is available. SPS-CA detects the language from the source, filename, and request, then chooses the appropriate capability.

For an existing source file, a request such as `add this function` is treated as code modification rather than test generation.

## Live activity

While a local model is processing, the composer displays an activity panel instead of only showing `Thinking…`.

The activity panel walks through the expected flow:

```text
Reading your request
        ↓
Checking system rules
        ↓
Choosing the right capability
        ↓
Working with the local model
        ↓
Checking the result
        ↓
Saving your turn
```

Elapsed time remains visible throughout the request. The steps are a user-interface progress indicator for the running request; final completion is confirmed only when the backend response returns.

Local inference has no default wall-clock cutoff. A specific caller can still provide a finite timeout when a bounded environment needs one.

## Working code

The Working code panel keeps the latest returned source visible after each successful turn. The source is also reflected in the conversation result when a change was requested.

## Chat history

Conversations are saved locally. A saved chat can be reopened and continued. Deleting a chat requires confirmation and removes only that session's stored conversation and working code.

## Trace and feedback

Each completed response can expose its structured trace, including the selected capability and SPS processing steps. Agree/Disagree feedback becomes Experience evidence for future routing and Evolution decisions.

A disagreement is evidence, not an unconditional instruction to create a new capability.

## Capabilities

The Capabilities view shows the registered skill population, active state, reuse, generated origin, and provenance information. Generated capabilities can be opened to inspect their lineage and evidence.

## Evolution

The Evolution view shows recorded capability-growth decisions and their supporting evidence. Controlled self-programming still passes through Software DNA, Governance, Verification & Validation, and Layer 10 execution/rollback controls.

## Model selection

Leaving the model field empty uses the connected Ollama server's currently installed model set. The provider resolves a usable model at request time and refreshes discovery when the server changes.

## Troubleshooting

### The UI stays on the activity panel

That usually means the local model is still processing. Check the Ollama process and model availability:

```bash
ollama list
curl -s http://127.0.0.1:11434/api/tags
```

A slow model response is not treated as an SPS source defect.

### Ollama is unavailable

Start Ollama and verify that the API is reachable before retrying the request. Provider and network failures are intentionally kept separate from autonomous self-repair.

### A code-change request selects the wrong capability

Requests with existing source and explicit change language are routed as code modification. Test Generation requires an explicit request for tests.

## Public sharing and security

Do not expose the application publicly with production credentials, secrets, private source code, or sensitive project data. Keep runtime state and credentials outside source control.
