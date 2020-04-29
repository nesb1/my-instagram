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
from final_project.models import Image, ImageIn, ImagePath, ImageWithPath, Base64
from final_project.utils import decode_base64_to_bytes, encode_bytes_to_base64
from PIL.Image import open
from starlette.responses import JSONResponse

app = FastAPI()


@app.get('/images', response_model=Image)
async def get_image_from_storage(image_path: str) -> Any:
    try:
        image = get_image(Path(image_path))
        print(image_path)
        return Image(image=image)
    except StorageDALNotExistsError as e:
        return JSONResponse({'message': str(e)}, HTTPStatus.NOT_FOUND.value)


@app.get('/user-images/', response_model=List[Image])
async def get_user_images(user_id: int) -> Any:
    try:
        res = get_all_user_images(user_id)
        return res
    except StorageDALNotExistsError as e:
        return JSONResponse({'message': str(e)}, HTTPStatus.NOT_FOUND.value)


@app.post('/images', response_model=ImagePath, status_code=HTTPStatus.CREATED.value)
async def add_image(image: ImageIn) -> Any:
    try:
        print(type(image.image))
        print(image.image)
        pillow_image = open(BytesIO(decode_base64_to_bytes(image.image)))
        path = save_image(image.user_id, pillow_image)
        return ImageWithPath(path=str(path), image=image.image)
    except PIL.UnidentifiedImageError:
        return JSONResponse(
            Message.BYTES_ARE_NOT_A_IMAGE.value,
            status_code=HTTPStatus.BAD_REQUEST.value,
        )

if __name__ == '__main__':
    uvicorn.run(app)

# from PIL.Image import Image as Img
# # if __name__ == '__main__':
# #     uvicorn.run(app)
# b= 'iVBORw0KGgoAAAANSUhEUgAAAZAAAAGQCAMAAAC3Ycb+AAAAOVBMVEUAAAD///9nfYQLlBQPzRsS7CATIiQfOTwgpewhCuxbW1tnfYNnfYSTFRWZZkTE2N7uIiLuu5n/////ozKDAAAAA3RSTlMAAP6gcxvFAAAEhUlEQVR42u3dy3LaQBBAURwsYydxMPz/x2bbm67qrhkJgc5d68UcVl16nN60q06WAIiAABEQIAJyIJDTk/Qxqb39LiBAgAABAgQIECBAgAABAgQIECDPC5It5DKpveEAAQIECBAgQIAAAQIECBAgQIAA2T/IyMKfk+5JcZu94QABAgQIECBAgAABAgQIECBAgADZJ8isha8gVHBij8IBAgQIECBAgAABAgQIECBAgAABsh+QCkJlkdbuMMNFIECAAAECBAgQIECAAAECBAgQIG2QCkJ2g9saHX64CAQIECBAgAABAgQIECBAgAABAiTF2XNAgAABAgQIECBAgAABAgQIECBAjgkSf+i/0C2ULcwtKT7EWdk+blPZd0scIECAAAECBAgQIECAAAECBAgQIM8LcisEBAgQIECAAAECBAgQIECAAAECBMiWIBlOFyTW3T67NiBAgAABAgQIECBAgAABAgQIECDHBMlwKkPHyrBw1r6ewgUCBAgQIECAAAECBAgQIECAAAHSHTpWFrICW+lRCECAAAECBAgQIECAAAECBAgQIECeC2RtnD2/gB8IECBAgAABAgQIECBAgAABAgTIa4CsjWO4CAQIECBAgAABAgQIECBAgAABAuRRIN2AAAECBAgQIECAAAECBAgQIECAABlBOIfWwMkQlpAXmAEBAgQIECBAgAABAgQIECBAgADJEJakWS8nq7y0DAgQIECAAAECBAgQIECAAAECBAiQyhBxaXYvVHnos3KuLXGAAAECBAgQIECAAAECBAgQIECAvAbINVQBORfKrqeCDAQIECBAgAABAgQIECBAgAABAuT1QLLBXhck7ntNyo5fAemCr4EDBAgQIECAAAECBAgQIECAAAECZHuQeLGVDz92Fy/rK/Qx0LXQe2gWDhAgQIAAAQIECBAgQIAAAQIECJB9gnQXL27/Wah7/GyBK/0KjeAAAQIECBAgQIAAAQIECBAgQIAAWQ+ke+FfA1UQ4rl+CmXXWdk3nvcSqqwDECBAgAABAgQIECBAgAABAgQIkG1A4oH/FOqCfDbLFvK7ULZglX0z2EuhDAcIECBAgAABAgQIECBAgAABAgTIXJDLQBWckZvgvgcawcn2/Vsobg8ECBAgQIAAAQIECBAgQIAAAQJkPZDfoe7NYl2cbJvuubYE6f5JgQABAgQIECBAgAABAgQIECBAgMwFyRC6INlHGis303V/dHZtcVErH6usbDMSECBAgAABAgQIECBAgAABAgQIkPVA4kWNDBcznMrQLl5P5ca0uG+8/mxYWBkuzsIBAgQIECBAgAABAgQIECBAgAABMhckHiAuRvfk2THvSdl5KzfuVYaLsx4S7X6sYOob5YAAAQIECBAgQIAAAQIECBAgQIBM+7DkrGNmA8LugLOLsBQ6DQQECBAgQIAAAQIECBAgQIAAAQJkPZBHNWvAuTSb9acDAgQIECBAgAABAgQIECBAgAABchyQWQPONYajQIAAAQIECBAgQIAAAQIECBAgQLYB0T4CAkRAgAgIEAE5QP8BIf/W56gS3cAAAAAASUVORK5CYII='
# image = open(BytesIO(decode_base64_to_bytes(b)))
# image.show()
# image = encode_bytes_to_base64(image.tobytes())
# a = 'iVBORw0KGgoAAAANSUhEUgAAAZAAAAGQCAMAAAC3Ycb+AAAAOVBMVEUAAAD///9nfYQLlBQPzRsS7CATIiQfOTwgpewhCuxbW1tnfYNnfYSTFRWZZkTE2N7uIiLuu5n/////ozKDAAAAA3RSTlMAAP6gcxvFAAAEhUlEQVR42u3dy3LaQBBAURwsYydxMPz/x2bbm67qrhkJgc5d68UcVl16nN60q06WAIiAABEQIAJyIJDTk/Qxqb39LiBAgAABAgQIECBAgAABAgQIECDPC5It5DKpveEAAQIECBAgQIAAAQIECBAgQIAA2T/IyMKfk+5JcZu94QABAgQIECBAgAABAgQIECBAgADZJ8isha8gVHBij8IBAgQIECBAgAABAgQIECBAgAABsh+QCkJlkdbuMMNFIECAAAECBAgQIECAAAECBAgQIG2QCkJ2g9saHX64CAQIECBAgAABAgQIECBAgAABAiTF2XNAgAABAgQIECBAgAABAgQIECBAjgkSf+i/0C2ULcwtKT7EWdk+blPZd0scIECAAAECBAgQIECAAAECBAgQIM8LcisEBAgQIECAAAECBAgQIECAAAECBMiWIBlOFyTW3T67NiBAgAABAgQIECBAgAABAgQIECDHBMlwKkPHyrBw1r6ewgUCBAgQIECAAAECBAgQIECAAAHSHTpWFrICW+lRCECAAAECBAgQIECAAAECBAgQIECeC2RtnD2/gB8IECBAgAABAgQIECBAgAABAgTIa4CsjWO4CAQIECBAgAABAgQIECBAgAABAuRRIN2AAAECBAgQIECAAAECBAgQIECAABlBOIfWwMkQlpAXmAEBAgQIECBAgAABAgQIECBAgADJEJakWS8nq7y0DAgQIECAAAECBAgQIECAAAECBAiQyhBxaXYvVHnos3KuLXGAAAECBAgQIECAAAECBAgQIECAvAbINVQBORfKrqeCDAQIECBAgAABAgQIECBAgAABAuT1QLLBXhck7ntNyo5fAemCr4EDBAgQIECAAAECBAgQIECAAAECZHuQeLGVDz92Fy/rK/Qx0LXQe2gWDhAgQIAAAQIECBAgQIAAAQIECJB9gnQXL27/Wah7/GyBK/0KjeAAAQIECBAgQIAAAQIECBAgQIAAWQ+ke+FfA1UQ4rl+CmXXWdk3nvcSqqwDECBAgAABAgQIECBAgAABAgQIkG1A4oH/FOqCfDbLFvK7ULZglX0z2EuhDAcIECBAgAABAgQIECBAgAABAgTIXJDLQBWckZvgvgcawcn2/Vsobg8ECBAgQIAAAQIECBAgQIAAAQJkPZDfoe7NYl2cbJvuubYE6f5JgQABAgQIECBAgAABAgQIECBAgMwFyRC6INlHGis303V/dHZtcVErH6usbDMSECBAgAABAgQIECBAgAABAgQIkPVA4kWNDBcznMrQLl5P5ca0uG+8/mxYWBkuzsIBAgQIECBAgAABAgQIECBAgAABMhckHiAuRvfk2THvSdl5KzfuVYaLsx4S7X6sYOob5YAAAQIECBAgQIAAAQIECBAgQIBM+7DkrGNmA8LugLOLsBQ6DQQECBAgQIAAAQIECBAgQIAAAQJkPZBHNWvAuTSb9acDAgQIECBAgAABAgQIECBAgAABchyQWQPONYajQIAAAQIECBAgQIAAAQIECBAgQLYB0T4CAkRAgAgIEAE5QP8BIf/W56gS3cAAAAAASUVORK5CYII='
# image: Img = open(BytesIO(decode_base64_to_bytes(image)))
# image.save(Path())
