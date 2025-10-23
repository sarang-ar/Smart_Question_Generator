import re

def classify_difficulty(question):
    # Tokenize using simple regex (splits on word boundaries)
    words = re.findall(r"\b\w+\b", question)
    length = len(words)

    if length == 0:
        return "Unknown"

    avg_word_len = sum(len(w) for w in words) / length

    if length <= 8 and avg_word_len <= 5:
        return "Easy"
    elif length <= 12:
        return "Moderate"
    else:
        return "Hard"