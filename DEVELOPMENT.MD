
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

# QuickGuides
## Adding a setting

### Is this a main app/default setting?

If so go into src.Settings.SettingsDefault and add it there.

Say i want to add a toggle to enable darkmode

I add the key i'll use under Main section. `{"darkmode_enabled":False}` I want it opt-in so i set it to False
Lets add the setting in the settings menu. Head to src.MetadataManager.GUI.windows.SettingsWindow. Add your key in the corresponding section using the SettingControl of your choosing. In my case its a boolean. So SettingControlType.Bool