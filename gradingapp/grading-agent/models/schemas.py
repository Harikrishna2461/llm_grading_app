from pydantic import BaseModel


class EssayRequest(BaseModel):
    essay: str
