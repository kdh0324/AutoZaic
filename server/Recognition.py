import pickle
import cv2
import imutils
import Detector
import face_recognition


class Recognition:
    def __init__(self, encoding_path, video_path):
        self.detected_faces = []

        # get known faces encoding
        self.data = pickle.loads(open(encoding_path, "rb").read())

        # initialize the pointer to the video file and the video writer
        self.stream = cv2.VideoCapture(video_path)
        self.frame_length = int(self.stream.get(cv2.CAP_PROP_FRAME_COUNT))

    def recognize(self):
        frame_number = 0

        # loop over frames from the video file stream
        while True:
            # grab the next frame
            (grabbed, frame) = self.stream.read()
            # if the frame was not grabbed, then we have reached the end of the stream
            if not grabbed:
                break

            # convert the input frame from BGR to RGB then resize it to have a height of 720px (to speedup processing)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb = imutils.resize(rgb, height=720)

            frame_copy = rgb.copy()

            face_list, M = Detector.detect_face(rgb)

            boxes = []
            for i in range(len(face_list)):
                top = face_list[i]['top']
                bottom = face_list[i]['bottom']
                left = face_list[i]['left']
                right = face_list[i]['right']
                boxes.append((top, right, bottom, left))
                face_list[i]['frame'] = frame_number

                # align the face with M
                alignedFace = None
                try:
                    rgb_aligned = cv2.warpAffine(frame_copy, M[i], (frame_copy.shape[1], frame_copy.shape[0]))
                    alignedFace = rgb_aligned[top:bottom, left:right, :]
                except:
                    print("align error")
                try:
                    frame_copy[top:bottom, left:right, :] = alignedFace
                except:
                    print("size difference")

            face_encodings = face_recognition.face_encodings(frame_copy, boxes)
            
            for i, encoding in enumerate(face_encodings):
                # attempt to match each face in the input image to our known encodings
                matches = face_recognition.compare_faces(self.data['encodings'], encoding, tolerance=0.4)

                # check to see if we have found a match
                if True in matches:
                    face_list[i]['mosaic'] = False

            self.detected_faces.extend(face_list)

            print("[Recog_INFO] Processing image {}".format(frame_number + 1), "/", self.frame_length)
            frame_number += 1
        print("[Recog_INFO] serializing encodings...")
        data = self.detected_faces
        f = open("detected_faces.pickle", "wb")
        f.write(pickle.dumps(data))
        f.close()
        
        return self.detected_faces
