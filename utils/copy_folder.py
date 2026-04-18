import shutil

from constraints import DirectoryPath


def copy_folder(source: DirectoryPath, destination: DirectoryPath) -> None:
    if not any(source.iterdir()):
        raise FileNotFoundError(f"Source folder {source} doesnt contain any files.")

    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)