import jiwer
import argparse
from pathlib import Path

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

    def compute_wer() -> float:
        hypothesis_texts: list[str] = [] # hypotesis txts
        ground_truth_texts: list[str] = [] # matching ground truth txts

        for hypothesis_path in sorted(hypothesis.rglob("*.txt")):
            ground_truth_path = resolve_ground_truth_path(hypothesis_path) # Find the corresponding ground truth file for the hypothesis file
            if ground_truth_path is None:
                print(f"Ground truth file not found for {hypothesis_path}. Skipping.") # Warning if no match is found
                continue

            # Read the hypothesis and ground truth texts
            with hypothesis_path.open("r", encoding="utf-8") as hyp_file:
                hypothesis_texts.append(hyp_file.read().strip())

            with ground_truth_path.open("r", encoding="utf-8") as gt_file:
                ground_truth_texts.append(gt_file.read().strip())

        # Warning if no hypothesis files were found
        if not hypothesis_texts:
            raise FileNotFoundError(f"No matching .txt files found in {hypothesis}")

        return jiwer.wer(ground_truth_texts, hypothesis_texts) # Compute WER
    
    print(f"Computing WER for hypothesis: {hypothesis} and ground truth: {ground_truth}")
    wer_value = compute_wer()
    print(f"WER: {wer_value:.4f}")


if __name__ == "__main__":
    main()