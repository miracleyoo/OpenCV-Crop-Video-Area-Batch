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
        pos.append([x, y])
        print(pos)

def crop(pos, in_path, out_path):
    global procs
    crop_area = [abs(pos[0][0]-pos[1][0]),abs(pos[0][1]-pos[1][1]),min(pos[0][0],pos[1][0]),min(pos[0][1],pos[1][1])]
    procs.append(subprocess.Popen("ffmpeg -i "+in_path+" -strict -2"+" -filter:v "+'"crop={}:{}:{}:{}"'.format(*crop_area)+" "+out_path, shell=True))


def start_play(in_path, out_path):
    global pos
    cap = cv2.VideoCapture(in_path)
    window_name="Original Video"
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, mouse_drawing)
    circles = []

    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret:
            h, w = frame.shape[:2]
            for center_position in pos:
                cv2.rectangle(frame, tuple([i-2 for i in center_position]), tuple([i+2 for i in center_position]), (183,143,58), 2)

            cv2.imshow(window_name, frame)

            if len(pos) == 2:
                flag = False
                cv2.rectangle(frame, (min(pos[0][0],pos[1][0]),min(pos[0][1],pos[1][1])), (max(pos[0][0],pos[1][0]),max(pos[0][1],pos[1][1])), (180,159,220), 2)
                cv2.imshow(window_name, frame)
                while True:
                    key = cv2.waitKey(1)
                    # Press enter to start crop
                    if key in [10,13]:
                        crop(pos, in_path, out_path)
                        flag = True
                        break
                    # Press esc, q, or p to quit cropping and set pos empty
                    elif key in [27, ord("q"),ord("p")]:
                        pos=[]
                        break
                    # Press z to delete the lastest point
                    elif key == ord("z") and len(pos)>0:
                        pos=pos[:len(pos)-1]
                        break
                if flag:
                    break

            # Quit the current video position marking
            key = cv2.waitKey(1)
            if key in [27, ord("q"), ord("p")]:
                break
            # Reset the positions
            elif key == ord("r"):
                pos = []
            # Delete the lastest point
            elif key == ord("z") and len(pos)>0:
                pos=pos[:len(pos)-1]
        else:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

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