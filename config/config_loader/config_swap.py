import os
import shutil
from contextlib import contextmanager

@contextmanager
def config_swap(test_config_path: str, original_config_path: str = 'config/config.yml') -> any:
    """Context manager to temporarily swap configuration files.

    Args:
        test_config_path (str): The path to the test configuration file to be used.
        original_config_path (str): The path to the original configuration file (default is 'config/config.yml').

    Raises:
        FileNotFoundError: If the test configuration file does not exist.
    """
    if not os.path.exists(test_config_path):
        raise FileNotFoundError(f"Test config file not found: {test_config_path}")

    original_backup_path = original_config_path + '.bak'
    if not os.path.exists(original_backup_path):
        shutil.copy(original_config_path, original_backup_path)

    shutil.copy(test_config_path, original_config_path)

    try:
        yield  # This can yield any necessary values, which can be typed accordingly if needed
    finally:
        if os.path.exists(original_backup_path):
            shutil.copy(original_backup_path, original_config_path)
            os.remove(original_backup_path)
