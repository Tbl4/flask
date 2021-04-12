import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Thing(SqlAlchemyBase):
    __tablename__ = 'things'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    fought = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    won = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

