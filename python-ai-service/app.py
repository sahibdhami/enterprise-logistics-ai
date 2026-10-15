from fastapi import FastAPI
from pydantic import BaseModel, Field

from rag_service import ask_rag
from tools import investigate_package


app = FastAPI(
    title="Enterprise Logistics AI Service",
    version="1.0.0",
)


class QuestionRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=4000,
    )


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/ai/rag")
def rag(request: QuestionRequest):
    return ask_rag(request.question)


@app.post("/ai/investigate")
def investigate(request: QuestionRequest):
    return investigate_package(request.question)
