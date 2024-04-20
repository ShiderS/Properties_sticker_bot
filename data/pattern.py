import datetime
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from flask_login import UserMixin

from .db_session import SqlAlchemyBase


class Pattern(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = "patterns"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, nullable=False, autoincrement=True)
    id_pattern = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=False)
    for_everyone = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)
    image = sqlalchemy.BLOB(sqlalchemy.BLOB)

