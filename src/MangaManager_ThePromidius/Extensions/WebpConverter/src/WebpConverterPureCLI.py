import argparse

import prompt_toolkit

from .WebpConverterLib import WebpConverterLib


class WebpConverterPureCLI(WebpConverterLib):
    # _pathList: list[str] = list()
    _log = None
    
    @property
    def items_path_list(self):
        return self._pathList
    
    @items_path_list.setter
    def items_path_list(self, path):
        self._pathList = [x for x in path if x.endswith(".cbz")]
        
    def __init__(self, path: list, recursive:bool = False):
        super(WebpConverterPureCLI, self).__init__()
        self.recursive = recursive
        self.items_path_list = path
    
    def run(self):
        print(f"You are about to convert {len(self._pathList)} file{'s' if len(self._pathList) >1 else ''}")
        input("Press to continue")
        self.process()
        
