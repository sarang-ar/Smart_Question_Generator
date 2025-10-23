import tkinter as tk
from tkinter import scrolledtext
from difficulty_classifier import classify_difficulty
from utils import clean_paragraph
from transformers import pipeline

# Load the improved question generation model
try:
    print("🔄 Loading question generation model...")
    generator = pipeline("text2text-generation", 
                         model="mrm8488/t5-base-finetuned-question-generation-ap")
    print("✅ Model loaded successfully.")
except Exception as e:
    print("⚠️ Failed to load transformer model:", e)
    generator = None

# Question validation logic
def is_valid_question(q):
    q = q.strip()
    return (
        len(q.split()) > 4 and
        "true" not in q.lower() and
        "false" not in q.lower() and
        q.lower() not in ["yes", "no"]
    )

# Uniqueness check
def is_unique(q, seen):
    return all(q.lower() != s.lower() and q.lower() not in s.lower() and s.lower() not in q.lower() for s in seen)

# Generate questions with difficulty filtering, uniqueness, and "Explain." suffix for Hard
def generate_questions(paragraph, selected_level, pool_size=15):
    print(f"🧠 Generating questions for difficulty: {selected_level}")
    if generator is None:
        return ["Model not available. Please check your internet or installation."]
    
    word_count = len(paragraph.split())
    if word_count < 20:
        return ["⚠️ Please enter a longer or more detailed paragraph for better results."]
    if not any(punct in paragraph for punct in [".", ",", "?", "!"]):
        return ["⚠️ Paragraph seems too abstract. Try adding more descriptive or factual content."]

    try:
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

        if filtered:
            print(f"✅ Found {len(filtered)} unique questions for {selected_level}")
            return filtered
        else:
            return [f"⚠️ No unique questions matched the selected difficulty: {selected_level}"]
    except Exception as e:
        print("⚠️ Error during generation:", e)
        return ["Error generating questions."]

# GUI logic
def run_gui():
    def process():
        para = clean_paragraph(text_input.get("1.0", tk.END))
        selected_level = difficulty_var.get()
        print("📥 Paragraph received:", para)
        questions = generate_questions(para, selected_level)
        output.configure(state="normal")
        output.delete("1.0", tk.END)

        if isinstance(questions[0], str):
            output.insert(tk.END, questions[0] + "\n\n")
        else:
            for q, level in questions:
                output.insert(tk.END, f"{q} [{level}]\n\n", level)

        output.configure(state="disabled")

    root = tk.Tk()
    root.title("🧠 Smart Question Generator")
    root.geometry("800x750")
    root.configure(bg="#f0f0f0")

    tk.Label(root, text="Enter Paragraph:", font=("Segoe UI", 12), bg="#f0f0f0").pack(pady=5)
    text_input = scrolledtext.ScrolledText(root, height=10, wrap=tk.WORD, font=("Segoe UI", 11))
    text_input.pack(padx=10, fill=tk.BOTH, expand=True)

    difficulty_var = tk.StringVar(value="Any")
    tk.Label(root, text="Select Difficulty:", font=("Segoe UI", 11), bg="#f0f0f0").pack(pady=5)
    difficulty_menu = tk.OptionMenu(root, difficulty_var, "Any", "Easy", "Moderate", "Hard")
    difficulty_menu.config(font=("Segoe UI", 11), width=10)
    difficulty_menu.pack()

    tk.Button(root, text="Generate Questions", command=process, bg="#007ACC", fg="white",
              font=("Segoe UI", 11, "bold")).pack(pady=10)

    tk.Button(root, text="Retry", command=process, bg="#555", fg="white",
              font=("Segoe UI", 11)).pack(pady=5)

    tk.Label(root, text="Generated Questions:", font=("Segoe UI", 12), bg="#f0f0f0").pack(pady=5)
    output = scrolledtext.ScrolledText(root, height=15, wrap=tk.WORD, font=("Segoe UI", 11))
    output.pack(padx=10, fill=tk.BOTH, expand=True)

    # Add color tags
    output.tag_config("Easy", foreground="green")
    output.tag_config("Moderate", foreground="orange")
    output.tag_config("Hard", foreground="red")

    root.mainloop()

if __name__ == "__main__":
    run_gui()