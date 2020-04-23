import pathlib

import pytest
from final_project.config import image_storage_settings
from final_project.image_processor.saver import save_image
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
