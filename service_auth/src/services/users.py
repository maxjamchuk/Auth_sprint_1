import uuid
import logging

from functools import lru_cache
from typing import List, Optional
from http import HTTPStatus

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import check_password_hash, generate_password_hash

from src.db.postgres import get_session, DbService
from src.schemas.entity import ShemaAccountHistory, Status, UserInDB
from src.models.entity import AccountHistory, User
from src.core.config import settings
from .abstracts import AsyncUsersService

logging.config.fileConfig('./src/core/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


class UserService(AsyncUsersService):
    def __init__(self, db_service: DbService) -> None:
        self.db_service = db_service

    async def get_account_history(
        self,
        user_id: uuid
    ) -> Optional[List[ShemaAccountHistory]]:
        try:
            logger.info(f"""Start to get account history. Params:
            user_id - {user_id}""")
            account_history = await self.db_service.simple_select(
                what_select=AccountHistory,
                where_select=[AccountHistory.user_id, user_id],
                order_select=AccountHistory.created_at.desc
            )
            logger.info("Finish to get account history")
            return [
                ShemaAccountHistory(
                    user_agent=login.user_agent,
                    created_at=login.created_at
                )
                for login in account_history
            ]
        except Exception as err:
            logger.error(f"Couldn't to get account history, Err - {err}")
            return None

    async def change_password(
        self,
        current_password: str,
        password: str,
        user_info: UserInDB
    ) -> Status:
        try:
            logger.info("Start to change password")
            user = await self.db_service.simple_select(
                what_select=User,
                where_select=[User.email, user_info.email]
            )
            user = user[0]

            password_match = check_password_hash(
                pwhash=user.hash_password,
                password=settings.SAULT + user.email + current_password
            )

            if not password_match:
                return HTTPStatus.UNAUTHORIZED

            user.hash_password = generate_password_hash(
                password=settings.SAULT + user.email + password
            )
            await self.db_service.db.commit()
            logger.info("End to change password")
            return Status(status='success')
        except Exception as err:
            logger.error(f"Couldn't to change password, Err - {err}")
            return None
        # add condition when user want to out of all his gadgets.

    async def change_email(
        self,
        current_password: str,
        new_email: str,
        user_info: UserInDB
    ) -> Status:
        try:
            logger.info("Start to change email")
            # check new_email in db
            check_email = await self.db_service.simple_select(
                what_select=User,
                where_select=[User.email, new_email]
            )
            if len(check_email) > 0:
                return HTTPStatus.CONFLICT

            user = await self.db_service.simple_select(
                what_select=User,
                where_select=[User.email, user_info.email]
            )
            user = user[0]

            password_match = check_password_hash(
                pwhash=user.hash_password,
                password=settings.SAULT + user_info.email + current_password
            )
            if not password_match:
                return HTTPStatus.UNAUTHORIZED

            user.email = new_email
            user.hash_password = generate_password_hash(
                password=settings.SAULT + new_email + current_password
            )
            await self.db_service.db.commit()
            logger.info("Finish to change email")
            return Status(status='success')
        except Exception as err:
            logger.error(f"Couldn't to change email. Err - {err}")
            return None


@lru_cache()
def user_service(
    db: AsyncSession = Depends(get_session),
) -> UserService:
    return UserService(
        db_service=DbService(db=db)
    )
