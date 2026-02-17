from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from . import models, schemas
from openai import OpenAI, RateLimitError, APIError, AuthenticationError
import os


app = FastAPI()

Base.metadata.create_all(bind=engine)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

     # Validate thread exists
    thread = db.query(models.Thread).filter(
        models.Thread.id == request.thread_id
    ).first()

    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")


    # Save user message
    user_message = models.Message(
        thread_id=request.thread_id,
        role="user",
        content=request.content
    )

    db.add(user_message)
    db.commit()

    # Retrieve full conversation history (including new message)
    messages = (
        db.query(models.Message)
        .filter(models.Message.thread_id == request.thread_id)
        .order_by(models.Message.created_at.asc())
        .all()
    )

    openai_messages = [
        {"role": m.role, "content": m.content}
        for m in messages
    ]

    # Send to OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=openai_messages,
        )

        assistant_reply = response.choices[0].message.content

    except RateLimitError as e:
        raise HTTPException(
            status_code=429,
            detail=f"OpenAI quota exceeded:"
        )

    except AuthenticationError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid OpenAI API key:"
        )
        
    except APIError as e:
        raise HTTPException(
            status_code=502,
            detail=f"OpenAI service error:"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected AI processing error:"
        )


    # Save assistant response
    assistant_message = models.Message(
        thread_id=request.thread_id,
        role="assistant",
        content=assistant_reply
    )

    db.add(assistant_message)
    db.commit()

    # Return assistant response
    return {"response": assistant_reply}


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