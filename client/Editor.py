import cv2
import os
import glob
import imutils
import copy
from moviepy.editor import *


class Editor:
    def __init__(self, mosaic_list, input_video_dir, mosaic_rate=15):
        self.mosaic_list = mosaic_list
        self.input_video_dir = input_video_dir
        self.mosaic_rate = mosaic_rate
        self.generate_images(self.mosaic_rate, 15)

    def generate_images(self, mosaic_rate, change): # if change != 0, it's first time to generate image
        cap = cv2.VideoCapture(self.input_video_dir) # capture every frame
        self.length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) # save the length of the video
        
        # make directories
        if not os.path.isdir("temp"): # make directory
            os.mkdir("temp")
        if not os.path.isdir("temp/raw"):
            os.mkdir("temp/raw")
        if not os.path.isdir("temp/box"):
            os.mkdir("temp/box")
        if not os.path.isdir("temp/mosaic"):
            os.mkdir("temp/mosaic")
        if not os.path.isdir("temp/blur"):
            os.mkdir("temp/blur")

        frame_i = 0

        while frame_i < self.length:
            (grabbed, mosaic_frame) = cap.read()
            mosaic_frame = imutils.resize(mosaic_frame, height=720) # resize frame images
            if change: # if first time to generate image, make raw, box, mosaic, blur image
                box_image = copy.deepcopy(mosaic_frame)
                raw_image = copy.deepcopy(mosaic_frame)
            mosaic_image = copy.deepcopy(mosaic_frame) # if not first time(when changing mosaic rate) remake mosaic, blur image
            blur_image = copy.deepcopy(mosaic_frame)

            mosaic_list_i = 0

            if grabbed:
                while mosaic_list_i < len(self.mosaic_list):
                    info = self.mosaic_list[mosaic_list_i]
                    if info['frame'] == frame_i:
                        if info['mosaic']:       # mosaic
                            if change:
                                cv2.rectangle(box_image, (info['left'], info['top']), (info['right'], info['bottom']), (0, 0, 255), 2)
                            h = info['bottom'] - info['top']
                            w = info['right'] - info['left']
                            face_img_m = mosaic_image[info['top']:info['top'] + h, info['left']:info['left'] + w] # extract face image
                            face_img_b = blur_image[info['top']:info['top'] + h, info['left']:info['left'] + w]

                            # mode 'm'
                            try:
                                face_img_m = cv2.resize(face_img_m, (w // mosaic_rate, h // mosaic_rate))
                                face_img_m = cv2.resize(face_img_m, (w, h), interpolation=cv2.INTER_AREA) # mosaic the face through resizing images

                            except Exception as e:
                                print(str(e))

                            try:
                                mosaic_image[info['top']:info['top'] + h, info['left']:info['left'] + w] = face_img_m # insert mosaic image

                            except Exception as e:
                                print(str(e))

                            # mode 'b'
                            try:
                                blur = cv2.blur(face_img_b, (mosaic_rate, mosaic_rate)) # blur through blur function

                            except Exception as e:
                                print(str(e))

                            try:
                                blur_image[info['top']:info['top'] + h, info['left']:info['left'] + w] = blur # insert blur image
                            except Exception as e:
                                print(str(e))
                        else:
                            if change:
                                cv2.rectangle(box_image, (info['left'], info['top']), (info['right'], info['bottom']), (0, 255, 0), 2)
                    mosaic_list_i += 1
            if change:
                cv2.imwrite('temp/raw/' + str(frame_i) + '.jpg', raw_image)
                cv2.imwrite('temp/box/' + str(frame_i) + '.jpg', box_image)
            cv2.imwrite('temp/mosaic/' + str(frame_i) + '.jpg', mosaic_image)
            cv2.imwrite('temp/blur/' + str(frame_i) + '.jpg', blur_image) # save images at corresponding directory

            frame_i += 1
        cap.release()
        self.length -= 1

    def edit(self, frame_i, left, top, right, bottom):
        # if box exists
        if right == -1: # if one coordinate exists
            for info in self.mosaic_list:
                if info['frame'] != frame_i:
                    continue

                elif self.isinthebox(left, top, info): # check the scope of coordinate
                    info['mosaic'] = not info['mosaic'] # change whether mosaic or not
                    temp_box = cv2.imread('temp/box/' + str(frame_i) + '.jpg')
                    temp_mosaic = cv2.imread('temp/mosaic/' + str(frame_i) + '.jpg')
                    temp_blur = cv2.imread('temp/blur/' + str(frame_i) + '.jpg')
                    temp_raw = cv2.imread('temp/raw/' + str(frame_i) + '.jpg')

                    # mosaic
                    if info['mosaic']:
                        cv2.rectangle(temp_box, (info['left'], info['top']), (info['right'], info['bottom']), (0, 0, 255), 2) # remake box image
                        h = info['bottom'] - info['top']
                        w = info['right'] - info['left']
                        face_img_m = temp_raw[info['top']:info['top'] + h, info['left']:info['left'] + w]
                        face_img_b = temp_raw[info['top']:info['top'] + h, info['left']:info['left'] + w]  # extract face image

                        # mode mosaic
                        try:
                            face_img_m = cv2.resize(face_img_m, (w // self.mosaic_rate, h // self.mosaic_rate))
                            face_img_m = cv2.resize(face_img_m, (w, h), interpolation=cv2.INTER_AREA)  # mosaic the face through resizing images

                        except Exception as e:
                            print(str(e))

                        try:
                            temp_mosaic[info['top']:info['top'] + h, info['left']:info['left'] + w] = face_img_m  # insert mosaic image

                        except Exception as e:
                            print(str(e))

                        # mode 'b'
                        try:
                            blur = cv2.blur(face_img_b, (self.mosaic_rate, self.mosaic_rate)) # blur through blur function

                        except Exception as e:
                            print(str(e))

                        try:
                            temp_blur[info['top']:info['top'] + h, info['left']:info['left'] + w] = blur  # insert blur image

                        except Exception as e:
                            print(str(e))

                    # cancel mosaic
                    else:
                        cv2.rectangle(temp_box, (info['left'], info['top']), (info['right'], info['bottom']), (0, 255, 0), 2) # remake box image
                        h = info['bottom'] - info['top']
                        w = info['right'] - info['left']
                        face_img = temp_raw[info['top']:info['top'] + h, info['left']:info['left'] + w] # extract face image
                        temp_mosaic[info['top']:info['top'] + h, info['left']:info['left'] + w] = face_img
                        temp_blur[info['top']:info['top'] + h, info['left']:info['left'] + w] = face_img # insert raw image

                    cv2.imwrite('temp/box/' + str(frame_i) + '.jpg', temp_box)
                    cv2.imwrite('temp/mosaic/' + str(frame_i) + '.jpg', temp_mosaic)
                    cv2.imwrite('temp/blur/' + str(frame_i) + '.jpg', temp_blur) # save the images
                    return True
            return False

        # generate box
        else:
            for info in self.mosaic_list:
                if info['frame'] != frame_i and info['frame'] != frame_i+1:
                    continue
                elif info['frame'] == frame_i:
                    if self.isinthebox(left, top, info) or self.isinthebox(right, bottom, info):
                        return False
                    else:
                        continue
                elif info['frame'] == frame_i+1: # fine the last index of the frame
                    idx = self.mosaic_list.index(info)
                    self.mosaic_list.insert(idx, {'frame': frame_i, 'left': left, 'right': right, 'top': top, 'bottom': bottom, 'mosaic': True}) # insert new node with input value
                    new = self.mosaic_list[idx]

                    temp_box = cv2.imread('temp/box/' + str(frame_i) + '.jpg')
                    temp_mosaic = cv2.imread('temp/mosaic/' + str(frame_i) + '.jpg')
                    temp_blur = cv2.imread('temp/blur/' + str(frame_i) + '.jpg')

                    cv2.rectangle(temp_box, (new['left'], new['top']), (new['right'], new['bottom']), (0, 0, 255), 2) # add new box
                    h = new['bottom'] - new['top']
                    w = new['right'] - new['left']
                    face_img_m = temp_mosaic[new['top']:new['top'] + h, new['left']:new['left'] + w]
                    face_img_b = temp_mosaic[new['top']:new['top'] + h, new['left']:new['left'] + w] # extract face image

                    # mode 'm'
                    try:
                        face_img_m = cv2.resize(face_img_m, (w // self.mosaic_rate, h // self.mosaic_rate))
                        face_img_m = cv2.resize(face_img_m, (w, h), interpolation=cv2.INTER_AREA) # mosaic the face through resizing images

                    except Exception as e:
                        print(str(e))

                    try:
                        temp_mosaic[new['top']:new['top'] + h, new['left']:new['left'] + w] = face_img_m  # insert mosaic image

                    except Exception as e:
                        print(str(e))

                    # mode 'b'
                    try:
                        blur = cv2.blur(face_img_b, (self.mosaic_rate, self.mosaic_rate))  # blur through blur function

                    except Exception as e:
                        print(str(e))

                    try:
                        temp_blur[new['top']:new['top'] + h, new['left']:new['left'] + w] = blur  # insert blur image

                    except Exception as e:
                        print(str(e))

                    cv2.imwrite('temp/box/' + str(frame_i) + '.jpg', temp_box)
                    cv2.imwrite('temp/mosaic/' + str(frame_i) + '.jpg', temp_mosaic)
                    cv2.imwrite('temp/blur/' + str(frame_i) + '.jpg', temp_blur)
                    return True
            return False

    def change_mosaic_rate(self, new_mosaic_rate):
        self.generate_images(new_mosaic_rate, 0) # call generate_image function with change value 0

    def isinthebox(self, x, y, info): # check whether the coordinate is in the scope(face box)
        if info['left'] < x < info['right'] and info['top'] < y < info['bottom']:
            return True
        else:
            return False

    def output(self, mode): # generate final video
        print("extracting audio...")
        audio = AudioFileClip(self.input_video_dir)
        audio.write_audiofile('audio.mp3') # extract audio from the raw video file
        print("complete extract")

        # encode mp4 file
        print("output video encoding...")
        img_array = []
        size = None
        frame_i = 0
        while frame_i < self.length:
            if mode == 0:
                for filename in glob.glob('temp/blur/*.jpg'): # get list of all files of image
                    if filename == 'temp/blur\\{}.jpg'.format(frame_i):
                        img = cv2.imread(filename)
                        height, width, layers = img.shape # get the size of image
                        size = (width, height)
                        img_array.append(img) # append the image to image list
            if mode == 1:
                for filename in glob.glob('temp/box/*.jpg'): # get list of all files of image
                    if filename == 'temp/box\\{}.jpg'.format(frame_i):
                        img = cv2.imread(filename)
                        height, width, layers = img.shape
                        size = (width, height)
                        img_array.append(img)
            if mode == 2:
                for filename in glob.glob('temp/mosaic/*.jpg'): # get list of all files of image
                    if filename == 'temp/mosaic\\{}.jpg'.format(frame_i):
                        img = cv2.imread(filename)
                        height, width, layers = img.shape
                        size = (width, height)
                        img_array.append(img)
            frame_i += 1

        video = cv2.VideoCapture(self.input_video_dir)
        fps = int(video.get(cv2.CAP_PROP_FPS))
        out = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc(*'DIVX'), fps, size)
        for i in range(len(img_array)):
            out.write(img_array[i])

        out.release()
        print("complete encoding")

        # merge mp4 and mp3
        print("merging...")
        audio = AudioFileClip('audio.mp3')
        video = VideoFileClip('output.avi')
        result = video.set_audio(audio) # assemble audio and video
        result.write_videofile('result.mp4') # save the video
        print("complete merge")