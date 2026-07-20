# [SIMSAMU dataset](https://huggingface.co/datasets/medkit/simsamu) related scripts

# Get the dataset

For offline use:

```bash
python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='medkit/simsamu', repo_type='dataset', local_dir='/path/to/local/dataset/empty/dir')"
```
# Helper/optional scripts for preprocessing

## Preprocess subtitle transcriptions (`.srt`)

`preprocess_srt.py` converts every `.srt` file in the SIMSAMU dataset into a plain-text `.txt` file.
With regular expressions, it removes subtitle indexes, timestamps, HTML-like tags, and keeps one subtitle turn per line.

Usage:

```bash
python preprocess_srt.py --dataset_dir /path/to/local/dataset
```

By default, the cleaned `.txt` files are written next to the original transcripts inside the same dataset tree.

To keep the original dataset untouched, provide an output directory:

```bash
python preprocess_srt.py --dataset_dir /path/to/local/dataset --output_dir /path/to/ouput/directory
```

## Put all audio files into the same directory

`prepare_simsamu_audios.py` takes care of iterating through the original dataset structure, fetch the `.m4a` files and copy them into a dedicated folder.

Usage:
```bash
python prepare_simsamu_audios.py --input /path/to/local/dataset --output path/to/output/directory