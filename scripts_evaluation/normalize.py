from pathlib import Path
import argparse
import re
from text_to_num import text2num
from number2text.number2text import NumberToText
# from nltk.corpus import stopwords
import jiwer

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Path to the directory of input text file")
    parser.add_argument("--output", type=str, required=True, help="Path to directory to save the normalized text files")
    args = parser.parse_args()

    # Load input text files and prepare the output path
    input_path = Path(args.input)
    output_path = Path(args.output)

    class TransformHours(jiwer.transforms.AbstractTransform):
        def process_string(self, txt: str):
            new_txt = re.sub(r"(\d+)\s*(h)eures", r"\1\2", txt)
            pattern = re.compile(r"(\d{1,2}h)\s(\d{2}[^h])", flags=re.MULTILINE)
            return pattern.sub(r"\1\2", new_txt)

    class TransformNum2Text(jiwer.transforms.AbstractTransform):
        def process_string(self, txt: str):
            converter = NumberToText(language="fr")
            new_txt = []
            for w in txt.split():
                try:
                    int_nb = int(w)
                    new_txt.append(converter.convert(int_nb))
                except:
                    new_txt.append(w)
            return " ".join(new_txt)

    # Compose pipeline
    NORMALIZATION_PIPELINE = jiwer.Compose([
        jiwer.RemoveEmptyStrings(),
        jiwer.ToLowerCase(),
        # jiwer.RemoveMultipleSpaces(),
        jiwer.Strip(),
        jiwer.RemovePunctuation(),
        jiwer.SubstituteRegexes({r"oe": r"œ"}),
        TransformHours(),
        TransformNum2Text(),
    ])

    # Create a clean wrapper function to normalize strings on-the-fly
    def normalize_text(text: str) -> str:
        # Run the pipeline
        word_list = NORMALIZATION_PIPELINE(text)
        # Reconstruct back into a clean string sentence
        # return " ".join(word_list)
        return word_list
        # Normalize
        # files = normalize(files)

if __name__ == "__main__":
    main()
