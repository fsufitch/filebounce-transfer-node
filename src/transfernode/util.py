import time


def make_timestamp():
    return int(time.time() * 1000)

class Singleton:
    def __init__(self, klass):
        self._class = klass
        self._instance = None

    def __call__(self, *args, **kwargs):
        if self.has_instance():
            raise ValueError("Singleton already instantiated")
        self._instance = self._class(*args, **kwargs)
        return self._instance

    def has_instance(self):
        return self._instance is not None

    def instance(self):
        if not self.has_instance():
            raise ValueError("Singleton not yet instantiated")
        return self._instance
