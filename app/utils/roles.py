"""
Здесь будет написан декоратор проверки необходимой роли
"""
from functools import wraps
from collections import namedtuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.users import User
from app.log import get_logger
from app.jwt_secrets_token import decode_info_from_token

# init logger
logger = get_logger(__name__)

AccessToken = namedtuple("AccessToken", ['token'])


def check_role(access_role: list[str]):
    """
    Декоратор проверки роли для доступа к API
    :param access_role: роли, которым есть доступ к данному endpoint
    :return:
    """
    def decorator(fun):
        @wraps(fun)
        async def wrapped(*args, **kwargs):
            logger.info(f'args и kwargs в check_role {args} {kwargs}')
            session = kwargs.get('session')
            schema = kwargs.get('schema', None)
            if not schema:
                schema = AccessToken(token=kwargs.get('token'))
            await session.begin()
            try:
                where = User.login == await decode_info_from_token(token=schema.token)
                exist_user = await session.execute(select(User.role).where(where))
                current_user_role: str = exist_user.scalar()  # в этом моменте получаем только роль
                logger.debug(f"Полученный пользователь по токену {exist_user}")
                await session.commit()
            except Exception:
                logger.exception("Время действия токена пришло в негодность",
                                 exc_info=True)
                await session.rollback()
            else:
                # если привилегии пользователя разрешают выполнить запрос, то он выполнится
                if current_user_role in access_role:
                    return await fun(*args, **kwargs)
                else:
                    logger.warning("Доступ запрещен, не хватает прав!")
                    pass
        return wrapped
    return decorator


