import unittest.mock
import pathlib
import pytest

from src.synchronizer import Synchronizer, TextFile, DirFile


class TestSynchronizer:
    @unittest.mock.patch('pathlib.Path.exists')
    def get_synchronizer(
            self,
            file_exists_mock: unittest.mock.MagicMock,
    ):

        file_exists_mock.side_effect = [True, False]

        return Synchronizer(
            DirFile(pathlib.Path('data/test/test_source').resolve()),
            DirFile(pathlib.Path('data/test/test_replica').resolve()),
        )

    @unittest.mock.patch('pathlib.Path.exists')
    @unittest.mock.patch('shutil.rmtree')
    def test_init(
            self,
            rmtree_mock: unittest.mock.MagicMock,
            file_exists_mock: unittest.mock.MagicMock,
    ):
        file_exists_mock.side_effect = [False]
        with pytest.raises(Exception):
            Synchronizer(
                DirFile(pathlib.Path('test/test_source').resolve()),
                DirFile(pathlib.Path('test/test_replica').resolve()),
            )

        file_exists_mock.side_effect = [True, True]
        Synchronizer(
            DirFile(pathlib.Path('test/test_source').resolve()),
            DirFile(pathlib.Path('test/test_replica').resolve()),
        )
        rmtree_mock.assert_called_once()

    @unittest.mock.patch('src.file._File.get_id')
    def test_save_tracked_file(
            self,
            file_id_mock: unittest.mock.MagicMock,
    ):

        file_id_mock.return_value = 1
        synchronizer = self.get_synchronizer()
        text_file = TextFile(synchronizer.source.path / 'text_file.txt')

        synchronizer.save_tracked_file(text_file)

        file_id_mock.assert_called()
        assert synchronizer.tracked_files == {1: {'source': text_file}}

    @unittest.mock.patch('src.synchronizer.Synchronizer.run_function_recursive')
    def test_initialize(
            self,
            save_recursive_mock: unittest.mock.MagicMock,
    ):

        synchronizer = self.get_synchronizer()
        assert synchronizer.tracked_files == {}

        synchronizer.initialize()

        update_children_call = unittest.mock.call(
            synchronizer.source,
            unittest.mock.ANY
        )
        save_tracked_file_call = unittest.mock.call(synchronizer.source, synchronizer.save_tracked_file)
        replicate_file_call = unittest.mock.call(synchronizer.source, synchronizer.replicate_file)

        save_recursive_mock.assert_has_calls([
            update_children_call,
            save_tracked_file_call,
            replicate_file_call
        ])

    @unittest.mock.patch('pathlib.Path.read_text')
    def test_run_function_recursive(
            self,
            read_text_mock: unittest.mock.MagicMock,
    ):
        read_text_mock.return_value = 'test_text'

        synchronizer = self.get_synchronizer()
        text_file = TextFile(synchronizer.source.path / 'text_file.txt')
        function = unittest.mock.MagicMock()

        synchronizer.run_function_recursive(text_file, function, 1, test_kwarg=2)

        function.assert_called_once_with(text_file, 1, test_kwarg=2)

        dir_file = DirFile(synchronizer.source.path)
        child_dir_file = DirFile(dir_file.path / 'child_dir/')
        child_child_dir_file = DirFile(child_dir_file.path / '/child_dir/')

        dir_file.children.extend([child_dir_file, text_file])
        child_dir_file.children.extend([child_child_dir_file])

        function.reset_mock()

        synchronizer.run_function_recursive(dir_file, function, 1, test_kwarg=2)

        assert function.call_count == 4

    @unittest.mock.patch('src.file.DirFile.create')
    @unittest.mock.patch('src.file.TextFile.create')
    @unittest.mock.patch('src.file._File.get_id')
    def test_replicate_file(
            self,
            file_get_id_mock: unittest.mock.MagicMock,
            text_file_create_mock: unittest.mock.MagicMock,
            dir_file_create_mock: unittest.mock.MagicMock
    ):

        synchronizer = self.get_synchronizer()
        dir_file = DirFile(synchronizer.source.path / 'dir/')
        text_file = TextFile(synchronizer.source.path / 'text_file.txt')
        text_file.content = 'test_text'

        file_get_id_mock.side_effect = [1, 2, 1, 2, 1, 2]
        synchronizer.save_tracked_file(dir_file)
        synchronizer.save_tracked_file(text_file)

        assert synchronizer.tracked_files == {1: {'source': dir_file}, 2: {'source': text_file}}

        synchronizer.replicate_file(dir_file)
        synchronizer.replicate_file(text_file)

        assert isinstance(synchronizer.tracked_files.get(1)['replica'], DirFile)
        assert isinstance(synchronizer.tracked_files.get(2)['replica'], TextFile)
        dir_file_create_mock.assert_called()
        text_file_create_mock.assert_called()

        dir_file_replica = synchronizer.tracked_files.get(1)['replica']
        assert isinstance(dir_file_replica, DirFile)
        assert dir_file_replica.path == synchronizer.replica.path / 'dir/'

        text_file_replica = synchronizer.tracked_files.get(2)['replica']
        assert isinstance(text_file_replica, TextFile)
        assert text_file_replica.path == synchronizer.replica.path / 'text_file.txt'
        assert text_file_replica.content == text_file.content

        synchronizer.save_tracked_file(dir_file)
        synchronizer.save_tracked_file(text_file)

        dir_file_replica = synchronizer.tracked_files.get(1)['replica']
        assert isinstance(dir_file_replica, DirFile)
        text_file_replica = synchronizer.tracked_files.get(2)['replica']
        assert isinstance(text_file_replica, TextFile)

    @unittest.mock.patch('src.file.DirFile.update_children')
    @unittest.mock.patch('src.file.DirFile.create')
    @unittest.mock.patch('src.file.DirFile.remove')
    @unittest.mock.patch('src.file.TextFile.create')
    @unittest.mock.patch('src.file.TextFile.remove')
    @unittest.mock.patch('pathlib.Path.exists')
    @unittest.mock.patch('src.synchronizer.Synchronizer.save_tracked_file')
    @unittest.mock.patch('pathlib.Path.stat')
    def test_sync(
            self,
            stats_mock: unittest.mock.MagicMock,
            save_tracked_file_mock: unittest.mock.MagicMock,
            exists_mock: unittest.mock.MagicMock,
            text_remove_mock: unittest.mock.MagicMock,
            text_create_mock: unittest.mock.MagicMock,
            dir_remove_mock: unittest.mock.MagicMock,
            dir_create_mock: unittest.mock.MagicMock,
            update_children_mock: unittest.mock.MagicMock,
    ):
        exists_mock.side_effect = [True, True, False]
        synchronizer = self.get_synchronizer()

        synchronizer.tracked_files = {
            1: {
                'source': DirFile(synchronizer.source.path / 'dira/'),
                'replica': DirFile(synchronizer.replica.path / 'dir/')
            },
            2: {
                'source': TextFile(synchronizer.source.path / 'dira/text_file.txt'),
                'replica': TextFile(synchronizer.replica.path / 'text_file.txt')
            },
            3: {
                'source': TextFile(synchronizer.source.path / 'text_file_3.txt'),
                'replica': TextFile(synchronizer.replica.path / 'dir/text_file_3.txt')
            }
        }
        stats_mock.side_effect = [
            unittest.mock.MagicMock(st_ino=1),
            unittest.mock.MagicMock(st_ino=2),
            unittest.mock.MagicMock(st_ino=4)
        ]
        synchronizer.tracked_files.get(2)['replica'].content = 'new content'

        def add_new_file(*args, **kwargs):
            synchronizer.tracked_files[4] = {
                'source': TextFile(synchronizer.source.path / 'text_file_4.txt'),
                'replica': TextFile(synchronizer.replica.path / 'text_file_4.txt')
            }

        save_tracked_file_mock.side_effect = add_new_file

        synchronizer.sync()

        for files in synchronizer.tracked_files.values():
            assert (
                files['source'].path.relative_to(synchronizer.source.path) ==
                files['replica'].path.relative_to(synchronizer.replica.path)
            )

            if isinstance(files['source'], TextFile):
                assert files['source'].content == files['replica'].content

        assert dir_create_mock.call_count == 1
        assert dir_remove_mock.call_count == 1
        assert synchronizer.tracked_files.get(3) is None
        assert text_create_mock.call_count == 3
        assert text_remove_mock.call_count == 2
        update_children_mock.assert_called_once()
