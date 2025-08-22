from fastapi import APIRouter, Depends, Header, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from api.schemas import RegisterUserData
from auth import create_tokens, hash_password, api_key_header, get_user_by_email, verify_password, service_refresh_tokens
from database import db_helper
from models import User
from api.schemas import LoginData

router = APIRouter(prefix='')

@router.post('/register', tags=['public'])
async def register_user(data: RegisterUserData, session: AsyncSession = Depends(db_helper.session_getter)):
    try:
        user = User(
            email=data.email,
            name=data.name,
            last_name=data.last_name,
            hashed_password=hash_password(data.password)
        )
        session.add(user)
        await session.commit()
        tokens = await create_tokens({'id': user.id, 'email': user.email})
        return {
            'access': f'{tokens[0]}',
            'refresh': tokens[1]
        }
    except IntegrityError:
        raise HTTPException(status_code=409, detail="User with this email is already registered")


@router.get('/secret', tags=['test'])
async def secured_method(user_id: str = Depends(api_key_header)):
    return {"user_id": user_id}

@router.post('/tokens/refresh', tags=['secret'])
async def refresh_tokens(refresh: str = Header(...)):
    new_tokens = await service_refresh_tokens(refresh)
    return new_tokens
    

@router.post('/login', tags=['public'])
async def login_method(data: LoginData, session: AsyncSession = Depends(db_helper.session_getter)):
    user = await get_user_by_email(data.email, session)
    isValid = await verify_password(data.email, data.password, session, user)
    if not isValid:
        raise HTTPException(status_code=401, detail='Wrong password')
    payload_data = {'id': user.id, 'email': data.email}
    tokens = await create_tokens(payload_data)
    return tokens

