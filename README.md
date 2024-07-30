# Image-Tagger
This is a Python-based Image Tagger for Windows XPKeywords

This Application uses a simple GUI to change the meta-tags for JPG images.
These tags are embedded into the image.

Requirements:
* `import sys, os, io`
* A check for versioning in PySimple Gui whem importing
```
  if sys.version_info[0] >= 3:
      import PySimpleGUI as sg
  else:
      import PySimpleGUI27 as sg
```
* `from PIL import Image, ImageTk`
* `import piexif`
* `from TagMasterLightList import TaggerList, SpecialList (your own data file)`


The goal of this application is to quickly read and update JPG images with their built-in meta-tags.  The app will read a directory of files (images). 

The window is split into 3 columns/frames. 
1) Shows the image being tagged and forward and back buttons ('<' '>')
2) [This will be tabbed to add more functions] The tag list The tags that can be selected and controls for special tags and tag "holding" (keeping the current selected tags for the next image.  This is an additive process nothing will be refreshed as different images are picked.)
3) The folder list shows all or a large portion of the files in the current folder.  There is placement information as well.


The Image-Tagger main page and main tab
![Capture_Tagger2_001](https://github.com/user-attachments/assets/95beb3b9-7e8e-4fd7-8f7e-da68d2abe251)


This is the main window with 4 sections.
* Top row
* *  Title
  *  The actve folder
  *  The button to browse to a new folder
  *  The 'Go' or commit to the selected folder
  *  Exit
* Left side
* * Two tall button to move forwared and back
  * The active image
  * A list of tags for that image
  * The file name and it's dimentions
* Central tab group
  * The Tag List tab
    * The active Tag list in checkboxes
    * The image rating
    * Clear boxes (Clear checkboxes)
    * Hold boxes (Hold the current checkboxes to add to newly loaded image)
    * A check box to show if the 'Hold Boxes' function is active
* Right side
  * File list of the active folder
    * Fully selectable
    * File number and total number of image files in the folder
    * Save Image
      * This will save the updated tags and rating (appending the new tags)
  * Specialty tags, only one per imgage (For artists, and unique tags)
  * Add tag (specialty), Clear tag, and specialty tag indicator      


The Image-Tagger Tagger tab
![Capture_Tagger2_002](https://github.com/user-attachments/assets/c2cc3fd4-cbb2-413a-b721-87c6ab9b5594)



* The Reader tab
  * Show the active file
  * Show the tags for the active file
  * Tag Directory (folder)
  * Directory tags show all of the unique tags for the folder
  * The progress line when tagging the direcory (This can take minuets for large directory with thousands of images)
