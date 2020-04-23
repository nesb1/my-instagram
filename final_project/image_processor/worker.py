from io import BytesIO

from final_project.config import image_cutting_settings
from final_project.database.database import create_session
from final_project.database.models import Post
from final_project.image_processor import cutter, saver
from PIL.Image import open as open_image


def process_image(user_id: int, post_id: int, image_in_bytes: bytes) -> None:
    '''
    Обрезает изображение до квадратного, сохраняет в файловое хранилище
    и фиксирует путь к изображению в бд
    '''
    image = open_image(BytesIO(image_in_bytes))
    image = cutter.cut(image, image_cutting_settings.aspect_resolution)
    path = saver.save_image(user_id, image)
    with create_session() as session:
        post = session.query(Post).filter(Post.id == post_id).first()
        post.image_path = path
        session.add(post)
