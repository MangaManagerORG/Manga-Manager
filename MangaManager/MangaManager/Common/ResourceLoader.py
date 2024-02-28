import os
from os.path import abspath

from pkg_resources import resource_filename

res_path = abspath(resource_filename(__name__, '../../res/'))


class ResourceLoader:
    """
        ResourceLoader loads resources from res/ folder for the application
    """

    @staticmethod
    def get(filename):
        return os.path.join(res_path, filename)
