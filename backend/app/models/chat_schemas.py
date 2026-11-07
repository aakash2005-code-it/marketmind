from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    stock_context: dict | None = None