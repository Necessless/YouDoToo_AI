from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from api.schemas import RegisterUserData
from auth import create_tokens, hash_password
from database import db_helper
from models import User

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