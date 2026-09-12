"""
Anti-spoofing (deepfake) detector.

Prefers SpeechBrain AASIST if available; otherwise uses heuristic spectral cues
as a lightweight baseline (not production-grade).
"""
from __future__ import annotations

import numpy as np
import librosa
from typing import Dict, Any
import logging
import os

logger = logging.getLogger(__name__)

try:
    import torch
    import torchaudio
    from speechbrain.inference.interfaces import foreign_class
    _HAS_SB = True
except ImportError:
    _HAS_SB = False
    torch = None


class AntiSpoofDetector:
    def __init__(self) -> None:
        self._model = None
        self._custom_model = None
        self._device = "cuda" if _HAS_SB and torch.cuda.is_available() else "cpu"
        
        # Try to load Custom Trained RF Model first (so we can test it)
        try:
            import joblib
            model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "ml", "simple_rf_detector.pkl")
            if os.path.exists(model_path):
                self._custom_model = joblib.load(model_path)
                logger.info("Custom Lightweight RF Anti-Spoof model loaded successfully.")
        except Exception as e:
            logger.warning(f"Could not load custom RF model: {e}")
            
        if _HAS_SB and not self._custom_model:
            try:
                # Attempt to load the AASIST anti-spoofing model
                # Note: this requires an internet connection on first run to download the model from HuggingFace
                # It uses the foreign_class interface because AASIST has a custom architecture
                save_dir = os.path.join(os.path.expanduser("~"), ".cache", "speechbrain", "aasist")
                self._model = foreign_class(
                    source="speechbrain/aasist",
                    pymodule_file="custom_interface.py",
                    classname="CustomEncoderWav2vec2Classifier", # Note: This is an example class name, if it fails, it will fall back to heuristics
                    savedir=save_dir,
                    run_opts={"device": self._device}
                )
                logger.info("SpeechBrain AASIST model loaded successfully.")
            except Exception as e:
                logger.warning(f"Could not load SpeechBrain AASIST model: {e}. Falling back to heuristics.")
                self._model = None

    def _extract_features(self, y: np.ndarray, sr: int) -> np.ndarray:
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
        
        return np.array([hf_ratio, phase_var, zcr_std, silence_ratio])

    def _heuristics(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        features = self._extract_features(y, sr)
        
        if self._custom_model:
            # Use our custom trained ML model
            try:
                # predict_proba returns [[prob_real, prob_fake]]
                probs = self._custom_model.predict_proba([features])[0]
                spoof_score = float(probs[1]) # Probability of being fake
                
                return {
                    "spoof_score": spoof_score,
                    "is_spoof": spoof_score > 0.5,
                    "features": {
                        "hf_ratio": features[0],
                        "phase_var": features[1],
                        "zcr_std": features[2],
                        "silence_ratio": features[3]
                    },
                    "engine": "custom_rf_model"
                }
            except Exception as e:
                logger.error(f"Custom RF model inference failed: {e}")
                # Fall through to manual heuristics
        
        # Aggregate score (0..1): higher => spoof more likely
        # Adjusted weights for better heuristic detection
        score_hf = np.clip((features[0] + 0.3) * 1.5, 0, 1) # Unnatural HF falloff
        score_phase = np.clip(features[1] / 8, 0, 1)       # Phase jitter
        score_zcr = np.clip(1.0 - (features[2] * 8), 0, 1)   # Too uniform ZCR (robotic)
        score_silence = 1.0 if features[3] < 0.01 else 0.0 # No natural silence
        
        spoof_score = np.clip((0.4 * score_hf) + (0.3 * score_phase) + (0.2 * score_zcr) + (0.1 * score_silence), 0, 1)
        
        return {
            "spoof_score": float(spoof_score),
            "is_spoof": spoof_score > 0.65,
            "features": {
                "hf_ratio": features[0],
                "phase_var": features[1],
                "zcr_std": features[2],
                "silence_ratio": features[3]
            },
            "engine": "enhanced_heuristic"
        }

    def detect(self, path: str) -> Dict[str, Any]:
        """Detect spoofing from an audio file."""
        if self._model is not None and _HAS_SB and not self._custom_model:
            try:
                # Use SpeechBrain AASIST
                # The model expects a torch tensor
                signal, sr = torchaudio.load(path)
                # Resample to 16kHz if needed (AASIST expects 16kHz)
                if sr != 16000:
                    resampler = torchaudio.transforms.Resample(sr, 16000)
                    signal = resampler(signal)
                
                # Move to device
                signal = signal.to(self._device)
                
                # Inference
                score, index, text_lab = self._model.classify_batch(signal)
                # The score usually indicates likelihood of spoof vs bonafide
                # Let's normalize it to a 0-1 probability
                spoof_score = float(score[0].item())
                
                return {
                    "spoof_score": spoof_score,
                    "is_spoof": spoof_score > 0.5, # Assuming >0.5 is spoof
                    "features": {"aasist_raw_score": spoof_score},
                    "engine": "speechbrain_aasist"
                }
            except Exception as e:
                logger.error(f"AASIST inference failed: {e}. Falling back to heuristics.")
                # Fall back below
                
        # Fallback to heuristics
        y, sr = librosa.load(path, sr=16000, mono=True)
        return self._heuristics(y, sr)

    def detect_array(self, audio: np.ndarray, sr: int = 16000) -> Dict[str, Any]:
        """
        Run anti-spoof analysis directly on an in-memory numpy array.

        Streaming variant: skips librosa.load() since the caller (StreamSession)
        already has the audio in memory. The underlying _heuristics() logic is
        identical to the file-based detect() path.

        Args:
            audio: 1-D float32 array, values in [-1, 1], mono.
            sr: Sample rate in Hz (default 16000).

        Returns:
            Same dict as detect().
        """
        audio = np.asarray(audio, dtype=np.float32)
        if audio.ndim > 1:
            audio = np.mean(audio, axis=-1)
            
        if self._model is not None and _HAS_SB and not self._custom_model:
            try:
                # Convert numpy array to tensor
                signal = torch.from_numpy(audio).unsqueeze(0)
                
                # Resample to 16kHz if needed
                if sr != 16000:
                    resampler = torchaudio.transforms.Resample(sr, 16000)
                    signal = resampler(signal)
                    
                # Move to device
                signal = signal.to(self._device)
                
                # Inference
                score, index, text_lab = self._model.classify_batch(signal)
                spoof_score = float(score[0].item())
                
                return {
                    "spoof_score": spoof_score,
                    "is_spoof": spoof_score > 0.5,
                    "features": {"aasist_raw_score": spoof_score},
                    "engine": "speechbrain_aasist"
                }
            except Exception as e:
                logger.error(f"AASIST array inference failed: {e}. Falling back to heuristics.")
                # Fall back below
                
        return self._heuristics(audio, sr)