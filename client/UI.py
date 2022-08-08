#!/bin/python
import glob
import os
import re
import time
import pickle
import cv2
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import Frame
from PIL import ImageTk, Image
import tkinter.filedialog as tkfd
import Editor

input_video_path_local = ''
input_dataset_path_local = ''
save_path_local = ''

WITH_QT = False
try:
    cv2.namedWindow('Test')
    cv2.displayOverlay('Test', 'Test QT', 500)
    WITH_QT = True
except cv2.error:	
    print('loading images')
cv2.destroyAllWindows()

# OpenCV
class_index = 0
img_index = 0
img = None
img_objects = []

# set later
frame = 2830
mode = 0
playing = 0
INPUT_DIR  = "temp"
WINDOW_NAME    = 'AutoZAIC'
TRACKBAR_IMG   = 'frame'
TRACKBAR_SPEED   = 'speed'
TRACKBAR_TOL   = 'tolerance'

# tkinter parameters
white = "#ffffff"
lightBlue2 = "#ffffff"
font = "consolas"
fontButtons = (font, 10)
maxWidth = 400
maxHeight = 200

#tkinter graphics window
mainWindow = tk.Tk()
mainWindow.configure(bg=lightBlue2)
mainWindow.title("AutoZAIC")
mainWindow.geometry('%dx%d+%d+%d' % (maxWidth, maxHeight, 0, 0))
mainWindow.resizable(0, 0)
logo = Image.open("autozaic.jpg")
logo = logo.resize((150, 150), 0)
img = ImageTk.PhotoImage(logo)

mainFrame = Frame(mainWindow)
mainFrame.place(x= 100, y=100)


# tkinter file explorer
def file_directory():
    input_video_path_local = tkfd.askdirectory()
    print(input_dataset_path_local)

def file_video():
    input_dataset_path_local = tkfd.askopenfilename(initialdir="/", title="Select file ",
                         filetypes=(("mp4 files", ".mp4"),("all files", ".")))
    print(input_video_path_local)

def insert_details():
    # dataset
    imageBtn = Button(mainWindow, text="Select Dataset ...", font=fontButtons, command=file_directory)
    imageBtn.place(x=220, y=30)

    # video
    imageBtn = Button(mainWindow, text="Select Video ...", font=fontButtons, command=file_video)
    imageBtn.place(x=220, y=70)

    # save location
    imageBtn = Button(mainWindow, text="Save here ...", font=fontButtons, command=file_directory)
    imageBtn.place(x=220, y=110)

    # Close
    closeButton = Button(mainWindow, text="CLOSE", font=fontButtons, width=10, height=1)
    closeButton.configure(command=lambda:mainWindow.destroy())
    closeButton.place(x=220, y=150)
    
	#Logo
    canvas = Canvas(mainWindow, width=180, height=180, bg=white)
    canvas.place(x=20, y=8)
    canvas.create_image(20, 20, anchor=NW, image=img)

# selected bounding box
prev_was_double_click = False
is_bbox_selected = False
selected_bbox = -1
LINE_THICKNESS = 1

mouse_x = 0
mouse_y = 0
point_1 = (-1, -1)
point_2 = (-1, -1)

'''
    0,0 ------> x (width)
     |
     |  (Left,Top)
     |      *_________
     |      |         |
            |         |
     y      |_________|
  (height)            *
                (Right,Bottom)
'''
#bring list of image path from main
def setImgPL(p, f):
    global IMAGE_PATH_LIST
    IMAGE_PATH_LIST = p
    global frame
    frame = f

# Check if a point belongs to a rectangle
def pointInRect(pX, pY, rX_left, rY_top, rX_right, rY_bottom):
    return rX_left <= pX <= rX_right and rY_top <= pY <= rY_bottom

#bring editor from main
def setEditor(e):
    global editor
    editor = e


def display_text(text, time):
    if WITH_QT:
        cv2.displayOverlay(WINDOW_NAME, text, time)
    else:
        print(text)

def setlasti(i):
    global last_img_index 
    last_img_index = i

#set img index and bring corresponding image
def set_img_index(x):
    global img_index, img
    img_index = x
    img_path = IMAGE_PATH_LIST[mode][img_index]
    img = cv2.imread(img_path)

#set speed index and set trackbar position accordingly
def set_speed_index(x):
    global speed_index
    if x == 0:
        x = 1
        text = 'Speed of 1/0 not allowed'
        display_text(text, 1000)
        setTrackbarPos(TRACKBAR_SPEED, WINDOW_NAME, x)
        return
    if x == 1000:
        speed_index = 0
        return
    speed_index = 1/x

def set_class_index(x):
    global class_index
    class_index = x

def decrease_index(current_index, last_index, mode):
    current_index -= 1
    if current_index < 0:
        current_index = last_index
    return current_index

def increase_index(current_index, last_index, mode):
    current_index += 1
    if current_index > last_index:
        current_index = 0
    return current_index

def draw_line(img, x, y, height, width, color):
    cv2.line(img, (x, 0), (x, height), color, LINE_THICKNESS)
    cv2.line(img, (0, y), (width, y), color, LINE_THICKNESS)
 
# mouse callback function
def mouse_listener(event, x, y, flags, param):
    global is_bbox_selected, prev_was_double_click, mouse_x, mouse_y, point_1, point_2

    if event == cv2.EVENT_MOUSEMOVE:
        #set x, y according to mouse position
		mouse_x = x
        mouse_y = y
    elif event == cv2.EVENT_LBUTTONDBLCLK:
		#left double click
        prev_was_double_click = True
        point_1 = (x,y)
		#send position coordinates to editor.py
        if editor.edit(img_index, point_1[0], point_1[1], point_2[0], point_2[1]):
            set_img_index(img_index)
            tmp_img = img.copy()
            cv2.imshow(WINDOW_NAME, tmp_img)
        point_1 = (-1, -1)
    elif event == cv2.EVENT_LBUTTONDOWN:
        if prev_was_double_click:
            # double click finished
            prev_was_double_click = False
        else:
            # left click
            if point_1[0] is -1:
                if is_bbox_selected:
                    if is_mouse_inside_delete_button():
                        edit_bbox(obj_to_edit, 'delete')
                    is_bbox_selected = False
                else:
                    # first click (start drawing a bounding box or delete an item)
                    point_1 = (x, y)
            else:
                # minimal size for bounding box to avoid errors
                threshold = 5
                if abs(x - point_1[0]) > threshold or abs(y - point_1[1]) > threshold:
                    # second click
                    point_2 = (x, y)   
#take txt file and convert
def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    return [int(text) if text.isdigit() else text.lower()
            for text in _nsre.split(s)]

def nonblank_lines(f):
    for l in f:
        line = l.rstrip()
        if line:
            yield line

#return color
def complement_bgr(color):
    lo = min(color)
    hi = max(color)
    k = lo + hi
    return tuple(k - u for u in color)

def setlci(i, c):
    global last_class_index
    last_class_index = i
    global CLASS_LIST
    CLASS_LIST = c

#enter given file directory use recursion on each directory element and load each image filepath into list.
def search_filedir(directory, m):
    tmp = directory
    for f in sorted(os.listdir(tmp), key = natural_sort_key):
        f_path = os.path.join(tmp, f)
        if os.path.isdir(f_path):
            # if directory
            m += 1
            search_filedir(f_path, m)
            continue
        # check if it is an image
        test_img = cv2.imread(f_path)

        if test_img is not None:
            IMAGE_PATH_LIST[m].append(f_path)

# change to the directory of this script
os.chdir(os.path.dirname(os.path.abspath(__file__)))
