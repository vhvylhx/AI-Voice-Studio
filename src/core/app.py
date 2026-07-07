from .config import Config
from .logger import Logger


class App:

    config = Config()

    logger = Logger.get()