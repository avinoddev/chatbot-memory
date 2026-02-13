from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    email: str


class CreateThreadRequest(BaseModel):
    user_id: str

class CreateMessageRequest(BaseModel):
    thread_id: str
    role: str   # "user" or "assistant"
    content: str