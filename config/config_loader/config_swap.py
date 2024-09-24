import os
import shutil
from contextlib import contextmanager

@contextmanager
def config_swap(test_config_path, original_config_path='config/config.yml'):
    if not os.path.exists(test_config_path):
        raise FileNotFoundError(f"Test config file not found: {test_config_path}")

    original_backup_path = original_config_path + '.bak'
    if not os.path.exists(original_backup_path):
        shutil.copy(original_config_path, original_backup_path)

    shutil.copy(test_config_path, original_config_path)

    try:
        yield
    finally:
        if os.path.exists(original_backup_path):
            shutil.copy(original_backup_path, original_config_path)
            os.remove(original_backup_path)