"""
Здесь будет написан декоратор проверки необходимой роли
"""
from functools import wraps

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.users import User
from app.jwt_secrets_token import decode_info_from_token


def check_role(access_role: list[str]):
    """
    Декоратор проверки роли для доступа к API
    :param access_role: роли, которым есть доступ к данному endpoint
    :return:
    """
    def decorator(fun):
        @wraps(fun)
        async def wrapped(schema, session: AsyncSession):
            await session.begin()
            try:
                where = User.login == await decode_info_from_token(token=schema.token)
                exist_user = await session.execute(select(User.role).where(where))
                current_user_role: str = exist_user.scalar()  # в этом моменте получаем только роль
                print(f"exist_user     {exist_user}")
                await session.commit()
            except Exception as trans_except:
                print(f"Что-то в декораторе пошло не так {trans_except}")
                await session.rollback()
            else:
                # если привилегии пользователя разрешают выполнить запрос, то он выполнится
                if current_user_role in access_role:
                    return await fun(schema, session)
                else:
                    print("Доступ запрещен!")
                    pass
        return wrapped
    return decorator


