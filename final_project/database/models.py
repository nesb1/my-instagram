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

    posts = so.relationship('Post', back_populates=__tablename__, uselist=True)
    marked_users = so.relationship('MarkedUser', back_populates=__tablename__)


class Post(Base):
    __tablename__ = 'post'
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey(User.id), nullable=False, index=True)
    image_path = sa.Column(sa.String)
    description = sa.Column(sa.String)
    location = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime)

    user = so.relationship(User, back_populates='posts')
    marked_users = so.relationship(
        'MarkedUser', back_populates=__tablename__, uselist=True
    )


class MarkedUser(Base):
    __tablename__ = 'marked_user'
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey(User.id), nullable=False, index=True)
    post_id = sa.Column(sa.Integer, sa.ForeignKey(Post.id), nullable=False, index=True)

    user = so.relationship(User, back_populates='marked_users')
    post = so.relationship(Post, back_populates='marked_users')
