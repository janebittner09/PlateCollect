import cv2
import time
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


class DetectEngine:
    CONFIDENCE_THRESHOLD = 0.05
    NMS_THRESHOLD = 0.3
    COLORS = [(0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 0, 0)]
    Net = None
    Model = None

    def __init__(self):
        self.weightPath = os.path.join(__location__, 'data/yolov3-tiny-prn-iraqplate_92800.weights')
        self.configPath = os.path.join(__location__, 'data/yolov3-tiny-prn-iraqplate.cfg')

        self.Net = cv2.dnn.readNet(self.weightPath, self.configPath)
        self.Net.setPreferableBackend(cv2.dnn.DNN_BACKEND_DEFAULT)
        self.Net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        self.Model = cv2.dnn_DetectionModel(self.Net)
        self.Model.setInputParams(size=(416, 416), scale=1 / 255)

    def detect(self, frame):
        ret = []
        classes, scores, boxes = self.Model.detect(frame, self.CONFIDENCE_THRESHOLD, self.NMS_THRESHOLD)
        for (classid, score, box) in zip(classes, scores, boxes):
            x, y, w, h = box
            if int(classid[0]) in [6, 4]:
                ret.append([x, y, w, h, classid[0]])

        return ret