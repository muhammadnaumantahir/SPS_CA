# SPS-CA UI

SPS-CA now has two interfaces:

## Advanced web dashboard

```bash
python ui/web_app.py
```

Open `http://127.0.0.1:8080`.

The dashboard is designed for both everyday coding-assistant use and thesis demonstration. It exposes:

- task/prompt workspace;
- source-code editor;
- separate Brain/provider/model panel;
- live ten-layer status;
- Brain intent and reasoning summary;
- ordered capability selection/execution;
- modified source and unified diff;
- raw JSON trace;
- architecture map showing that Brain and Capability Registry are separate from the ten layers.

The browser API uses the real provider abstraction and capability registry. Its run endpoint is a controlled preview and does not silently mutate the browser user's local filesystem. Controlled project mutation belongs to the Execution layer.

## CLI

```bash
python ui/cli_interface.py
```

The CLI supports project loading, architecture inspection, Brain status, capability registry inspection, experience history and natural-language coding requests.

## Design rule

The UI is an observability/presentation layer. It must not become the decision-maker for SPS-CA. Brain planning, capabilities, Validation, Governance and Execution remain backend responsibilities.
