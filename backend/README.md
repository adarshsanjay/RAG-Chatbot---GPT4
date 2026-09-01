# E-Commerce RAG Chatbot - Backend

FastAPI backend service providing RAG vector search, intent classification via Groq LLM API, and PDF document parsing.

## Prerequisites
- Python 3.10+
- Installed packages from `requirements.txt`

## Quick Start

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables in `.env`:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   ```

4. Run the Uvicorn server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

5. Access interactive API documentation at `http://localhost:8000/docs`.
