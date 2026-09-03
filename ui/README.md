# UI Architecture

The UI is a presentation layer over `CanonicalSPSPipeline`. It must not invent a parallel architecture vocabulary.

Use:

```python
from layers.architecture import LAYERS, LAYER_NAMES, LAYER_SUBCOMPONENTS
```

The ten canonical layers are **Software DNA Core, Governance Core, Cognitive core, Knowledge core, Experience core, Meta-learning core, Adaptation core, Evolution core, Verification & Validation Core, Execution Core**.

The Brain is displayed separately because it is a replaceable reasoning service, not a layer.
