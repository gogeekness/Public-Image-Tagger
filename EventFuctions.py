#!/usr/bin/env python3
# This is to help speed up image tagging in creating a push button
# tagger for my images
# Richard Eseke 2020, 2024

import os, sys, io
import piexif, struct

from InitVars import ImageSize, radio_list, img_types, ImgHeight, ImgWidth

from Image_Tager_List import TaggerList, SpecialList
from PIL import Image, ImageTk

if sys.version_info[0] >= 3:
    import PySimpleGUI as sg
else:
    import PySimpleGUI27 as sg

#### Event functions variables ==========================================================================
###  

## ExIF keys for JPEG images 
KeyValue = 40094    #  ExIF key for KeyWords in Windows
KeyRating = 18246   #  ExIF key for rating in Windows
PerRating = 18249   #  ExIF Percentage rating
ImageWxif = 256     #  ExIF key for image width
ImageHxif = 257     #  ExIF key for image hight
BlankTag = {'0th': {18246: 0, 18249: 0, 40094: (65, 0)}, 'Exif': {}, 'GPS': {}, 'Interop': {}, '1st': {}, 'thumbnail': None}
Nullth = '0th'

menu_def = [['&File', ['&Open', '&Save', 'E&xit', 'Properties']],
            ['&Help', '&About...'], ]

#### Event functions =====================================================================================
### split the list of tags equally into N (splits) sub-columns  (supporter function)
##
def SplitTags(Taglists, splits):
    SubList, remander = divmod( len(TaggerList), splits)
    SubTags =  [Taglists[i * SubList + min(i, remander):(i+1)*SubList + min(i+1, remander)] for i in range(splits)]
    return SubTags

### Fetch files from directory
def GetFileList(ImagePath):
    FileList = os.listdir(ImagePath)
    LocFilenames = [f for f in FileList if os.path.isfile(os.path.join(ImagePath, f)) and f.lower().endswith(img_types)]
    return LocFilenames

## Get image data from file and set for image pane in the application window
def GetImgData(f, maxsize = ImageSize, first = False, ImgSizeOnly = False):
    try:
        img = Image.open(f)
        if ImgSizeOnly:
            ImgWidth, ImgHeight = img.size
            return ImgWidth, ImgHeight
        img.thumbnail(maxsize)
    except OSError:
        print("OS Error", OSError, "  First ", first)
        return None
    ## need to active and set image for the first time
    if first:                     # tkinter is inactive the first time
        bio = io.BytesIO()
        img.save(bio, format = "PNG")
        del img
        return bio.getvalue()
    return ImageTk.PhotoImage(img)

### Fetch and Push TAGS

### Fetch the metatags from the image file.
##  The processes the binary data from specific keys (for Windows) and fetches the values.
##  Add those values to a str to be returned
def PullTags(pathname, filename):
    global exifDataRaw
    try:
        exifDataRaw = piexif.load(pathname + '\\' + filename) 
        if exifDataRaw[Nullth]:
            if KeyValue in exifDataRaw[Nullth]:
                TagOutput = str(bytes(exifDataRaw[Nullth][KeyValue]).decode('utf_16_le'))#[:-1]
                return str(TagOutput)
    except struct.error as err:
        print("Strut Error on loading ", filename, " Error ", err )
        return ""
    except ValueError:
        print("Error no", Nullth, "Data:", exifDataRaw)
        print("Dump 0th:", piexif.dump(BlankTag))
        piexif.insert(piexif.dump(BlankTag), pathname + '\\' + filename)
        return ""
    return ""
        
### Fetch all of the tags in a directory.
##  Get the file list and then iterate over each file fetching the tags
##  Append the list wiht the tags from the file         
def PullDirTags(pathname, window, DirTags):
    global exifDataRaw
    DirList = GetFileList(pathname)
    ## For progress bar 0 to 100
    
    ## Is there any files 
    if len(DirList) < 1:
        return []

    DirIncrament = 1/(len(DirList) / 100)
    DirProgress = 0    
    for DirFileName in DirList[:-1]:
        DirProgress += DirIncrament
        try:     
                DirFileTags = PullTags(pathname, DirFileName)
                for tag in DirFileTags.split(';'):      # The file meta-tags are sperated by ; 
                    cleaned_tag = tag.rstrip('\x00')    # Removing '\x00' if it exists, a side effect of the decodeing exif-data
                    DirTags.add(cleaned_tag)
                    if cleaned_tag not in DirTags:      # Test for uniqueness, if so add to maine Directory Tag List
                        DirTags.append(cleaned_tag)
                # DirTags.append(DirFileTags)
                window['PBAR'].update(current_count=int(DirProgress))
        except ValueError:
            print("Error File : ", DirFileName)
            print("Error no : ", Nullth, "Data:", exifDataRaw)
            print("Dump 0th : ", piexif.dump(BlankTag))
            # return list from the set   
    window['PBAR'].update(current_count=0)   
    return list(DirTags)
    
### Push the changes to the metatags to the image
##  The reverse. Convert the str to binary data and insert the new data to the image 
def PushTags(pathname, filename, ListTag, values, window):
    InsertString = ""
    global exifDataRaw
    for Tag in TaggerList[:-1]:
        if values[Tag]:
            InsertString = InsertString + Tag + ";"
    InsertString = ListTag + InsertString
    print("Push string", InsertString)
    #Get whole dataset
    print("Missing ", Nullth, "Data:", exifDataRaw)
    if exifDataRaw:
        exifDataRaw[Nullth][KeyValue] = tuple(InsertString[:-1].encode('utf_16_le'))
        exifDataRaw[Nullth][KeyRating] = GetRadio(window)
        exifDataRaw[Nullth][PerRating] = 20 * GetRadio(window)
        try:
            ByteExif = piexif.dump(exifDataRaw)
            piexif.insert(ByteExif, pathname + '\\' + filename)
        except Exception:
            print("Error Data not JPG can not save EXIF data")
    else:
        print("No Exif Data")

### print out the tages as a text box below the file 
def ShowImageTags(TagStr, window):
    InterList = []
    if TagStr != None:
            for Tag in TaggerList:
                if str(Tag) in TagStr:
                    InterList.append(str(Tag))
                    window.Element(str(Tag)).Update(value=True)

### On image change clear the tags str
def ImageTagsClear(window):
    for Tag in TaggerList[:-1]:
        try:
            window.Element(str(Tag)).Update(value=False)
        except KeyError:
            print("No Key found :", Tag)

### Sent the state of the check box back the main loop.
def CheckBoxButton(BoxText):
    return sg.Checkbox(BoxText, size=(11, 1), default=False, key=(BoxText))

### STARS/RATING  
  
### Fetch the star rating for the image.
##  return an integer back
def GetRadio(window):
    rating = 0
    test = len(radio_list)
    for i in range(len(radio_list)):
        if window.FindElement(radio_list[i]).Get() == True:
            return rating
        rating = rating + 1
    return rating

### Fetch the star rating from the image file as an integer
def PullRating(pathname, filename):
    global exifDataRaw
    exifDataRaw = piexif.load(pathname + '\\' + filename)
    RatingOut = 0
    #print("this if the rating: ", exifDataRaw.get(Nullth, {}).get(KeyRating))
    try:
        if exifDataRaw[Nullth]:
            try:                
                ## fetch rating, execptions on if: there, out of bounds, or can't lookup value 
                RatingOut = exifDataRaw.get(Nullth, {}).get(KeyRating)
            except IndexError:
                print("Key Index Error missing Index: ", filename)
                # RatingOut = 0
            except KeyError:
                print("Key Error with KeyRating, No Key: ", filename)
                # RatingOut = 0
            except LookupError:
                print("Lookup Key error with: KeyRating: ", filename)
                # RatingOut = 0
            return RatingOut
    except ValueError:
        print("Error no", Nullth, "Data:", exifDataRaw)
        return 0
    return 0
