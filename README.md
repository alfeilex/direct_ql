# direct_ql

Basis-Anwendung zum Hochladen, Anzeigen und Annotieren von PDF-Dateien mit angebundenen Prompt-Services.

## Features

- Upload von PDF-Dateien (lokale Speicherung im Verzeichnis `uploads/`)
- Anzeige von Dokumenten direkt im Browser mittels [PDF.js](https://mozilla.github.io/pdf.js/)
- Auswahl von Textpassagen und Ausführen vordefinierter Aktionen:
  - **Übersetzen** (Platzhalter)
  - **Erklären** (Wortanzahl)
  - **In Karteikarte speichern** (speichert automatisch in einer lokalen Liste)
- Verwaltung von Annotationen und Flashcards über einfache JSON-Dateien

## Projektstruktur

```
app/
  main.py            # FastAPI-Anwendung und API-Routen
  services.py        # Datei- und Datenspeicher, Prompt-Service
  static/
    app.js           # Frontend-Logik
    styles.css       # Basis-Styles
  templates/
    index.html       # Startseite mit PDF-Viewer
uploads/             # Ablage für hochgeladene PDFs
```

## Voraussetzungen

- Python 3.11+
- Pipenv oder `pip`

## Installation und Start

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Die Anwendung ist danach unter http://127.0.0.1:8000 erreichbar.

## Hinweise

- Die LLM-Integration ist aktuell nur als Platzhalter umgesetzt, um die Architektur zu demonstrieren.
- Annotationen, Dokumente und Flashcards werden lokal in JSON-Dateien gespeichert und können leicht gegen eine Datenbank ausgetauscht werden.
