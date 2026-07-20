# Benchmarking ASR models for medical use

## Organization

- `scripts_parakeet` contains instructions and scripts to use NVIDIA [parakeet-tdt-0.6b-v3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3): Multilingual Speech-to-Text Model for Automatic Speech Recognition

- `scripts_simsamu` contains instructions and scripts to preprocess to benchmark models with the [simsamu dataset](https://huggingface.co/datasets/medkit/simsamu)

- `scripts_evaluation` contains instructions and scripts to compute evaluation metrics. ⚠️ Under construction ⚠️

Each subdirectory has its own `README.md` with instructions.

# General requirements

- Python >3.9

Tested with Python 3.12.13

Install required packages:

```bash
pip install requirements.txt
```

# Other files

- `figuring_out.ipynb` contains information about the models, requirements etc.

- `results.csv` contains evaluation results on the SIMSAMU dataset for the models tested - ⚠️ Under construction ⚠️

- `requirements.txt`