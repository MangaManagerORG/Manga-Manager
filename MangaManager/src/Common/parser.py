import re

"""
Regex Patterns adapted from Kavita: https://github.com/Kareadita/Kavita
"""
Number = "\d+(\.\d)?"
NumberRange = Number + "(-" + Number + ")?"

volume_patterns = [
    # Dance in the Vampire Bund v16-17
    re.compile(r"(?P<Series>.*)(\b|_|\s)v(?P<Volume>\d+-?\d+)", re.IGNORECASE),
    # NEEDLESS_Vol.4_-Simeon_6_v2[SugoiSugoi].rar
    re.compile(r"(?P<Series>.*)(\b|_|\s)(?!\[)(vol\.?)(?P<Volume>\d+(-\d+)?)(?!\])", re.IGNORECASE),
    # Historys Strongest Disciple Kenichi_v11_c90-98.zip or Dance in the Vampire Bund v16-17
    re.compile(r"(?P<Series>.*)(\b|_|\s)(?!\[)v(?P<Volume>" + NumberRange + ")(?!\])", re.IGNORECASE),
    # Kodomo no Jikan vol. 10, [dmntsf.net] One Piece - Digital Colored Comics Vol. 20.5-21.5 Ch. 177
    re.compile(r"(?P<Series>.*)(\b|_|\s)(vol\.? ?)(?P<Volume>\d+(\.\d)?(-\d+)?(\.\d)?)", re.IGNORECASE),
    # Killing Bites Vol. 0001 Ch. 0001 - Galactica Scanlations (gb)
    re.compile(r"(vol\.? ?)(?P<Volume>\d+(\.\d)?)", re.IGNORECASE),
    # Tonikaku Cawaii [Volume 11].cbz
    re.compile(r"(volume )(?P<Volume>\d+(\.\d)?)", re.IGNORECASE),
    # Tower Of God S01 014 (CBT) (digital).cbz
    re.compile(r"(?P<Series>.*)(\b|_||\s)(S(?P<Volume>\d+))", re.IGNORECASE),
    # vol_001-1.cbz for MangaPy default naming convention
    re.compile(r"(vol_)(?P<Volume>\d+(\.\d)?)", re.IGNORECASE)
]

series_patterns = [
    # Grand Blue Dreaming - SP02
    re.compile(r'(?P<Series>.*)(\b|_|-|\s)(?:sp)\d', re.IGNORECASE),
    # [SugoiSugoi]_NEEDLESS_Vol.2_-_Disk_The_Informant_5_[ENG].rar, Yuusha Ga Shinda! - Vol.tbd Chapter 27.001 V2 Infection ①.cbz
    re.compile(r'^(?P<Series>.*)( |_)Vol\.?(\d+|tbd)', re.IGNORECASE),
    # Mad Chimera World - Volume 005 - Chapter 026.cbz, The Duke of Death and His Black Maid - Vol. 04 Ch. 054.5 - V4 Omake
    re.compile(r'(?P<Series>.+?)(\s|_|-)+(?:Vol(ume|\.)?(\s|_|-)+\d+)(\s|_|-)+(?:(Ch|Chapter|Ch)\.?)(\s|_|-)+(?P<Chapter>\d+)', re.IGNORECASE),
    # Ichiban_Ushiro_no_Daimaou_v04_ch34_[VISCANS].zip, VanDread-v01-c01.zip
    re.compile(r'(?P<Series>.*)(\b|_)v(?P<Volume>\d+-?\d*)(\s|_|-)', re.IGNORECASE),
    # Gokukoku no Brynhildr - c001-008 (v01) [TrinityBAKumA], Black Bullet - v4 c17 [batoto]
    re.compile(r'(?P<Series>.*)( - )(?:v|vo|c|chapters)\d', re.IGNORECASE),
    # Kedouin Makoto - Corpse Party Musume, Chapter 19 [Dametrans].zip
    re.compile(r'(?P<Series>.*)(?:, Chapter )(?P<Chapter>\d+)', re.IGNORECASE),
    # Please Go Home, Akutsu-San! - Chapter 038.5 - Volume Announcement.cbz, My Charms Are Wasted on Kuroiwa Medaka - Ch. 37.5 - Volume Extras
    re.compile(r'(?P<Series>.+?)(\s|_|-)(?!Vol)(\s|_|-)((?:Chapter)|(?:Ch\.))(\s|_|-)(?P<Chapter>\d+)', re.IGNORECASE),
    # [dmntsf.net] One Piece - Digital Colored Comics Vol. 20 Ch. 177 - 30 Million vs 81 Million.cbz
    re.compile(r'(?P<Series>.+?):? (\b|_|-)(vol)\.?(\s|-|_)?\d+', re.IGNORECASE),
    # [xPearse] Kyochuu Rettou Chapter 001 Volume 1 [English] [Manga] [Volume Scans]
    re.compile(r'(?P<Series>.+?):?(\s|\b|_|-)Chapter(\s|\b|_|-)\d+(\s|\b|_|-)(vol)(ume)', re.IGNORECASE),
    # [xPearse] Kyochuu Rettou Volume 1 [English] [Manga] [Volume Scans]
    re.compile(r'(?P<Series>.+?):? (\b|_|-)(vol)(ume)', re.IGNORECASE),
]

chapter_patterns = [
    # Teen Titans v1 001 (1966-02) (digital) (OkC.O.M.P.U.T.O.-Novus)
    re.compile(r'^(?P<Series>.+?)(?: |_)v(?P<Volume>\d+)(?: |_)(c? ?)(?P<Chapter>(\d+(\.\d)?)-?(\d+(\.\d)?)?)(c? ?)', re.IGNORECASE),
    # Batman & Robin the Teen Wonder #0
    re.compile(r'^(?P<Series>.+?)(?:\s|_)#(?P<Chapter>\d+)', re.IGNORECASE),
    # Batman 2016 - Chapter 01, Batman 2016 - Issue 01, Batman 2016 - Issue #01
    re.compile(r'^(?P<Series>.+?)((c(hapter)?)|issue)(_|\s)#?(?P<Chapter>(\d+(\.\d)?)-?(\d+(\.\d)?)?)', re.IGNORECASE),
    # Batgirl Vol.2000 #57 (December, 2004)
    re.compile(r'^(?P<Series>.+?)(?:vol\.?\d+)\s#(?P<Chapter>\d+)', re.IGNORECASE),
    # Saga 001 (2012) (Digital) (Empire-Zone)
    re.compile(r'(?P<Series>.+?)(?: |_)(c? ?)(?P<Chapter>(\d+(\.\d)?)-?(\d+(\.\d)?)?)\s\(\d{4}', re.IGNORECASE),
    # Historys Strongest Disciple Kenichi_v11_c90-98.zip, ...c90.5-100.5
    re.compile(r'(\b|_)(c|ch)(\.?\s?)(?P<Chapter>(\d+(\.\d)?)-?(\d+(\.\d)?)?)', re.IGNORECASE),
    # Green Worldz - Chapter 027, Kimi no Koto ga Daidaidaidaidaisuki na 100-nin no Kanojo Chapter 11-10
    re.compile(r'^(?!Vol)(?P<Series>.*)\s?(?<!vol\. )\sChapter\s(?P<Chapter>\d+(?:\.?[\d-]+)?)', re.IGNORECASE),
    # Hinowa ga CRUSH! 018 (2019) (Digital) (LuCaZ).cbz, Hinowa ga CRUSH! 018.5 (2019) (Digital) (LuCaZ).cbz
    re.compile(r'^(?!Vol)(?P<Series>.+?)(?<!Vol)(?<!Vol\.)\s(\d\s)?(?P<Chapter>\d+(?:\.\d+|-\d+)?)(?:\s\(\d{4}\))?(\b|_|-)', re.IGNORECASE),
    # Tower Of God S01 014 (CBT) (digital).cbz
    re.compile(r'(?P<Series>.*)\sS(?P<Volume>\d+)\s(?P<Chapter>\d+(?:.\d+|-\d+)?)', re.IGNORECASE),
    # Vol 1 Chapter 2
    re.compile(r'(?P<Volume>((vol|volume|v))?(\s|_)?\.?\d+)(\s|_)(Chp|Chapter)\.?(\s|_)?(?P<Chapter>\d+)', re.IGNORECASE),
]

def _parse(patterns, group, filename):
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            volume_number = match.group(group)
            return volume_number
    return ""


def parse_volume(filename: str) -> str:
    """Attempts to parse the Volume from a filename"""
    return _parse(volume_patterns, "Volume", filename)


def parse_series(filename: str) -> str:
    """Attempts to parse the Series from a filename"""
    return _parse(series_patterns, "Series", filename)


def parse_number(filename: str) -> str:
    """Attempts to parse the Number from a filename"""
    return _parse(chapter_patterns, "Chapter", filename)
