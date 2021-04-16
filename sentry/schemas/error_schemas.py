from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ErrorSchema(BaseModel):
    id_error: int
    project_name: Optional[str] = None
    date_time: Optional[datetime] = None
    name_py: Optional[str] = None
    type_error: Optional[str] = None
    description: Optional[str] = None
    code_of_line: Optional[str] = None
    program_code: Optional[str] = None
    name_function: Optional[str] = None
    args: Optional[str] = None
    kwargs: Optional[str] = None
    traceback: Optional[str] = None


class ProjectCreate(BaseModel):
    name: Optional[str] = None
    count_error: Optional[int] = None
    count_transaction: Optional[int] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None


class ProjectSchema(BaseModel):
    project_id: Optional[str] = None
    name: Optional[str] = None
    count_error: Optional[int] = None
    count_transaction: Optional[int] = None
    user_id: Optional[int]


class DeleteErrors(BaseModel):
    error_ids: List


