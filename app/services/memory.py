from .. import models
from sqlalchemy.orm import Session
import re

def extract_memory(content: str):
    events = []

    if "I struggle with" in content:
        topic = content.split("I struggle with")[-1].strip()
        events.append(("weakness_inferred", {"topic": topic}))

    if "I am good at" in content:
        topic = content.split("I am good at")[-1].strip()
        events.append(("strength_inferred", {"topic": topic}))

    if "explain like beginner" in content.lower():
        events.append(("preference_set", {"level": "intro"}))

    return events


def apply_memory(db: Session, user_id: str, events):
    profile = db.query(models.UserProfile).filter(
        models.UserProfile.user_id == user_id
    ).first()

    for event_type, payload in events:

        memory_event = models.MemoryEvent(
            user_id=user_id,
            event_type=event_type,
            payload=payload,
            confidence=0.7
        )
        db.add(memory_event)

        if event_type == "weakness_inferred":
            profile.weaknesses[payload["topic"]] = True

        if event_type == "strength_inferred":
            profile.strengths[payload["topic"]] = True

        if event_type == "preference_set":
            profile.preferred_level = payload["level"]

    db.commit()