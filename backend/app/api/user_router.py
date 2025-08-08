from fastapi import APIRouter 

router = APIRouter(prefix='')

@router.get('/register', tags=['public'])
async def register(data: NewUserData):
    