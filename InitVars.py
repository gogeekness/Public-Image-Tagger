#!/usr/bin/env python3
# This is to help speed up image tagging in creating a push button
# tagger for my images
# Richard Eseke 2020, 2024

ImageSize = (640,800) #(1440, 920)
radio_list = ['RAD0', 'RAD1', 'RAD2', 'RAD3', 'RAD4', 'RAD5']

#### PIL supported image types
img_types = ("jpg", "jpeg", 'tiff')

## Starting ExIF vaules
ImgHeight = 0
ImgWidth = 0