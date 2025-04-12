import unittest.mock
import pathlib

from src.file import DirFile, TextFile


class TestDirFile:
    def get_dir_file(self):
        return DirFile(pathlib.Path('./test').resolve())

    @unittest.mock.patch('pathlib.Path.stat')
    @unittest.mock.patch('pathlib.Path.is_dir')
    @unittest.mock.patch('pathlib.Path.iterdir')
    def test_update_children(
            self,
            iterdir_mock: unittest.mock.MagicMock,
            is_dir_mock: unittest.mock.MagicMock,
            stats_mock: unittest.mock.MagicMock
    ):
        is_dir_mock.return_value = True
        iterdir_mock.return_value = [pathlib.Path('test/test')]

        dir_file = self.get_dir_file()
        dir_file.update_children()
        dir_file.update_children()

        assert len(dir_file.children) == 1
        assert str(dir_file.children[0].path) == 'test/test'
        stats_mock.assert_called_once()

    @unittest.mock.patch('pathlib.Path.mkdir')
    def test_create(
            self,
            mkdir_mock: unittest.mock.MagicMock
    ):
        dir_file = self.get_dir_file()
        dir_file.create()

        mkdir_mock.assert_called_once()

    @unittest.mock.patch('shutil.rmtree')
    def test_remove(
            self,
            rmtree_mock: unittest.mock.MagicMock
    ):
        dir_file = self.get_dir_file()
        dir_file.remove()

        rmtree_mock.assert_called_once_with(dir_file.path)


class TestTextFile:
    def get_text_file(self):
        return TextFile(pathlib.Path('../test_replica/dsdddd').resolve())

    @unittest.mock.patch('pathlib.Path.write_text')
    def test_create(
            self,
            write_text_mock: unittest.mock.MagicMock
    ):
        text_file = self.get_text_file()
        text_file.create()

        write_text_mock.assert_called_once_with(text_file.content)

    @unittest.mock.patch('pathlib.Path.unlink')
    def test_remove(
            self,
            unlink_mock: unittest.mock.MagicMock
    ):
        text_file = self.get_text_file()
        text_file.remove()

        unlink_mock.assert_called_once()
