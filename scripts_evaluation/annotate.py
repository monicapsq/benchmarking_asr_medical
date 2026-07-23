import json

# with open("path/to/.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Flatten words for linear indexing
words = []
for turn in data.get("monologues", []):
    speaker = turn.get("speaker", {}).get("id", "Unknown")
    for term in turn.get("terms", []):
        if term.get("type") == "WORD":
            words.append((speaker, term))

idx = 0
print(
    "\n--- Navigation: 'y' = Medical | ENTER = Skip | 'b' = Back | 'q' = Save & Quit ---\n"
)

while 0 <= idx < len(words):
    speaker, term = words[idx]
    word_text = term.get("text", "")
    current_status = "[MEDICAL]" if term.get("is_medical") else "[NORMAL]"

    cmd = (
        input(
            f"[{idx+1}/{len(words)}] [{speaker}] '{word_text}' {current_status} -> (y/N/b/q): "
        )
        .strip()
        .lower()
    )

    if cmd == "q":
        break
    elif cmd == "b":
        if idx > 0:
            idx -= 1
        else:
            print("Already at the first word!")
    elif cmd == "y":
        term["is_medical"] = True
        idx += 1
    else:
        term["is_medical"] = False
        idx += 1

# with open("path/to/_annotated.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("\n💾 Progress saved successfully!")