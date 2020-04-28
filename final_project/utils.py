import base64
from pathlib import Path


def rmtree(root: Path) -> None:
    for p in root.iterdir():
        if p.is_dir():
            rmtree(p)
        else:
            p.unlink()

    root.rmdir()


def decode_base64_to_bytes(base_64) -> bytes:
    return base64.standard_b64decode(base_64)
