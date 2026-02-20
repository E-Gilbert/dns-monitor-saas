from fastapi import FastAPI
from app.db.database import Base, engine
from app.routes.domains import router as domains_router
from app.scheduler import start_scheduler, shutdown_scheduler

# Import models so SQLAlchemy knows them before create_all
from app.models.domain import Domain  # noqa: F401
from app.models.dns_check import DNSCheck  # noqa: F401

app = FastAPI(title="DNS Monitor SaaS", version="0.1.0")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    start_scheduler()

@app.on_event("shutdown")
def on_shutdown():
    shutdown_scheduler()


app.include_router(domains_router)

