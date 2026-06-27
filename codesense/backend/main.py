from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import asyncio
import json

from llm import stream_code_review
from rag import get_relevant_context, ingest_docs

app = FastAPI(title="CodeSense API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReviewRequest(BaseModel):
    code: str
    language: str = "python"
    mode: str = "review"  # review | docstring | explain | optimize

class IngestRequest(BaseModel):
    texts: list[str]
    metadata: Optional[list[dict]] = None

@app.on_event("startup")
async def startup_event():
    ingest_docs()

@app.get("/")
def root():
    return {"status": "CodeSense API running", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/review/stream")
async def review_stream(req: ReviewRequest):
    if not req.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    if len(req.code) > 10000:
        raise HTTPException(status_code=400, detail="Code too long (max 10,000 chars)")

    context = get_relevant_context(req.code, req.language)

    async def event_generator():
        try:
            async for chunk in stream_code_review(req.code, req.language, req.mode, context):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )

@app.post("/review")
async def review(req: ReviewRequest):
    """Non-streaming fallback endpoint"""
    if not req.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")

    context = get_relevant_context(req.code, req.language)
    full_response = ""
    async for chunk in stream_code_review(req.code, req.language, req.mode, context):
        full_response += chunk
    return {"result": full_response, "language": req.language, "mode": req.mode}
