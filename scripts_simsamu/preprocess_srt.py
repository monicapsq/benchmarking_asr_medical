import argparse
import re
from pathlib import Path


SRT_TIMESTAMP_RE = re.compile(r"^\s*\d{2}:\d{2}:\d{2},\d{3}\s+-->\s+\d{2}:\d{2}:\d{2},\d{3}\s*$") # Subtitle timestamp pattern (e.g., "00:01:23,456 --> 00:01:25,789")

def parse_args() -> argparse.Namespace: # Parsing command-line arguments for the script
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset_dir", type=str, required=True, help="Path to the SIMSAMU dataset root")
    parser.add_argument(
        "--output_dir",
        type=str,
        default=None,
        help="Where to write cleaned transcript files. Defaults to the dataset root.",
    )
    return parser.parse_args()

def preprocess_transcripts(text: str) -> str:
    """Clean SRT subtitles into plain text for future evaluation."""
    turns = [] # Keeping each turn in a new line

    for block in re.split(r"\n\s*\n", text.strip()): # Split the text into blocks separated by empty lines
        block_lines = []

        for raw_line in block.splitlines():
            line = raw_line.strip() # Remove leading/trailing whitespace
            if not line:
                continue
            line = re.sub(
                r"^\s*\d{2}:\d{2}:\d{2},\d{3}\s+-->\s+\d{2}:\d{2}:\d{2},\d{3}\s*", # Remove subtitle timestamps from the beginning of the line
                "",
                line,
            )
            line = re.sub(r"^\s*\d+\s*", "", line) # Remove subtitle/line numbers from the beginning of the line

            line = re.sub(r"<[^>]+>", "", line) # Remove any HTML-like tags (e.g., <i>, <b>, etc.)
            line = line.replace("\ufeff", "").strip() # Remove BOM character and strip whitespace
            if line:
                block_lines.append(line)

        if block_lines:
            turn = re.sub(r"\s+", " ", " ".join(block_lines)).strip() # Replace multiple whitespace characters with a single space and join the lines into a single turn
            if turn:
                turns.append(turn)

    return "\n".join(turns) # Return the cleaned text with each turn on a new line


def convert_srt_files(dataset_path: Path, output_dir: Path) -> list[Path]:
    written_files: list[Path] = [] # List to keep track of the written output files

    for srt_path in sorted(dataset_path.rglob("*.srt")): # Recursively find all .srt files in the dataset directory (they are all .srt in SIMSAMU)
        relative_path = srt_path.relative_to(dataset_path) # Get the relative path of the .srt file with respect to the dataset root
        output_path = output_dir / relative_path.with_suffix(".txt") # Change the suffix to .txt for the output file
        output_path.parent.mkdir(parents=True, exist_ok=True) # Create the parent directories for the output file if they don't exist

        cleaned_text = preprocess_transcripts(srt_path.read_text(encoding="utf-8-sig")) # Read the .srt file, clean it, and store the cleaned text

        output_path.write_text(cleaned_text + ("\n" if cleaned_text else ""), encoding="utf-8") #  Write the cleaned text to the output file, adding a newline at the end if the cleaned text is not empty
        written_files.append(output_path) # Add the output file path to the list of written files

    return written_files


def main() -> None: # Main function to handle the conversion of SRT files to cleaned text files
    args = parse_args()
    dataset_path = Path(args.dataset_dir).expanduser().resolve() # Resolve the dataset path to an absolute path, expanding any user (~) references
    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else dataset_path # Resolve the output directory to an absolute path, expanding any user (~) references. If not provided, use the dataset path

    if not dataset_path.exists(): # Check if the dataset path exists, and raise an error if it doesn't
        raise FileNotFoundError(f"Dataset path does not exist: {dataset_path}")

    
    written_files = convert_srt_files(dataset_path, output_dir) # Call the function to convert the SRT files to cleaned text files and store the list of written output files
    
    # Confirmation messages to comment out if needed
    # print(f"Converted {len(written_files)} subtitle files to plain text") 
    # print(f"Output directory: {output_dir}")

if __name__ == "__main__":
    main()