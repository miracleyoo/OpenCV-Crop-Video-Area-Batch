# OpenCV Crop Video Area Batch

Sometimes we need to crop a certain area of the video, like crop the live streamer face video from the entire live video. It only needs two points to define a rectangle, whatever your order is. 

Also, I need to do this in batch, since I have a dataset to deal with, so I added batch folder support. If your `in_path` and `out_path` is all folder, then you will enter batch mode and the program will guide and show you videos in that folder one by one, what you need to do is just click two points. Once two points are detected, the program will start cropping.

