import unittest
from unittest.mock import patch

from src.MangaManager_ThePromidius.MetadataManager.MetadataManagerLib import MetadataManagerLib


class CoreTesting(unittest.TestCase):

    @patch.multiple(MetadataManagerLib, __abstractmethods__=set())
    def test(self):
        self.instance = MetadataManagerLib()
