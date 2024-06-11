from pydantic import BaseModel


class Task(BaseModel):
    title: str
    body: str
