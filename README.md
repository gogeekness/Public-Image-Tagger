# Image-Tagger
This is a Python-based Image Tagger for Windows XPKeywords

This Application uses a simple GUI to change the meta-tags for JPG images.
These tags are embedded into the image.

#### The goal of this application is to quickly read and update JPG images with their built-in meta-tags.  The app will read a directory of files (images). 

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

## InitVars.py 
File containns default and set variables used in the Tagger program.
* `ImageSize` is currently set as (640,800)
* `img_types` set to JGP, JPEG, TIFF
* `DefaultPath` where the Tagger looks for images, otherwise it asks the user for the starting folder.

## Main Screen

The window is split into 3 columns/frames. 
1) Shows the image being tagged and forward and back buttons ('◄' '►') as well as the up and down cursor keys.
2) This will be tabbed to add more functions
   The tag list The tags that can be selected and controls for special tags and tag "holding" (keeping the current selected tags for the next image.  This is an additive process nothing will be refreshed as different images are picked.)
4) The folder list shows all or a large portion of the files in the current folder.  There is placement information as well.


#### The Image-Tagger main page and main tab
![Capture_Tagger2_2001](https://github.com/user-attachments/assets/8fa60ee5-14d3-4d22-bf87-7e795398767d)




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
    * Save Image (Update Tags to Image)
      * This will save the updated tags and rating (appending the new tags)
  * Specialty tags, only one per imgage (For artists, and unique tags)
  * Add tag (specialty), Clear tag, and specialty tag indicator      

### The Tag list

* #### Tag Lists
  * The active Tag list in checkboxes (Showing the tags what will be applied to the image)
  * The image rating  (Microsofts Star rating: 0-5 Stars.)
  * Clear boxes (Clear checkboxes)
  * Hold boxes (Hold the current checkboxes to add to newly loaded image, This can be done across many images as in a series of simular images)
  * A check box to show if the 'Hold Boxes' function is active

### The directory Tag reader
* This tab has controls to read tags for all the images in a directory.
* The 'Tag Directory' button will fetch the tag data from every image in the directory
* 'Hold Directory Tags' button acts simular to the 'hold tag' button, but across directories.
* 'Clear Directory Directory' button clears all tags (Will be fixed to 'Clear Directory Tags')
* The two (2) types of Tags normal and special.  (Note: This is being updated so the final form is unknown)
  * To create tow (2) lists from the directory's tage to create a new MasterTag file.

#### The Image-Tagger Tagger tab
![Capture_Tagger2_002](https://github.com/user-attachments/assets/ce27d57b-4bdb-419e-85ec-8ca6e090e916)


## Plans
* Continue adding to Directory Reader.
  * Create Taglist
  * Load Taglist
  * Save Taglist
* AI vision to tag images automaticly
  * Use standalone AI vision model to tag images automaticaly
  * Create a Taglist
* Adding PNG support

### Note: Update Window before exiting the application. 
