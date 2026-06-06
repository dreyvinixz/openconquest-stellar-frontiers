from sqlalchemy import Column, String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Match(Base):
    __tablename__ = "matches"

    id = Column(String, primary_key=True, index=True)
    room_id = Column(String, ForeignKey("rooms.id"), unique=True)
    state_json = Column(JSON, nullable=False) # Isolamento da Engine: o estado fica aqui
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Optional: we can add relationship to room if we want:
    # room = relationship("Room")
