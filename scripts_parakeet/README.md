# NeMo Parakeet 🦜 usage

## Get the model

⚠️ The documentation tells to install it after you've installed latest PyTorch version, therefore after installing `requirements.txt`, separately run:

```bash
pip install nemo_toolkit[asr]
```
I have version 2.7.3 (should I specify that?)

Then, download the model with the following command:

```bash
python -c "import nemo.collections.asr as nemo_asr; model = nemo_asr.models.ASRModel.from_pretrained(model_name='nvidia/parakeet-tdt-0.6b-v3'); model.save_to('./model/parakeet-tdt-0.6b-v3.nemo')"
```

This download does not need a GPU. It can be done on any machine or login node with internet access. Copy the resulting `.nemo` file to a cluster or shared filesystem.

With this command, a `model/` folder is created to store the checkpoint.

## Transcribe

`transcribe_parakeet.py` takes a directory of recordings and transcribes them using NeMo parakeet 6b.

First, find the path to the model:

```bash
find ~ -name "parakeet-tdt-0.6b-v3.nemo"
```

Then:
```bash
python transcribe_parakeet.py --model_path path/to/model.nemo --input path/to/input/dir --output path/to/output/dir
```