import argparse
import shutil
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Path to the dataset directory containing audio files")
    parser.add_argument("--output", type=str, required=True, help="Path to save audio files")
    args = parser.parse_args()

    # Organizes and copies the raw .m4a files to the target folder
    organize_m4a_files(args.input, args.output)


def organize_m4a_files(input_dir: str, output_dir: str):
    """Recursively finds all .m4a files and copies them to a flat output folder."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # Ensure the output directory exists
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Scanning {input_path} for .m4a files...")
    
    # Recursively find all files ending in .m4a
    m4a_files = list(input_path.rglob("*.m4a"))
    
    if not m4a_files:
        print("No .m4a files found.")
        return

    copied_count = 0
    for file_path in m4a_files:
        # Create a unique name in case different folders have files with the same name
        # e.g., "dj_2022_brulures/audio.m4a" -> "dj_2022_brulures_audio.m4a"
        parent_dir_name = file_path.parent.name
        new_filename = f"{parent_dir_name}_{file_path.name}"
        destination = output_path / new_filename

        # Copy the file without modifying its metadata or audio contents
        shutil.copy2(file_path, destination)
        copied_count += 1

    print(f"Successfully copied {copied_count} files to {output_path}")

if __name__ == "__main__":
    main()