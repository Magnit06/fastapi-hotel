from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_
from datetime import datetime, date

from app import app
from app.models.users.users_schema import (UserSchema, UserCreate, UserLogin, UserToken,
                                           UserAddManagerCreate, UserAddManagerSchema)
from app.models.rooms.rooms_schema import RoomSchema, RoomCreate
from app.models.rooms.rooms_schema import BookingNumberSchema, BookingNumberBase
from app.models.users import User
from app.models.rooms import Room, BookingNumber
from app.db import get_session
from app.jwt_secrets_token import create_jwt_token, decode_info_from_token
from app.utils import check_role


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
    except Exception as trans_except:
        print(f"Ошибка добавления пользователя!\n{trans_except}")
        await session.rollback()
    else:
        await session.refresh(new_user)
        return new_user


@app.post("/api/login",
          response_model=UserToken,
          status_code=200,
          tags=["login"],
          summary="Получаем токен",
          description="Получаем токен на основе регистрационных данных")
async def login(user: UserLogin, session: AsyncSession = Depends(get_session)):
    await session.begin()
    try:
        exist_user = await session.execute(select(User).where(User.login == user.login))
        exist_user = exist_user.scalars().first()
        print(f"exist_user    {exist_user.login} {exist_user.password}")
        if exist_user and exist_user.check_password(inp_passwd=user.password):
            token = await create_jwt_token(user=exist_user.login)
        else:
            return UserToken(token="Неправильные логин пользователя или пароль")
        await session.commit()
    except Exception as trans_except:
        print(f"Ошибка извлечения записи из БД по логину {trans_except}")
        await session.rollback()
    else:
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
    except Exception as trans_except:
        print(f"Ошибка добавления пользователя!\n{trans_except}")
        await session.rollback()
    else:
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
    except Exception as trans_exc:
        print(f"Ошибка создания комнаты {trans_exc}")
        await session.rollback()
    else:
        await session.refresh(new_room)
        return new_room


@app.post("/api/booking/room",
          response_model=BookingNumberSchema,
          status_code=201,
          tags=['booking_room'],
          summary="Забронировать номер",
          description="Бронирование номера")
@check_role(access_role=["A", "M"])
async def booking_room(schema: BookingNumberBase, session: AsyncSession = Depends(get_session)):
    await session.begin()
    try:
        # получаем id комнаты
        where = Room.name == schema.room_name
        exist_room_name = await session.execute(select(Room.id).where(where))
        id_room: int = exist_room_name.scalar()

        where_date = or_(BookingNumber.date_in == schema.date_in,
                         BookingNumber.date_out == schema.date_out)
        where_room_id = and_(BookingNumber.room_id == id_room)
        exist_record = await session.execute(select(BookingNumber.id).where(where_date, where_room_id).limit(1))
        exist_record = exist_record.first()
        if exist_record:
            # TODO доработать этот момент логинга
            return
        # +
        if schema.date_in == schema.date_out or schema.date_in > schema.date_out or \
                schema.date_in < date.today():
            print("Даты заезда и выезда не могут быть равны, "
                  "к тому же заезжать нужно раньше выезда и приезжать не задним числом!!!\n"
                  f"{schema.date_in} == {schema.date_out}")
            return

        # запрос на получение последней даты бронирования запрошенной комнаты
        query = await session.execute(select(BookingNumber.date_in, BookingNumber.date_out)
                                      .where(BookingNumber.room_id == id_room)
                                      .order_by(BookingNumber.id.desc()).limit(1))
        result_date = query.first()
        if result_date:
            print(f"result_date ==== {result_date}")

            # последняя бронь на въезд
            last_booking_date_in = datetime.strptime(
                str(result_date.date_in),
                "%Y-%m-%d"
            )
            # последняя бронь на выезд
            last_booking_date_out = datetime.strptime(
                str(result_date.date_out),
                "%Y-%m-%d"
            )
            # введенная бронь на въезд
            input_date_in = datetime.strptime(
                str(schema.date_in),
                "%Y-%m-%d"
            )
            # введенная бронь на выезд
            input_date_out = datetime.strptime(
                str(schema.date_out),
                "%Y-%m-%d"
            )

            # +
            if input_date_out < last_booking_date_out and input_date_in > last_booking_date_in or \
                    (input_date_out < last_booking_date_out or input_date_in > last_booking_date_in):
                print("Даты разной брони одной комнаты не могут пересекаться\n"
                      f"{input_date_out} < {last_booking_date_out}\n"
                      f"{input_date_in} > {last_booking_date_in}")
                return

            print(f"last_booking_date_out ==== {last_booking_date_out}\n"
                  f"input_date_out ==== {input_date_out}\n"
                  f"input_date_in ==== {input_date_in}\n"
                  f"last_booking_date_in ==== {last_booking_date_in}")

        new_booking = BookingNumber(date_in=schema.date_in,
                                    date_out=schema.date_out,
                                    room_id=id_room)
        session.add(new_booking)
        await session.commit()
    except Exception as trans_exc:
        print(f"Ошибка создания брони на комнату {trans_exc}")
        await session.rollback()
    else:
        await session.refresh(new_booking)
        return new_booking
