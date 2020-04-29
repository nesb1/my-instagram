import uvicorn
from final_project.api.storage import app


def start_storage_app():
    uvicorn.run(app, host='0.0.0.0', port=8001)
