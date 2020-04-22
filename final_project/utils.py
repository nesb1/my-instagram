from pathlib import Path


def rmtree(root: Path) -> None:
    for p in root.iterdir():
        if p.is_dir():
            rmtree(p)
        else:
            p.unlink()

    root.rmdir()
