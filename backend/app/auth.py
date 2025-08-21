from sqlalchemy import select
import jwt
from config import settings
from passlib.context import CryptContext
import datetime
from datetime import timedelta
import uuid
from models import User
from fastapi import HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from redis_client import get_redis


SECRET_KEY = settings.hash.secret
ALGORITHM = settings.hash.algorithm
ACCESS_TOKEN_LIFETIME = settings.hash.access_token_lifetime
REFRESH_TOKEN_LIFETIME = settings.hash.refresh_token_lifetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_tokens(data: dict) -> tuple[str, str]:
    """
    Метод для создания access и refresh токенов.
    access и refresh - jwt токены, со сроками жизни 15 минут и 30 дней соответственно.
    Сохраняет айди каждого рефреш токена как ключ и айди юзера как значение для "блеклиста" токенов.
    """
    to_encode = {
        'id': str(data['id']),
        'email': data['email']
    }
    acc_expire = datetime.datetime.now(datetime.timezone.utc) + timedelta(minutes=ACCESS_TOKEN_LIFETIME)
    refresh_expire = datetime.datetime.now(datetime.timezone.utc) + timedelta(days=REFRESH_TOKEN_LIFETIME)
    access_payload = {
        **to_encode, 
        'type': 'access',
        'exp': acc_expire
    }
    refresh_payload = {
        **to_encode, 
        'type': 'refresh',
        'exp': refresh_expire,
        'token_id': str(uuid.uuid4())
    }
    await store_token_to_redis(refresh_payload['token_id'], to_encode['id'])
    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)
    refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm=ALGORITHM)
    return (access_token, refresh_token)


def hash_password(password: str) -> str:
    """Хеширование пароля через CryptContext"""
    return pwd_context.hash(str(password))


async def get_user_by_id(id: uuid, session: AsyncSession) -> User:
    """Метод для получения юзера из базы данных по его айди"""
    query = select(User).where(User.id == id)
    user = await session.scalar(query)
    if not user:
        raise HTTPException(status_code=404, detail="User with this id was not found")
    return user


async def get_user_by_email(email: str, session: AsyncSession) -> User:
    """Метод для получения юзера из базы данных по email"""
    query = select(User).where(User.email == email)
    user = await session.scalar(query)
    if not user:
        raise HTTPException(404, "User with this email was not found")
    return user


async def verify_password(email: str, password: str, session: AsyncSession) -> bool:
    """Метод, получающий юзера из базы и сверяющий пароли."""
    user = await get_user_by_email(email, session)
    return pwd_context.verify(password, user.hashed_password)


def api_key_header(authorization: str = Header(...)) -> str:
    """Метод для обработки входящего токена авторизации в заголовках"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"require": ["exp"], "verify_exp": True})
        user_id = payload.get("id")
        type = payload.get("type")
        if type is None or type != 'access':
            raise HTTPException(status_code=401, detail='Wrong auth token')
        return user_id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authorization token")


async def store_token_to_redis(token_id: str, user_id: str) -> None:
    """Метод, сохраняющий айди токенов в редис, для создания блеклиста рефреш токенов"""
    redis = await get_redis()
    await redis.set(token_id, user_id, ex=REFRESH_TOKEN_LIFETIME*60*60*24)


async def delete_token_from_redis(token_id: str) -> None:
    """Метод, удаляющий айди неактуальные токены из редиса"""
    redis = await get_redis()
    await redis.delete(token_id)


async def verify_refresh_token(token_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    """Метод, проверяющий на актуальность рефреш токен"""
    redis = await get_redis()
    stored_user_id = await redis.get(token_id)
    if not stored_user_id or stored_user_id != user_id:
        return False
    return True


async def refresh_token(refresh_token: str):
    """Метод для обновления рефреш и аксесс токенов по рефреш токену"""
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM], options={"require": ["exp"], "verify_exp": True})
        type = payload.get('type')
        user_id = payload.get('id')
        token_id = payload.get('token_id')
        is_valid = await verify_refresh_token(token_id, user_id)
        if type is None or type != 'refresh' or is_valid != True:
            raise HTTPException(status_code=401, detail='Wrong auth token')
        new_payload = {
            'id': user_id,
            'email': payload['email']
        }
        await delete_token_from_redis(str(token_id))
        return create_tokens(new_payload)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authorization token")
        
