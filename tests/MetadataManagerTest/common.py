import zipfile


def create_dummy_files(nfiles):
    test_files_names = []
    for i in range(nfiles):
        out_tmp_zipname = f"random_image_{i}_not_image.ext.cbz"
        test_files_names.append(out_tmp_zipname)
        with zipfile.ZipFile(out_tmp_zipname, "w") as zf:
            zf.writestr("Dummyfile.ext", "Dummy")
    return test_files_names