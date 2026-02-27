# Chatbot Memory Service

Backend API providing secure, multi-user, multi-thread conversation memory for the Physics Department chatbot.  
Handles authentication, persistent chat history, basic cross-thread learning, and context-aware OpenAI responses.

---

## Tech Stack

- Python 3.11
- FastAPI
- PostgreSQL
- SQLAlchemy
- OpenAI API
- JWT Authentication
- Streamlit (frontend)

---

## Core Features

- JWT-based user authentication  
- Multiple threads per user  
- Persistent message storage in PostgreSQL  
- Thread ownership protection  
- Cross-thread memory (strengths, weaknesses, preferences)  
- User profile context injected into AI responses  

---

## Data Model

- **User** → owns threads and a profile  
- **Thread** → contains ordered messages  
- **Message** → role, content, timestamp  
- **UserProfile** → cross-thread learning state  
- **MemoryEvent** → memory audit log  

---

## Conversation Flow

1. User logs in and receives JWT  
2. User creates a thread  
3. User message is saved  
4. Memory signals are extracted and stored  
5. Thread history + profile context sent to OpenAI  
6. Assistant response saved and returned  

---

## Setup

### 1. Create Virtual Environment (Python 3.11)

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create `.env`

```
DATABASE_URL=postgresql+psycopg://localhost/chatbot_memory
OPENAI_API_KEY=your_key_here
JWT_SECRET=your_secret_here
```

### 4. Run the Server

```bash
uvicorn app.main:app --reload
```

Server runs at:

http://127.0.0.1:8000  

API docs available at:

http://127.0.0.1:8000/docs  

### 5. Run Frontend (Optional)

```bash
streamlit run streamlit_app.py
```

Frontend runs at:

http://localhost:8501