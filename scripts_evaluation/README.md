# Evaluation pipeline

## Normalizing

`normalize.py` normalizes any text file with the guidelines of the original project. ⚠️ unfinished ⚠️

Usage:

```bash
python normalize.py --input path/to/input/dir/of/txts --output path/to/output/dir/of/txts
```

## Computing Word Error Rate (WER)

`compute_wer.py` is a general script for calculating Word Error Rate (WER) in filename-matching text files. Resulting WER is printed in the terminal. It is highly suggested to normalize the transcriptions beforehand not to bias the resulting score.

Usage:
```bash
python compute_wer.py -h path/to/dir/of/hypothesis/transcriptions -gt path/to/dir/of/ground_truth/transcriptions