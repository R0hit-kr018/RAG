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

## Push the Project to GitHub

### 1. Create a repository on GitHub

1. Sign in to [GitHub](https://github.com).
2. Select **New repository**.
3. Enter a repository name, such as `rag-pdf-assistant`.
4. Choose **Private** or **Public**.
5. Do not add a README, `.gitignore`, or license because this project already has them.
6. Select **Create repository**.

Keep the GitHub repository URL from the next screen. It will look like this:

```text
https://github.com/YOUR_USERNAME/rag-pdf-assistant.git
```

### 2. Open a terminal in the project folder

```powershell
cd X:\ML\rag-pdf-assistant
```

This makes sure every Git command is run against this project.

### 3. Check the files that will be uploaded

```powershell
git status
```

Review the list carefully. `.env`, `venv`, `node_modules`, and other local files should not appear because they are ignored.

Never upload API keys. If a key has already been exposed or committed, revoke it and create a new one before pushing.

### 4. Create the first commit

```powershell
git add .
git commit -m "Initial project setup"
```

- `git add .` stages the project files.
- `git commit` saves a version of the staged files locally.

### 5. Connect the local project to GitHub

Replace `YOUR_USERNAME` with your GitHub username:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/rag-pdf-assistant.git
```

This stores the GitHub repository as the remote named `origin`.

### 6. Push the project

```powershell
git branch -M main
git push -u origin main
```

- `git branch -M main` names the current branch `main`.
- `git push -u origin main` uploads the commit and remembers the default remote branch.

Refresh the GitHub repository page to see the project files.

### Future Updates

After changing the project, run:

```powershell
git add .
git commit -m "Describe your change"
git push
```

Use a short message that explains what changed, such as `Fix PDF upload error` or `Update chat layout`.
