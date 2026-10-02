from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.db import get_db
from app.models import Case
from app.schemas import CaseOut, CaseUpdate

router = APIRouter(prefix="/api/v1/cases", dependencies=[Depends(require_api_key)])

ALLOWED_STATUSES = ["new", "in_review", "confirmed_phish", "false_positive"]


@router.get("", response_model=list[CaseOut])
def list_cases(status: str | None = None, category: str | None = None, db: Session = Depends(get_db)):
    query = select(Case).order_by(Case.id.desc())
    if status:
        query = query.where(Case.status == status)
    if category:
        query = query.where(Case.category == category)

    case_dicts = []
    for case in db.scalars(query).all():
        case_dicts.append(case.to_dict())
    return case_dicts


@router.get("/{case_id}", response_model=CaseOut)
def get_case(case_id: int, db: Session = Depends(get_db)):
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return case.to_dict()


@router.patch("/{case_id}", response_model=CaseOut)
def update_case(case_id: int, changes: CaseUpdate, db: Session = Depends(get_db)):
    if changes.status not in ALLOWED_STATUSES:
        raise HTTPException(status_code=400, detail="Unknown status")

    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    case.status = changes.status
    if changes.notes is not None:
        case.notes = changes.notes

    db.commit()
    return case.to_dict()
