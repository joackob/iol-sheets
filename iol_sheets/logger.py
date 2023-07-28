import logging
import sys


class Logger(logging.Logger):
    def __init__(self, name: str, level=logging.NOTSET) -> None:
        formatter = logging.Formatter("%(levelname)s:%(name)s: %(message)s")
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)

        logging.Logger.__init__(self, name, level)
        self.addHandler(handler)
