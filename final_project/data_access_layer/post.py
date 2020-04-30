from final_project.data_access_layer.serialization import serialize
from final_project.database.database import create_session
from final_project.database.models import Post as DBPost
from final_project.exceptions import PostDALNotExistsError, StorageError, PostDALError
from final_project.messages import Message
from final_project.models import Base64, Post, PostWithImage
from final_project import storage_client


class PostDAL:
    @staticmethod
    async def get_post(post_id: int) -> PostWithImage:
        with create_session() as session:
            post: DBPost = session.query(DBPost).filter(DBPost.id == post_id).first()
            if not post:
                raise PostDALNotExistsError(Message.POST_NOT_EXISTS.value)
            try:
                image: Base64 = await storage_client.get_image_from_storage_async(post.image_path)
            except StorageError:
                raise PostDALError(Message.IMAGE_DOES_NOT_EXISTS_ON_STORAGE.value)
            serialized_post: Post = serialize(post)
            return PostWithImage(**serialized_post.dict(), image=image)
