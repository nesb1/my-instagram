import sqlalchemy as sa
from final_project.database.database import Base


class User(Base):
    __tablename__ = 'users'
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    username = sa.Column(sa.String, unique=True)
    password_hash = sa.Column(sa.String)
