from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .services import (
    AnnotationStore,
    DocumentStore,
    FlashcardStore,
    PromptService,
)

app = FastAPI(title="DirectQL PDF Annotator")

documents = DocumentStore()
annotations = AnnotationStore()
flashcards = FlashcardStore()
prompts = PromptService()

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)) -> Dict[str, str]:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Es werden nur PDF-Dateien unterstützt.")
    content = await file.read()
    document_id = documents.save(file.filename, content)
    return {"id": document_id, "name": file.filename}


@app.get("/api/documents")
async def list_documents() -> List[Dict[str, str]]:
    return documents.list_documents()


@app.get("/api/documents/{document_id}")
async def get_document(document_id: str) -> FileResponse:
    path = documents.get_path(document_id)
    if not path:
        raise HTTPException(status_code=404, detail="Dokument nicht gefunden")
    return FileResponse(path, media_type="application/pdf")


@app.get("/api/annotations/{document_id}")
async def list_annotations(document_id: str) -> List[Dict[str, str]]:
    return [a.__dict__ for a in annotations.list_for_document(document_id)]


@app.post("/api/annotations")
async def create_annotation(
    document_id: str = Form(...),
    page: int = Form(...),
    text: str = Form(...),
    note: str = Form(...),
) -> Dict[str, str]:
    annotation = annotations.add(document_id, page, text, note)
    return annotation.__dict__


@app.post("/api/process")
async def process_text(
    document_id: str = Form(...),
    action: str = Form(...),
    text: str = Form(...),
    note: str | None = Form(None),
) -> JSONResponse:
    response = prompts.run(action, text)
    payload = {"action": action, "text": text, **response}

    if action.lower() == "flashcard":
        card = flashcards.add(front=text, back=response["result"])
        payload["flashcardId"] = card.id

    if note:
        annotations.add(document_id=document_id, page=0, text=text, note=note)

    return JSONResponse(payload)


@app.get("/api/flashcards")
async def list_flashcards() -> List[Dict[str, str]]:
    return [card.__dict__ for card in flashcards.list()]
