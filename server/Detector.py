from mtcnn.mtcnn import MTCNN
import cv2
import numpy as np


def detect_face(image):
    detector = MTCNN()
    face_list = []
    M = []

    detected_faces = detector.detect_faces(image)

    for detected_face in detected_faces:
        # default frame number
        face = {'frame': None}

        # add left, top, width, height key
        (left, top, width, height) = detected_face['box']
        face['left'] = left
        face['top'] = top
        face['right'] = left + width
        face['bottom'] = top + height
        # default mosaic
        face['mosaic'] = True

        face_list.append(face)
        M.append(align(detected_face['keypoints']))\

    return face_list, M


def align(keypoints):
    # get left, right eye and nose landmarks
    leftEyeCenter = keypoints['left_eye']
    rightEyeCenter = keypoints['right_eye']
    noseCenter = keypoints['nose']

    # get slop of left and right eyes
    dY = rightEyeCenter[1] - leftEyeCenter[1]
    dX = rightEyeCenter[0] - leftEyeCenter[0]
    angle = np.degrees(np.arctan2(dY, dX))

    # get rotation matrix (rotate based on nose)
    return cv2.getRotationMatrix2D(noseCenter, angle, 1)
