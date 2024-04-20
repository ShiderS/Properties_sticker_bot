import datetime

from data.db_session import SqlAlchemyBase

from flask_login import UserMixin

import sqlalchemy

from sqlalchemy_serializer import SerializerMixin


__all__ = []


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, nullable=False)
    full_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    tg_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    id_call_admin = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    is_relax = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True, default=False)
    workload = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    is_developer = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True, default=False)
