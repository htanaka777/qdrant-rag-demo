from qdrant_client import QdrantClient, models

from app.config import get_settings


class VectorStore:
    def __init__(self) -> None:
        settings = get_settings()
        self.client = QdrantClient(url=settings.qdrant_url)
        self.collection = settings.qdrant_collection
        self.dimension = settings.embedding_dimension
        self.min_score = settings.min_score

    def ensure_collection(self) -> None:
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=models.VectorParams(
                    size=self.dimension,
                    distance=models.Distance.COSINE,
                ),
            )

    def upsert(self, points: list[models.PointStruct]) -> None:
        self.client.upsert(
            collection_name=self.collection,
            points=points,
            wait=True,
        )

    def search(self, query_vector: list[float], top_k: int) -> list[models.ScoredPoint]:
        result = self.client.query_points(
            collection_name=self.collection,
            query=query_vector,
            limit=top_k,
            with_payload=True,
            score_threshold=self.min_score if self.min_score > 0 else None,
        )
        return result.points
