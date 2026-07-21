from pathlib import Path
import argparse
import re
from text_to_num import text2num
from number2text.number2text import NumberToText
# from nltk.corpus import stopwords
import jiwer
# import unidecode

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Path to the directory of input text file")
    parser.add_argument("--output", type=str, required=True, help="Path to directory to save the normalized text files")
    args = parser.parse_args()

    # Load input text files and prepare the output path
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    class TransformHours(jiwer.transforms.AbstractTransform): # From Stéphanie's normalization script
        def process_string(self, txt: str):
            new_txt = re.sub(r"(\d+)\s*(h)eures", r"\1\2", txt)
            pattern = re.compile(r"(\d{1,2}h)\s(\d{2}[^h])", flags=re.MULTILINE)
            return pattern.sub(r"\1\2", new_txt)

    # class RemoveAccents(jiwer.transforms.AbstractTransform): # From Stéphanie's normalization script
    #     def process_string(self, txt: str):
    #         new_txt = unidecode(txt, "utf-8")
    #         return new_txt

    class TransformText2Num(jiwer.transforms.AbstractTransform): # From Stéphanie's normalization script
        def process_string(self, txt: str):
            new_txt = txt
            splitted_txt = txt.split()
            for i, t in enumerate(splitted_txt):
                if i+1 < len(splitted_txt):
                    if splitted_txt[i+1] in ["mois", "jours", "an", "ans"]:
                        try:
                            textual_nb = str(text2num(t, "fr"))
                            new_txt = new_txt.replace(t, textual_nb)
                        except ValueError:
                            pass
                if i+2 < len(splitted_txt):
                    if splitted_txt[i+2] in ["mois", "jours", "an", "ans", "heures"]:
                        try:
                            textual_nb = str(text2num(t, "fr"))
                            new_txt = new_txt.replace(t, textual_nb)
                        except ValueError:
                            pass
            return new_txt
        
    class TransformNum2Text(jiwer.transforms.AbstractTransform): # From Stéphanie's normalization script
        def process_string(self, txt: str):
            converter = NumberToText(language="fr")

            # Convert a number to text
            new_txt = []
            for w in txt.split():
                try:
                    int_nb = int(w)
                    str_nb = converter.convert(int_nb)
                    new_txt.append(str_nb)
                except:
                    new_txt.append(w)
            return " ".join(new_txt)


    # Compose pipeline
    NORMALIZATION_PIPELINE = jiwer.Compose([
        jiwer.RemoveEmptyStrings(),
        jiwer.ToLowerCase(), # pas de majuscule 
        # jiwer.RemoveMultipleSpaces(),
        jiwer.Strip(), # Removes leading and trailing spaces
        jiwer.RemovePunctuation(), # pas de ponctuation
        jiwer.SubstituteRegexes({r"oe": r"œ"}), # Aligning to Stéphanie's
        TransformHours(), 
        TransformText2Num(), # Chriffres en chiffres
        TransformNum2Text(),
    ])

    # Wrapper to normalize
    def normalize_text(text: str) -> str:
        return NORMALIZATION_PIPELINE(text)

    def output_filename(input_file: Path) -> str:
        stem_parts = input_file.stem.split("_")
        if len(stem_parts) % 2 == 0:
            half = len(stem_parts) // 2
            if stem_parts[:half] == stem_parts[half:]:
                return "_".join(stem_parts[:half]) + input_file.suffix
        return input_file.name

    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Process each input text file, including files in subdirectories
    for input_file in input_path.rglob("*.txt"):
        with input_file.open("r", encoding="utf-8") as file_handle:
            normalized_text = normalize_text(file_handle.read()) # normalize

        # Save the normalized text to the output directory with the same filename
        output_file = output_path / output_filename(input_file)
        with output_file.open("w", encoding="utf-8") as file_handle:
            file_handle.write(normalized_text)

if __name__ == "__main__":
    main()
