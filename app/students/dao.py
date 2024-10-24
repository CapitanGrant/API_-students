from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.students.models import Student, Major
from app.dao.base import BaseDao
from app.database import async_session_maker

class StudentDAO(BaseDao):
    model = Student

    @classmethod
    async def find_full_data(cls, student_id: int):
        async with async_session_maker() as session:
            # Первый запрос для получения информации о студенте
            query = select(cls.model).options(joinedload(cls.model.major)).filter_by(id=student_id)
            result = await session.execute(query)
            student_info = result.scalar_one_or_none()

            # Если студент не найден, возвращаем None
            if not student_info:
                return None

            student_data = student_info.to_dict()
            student_data["major"] = student_info.major_name
            return student_data