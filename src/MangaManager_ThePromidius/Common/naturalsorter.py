import pathlib
from natsort import natsort_key
def decompose_path_into_components(x):
    path_split = list(pathlib.Path(x).parts)
    # Remove the final filename component from the path.
    final_component = pathlib.Path(path_split.pop())
    # Split off all the extensions.
    suffixes = final_component.suffixes
    stem = final_component.name.replace(''.join(suffixes), '')
    # Remove the '.' prefix of each extension, and make that
    # final component a list of the stem and each suffix.
    final_component = [stem] + [x[1:] for x in suffixes]
    # Replace the split final filename component.
    path_split.extend(final_component)
    return path_split
def natsort_key_with_path_support(x):
    return tuple(natsort_key(s) for s in decompose_path_into_components(x))


# list_of_files = ['/file_in_root.ext', '/aaaaa/file_in_aaa_folder_1.ext', '/aaaaa/file_in_aaa_folder_2.ext',
#                  '/aaaaa/BBBBB/file_in_BBB_folder_1.ext', "/aaaaa/BBBBB/file_in_BBB_folder_2.ext"]
# if __name__ == '__main__':
#     print(sorted(list_of_files, key=natsort_key_with_path_support,reverse=True))
