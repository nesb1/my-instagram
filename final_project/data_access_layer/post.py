from final_project.data_access_layer.serialization import serialize
from final_project.database.database import create_session
from final_project.database.models import Post as DBPost
from final_project.exceptions import PostDALNotExistsError
from final_project.messages import Message
from final_project.models import Post, Base64, PostWithImage
from final_project.storage_client import get_image_from_storage_async


class PostDAL:
    @staticmethod
    async def get_post(post_id: int) -> PostWithImage:
        with create_session() as session:
            post: DBPost = session.query(DBPost).filter(DBPost.id == post_id).first()
            if not post:
                raise PostDALNotExistsError(Message.POST_NOT_EXISTS.value)

            image: Base64 = await get_image_from_storage_async(post.image_path)
            serialized_post: Post = serialize(post)
            return PostWithImage(**serialized_post.dict(), image=image)
