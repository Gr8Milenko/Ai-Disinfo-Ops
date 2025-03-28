import os
import json
from pathlib import Path
import random
from faker import Faker

fake = Faker()
random.seed(42)

OUTPUT_DIR = Path("data/processed/test_inputs")
TYPES = ["article", "tweet", "video_transcript"]
ENTITIES = ["Putin", "NATO", "election", "Ukraine", "propaganda", "media", "Belarus"]

def generate_sample(i):
    return {
        "text": fake.paragraph(nb_sentences=5),
        "named_entities": random.sample(ENTITIES, k=random.randint(1, 4)),
        "type": random.choice(TYPES),
        "url": fake.url()
    }

def main(n=10):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for i in range(n):
        sample = generate_sample(i)
        path = OUTPUT_DIR / f"sample{i+1}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(sample, f, indent=2)
    print(f"[DONE] Generated {n} synthetic test samples in: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
