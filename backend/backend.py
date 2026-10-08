"""
Backend for the PDF Q&A Assistant.

Start it with:
    pip install -r backend/requirements.txt
    python backend/backend.py
    # OR: uvicorn backend.backend:app --reload --port 8000
"""

import os
import io
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# PDF, search, and language model dependencies
from pypdf import PdfReader
import faiss
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from groq import Groq

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

app = FastAPI(title="PDF Q&A Assistant Backend")

# Allow the frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# The current document stays in memory while the server is running.
rag_state = {
    "index": None,
    "chunks": [],
    "filename": None,
    "embedder": None,
}

def get_embedder():
    """Load the embedding model the first time it is needed."""
    if rag_state["embedder"] is None:
        print("Loading SentenceTransformer('all-MiniLM-L6-v2')...")
        rag_state["embedder"] = SentenceTransformer("all-MiniLM-L6-v2")
    return rag_state["embedder"]

@app.get("/")
@app.get("/health")
def health_check():
    """Return the current server and index status."""
    return {
        "status": "online",
        "has_index": rag_state["index"] is not None,
        "chunk_count": len(rag_state["chunks"]),
        "filename": rag_state["filename"]
    }

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Read a PDF, split its text, and build a FAISS index."""
    try:
        contents = await file.read()
        pdf_file = io.BytesIO(contents)
        reader = PdfReader(pdf_file)

        pages = []
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append({"page": i, "text": text})

        if not pages:
            raise HTTPException(status_code=400, detail="No readable text found in PDF.")

        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        chunks = []
        for p in pages:
            pieces = splitter.split_text(p["text"])
            for piece in pieces:
                chunks.append({"page": p["page"], "chunk": piece})

        if not chunks:
            raise HTTPException(status_code=400, detail="Could not create chunks from PDF.")

        embedder = get_embedder()
        chunk_texts = [c["chunk"] for c in chunks]
        embeddings = embedder.encode(chunk_texts, normalize_embeddings=True)
        embeddings = np.array(embeddings).astype("float32")

        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings)

        rag_state["index"] = index
        rag_state["chunks"] = chunks
        rag_state["filename"] = file.filename

        return {
            "status": "Ready",
            "filename": file.filename,
            "chunks": int(index.ntotal),
            "message": f"Successfully indexed {index.ntotal} chunks."
        }
    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process")
def process_document():
    """Return the current document status."""
    count = len(rag_state["chunks"])
    return {
        "status": "Ready",
        "chunks": count,
        "filename": rag_state["filename"]
    }

class QueryRequest(BaseModel):
    question: Optional[str] = None
    query: Optional[str] = None
    top_k: int = 4

@app.post("/chat")
async def chat_endpoint(req: QueryRequest):
    """Find relevant document chunks and generate an answer."""
    user_query = req.question or req.query
    if not user_query:
        raise HTTPException(status_code=400, detail="Question is required.")

    # There is nothing to search until a document has been uploaded.
    if rag_state["index"] is None or not rag_state["chunks"]:
        return {
            "answer": "No document is indexed yet. Please upload a PDF first, then ask your question.",
            "page": 0,
            "match": 0,
            "citation": None,
            "retrieved_chunks": []
        }

    try:
        embedder = get_embedder()
        query_vector = embedder.encode([user_query], normalize_embeddings=True)
        query_vector = np.array(query_vector).astype("float32")

        top_k = min(req.top_k, rag_state["index"].ntotal)
        scores, indices = rag_state["index"].search(query_vector, top_k)

        retrieved_chunks = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(rag_state["chunks"]):
                chunk_data = rag_state["chunks"][idx]
                # Convert the similarity score to a percentage for the UI.
                raw_score = float(score)
                match_pct = max(1, min(99, int(raw_score * 100))) if raw_score <= 1.0 else 94
                retrieved_chunks.append({
                    "page": chunk_data["page"],
                    "chunk": chunk_data["chunk"],
                    "score": raw_score,
                    "match": match_pct
                })

        top_page = retrieved_chunks[0]["page"] if retrieved_chunks else 1
        top_match = retrieved_chunks[0]["match"] if retrieved_chunks else 94
        top_chunk_text = retrieved_chunks[0]["chunk"] if retrieved_chunks else ""

        # Assemble the text sent to the language model.
        context_text = ""
        for c in retrieved_chunks:
            context_text += f"[Page {c['page']}]\n{c['chunk']}\n\n"

        system_prompt = """Answer questions using only the document excerpts below.
Cite the page number for each claim, for example [Page 3].
If the excerpts do not contain the answer, say so.

Use clear Markdown:
- Start with a one-sentence summary.
- Use bullet points (- ) for lists of facts or numbers.
- Use **bold** for key figures and terms.
- Separate paragraphs with blank lines.
- Do not nest bullets more than one level deep.
- Keep it concise and readable."""

        user_prompt = f"""Relevant parts of the document:

{context_text}

Question: {user_query}

Answer from the excerpts above and include page citations."""

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            # Return the best matching passage when no API key is configured.
            answer = f"According to [Page {top_page}]: {top_chunk_text[:280]}..."
        else:
            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
            )
            answer = response.choices[0].message.content

        return {
            "answer": answer,
            "page": top_page,
            "match": top_match,
            "citation": {
                "page": top_page,
                "match": top_match,
                "chunk": top_chunk_text
            },
            "retrieved_chunks": retrieved_chunks
        }
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("Starting PDF Q&A Assistant backend on http://0.0.0.0:8000 ...")
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)
