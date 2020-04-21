import uvicorn
from fastapi import FastAPI
from final_project.api import auth, users
from final_project.database.database import Base


def get_app() -> FastAPI:
    Base.metadata.create_all()
    _app = FastAPI()
    _app.include_router(users.router, prefix='/users')
    _app.include_router(auth.router, prefix='/auth')
    return _app


app = get_app()
if __name__ == '__main__':
    uvicorn.run(app)
