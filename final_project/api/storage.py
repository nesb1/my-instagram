from http import HTTPStatus
from io import BytesIO
from pathlib import Path
from typing import Any, List

import PIL
import uvicorn
from fastapi import FastAPI
from final_project.data_access_layer.storage import (
    get_all_user_images,
    get_image,
    save_image,
)
from final_project.exceptions import StorageDALNotExistsError
from final_project.messages import Message
from final_project.models import ImageIn, ImagePath, ImageWithPath
from final_project.utils import decode_base64_to_bytes
from PIL.Image import open as open_image
from starlette.responses import JSONResponse

app = FastAPI()


@app.get('/images', response_model=ImageWithPath)
async def get_image_from_storage(image_path: str) -> Any:
    try:
        image = get_image(Path(image_path))
        return ImageWithPath(image=image, path=image_path)
    except StorageDALNotExistsError as e:
        return JSONResponse({'message': str(e)}, HTTPStatus.NOT_FOUND.value)


@app.get('/user-images/{user_id}', response_model=List[ImageWithPath])
async def get_user_images(user_id: int) -> Any:
    try:
        res = get_all_user_images(user_id)
        return res
    except StorageDALNotExistsError as e:
        return JSONResponse({'message': str(e)}, HTTPStatus.NOT_FOUND.value)


@app.post('/images', response_model=ImagePath, status_code=HTTPStatus.CREATED.value)
async def add_image(image: ImageIn) -> Any:
    try:
        pillow_image = open_image(BytesIO(decode_base64_to_bytes(image.image)))
        path = save_image(image.user_id, pillow_image)
        return ImageWithPath(path=str(path), image=image.image)
    except PIL.UnidentifiedImageError:
        return JSONResponse(
            Message.BYTES_ARE_NOT_A_IMAGE.value,
            status_code=HTTPStatus.BAD_REQUEST.value,
        )


if __name__ == '__main__':
    uvicorn.run(app)
