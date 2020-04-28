from final_project.app_creation import get_app
from final_project.database.database import Base, engine

Base.metadata.create_all(engine)
app = get_app()
