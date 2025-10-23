from transformers import pipeline

try:
    generator = pipeline("text2text-generation", model="valhalla/t5-base-qg-hl")
    print("✅ Model loaded.")
    input_text = "generate question: The sun is a star that emits light and heat."
    results = generator(input_text, max_length=64, do_sample=False)
    for res in results:
        print("🧠 Generated:", res["generated_text"])
except Exception as e:
    print("❌ Error:", e)