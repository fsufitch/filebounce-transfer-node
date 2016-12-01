from transfernode.util import Singleton

_default_config_sentinel = object()

@Singleton
class TransferNodeConfiguration:
    def __init__(self, config_object):
        self._CONFIG = config_object


    def get_config(self, *path, default=_default_config_sentinel):
        config = self._CONFIG
        for key in path:
            if key not in config:
                config = default
                if config == _default_config_sentinel:
                    raise KeyError("Configuration key path not found: %s" % ' > '.join(path))
            else:
                config = config[key]
        return config
