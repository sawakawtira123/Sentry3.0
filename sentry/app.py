from typing import List, Dict, Any, AnyStr, Union
from fastapi import FastAPI, Response, HTTPException, BackgroundTasks
from sentry.schemas.error_schemas import ProjectSchema, ErrorSchema, ProjectCreate, ProjectUpdate
from sentry.db import database, metadata, engine
from sentry.models.models import error, project
from sentry import parse_error
from sentry.service import user_service
from sentry.service.project_service import create_project
from sentry.schemas.user_schemas import User, UserCreate
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sentry.utils.dependecies import get_current_user
import json
import pickle

from sentry.celery_worker import receiving_errors

app = FastAPI()

app.add_middleware(CORSMiddleware,
                   allow_origins=['*'],
                   allow_credentials=True,
                   allow_methods=['*'],
                   allow_headers=['*'])

JSONObject = Dict[AnyStr, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject]


@app.on_event('startup')
async def startup():
    await database.connect()


@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()


# получить все проекты и создать базу (если надо) !
@app.get("/api/v1/project/", response_model=List[ProjectSchema])
async def get_project(current_user: User = Depends(get_current_user)):
    metadata.create_all(engine)  # создание базы
    projects = project.select().where(current_user['id'] == project.c.user_id)
    return await database.fetch_all(query=projects)


# получить один проект !
@app.get("/api/v1/project/{project_id}", response_model=ProjectSchema)
async def get_project(project_id: str, current_user: User = Depends(get_current_user)):
    projects = project.select().where(current_user['id'] == project.c.user_id and project_id == project.c.project_id)
    return await database.fetch_all(query=projects)


# создание проекта !
@app.post("/api/v1/project/")
async def add_project(new_project: ProjectCreate, current_user: User = Depends(get_current_user)):
    return await create_project(new_project, current_user)


# удаление проекта и его ошибок !
@app.delete('/api/v1/project/{_project_id}')
async def delete_project(_project_id: str, current_user: User = Depends(get_current_user)):
    query = error.delete().where(error.c.project_id == _project_id)
    second_query = project.delete().where(project.c.project_id == _project_id and
                                          current_user['id'] == project.user_id)
    await database.fetch_all(query=query)
    await database.fetch_one(query=second_query)
    return Response(content="Успешно удалено", status_code=203)


# Обновить имя проекта !
@app.put("/api/v1/project/{project_id}")
async def update_project(project_id: str, new_project: ProjectUpdate, current_user: User = Depends(get_current_user)):
    query = f"UPDATE public.project SET name = '{new_project.name}' WHERE (project_id = '{project_id}' AND user_id = {current_user['id']});"
    await database.execute(query=query)
    return new_project


# получить ошибки проекта !
@app.get("/api/v1/errors/{_project_id}", response_model=List[ErrorSchema])
async def get_error(_project_id: str):
    errors = error.select().where(_project_id == error.c.project_id)
    return await database.fetch_all(query=errors)


# получение ошибки по id !
@app.get('/api/v1/errors/{_project_id}/{_id_error}')
async def get_error(_id_error: int, _project_id: str):
    get_errors = error.select().where(error.c.id_error == _id_error and _project_id == error.c.project_id)
    return await database.fetch_all(query=get_errors)


# удаление одной ошибки !
@app.delete('/api/v1/errors/{_project_id}/{_id_error}')
async def delete_error(_id_error: int, _project_id: str):
    query = error.delete().where(error.c.id_error == _id_error and _project_id == error.c.project_id)
    await database.fetch_one(query=query)
    return Response(content="Успешно удалено", status_code=204)


# регистрация пользователя
@app.post("/sign-up")
async def create_user(user: UserCreate):
    db_user = await user_service.get_user_by_email(email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await user_service.create_user(user=user)


# авторизация
@app.post("/auth")
async def auth(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await user_service.get_user_by_email(email=form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user_service.validate_password(
            password=form_data.password, hashed_password=user["hashed_password"]
    ):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    user_token = await user_service.create_user_token(user_id=user['id'])
    token_base = {
        "user_id": user['id'],
        "username": form_data.username,
        "token_type": "Bearer",
        "email": user['email'],
        "user_token": user_token
    }
    return token_base


# получить информацию о пользователе
@app.get("/api/v1/user/")
async def get_user_info(current_user: User = Depends(get_current_user)):
    user_id = current_user['user_id']
    query = f'SELECT us.id, us.email, name, tk.token, tk.expires, us."createdAt", us."updatedAt", us.image FROM public.users us join tokens tk on tk.user_id=us.id where us.id = {user_id} ORDER BY tk.id DESC LIMIT 1'
    token = await database.fetch_one(query=query)
    token_dict = {"token": token["token"], "expires": token["expires"]}
    return {"id": token['id'],
            "email": token['email'],
            "user_token": token_dict,
            "createdAt": token['createdAt'],
            "updatedAt": token['updatedAt'],
            "image": token["image"]}


# получение ошибок из сервисов
@app.post('/api/send/message')
async def get_error_task(my_json: Dict):
    receiving_errors.delay(my_json)
    return {"message": "Поступила ошибка!"}
