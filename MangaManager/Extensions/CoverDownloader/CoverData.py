import dataclasses
from pathlib import Path
from os.path import splitext
@dataclasses.dataclass
class SeriesCoverData:
    normalized_name:str

class CoverData:
    # filename:str
    # extension:str
    #
    # volume:str
    # locale:str
    @property
    def dest_filename(self):
        """
        The final filename
        :return:
        """
        return f"Cover{'_Vol.'+str(self.volume).zfill(2) if self.volume else ''}{'_' + self.locale if self.locale else ''}{self.extension}"


    def __init__(self,source_filename=None,volume=None,locale=None):

        self.source_filename=source_filename
        if source_filename:
            self.filename, self.extension = splitext(self.source_filename)
        else:
            self.filename, self.extension = None, None
        self.volume=volume
        self.locale=locale


    def from_cover_data(self,cover_data):
        self.source_filename = cover_data.get("attributes").get("fileName")
        self.filename, self.extension = splitext(self.source_filename)
        self.volume = cover_data.get("attributes").get("volume")
        self.locale = cover_data.get("attributes").get("locale")
        return self