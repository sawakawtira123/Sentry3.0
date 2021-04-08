import sqlalchemy as db
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import datetime

from sentry.db import metadata

Base = declarative_base()

error = db.Table(
    'error',
    metadata,
    db.Column('id_error', db.Integer, primary_key=True, index=True),
    db.Column('project_id', db.String, ForeignKey('project.project_id')),
    db.Column('date_time', db.DateTime),

    db.Column('name_py', db.String),
    db.Column('type_error', db.String),
    db.Column('description', db.String),
    db.Column('code_of_line', db.Integer),
    db.Column('program_code', db.String),

    db.Column('name_function', db.String),
    db.Column('args', db.String),
    db.Column('kwargs', db.String),
    db.Column('traceback', db.String)
)

project = db.Table(
    'project',
    metadata,
    db.Column('project_id', db.String, primary_key=True),
    db.Column('name', db.String, nullable=False),
    db.Column('count_error', db.Integer),
    db.Column('count_transaction', db.Integer),
    db.Column('user_id', db.Integer, ForeignKey('users.id'))
)

users_table = db.Table(
    "users",
    metadata,
    db.Column("id", db.Integer, primary_key=True),
    db.Column("email", db.String(40), unique=True, index=True),
    db.Column("name", db.String(100)),
    db.Column("hashed_password", db.String()),
    db.Column(
        "is_active",
        db.Boolean(),
        server_default=db.sql.expression.true(),
        nullable=False,
    ),
    db.Column("createdAt", db.DateTime, default=datetime.datetime.now()),
    db.Column("updatedAt", db.DateTime, default=datetime.datetime.now()),
    db.Column("image", db.BLOB),
)

tokens_table = db.Table(
    "tokens",
    metadata,
    db.Column("id", db.Integer, primary_key=True),
    db.Column(
        "token",
        UUID(as_uuid=False),
        server_default=db.text("uuid_generate_v4()"),
        unique=True,
        nullable=False,
        index=True,
    ),
    db.Column("expires", db.DateTime()),
    db.Column("user_id", db.ForeignKey("users.id")),
)

