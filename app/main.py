from fastapi import FastAPI
import os
from app.students.router import router as router_students
from app.majors.router import router as router_majors
from app.users.router import router as router_users

app = FastAPI()


@app.get("/")
def home_page():
    return {"message": "Привет, Хабр!"}


app.include_router(router_users)
app.include_router(router_students)
app.include_router(router_majors)
