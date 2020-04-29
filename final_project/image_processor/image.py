from io import BytesIO
from pathlib import Path

from final_project.exceptions import MyImageError
from final_project.messages import Message
from final_project.utils import encode_bytes_to_base64
from PIL import UnidentifiedImageError
from PIL.Image import Image
from PIL.Image import open as open_image


class MyImage:
    def __init__(self, image: bytes) -> None:
        try:
            self.image: Image = open_image(BytesIO(image))
        except UnidentifiedImageError:
            raise MyImageError(Message.BYTES_ARE_NOT_A_IMAGE.value)

    @property
    def height(self):
        return self.image.height

    @property
    def width(self):
        return self.image.width

    @staticmethod
    def _increase_proportionally(image: Image, increase_ratio) -> Image:
        width, height = image.width * increase_ratio, image.height * increase_ratio
        return image.resize((width, height))

    @staticmethod
    def _crop_image(image: Image, aspect_resolution: int) -> Image:
        x1, y1, x2, y2 = (
            image.width // 2,
            image.height // 2,
            image.width // 2 + 1,
            image.height // 2 + 1,
        )
        shift = aspect_resolution // 2
        return image.crop((x1 - shift, y1 - shift, x2 + shift, y2 + shift))

    def cut(self, aspect_resolution: int) -> Image:
        '''
        Обрезает изображение до квадратного, так,
        чтобы разрешение стороны соотвествовало aspect_resolution.
        Если image уже квадратное и в заданном разерешении, то возваращет image без изменений
        '''
        width = self.width
        height = self.height
        if width % 2 != 0 or height % 2 != 0:
            raise MyImageError(Message.INVALID_IMAGE.value)
        if height == width == aspect_resolution:
            return self.image
        if height < aspect_resolution or width < aspect_resolution:
            self.image = MyImage._increase_proportionally(
                self.image, aspect_resolution // min(height, width) + 1
            )
        self.image = MyImage._crop_image(self.image, aspect_resolution)
        return self.image

    def save(self, user_id: int) -> Path:
        # делает запрос на сервер
        image = encode_bytes_to_base64(self.image.tobytes())
        # return save_image(user_id, self.image)
