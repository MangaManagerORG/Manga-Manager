from concurrent.futures import ProcessPoolExecutor


class ProcessingPool(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
            cls._instance.pool = ProcessPoolExecutor()
        return cls._instance

    def submit(self, func, *args, **kwargs):
        return self.pool.submit(func, *args, **kwargs)
