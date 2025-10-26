const documentSelect = document.getElementById("document-select");
const uploadForm = document.getElementById("upload-form");
const annotationList = document.getElementById("annotation-list");
const flashcardList = document.getElementById("flashcard-list");
const processButton = document.getElementById("process-button");
const selectedTextEl = document.getElementById("selected-text");
const resultEl = document.getElementById("result");
const noteInput = document.getElementById("note-input");
const actionSelect = document.getElementById("action-select");
const viewer = document.getElementById("pdf-viewer");

let currentDocumentId = null;
let currentPDF = null;
let lastSelection = "";

const pdfjsLib = window["pdfjs-dist/build/pdf"];
pdfjsLib.GlobalWorkerOptions.workerSrc = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.0.379/pdf.worker.min.js";

async function loadDocuments() {
  const response = await fetch("/api/documents");
  const docs = await response.json();
  documentSelect.innerHTML = "";
  if (docs.length === 0) {
    const option = document.createElement("option");
    option.textContent = "Bitte laden Sie ein PDF hoch";
    option.disabled = true;
    option.selected = true;
    documentSelect.appendChild(option);
    processButton.disabled = true;
    return;
  }

  docs.forEach((doc, index) => {
    const option = document.createElement("option");
    option.value = doc.id;
    option.textContent = doc.name;
    if (index === 0) {
      option.selected = true;
      currentDocumentId = doc.id;
    }
    documentSelect.appendChild(option);
  });

  if (!currentDocumentId) {
    currentDocumentId = docs[0].id;
  }

  await loadDocument(currentDocumentId);
}

async function loadDocument(documentId) {
  if (!documentId) return;
  currentDocumentId = documentId;
  processButton.disabled = true;
  selectedTextEl.textContent = "";
  resultEl.textContent = "";

  const url = `/api/documents/${documentId}`;
  const loadingTask = pdfjsLib.getDocument(url);
  currentPDF = await loadingTask.promise;

  viewer.innerHTML = "";
  for (let pageNum = 1; pageNum <= currentPDF.numPages; pageNum++) {
    const page = await currentPDF.getPage(pageNum);
    const viewport = page.getViewport({ scale: 1.3 });

    const pageContainer = document.createElement("div");
    pageContainer.className = "page-container";
    pageContainer.dataset.pageNumber = pageNum;

    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");
    canvas.height = viewport.height;
    canvas.width = viewport.width;

    const renderContext = {
      canvasContext: context,
      viewport,
    };

    await page.render(renderContext).promise;

    const textContent = await page.getTextContent();
    const textLayerDiv = document.createElement("div");
    textLayerDiv.className = "textLayer";
    pageContainer.appendChild(canvas);
    pageContainer.appendChild(textLayerDiv);

    pdfjsLib.renderTextLayer({
      textContent,
      container: textLayerDiv,
      viewport,
      textDivs: [],
    });

    viewer.appendChild(pageContainer);
  }

  loadAnnotations(documentId);
  loadFlashcards();
}

async function loadAnnotations(documentId) {
  const response = await fetch(`/api/annotations/${documentId}`);
  const items = await response.json();
  annotationList.innerHTML = "";
  items.forEach((item) => {
    const li = document.createElement("li");
    li.className = "annotation";
    li.innerHTML = `<strong>Seite ${item.page}</strong><div>${item.text}</div><div>${item.note}</div>`;
    annotationList.appendChild(li);
  });
}

async function loadFlashcards() {
  const response = await fetch("/api/flashcards");
  const items = await response.json();
  flashcardList.innerHTML = "";
  items.forEach((item) => {
    const li = document.createElement("li");
    li.className = "flashcard";
    li.innerHTML = `<strong>${item.front}</strong><span>${item.back}</span>`;
    flashcardList.appendChild(li);
  });
}

viewer.addEventListener("mouseup", () => {
  const selection = window.getSelection();
  const text = selection ? selection.toString().trim() : "";
  if (!text) {
    processButton.disabled = true;
    selectedTextEl.textContent = "";
    lastSelection = "";
    return;
  }
  lastSelection = text;
  selectedTextEl.textContent = text;
  processButton.disabled = false;
});

processButton.addEventListener("click", async () => {
  if (!lastSelection || !currentDocumentId) return;
  const formData = new FormData();
  formData.append("document_id", currentDocumentId);
  formData.append("action", actionSelect.value);
  formData.append("text", lastSelection);
  if (noteInput.value) {
    formData.append("note", noteInput.value);
  }

  const response = await fetch("/api/process", {
    method: "POST",
    body: formData,
  });
  const data = await response.json();
  resultEl.textContent = data.result;
  noteInput.value = "";
  await loadAnnotations(currentDocumentId);
  await loadFlashcards();
});

uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(uploadForm);
  const response = await fetch("/api/upload", {
    method: "POST",
    body: formData,
  });

  if (response.ok) {
    uploadForm.reset();
    await loadDocuments();
  } else {
    const error = await response.json();
    alert(error.detail || "Upload fehlgeschlagen");
  }
});

documentSelect.addEventListener("change", async (event) => {
  const id = event.target.value;
  if (id) {
    await loadDocument(id);
  }
});

loadDocuments();
