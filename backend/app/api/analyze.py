from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.db import get_db
from app.schemas import CaseOut, EmailSubmission
from app.services.pipeline import create_case

router = APIRouter(prefix="/api/v1")


@router.post("/analyze", response_model=CaseOut, dependencies=[Depends(require_api_key)])
def analyze_email(submission: EmailSubmission, db: Session = Depends(get_db)):
    case = create_case(db, submission)
    return case.to_dict()
