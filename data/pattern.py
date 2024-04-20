import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from flask_login import UserMixin

from .db_session import SqlAlchemyBase


class Pattern(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = "patterns"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, nullable=False, autoincrement=True)
    pattern_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=False)
    for_everyone = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    image_id = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    is_public = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)
