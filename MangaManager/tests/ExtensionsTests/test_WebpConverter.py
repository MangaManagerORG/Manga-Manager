# from src.Common.loadedcomicinfo import LoadedComicInfo
from logging_setup import add_trace_level

add_trace_level()

# Fixme reimplement extensions
# class LoadedComicInfoConvertsToWebpTests(unittest.TestCase):
#     def setUp(self) -> None:
#         print(os.getcwd())
#         # Make sure there are no test files else delete them:
#         leftover_files = [listed for listed in os.listdir() if listed.startswith("Test__") and listed.endswith(".cbz")
#                           or listed.startswith("tmp")]
#         for file in leftover_files:
#             os.remove(file)
#         self.test_files_names = []
#         print("\n", self._testMethodName)
#         print("Setup:")
#         self.random_int = random.random() + random.randint(1, 40)
#         for ai in range(3):
#             out_tmp_zipname = f"Test__{ai}_{random.randint(1, 6000)}.cbz"
#             self.test_files_names.append(out_tmp_zipname)
#             self.temp_folder = tempfile.mkdtemp()
#             print(f"    Creating: {out_tmp_zipname}")  # , self._testMethodName)
#             # Create a random int so the values in the cinfo are unique each test
#
#             with zipfile.ZipFile(out_tmp_zipname, "w") as zf:
#                 for i in range(5):
#                     image = Image.new('RGB', size=(20, 20), color=(255, 73, 95))
#                     image.format = "JPEG"
#                     # file = tempfile.NamedTemporaryFile(suffix=f'.jpg', prefix=str(i).zfill(3), dir=self.temp_folder)
#                     imgByteArr = io.BytesIO()
#                     image.save(imgByteArr, format=image.format)
#                     imgByteArr = imgByteArr.getvalue()
#                     zf.writestr(os.path.basename(f"{str(i).zfill(3)}.jpg"), imgByteArr)
#             self.initial_dir_count = len(os.listdir(os.getcwd()))
#
#     def tearDown(self) -> None:
#         print("Teardown:")
#         for filename in self.test_files_names:
#             print(f"    Deleting: {filename}")  # , self._testMethodName)
#             try:
#                 os.remove(filename)
#             except Exception as e:
#                 print(e)
#
#     def test_processing_should_convert_to_webp(self):
#         file_name = self.test_files_names[0]
#         loaded_cinfo = LoadedComicInfo(file_name).load_cover_info()
#         loaded_cinfo.convert_to_webp()
#
#         with zipfile.ZipFile(file_name, "r") as zf:
#             for filename in zf.namelist():
#                 with zf.open(filename) as imagebytes:
#                     image = Image.open(imagebytes)
#                     self.assertEqual("WEBP", image.format)


# if __name__ == '__main__':
#     unittest.main()
