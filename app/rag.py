from time import perf_counter

from app.embeddings import OpenAIEmbedder
from app.llm import OpenAILLM
from app.vector_store import VectorStore


class RAGService:
    def __init__(self) -> None:
        self.embedder = OpenAIEmbedder()
        self.vector_store = VectorStore()
        self.llm = OpenAILLM()

    def ask(self, question: str, top_k: int) -> dict:
        total_start = perf_counter()

        retrieval_start = perf_counter()
        query_vector = self.embedder.embed([question])[0]
        hits = self.vector_store.search(query_vector, top_k=top_k)
        retrieval_ms = (perf_counter() - retrieval_start) * 1000

        contexts = []
        sources = []
        for hit in hits:
            payload = hit.payload or {}
            context = {
                "title": str(payload.get("title", "Untitled")),
                "text": str(payload.get("text", "")),
                "source": str(payload.get("source", "unknown")),
            }
            contexts.append(context)
            sources.append(
                {
                    "title": context["title"],
                    "source": context["source"],
                    "score": round(float(hit.score), 4),
                }
            )

        generation_start = perf_counter()
        answer = self.llm.generate(question, contexts)
        generation_ms = (perf_counter() - generation_start) * 1000

        total_ms = (perf_counter() - total_start) * 1000

        return {
            "answer": answer,
            "sources": sources,
            "retrieval_ms": round(retrieval_ms, 2),
            "generation_ms": round(generation_ms, 2),
            "total_ms": round(total_ms, 2),
        }
