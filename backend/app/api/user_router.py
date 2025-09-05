from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from api.schemas import (
    ProfileUpdate,
    RegisterUserData,
    LoginData,
    ConfidentialData
    )
from auth import (
    create_tokens,
    hash_password,
    api_key_header,
    verify_password,
    service_refresh_tokens,
    logout_refresh_token,
)
from api.utils import get_user
from database import db_helper
from models import User


router = APIRouter(prefix="/v1/user")


@router.post("/register", tags=["public", "profile"])
async def register_user(
    data: RegisterUserData, session: AsyncSession = Depends(db_helper.session_getter)
):
    try:
        user = User(
            email=data.email,
            name=data.name,
            last_name=data.last_name,
            hashed_password=hash_password(data.password),
        )
        session.add(user)
        await session.commit()
        tokens = await create_tokens({"id": user.id, "email": user.email})
        return {"access": tokens[0], "refresh": tokens[1]}
    except IntegrityError:
        raise HTTPException(
            status_code=409, detail="User with this email is already registered"
        )


@router.get("/secret", tags=["test"])
async def secured_method(user_id: str = Depends(api_key_header)):
    return {"user_id": user_id}


@router.post("/tokens/refresh", tags=["secret"])
async def refresh_tokens(refresh: str = Header(...)):
    new_tokens = await service_refresh_tokens(refresh)
    return {"access": new_tokens[0], "refresh": new_tokens[1]}


@router.post("/login", tags=["public", "profile"])
async def login_method(
    data: LoginData, session: AsyncSession = Depends(db_helper.session_getter)
):
    user = await get_user(session, email=data.email)
    isValid = await verify_password(data.email, data.password, session, user)
    if isValid is not True:
        raise HTTPException(status_code=401, detail="Wrong password")
    payload_data = {"id": user.id, "email": data.email}
    tokens = await create_tokens(payload_data)
    return tokens


@router.post("/logout", tags=["private", "profile"])
async def logout_method(
    user_id: str = Depends(api_key_header), refresh: str = Header(...)
):
    resp = await logout_refresh_token(token=refresh)
    return resp


@router.patch("/update", tags=["private", "profile"])
async def update_profile(
    new_data: ProfileUpdate,
    user_id: str = Depends(api_key_header),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    user = await get_user(session, id=user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    new_data_dict = new_data.model_dump(exclude_none=True)
    for key, value in new_data_dict.items():
        setattr(user, key, value)
    await session.commit()
    return user


@router.post("/update/confidential", tags=["private", "confidential"])
async def change_confidentials(
    confidential_data: ConfidentialData,
    user_id: str = Depends(api_key_header),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    user = await get_user(session, id=user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    confidential_data = confidential_data.model_dump(exclude_none=True)
    for key, value in confidential_data.items():
        if key == "new_password":
            key = "hashed_password"
            value = hash_password(value)
        if key == "new_email":
            key = "email"
        setattr(user, key, value)
    await session.commit()
    return user


@router.post("/verify-password", tags=["private", "confidential"])
async def check_passwords(
    input_password: SecretStr,
    user_id: str = Depends(api_key_header),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    user = await get_user(session, id=user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    isValid = await verify_password(user.email, input_password, session, user)
    if isValid is not True:
        raise HTTPException(status_code=401, detail="Wrong password")
    return {"success": True}
