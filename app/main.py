from fastapi import FastAPI
from utils import json_to_dict_list
import os
from typing import Optional
import requests

from app.students.router import router as router_students

script_dir = os.path.dirname(os.path.abspath(__file__))

parent_dir = os.path.dirname(script_dir)

path_to_json = os.path.join(parent_dir, "students.json")

app = FastAPI()



@app.get("/")
def home_page():
    return {"message": "Привет, Хабр!"}


app.include_router(router_students)

#
# @app.get("/students")
# def get_all_students():
#     return json_to_dict_list(path_to_json)
#
#
# @app.get("/students/{course}")
# def get_all_students_course(course: int, major: Optional[str] = None, enrollment_year: Optional[int] = 2018):
#     students = json_to_dict_list(path_to_json)
#     filtered_students = []
#     for student in students:
#         if student["course"] == course:
#             filtered_students.append(student)
#
#     if major:
#         filtered_students = [student for student in filtered_students if student['major'].lower() == major.lower()]
#
#     if enrollment_year:
#         filtered_students = [student for student in filtered_students if student['enrollment_year'] == enrollment_year]
#
#     return filtered_students
#
#
# @app.get("/students/")
# def get_all_students(course: Optional[int] = None):
#     students = json_to_dict_list(path_to_json)
#     if course is None:
#         return students
#     else:
#         return_list = []
#         for student in students:
#             if student["course"] == course:
#                 return_list.append(student)
#             return return_list
#
#
# @app.get("/students/{students_id}")
# def get_students_id(students_id: int, course: Optional[int] = None):
#     students = json_to_dict_list(path_to_json)
#     if course is None:
#         return students
#     else:
#         for student in students:
#             if student["student_id"] == students_id:
#                 return students_id
#             else:
#                 print(f'Пользователь с данным {students_id} не найден!')
#
#
# def get_student_id(students_id: int):
#     url = f"http://127.0.0.1:8000/students/{students_id}"
#     response = requests.get(url)
#     return response.json()
