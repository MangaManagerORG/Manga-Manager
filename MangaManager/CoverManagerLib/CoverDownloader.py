import os
import urllib.request
from pprint import pprint

import requests

url = "https://api.mangadex.org"

manga_id = import("Mangadex Manga ID Here: ")
if __name__ == '__main__':
    data = {"manga[]": [manga_id], "includes[]": ["manga"], "limit":50}
    r = requests.get(url + "/cover", params=data)

    r_json = r.json()
    pprint(r_json)

    print("\nfirst cover:\n")

    for i, cover_data in enumerate(r_json.get("data")):
        data = {"includes[]": ["cover_art"],
                "order": {
                    "createdAt": "asc",
                    "updatedAt": "asc",
                    "volume": "asc"
                }
                }
        cover_id = cover_data.get('id')
        cover_titles = list(filter(lambda p: p.get("type") == "manga", cover_data.get("relationships")))[0]. \
            get("attributes").get("title")

        normalized_manga_name = (cover_titles.get("jp") or cover_titles.get("en"))
        cover_filename = cover_data.get("attributes").get("fileName")
        cover_volume = cover_data.get("attributes").get("volume")
        cover_loc = cover_data.get("attributes").get("locale")
        filename, file_extension = os.path.splitext(cover_filename)
        image_url = f"https://mangadex.org/covers/{manga_id}/{cover_filename}"
        print(image_url)
        urllib.request.urlretrieve(image_url, f"Cover_Vol.{str(cover_volume).zfill(2)}_{cover_loc}{file_extension}")
