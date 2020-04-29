import base64
from io import BytesIO
from pathlib import Path
from PIL.Image import open, Image
from final_project.models import Base64


def rmtree(root: Path) -> None:
    for p in root.iterdir():
        if p.is_dir():
            rmtree(p)
        else:
            p.unlink()

    root.rmdir()


def decode_base64_to_bytes(base_64: Base64) -> bytes:
    return base64.standard_b64decode(base_64)


def encode_bytes_to_base64(bytes_: bytes) -> Base64:
    k = base64.standard_b64encode(bytes_)
    return Base64(k)


# a = 'iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAABhWlDQ1BJQ0MgcHJvZmlsZQAAKJF9kT1Iw0AcxV/TSkUqIhYRcQhYO1kQFXHUKhShQqkVWnUwufRDaNKQpLg4Cq4FBz8Wqw4uzro6uAqC4AeIk6OToouU+L+k0CLGg+N+vLv3uHsHCPUyU83AGKBqlpFOxMVsbkUMviKAfvQiimGJmfpsKpWE5/i6h4+vdzGe5X3uz9Gt5E0G+ETiGaYbFvE68dSmpXPeJw6zkqQQnxOPGnRB4keuyy6/cS46LPDMsJFJzxGHicViG8ttzEqGSjxJHFFUjfKFrMsK5y3OarnKmvfkLwzlteUlrtMcQgILWEQKImRUsYEyLMRo1Ugxkab9uId/0PGnyCWTawOMHPOoQIXk+MH/4He3ZmFi3E0KxYGOF9v+GAGCu0CjZtvfx7bdOAH8z8CV1vJX6sD0J+m1lhY5Anq2gYvrlibvAZc7wMCTLhmSI/lpCoUC8H5G35QD+m6BrlW3t+Y+Th+ADHWVvAEODoFokbLXPN7d2d7bv2ea/f0Ai/dysXLRVz4AAAAJcEhZcwAALiMAAC4jAXilP3YAAAAHdElNRQfkBBYRKQCYUQsbAAAAGXRFWHRDb21tZW50AENyZWF0ZWQgd2l0aCBHSU1QV4EOFwAAABZJREFUCNdj/P//PwMDAxMDAwMDAwMAJAYDAb0e47oAAAAASUVORK5CYII='
# k = decode_base64_to_bytes(a)
# image: Image = open(BytesIO(k))
# res = BytesIO()
# image.save(res, 'png')
# c = encode_bytes_to_base64(res.getvalue())
# print(c)
