import cv2
import numpy as np
import subprocess
import math
import signal
import argparse
import threading 
from pathlib2 import Path
pos = []
procs = []
global pts1
def mouse_drawing(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        # circles.append((x, y))
        pos.append([x, y])
        print(pos)


def draw ():
    pts1 = np.float32([pos[0], pos[1], pos[2], pos[3]])
    pts2 = np.float32([[0, 0], [576, 0], [0, 704], [576, 704]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    result = cv2.warpPerspective(frame, matrix, (576, 704))
    cv2.imshow("pres", result)


def crop(pos, in_path, out_path):
    global procs
    crop_area = [abs(pos[0][0]-pos[1][0]),abs(pos[0][1]-pos[1][1]),min(pos[0][0],pos[1][0]),min(pos[0][1],pos[1][1])]
    procs.append(subprocess.Popen("ffmpeg -i "+in_path+" -strict -2"+" -filter:v "+'"crop={}:{}:{}:{}"'.format(*crop_area)+" "+out_path, shell=True))
    # subprocess.run(["ffmpeg", "-i", in_path, "-filter:v","crop", "{}:{}:{}:{}".format(*crop_area), out_path])
    
    # proc.wait()

def start_play(in_path, out_path):
    global pos
    cap = cv2.VideoCapture(in_path)
    window_name="Original Video"
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, mouse_drawing)
    circles = []

    while True:
        _, frame = cap.read()
        h, w = frame.shape[:2]
        for center_position in pos:
            cv2.rectangle(frame, tuple([i-2 for i in center_position]), tuple([i+2 for i in center_position]), (255,0,0), 2)

        cv2.imshow(window_name, frame)

        if len(pos) == 2:
            crop(pos, in_path, out_path)
            break

        # Quit the current video position marking
        key = cv2.waitKey(1)
        if key in [27, ord("q"), ord("p")]:
            break
        # Reset the positions
        elif key == ord("r"):
            pos = []

    cap.release()
    cv2.destroyAllWindows()
    pos = []

def signal_handler(sig, frame):
    global procs
    for proc in procs:
        proc.wait()
    log('Program exit successfully and video cropped well!\nThank for using!')
    sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_path","-i",type=str,default="./video.mp4",help="Input video path.")
    parser.add_argument("--out_path","-o",type=str,default="./video_crop.mp4",help="Output video path.")
    args=parser.parse_args()
    args.in_path=Path(args.in_path)
    args.out_path=Path(args.out_path)
    signal.signal(signal.SIGINT, signal_handler)
    if args.in_path.is_file():
        start_play(str(args.in_path), str(args.out_path))
    elif args.in_path.is_dir():
        videos=[i for i in list(args.in_path.iterdir()) if not i.name.startswith(".") and i.is_file()]
        for video in videos:
            start_play(str(video), str(args.out_path/video.name))
    for proc in procs:
        proc.wait()