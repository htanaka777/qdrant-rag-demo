from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=3, ge=1, le=10)


class Source(BaseModel):
    source: str
    title: str
    score: float


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]
    retrieval_ms: float
    generation_ms: float
    total_ms: float
