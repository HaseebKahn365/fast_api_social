import databases

import sqlalchemy
from config import config

metadata = sqlalchemy.MetaData()


post_table = sqlalchemy.Table(
    "posts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String, nullable=False),
)

user_table = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.String, nullable=False, unique=True),
    sqlalchemy.Column("email", sqlalchemy.String, nullable=False, unique=True),
)
comment_table = sqlalchemy.Table(
    "comments",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("post_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("posts.id"), nullable=False),
    sqlalchemy.Column("content", sqlalchemy.String, nullable=False),
)

# SQLAlchemy sync engine for running DDL (create_all) synchronously.
# If using an async driver like aiosqlite we convert the URL to the sync sqlite URL
# so SQLAlchemy can open a normal DBAPI connection for table creation.
sync_db_url = config.DATABASE_URL
if sync_db_url and sync_db_url.startswith("sqlite+aiosqlite://"):
    # convert 'sqlite+aiosqlite:///./test.db' -> 'sqlite:///./test.db'
    sync_db_url = sync_db_url.replace("+aiosqlite", "")

engine = sqlalchemy.create_engine(
    sync_db_url,
    connect_args={"check_same_thread": False} if "sqlite" in sync_db_url else {},
)

# Create tables synchronously on startup/import (safe now with sync engine)
metadata.create_all(engine)

# Async Database instance used by the app
database = databases.Database(config.DATABASE_URL, force_rollback=config.BD_FORCE_ROLLBACK)