from sqlalchemy import select, insert, update, delete, event
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from app.majors.models import Major
from app.students.models import Student
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

    @classmethod
    async def add_student(cls, **student_data: dict):
        async with async_session_maker() as session:
            async with session.begin():
                new_student = Student(**student_data)
                session.add(new_student)
                await session.flush()
                new_student_id = new_student.id
                await session.commit()
                return new_student_id

    @event.listens_for(Student, "after_insert")
    def receive_updates(mapper, connection, target):
        major_id = target.major_id
        connection.execute(
            update(Major)
            .where(Major.id ==major_id)
            .values(count_students=Major.count_students + 1)
        )

    @event.listens_for(Student, "after_delete")
    def receive_delete(mapper, connection, target):
        major_id = target.major_id
        connection.execute(
            update(Major)
            .where(Major.id ==major_id)
            .values(count_students=Major.count_students - 1)
        )

    @classmethod
    async def delete_student_by_id(cls, student_id: int):
        async with async_session_maker() as session:
            async with session.begin():
                query = session.query(cls.model).filter_by(id=student_id)
                result = await session.execute(query)
                student_to_delete = result.scalar_one_or_none()
                if not student_to_delete:
                    return None
                # Удаляем студента
                await session.execute(delete(cls.model).filter_by(id=student_id))
                await session.commit()
                return student_id