import csv
import uuid
from pathlib import Path

from qdrant_client import models

from app.embeddings import OpenAIEmbedder
from app.vector_store import VectorStore


DATA_FILE = Path("data/faq.csv")


def load_documents() -> list[dict[str, str]]:
    with DATA_FILE.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    docs = load_documents()
    texts = [f"{doc['title']}\n{doc['text']}" for doc in docs]

    embedder = OpenAIEmbedder()
    store = VectorStore()
    store.ensure_collection()

    vectors = embedder.embed(texts)

    points = []
    for doc, vector in zip(docs, vectors, strict=True):
        # 同じsourceで再実行しても同じIDになるようにUUID5を利用
        point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, doc["source"]))
        points.append(
            models.PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "title": doc["title"],
                    "text": doc["text"],
                    "source": doc["source"],
                },
            )
        )

    store.upsert(points)
    print(f"Indexed {len(points)} documents into Qdrant.")


if __name__ == "__main__":
    main()
