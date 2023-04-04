
## Versioning and building
When a build is to be made, copy the short hash of last commit and update it in `src/__version__.py`. After that make commit and push the version bump.

After that you can now create the build with the command below

## How to build:
`python -m PyInstaller .\MangaManager.spec --clean`

## Errors building with pyinstaller
If you can not run the build make sure all requirements are installed.
Pyinstaller does not use the virtual env requirements. So make sure the base python has them installed
Some of the requirements that gave me issues are:
- `chardet`