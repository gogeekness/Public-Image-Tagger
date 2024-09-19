
#!/usr/bin/env python3
# This is to help speed up image tagging in creating a push button
# tagger for my images
# Richard Eseke 2020, 2024

import sys, os
if sys.version_info[0] >= 3:
    import PySimpleGUI as sg
else:
    import PySimpleGUI27 as sg

from InitVars import ImageSize, radio_list, img_types, ImgWidth, ImgHeight
from Image_Tager_List import TaggerList, SpecialList

from EventFuctions import  SplitTags, GetFileList, GetImgData, PullTags, PullDirTags, PushTags, ShowImageTags, ImageTagsClear, CheckBoxButton, GetRadio, PullRating


#### Global Var Lists


### Sorting Tag list alphebetacaly
TaggerList.sort()
TaggerList.append("<end>")
SpecialList.sort()

BaseTag = Filenames = []

KeyStr = "XPKeywords"
exifDataRaw = {}
ExtRating = 0  # temporary value
image_idx = 1 # default start of impage index
numsplits = 6

# Directory Tags
DirTags = set()


#### ----------------------------------------------------------------------------------------------------
#### Inital starting proccess to setup needed variables and values

sg.theme('Dark Red')
### Get the folder containin:g the images from the user

ImagePath = 'R:/images/Fresh Images/'  # inital value, can be overidden  
try: 
    flist0 = os.listdir(ImagePath)
except FileNotFoundError:
    # if no default, pop up windows to get starting dir, default not needed abandon in place
    ImagePath = sg.PopupGetFolder('Image folder to open', default_path='R:/images/Fresh Images/', )
    Browsed = True
    try: 
        flist0 = os.listdir(ImagePath)  # get list of files in new folder
    except FileNotFoundError:  #  if the 2nd time, then fail out 
        sg.Popup('No files in folder ', ImagePath)
        raise SystemExit()    


#### create sub list of image files (no sub folders, no wrong file types)
Filenames = [f for f in flist0 if os.path.isfile(os.path.join(ImagePath, f)) and f.lower().endswith(img_types)]

### number of images found in directory
##
num_files = len(Filenames)                
if num_files == 0:
    sg.Popup('No files in folder ', ImagePath)
    raise SystemExit()


#### Layout sets ===============================================
##   make these 2 elements outside the layout as we want to "update" them later
##   initialize to the first file in the list

## name of first file in list
filename = os.path.join(ImagePath, Filenames[0]) 

## Display emement 
image_elem = sg.Image(data = GetImgData(filename, first = True))

### Image display with text
##
col_image = [[image_elem]]
# ImageNameText = sg.Text(Filenames[0], size=(30, 1), justification='left',  relief='sunken', auto_size_text=True)

###     2ND COLUMN
##      Broken into N sub-columns of tags currently numsplits
TagsOverList = SplitTags(TaggerList, numsplits)
Tcolumns = []

for sublist in TagsOverList:
    column = [[sg.Checkbox(tag, key=tag)] for tag in sublist]
    Tcolumns.append(sg.Column(column))

Tag_List_Frame = [[sg.Frame('Tag List', [Tcolumns], border_width=2)]]



###     3rd COLUMN ####
##      Base command buttons for files and tag buttons
TagButtons = [sg.Button(('Save Image'), size=(10, 2)), sg.Button(('Clear Boxes'), size= (10, 2)), sg.Button(('Hold Boxes'), size= (10, 2))]

##      Tag Button section
##      Contains the speciallized tags.
BoxListButtons = [[sg.Button(('Apply Tag'), size=(8, 2)), sg.Button(('Clear Tag'), size=(8, 2))], 
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
        [sg.Text(str('Directoy :' +  ImagePath), size=(80,1), key='ReaderTextTag'),
        sg.Button(('Tag Directory'), size=(12, 2), key='DirectoryTag'), sg.Button(('Hold Directory Tags'), size=(16, 2), key='HoldDirectoryTag'), 
        sg.Button(('Clear Directory Directory'), size=(12, 2), key='DirectoryTagClear'), sg.Checkbox(('Tags\nHeld'), key='DirTagHold', default=False, size=(12,12))],
        [sg.Text('General Tags:', size=(15, 4)), sg.Listbox([ 'test1', 'test2','test3' ], size=(40, 15), select_mode='LISTBOX_SELECT_MODE_MULTIPLE', key='GeneralTagBox' ), 
            sg.Button(('Invert General Tags'), size=(18, 2), key='GeneralTagInv')],
        [sg.HorizontalSeparator()],
        [sg.Text('Custom Tags:', size=(15, 4)), sg.Listbox([ 'test1', 'test2','test3' ], size=(40, 15), select_mode='LISTBOX_SELECT_MODE_MULTIPLE', key='CustomTagBox'  ),
            sg.Button(('Invert Custom Tags'), size=(18, 2), key='CustomTagInv')],
        # sg.Text(str(PullTags(ImagePath, Filenames[0])), enable_events=True, text_color = 'Black', background_color = 'White', key = 'single_tag_reader', 
        #         size=(60, 4), border_width = 2, justification = 'left')],

        # [ 
        # sg.Button(('Clear Directory Directory'), size=(12, 2), key='DirectoryTagClear'), sg.Checkbox(('Tags\nHeld'), key='DirTagHold', default=False, size=(12,12))],
        # [sg.Text('Directory Tags:', size=(15, 4)), 
        #  sg.Multiline(str(""), enable_events=True, text_color = 'Black', background_color = 'White', key = 'DirTagsBox', size=(67, 20), border_width = 2, justification = 'left')],
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
ExitColumn = [[sg.Button(('Exit'),size=(16,2))]]

layout = [
    ## Title and top controls bar
    [sg.Text('Image Tagger', size=(30, 1), justification='center', font=("Helvetica", 25), relief=sg.RELIEF_RIDGE), 
     sg.Text('Your Folder', size=(15, 1), justification='right'), sg.InputText(ImagePath), sg.FolderBrowse('BrowseDir'),
     sg.Button(('Refresh Window'), key='Go', size=(20,1)), sg.Column(ExitColumn, element_justification='right', expand_x=True)
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


    global ImagePath, Filenames, window, ProperListNames, Browsed, image_idx, num_files
    NewDirPath = ImagePath  ## set for default
    Browsed = False

    window = sg.Window('Image Tagger', layout, return_keyboard_events=True,
                       location=(0, 0), use_default_focus=False)

### Main update loop for tagger
##
    while Running == True:
        # Interlist = []
        event, values = window.read()
        Filenames = GetFileList(ImagePath)

        if event is None:
            ## nothing to do
            break
    
### Commit to new directory
        elif event == 'Go':
            ImagePath = values[0]  # get browse str
            image_idx = 0          # set to 0 for new dir
            Filenames = GetFileList(ImagePath)
            window.Element('listbox').Update(Filenames)
            # window.Element('listbox').Update(file_num_display_elem)
            filename = Filenames[0]
            num_files = len(Filenames)
            Browsed = False
            ImageTagsClear(window)

        elif event == 'BrowseDir':
            ImagePath = values[0]  # get browse str
            image_idx = 0          # set to 0 for new dir
            Filenames = GetFileList(ImagePath) 
            window.Element('listbox').Update(Filenames)
            NewDirPath = ImagePath
            Browsed = False
            ImageTagsClear(window)
       
            
### Input events (cursour keys, mouse wheel, and < > buttons)
##  
### Mouse and control buttons         
        elif event in ('>', 'MouseWheel:Down', 'Down:40', 'Next:34') and image_idx < (num_files-1):
            ## if > or change image file then change the image index by adding 1
            image_idx += 1
            filename = Filenames[image_idx]
            if not Hold:
                ImageTagsClear(window)
        elif event in ('<', 'MouseWheel:Up',  'Up:38', 'Prior:33') and image_idx >= 1:
            ## if < or change image file then change the image index by subtrcting 1
            image_idx -= 1
            filename = Filenames[image_idx]
            if not Hold:
                ImageTagsClear(window)
                
### Mouse select for the file list box
        elif event == 'listbox':
            imagef = values["listbox"][0]
            ImageName = os.path.join(ImagePath, imagef)   ## get new image fileaname
            image_idx = Filenames.index(imagef)
            filename = Filenames[image_idx]
            if not Hold:
                ImageTagsClear(window)


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
            ImageTagsClear(window)


### Hold the directory tags and add them for the next directory.
##  To allow build a list for many directories
##
        elif event == 'DirectoryTag':            
            window.Element('GeneralTagBox').update(PullDirTags(ImagePath, window, DirTags))
            window.Element('CustomTagBox').update(PullDirTags(ImagePath, window, DirTags))         
        
### Hold to append the directory string      
        elif event == 'HoldDirectoryTag':
            try:
                window.Element('DirTagHold').Update(value=True)
            except IndexError:
                print("No tag selected.")

### Release the append hold
        elif event == 'DirectoryTagClear':    
            try:
                window.Element('DirTagHold').Update(value=False)
            except IndexError:
                print("No tag selected.")                        


### Save file (Update image with new tags)            
        elif event == 'Save Image':
            PushTags(ImagePath, Filenames[image_idx], ListTag, values, window)
            
        elif event == 'Apply Tag':
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
        ShowImageTags(PullTags(ImagePath, Filenames[image_idx]), window)
        ImageName = os.path.join(ImagePath, Filenames[image_idx])
        image_elem.Update(data=GetImgData(ImageName))
        #filename = ''
        
        ### To fetch teh size info I run the Getdata with only size selected
        ImgWidth, ImgHeight = GetImgData(ImageName, first = False, ImgSizeOnly = True)
        
        window.Element('upWidth').update(ImgWidth)
        window.Element('upHeight').update(ImgHeight)
        window.Element('TextTag').Update(PullTags(ImagePath, Filenames[image_idx]))    
        #window.Element('GeneralTagBox').update(PullTags(ImagePath, Filenames[image_idx]))
        #window.Element('CustomTagBox').update(PullTags(ImagePath, Filenames[image_idx]))

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
