import jiwer
import argparse
from pathlib import Path
from statistics import mean, median, stdev

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h", type=str, required=True, help="Path to the directory of ASR transcriptions")
    parser.add_argument("--gt", type=str, required=True, help="Path to directory containing ground truth transcriptions")
    args = parser.parse_args()

    # Load input text files (hypothesis and ground truth)
    hypothesis = Path(args.h) 
    ground_truth = Path(args.gt)

    # Help identify matching ground truth file for a given hypothesis file
    def resolve_ground_truth_path(hypothesis_path: Path) -> Path | None:
        relative_path = hypothesis_path.relative_to(hypothesis)

        candidate = ground_truth / relative_path
        if candidate.exists():
            return candidate

        candidate = ground_truth / hypothesis_path.name
        if candidate.exists():
            return candidate

        matches = list(ground_truth.rglob(hypothesis_path.name))
        if matches:
            return matches[0]

        return None

    def compute_wer() -> list[tuple[Path, Path, float]]:
        per_file_wers: list[tuple[Path, Path, float]] = []

        for hypothesis_path in sorted(hypothesis.rglob("*.txt")):
            ground_truth_path = resolve_ground_truth_path(hypothesis_path)
            if ground_truth_path is None:
                print(f"Ground truth file not found for {hypothesis_path}. Skipping.")
                continue

            with hypothesis_path.open("r", encoding="utf-8") as hyp_file:
                hypothesis_text = hyp_file.read().strip()

            with ground_truth_path.open("r", encoding="utf-8") as gt_file:
                ground_truth_text = gt_file.read().strip()

            wer_value = jiwer.wer(ground_truth_text, hypothesis_text)
            per_file_wers.append((hypothesis_path, ground_truth_path, wer_value))

        if not per_file_wers:
            raise FileNotFoundError(f"No matching .txt files found in {hypothesis}")

        return per_file_wers
        
    
    print(f"Computing WER for hypothesis: {hypothesis} and ground truth: {ground_truth}")
    per_file_wers = compute_wer()

    print("Per-file WERs:")
    for hypothesis_path, ground_truth_path, wer_value in per_file_wers:
        print(f"{hypothesis_path.name}, {wer_value:.4f}")

    wer_values = [wer_value for _, _, wer_value in per_file_wers]
    print(f"Mean WER: {mean(wer_values):.4f}")
    print(f"Median WER: {median(wer_values):.4f}")
    print(f"Std WER: {stdev(wer_values):.4f}" if len(wer_values) > 1 else "Std WER: 0.0000")


if __name__ == "__main__":
    main()