from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.db import get_db
from app.models import Case
from app.schemas import CaseOut, VerdictUpdate

router = APIRouter(prefix="/api/v1/cases", dependencies=[Depends(require_api_key)])

STATUSES = ["new", "in_review", "confirmed_phish", "false_positive"]


@router.get("", response_model=list[CaseOut])
def list_cases(status: str | None = None, category: str | None = None, db: Session = Depends(get_db)):
    query = select(Case).order_by(Case.id.desc())
    if status:
        query = query.where(Case.status == status)
    if category:
        query = query.where(Case.category == category)

    results = []
    for case in db.scalars(query).all():
        results.append(case.to_dict())
    return results


@router.get("/{case_id}", response_model=CaseOut)
def get_case(case_id: int, db: Session = Depends(get_db)):
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return case.to_dict()


@router.patch("/{case_id}", response_model=CaseOut)
def set_verdict(case_id: int, update: VerdictUpdate, db: Session = Depends(get_db)):
    if update.status not in STATUSES:
        raise HTTPException(status_code=400, detail="Unknown status")

    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    case.status = update.status
    if update.notes is not None:
        case.notes = update.notes

    db.commit()
    return case.to_dict()
