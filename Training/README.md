# VCaaS Training Pipeline (XTTS v2 fine-tuning)

This folder contains scripts to prepare your dataset and kick off a small-footprint fine-tune of Coqui XTTS v2 suitable for ~4GB VRAM GPUs.

Requirements
- Python packages: torch (CUDA build), TTS, librosa, soundfile, numpy
- Data layout under Training/: either
  - speaker folders: Training/<SPEAKER_NAME>/*.wav with matching .txt transcriptions, or
  - flat layout with pairs <name>.wav and <name>.txt

Steps
1) Prepare manifest
```
python Training/prepare_dataset.py --data-root Training --out Training/processed/train.jsonl --lang en
```

2) Start fine-tune (tiny settings, gradient accumulation)
```
python Training/train_xtts.py ^
  --manifest Training/processed/train.jsonl ^
  --output-dir Training/runs/xtts_small ^
  --epochs 2 --batch-size 1 --grad-accum 8 --lang en
```
Note: first run downloads base model weights (~1–2GB). With 4GB VRAM, keep batch-size 1 and use grad-accum.

3) Use the fine-tuned checkpoint
- The trainer will save a best checkpoint in the run directory. To clone using it:
```
curl -X POST http://localhost:8000/api/tts/clone/warmup
curl -X POST http://localhost:8000/api/tts/clone ^
  -F "text=Hello from my finetuned voice" ^
  -F "language=en" ^
  -F "reference=@Training/sample_ref.wav" ^
  -F "model_dir=Training/runs/xtts_small/best_model"
```

Tips
- Ensure audio is 16–22.05kHz mono WAV for best results; keep clips 3–15s and transcripts clean.
- To extend training, increase epochs and consider multiple speakers.
- For stronger results, migrate to Linux + newer GPU, then raise batch size and enable mixed precision.
