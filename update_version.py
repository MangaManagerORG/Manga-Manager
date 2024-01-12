import os

def update_version_file():
    """Updates the version file with the hash from prev-rev."""
    version_file_path = os.path.join(
        os.path.dirname(__file__), "MangaManager","src", "__version__.py"
    )

    # Read the version file
    with open(version_file_path, "r") as version_file:
        version_data = version_file.read()

    # Get the last commit hash
    branch = os.popen("git rev-parse --abbrev-ref HEAD").read().strip()
    tag = "stable" if branch == "main" else "nightly"
    prev_rev_hash = os.popen("git rev-parse --short HEAD").read().strip()
    version = ":".join(version_data.split(":")[:-2])
    new_hash = prev_rev_hash + '"'
    new_version = ":".join((version, tag, new_hash))

    # Update the version file with the modified data
    with open(version_file_path, "w") as version_file:
        version_file.write(new_version)

if __name__ == '__main__':
    update_version_file()