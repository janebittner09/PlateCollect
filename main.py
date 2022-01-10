import time
import cv2
import os
from utils import Camera
from utils.detect_engine_cpu import DetectEngine

rtsp = "rtsp://192.168.101.111:556/live"

cv2.namedWindow("Display", cv2.WINDOW_NORMAL)
Engine = DetectEngine()
camera = Camera.IPCamera(rtsp, 0)
while True:
    frame = camera.read_frame()
    if frame is None:
        continue
    height, width, _ = frame.shape
    result = Engine.detect(frame)
    for r in result:
        x, y, w, h, _ = r
        if (x <= 0 or y <= 0) and (x+w > width or y+h > height):
            continue

        if w/h > 1.5:
            ufilename = time.time()
            path = "images/{}.jpg".format(ufilename)
            cv2.imwrite(path, frame[y:y+h, x:x+w])

            path = "images/{}-{}_{}_{}_{}.jpg".format(ufilename, x, y, w, h)
            cv2.imwrite(path, frame)
            print(w, h, w/h)

    cv2.imshow("Display", frame)
    cv2.waitKey(1)

# dir = 'E:\\2021_8_Projects\\000.BOMN_LPR\\VIDEO\en'
# for afile in os.listdir(dir):
#     frame = cv2.imread(os.path.join(dir, afile))
#     height, width, _ = frame.shape
#     result = Engine.detect(frame)
#     for r in result:
#         x, y, w, h, cl = r
#         if (x <= 0 or y <=0) and (x+w > width or y+h > height):
#             continue
#         ufilename = time.time()
#         path = "images/{}.jpg".format(ufilename)
#         cv2.imwrite(path, frame[y:y+h, x:x+w])
#         print(w, h, w/h, cl, ufilename)