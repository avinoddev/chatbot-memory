# Chatbot Memory Service

Backend service responsible for managing persistent chat history
for the Physics Department chatbot.

## Purpose

This service implements:

- User-linked conversation threads
- Persistent message storage
- Thread-based memory isolation
- Basic cross-thread user memory (optional)
- Controlled history retrieval for LLM context

The model itself does not store memory.
This service handles all conversation state.

## Architecture

- Python: 3.11
- Backend: FastAPI
- Database: PostgreSQL
- ORM: SQLAlchemy
- Deployment: Render (planned)

## Data Model

- Users → can own multiple threads
- Threads → contain ordered messages
- Messages → stored with role + content + timestamp

Each interaction:
1. Saves user message
2. Retrieves thread history
3. Sends history to LLM
4. Stores assistant response

## Setup

Create a virtual environment using Python 3.11:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
