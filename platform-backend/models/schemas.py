from pydantic import BaseModel


class ProcessRequest(BaseModel):
    essay: str
    submission_id: str = ""
