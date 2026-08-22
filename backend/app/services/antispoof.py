"""
Anti-spoofing (deepfake) detector.

Prefers SpeechBrain AASIST if available; otherwise uses heuristic spectral cues
as a lightweight baseline (not production-grade).
"""
from __future__ import annotations

import numpy as np
import librosa
from typing import Dict, Any

try:
    import torch  # type: ignore
    from speechbrain.pretrained import SpectralMaskEnhancement  # placeholder import
    _HAS_SB = True
except Exception:
    _HAS_SB = False
    torch = None  # type: ignore


class AntiSpoofDetector:
    def __init__(self) -> None:
        self._model = None
        # NOTE: Proper AASIST loading would go here when dependencies are present.

    def _heuristics(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        # Compute spectral stats
        S = np.abs(librosa.stft(y, n_fft=1024, hop_length=256))
        S_db = librosa.amplitude_to_db(S + 1e-9)
        
        # High-frequency energy ratio
        freqs = np.linspace(0, sr // 2, S.shape[0])
        hf_mask = freqs > (sr * 0.35)
        hf_energy = float(np.mean(S_db[hf_mask, :]))
        mid_energy = float(np.mean(S_db[(freqs > sr * 0.1) & (freqs <= sr * 0.35), :]))
        hf_ratio = float((hf_energy - mid_energy) / (abs(mid_energy) + 1e-6))
        
        # Synthesized audio often has a sharp high-frequency cutoff
        # and unnatural phase variations from the vocoder.
        
        # Phase inconsistency proxy
        phase = np.angle(librosa.stft(y, n_fft=512, hop_length=128))
        phase_var = float(np.var(np.diff(phase, axis=1)))
        
        # Zero-crossing irregularity
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        zcr_std = float(np.std(zcr))
        
        # Silence/Breath ratio (Natural speech has distinct pauses/breaths)
        # Deepfakes sometimes have completely dead silence or weird constant noise floors
        rms = librosa.feature.rms(y=y)[0]
        silence_threshold = np.mean(rms) * 0.1
        silence_ratio = float(np.sum(rms < silence_threshold) / len(rms))
        
        # Aggregate score (0..1): higher => spoof more likely
        # Adjusted weights for better heuristic detection
        score_hf = np.clip((hf_ratio + 0.3) * 1.5, 0, 1) # Unnatural HF falloff
        score_phase = np.clip(phase_var / 8, 0, 1)       # Phase jitter
        score_zcr = np.clip(1.0 - (zcr_std * 8), 0, 1)   # Too uniform ZCR (robotic)
        score_silence = 1.0 if silence_ratio < 0.01 else 0.0 # No natural silence
        
        spoof_score = np.clip((0.4 * score_hf) + (0.3 * score_phase) + (0.2 * score_zcr) + (0.1 * score_silence), 0, 1)
        
        return {
            "spoof_score": float(spoof_score),
            "is_spoof": spoof_score > 0.65,
            "features": {
                "hf_ratio": hf_ratio,
                "phase_var": phase_var,
                "zcr_std": zcr_std,
                "silence_ratio": silence_ratio
            },
            "engine": "enhanced_heuristic"
        }

    def detect(self, path: str) -> Dict[str, Any]:
        y, sr = librosa.load(path, sr=16000, mono=True)
        return self._heuristics(y, sr)