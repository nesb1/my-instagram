import sqlalchemy as sa
import sqlalchemy.orm as so
from final_project.database.database import Base

post_marked_users_association_table = sa.Table(
    'post_marked_users_association',
    Base.metadata,
    sa.Column('post.id', sa.Integer, sa.ForeignKey('user.id')),
    sa.Column('user.id', sa.Integer, sa.ForeignKey('post.id')),
)

post_likes_association_table = sa.Table(
    'post_likes_association',
    Base.metadata,
    sa.Column('post.id', sa.Integer, sa.ForeignKey('user.id')),
    sa.Column('user.id', sa.Integer, sa.ForeignKey('post.id')),
)

post_comments_likes_association_table = sa.Table(
    'post_comments_likes_association',
    Base.metadata,
    sa.Column('comment.id', sa.Integer, sa.ForeignKey('user.id')),
    sa.Column('user.id', sa.Integer, sa.ForeignKey('comment.id')),
)

user_subsriptions = sa.Table(
    'user_subsriptions_association',
    Base.metadata,
    sa.Column('follower_id', sa.Integer, sa.ForeignKey('user.id')),
    sa.Column('followed_id', sa.Integer, sa.ForeignKey('user.id')),
)


class User(Base):
    __tablename__ = 'user'
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    username = sa.Column(sa.String, unique=True)
    password_hash = sa.Column(sa.String)
    access_token = sa.Column(sa.String)
    refresh_token = sa.Column(sa.String)

    subscriptions = so.relationship(
        'User',
        secondary=user_subsriptions,
        primaryjoin=(user_subsriptions.c.follower_id == id),
        secondaryjoin=(user_subsriptions.c.followed_id == id),
        backref=so.backref('subscribers'),
    )
    posts = so.relationship('Post', back_populates=__tablename__, uselist=True)
    marked_on_posts = so.relationship(
        'Post',
        back_populates='marked_users',
        secondary=post_marked_users_association_table,
    )
    likes = so.relationship(
        'Post', back_populates='likes', secondary=post_likes_association_table
    )
    comments_likes = so.relationship(
        'Comment',
        back_populates='likes',
        secondary=post_comments_likes_association_table,
    )
    comments = so.relationship('Comment', back_populates='user', uselist=True)


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
        User,
        back_populates='marked_on_posts',
        secondary=post_marked_users_association_table,
    )
    comments = so.relationship('Comment', back_populates='post')
    likes = so.relationship(
        User, back_populates='likes', secondary=post_likes_association_table
    )


class Comment(Base):
    __tablename__ = 'comment'
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey(User.id), nullable=False, index=True)
    post_id = sa.Column(sa.Integer, sa.ForeignKey(Post.id), nullable=False, index=True)
    text = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime)

    post = so.relationship(Post, back_populates='comments')
    likes = so.relationship(
        User,
        back_populates='comments_likes',
        secondary=post_comments_likes_association_table,
    )
    user = so.relationship(User, back_populates='comments')
