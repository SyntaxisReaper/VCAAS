import numpy as np
import wave
import struct
from typing import Optional
from pathlib import Path
import uuid

from app.core.config import settings


class AudioWatermarker:
    """Simple inaudible watermarking using spread-spectrum in high frequencies.
    Note: This is a placeholder. For production, replace with a robust scheme.
    """

    def __init__(self, strength: float = None):
        self.strength = strength or settings.WATERMARK_STRENGTH

    def embed(self, input_wav_path: str, output_wav_path: str, watermark_id: Optional[str] = None) -> str:
        wm_id = watermark_id or f"wm-{uuid.uuid4().hex[:10]}"

        with wave.open(input_wav_path, 'rb') as wf:
            n_channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            framerate = wf.getframerate()
            n_frames = wf.getnframes()
            frames = wf.readframes(n_frames)

        # Convert to numpy array (mono mix if stereo)
        if sample_width == 2:
            dtype = np.int16
            scale = 32768.0
        else:
            dtype = np.int32
            scale = 2147483648.0

        audio = np.frombuffer(frames, dtype=dtype).astype(np.float32) / scale
        if n_channels == 2:
            audio = audio.reshape(-1, 2).mean(axis=1)

        # Generate pseudo-random watermark signal from wm_id
        rng = np.random.default_rng(abs(hash(wm_id)) % (2**32))
        wm_signal = rng.standard_normal(audio.shape[0]).astype(np.float32)

        # Emphasize watermark in high-frequency bands via pre-emphasis
        pre_emph = np.concatenate([[audio[0]], audio[1:] - 0.95 * audio[:-1]])
        marked = audio + self.strength * 0.005 * wm_signal + 0.002 * pre_emph

        # Normalize to prevent clipping
        max_abs = np.max(np.abs(marked)) + 1e-9
        if max_abs > 0.99:
            marked = marked / max_abs * 0.99

        # Save watermarked audio as mono WAV
        out_int16 = (marked * 32767.0).astype(np.int16)
        with wave.open(output_wav_path, 'wb') as wf_out:
            wf_out.setnchannels(1)
            wf_out.setsampwidth(2)
            wf_out.setframerate(framerate)
            wf_out.writeframes(out_int16.tobytes())

        return wm_id


# Global instance
watermarker = AudioWatermarker()
