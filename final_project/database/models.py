import sqlalchemy as sa
import sqlalchemy.orm as so
from final_project.database.database import Base


class User(Base):
    __tablename__ = 'user'
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    username = sa.Column(sa.String, unique=True)
    password_hash = sa.Column(sa.String)
    access_token = sa.Column(sa.String)
    refresh_token = sa.Column(sa.String)

    posts = so.relationship('Post', back_populates=__tablename__)


class Post(Base):
    __tablename__ = 'posts'
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey(User.id), nullable=False, index=True)
    image_path = sa.Column(sa.String)

    user = so.relationship(User, back_populates=__tablename__, uselist=True)
