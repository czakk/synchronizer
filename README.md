# Synchronizer

1. Python version: 3.12
2. git clone repo
3. Download poetry
```pip install poetry```
4. ```poetry install```
5. Run app ``poetry run synchronize``
    ```
    usage: synchronize [-h]
    
        --source-dir SOURCE_DIR
        --replica-dir REPLICA_DIR
        [--interval INTERVAL]
        [--log-file LOG_FILE]
        [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
        
        options:
        -h, --help      show this help message and exit
        --source-dir SOURCE_DIR
                Required. Path to source directory.
        --replica-dir REPLICA_DIR
                Required. Path to replica directory.
        --interval INTERVAL   Optional. Synchronization interval in seconds. Default 30 seconds.
        --log-file LOG_FILE   Optional. Path to log file. Default PROJECT_ROOT/console.log.
        --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                Optional. Set the logging level
    ```
6. Example of usage
    
    ``poetry run synchronize --source-dir ./source_dir --replica-dir ./replica_dir --interval 30 --log-file console.
    log --log-level DEBUG``