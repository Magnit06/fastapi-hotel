import datetime

import jwt

from config import get_config
from app.log import get_logger

conf = get_config()
logger = get_logger(__name__)


async def create_jwt_token(user: str) -> str:
    payload = dict(login=user)
    payload.update(dict(exp=datetime.datetime.utcnow() + datetime.timedelta(minutes=conf.JWT_EXPIRE)))
    token = jwt.encode(
        payload=payload,
        key=conf.JWT_SECRET_KEY,
        algorithm=conf.JWT_ALGORITHM
    )
    return token


async def decode_info_from_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            jwt=token,
            key=conf.JWT_SECRET_KEY,
            algorithms=conf.JWT_ALGORITHM,
            options={"require": ["exp", "login"]}
        )
    except jwt.exceptions.ExpiredSignatureError:
        logger.exception("Истек срок годности токена", exc_info=True)
        return None
    else:
        return payload["login"]
