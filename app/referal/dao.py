from sqlalchemy import select, delete

from app.dao.base import BaseDao
from app.database import async_session_maker
from app.referal.models import ReferralCode, Referral


class ReferralCodeDAO(BaseDao):
    model = ReferralCode

    @classmethod
    async def find_code_user_id(cls, code_user_id: int):
        async with async_session_maker() as session:
            query = select(ReferralCode).filter_by(user_id=code_user_id)
            result = await session.execute(query)
            code_info = result.scalar_one_or_none()
            return code_info

    @classmethod
    async def find_code(cls, code_referral: str):
        async with async_session_maker() as session:
            query = select(ReferralCode).filter_by(code=code_referral)
            result = await session.execute(query)
            code_info = result.scalar_one_or_none()
            return code_info

    @classmethod
    async def delete_code_by_id(cls, code_id: int):
        async with async_session_maker() as session:
            async with session.begin():
                query = select(cls.model).filter_by(id=code_id)
                result = await session.execute(query)
                code_to_delete = result.scalar_one_or_none()

                if not code_to_delete:
                    return None

                await session.execute(
                    delete(cls.model).filter_by(id=code_id)
                )

                await session.commit()
                return code_id


class ReferralDAO(BaseDao):
    model = Referral

    @classmethod
    async def get_referrals_by_referrer_id(cls, referrer_id: int):
        async with async_session_maker() as session:
            query = select(Referral).filter_by(referrer_id=referrer_id)
            result = await session.execute(query)
            referrals = result.scalars().all()
            return referrals
