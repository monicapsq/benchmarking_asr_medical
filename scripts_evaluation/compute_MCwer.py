import jiwer
import json
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

    def resolve_ground_truth_path(hypothesis_path: Path) -> Path | None:
        """Find matching .json file for a given .txt hypothesis file"""
        target_name = f"{hypothesis_path.stem}_annotated.json"

        candidate = ground_truth / target_name
        if candidate.exists():
            return candidate
        
        matches = list(ground_truth.rglob(target_name))
        return matches[0] if matches else None

    def extract_gt_from_json(json_path: Path) -> tuple[list[str], list[str]]:
        """Extract ground truth text from the JSON file"""
        with json_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        ref_words = []
        is_medical_flags = []

        for turn in data.get("monologues", []):
            for term in turn.get("terms", []):
                if term.get("type") == "WORD" and "text" in term:
                    word = term["text"].strip()
                    if word:
                        ref_words.append(word)
                        is_medical_flags.append(term.get("is_medical", False))

        return ref_words, is_medical_flags

    def compute_mwer():
        per_file_results = []
        total_med_ref_counts = 0
        total_med_errors = 0

        for hypothesis_path in sorted(hypothesis.rglob("*.txt")):
            ground_truth_path = resolve_ground_truth_path(hypothesis_path)
            if ground_truth_path is None:
                print(f"Ground truth JSON not found for {hypothesis_path}. Skipping.")
                continue

            # Load hypothesis text
            with hypothesis_path.open("r", encoding="utf-8") as hyp_file:
                hypothesis_text = hyp_file.read().strip()

            # Load ground truth text and medical flags from JSON
            ref_words, is_medical_flags = extract_gt_from_json(ground_truth_path)
            ground_truth_text = " ".join(ref_words)

            if not ref_words:
                continue  # Skip if no reference words found

            # Run jiwer word-level alignment
            out = jiwer.process_words(ground_truth_text, hypothesis_text)

            # Analyze the alignment specifically for medical terms
            med_hits = 0
            med_subs = 0
            med_del = 0
            med_ins = 0

            alignment_chunks = out.alignments[0]

            for chunk in alignment_chunks:
                if chunk.type == "equal":
                    # Match: check if reference tokens are medical
                    for ref_idx in range(chunk.ref_start_idx, chunk.ref_end_idx):
                        if is_medical_flags[ref_idx]:
                            med_hits += 1
                elif chunk.type == "substitute":
                    # Substitution: check if reference tokens are medical
                    for ref_idx in range(chunk.ref_start_idx, chunk.ref_end_idx):
                        if is_medical_flags[ref_idx]:
                            med_subs += 1
                elif chunk.type == "delete":
                    # Deletion: check if reference tokens are medical
                    for ref_idx in range(chunk.ref_start_idx, chunk.ref_end_idx):
                        if is_medical_flags[ref_idx]:
                            med_del += 1
                # elif chunk.type == "insert":
                    # Insertion: count as error (hypothesis has extra words)
                    # We count all insertions as errors in medical context
                    # med_ins += chunk.hyp_end_idx - chunk.hyp_start_idx

            # Count total medical reference words
            file_med_ref_count = sum(is_medical_flags)
            total_med_ref_counts += file_med_ref_count

            # Calculate medical errors (substitutions + deletions + insertions)
            file_med_errors = med_subs + med_del + med_ins
            total_med_errors += file_med_errors

            # Calculate file-level mWER
            file_mwer = (med_subs + med_del + med_ins) / file_med_ref_count if file_med_ref_count > 0 else 0.0

            per_file_results.append((hypothesis_path.name, file_mwer, file_med_ref_count))

        if not per_file_results:
            print(f"No matching .txt/.json pairs found in {hypothesis}. Nothing to score.")
            return [], 0.0

        # Calculate dataset-level mcWER (micro-averaged)
        dataset_mcwer = (total_med_errors / total_med_ref_counts) if total_med_ref_counts > 0 else 0.0

        return per_file_results, dataset_mcwer

    per_file_results, dataset_mcwer = compute_mwer()

    print("Per-file Medical Concept WERs (MC-WER):")
    for filename, mwer, med_word_count in per_file_results:
        print(
        f"{filename}: MC-WER = {mwer:.4f} (Medical Words: {med_word_count})"
        )

    print(f"\nDataset Medical Concept WER (Micro-averaged): {dataset_mcwer:.4f}")

    mwer_values = [res[1] for res in per_file_results]
    print(f"Mean MC-WER: {mean(mwer_values):.4f}")



if __name__ == "__main__":
    main()