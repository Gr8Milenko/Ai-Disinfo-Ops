# scripts/hf_pipeline_test.py

from transformers import pipeline

def run_pipeline_inference(model_id="bert-base-uncased"):
    classifier = pipeline("text-classification", model=model_id)

    samples = [
        "Breaking: Officials confirm new cyber campaign targeting elections.",
        "Experts warn of AI-generated content used to sway voters.",
        "Community celebrates record turnout at local event.",
        "Viral post claims vaccine has microchips—experts disagree.",
    ]

    print(f"\n[INFO] Running inference using model: {model_id}\n")
    for text in samples:
        result = classifier(text)[0]
        print(f"[TEXT] {text}")
        print(f"[PRED] {result['label']} ({round(result['score'] * 100, 2)}%)\n")

if __name__ == "__main__":
    run_pipeline_inference()
