import logging
import pathlib
import typing
import shutil

class _File:
    """Private class which handle default file information"""

    def __init__(self, path: pathlib.Path) -> None:
        """
        Init File class

        :param pathlib.Path path: Path to the file.
        """

        self.path: pathlib.Path = path

    def get_id(self) -> int:
        """
        Get file inode.
        :return: int File inode.
        """

        return self.path.stat().st_ino

    def create(self):
        """Create file."""

        raise NotImplementedError

    def remove(self):
        """Remove file."""

        raise NotImplementedError

    def move(self, new_path: pathlib.Path):
        """Move  file to object path."""

        logging.info(f'Replacing to {self.path}')
        self.remove()
        self.path = new_path
        self.create()


class DirFile(_File):
    """Class which handle dir file object"""

    def __init__(self, path: pathlib.Path) -> None:
        super().__init__(path)
        self.children: typing.List[typing.Union[DirFile, TextFile]] = []

    def update_children(self):
        """Update children attribute."""

        self.children = []

        for file in self.path.iterdir():
            self.children.append(
                DirFile(file) if file.is_dir() else TextFile(file)
            )

    def create(self):
        """Create dir from object path."""

        logging.info(f'Creating dir from path: {self.path}')
        self.path.mkdir(exist_ok=True, parents=True)

    def remove(self):
        """Remove dir from object path."""

        logging.info(f'Removing dir from path: {self.path}')
        shutil.rmtree(self.path)


class TextFile(_File):
    """Class which handle text file object"""

    def __init__(self, path: pathlib.Path) -> None:
        super().__init__(path)
        self.content: str = ''

    def create(self):
        """Create text file from object path."""

        logging.info(f'Creating file from path: {self.path}')
        try:
            self.path.write_text(self.content)
        except FileNotFoundError:
            self.path.parent.mkdir(exist_ok=True, parents=True)

    def remove(self):
        """Remove text file from object path."""

        logging.info(f'Removing file from path: {self.path}')
        self.path.unlink()
