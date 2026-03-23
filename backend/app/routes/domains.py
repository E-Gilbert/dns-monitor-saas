from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.domain import Domain
from app.models.dns_check import DNSCheck
from app.schemas.domain import DomainCreate, DomainOut
from app.schemas.dns_check import DNSCheckOut
from app.dns_client import resolve_a
from services.ai_insights import generate_dns_insight

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

    # AI logic trigger:
    # When the DNS value changes, we generate a short "DNS Insight" that helps
    # interpret the impact. This is simulated LLM logic with a safe fallback.
    change = None
    insight = None
    if changed:
        change = f"{previous_value} -> {ip}"
        try:
            insight = generate_dns_insight(check.record_type, previous_value, ip)
        except Exception:
            # generate_dns_insight() should never raise, but we keep this as a final safety net.
            insight = None

    # Return a response model instead of mutating SQLAlchemy relationship fields.
    return DNSCheckOut(
        id=check.id,
        domain_id=check.domain_id,
        record_type=check.record_type,
        resolved_value=check.resolved_value,
        latency_ms=check.latency_ms,
        checked_at=check.checked_at,
        domain=domain.name,
        change=change,
        insight=insight,
        previous_value=previous_value,
        changed=changed,
    )


@router.get("/{domain_id}/history", response_model=list[DNSCheckOut])
def get_history(domain_id: int, db: Session = Depends(get_db)):
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    # Compute change + AI insight on the fly.
    # (We do not persist insight to keep this minimal; it can be regenerated safely.)
    checks = (
        db.query(DNSCheck)
        .filter(DNSCheck.domain_id == domain_id)
        .order_by(DNSCheck.checked_at.asc())
        .all()
    )

    # Safe fallback: return empty list when no history exists.
    if not checks:
        return []

    previous_value = None
    response_items = []
    for check in checks:
        # Keep these computed fields consistent with run_check().
        changed = (
            previous_value is not None
            and check.resolved_value is not None
            and check.resolved_value != previous_value
        )

        change = None
        insight = None
        if changed:
            change = f"{previous_value} -> {check.resolved_value}"
            try:
                # AI logic trigger: only when DNS value changes.
                insight = generate_dns_insight(
                    check.record_type,
                    previous_value,
                    check.resolved_value,
                )
            except Exception:
                insight = None

        response_items.append(
            DNSCheckOut(
                id=check.id,
                domain_id=check.domain_id,
                record_type=check.record_type,
                resolved_value=check.resolved_value,
                latency_ms=check.latency_ms,
                checked_at=check.checked_at,
                domain=domain.name,
                change=change,
                insight=insight,
                previous_value=previous_value,
                changed=changed,
            )
        )

        previous_value = check.resolved_value

    # Safe fallback for "no DNS changes" cases: return [].
    changed_items = [item for item in response_items if item.changed]
    if not changed_items:
        return []

    # Return newest changed events first for the UI.
    return list(reversed(changed_items))
