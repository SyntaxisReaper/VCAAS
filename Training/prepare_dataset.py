import argparse
import json
import os
from pathlib import Path

def generate_manifest(data_root, output_file, language="en"):
    """
    Generates a JSONL manifest for Coqui TTS fine-tuning.
    Expects either:
      - speaker folders: <data_root>/<speaker_name>/<name>.wav and <name>.txt
      - flat layout: <data_root>/<name>.wav and <name>.txt
    """
    data_path = Path(data_root)
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    manifest_entries = []

    # Find all .wav files in the data_root directory
    for wav_file in data_path.rglob("*.wav"):
        txt_file = wav_file.with_suffix(".txt")
        
        if not txt_file.exists():
            print(f"Warning: No transcription found for {wav_file}, skipping.")
            continue
        
        with open(txt_file, "r", encoding="utf-8") as f:
            text = f.read().strip()
            
        # Determine speaker name
        # If flat layout, speaker name is "default_speaker"
        # If in a subfolder, use the subfolder name as speaker name
        rel_path = wav_file.relative_to(data_path)
        if len(rel_path.parts) > 1:
            speaker_name = rel_path.parts[0]
        else:
            speaker_name = "default_speaker"
            
        entry = {
            "audio_file": str(wav_file.absolute()),
            "text": text,
            "speaker_name": speaker_name,
            "language": language
        }
        manifest_entries.append(entry)

    if not manifest_entries:
        print(f"No valid wav/txt pairs found in {data_root}.")
        return

    with open(output_path, "w", encoding="utf-8") as f:
        for entry in manifest_entries:
            f.write(json.dumps(entry) + "\n")
            
    print(f"Successfully generated manifest with {len(manifest_entries)} entries at {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare dataset for XTTS fine-tuning")
    parser.add_argument("--data-root", type=str, required=True, help="Path to the root folder of audio and txt files")
    parser.add_argument("--out", type=str, required=True, help="Output path for the jsonl manifest file")
    parser.add_argument("--lang", type=str, default="en", help="Language code (e.g. 'en')")
    args = parser.parse_args()

    generate_manifest(args.data_root, args.out, args.lang)
