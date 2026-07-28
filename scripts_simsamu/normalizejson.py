from pathlib import Path
import argparse
import re
from text_to_num import text2num
from number2text.number2text import NumberToText
import json
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

    class TransformText2Num(jiwer.transforms.AbstractTransform):
        def process_string(self, txt: str):
            def convert_token(token: str) -> str:
                try:
                    return str(text2num(token, "fr"))
                except ValueError:
                    return token 
                
            tokens = txt.split()
            return " ".join(convert_token(token) for token in tokens)
        
    class TransformNum2Text(jiwer.transforms.AbstractTransform):
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
        jiwer.SubstituteRegexes({r"oe": r"œ"}), # Aligning to Stéphanie's
        TransformHours(), 
        TransformText2Num(), # Chriffres en chiffres
        TransformNum2Text(),
        jiwer.RemovePunctuation(), # pas de ponctuation after transforming text to digits
    ])

    # Wrapper to normalize
    def normalize_text(text: str) -> str:
        if not text:
            return ""
        res = NORMALIZATION_PIPELINE(text)
        return res if isinstance(res, str) else "".join(res)  # Ensure the result is a string, even if it's a list

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
    for input_file in input_path.rglob("*.json"):
        with input_file.open("r", encoding="utf-8") as f:
            data = json.load(f)

        for monologue in data.get("monologues", []):
            for term in monologue.get("terms", []):
                if term.get("type") == "WORD" and "text" in term:
                    normalized_word = normalize_text(term["text"])  
                    term["text"] = normalized_word # preserve "is_medical: true" when normalizing

        # Save the normalized text to the output directory with the same filename
        output_file = output_path / output_filename(input_file)
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
