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
        result = {}
        for column in self.__table__.columns:
            result[column.name] = getattr(self, column.name)
        return result
