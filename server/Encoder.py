from imutils import paths
import pickle
import cv2
import os
import face_recognition
import Detector


class Encoder:
    def __init__(self, image_path_list=[]):
        self.imagePaths = list(paths.list_images(image_path_list))
        self.outputPath = "encodings.pickle"

        # initialize the list of known encodings and known names
        self.knownEncodings = []
        self.knownNames = []

    def set_image_paths(self, image_path_list):
        self.imagePaths = list(paths.list_images(image_path_list))

    def encode(self):
        # loop over the image paths
        if not self.imagePaths:
            print("ImagePath is empty")
            return

        for (i, imagePath) in enumerate(self.imagePaths):
            # extract the person name from the image path
            print("[Encode_INFO] Processimg image {}/{}".format(i + 1, len(self.imagePaths)))
            name = imagePath.split(os.path.sep)[-2]

            # load the input im
            # age and convert it from RGB (OpenCV ordering)
            # to dlib ordering (RGB)
            image = cv2.imread(imagePath)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            img_copy = rgb.copy()

            # detect the face and get the transformation matrix list
            face_list, M = Detector.detect_face(rgb)

            top = face_list[0]['top']
            bottom = face_list[0]['bottom']
            left = face_list[0]['left']
            right = face_list[0]['right']
            boxes = [(top, right, bottom, left)]
            
            # align the face with M
            rgb_aligned = cv2.warpAffine(img_copy, M[0], (img_copy.shape[1], img_copy.shape[0]))
            alignedFace = rgb_aligned[top:bottom, left:right, :]
            rgb[top:bottom, left:right, :] = alignedFace

            # compute the facial embedding for the face
            encodings = face_recognition.face_encodings(rgb, boxes)

            # loop over the encodings
            for encoding in encodings:
                # add each encoding + name to our set of known names and encodings
                self.knownEncodings.append(encoding)
                self.knownNames.append(name)

        # dump the facial encodings + names to disk
        print("[Encode_INFO] serializing encodings...")
        data = {"encodings": self.knownEncodings, "name": self.knownNames}
        f = open(self.outputPath, "wb")
        f.write(pickle.dumps(data))
        f.close()

        return self.outputPath
