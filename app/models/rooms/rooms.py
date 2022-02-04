from uuid import uuid4

from sqlalchemy import (Column, SmallInteger,
                        Integer, DECIMAL, Date, ForeignKey)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimeCheckInterface


class Room(Base, TimeCheckInterface):
    """
    Комнаты
    """
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    price = Column(DECIMAL, nullable=False, comment="Цена за ночь")
    name = Column(Integer, nullable=False, unique=True, comment="Номер комнаты")
    number_of_seats = Column(SmallInteger, nullable=False,
                             comment="количество мест")
    booking_numbers = relationship("BookingNumber", back_populates="room")

    def __str__(self) -> str:
        return f"<{Room.__name__}> {self.name}"

    def __repr__(self) -> str:
        return f"<{Room.__name__}> {self.name}"


class BookingNumber(Base, TimeCheckInterface):
    """
    Номер брони
    """
    __tablename__ = "booking_numbers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    booking_number = Column(UUID(as_uuid=True), nullable=False, unique=True, comment="Номер брони",
                            default=uuid4)
    date_in = Column(Date, nullable=False, unique=False, comment="Дата заезда")
    date_out = Column(Date, nullable=False, unique=False, comment="Дата выезда")
    room_id = Column(Integer, ForeignKey('rooms.id'), comment="Внешний ключ к комнатам")

    room = relationship("Room", back_populates="booking_numbers")

    def __str__(self) -> str:
        return f"<{BookingNumber.__name__}> {self.booking_number}"

    def __repr__(self) -> str:
        return f"<{BookingNumber.__name__}> {self.booking_number}"
