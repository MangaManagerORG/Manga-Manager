import unittest

from CoverManagerLib.CoverDownloader import App as CoverDownloaderApp


class CoverDownloaderTest(unittest.TestCase):

    def test_UrlIsImage(self):
        test_url = ["https://mangadex.org/title/a96676e5-8ae2-425e-b549-7f15dd34a6d8/komi-san-wa-komyushou-desu",
                    "https://mangadex.org/title/4b2e5feb-6137-4be9-a73d-add5e27263e7/limit-breaker?tab=art",
                    "https://mangadex.org/title/37f5cce0-8070-4ada-96e5-fa24b1bd4ff9/kaguya-sama-wa-kokurasetai-tensai-tachi-no-renai-zunousen,"
                    "https://mangadex.org/title/1180743d-8e38-4c00-b767-c53169fadc6a/tensura-nikki-tensei-shitara-slime-datta-ken"
                    ]
        app = CoverDownloaderApp()
        app.set_output_folder()
        for i, url in enumerate(test_url):
            print(f"Asserting values for serie: {url.split('/')[-1]}")
            with self.subTest(i=i):
                parsed_url = app.parse_mangadex_id(url)

                app.download_covers(parsed_url, test_run=True)
