from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.database import Base

class DNSCheck(Base):
    __tablename__ = "dns_checks"

    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=False)

    record_type = Column(String(10), nullable=False, default="A")
    resolved_value = Column(String(255), nullable=True)
    latency_ms = Column(Integer, nullable=True)

    checked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    domain = relationship("Domain", back_populates="checks")
