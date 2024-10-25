from app.majors.models import Major
from app.dao.base import BaseDao


class MajorsDAO(BaseDao):
    model = Major