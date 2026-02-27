from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from .auth import create_access_token, get_current_user
from .services.memory import extract_memory, apply_memory
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

    existing = db.query(models.User).filter(
        models.User.email == request.email
    ).first()

    if existing:
        return {"user_id": existing.id}

    user = models.User(email=request.email)
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create default profile
    profile = models.UserProfile(user_id=user.id)
    db.add(profile)
    db.commit()

    token = create_access_token({"sub": user.id})

    return {
        "user_id": user.id,
        "access_token": token
    }

@app.post("/threads")
def create_thread(
    request: schemas.CreateThreadRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    if user_id != request.user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Validate user exists
    user = db.query(models.User).filter(
        models.User.id == request.user_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    thread = models.Thread(user_id=request.user_id)

    db.add(thread)
    db.commit()
    db.refresh(thread)

    return {"thread_id": thread.id}


@app.post("/messages")
def create_message(
    request: schemas.CreateMessageRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):

     # Validate thread exists
    thread = db.query(models.Thread).filter(
        models.Thread.id == request.thread_id,
        models.Thread.user_id == user_id
    ).first()

    if not thread:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Save user message
    user_message = models.Message(
        thread_id=request.thread_id,
        role="user",
        content=request.content
    )

    db.add(user_message)
    db.commit()

    # ---- MEMORY EXTRACTION ----
    events = extract_memory(request.content)
    apply_memory(db, user_id, events)

    # Retrieve full conversation history
    messages = (
        db.query(models.Message)
        .filter(models.Message.thread_id == request.thread_id)
        .order_by(models.Message.created_at.asc())
        .all()
    )

    # Fetch user profile for context injection
    profile = db.query(models.UserProfile).filter(
        models.UserProfile.user_id == user_id
    ).first()

    system_prompt = {
        "role": "system",
        "content": f"""
    User Profile Context:
    Weaknesses: {profile.weaknesses}
    Strengths: {profile.strengths}
    Preferred Level: {profile.preferred_level}

    Adapt explanations accordingly.
    """
    }

    openai_messages = [system_prompt] + [
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

@app.get("/users/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user.id,
        "email": user.email,
        "created_threads": len(user.threads)
    }