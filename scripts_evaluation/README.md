# Evaluation pipeline

## Normalizing

`normalize.py` normalizes any text file with the guidelines of the original project. ⚠️ Work in progress ⚠️

Usage:

```bash
python normalize.py --input path/to/input/dir/of/txts --output path/to/output/dir/of/txts
```

## Computing Word Error Rate (WER)

`compute_wer.py` is a general script for calculating Word Error Rate (WER) in filename-matching text files. Resulting WER is printed in the terminal. It is highly suggested to normalize the transcriptions beforehand not to bias the resulting score.

Usage:
```bash
python compute_wer.py -h path/to/dir/of/hypothesis/transcriptions -gt path/to/dir/of/ground_truth/transcriptions
``` 

## Computing MC-WER ([Adedeji et. al, 2024](https://arxiv.org/abs/2402.07658)) ⚠️ Work in progress ⚠️

Medical Concept Word Error Rate (MC-WER) is an evaluation metric that computes WER related to Substitutions, Insertions or Deletions of medically relevant words. 

The script `annotate.py` is a helper for JSON-based transcriptions like those of the SIMSAMU dataset, to test MC-WER. To use it it is needed to insert the path to the `.json` file to edit.

Actual computing of MC-WER is ⚠️ Work in progress ⚠️
