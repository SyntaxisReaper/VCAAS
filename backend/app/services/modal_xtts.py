import modal
import os
import io

def download_model():
    """
    Runs during container build time.
    Downloads the multi-gigabyte heavy model so it is cached inside the image itself.
    """
    import os
    os.environ["COQUI_TOS_AGREED"] = "1"
    
    from TTS.api import TTS
    print("Downloading XTTS v2 model during build...")
    TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    print("Model downloaded and cached in image!")

# Define the custom Docker image
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("libsndfile1")
    .pip_install(
        "TTS==0.22.0",
        "transformers<4.41.0",
        "torch==2.5.1",
        "torchaudio==2.5.1",
        "numpy",
        "soundfile"
    )
    .run_function(download_model)
)

app = modal.App("vcaas-xtts", image=image)

# We request an NVIDIA T4 GPU for inference
@app.cls(gpu="T4", timeout=300)
class ModalXTTS:

    @modal.enter()
    def load_model(self):
        """
        Runs when the container boots up.
        Loads the pre-downloaded model into the GPU VRAM.
        """
        import os
        os.environ["COQUI_TOS_AGREED"] = "1"
        import torch
        from TTS.api import TTS
            
        print("Loading model into GPU...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
        print("Model loaded and ready for synthesis!")

    @modal.method()
    def synthesize(self, text: str, speaker_wav_bytes: bytes, language: str = "en") -> bytes:
        """
        The main inference endpoint. 
        Takes text and reference audio bytes, runs it through the GPU, and returns the generated audio bytes.
        """
        import soundfile as sf
        import tempfile
        import os
        
        # Safely write the reference wrapper to a temporary file since TTS expects a filepath
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(speaker_wav_bytes)
            tmp_path = tmp.name

        try:
            print(f"Generating audio for text: {text[:50]}...")
            audio = self.tts.tts(
                text=text,
                speaker_wav=tmp_path,
                language=language,
            )
            
            # Convert the raw numpy array back into WAV bytes
            buf = io.BytesIO()
            sf.write(buf, audio, samplerate=22050, format="WAV")
            return buf.getvalue()
        finally:
            # Always clean up temp files
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
