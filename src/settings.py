import pathlib

### PATHS ###
# Project root dir
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
# Logging output
LOG_FILE = BASE_DIR / 'console.log'

### LOGGING CONFIG ###
# Logging log levels
LOGGING_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
# Default logging log-level
DEFAULT_LOG_LEVEL = 'INFO'
