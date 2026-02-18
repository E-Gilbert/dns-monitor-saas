from fastapi import FastAPI
from app.db.database import Base, engine
from app.routes.domains import router as domains_router

# Import models so SQLAlchemy knows them before create_all
from app.models.domain import Domain  # noqa: F401
from app.models.dns_check import DNSCheck  # noqa: F401

app = FastAPI(title="DNS Monitor SaaS", version="0.1.0")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(domains_router)

@app.get("/")
def root():
    return {"message": "DNS Monitor SaaS API. Visit /docs"}
