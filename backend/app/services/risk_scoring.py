"""
Shared risk scoring function — Phase 5 of Real-Time Streaming Detection.

Extracted from the inline logic in api/v1/verify.py (lines 408–427) so that
both the batch /full-analysis endpoint and the streaming StreamSession use
the same weighting, verdict thresholds, and watermark override logic.

Single source of truth: change the weights or thresholds here and both
callers update automatically.
"""
from __future__ import annotations

import math
from typing import Any, Dict, Tuple


def sanitize_numpy(obj: Any) -> Any:
    """Recursively convert numpy scalars / arrays to plain Python types."""
    try:
        import numpy as np  # type: ignore
        if isinstance(obj, np.ndarray):
            return sanitize_numpy(obj.tolist())
        if isinstance(obj, (np.floating,)):
            v = float(obj)
            return 0.0 if (math.isnan(v) or math.isinf(v)) else v
        if isinstance(obj, (np.integer,)):
            return int(obj)
    except ImportError:
        pass
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return 0.0
    if isinstance(obj, dict):
        return {k: sanitize_numpy(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_numpy(v) for v in obj]
    if isinstance(obj, tuple):
        return tuple(sanitize_numpy(v) for v in obj)
    return obj


def combine_layer_results(
    layer_results: Dict[str, Any],
    weights: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Compute the final weighted authenticity score and human-readable verdict.

    Args:
        layer_results: Dict mapping layer keys (e.g. "layer1_antispoof") to
                       their raw result dicts. Populated by the caller.
        weights: Dict mapping weight keys (e.g. "l1") to
                 {"score": float, "weight": float} dicts.
                 Layers that failed or were skipped should not have entries here.

    Returns:
        Dict with:
          - overall_authenticity_score (float, 0–1, higher = more authentic)
          - verdict (str)
          - is_authentic (bool)
          - confidence (float)
          - layers (dict, sanitized)
          - weights_used (dict)
    """
    # Weighted average
    total_weight = sum(w["weight"] for w in weights.values())
    if total_weight > 0:
        final_authenticity = (
            sum(w["score"] * w["weight"] for w in weights.values()) / total_weight
        )
    else:
        final_authenticity = 0.5

    # Clamp
    final_authenticity = float(max(0.0, min(1.0, final_authenticity)))

    # Watermark override — definitive synthetic signal
    watermark_found = layer_results.get("layer6_watermark", {}).get("found", False)
    if watermark_found:
        final_authenticity = 0.0

    # Human-readable verdict
    if watermark_found:
        verdict = "Deepfake (Watermarked Synthetic)"
    elif final_authenticity > 0.8:
        verdict = "Authentic (Human)"
    elif final_authenticity > 0.5:
        verdict = "Suspicious (Likely Human)"
    elif final_authenticity > 0.2:
        verdict = "Suspicious (Likely Synthetic)"
    else:
        verdict = "Deepfake (Synthetic)"

    return {
        "overall_authenticity_score": round(final_authenticity, 4),
        "verdict": verdict,
        "is_authentic": final_authenticity > 0.5 and not watermark_found,
        "confidence": round(total_weight, 4),  # how many layers contributed
        "layers": sanitize_numpy(layer_results),
        "weights_used": weights,
    }
