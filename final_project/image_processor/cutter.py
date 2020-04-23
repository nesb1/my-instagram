from final_project.messages import Message
from PIL.Image import Image


def _increase_proportionally(image: Image, increase_ratio) -> Image:
    width, height = image.width * increase_ratio, image.height * increase_ratio
    return image.resize((width, height))


def _crop_image(image: Image, aspect_resolution: int) -> Image:
    x1, y1, x2, y2 = (
        image.width // 2,
        image.height // 2,
        image.width // 2 + 1,
        image.height // 2 + 1,
    )
    shift = aspect_resolution // 2
    return image.crop((x1 - shift, y1 - shift, x2 + shift, y2 + shift))


def cut(image: Image, aspect_resolution: int) -> Image:
    '''
    Обрезает изображение до квадратного, так,
    чтобы разрешение стороны соотвествовало aspect_resolution.
    Если image уже квадратное и в заданном разерешении, то возваращет image без изменений
    '''
    height = image.height
    width = image.width
    if width % 2 != 0 or height % 2 != 0:
        raise ValueError(Message.INVALID_IMAGE.value)
    if height == width == aspect_resolution:
        return image
    if height < aspect_resolution or width < aspect_resolution:
        image = _increase_proportionally(
            image, aspect_resolution // min(height, width) + 1
        )
    return _crop_image(image, aspect_resolution)
