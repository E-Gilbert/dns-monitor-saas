from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.config import CHECK_INTERVAL_SECONDS
from app.db.database import SessionLocal
from app.dns_client import resolve_a
from app.models.domain import Domain
from app.models.dns_check import DNSCheck

scheduler = BackgroundScheduler()

def run_checks_job():
    db: Session = SessionLocal()
    try:
        domains = db.query(Domain).all()

        for domain in domains:
            try:
                ip, latency_ms = resolve_a(domain.name)
            except Exception:
                # if DNS fails, still store a check with resolved_value=None
                ip, latency_ms = None, None

            # last check for comparison (optional: can compute and log)
            last = (
                db.query(DNSCheck)
                .filter(DNSCheck.domain_id == domain.id)
                .order_by(DNSCheck.checked_at.desc())
                .first()
            )
            previous_value = last.resolved_value if last else None
            changed = (
                previous_value is not None and ip is not None and ip != previous_value
            )

            check = DNSCheck(
                domain_id=domain.id,
                record_type="A",
                resolved_value=ip,
                latency_ms=latency_ms,
            )
            db.add(check)
            db.commit()

            # (Optional) print change events to terminal for now
            if changed:
                print(f"[DNS CHANGE] {domain.name}: {previous_value} -> {ip}")

    finally:
        db.close()

def start_scheduler():
    # Avoid duplicate jobs on reload
    if scheduler.get_job("dns_checks_job"):
        return

    scheduler.add_job(
        run_checks_job,
        "interval",
        seconds=CHECK_INTERVAL_SECONDS,
        id="dns_checks_job",
        replace_existing=True,
    )
    scheduler.start()

def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
