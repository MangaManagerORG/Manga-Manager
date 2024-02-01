## 1.0.0-beta.1

### Features

* Select multiple files and preview the covers of each file.
* Select a folder and open files recursively 
* Choose the files you want to change metadata (without needing to open again) Just click and edit!
* Bulk edit metadata for all files at once
* Changes are kept in one session. You can edit a single file, edit a different one and edit again without needing to save/write the files each time.
* Apply all changes (save to file) all at once when you are done editing.
* Edit cover or backcover from the metadata view itself. Append, replace, or delete.
* Cover manager to batch edit covers (the old cover manager but improved significantly)
* Online Metadata scraping
* Webp converter
* Errors and warnings log inside the UI itself!


## 0.4.6

### Features

* Added settings button in main menu
* Added .bmp support to webp converter (previously it skipped it)

### Fixed

* A bug in docker that wouldn't select files
* Handled exception when no cover is selected and process is clicked
* Re-encode to UTF-8 if file encoding is wrong reading ComicInfo.xml
* Keep original file if recompressed one is bigger. Closes #106
* Skip image if recompress fails. Closes #115