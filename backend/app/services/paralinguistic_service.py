"""
Paralinguistic / Emotion Coherence Service — Layer 4 of the 6-layer defense pipeline.

Analyses the acoustic features (MFCC, spectral contrast, energy) to extract a rough
emotional valence/arousal profile, and compares it against expected natural speech variance.
In a full production environment, this would use a speech-emotion-recognition (SER) model 
(like wav2vec2-emotion) paired with semantic sentiment analysis to detect tone/content mismatch.
For this MVP, we analyze energetic variance (arousal) to detect "flat delivery".

Synthetic audio tends to be emotionally flat or have a mismatched energy profile compared 
to human speech which naturally varies significantly.
"""
from __future__ import annotations

import librosa
import numpy as np
from typing import Dict, Any


class ParalinguisticService:
    """Layer 4: Paralinguistic Coherence analyser."""

    def __init__(self) -> None:
        pass

    def analyse(self, audio_path: str) -> Dict[str, Any]:
        """Run paralinguistic analysis on an audio file.

        Args:
            audio_path: Path to a WAV/FLAC/MP3 file.

        Returns:
            Dict with:
              - authenticity_score (float, 0–1, higher = more natural)
              - arousal_variance (float)
              - spectral_contrast_std (float)
              - engine (str)
        """
        try:
            y, sr = librosa.load(audio_path, sr=16000, mono=True)
            return self._analyse_waveform(y, sr)
        except Exception as exc:
            return {
                "authenticity_score": 0.5,
                "error": str(exc),
                "engine": "paralinguistic_heuristic",
            }

    def _analyse_waveform(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        # 1. Arousal Variance (Energy/RMS fluctuations)
        # Humans naturally vary their volume/energy when speaking (prosodic stress).
        # TTS is often normalized and flat.
        rms = librosa.feature.rms(y=y)[0]
        # Ignore complete silence to focus on speech energy
        speech_rms = rms[rms > (np.mean(rms) * 0.1)]
        
        if len(speech_rms) < 10:
            return {
                "authenticity_score": 0.5,
                "error": "Not enough speech for paralinguistic analysis",
                "engine": "paralinguistic_heuristic",
            }

        arousal_variance = float(np.std(speech_rms) / (np.mean(speech_rms) + 1e-6))
        
        # 2. Spectral Contrast Variance
        # Spectral contrast represents the difference in amplitude between peaks and valleys.
        # High variation means dynamic articulation; low means robotic/flat.
        contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        contrast_std = float(np.mean(np.std(contrast, axis=1)))

        # Natural speech arousal CV is typically > 0.4.
        # TTS is usually < 0.25
        arousal_score = np.clip((arousal_variance - 0.2) / 0.4, 0.0, 1.0)
        
        # Spectral contrast std typically > 3.0 for natural speech
        contrast_score = np.clip((contrast_std - 2.0) / 2.0, 0.0, 1.0)

        # Authenticity score combining the two
        authenticity_score = float(0.6 * arousal_score + 0.4 * contrast_score)

        return {
            "authenticity_score": round(authenticity_score, 4),
            "arousal_variance": round(arousal_variance, 4),
            "spectral_contrast_std": round(contrast_std, 4),
            "engine": "paralinguistic_heuristic",
            "details": {
                "arousal_score": round(float(arousal_score), 4),
                "contrast_score": round(float(contrast_score), 4),
            }
        }
