import uuid
from http import HTTPStatus
from pathlib import Path
from typing import List

from final_project.config import image_storage_settings
from final_project.exceptions import DALError
from final_project.messages import Message
from final_project.models import Base64, ImageWithPath
from final_project.utils import encode_bytes_to_base64
from PIL.Image import Image


def _get_project_root() -> Path:
    root: Path = Path(
        __file__
    ).resolve().parent.parent.parent / image_storage_settings.storage_folder_name
    if not root.exists():
        root.mkdir()
    return root


def _get_name_for_grouping_id(user_id: int) -> str:
    if user_id <= 0:
        raise ValueError()
    items_count = image_storage_settings.items_in_one_folder
    if user_id <= items_count:
        return f'1-{items_count}'
    start: int = (user_id - 1) // items_count * items_count
    finish: int = start + items_count
    return f'{start + 1}-{finish}'


def _make_dir_if_not_exists(dir_path: Path, sub_dir_name: str) -> Path:
    res = dir_path / sub_dir_name
    if not res.exists():
        res.mkdir()
    return res


def _get_path(user_id: int) -> Path:
    root = _get_project_root()
    grouping_ids = _get_name_for_grouping_id(user_id)
    grouping_ids_dir = _make_dir_if_not_exists(root, grouping_ids)
    id_dir = _make_dir_if_not_exists(grouping_ids_dir, str(user_id))
    return id_dir / f'{(uuid.uuid4())}.png'


def save_image(user_id: int, image: Image) -> Path:
    '''
        Сохраняет изображение в хранилище
        :return: Путь к изображению
        '''
    path = _get_path(user_id)
    image.save(path, format='png')
    return path


def get_image(image_path: Path) -> Base64:
    if not image_path.exists():
        raise DALError(
            HTTPStatus.NOT_FOUND.value, Message.IMAGE_DOES_NOT_EXISTS_ON_STORAGE.value
        )
    with image_path.open('rb') as f:
        image_bytes = f.read()
        return encode_bytes_to_base64(image_bytes)


def _get_all_images_from_folder(path: Path) -> List[ImageWithPath]:
    res = []
    for img in path.iterdir():
        with img.open('rb') as f:
            res.append(
                ImageWithPath(path=str(img), image=encode_bytes_to_base64(f.read()))
            )
    return res


def get_all_user_images(user_id: int) -> List[ImageWithPath]:
    users_folder = _get_project_root() / _get_name_for_grouping_id(user_id)
    user_folder = users_folder / str(user_id)
    if not user_folder.exists():
        raise DALError(
            HTTPStatus.NOT_FOUND.value, Message.USER_DOES_NOT_HAVE_IMAGES.value
        )
    return _get_all_images_from_folder(user_folder)
