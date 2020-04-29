from final_project.data_access_layer.serialization import serialize
from final_project.database.database import create_session
from final_project.database.models import Post as DBPost
from final_project.exceptions import PostDALNotExistsError
from final_project.messages import Message
from final_project.models import Post


class PostDAL:
    @staticmethod
    async def get_post(post_id: int) -> Post:
        with create_session() as session:
            post = session.query(DBPost).filter(DBPost.id == post_id).first()
            if not post:
                raise PostDALNotExistsError(Message.POST_NOT_EXISTS.value)
            return serialize(post)
