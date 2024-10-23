from sqlalchemy import select
from app.students.models import Student
from app.dao.base import BaseDao


class StudentDAO(BaseDao):
    model = Student

