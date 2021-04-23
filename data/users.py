import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm

from time import time
import jwt


from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    is_admin = sqlalchemy.Column(sqlalchemy.BOOLEAN, default=False)

    # def __repr__(self):
    #     return f'{self.id} {self.email} {self.name} {self.is_admin}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            'sc*FzSPF72itHTt&Cj3bPMAe&4bRxGoH', algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, 'sc*FzSPF72itHTt&Cj3bPMAe&4bRxGoH',
                            algorithms=['HS256'])['reset_password']
            return id
        except:
            return