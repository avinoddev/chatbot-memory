# Chatbot Memory Service

Backend API providing persistent, multi-user, multi-thread conversation memory for the Physics Department chatbot.  
Handles all conversation state and context retrieval for OpenAI.

---

## Tech Stack

- **Python 3.11**
- **FastAPI**
- **PostgreSQL**
- **SQLAlchemy**
- **OpenAI API**

---

## Core Features

- Multi-user support  
- Multiple threads per user  
- Persistent message storage  
- Ordered conversation history retrieval  
- Context-aware OpenAI integration  
- Structured error handling  

---

## Data Model

- **User** → owns multiple threads  
- **Thread** → contains ordered messages  
- **Message** → role, content, timestamp  

### Conversation Flow

1. Save user message  
2. Retrieve thread history  
3. Send history to OpenAI  
4. Save assistant response  
5. Return assistant response  

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


### 3. Run the Server
```bash
uvicorn app.main:app --reload
```

Server will run at:

```
http://127.0.0.1:8000
```

API documentation available at:

```
http://127.0.0.1:8000/docs
```