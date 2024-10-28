from app.dao.base import BaseDao
from app.database import async_session_maker
from app.users.models import User
from sqlalchemy import select
class UsersDAO(BaseDao):
    model = User

    @classmethod
    async def get_referral_code_by_email(cls, email: str):
        async with async_session_maker() as session:
            query = select(User).filter_by(email=email)
            result = await session.execute(query)
            code_info = result.scalar_one_or_none()
            if code_info:
                return code_info
            else:
                return None



