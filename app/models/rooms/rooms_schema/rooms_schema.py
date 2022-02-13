from decimal import Decimal
from datetime import date
import uuid

from pydantic import BaseModel


class BookingNumberBase(BaseModel):
    date_in: date
    date_out: date
    room_name: int  # номер комнаты на которую бронь
    token: str


class BookingNumberSchema(BaseModel):
    booking_number: uuid.UUID

    class Config:
        orm_mode = True


class RoomBase(BaseModel):
    name: int
    price: Decimal
    number_of_seats: int


class RoomCreate(RoomBase):
    token: str


class RoomSchema(RoomBase):
    id: int
    # показываем брони
    # booking_numbers: list[BookingNumberSchema] = []  # не работает в асинхронном варианте

    class Config:
        orm_mode = True


class RoomSearchResponse(RoomBase):
    """Ответ на поиск номера"""
    pass


class BookingRoomSearchResponse(BaseModel):
    """Ответ на поиск дат по номеру брони"""
    date_in: date
    date_out: date
