from celery import Celery
from celery.utils.log import get_task_logger
from sentry import parse_error
from typing import List, Dict, Any, AnyStr, Union
import psycopg2
import json

celery = Celery('tasks',
                backend="redis://localhost:6379/0",
                broker="redis://localhost:6379/0",
                accept_content=['json'],
                task_serializer='json',
                result_serializer='json'
                )

celery_log = get_task_logger(__name__)


JSONObject = Dict[AnyStr, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject]


@celery.task
def receiving_errors(arbitrary_json):
    # conn.autocommit = True
    conn = psycopg2.connect(dbname='postgres', user='postgres',
                            password='123', host='localhost')
    cursor = conn.cursor()
    data = arbitrary_json
    project_id = None
    if data['project_id'] == '':
        print(data['project_id'] + 'Введите ключ проекта')
    else:
        project_id = data['project_id']
    args = '{}'
    kwargs = '{}'
    name_function = ''
    message = data['message']
    if data['exist'] == 1:
        pass
    else:
        name_function = data['name_function']
        args = data['args']
        kwargs = data['kwargs']
    data_error = parse_error.parsing(message)
    data_program_code = parse_error.parse_code(data['script_code'], data_error['line_error'])
    print(f'ID ПРОЕКТА: {project_id}')
    try:
        cursor.execute("insert into error"
                       "(project_id, date_time, name_py, type_error, description, code_of_line, program_code,"
                       "name_function, args, kwargs, traceback) "
                       "values(%s ,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                   (project_id, str(data_error["date_error"]),
                    data_error["name_of_py"], data_error["type_error"],
                    data_error["description"], data_error["line_error"],
                    json.dumps(data_program_code), name_function, args, kwargs, data_error["traceback"]))
        conn.commit()
        counter_error = f"UPDATE public.project SET count_error = count_error+1 WHERE project_id = '{project_id}';"
        cursor.execute(query=counter_error)
        conn.commit()
        celery_log.info(f"Ошибка успешно обработана!")
        cursor.close()
        conn.close()
        return {"message": f"Ошибка занесена в базу", "Ошибка": "месаге"}
    except Exception as ex:
        print(f'{ex} project id not found')


