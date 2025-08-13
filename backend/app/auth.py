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

SECRET_KEY = settings.hash.secret
ALGORITHM = settings.hash.algorithm
ACCESS_TOKEN_LIFETIME = settings.hash.access_token_lifetime
REFRESH_TOKEN_LIFETIME = settings.hash.refresh_token_lifetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_tokens(data: dict) -> tuple[str, str]:
    """
    Метод для создания access и refresh токенов.
    access и refresh - jwt токены, со сроками жизни 15 минут и 30 дней соответственно
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
        'exp': refresh_expire
    }
    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)
    refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm=ALGORITHM)
    return (access_token, refresh_token)


def hash_password(password: str) -> str:
    """Хеширование пароля через CryptContext"""
    return pwd_context.hash(password)


async def get_user_by_id(id: uuid, session: AsyncSession) -> User:
    """Метод для получения юзера из базы данных по его айди"""
    query = select(User).where(User.id == id)
    user = await session.scalar(query)
    if not user:
        raise HTTPException(404, "User with this id was not found")
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
            raise HTTPException(status_code=401, 'Wrong auth token')
        return user_id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authorization token")

def refresh_token(refresh_token: str):
    """Метод для обновления рефреш и аксесс токенов по рефреш токену"""
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM], options={"require": ["exp"], "verify_exp": True})
        type = payload.get('type')
        if type is None or type != 'refresh':
            raise HTTPException(status_code=401, 'Wrong auth token')
        new_payload = {
            'id': payload['id'],
            'email': payload['email']
        }
        return create_tokens(new_payload)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authorization token")
        
