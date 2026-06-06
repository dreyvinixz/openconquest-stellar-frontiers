from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.database import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(String, primary_key=True, index=True) # Ex: "A1B2C3"
    max_players = Column(Integer, default=4)
    map_id = Column(String, default="default_galaxy")
    status = Column(String, default="waiting") # waiting, started
    match_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    players = relationship("RoomPlayer", back_populates="room", cascade="all, delete-orphan")

    @property
    def room_code(self) -> str:
        return self.id

class RoomPlayer(Base):
    __tablename__ = "room_players"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    room_id = Column(String, ForeignKey("rooms.id"))
    player_name = Column(String, nullable=False)
    is_host = Column(Boolean, default=False)
    token = Column(String, default=lambda: str(uuid.uuid4()))

    room = relationship("Room", back_populates="players")

    @property
    def name(self) -> str:
        return self.player_name
