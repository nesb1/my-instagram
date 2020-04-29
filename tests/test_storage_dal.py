import pathlib

import pytest
from final_project.config import image_storage_settings
from final_project.data_access_layer.storage import (
    get_all_user_images,
    get_image,
    save_image,
)
from final_project.exceptions import StorageDALNotExistsError
from final_project.utils import rmtree
from PIL.Image import Image


@pytest.fixture()
def proj_root():
    return pathlib.Path(__file__).resolve().parent.parent


@pytest.fixture(autouse=True)
def _delete_image_directory(proj_root: pathlib.Path):
    yield
    directory = proj_root / image_storage_settings.storage_folder_name
    if directory.exists():
        rmtree(directory)


@pytest.fixture()
def _mock_image_save(mocker):
    mocker.patch.object(Image, 'save')


@pytest.mark.usefixtures('_mock_image_save')
@pytest.mark.parametrize('image', ['1x1.png'], indirect=True)
def test_save_image_raises_error_if_user_id_is_zero(image):
    with pytest.raises(ValueError):
        save_image(0, image)


@pytest.mark.usefixtures('_mock_image_save')
@pytest.mark.parametrize(
    ('user_id', 'expected_path_part', 'image'),
    [
        (1, '1-1000', '1x1.png'),
        (1000, '1-1000', '1x1.png'),
        (50, '1-1000', '1x1.png'),
        (1001, '1001-2000', '1x1.png'),
        (2000, '1001-2000', '1x1.png'),
        (1500, '1001-2000', '1x1.png'),
    ],
    indirect=['image'],
)
def test_save_image_return_expected_path(user_id, expected_path_part, image):
    path = save_image(user_id, image)
    assert f'{expected_path_part}/{user_id}' in str(path)


@pytest.mark.parametrize('image', ['1x1.png'], indirect=True)
def test_save_image(image):
    path = save_image(1, image)
    assert path.exists()


def test_get_image_from_storage_with_not_exists_path_raises_error():
    with pytest.raises(StorageDALNotExistsError):
        get_image(pathlib.Path('12343'))


@pytest.fixture()
def save_image_fixture(image_2x2):
    return save_image(1, image_2x2)


@pytest.fixture()
def _save_two_images(image_2x2, image_1x1):
    save_image(1, image_1x1)
    save_image(1, image_2x2)


def test_get_image_from_storage(save_image_fixture):
    assert get_image(save_image_fixture)


def test_get_all_users_images_when_main_folder_does_not_exists():
    with pytest.raises(StorageDALNotExistsError):
        get_all_user_images(1)


def test_get_all_users_images_when_user_does_not_exists_images(proj_root):
    image_folder = (proj_root / image_storage_settings.storage_folder_name).resolve()
    image_folder.mkdir()
    with pytest.raises(StorageDALNotExistsError):
        get_all_user_images(1)


@pytest.fixture()
def _mock_uuid4(mocker):
    mocker.patch('final_project.data_access_layer.storage.uuid.uuid4').side_effect = [
        '1',
        '2',
    ]


@pytest.fixture()
def image_path_for_user1():
    return f'{image_storage_settings.storage_folder_name}/1-{image_storage_settings.items_in_one_folder}/1'


@pytest.mark.usefixtures('_mock_uuid4', '_save_two_images')
def test_get_all_users_images(image_path_for_user1):
    images = get_all_user_images(1)
    res = list(map(lambda img: img.path, images))
    assert len(res) == 2
    for path in res:
        assert (
            f'{image_path_for_user1}/1' in path or f'{image_path_for_user1}/2' in path
        )
