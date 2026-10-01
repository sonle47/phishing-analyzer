from pydantic import BaseModel


class EmailSubmission(BaseModel):
    raw_eml: str


class VerdictUpdate(BaseModel):
    status: str
    notes: str | None = None
