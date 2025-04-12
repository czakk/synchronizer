import argparse
import logging
import pathlib
import schedule

from src.file import DirFile
from src.synchronizer import Synchronizer

import src.settings as settings

parser = argparse.ArgumentParser(description='')

def main():
    parser.add_argument(
        '--source-dir',
        type=pathlib.Path,
        required=True,
        help='Required. Path to source directory.'
    )
    parser.add_argument(
        '--replica-dir',
        type=pathlib.Path,
        required=True,
        help='Required. Path to replica directory.'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Optional. Synchronization interval in seconds. Default 30 seconds.'
    )
    parser.add_argument(
        '--log-file',
        type=pathlib.Path,
        help=f'Optional. Path to log file. Default PROJECT_ROOT/{settings.LOG_FILE.name}.',
        default=settings.LOG_FILE
    )
    parser.add_argument(
        '--log-level',
        default=settings.DEFAULT_LOG_LEVEL,
        choices=settings.LOGGING_LEVELS,
        help='Optional. Set the logging level',
    )
    args = parser.parse_args(namespace=parser)

    logging.basicConfig(
        level=logging.getLevelName(args.log_level),
        format='%(asctime)s - [ %(levelname)s ] - %(message)s',
        handlers=[
            logging.FileHandler(args.log_file.resolve()),
            logging.StreamHandler()
        ],
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    sync = Synchronizer(
        DirFile(args.source_dir.resolve()),
        DirFile(args.replica_dir.resolve())
    )
    sync.initialize()

    schedule.every(args.interval).seconds.do(sync.sync)
    while True:
        try:
            schedule.run_pending()
        except KeyboardInterrupt:
            logging.info('Stopping synchronizer.')

if __name__ == '__main__':
    main()
