from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.domain import Domain
from app.models.dns_check import DNSCheck
from app.schemas.domain import DomainCreate, DomainOut
from app.schemas.dns_check import DNSCheckOut
from app.dns_client import resolve_a

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


@router.post("/{domain_id}/check", response_model=DNSCheckOut)
def run_check(domain_id: int, db: Session = Depends(get_db)):
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    # Resolve DNS (A record)
    try:
        ip, latency_ms = resolve_a(domain.name)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    # (+) Get last check for this domain (if any)
    last = (
        db.query(DNSCheck)
        .filter(DNSCheck.domain_id == domain.id)
        .order_by(DNSCheck.checked_at.desc())
        .first()
    )

    # (+) Compute previous_value + changed flag
    previous_value = last.resolved_value if last else None
    changed = (previous_value is not None and ip is not None and ip != previous_value)

    # Save the new check
    check = DNSCheck(
        domain_id=domain.id,
        record_type="A",
        resolved_value=ip,
        latency_ms=latency_ms,
    )
    db.add(check)
    db.commit()
    db.refresh(check)

    # (+) Attach computed fields to the returned object (not stored in DB)
    check.previous_value = previous_value
    check.changed = changed
    return check


@router.get("/{domain_id}/history", response_model=list[DNSCheckOut])
def get_history(domain_id: int, db: Session = Depends(get_db)):
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    return (
        db.query(DNSCheck)
        .filter(DNSCheck.domain_id == domain_id)
        .order_by(DNSCheck.checked_at.desc())
        .all()
    )
