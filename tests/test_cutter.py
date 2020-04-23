import pytest
from final_project.image_processor.cutter import cut


@pytest.mark.parametrize('image', ['1x2.png', '1x1.png'], indirect=True)
def test_cutter_raise_error_when_image_invalid(image):
    with pytest.raises(ValueError):
        cut(image, 1)


@pytest.mark.parametrize('image', ['2x2.png'], indirect=True)
@pytest.mark.parametrize('aspect_resolution', [1, 2, 3])
def test_cutter_image(image, aspect_resolution):
    image = cut(image, aspect_resolution)
    assert image.height == image.width == aspect_resolution
