"""
USAGE
python main.py -i videos/sj.mp4 -d dataset
"""

import Recognition
import Encoder
import argparse

# read arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", type=str, default="dataset",
                help="input face dataset path")
ap.add_argument("-i", "--input", type=str, help="path to input video")
args = vars(ap.parse_args())

# start encoding
print("Encoding data set...")
encoder = Encoder.Encoder(args['dataset'])
encode_file_dir = encoder.encode()
print("Completely encode the data set")

# start detection and recognition
print("Detecting the face...")
input_video_dir = args['input']
recognition = Recognition.Recognition(encode_file_dir, input_video_dir)
mosaic_list = recognition.recognize()
print("Completely detected faces from input video")
