"""
Speaker verification service.

Prefers SpeechBrain ECAPA-TDNN if available; falls back to MFCC cosine similarity.
"""
from __future__ import annotations

import numpy as np
import librosa
from typing import Optional, Dict, Any

try:
    import torch  # type: ignore
    from speechbrain.pretrained import SpeakerRecognition  # type: ignore
    _SB_AVAILABLE = True
except Exception:
    _SB_AVAILABLE = False
    SpeakerRecognition = None  # type: ignore
    torch = None  # type: ignore


class SpeakerVerifier:
    def __init__(self) -> None:
        self._rec: Optional[SpeakerRecognition] = None
        if _SB_AVAILABLE:
            try:
                # Downloads the model on first use
                self._rec = SpeakerRecognition.from_hparams(
                    source="speechbrain/spkrec-ecapa-voxceleb", savedir=".cache/spkrec_ecapa"
                )
            except Exception:
                self._rec = None

    def _mfcc_embed(self, wav_path: str, sr: int = 16000) -> np.ndarray:
        y, s = librosa.load(wav_path, sr=sr, mono=True)
        mfcc = librosa.feature.mfcc(y=y, sr=s, n_mfcc=40)
        # Mean pooling
        emb = np.mean(mfcc, axis=1)
        emb = emb / (np.linalg.norm(emb) + 1e-9)
        return emb

    def verify(self, ref_path: str, qry_path: str) -> Dict[str, Any]:
        if self._rec is not None:
            try:
                score, decision = self._rec.verify_files(ref_path, qry_path)
                return {
                    "engine": "speechbrain_ecapa",
                    "score": float(score),
                    "is_same_speaker": bool(decision),
                }
            except Exception as e:
                # Fallback to MFCC
                pass
        # MFCC cosine similarity fallback
        ref = self._mfcc_embed(ref_path)
        qry = self._mfcc_embed(qry_path)
        score = float(np.dot(ref, qry))
        return {
            "engine": "mfcc_cosine",
            "score": score,
            "is_same_speaker": bool(score > 0.8),
        }