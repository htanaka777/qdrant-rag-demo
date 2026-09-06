import json
from pathlib import Path
from statistics import mean

from app.rag import RAGService


QUESTIONS = Path("eval/questions.json")


def main() -> None:
    cases = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    rag = RAGService()

    results = []
    for case in cases:
        result = rag.ask(case["question"], top_k=3)
        retrieved_sources = [s["source"] for s in result["sources"]]
        hit = case["expected_source"] in retrieved_sources

        results.append(
            {
                "question": case["question"],
                "expected_source": case["expected_source"],
                "retrieved_sources": retrieved_sources,
                "retrieval_hit": hit,
                "total_ms": result["total_ms"],
            }
        )

    hit_rate = sum(r["retrieval_hit"] for r in results) / len(results)
    avg_latency = mean(r["total_ms"] for r in results)

    print(json.dumps(results, ensure_ascii=False, indent=2))
    print()
    print(f"Retrieval Hit@3: {hit_rate:.1%}")
    print(f"Average total latency: {avg_latency:.2f} ms")


if __name__ == "__main__":
    main()
