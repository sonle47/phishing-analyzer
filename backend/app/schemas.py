from pydantic import BaseModel


class EmailSubmission(BaseModel):
    raw_eml: str


class VerdictUpdate(BaseModel):
    status: str
    notes: str | None = None


class CaseOut(BaseModel):
    id: int
    sender: str
    subject: str
    body: str | None
    urls: list[str]
    signals: dict
    score: float
    category: str
    status: str
    notes: str | None
