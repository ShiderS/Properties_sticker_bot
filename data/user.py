import datetime
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from flask_login import UserMixin

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, nullable=False)
    full_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    tg_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    workload = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    is_developer = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True, default=False)
