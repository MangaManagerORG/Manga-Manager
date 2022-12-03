import abc
import logging
import time
from threading import Timer

from src.MangaManager_ThePromidius.Common.utils import get_elapsed_time, get_estimated_time

logger = logging.getLogger()

class RepeatedTimer(object):
    def __init__(self, interval = 1):
        """

        :param interval:
        :param total:
        """
        self._timer = None
        self.interval = interval

        self.is_running = False
        self.total = -1
        # self.start()
        self.update_hook: set[callable] = set()

    def register_callable(self, function: callable):
        """
        Registers a function that will be called in the defined interval
        :param function: The callable
        :return:
        """
        self.update_hook.add(function)

    def unregister_callable(self, function: callable):
        self.update_hook.remove(function)

    def _run(self):
        self.is_running = False
        self.start()
        self._call_hooks()

    def _call_hooks(self):
        for function in self.update_hook:
            try:
                function()
            except Exception:
                logger.exception("Exception calling the update hook")

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        if self._timer is not None:
            self._timer.cancel()
        self.is_running = False
        self._timer = None


class ProgressBar(abc.ABC):
    def __init__(self):

        self.timer = RepeatedTimer()
        self.timer.register_callable(self._update)
        self.start_time = -1
        self.processed = 0
        self.processed_errors = 0
        self.total = -1


    @property
    def label_text(self):
        return f"""Processed: {(self.processed - self.processed_errors)}/{self.total} files - {self.processed_errors} errors
Elapsed time  : {get_elapsed_time(self.start_time)}
Estimated time: {get_estimated_time(self.start_time, self.processed, self.total)}"""
    @property
    def percentage(self):
        return (self.processed / self.total) * 100

    @abc.abstractmethod
    def _update(self):
        ...
    def start(self,total):
        self.total = total
        if self.total == -1:
            raise ValueError("Configure the progressbar items first")
        self.start_time = time.time()
        self.timer.start()
    def stop(self):
        self.timer.stop()
        self._update()
    def increase_processed(self):
        if self.processed >= self.total:
            return
        self.processed += 1
        self._update()

    def increase_failed(self):
        self.processed_errors += 1
        self.increase_processed()

    def reset(self):
        self.total = self.timer.total = -1
        self.processed = 0  # Processed items. Whether they fail or not
        self.processed_errors = 0  # Items that failed
        self._update()




