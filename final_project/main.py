from fastapi import FastAPI
from final_project.api import auth, users
from final_project.database.database import Base

Base.metadata.create_all()
app = FastAPI()
app.include_router(users.router, prefix='/users')
app.include_router(auth.router, prefix='/auth')
