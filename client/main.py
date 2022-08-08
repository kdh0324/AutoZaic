from SSHConnect import *
import Editor
import pickle
import cv2
import os
import shutil
from UI import *
import copy
import UI

# Load file dir. and video
insert_details()
mainWindow.mainloop()  # Starts GUI1
'''
only download detectec face info from server
ssh = SSHConnect("141.223.181.102", 22, "oop8917", "8917")
output_pickle_path_local = "./detected_faces.pickle"
output_pickle_path_remote ="/home/oop8917/minseok/hacksmall_detected_faces.pickle"
ssh.file_download(output_pickle_path_remote, output_pickle_path_local)
'''
'''
total server communication version
#user input
input_video_path_local ="./videos/hacksmall.mp4"
input_dataset_path_local = "./dataset"

input_dataset_path_remote = "/home/oop8917/minseok/"
input_video_path_remote = "/home/oop8917/minseok/videos/hacksmall.mp4"
output_pickle_path_local = "./detected_faces.pickle"
output_pickle_path_remote ="/home/oop8917/minseok/detected_faces.pickle"
print("==========Upload file start==========")
ssh.directory_upload(input_dataset_path_local, input_dataset_path_remote)
ssh.file_upload(input_video_path_local, input_video_path_remote)
print("==========Upload file done===========")

ssh.ssh_execute("pwd;source ~/.bashrc; source cuda9-env; conda activate cuda9; conda env list; cd minseok; pwd;python main.py -i videos/hacksmall.mp4 -d dataset")
print("==========Donwload file start==========")
ssh.file_download(output_pickle_path_remote, output_pickle_path_local)
print("==========Download file done===========")
'''
#load made pickle file to mosaic list
mosaic_list = pickle.loads(open("sjhalf_detected_faces.pickle", "rb").read())

editor = Editor.Editor(mosaic_list, "videos/sjhalff.mp4")
setEditor(editor)
frame = editor.length
# video processing......
# load all images and videos (with multiple extensions) from a directory using OpenCV
IMAGE_PATH_LIST = [[], [], [], []]

setImgPL(IMAGE_PATH_LIST, frame)

# fill IMAGE_PATH_LIST
search_filedir(INPUT_DIR, -1)
last_img_index = frame
setlasti(last_img_index)

# load class list
with open('class_list.txt') as f:
    CLASS_LIST = list(nonblank_lines(f))

# print(CLASS_LIST)
last_class_index = len(CLASS_LIST) - 1
setlci(last_class_index, CLASS_LIST)
print('class list is', last_class_index, 'long')

# Make the class colors the same each session
# The colors are in BGR order because we're using OpenCV
class_rgb = [
    (0, 0, 255), (255, 0, 0), (0, 255, 0), (255, 255, 0), (0, 255, 255),
    (255, 0, 255), (192, 192, 192), (128, 128, 128), (128, 0, 0),
    (128, 128, 0), (0, 128, 0), (128, 0, 128), (0, 128, 128), (0, 0, 128)]
class_rgb = np.array(class_rgb)

# If there are still more classes, add new colors randomly
num_colors_missing = len(CLASS_LIST) - len(class_rgb)
if num_colors_missing > 0:
    more_colors = np.random.randint(0, 255 + 1, size=(num_colors_missing, 3))
    class_rgb = np.vstack([class_rgb, more_colors])

# create window
cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_KEEPRATIO)
cv2.resizeWindow(WINDOW_NAME, 1000, 700)
cv2.setMouseCallback(WINDOW_NAME, mouse_listener)

# add trackbar for frame and speed
cv2.createTrackbar(TRACKBAR_IMG, WINDOW_NAME, 0, last_img_index, set_img_index)
cv2.createTrackbar(TRACKBAR_SPEED, WINDOW_NAME, 1, 1000, set_speed_index)

# initialize
set_img_index(0)
set_speed_index(1)

display_text('Welcome!\n Press [h] for help.', 4000)

# loop
while True:
    color = class_rgb[class_index].tolist()
    # clone the img
    tmp_img = UI.img.copy()
    height, width = tmp_img.shape[:2]
    # draw vertical and horizontal guide lines
    draw_line(tmp_img, UI.mouse_x, UI.mouse_y, height, width, color)
    # write selected class
    class_name = CLASS_LIST[class_index]
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    margin = 3
    text_width, text_height = cv2.getTextSize(class_name, font, font_scale, LINE_THICKNESS)[0]
    tmp_img = cv2.rectangle(tmp_img, (UI.mouse_x + LINE_THICKNESS, UI.mouse_y - LINE_THICKNESS),
                            (UI.mouse_x + text_width + margin, UI.mouse_y - text_height - margin),
                            complement_bgr(color), -1)
    tmp_img = cv2.putText(tmp_img, class_name, (UI.mouse_x + margin, UI.mouse_y - margin), font, font_scale, color,
                          LINE_THICKNESS, cv2.LINE_AA)
    # if first click
    if UI.point_1[0] is not -1:
        # draw partial bbox
        cv2.rectangle(tmp_img, UI.point_1, (UI.mouse_x, UI.mouse_y), color, LINE_THICKNESS)
        # if second click
        if UI.point_2[0] is not -1:
            if editor.edit(img_index, UI.point_1[0], UI.point_1[1], UI.point_2[0], UI.point_2[1]):
                set_img_index(img_index)
                tmp_img = UI.img.copy()
                cv2.imshow(WINDOW_NAME, tmp_img)
            cv2.imshow(WINDOW_NAME, tmp_img)
            # reset the points
            UI.point_1 = (-1, -1)
            UI.point_2 = (-1, -1)
	#display
    cv2.imshow(WINDOW_NAME, tmp_img)
    #receive user keyboard input
	pressed_key = cv2.waitKey(DELAY)

    if pressed_key == ord('a') or pressed_key == ord('d'):
        # show previous image
        if pressed_key == ord('a'):
            img_index = decrease_index(img_index, last_img_index, mode)
        # show next image
        elif pressed_key == ord('d'):
            img_index = increase_index(img_index, last_img_index, mode)
        set_img_index(img_index)
        cv2.setTrackbarPos(TRACKBAR_IMG, WINDOW_NAME, img_index)

    # help
    elif pressed_key == ord('h'):
        text = ('[q] to quit;\n'
                '[a] or [d] to change Image;\n'
                '[1] , [2], or [3] to change Mode;\n'
                '[p] to play and ' ' to stop;\n'
                '[s] to save output. \n'
                )
        display_text(text, 5000)
    #mode swap
	elif pressed_key == ord('1') or pressed_key == ord('2') or pressed_key == ord('3'):
        # change mode
        if pressed_key == ord('1'):
            class_index = 0
            UI.mode = 0
            mode = 0
        elif pressed_key == ord('2'):
            class_index = 1
            UI.mode = 1
            mode = 1
        elif pressed_key == ord('3'):
            class_index = 2
            UI.mode = 2
            mode = 2
        draw_line(tmp_img, UI.mouse_x, UI.mouse_y, height, width, color)
        set_class_index(class_index)
        set_img_index(img_index)
        cv2.setTrackbarPos(TRACKBAR_IMG, WINDOW_NAME, img_index)
    #play
	elif pressed_key == ord('p'):
        for x in range(img_index, frame):
            img_index = increase_index(img_index, last_img_index, mode)
            cv2.setTrackbarPos(TRACKBAR_IMG, WINDOW_NAME, img_index)
            tmp_img = UI.img.copy()
            cv2.imshow(WINDOW_NAME, tmp_img)
            pressed_key = cv2.waitKey(DELAY)
            #play speed (time gap between each frame)
			time.sleep(UI.speed_index)
            #pause
			if pressed_key == ord(' '):
                break

    # quit
    elif pressed_key == ord('q'):
        break
	#extract video file
    elif pressed_key == ord('s'):
        editor.output(mode)
        if os.path.isfile("output.avi"):
            os.remove("output.avi")
        if os.path.isfile("audio.mp3"):
            os.remove("audio.mp3")

    ''' Key Listeners END '''

    if WITH_QT:
        # if window gets closed then quit
        if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
            break

cv2.destroyAllWindows()

if os.path.isfile("output.avi"):
    os.remove("output.avi")
if os.path.isfile("audio.mp3"):
    os.remove("audio.mp3")

'''
mosaic_list = pickle.load(open("hacksmall_detected_faces.pickle", "rb"))
input_video_dir = "videos/hacksmall.mp4"
editor = Editor.Editor(mosaic_list, input_video_dir)

if os.path.isfile("detected_faces.pickle"):
    os.remove("detected_faces.pickle")
'''
if os.path.isdir("temp"):
    shutil.rmtree("temp")
if os.path.isfile("detected_faces.pickle"):
    os.remove("detected_faces.pickle")
