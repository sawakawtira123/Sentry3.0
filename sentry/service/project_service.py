import uuid

from sentry.db import database
from sentry.models.models import project
from sentry.schemas.error_schemas import ProjectCreate


async def create_project(new_project: ProjectCreate, user):
    unique_key = str(uuid.uuid4())
    query = (
        project.insert().values(
            project_id=unique_key,
            name=new_project.name,
            user_id=user["id"],
            count_error=0,
            count_transaction=0
        )
    )
    await database.execute(query)
    return unique_key
