from sqlalchemy import JSON, Column, Float, Integer, String, Text

from app.db import Base


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True)
    sender = Column(String)
    subject = Column(String)
    body = Column(Text)
    urls = Column(JSON)
    signals = Column(JSON)
    score = Column(Float)
    category = Column(String)
    status = Column(String, default="new")
    notes = Column(Text)

    def to_dict(self):
        return {
            "id": self.id,
            "sender": self.sender,
            "subject": self.subject,
            "body": self.body,
            "urls": self.urls,
            "signals": self.signals,
            "score": self.score,
            "category": self.category,
            "status": self.status,
            "notes": self.notes,
        }
