from pathlib import Path


def ensure_dir(path):

    path = Path(path)

    path.mkdir(
        parents=True,
        exist_ok=True
    )

    return path


def ensure_dirs(*paths):

    for path in paths:

        ensure_dir(path)