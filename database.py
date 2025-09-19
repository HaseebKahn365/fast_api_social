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

comment_table = sqlalchemy.Table(
    "comments",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("post_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("posts.id"), nullable=False),
    sqlalchemy.Column("content", sqlalchemy.String, nullable=False),
)

engine = sqlalchemy.create_engine(config.DATABASE_URL,
                                   connect_args={"check_same_thread": False} if "sqlite" in config.DATABASE_URL else {})

metadata.create_all(engine)
database = databases.Database(config.DATABASE_URL, force_rollback=config.BD_FORCE_ROLLBACK)