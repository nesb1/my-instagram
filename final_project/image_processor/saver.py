import uuid
from pathlib import Path

from final_project.config import image_storage_settings
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


def _get_path(user_id: int, format_: str) -> Path:
    root = _get_project_root()
    grouping_ids = _get_name_for_grouping_id(user_id)
    grouping_ids_dir = _make_dir_if_not_exists(root, grouping_ids)
    id_dir = _make_dir_if_not_exists(grouping_ids_dir, str(user_id))
    format_ = format_.lower()
    return id_dir / f'{(uuid.uuid4())}.{format_}'


def save_image(user_id: int, image: Image) -> Path:
    '''
    Сохраняет изображение в хранилище
    :return: Путь к изображению
    '''
    path = _get_path(user_id, image.format)
    image.save(path)
    return path
