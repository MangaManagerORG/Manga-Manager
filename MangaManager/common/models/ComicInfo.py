from io import BytesIO
from xml.etree import ElementTree as ET

comic_info_tag_map = {
    "series": "Series",
    "localized_series": "LocalizedSeries",
    "series_sort": "SeriesSort",
    "count": "Count",
    "writer": "Writer",
    "penciller": "Penciller",
    "inker": "Inker",
    "colorist": "Colorist",
    "letterer": "Letterer",
    "cover_artist": "CoverArtist",
    "editor": "Editor",
    "translator": "Translator",
    "publisher": "Publisher",
    "imprint": "Imprint",
    "characters": "Characters",
    "teams": "Teams",
    "locations": "Locations",
    "main_character_or_team": "MainCharacterOrTeam",
    "other": "Other",
    "genre": "Genre",
    "age_rating": "AgeRating",
    "series_group": "SeriesGroup",
    "alternate_series": "AlternateSeries",
    "story_arc": "StoryArc",
    "story_arc_number": "StoryArcNumber",
    "alternate_count": "AlternateCount",
    "alternate_number": "AlternateNumber",
    "title": "Title",
    "summary": "Summary",
    "review": "Review",
    "tags": "Tags",
    "web": "Web",
    "number": "Number",
    "volume": "Volume",
    "format": "Format",
    "manga": "Manga",
    "year": "Year",
    "month": "Month",
    "day": "Day",
    "language_iso": "LanguageISO",
    "notes": "Notes",
    "community_rating": "CommunityRating",
    "black_and_white": "BlackAndWhite",
    "page_count": "PageCount",
    "scan_information": "ScanInformation",
    "gtin": "GTIN"
}


class ComicInfo:
    series = ""
    localized_series = ""
    count = ""
    writer = ""
    penciller = ""
    inker = ""
    colorist = ""
    letterer = ""
    cover_artist = ""
    editor = ""
    translator = ""
    publisher = ""
    imprint = ""
    characters = ""
    teams = ""
    locations = ""
    main_character_or_team = ""
    genre = ""
    age_rating = ""
    series_sort = ""
    series_group = ""
    alternate_series = ""
    story_arc = ""
    story_arc_number = ""
    alternate_count = ""
    alternate_number = ""
    title = ""
    summary = ""
    review = ""
    tags = ""
    web = ""
    number = ""
    volume = ""
    format = ""
    manga = ""
    year = ""
    month = ""
    day = ""
    language_iso = ""
    notes = ""
    community_rating = ""
    black_and_white = ""
    page_count = ""
    scan_information = ""
    other = ""
    gtin = ""

    def __init__(self):
        pass

    def set_by_tag_name(self, tag, value):
        for key, v in comic_info_tag_map.items():
            if tag == v:
                if value is None:
                    value = ""
                self.__setattr__(key, value)

    def get_by_tag_name(self, name) -> str:
        for key, value in comic_info_tag_map.items():
            if name == value:
                ret = getattr(self, key)
                if ret is None:
                    return ""
                return ret
        return ""

    @classmethod
    def from_xml(cls, xml_string):
        root = ET.ElementTree(ET.fromstring(xml_string.encode("utf-8"), parser=ET.XMLParser(encoding='utf-8')))
        comic_info = cls()
        for prop in [a for a in dir(comic_info) if not a.startswith('__') and not callable(getattr(comic_info, a))]:
            comic_info.__setattr__(prop, root.findtext(comic_info_tag_map[prop]))

        return comic_info

    def to_xml(self):
        root = ET.Element("ComicInfo")
        for key, mapped_key in comic_info_tag_map.items():
            value = str(self.get_by_tag_name(mapped_key))
            if value:
                ET.SubElement(root, mapped_key).text = value

        # prevent creation of self-closing tags
        for node in root.iter():
            if node.text is None:
                node.text = ""
        f = BytesIO()
        et = ET.ElementTree(root)
        ET.indent(et)
        et.write(f, encoding='utf-8', xml_declaration=True)
        ret_xml = f.getvalue()
        return str(ret_xml, encoding="utf-8")
        # print(f.getvalue())  # your XML file, encoded as UTF-8
        # output_xml = ET.tostring(root, encoding="UTF-8", xml_declaration=True, method='xml').decode("utf8")
        # return output_xml

    """Returns TRUE if it has changes"""
    def has_changes(self, other):
        for key in comic_info_tag_map.keys():
            if getattr(self, key) != getattr(other, key):
                return True
        return False