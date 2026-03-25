from __future__ import annotations

import json
import math
import time
from pathlib import Path


def embed_text(text: str, dimension: int = 32) -> list[float]:
    vector = [0.0] * dimension
    for index, char in enumerate(text.encode("utf-8")):
        vector[index % dimension] += char / 255.0
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


def cosine(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=False))


def build_corpus(size: int) -> list[dict]:
    return [
        {
            "expert_id": f"expert-{index}",
            "document": f"Expert {index} helps with reproducible research workflows and metadata.",
        }
        for index in range(size)
    ]


def run_case(size: int) -> dict:
    corpus = build_corpus(size)
    query_vector = embed_text("reproducible research workflows")
    started = time.perf_counter()
    scores = []
    for row in corpus:
        score = cosine(query_vector, embed_text(row["document"]))
        scores.append(score)
    elapsed_ms = (time.perf_counter() - started) * 1000
    return {
        "corpus_size": size,
        "elapsed_ms": round(elapsed_ms, 3),
        "top_score": round(max(scores), 4),
    }


def main() -> None:
    results = [run_case(size) for size in (10, 100, 1000)]
    output_path = Path(__file__).resolve().parent / "results" / "001-expert-matching-app.json"
    output_path.write_text(json.dumps({"cases": results}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
