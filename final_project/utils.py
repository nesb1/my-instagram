import base64
from pathlib import Path

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
