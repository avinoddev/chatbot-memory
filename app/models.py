from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import uuid
import enum

from .database import Base


# ---------------------------
# MEMORY ENUMS
# ---------------------------

class MemoryEventType(str, enum.Enum):
    topic_seen = "topic_seen"
    weakness_inferred = "weakness_inferred"
    strength_inferred = "strength_inferred"
    preference_set = "preference_set"
    correction = "correction"


class ExplanationLevel(str, enum.Enum):
    intro = "intro"
    intermediate = "intermediate"
    advanced = "advanced"


# ---------------------------
# CORE MODELS
# ---------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)

    threads = relationship("Thread", back_populates="user")
    profile = relationship("UserProfile", uselist=False, back_populates="user")


class Thread(Base):
    __tablename__ = "threads"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="threads")
    messages = relationship("Message", back_populates="thread")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    thread_id = Column(String, ForeignKey("threads.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    thread = relationship("Thread", back_populates="messages")


# ---------------------------
# USER PROFILE (CROSS-THREAD MEMORY SNAPSHOT)
# ---------------------------

class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)

    study_topics = Column(JSONB, nullable=False, default=dict)
    strengths = Column(JSONB, nullable=False, default=dict)
    weaknesses = Column(JSONB, nullable=False, default=dict)

    preferred_level = Column(
        Enum(ExplanationLevel),
        nullable=True
    )

    preferred_style = Column(JSONB, nullable=True)

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    user = relationship("User", back_populates="profile")


# ---------------------------
# MEMORY EVENTS (APPEND-ONLY AUDIT LOG)
# ---------------------------

class MemoryEvent(Base):
    __tablename__ = "memory_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    thread_id = Column(String, ForeignKey("threads.id"), nullable=True)
    message_id = Column(String, ForeignKey("messages.id"), nullable=True)

    event_type = Column(
        Enum(MemoryEventType),
        nullable=False
    )

    payload = Column(JSONB, nullable=False)

    confidence = Column(Float, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")