⚡ CodeSense — AI-Powered Code Review Assistant
Real-time AI code analysis using Llama 3.3 70B via Groq API, RAG with ChromaDB, and a React + Monaco frontend. Built as a full-stack SWE + AI/ML project.

CodeSense Demo FastAPI React Llama

✨ Features
Real-time streaming — responses stream token-by-token via SSE
4 analysis modes — Code Review, Explain, Optimize, Add Docstrings
RAG-enhanced — ChromaDB vector search enriches prompts with relevant docs
Monaco Editor — VS Code-quality editor in the browser
Multi-language — Python, JavaScript, TypeScript, Java, C++, Go, Rust, SQL
Docker + CI/CD — containerized, deployable to Render/Railway in one click
🏗️ Architecture
User → React (Monaco Editor)
         ↓ SSE Stream
     FastAPI Backend
      ├── Groq API (Llama 3.3 70B streaming)
      └── RAG Pipeline (LangChain + ChromaDB)
         ↓
     Docker → Render
🚀 Quick Start
Prerequisites
Python 3.11+
Node.js 18+
Groq API key (free at console.groq.com)
Backend
cd backend
pip install -r requirements.txt
export GROQ_API_KEY=your_key_here
uvicorn main:app --reload --port 8000
Frontend
cd frontend
npm install
REACT_APP_API_URL=http://localhost:8000 npm start
Open http://localhost:3000

🐳 Docker
# Backend
cd backend
docker build -t codesense-backend .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key codesense-backend

# Frontend
cd frontend
docker build --build-arg REACT_APP_API_URL=http://localhost:8000 -t codesense-frontend .
docker run -p 3000:80 codesense-frontend
☁️ Deploy to Render
Backend (Web Service)
Push to GitHub
New Web Service → connect repo → select backend/ as root
Build: pip install -r requirements.txt
Start: uvicorn main:app --host 0.0.0.0 --port $PORT
Add env var: GROQ_API_KEY=your_key
Frontend (Static Site)
New Static Site → connect repo → select frontend/ as root
Build: npm install && npm run build
Publish: build/
Add env var: REACT_APP_API_URL=https://your-backend.onrender.com
🧠 Tech Stack
Layer	Technology
Frontend	React 18, Monaco Editor, SSE
Backend	FastAPI, Python 3.11, async/await
LLM	Llama 3.3 70B via Groq API (streaming)
RAG	LangChain, ChromaDB, sentence-transformers
Deploy	Docker, Render, GitHub Actions
📁 Project Structure
codesense/
├── backend/
│   ├── main.py          # FastAPI app + endpoints
│   ├── llm.py           # Groq streaming + prompts
│   ├── rag.py           # ChromaDB + LangChain RAG
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx      # Main UI component
│   │   └── App.css      # Styles
│   ├── public/
│   │   └── index.html
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
└── README.md
🔑 Environment Variables
Variable	Where	Description
GROQ_API_KEY	Backend	Your Groq API key
REACT_APP_API_URL	Frontend	Backend URL
Built by Sandesh Mane · VIT Bhopal · B.Tech CSE (AI & ML)
