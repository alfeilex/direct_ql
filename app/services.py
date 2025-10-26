from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List

UPLOAD_DIR = Path("uploads")
ANNOTATIONS_FILE = Path("data/annotations.json")
FLASHCARDS_FILE = Path("data/flashcards.json")


@dataclass
class Annotation:
    id: str
    document_id: str
    page: int
    text: str
    note: str


@dataclass
class Flashcard:
    id: str
    front: str
    back: str


class JSONStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write([])

    def _read(self) -> List[Dict]:
        with self.path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: List[Dict]) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


class AnnotationStore(JSONStore):
    def __init__(self, path: Path = ANNOTATIONS_FILE):
        super().__init__(path)

    def list_for_document(self, document_id: str) -> List[Annotation]:
        return [Annotation(**item) for item in self._read() if item["document_id"] == document_id]

    def add(self, document_id: str, page: int, text: str, note: str) -> Annotation:
        annotation = Annotation(id=str(uuid.uuid4()), document_id=document_id, page=page, text=text, note=note)
        data = self._read()
        data.append(asdict(annotation))
        self._write(data)
        return annotation


class FlashcardStore(JSONStore):
    def __init__(self, path: Path = FLASHCARDS_FILE):
        super().__init__(path)

    def list(self) -> List[Flashcard]:
        return [Flashcard(**item) for item in self._read()]

    def add(self, front: str, back: str) -> Flashcard:
        flashcard = Flashcard(id=str(uuid.uuid4()), front=front, back=back)
        data = self._read()
        data.append(asdict(flashcard))
        self._write(data)
        return flashcard


class DocumentStore:
    def __init__(self, base_dir: Path = UPLOAD_DIR):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, filename: str, content: bytes) -> str:
        document_id = str(uuid.uuid4())
        safe_name = f"{document_id}_{filename}"
        path = self.base_dir / safe_name
        path.write_bytes(content)
        return document_id

    def list_documents(self) -> List[Dict[str, str]]:
        documents: List[Dict[str, str]] = []
        for file_path in self.base_dir.glob("*_*.pdf"):
            doc_id, original_name = file_path.name.split("_", 1)
            documents.append({"id": doc_id, "name": original_name})
        return sorted(documents, key=lambda x: x["name"].lower())

    def get_path(self, document_id: str) -> Path | None:
        matches = list(self.base_dir.glob(f"{document_id}_*.pdf"))
        return matches[0] if matches else None


class PromptService:
    """Provide simple placeholder responses for different actions."""

    def run(self, action: str, text: str) -> Dict[str, str]:
        action = action.lower()
        if action == "translate":
            return {"result": self._translate(text)}
        if action == "explain":
            return {"result": self._explain(text)}
        if action == "flashcard":
            return {"result": self._make_flashcard(text)}
        return {"result": f"Unknown action: {action}"}

    def _translate(self, text: str) -> str:
        # Placeholder: reverse text to simulate processing
        return text[::-1]

    def _explain(self, text: str) -> str:
        return f"Erklärung: Dieser Text besteht aus {len(text.split())} Wörtern."

    def _make_flashcard(self, text: str) -> str:
        return f"Frage: Was bedeutet '{text[:40]}...'?\nAntwort: Platzhalter-Antwort"
