import pytest
from final_project.exceptions import MyImageError
from final_project.image_processor.image import MyImage


@pytest.mark.parametrize('image_in_bytes', ['1x2.png', '1x1.png'], indirect=True)
def test_cut_raise_error_when_image_invalid(image_in_bytes):
    my_image = MyImage(image_in_bytes)
    with pytest.raises(MyImageError):
        my_image.cut(1)


@pytest.mark.parametrize('image_in_bytes', ['2x2.png'], indirect=True)
@pytest.mark.parametrize('aspect_resolution', [1, 2, 3])
def test_cut_image(image_in_bytes, aspect_resolution):
    my_image = MyImage(image_in_bytes)
    my_image.cut(aspect_resolution)
    assert my_image.height == my_image.width == aspect_resolution


def test_image_constructor_will_fail_if_bytes_is_not_a_image():
    with pytest.raises(MyImageError):
        MyImage(b'123')
