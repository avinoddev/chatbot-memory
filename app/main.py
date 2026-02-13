from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from . import models, schemas

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def health_check():
    return {"status": "Chatbot memory service running"}


@app.post("/users")
def create_user(request: schemas.CreateUserRequest, db: Session = Depends(get_db)):
    user = models.User(email=request.email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"user_id": user.id}


@app.post("/threads")
def create_thread(request: schemas.CreateThreadRequest, db: Session = Depends(get_db)):
    thread = models.Thread(user_id=request.user_id)
    db.add(thread)
    db.commit()
    db.refresh(thread)
    return {"thread_id": thread.id}


@app.post("/messages")
def create_message(request: schemas.CreateMessageRequest, db: Session = Depends(get_db)):

    # 1️⃣ Save message
    message = models.Message(
        thread_id=request.thread_id,
        role=request.role,
        content=request.content
    )

    db.add(message)
    db.commit()

    # 2️⃣ Retrieve full conversation history
    messages = (
        db.query(models.Message)
        .filter(models.Message.thread_id == request.thread_id)
        .order_by(models.Message.created_at.asc())
        .all()
    )

    history = [
        {"role": m.role, "content": m.content}
        for m in messages
    ]

    return {"history": history}

@app.get("/threads/{thread_id}")
def get_thread(thread_id: str, db: Session = Depends(get_db)):

    messages = (
        db.query(models.Message)
        .filter(models.Message.thread_id == thread_id)
        .order_by(models.Message.created_at.asc())
        .all()
    )

    history = [
        {"role": m.role, "content": m.content}
        for m in messages
    ]

    return {"history": history}

@app.get("/threads")
def list_threads(db: Session = Depends(get_db)):

    threads = db.query(models.Thread).all()

    return [
        {
            "thread_id": t.id,
            "user_id": t.user_id,
            "created_at": t.created_at
        }
        for t in threads
    ]