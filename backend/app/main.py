from fastapi import FastAPI

from app.api import analyze, cases
from app.db import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Phishing Analyzer")

app.include_router(analyze.router)
app.include_router(cases.router)


@app.get("/health")
def health():
    return {"status": "ok"}
