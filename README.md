
# Manga-Manager

Currently it has 2 features

## Set Volume

This option adds Vol.00 to the filename just before Ch/Chapter.
If there is no Ch/Chapter in the file name the script assumes the last digits are the capter indicator. So it will place it before them.

Example

I want to place `Vol.03` to the following filenames
<br>
The wonderful world of invented titles ch3.ext -> The wonderful world of invented titles Vol.03 ch3.ext
<br>
The wonderful world of invented titles ch.3.ext -> The wonderful world of invented titles Vol.03 ch.3.ext
<br>
The wonderful world of invented titles ch 3.ext -> The wonderful world of invented titles Vol.03 ch 3.ext
<br>
The wonderful world of invented titles chapter 3.ext -> The wonderful world of invented titles Vol.03 chapter 3.ext


If either `Ch` or `Chapter` is not present in the file name, the script will asume the last digits as chapter identifier:
<br>
The wonderful world of invented titles 03.ext -> The wonderful world of invented titles Vol.03 03.ext

**Note: there is a confirmation window where you can check everything is correct.**

## Set Cover
This option extracts the selected files -> replaces the cover or adds a new one -> compress back the files.

If there is any file named 000.ext or 001.ext, the script will save it in the file as OldCover0000.ext.back

### Overwrite 0001 or not?
It is as simple as it sounds. 

If you want to replace current 0001.ext image say YES.<br>
If you want to keep current 0001.ext image say NO.

By selecting NO it will add the image you selected as 0000.ext
<br>Then it saves the selected image as 0000.ext
### R
