from flask import Flask, render_template, request
from transformers import pipeline
from difficulty_classifier import classify_difficulty
from utils import clean_paragraph

app = Flask(__name__)

# Load model
generator = pipeline("text2text-generation", model="mrm8488/t5-base-finetuned-question-generation-ap")

def is_valid_question(q):
    q = q.strip()
    return (
        len(q.split()) > 4 and
        "true" not in q.lower() and
        "false" not in q.lower() and
        q.lower() not in ["yes", "no"]
    )

def is_unique(q, seen):
    return all(q.lower() != s.lower() and q.lower() not in s.lower() and s.lower() not in q.lower() for s in seen)

def generate_questions(paragraph, selected_level, pool_size=15):
    word_count = len(paragraph.split())
    if word_count < 20:
        return [("⚠️ Please enter a longer or more detailed paragraph.", "Warning")]
    if not any(punct in paragraph for punct in [".", ",", "?", "!"]):
        return [("⚠️ Paragraph seems too abstract. Try adding more descriptive or factual content.", "Warning")]

    seen = []
    filtered = []

    for _ in range(pool_size):
        input_text = f"generate question: {paragraph}"
        result = generator(
            input_text,
            max_length=64,
            do_sample=True,
            temperature=1.0,
            top_k=50,
            top_p=0.95,
            truncation=True
        )
        q = result[0]["generated_text"].strip()
        if is_valid_question(q) and is_unique(q, seen):
            level = classify_difficulty(q)
            if selected_level == "Any" or level == selected_level:
                if level == "Hard" and not q.lower().endswith("explain.") and not q.lower().endswith("explain"):
                    q += " Explain."
                filtered.append((q, level))
                seen.append(q)

    return filtered if filtered else [("⚠️ No unique questions matched the selected difficulty.", "Warning")]

@app.route("/", methods=["GET", "POST"])
def index():
    questions = []
    paragraph = ""
    selected_level = "Any"

    if request.method == "POST":
        paragraph = clean_paragraph(request.form["paragraph"])
        selected_level = request.form["difficulty"]
        questions = generate_questions(paragraph, selected_level)

    return render_template("index.html", questions=questions, paragraph=paragraph, selected_level=selected_level)

if __name__ == "__main__":
    app.run(debug=True)