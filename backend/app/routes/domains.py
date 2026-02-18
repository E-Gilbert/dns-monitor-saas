from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.domain import Domain
from app.schemas.domain import DomainCreate, DomainOut

router = APIRouter(prefix="/domains", tags=["Domains"])

@router.post("", response_model=DomainOut)
def create_domain(payload: DomainCreate, db: Session = Depends(get_db)):
    name = payload.name.strip().lower()

    existing = db.query(Domain).filter(Domain.name == name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Domain already exists")

    domain = Domain(name=name)
    db.add(domain)
    db.commit()
    db.refresh(domain)
    return domain

@router.get("", response_model=list[DomainOut])
def list_domains(db: Session = Depends(get_db)):
    return db.query(Domain).order_by(Domain.created_at.desc()).all()
