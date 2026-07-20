import argparse
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from pydub import AudioSegment

import nemo.collections.asr as nemo_asr

@dataclass
class Sample: # Represents a single audio/transcript pair for ASR training
    audio_path: Path # Expected path rather than string
    transcript_path: Path # Idem
    text: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_path",
        type=str,
        required=True,
        help="Path to a local .nemo checkpoint. Required for offline use.",
    )
    parser.add_argument("--audio_dir", type=str, required=True, help="Path to the dataset root containing .m4a files")
    parser.add_argument(
        "--transcript_dir",
        type=str,
        required=True,
        help="Path to the root containing preprocessed .txt transcripts",
    )
    parser.add_argument("--output_dir", type=str, default="./outputs", help="Where to store manifests and resampled audio")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible splits")
    parser.add_argument("--skip_training", action="store_true", help="Only prepare data and stop")
    return parser.parse_args()


def discover_samples(audio_dir: Path, transcript_dir: Path) -> List[Sample]:
    """Discover paired .m4a audio and cleaned .txt transcript files from separate roots."""
    samples: List[Sample] = []

    audio_files = {path.stem: path for path in audio_dir.rglob("*.m4a") if path.is_file()}
    transcript_files = {path.stem: path for path in transcript_dir.rglob("*.txt") if path.is_file()}

    for stem in sorted(audio_files.keys() & transcript_files.keys()):
        audio_path = audio_files[stem]
        transcript_path = transcript_files[stem]
        text = transcript_path.read_text(encoding="utf-8").strip()
        samples.append(Sample(audio_path=audio_path, transcript_path=transcript_path, text=text))

    return samples


def resample_audio(input_path: Path, output_path: Path, sample_rate: int = 16000) -> Path:
    """Resample audio to 16kHz and export it as PCM WAV for NeMo training."""
    audio = AudioSegment.from_file(str(input_path))
    audio = audio.set_frame_rate(sample_rate).set_channels(1) # Change sample rate and convert to mono
    output_path.parent.mkdir(parents=True, exist_ok=True)
    audio.export(str(output_path), format="wav")
    return output_path


def build_manifest(samples: List[Sample], manifest_path: Path, output_dir: Path) -> List[Path]:
    """Create a manifest file and resampled wav copies for the samples."""
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    resampled_dir = output_dir / "resampled"
    resampled_dir.mkdir(parents=True, exist_ok=True)

    written_files: List[Path] = []
    with manifest_path.open("w", encoding="utf-8") as handle:
        for sample in samples:
            output_wav = resampled_dir / f"{sample.audio_path.stem}.wav"
            resampled_audio = resample_audio(sample.audio_path, output_wav)
            audio_duration = AudioSegment.from_file(str(resampled_audio)).duration_seconds

            row = {
                "audio_filepath": str(resampled_audio),
                "duration": audio_duration,
                "text": sample.text,
            }
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            written_files.append(resampled_audio)

    return written_files


def split_manifest(
    manifest_path: Path,
    output_dir: Path,
    val_ratio: float,
    test_ratio: float,
    seed: int,
) -> tuple[Path, Path, Path]:
    """Split one manifest into train/validation/test manifests."""
    if not 0 < val_ratio + test_ratio < 1:
        raise ValueError("val_ratio + test_ratio must be between 0 and 1")

    rows = [line.strip() for line in manifest_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    rng = random.Random(seed)
    rng.shuffle(rows)

    n_val = int(len(rows) * val_ratio)
    n_test = int(len(rows) * test_ratio)
    n_train = len(rows) - n_val - n_test

    train_rows = rows[:n_train]
    val_rows = rows[n_train:n_train + n_val]
    test_rows = rows[n_train + n_val:]

    output_dir.mkdir(parents=True, exist_ok=True)
    train_path = output_dir / "train_manifest.json"
    val_path = output_dir / "val_manifest.json"
    test_path = output_dir / "test_manifest.json"

    for path, rows_to_write in [(train_path, train_rows), (val_path, val_rows), (test_path, test_rows)]:
        path.write_text("\n".join(rows_to_write) + ("\n" if rows_to_write else ""), encoding="utf-8")

    return train_path, val_path, test_path


def load_model(model_path: str):
    """Load a NeMo ASR model from a local .nemo checkpoint."""

    model_path_obj = Path(model_path)
    if not model_path_obj.exists():
        raise FileNotFoundError(f"Model checkpoint not found: {model_path_obj}")
    if model_path_obj.suffix != ".nemo":
        raise ValueError("model_path must point to a local .nemo file")
    return nemo_asr.models.ASRModel.restore_from(str(model_path_obj))


def train_model(model, train_manifest: Path, val_manifest: Optional[Path], output_dir: Path) -> None:
    """Hook for the actual NeMo training setup.

    In practice, the exact config depends on the NeMo version you install.
    The important architectural point is that data preparation, splitting and
    model loading happen before this step.
    """
    print("Model loading completed.")
    print(f"Train manifest: {train_manifest}")
    if val_manifest is not None:
        print(f"Validation manifest: {val_manifest}")
    print(f"Output directory: {output_dir}")
    print("Add your version-specific NeMo training config here, for example by calling setup_training_data/setup_validation_data and then trainer.fit().")


def main() -> None:
    args = parse_args()
    audio_dir = Path(args.audio_dir).expanduser().resolve()
    transcript_dir = Path(args.transcript_dir).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    samples = discover_samples(audio_dir, transcript_dir)
    if not samples:
        raise RuntimeError(f"No compatible audio/transcript pairs were found between {audio_dir} and {transcript_dir}")

    manifest_path = output_dir / "manifest.jsonl"
    build_manifest(samples, manifest_path, output_dir)

    train_manifest, val_manifest, test_manifest = split_manifest(
        manifest_path=manifest_path,
        output_dir=output_dir,
        val_ratio=0.10,
        test_ratio=0.10,
            seed=args.seed,
    )

    print(f"Prepared {len(samples)} samples")
    print(f"Train manifest: {train_manifest}")
    print(f"Validation manifest: {val_manifest}")
    print(f"Test manifest: {test_manifest}")

    if args.skip_training:
        return

    model = load_model(args.model_path)
    train_model(model, train_manifest, val_manifest, output_dir)


if __name__ == "__main__":
    main()