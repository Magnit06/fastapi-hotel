import uuid
from datetime import date

from fastapi import Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_
from asyncpg.exceptions import UniqueViolationError

from app import app
from app.models.users.users_schema import (UserSchema, UserCreate, UserLogin, UserToken,
                                           UserAddManagerCreate, UserAddManagerSchema)
from app.models.rooms.rooms_schema import RoomSchema, RoomCreate
from app.models.rooms.rooms_schema import BookingNumberSchema, BookingNumberBase
from app.models.rooms.rooms_schema import RoomSearchResponse, BookingRoomSearchResponse
from app.models.users import User
from app.models.rooms import Room, BookingNumber
from app.db import get_session
from app.jwt_secrets_token import create_jwt_token
from app.utils import check_role
from app.log import get_logger

# init logger
logger = get_logger(__name__)


@app.get("/")
async def home():
    return {"Привет!": "Ты  находишься на домашнем endpoint"}


@app.post("/api/register",
          response_model=UserSchema,
          status_code=201,
          tags=['register'],
          summary="Регистрируем пользователя в БД",
          description="Регистрируем пользователя в БД на основе переданных логина и пароля")
async def register(user: UserCreate, session: AsyncSession = Depends(get_session)):
    await session.begin()
    try:
        new_user = User(login=user.login, role=user.role)
        new_user.password = user.password
        session.add(new_user)
        await session.commit()
    except Exception:
        logger.exception("Ошибка добавления пользователя!", exc_info=True)
        await session.rollback()
    else:
        logger.info(f"Пользователь {new_user.login} успешно добавлен")
        await session.refresh(new_user)
        return new_user


@app.post("/api/login",
          status_code=200,
          tags=["login"],
          summary="Получаем токен",
          description="Получаем токен на основе регистрационных данных")
async def login(user: UserLogin, session: AsyncSession = Depends(get_session)):
    await session.begin()
    try:
        exist_user = await session.execute(select(User).where(User.login == user.login))
        exist_user = exist_user.scalars().first()
        logger.debug(f"Полученный пользователь {user.login} {user.password}")
        if exist_user and exist_user.check_password(inp_passwd=user.password):
            token = await create_jwt_token(user=exist_user.login)
        else:
            logger.debug("Неправильные логин пользователя или пароль")
            return HTTPException(status_code=401,
                                 detail="Неправильные логин пользователя или пароль")
        await session.commit()
    except Exception:
        logger.exception("Ошибка извлечения записи из БД по логину и паролю", exc_info=True)
        await session.rollback()
    else:
        logger.info(f"Токен для пользователя {exist_user.login} выдан")
        return UserToken(token=token)


@app.post('/api/add/manager',
          response_model=UserAddManagerSchema,
          status_code=201,
          tags=["manager"],
          summary="Добавляем менеджера",
          description="Добавляем менеджера с логином и паролем, передав секретный токен")
@check_role(access_role=["A"])
async def add_manager(schema: UserAddManagerCreate, session: AsyncSession = Depends(get_session)):
    await session.begin()
    try:
        new_manager = User(login=schema.login, role=schema.role)
        new_manager.password = schema.password
        session.add(new_manager)
        await session.commit()
    except UniqueViolationError:
        logger.exception(f"Ошибка добавления пользователя {schema.login}", exc_info=True)
        await session.rollback()
    else:
        logger.info(f"Пользователь {schema.login} успешно добавлен")
        await session.refresh(new_manager)
        return new_manager


@app.post("/api/add/room_in_hotel",
          response_model=RoomSchema,
          status_code=201,
          tags=["add_room_in_hotel"],
          summary="Добавляем комнату",
          description="Добавляем комнату в отель")
@check_role(["A"])
async def add_room_in_hotel(schema: RoomCreate, session: AsyncSession = Depends(get_session)):
    await session.begin()
    try:
        new_room = Room(name=schema.name, price=schema.price,
                        number_of_seats=schema.number_of_seats)
        session.add(new_room)
        await session.commit()
    except UniqueViolationError:
        logger.exception(f"Ошибка создания комнаты {schema.name}", exc_info=True)
        await session.rollback()
    else:
        logger.info(f"Комната {new_room.name} успешно добавлена")
        await session.refresh(new_room)
        return new_room


@app.post("/api/booking/room",
          status_code=201,
          tags=['booking_room'],
          summary="Забронировать номер",
          description="Бронирование номера")
@check_role(access_role=["A", "M"])
async def booking_room(schema: BookingNumberBase, session: AsyncSession = Depends(get_session)):
    await session.begin()
    try:
        # + Дата заезда и отъезда
        # одного номера брони не могут быть равны
        if schema.date_in == schema.date_out:
            logger.debug("Даты заезда и выезда не могут быть равны, "
                         f"заезд {schema.date_in} == выезд {schema.date_out}")
            return HTTPException(status_code=412,
                                 detail=str("Даты заезда и выезда не могут быть равны, "
                                            f"заезд {schema.date_in} == выезд {schema.date_out}"))

        # получаем id комнаты, чтобы на его основе валидировать бронь
        where_room_name = Room.name == schema.room_name
        query = await session.execute(select(Room.id)
                                      .where(where_room_name))
        room_id = query.scalar()

        # проверим даты на уникальность для конкретного номера, для проверки хватит одной записи
        where = or_(BookingNumber.date_in == schema.date_in,
                    BookingNumber.date_out == schema.date_out)
        query = await session.execute(select(BookingNumber.id,
                                             BookingNumber.date_in,
                                             BookingNumber.date_out)
                                      .where(where, and_(BookingNumber.room_id == room_id)).limit(1))
        exist_booking = query.first()
        if exist_booking:
            logger.warning(f"Такая дата въезда {exist_booking.date_in} или "
                           f"выезда {exist_booking.date_out} уже существует "
                           f"в записи {exist_booking.id}, выберите другие даты")
            return HTTPException(status_code=412,
                                 detail=str(f"Такая дата въезда {exist_booking.date_in} или "
                                            f"выезда {exist_booking.date_out} уже существует, выберите другие даты"))

        # + даты разных номеров брони одной комнаты не могут пересекаться
        # здесь смотрю, чтобы дата въезда не была меньше даты выезда
        where = and_(schema.date_in < BookingNumber.date_out,
                     BookingNumber.room_id == room_id)
        query = await session.execute(select(BookingNumber.id)
                                      .where(where))
        crossed_reservation = query.first()
        if crossed_reservation:
            logger.error("Даты разных номеров брони одной комнаты не могут пересекаться")
            return HTTPException(status_code=412,
                                 detail="Даты разных номеров брони одной комнаты не могут пересекаться")

        new_booking = BookingNumber(date_in=schema.date_in,
                                    date_out=schema.date_out,
                                    room_id=room_id)
        session.add(new_booking)
        await session.commit()
    except Exception:
        logger.exception(f"Ошибка создания брони на комнату {schema.room_name}")
        await session.rollback()
    else:
        logger.info(f"Бронь на комнату {schema.room_name} успешно создалась "
                    f"{schema.date_in} {schema.date_out}")
        await session.refresh(new_booking)
        return BookingNumberSchema(**new_booking.to_dict())


@app.get('/api/room/search',
         response_model=list[RoomSearchResponse],
         status_code=200,
         tags=["search_room"],
         summary="Поиск номера",
         description="Поиск номера на основании дат и кол-ва мест")
@check_role(access_role=["A", "M"])
async def search_room(data_in: date = Query(...,
                                            title="Дата въезда",
                                            example="YYYY-MM-DD"),
                      data_out: date = Query(...,
                                             title="Дата выезда",
                                             example="YYYY-MM-DD"),
                      number_of_seats: int = Query(...,
                                                   title="Количество мест",
                                                   example=int(2)),
                      token: str = Query(...,
                                         title="Токен доступа"),
                      session: AsyncSession = Depends(get_session)):
    await session.begin()
    try:
        where = and_(BookingNumber.date_in == data_in,
                     BookingNumber.date_out == data_out,
                     Room.number_of_seats == number_of_seats)
        query = await session.execute(select(Room.name,
                                             Room.number_of_seats,
                                             Room.price).join(BookingNumber)
                                      .where(where))
        rooms = query.all()
        logger.debug(f"Результат запроса на поиск номера {rooms}")
        await session.commit()
    except Exception:
        await session.rollback()
        logger.exception("Ошибка поиска номера", exc_info=True)
    else:
        return rooms


@app.get('/api/booking/room/date',
         status_code=200,
         tags=["get_info_by_booking_room"],
         summary="Поиск дат",
         description="Поиск дат на основании номер брони")
@check_role(['A', 'M'])
async def get_info_by_booking_room(booking_number: uuid.UUID = Query(...,
                                                                     title="Номер брони",
                                                                     example="uuid4"),
                                   token: str = Query(...,
                                                      title="Токен"),
                                   session: AsyncSession = Depends(get_session)):
    await session.begin()
    try:
        where = BookingNumber.booking_number == booking_number
        query = await session.execute(select(BookingNumber.date_in,
                                             BookingNumber.date_out)
                                      .where(where))
        info_by_booking_number = query.first()
        await session.commit()
    except Exception:
        logger.exception("Ошибка получения информации по номеру брони",
                         exc_info=True)
        return HTTPException(status_code=412,
                             detail="Ошибка получения информации по номеру брони")
    else:
        logger.debug(f"Получена информация по номеру брони {info_by_booking_number}")
        return BookingRoomSearchResponse(date_in=info_by_booking_number.date_in,
                                         date_out=info_by_booking_number.date_out)
