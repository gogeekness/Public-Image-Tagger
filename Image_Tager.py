#!/usr/bin/env python3
# This is to help speed up image tagging in creating a push button
# tagger for my images
# Richard Eseke 2020, 2024

import sys
if sys.version_info[0] >= 3:
    import PySimpleGUI as sg
else:
    import PySimpleGUI27 as sg
from PIL import Image, ImageTk
import piexif
from TagMasterLightList import TaggerList, SpecialList

import os
import io

#### Global Var Lists
menu_def = [['&File', ['&Open', '&Save', 'E&xit', 'Properties']],
            ['&Help', '&About...'], ]
radio_list = ['RAD0', 'RAD1', 'RAD2', 'RAD3', 'RAD4', 'RAD5']

### Sorting Tag list alphebetacaly
TaggerList.sort()
TaggerList.append("<end>")
SpecialList.sort()

BaseTag = Filenames = []
ImageSize = (640,800) #(1440, 920)

## ExIF keys for JPEG images 
KeyValue = 40094    #  ExIF key for KeyWords in Windows
KeyRating = 18246   #  ExIF key for rating in Windows
PerRating = 18249   #  ExIF Percentage rating
ImageWxif = 256     #  ExIF key for image width
ImageHxif = 257     #  ExIF key for image hight
BlankTag = {'0th': {18246: 0, 18249: 0, 40094: (65, 0)}, 'Exif': {}, 'GPS': {}, 'Interop': {}, '1st': {}, 'thumbnail': None}

## Starting ExIF vaules
ImgHeight = 0
ImgWidth = 0
Nullth = '0th'
KeyStr = "XPKeywords"
exifDataRaw = {}
ExtRating = 0  # temporary value
image_idx = 1 # default start of impage index

# Directory Tags
DirTags = set()
DirHold = False


#### ----------------------------------------------------------------------------------------------------
#### Inital starting proccess to setup needed variables and values

### Get the folder containin:g the images from the user
sg.theme('Dark Red')

ImagePath = 'C:/user/Images/'  # inital value, can be overidden  
try: 
    flist0 = os.listdir(ImagePath)
except FileNotFoundError:
    # if no default, pop up windows to get starting dir, default not needed abandon in place
    ImagePath = sg.PopupGetFolder('Image folder to open', default_path='C:/user/Images/', )
    Browsed = True
    try: 
        flist0 = os.listdir(ImagePath)  # get list of files in new folder
    except FileNotFoundError:  #  if the 2nd time, then fail out 
        sg.Popup('No files in folder ', ImagePath)
        raise SystemExit()    
    
#### PIL supported image types
img_types = ("jpg", "jpeg", 'tiff')

#### create sub list of image files (no sub folders, no wrong file types)
Filenames = [f for f in flist0 if os.path.isfile(os.path.join(ImagePath, f)) and f.lower().endswith(img_types)]

### number of images found in directory
##
num_files = len(Filenames)                
if num_files == 0:
    sg.Popup('No files in folder ', ImagePath)
    raise SystemExit()

## split the list of tags equally into 4 sub-columns
def Split_tags(Taglists):
    ListInterval = len(TaggerList)//4
    rem = len(TaggerList) % 4
    
    ## set each string in Tagger list to only 30 chars, padding or cut where needed.
    # for idx, Taggros in enumerate(TaggerList):
    #      TaggerList[idx] = Taggros.ljust(30)[:30]

    
    ## Split the list into 4 equal parts     
    TagColLists = [TaggerList[i * ListInterval + min(i, rem):(i + 1) * ListInterval + min(i + 1, rem)] for i in range(4)] 
    Tags1 = TaggerList[:ListInterval]
    Tags2 = TaggerList[ListInterval:ListInterval*2-1]
    Tags3 = TaggerList[ListInterval*2:ListInterval*3-1]
    Tags4 = TaggerList[ListInterval*3:-1]
    return TagColLists



#### Event functions =====================================================================================
###  

def get_file_list(ImagePath):
    FileList = os.listdir(ImagePath)
    LocFilenames = [f for f in FileList if os.path.isfile(os.path.join(ImagePath, f)) and f.lower().endswith(img_types)]
    return LocFilenames

## Get image data from file and set for image pane in the application window
def get_img_data(f, maxsize = ImageSize, first = False):
    global ImgWidth, ImgHeight
    try:
        img = Image.open(f)
        ImgWidth, ImgHeight = img.size
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
    except ValueError:
        print("Error no", Nullth, "Data:", exifDataRaw)
        print("Dump 0th:", piexif.dump(BlankTag))
        piexif.insert(piexif.dump(BlankTag), pathname + '\\' + filename)
        return ""
    return ""
        
### Fetch all of the tags in a directory.
##  Get the file list and then iterate over each file fetching the tags
##  Append the list wiht the tags from the file         
def PullDirTags(pathname):
    global exifDataRaw, DirHold, DirTags
    DirList = get_file_list(pathname)
    ## For progress bar 0 to 100
    
    ## Is there any files 
    if len(DirList) < 1:
        return []

    DirIncrament = 1/(len(DirList) / 100)
    DirProgress = 0
    
    if not DirHold:
        DirTags = set()     
    
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
def PushTags(pathname, filename, ListTag):
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
        exifDataRaw[Nullth][KeyRating] = GetRadio()
        exifDataRaw[Nullth][PerRating] = 20 * GetRadio()
        try:
            ByteExif = piexif.dump(exifDataRaw)
            piexif.insert(ByteExif, pathname + '\\' + filename)
        except Exception:
            print("Error Data not JPG can not save EXIF data")
    else:
        print("No Exif Data")

### print out the tages as a text box below the file 
def ShowImageTags(TagStr):
    InterList = []
    global window
    if TagStr != None:
            for Tag in TaggerList:
                if str(Tag) in TagStr:
                    InterList.append(str(Tag))
                    window.Element(str(Tag)).Update(value=True)

### On image change clear the tags str
def ImageTagsClear():
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
def GetRadio():
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



#### Layout sets ===============================================
##   make these 2 elements outside the layout as we want to "update" them later
##   initialize to the first file in the list

## name of first file in list
filename = os.path.join(ImagePath, Filenames[0]) 

## Display emement 
image_elem = sg.Image(data = get_img_data(filename, first = True))

### Image display with text
##
col_image = [[image_elem]]
# ImageNameText = sg.Text(Filenames[0], size=(30, 1), justification='left',  relief='sunken', auto_size_text=True)

###     2ND COLUMN
##      Broken into 4 sub-columns of tags 
Tags1, Tags2, Tags3, Tags4 = Split_tags(TaggerList)

column1 = [[CheckBoxButton(Tags1[i])] for i in range(len(Tags1))]
column2 = [[CheckBoxButton(Tags2[i])] for i in range(len(Tags2))]
column3 = [[CheckBoxButton(Tags3[i])] for i in range(len(Tags3))]
column4 = [[CheckBoxButton(Tags4[i])] for i in range(len(Tags4)-1)]  ## remove <end> from tags

### Frame for the 4 columns for the Tags
##
Tag_List_Frame = [[sg.Frame('Tag List', [[
    sg.Column(column1), sg.Column(column2),
    sg.Column(column3), sg.Column(column4) ]], border_width=2) ]]

###     3rd COLUMN ####
##      Base command buttons for files and tag buttons
TagButtons = [sg.Button(('Save Image'), size=(10, 2)), sg.Button(('Clear Boxes'), size= (10, 2)), sg.Button(('Hold Boxes'), size= (10, 2))]

##      Tag Button section
##      Contains the speciallized tags.
BoxListButtons = [[sg.Button(('Add Tag'), size=(8, 2)), sg.Button(('Clear Tag'), size=(8, 2))], 
                  [sg.Checkbox(('Special Tag\nSelected'), key='TagSpecial', default=False, size=(12,12))]]

file_num_display_elem = sg.Text('File 1 of {}'.format(num_files),)
##      Display list of the image files in this directory
##      + control buttons and checkbox for hold 
col_files = [[sg.Listbox(values=Filenames, change_submits=True, size=(40, 40), key='listbox')], 
             [sg.Text(str(str(image_idx + 1) + ' of '), key='FileNumIndex'), sg.Text(str(str(num_files)),  size=(20,1), key = 'DirFileTotal') ],  
             [sg.Button(('Save Image'), size=(10, 2)) ] 
            ]


###     Image and < > buttons
##      Make a shared control and display for editor
col_image = [[sg.Column(col_image, size=ImageSize)]]
  
### Set Image Column with <> buttons, and image, with tags and size
##
###     BOTTOM OF WINDOW
##      Image width text boxes, display data as well
Image_set = [[sg.Button(('◄'), size=(3, 50), key='<'), sg.Column(col_image), 
                sg.Button(('►'), size=(3, 50), key='>')], 
             ## list out tats
             [sg.Text('Tags:', size=(6, 1)), sg.Text( str( PullTags(ImagePath, Filenames[0])), size=(80,1), key='TextTag')],
            ## get filename
             [sg.Text(str('File: ' + filename), size=(45, 1), justification='left',  relief='sunken', auto_size_text=True, key='FileNameLabel'), 
            ## get image dimentions 
              sg.Text('Image Width:', size=(10, 1), justification='right', font=("Helvetica", 10)), sg.Text(text=ImgWidth, size=(4, 1), key='upWidth', relief='sunken'), 
              sg.Text('Height:', size=(5, 1),  justification='right'), sg.Text(text=ImgHeight, size=(4, 1), key='upHeight', relief='sunken')]
             ] 


#### =========================================================================================
###     Tab #1 (Tagger) layout
tab1_taglists = [[sg.Text('Main Tab')],
        [sg.Column(Tag_List_Frame)],
        [sg.Radio('Star 5', "RadStr", size=(7, 1), key='RAD5'), 
            sg.Radio('Star 4', "RadStr", size=(7, 1), key='RAD4'),
            sg.Radio('Star 3', "RadStr", size=(7, 1), key='RAD3'),
            sg.Radio('Star 2', "RadStr", size=(7, 1), key='RAD2'),
            sg.Radio('Star 1', "RadStr", size=(7, 1), key='RAD1'),
            sg.Radio('No Star', "RadStr", size=(7, 1), key='RAD0', default=True)],
        [sg.Button(('Clear\nBoxes'), size=(6, 2),key='Clear Boxes'), sg.Button(('Hold\nBoxes'), size=(6, 2), key='Hold Boxes'), sg.Checkbox(('Boxes\nHeld'), key='TagHold', default=False, size=(12,12))], 
        [sg.HorizontalSeparator()],
        [sg.Listbox(values=SpecialList, size=(30, 8), key='proplist', select_mode="LISTBOX_SELECT_MODE_SINGLE", enable_events=True), 
         sg.Column(BoxListButtons) ]     
    ]   

###     Tab #1 (Directory Reader)
tab2_reader = [
        [sg.Text('Reader Tab')],
        [sg.Text(str('File :' +  filename), size=(80,1), key='ReaderTextTag')],
        [sg.Text('Tags:', size=(15, 4)),
        sg.Text(str(PullTags(ImagePath, Filenames[0])), enable_events=True, text_color = 'Black', background_color = 'White', key = 'single_tag_reader', 
                size=(60, 4), border_width = 2, justification = 'left')],
        [sg.HorizontalSeparator()],
        [sg.Button(('Tag Directory'), size=(12, 2), key='DirectoryTag'), sg.Button(('Hold Directory Tags'), size=(16, 2), key='HoldDirectoryTag'), 
         sg.Button(('Clear Directory Directory'), size=(12, 2), key='DirectoryTagClear'), sg.Checkbox(('Tags\nHeld'), key='DirTagHold', default=False, size=(12,12))],
        [sg.Text('Directory Tags:', size=(15, 4)), 
         sg.Multiline(str(""), enable_events=True, text_color = 'Black', background_color = 'White', key = 'DirTagsBox', size=(67, 20), border_width = 2, justification = 'left')],
        [sg.Text('Directory Progress :', size=(15, 4)), sg.ProgressBar(100, orientation='h', expand_x=True, size=(60, 10),  key='PBAR')] 
    ]

### Main layout for Tab-grouping
##
tab_group = [[sg.TabGroup([[
    sg.Tab('Tag Lists', tab1_taglists), 
    sg.Tab('Reader Control',tab2_reader)
        ]], border_width=2)       
    ]]

###     Tab #2 layout
layout = [
    ## Title and top controls bar
    [sg.Text('Image Tagger', size=(30, 1), justification='center', font=("Helvetica", 25), relief=sg.RELIEF_RIDGE), 
     sg.Text('Your Folder', size=(15, 1), justification='right'), sg.InputText(ImagePath), sg.FolderBrowse('BrowseDir'),
     sg.Button(('Go'), size=(4,1)), sg.Button(('Exit'), size=(16,2))
     ],
    ## Columns List
    [sg.Column(Image_set), sg.VerticalSeparator(), sg.Column(tab_group), sg.VerticalSeparator(), sg.Column(col_files)]
      # file list and controls    
]

### Main ========================================================================================
##
##
def main():
    Running = True
    Hold = False
    ExtRating = 0
    ImageName = ListTag = ""
    HoldList = []


    global ImagePath, Filenames, window, values, ProperListNames, Browsed, image_idx, DirHold, num_files
    NewDirPath = ImagePath  ## set for default
    Browsed = False

    window = sg.Window('Image Tagger', layout, return_keyboard_events=True,
                       location=(0, 0), use_default_focus=False)

### Main update loop for tagger
##
    while Running == True:
        # Interlist = []
        event, values = window.read()
        Filenames = get_file_list(ImagePath)

        if event is None:
            ## nothing to do
            break
    
### Commit to new directory
        elif event == 'Go':
            ImagePath = values[0]  # get browse str
            image_idx = 0          # set to 0 for new dir
            Filenames = get_file_list(ImagePath)
            window.Element('listbox').Update(Filenames)
            # window.Element('listbox').Update(file_num_display_elem)
            filename = Filenames[0]
            num_files = len(Filenames)
            Browsed = False
            ImageTagsClear()

        elif event == 'BrowseDir':
            ImagePath = values[0]  # get browse str
            image_idx = 0          # set to 0 for new dir
            Filenames = get_file_list(ImagePath) 
            window.Element('listbox').Update(Filenames)
            NewDirPath = ImagePath
            Browsed = False
            ImageTagsClear()
            
### Input events (cursour keys, mouse wheel, and < > buttons)
##  
### Mouse and control buttons         
        elif event in ('>', 'MouseWheel:Down', 'Down:40', 'Next:34') and image_idx < (num_files-1):
            ## if > or change image file then change the image index by adding 1
            image_idx += 1
            filename = Filenames[image_idx]
            if not Hold:
                ImageTagsClear()
        elif event in ('<', 'MouseWheel:Up',  'Up:38', 'Prior:33') and image_idx >= 1:
            ## if < or change image file then change the image index by subtrcting 1
            image_idx -= 1
            filename = Filenames[image_idx]
            if not Hold:
                ImageTagsClear()
                
### Mouse select for the file list box
        elif event == 'listbox':
            imagef = values["listbox"][0]
            ImageName = os.path.join(ImagePath, imagef)   ## get new image fileaname
            image_idx = Filenames.index(imagef)
            filename = Filenames[image_idx]
            if not Hold:
                ImageTagsClear()


### Hold the tages and add them to the tags from the new image
##  To allow tagging of simular images much quicker
##
### Hold for tagging each image
        elif event == 'Hold Boxes':
            Hold = True
            if len(HoldList) > len(TaggerList):
                HoldList = []
            for LookChk in (TaggerList[:-1]):
                HoldList.append(values[LookChk])
            try:
                window.Element('TagHold').Update(value=True)
            except IndexError:
                print("No tag selected.")
                
### Release hold update chcekbox
        elif event == 'Clear Boxes':
            Hold = False
            HoldList = []
            window.Element('TagHold').Update(value=False)
            ImageTagsClear()


### Hold the directory tags and add them for the next directory.
##  To allow build a list for many directories
##
        elif event == 'DirectoryTag':            
            window.Element('DirTagsBox').update(PullDirTags(ImagePath))
        
### Hold to append the directory string      
        elif event == 'HoldDirectoryTag':
            DirHold = True
            try:
                window.Element('DirTagHold').Update(value=True)
            except IndexError:
                print("No tag selected.")

### Release the append hold
        elif event == 'DirectoryTagClear':    
            DirHold = False   
            try:
                window.Element('DirTagHold').Update(value=False)
            except IndexError:
                print("No tag selected.")                        


### Save file (Update image with new tags)            
        elif event == 'Save Image':
            PushTags(ImagePath, Filenames[image_idx], ListTag)
        elif event == 'Add Tag':
            TupIndex = window['proplist'].get_indexes()
            try:
                ListTag = SpecialList[TupIndex[0]] + ";"
                window.Element('TagSpecial').Update(value=True)
            except IndexError:
                print("No special tag selected.")
                
### Clear the selected tags from the main tabgroup
        elif event == 'Clear Tag':
            window.Element('TagSpecial').Update(value=False)
            ListTag = ""
            
### Exit the application 
        elif event == 'Exit':
            Running = False
        else:
            pass
        
### ================================================================================================
### Update image if needed
        ShowImageTags(PullTags(ImagePath, Filenames[image_idx]))
        ImageName = os.path.join(ImagePath, Filenames[image_idx])
        image_elem.Update(data=get_img_data(ImageName))
        
        window.Element('upWidth').update(ImgWidth)
        window.Element('upHeight').update(ImgHeight)
        window.Element('TextTag').Update(PullTags(ImagePath, Filenames[image_idx]))    
        window.Element('single_tag_reader').update(PullTags(ImagePath, Filenames[image_idx]))
        window.Element('DirFileTotal').update(len(Filenames))
        window.Element('FileNumIndex').update(str( image_idx ) + ' of ')
        
        ## Edge case if exiting with out doing anything
        # Is filename defined, then add blank. (The update will show 'blank' on exit)
        try:
            window.Element('FileNameLabel').update(filename)
        except UnboundLocalError:
            window.Element('FileNameLabel').update('Blank')
        # Is filename for tag read defined, then add blank.            
        try:
            window.Element('ReaderTextTag').update('File :' +  filename)
        except UnboundLocalError:
            window.Element('ReaderTextTag').update('File :' +  str('Blank'))

### Update Rating Radio buttons
        ExtRating = PullRating(ImagePath, Filenames[image_idx])
        # Key = RAD[0 5]
        for i in range(len(radio_list)):
            if i == ExtRating:
                #RadTag = 'RAD' + str(i)
                window.Element('RAD' + str(i)).Update(value=True)
                break
            else:
                window.Element('RAD' + str(i)).Update(value=False)

        #ImageNameText.Update(ImageName)
        #file_num_display_elem.Update('File {} of {}'.format(image_idx+1, num_files ))


#### This is the main_init
if __name__=='__main__':
    main()

### Ende