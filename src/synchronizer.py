import logging
import pathlib
import shutil
import typing

from collections import defaultdict

from src.file import DirFile, TextFile


class Synchronizer:
    """Synchronizer class tool."""

    def __init__(
            self,
            source_dir: pathlib.Path,
            replica_dir: pathlib.Path
    ) -> None:
        """
        Initializer Synchronizer class.

        :param pathlib.Path source_dir: Path to source directory.
        :param pathlib.Path replica_dir: Path to replica directory.
        """

        self.source: DirFile = source_dir
        self.replica: DirFile = replica_dir
        self.tracked_files: dict[int, dict[str, TextFile | DirFile]] = defaultdict(dict)

        if not self.source.path.exists():
            logging.error(f'Source directory does not exist: {self.source.path}')
            raise Exception("Source directory does not exist.")

        if self.replica.path.exists():
            logging.warning('Replica directory exist and will be cleared.')
            shutil.rmtree(self.replica.path)

    def initialize(self) -> None:
        """Initialize synchronization."""

        logging.info('Initialization...')
        self.run_function_recursive(
            self.source,
            lambda file: file.update_children() if isinstance(file, DirFile) else None,
        )
        self.run_function_recursive(self.source, self.save_tracked_file)
        self.run_function_recursive(self.source, self.replicate_file)

    def save_tracked_file(
            self,
            file: DirFile | TextFile
    ) -> None:
        """Save tracked files."""

        file_id = file.get_id()
        if not self.tracked_files.get(file_id):
            logging.info(f'Started tracking {file.path}')

        self.tracked_files[file_id].update({
            'source': file,
        })

    def run_function_recursive(
            self,
            file: DirFile | TextFile,
            function: typing.Callable,
            *args,
            **kwargs
    ) -> None:
        """
        Save recursive files.

        :param pathlib.Path file: File.
        :param typing.Callable function: callable that will be call on each file object.
        """

        function(file, *args, **kwargs)
        if isinstance(file, TextFile):
            logging.debug(f'Saving content of {file.path} to {file}')
            file.content = file.path.read_text()
            return

        for child in file.children:
            self.run_function_recursive(child, function)

    def replicate_file(
            self,
            file: DirFile | TextFile
    ) -> None:
        """
        Create replica of given file.

        :param DirFile | TextFile file: File to replicate.
        """

        replica_path = self.replica.path / file.path.relative_to(self.source.path)

        if isinstance(file, DirFile):
            replica_file = DirFile(replica_path)
        else:
            replica_file = TextFile(replica_path)
            replica_file.content = file.content

        replica_file.create()
        self.tracked_files.get(file.get_id()).update({'replica': replica_file})

    def sync(self):
        """Run source and replica dir synchronization."""

        logging.info(f'Synchronizing {self.source.path} with {self.replica.path}')
        files = self.tracked_files.copy()
        saved_files_ids = files.keys()

        self.run_function_recursive(
            self.source,
            lambda file: file.update_children() if isinstance(file, DirFile) else None,
        )
        self.run_function_recursive(self.source, self.save_tracked_file)

        deleted_files_ids = []
        for file_id in saved_files_ids:
            source_file = self.tracked_files[file_id].get('source')
            file_exists = source_file.path.exists()
            if not file_exists or file_exists and source_file.path.stat().st_ino != file_id:
                del self.tracked_files[file_id]
                deleted_files_ids.append(file_id)

        new_files = set(self.tracked_files.keys()) - set(saved_files_ids)

        for deleted_file_id in deleted_files_ids:
            replica_file = files.get(deleted_file_id)['replica']
            try:
                logging.info(f'Trying to remove replica of {replica_file.path}')
                replica_file.remove()
            except FileNotFoundError:
                logging.info(f'{files.get(deleted_file_id)['replica'].path} was deleted before.')
            else:
                logging.info('File removed')

        for new_file_id in new_files:
            self.replicate_file(self.tracked_files[new_file_id]['source'])

        for file in self.tracked_files.values():
            source_file = file['source']
            replica_file = file['replica']

            if replica_file.path.relative_to(self.replica.path) != source_file.path.relative_to(self.source.path):
                new_path = self.replica.path / source_file.path.relative_to(self.source.path)
                logging.info(f'{replica_file.path} moved to {new_path}')
                try:
                    replica_file.move(new_path)
                except FileNotFoundError:
                    replica_file.path = new_path
                    replica_file.create()

            if hasattr(source_file, 'content'):
                if replica_file.content != source_file.content:
                    logging.info(f'Content of {source_file.path} is has been changed.')
                    logging.debug(f'Content of {replica_file.path} is now {source_file.content}.')

                    replica_file.content = source_file.content
                    replica_file.create()
