from http import HTTPStatus
from io import BytesIO
from pathlib import Path
from typing import List

import uvicorn
from fastapi import FastAPI
from final_project.data_access_layer.storage import (
    get_all_user_images,
    get_image,
    save_image,
)
from final_project.models import ImageIn, ImageWithPath
from final_project.utils import decode_base64_to_bytes
from PIL.Image import open as open_image

app = FastAPI()


@app.get('/images', response_model=ImageWithPath)
async def get_image_from_storage(image_path: str) -> ImageWithPath:
    image = get_image(Path(image_path))
    return ImageWithPath(image=image, path=image_path)


@app.get('/user-images/{user_id}', response_model=List[ImageWithPath])
async def get_user_images(user_id: int) -> List[ImageWithPath]:
    return get_all_user_images(user_id)


@app.post('/images', response_model=ImageWithPath, status_code=HTTPStatus.CREATED.value)
async def add_image(image: ImageIn) -> ImageWithPath:
    pillow_image = open_image(BytesIO(decode_base64_to_bytes(image.image)))
    path = save_image(image.user_id, pillow_image)
    return ImageWithPath(path=str(path), image=image.image)


if __name__ == '__main__':
    uvicorn.run(app)
