import logging

from .app_info import LOG_FILE
from .app_paths import AppPaths


class Logger:

    _logger = None

    @classmethod
    def get(cls):

        if cls._logger:
            return cls._logger

        AppPaths.ensure()

        logger = logging.getLogger("AI Voice Studio")

        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s : %(message)s"
        )

        file_handler = logging.FileHandler(
            AppPaths.LOGS / LOG_FILE,
            encoding="utf-8"
        )

        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()

        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        cls._logger = logger

        return logger