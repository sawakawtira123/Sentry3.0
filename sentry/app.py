from typing import List, Dict, Any, AnyStr, Union
from fastapi import FastAPI, Response, HTTPException

from sentry.schemas.error_schemas import ProjectSchema, ErrorSchema, ProjectCreate
from sentry.db import database, metadata, engine
from sentry.models.models import error, project
from sentry import parse_error
from sentry.service import user_service
from sentry.service.project_service import create_project
from sentry.schemas.user_schemas import User, UserCreate, TokenBase, UserBase
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from sentry.utils.dependecies import get_current_user

redis_broker = RedisBroker
app = FastAPI()
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
    # metadata.create_all(engine) # создание базы
    projects = project.select().where(current_user['id'] == project.c.user_id)
    return await database.fetch_all(query=projects)


# создание проекта !
@app.post("/api/v1/project/")
async def add_project(new_project: ProjectCreate, current_user: User = Depends(get_current_user)):
    return await create_project(new_project, current_user)


# удаление проекта и его ошибок TODO сделать одним запросом !
@app.delete('/api/v1/project/{_project_id}')
async def delete_project(_project_id: str, current_user: User = Depends(get_current_user)):
    query = error.delete().where(error.c.project_id == _project_id)
    second_query = project.delete().where(project.c.project_id == _project_id and
                                          current_user['id'] == project.user_id)
    await database.execute(query=query)
    await database.execute(query=second_query)
    return None


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
    await database.execute(query=query)
    return None


# получение ошибки из сервиса
@app.post('/api/send/message')
async def receiving_errors(arbitrary_json: JSONStructure = None):
    data = arbitrary_json
    project_id = None
    if data[b'project_id'] == '':
        print(data[b'project_id'] + 'Введите ключ проекта')
    else:
        project_id = data[b'project_id']
    args = '{}'
    kwargs = '{}'
    name_function = ''
    message = data[b'message']
    if data[b'exist'] == 1:
        pass
    else:
        name_function = data[b'name_function']  # Можно тут заменить """"""""
        args = data[b'args']
        kwargs = data[b'kwargs']
    data_error = parse_error.parsing(message)
    data_program_code = parse_error.parse_code(data[b'script_code'], data_error['line_error'])
    print(f'ID ПРОЕКТА: {project_id}')
    try:
        query = error.insert().values(project_id=project_id,
                                      date_time=data_error['date_error'],
                                      type_error=data_error['type_error'],
                                      name_py=data_error['name_of_py'],
                                      code_of_line=data_error['line_error'],
                                      program_code=data_program_code,
                                      description=data_error['description'],
                                      name_function=name_function,
                                      args=args,
                                      kwargs=kwargs,
                                      traceback=data_error['traceback'])
        last_error = await database.execute(query)
        counter_error = f"UPDATE public.project SET count_error = count_error+1 WHERE project_id = '{project_id}';"
        await database.execute(counter_error)
        return last_error
    except Exception as ex:
        print(f'{ex} project id not found')
        return Response(content=f'"exception": {project_id}', status_code=404)


# регистрация пользователя
@app.post("/sign-up", response_model=User)
async def create_user(user: UserCreate):
    db_user = await user_service.get_user_by_email(email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await user_service.create_user(user=user)


# авторизация
@app.post("/auth", response_model=TokenBase)
async def auth(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await user_service.get_user_by_email(email=form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not user_service.validate_password(
            password=form_data.password, hashed_password=user["hashed_password"]
    ):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    return await user_service.create_user_token(user_id=user['id'])


# рут только для активного пользователя
@app.get("/users/me", response_model=UserBase)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user





