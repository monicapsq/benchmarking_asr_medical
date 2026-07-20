from pathlib import Path

from codecarbon import OfflineEmissionsTracker # Using the same emissions tracker as Stephanie's

import argparse
import time
import nemo.collections.asr as nemo_asr

tracker = OfflineEmissionsTracker(country_iso_code="FRA")
tracker.start()

start = time.time()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, required=True, help="Path to a local .nemo checkpoint") # Found with `find ~ -name "parakeet-tdt-0.6b-v3.nemo"`
    parser.add_argument("--input", type=str, required=True, help="Path to the audio file to transcribe")
    parser.add_argument("--output", type=str, required=True, help="Path to save the transcription output")
    args = parser.parse_args()

    # Load model
    asr_model = load_model(args.model_path)

    # Load input audio and prepare the output path
    input_path = Path(args.input)
    output_path = Path(args.output)

    if input_path.is_dir():
        output_path.mkdir(parents=True, exist_ok=True)
        audios = [str(f) for f in (input_path.iterdir()) if f.is_file() and f.suffix.lower() in {".wav", ".m4a", ".flac", ".mp3"}]
    else:
        audios = [str(input_path)]

    """# Transcribe
    transcriptions = asr_model.transcribe(audios, batch_size=1)[0]

    for audio_path_str, transcription in zip(audios, transcriptions):
        current_audio_path = Path(audio_path_str)

        # Extract text out of Hypothesis object if needed
        text = transcription.text if hasattr(transcription, "text") else str(transcription)

        output_file = output_path / (current_audio_path.stem + ".txt") if input_path.is_dir() else output_path
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)"""

    for audio in audios:
        # Transcribe 
        # get hypothesis object from NeMo parakeet
        hypothesis = asr_model.transcribe([audio])
        # Extract text out of Hypothesis object 
        transcription = hypothesis[0].text if hasattr(hypothesis[0], "text") else str(hypothesis[0])

        # Save transcription
        if input_path.is_dir():
            output_file = output_path / (Path(audio).stem + ".txt")
        else:
            output_file = output_path
            output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcription)

def load_model(model_path: str):
    """Load NeMo parakeet from a local .nemo checkpoint."""

    model_path_obj = Path(model_path)
    if not model_path_obj.exists():
        raise FileNotFoundError(f"Model checkpoint not found: {model_path_obj}")
    if model_path_obj.suffix != ".nemo":
        raise ValueError("model_path must point to a local .nemo file")

    return nemo_asr.models.ASRModel.restore_from(str(model_path_obj))
    
if __name__ == "__main__":
    main()
    end = time.time()
    print(f"Processing time: {end - start} seconds")
    tracker.stop()