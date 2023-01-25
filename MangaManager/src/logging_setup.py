import logging
import sys
from logging.handlers import RotatingFileHandler


def trace(self, message, *args, **kws):
    # Yes, logger takes its '*args' as 'args'.
    self._log(logging.TRACE, message, args, **kws)


def add_trace_level():
    logging.TRACE = 9
    logging.addLevelName(logging.TRACE, "TRACE")

    logging.Logger.trace = trace


def setup_logging(LOGFILE_PATH,level=logging.DEBUG):
    # Create our own implementation to have trace logging

    # Setup Logger

    logging.getLogger('PIL').setLevel(logging.WARNING)

    rotating_file_handler = RotatingFileHandler(LOGFILE_PATH, maxBytes=10_000_000,
                                                backupCount=2)
    rotating_file_handler.setLevel(level)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(level)
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)20s - %(levelname)8s - %(message)s',
                        handlers=[stream_handler, rotating_file_handler]
                        )

    logger = logging.getLogger()

    logger.debug('DEBUG LEVEL - MAIN MODULE')
    logger.info('INFO LEVEL - MAIN MODULE')
    logger.trace('TRACE LEVEL - MAIN MODULE')
