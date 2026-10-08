# RAG PDF Assistant

A React frontend and FastAPI backend for uploading PDF documents, searching their content, and asking questions with page citations.

## Project Structure

```text
rag-pdf-assistant/
├── frontend/
│   ├── index.html
│   └── src/
│       ├── App.tsx
│       ├── index.css
│       └── main.tsx
├── backend/
│   ├── backend.py
│   └── requirements.txt
├── .env
├── .gitignore
├── package.json
├── package-lock.json
├── tsconfig.json
└── vite.config.ts
```

## Requirements

- Node.js and npm
- Python 3.10 or newer
- A Groq API key for AI-generated answers

## Configuration

Create or update the root `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
APP_URL=http://localhost:3000
```

Do not commit `.env` or share the API key.

## Backend Setup

From the project root:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
python backend\backend.py
```

The backend runs at:

```text
http://localhost:8000
```

## Frontend Setup

Open a second terminal in the project root:

```powershell
npm install
npm run dev
```

Open the URL shown by Vite, usually:

```text
http://localhost:3000
```

## How to Use

1. Start the backend.
2. Start the frontend.
3. Upload a PDF file.
4. Wait for the document to be indexed.
5. Ask a question about the document.
6. Review the answer and page citation.

## Useful Commands

```powershell
# Start the frontend development server
npm run dev

# Check TypeScript
npm run lint

# Create a production frontend build
npm run build

# Preview the production build
npm run preview
```

## Backend Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Check backend and index status |
| POST | `/upload` | Upload and index a PDF |
| POST | `/process` | Check the current indexed document |
| POST | `/chat` | Ask a question about the indexed PDF |


