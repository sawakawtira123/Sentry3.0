import sqlalchemy
import databases

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:2223404egor@localhost:5432/postgres"
#SQLALCHEMY_DATABASE_URL = "postgresql://postgres:123@localhost:5432/postgres"

database = databases.Database(SQLALCHEMY_DATABASE_URL)

metadata = sqlalchemy.MetaData()
engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URL)
metadata.create_all(engine)