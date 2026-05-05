import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from datetime import timezone, timedelta

default_tz = timezone(timedelta(hours=3), name="MSK")


class Book(SqlAlchemyBase):
    __tablename__ = "books"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    owner_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    owner = orm.relationship("User")
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(
        sqlalchemy.DateTime, default=datetime.datetime.now(default_tz)
    )

    images = sqlalchemy.orm.relationship("BookImage", back_populates="book")

    likes = orm.relationship("Like", back_populates="book")

    def is_liked_by(self, user):
        return any(like.user_id == user.id for like in self.likes)

    def get_like_users(self):
        return [like.user for like in self.likes]


class BookImage(SqlAlchemyBase):
    __tablename__ = "book_images"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    position = sqlalchemy.Column(sqlalchemy.Integer)  # порядок в списке
    book_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("books.id"))
    book = orm.relationship("Book")
    image = sqlalchemy.Column(sqlalchemy.String)
