import argparse
import os

from trainer import Trainer, TrainerArgs
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.datasets import load_tts_samples
from TTS.tts.models.xtts import Xtts
from TTS.config.shared_configs import BaseDatasetConfig

def train_model(manifest_path, output_dir, epochs=2, batch_size=1, grad_accum=8, lang="en"):
    # Output path
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Dataset Config
    dataset_config = BaseDatasetConfig(
        formatter="ljspeech", # Since we generate a simple jsonl or custom, we map to standard dataset format 
        # For XTTS we use our own dataset format parser, JSONL is parsed differently or via standard list
        meta_file_train=manifest_path,
        language=lang
    )

    # 2. Xtts Config
    config = XttsConfig(
        batch_size=batch_size,
        eval_batch_size=batch_size,
        num_loader_workers=2,
        num_eval_loader_workers=2,
        run_eval=True,
        test_delay_epochs=-1,
        epochs=epochs,
        text_cleaner="multilingual_cleaners",
        use_phonemes=False,
        phoneme_language=lang,
        phoneme_cache_path=os.path.join(output_dir, "phoneme_cache"),
        compute_input_seq_cache=True,
        print_step=25,
        print_eval=True,
        mixed_precision=True,
        output_path=output_dir,
        datasets=[dataset_config],
    )
    
    # Enable gradient accumulation for low VRAM
    config.optimizer_params["accumulate_grad_batches"] = grad_accum

    # 3. Load model and set it up for fine-tuning
    # XTTS v2 requires the base model to be downloaded or provided
    model = Xtts.init_from_config(config)
    
    # 4. Load train and eval samples
    train_samples, eval_samples = load_tts_samples(
        dataset_config,
        eval_split=True,
        eval_split_max_size=config.eval_split_max_size,
        eval_split_size=config.eval_split_size,
    )

    # 5. Initialize trainer
    trainer = Trainer(
        TrainerArgs(),
        config,
        output_path=output_dir,
        model=model,
        train_samples=train_samples,
        eval_samples=eval_samples,
    )

    # 6. Start Training
    trainer.fit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine-tune XTTS v2 model")
    parser.add_argument("--manifest", type=str, required=True, help="Path to train.jsonl")
    parser.add_argument("--output-dir", type=str, required=True, help="Output directory for checkpoints")
    parser.add_argument("--epochs", type=int, default=2, help="Number of epochs to train")
    parser.add_argument("--batch-size", type=int, default=1, help="Batch size per GPU")
    parser.add_argument("--grad-accum", type=int, default=8, help="Gradient accumulation steps")
    parser.add_argument("--lang", type=str, default="en", help="Language code")
    args = parser.parse_args()

    train_model(
        manifest_path=args.manifest,
        output_dir=args.output_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        grad_accum=args.grad_accum,
        lang=args.lang
    )
