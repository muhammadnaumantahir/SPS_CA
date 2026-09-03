"""Canonical SPS layers package.

Legacy layer import paths are provided as small filesystem compatibility
packages instead of eagerly importing every canonical layer here. This keeps
package initialization lazy and avoids circular imports during Layer 8
(Evolution) startup.
"""

from .architecture import LayerManifest, LAYER_MANIFEST, get_layer

__all__ = ["LayerManifest", "LAYER_MANIFEST", "get_layer"]
