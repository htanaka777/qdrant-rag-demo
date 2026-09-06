from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.rag import RAGService
from app.schemas import AskRequest, AskResponse

app = FastAPI(
    title="Qdrant RAG Demo",
    version="1.0.0",
    description="FastAPI + Qdrant + OpenAI の小型RAG API",
)

rag_service: RAGService | None = None


@app.on_event("startup")
def startup() -> None:
    global rag_service
    rag_service = RAGService()
    rag_service.vector_store.ensure_collection()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    if rag_service is None:
        raise HTTPException(status_code=503, detail="RAG service is not ready")

    try:
        result = rag_service.ask(request.question, request.top_k)
        return AskResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=FileResponse, include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
