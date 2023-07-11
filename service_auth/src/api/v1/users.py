from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from typing import List

from src.utils.oauth2 import get_current_user
from src.schemas.entity import (
    ShemaAccountHistory, Status, UserInDB, ChangePassword
)
from src.services.users import user_service, UserService

router = APIRouter()


@router.get(
    "/me",
    response_model=UserInDB,
    status_code=HTTPStatus.ACCEPTED,
    summary="Кто я",
    tags=['Пользователь']
)
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    return current_user


@router.get(
    "/account-history",
    response_model=List[ShemaAccountHistory],
    status_code=HTTPStatus.ACCEPTED,
    summary="История входов",
    tags=['Пользователь']
)
async def get_account_history(
    current_user: UserInDB = Depends(get_current_user),
    service_user: UserService = Depends(user_service)
) -> List[ShemaAccountHistory]:
    result = await service_user.get_account_history(current_user.id)
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.BAD_GATEWAY,
            detail="Can't get account history"
        )
    return result


@router.put(
    "/password",
    response_model=Status,
    status_code=HTTPStatus.ACCEPTED,
    summary="Смена пароля",
    tags=['Пользователь']
)
async def change_password(
    change_password_data: ChangePassword,
    current_user: UserInDB = Depends(get_current_user),
    service_user: UserService = Depends(user_service),
 ):

    if change_password_data.password != change_password_data.repeat_password:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='New password and repeat password do not match'
        )

    result = await service_user.change_password(
        current_password=change_password_data.current_password,
        password=change_password_data.password,
        user_info=current_user
    )

    if result == HTTPStatus.UNAUTHORIZED:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Invalid password'
        )

    if not result:
        raise HTTPException(
            status_code=HTTPStatus.BAD_GATEWAY,
            detail="Can't change password"
        )

    return result
