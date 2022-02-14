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

    id = Column(Integer, primary_key=True,
                index=True, autoincrement=True)
    price = Column(DECIMAL, nullable=False, comment="Цена за ночь")
    name = Column(Integer, nullable=False, unique=True, index=True,
                  comment="Номер комнаты")
    number_of_seats = Column(SmallInteger, nullable=False, index=True,
                             comment="количество мест")
    booking_numbers = relationship("BookingNumber", back_populates="room",
                                   cascade="all, delete")

    def __str__(self) -> str:
        return f"<{Room.__name__}> {self.name}"

    def __repr__(self) -> str:
        return f"<{Room.__name__}> {self.name}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "price":  self.price,
            "name": self.name,
            "number_of_seats": self.number_of_seats
        }


class BookingNumber(Base, TimeCheckInterface):
    """
    Номер брони
    """
    __tablename__ = "booking_numbers"

    id = Column(Integer, primary_key=True, index=True,
                autoincrement=True)
    booking_number = Column(UUID(as_uuid=True),
                            nullable=False, unique=True,
                            comment="Номер брони", default=uuid4,
                            index=True)
    date_in = Column(Date, nullable=False,
                     unique=False, index=True,
                     comment="Дата заезда")
    date_out = Column(Date, nullable=False,
                      unique=False, index=True,
                      comment="Дата выезда")
    room_id = Column(Integer, ForeignKey('rooms.id', ondelete="CASCADE"),
                     index=True, comment="Внешний ключ к комнатам")

    room = relationship("Room", back_populates="booking_numbers")

    def __str__(self) -> str:
        return f"<{BookingNumber.__name__}> {self.booking_number}"

    def __repr__(self) -> str:
        return f"<{BookingNumber.__name__}> {self.booking_number}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "booking_number": self.booking_number,
            "date_in": self.date_in,
            "date_out": self.date_out,
            "room_id": self.room_id,
        }
