# Camera Class
# Brandon Joffe
# 2016
#
# Copyright 2016, Brandon Joffe, All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import threading
import time
import cv2
import datetime

class FPS:
	def __init__(self):
		self.qsize = 100
		self.queue = []

	def update(self, dt, onlytime=False):
		if onlytime:
			if len(self.queue) > 0:
				self.queue[-1] = dt # time.time()
			else:
				self.queue.append(dt)
		else:
			if len(self.queue) < self.qsize:
				self.queue.append(dt)
			else:
				self.queue.pop(0)
				self.queue.append(dt)

	def fps(self):
		# compute the (approximate) frames per second
		if len(self.queue) > 80:
			return len(self.queue) / (self.queue[-1] - self.queue[0]).total_seconds()
		else:
			return 0


CAPTURE_HZ = 5.0  # Determines frame rate at which frames are captured from IP camera
SKIPFRAME = 3


class IPCamera(object):
	"""The IPCamera object continually captures frames
	from a camera and makes these frames available for
	proccessing and streamimg to the web client. A 
	IPCamera can be processed using 5 different processing 
	functions detect_motion, detect_recognise, 
	motion_detect_recognise, segment_detect_recognise, 
	detect_recognise_track. These can be found in the 
	SureveillanceSystem object, within the process_frame function"""

	def __init__(self, camURL, camID, roi=''):
		# logger.info("Loading Stream From IP Camera: " + camURL)
		self.camID = camID
		self.gpu_id = 0
		self.pid = 0

		# self.queue = Queue(30)
		# self.x, self.y, self.w, self.h = x, y, w, h
		self.roi = roi.split(',')
		if roi == '' or len(self.roi) < 6:
			self.roi = [0, 0, 1, 0, 1, 1, 0, 1]

		self.processing_frame = None
		self.tempFrame = None
		self.captureFrame = None
		self.showFrame = None
		self.streamingFPS = FPS()  # Streaming frame rate per second
		self.processingFPS = FPS()

		# self.url = "rtspsrc location={} latency=30 ! queue ! rtph264depay ! h264parse ! omxh264dec ! nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! video/x-raw,format=BGR ! appsink".format(camURL)
		self.url = camURL

		self.video = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)  # VideoCapture object used to capture frames from IP camera
		if not self.video.isOpened():
			self.video.open()

		self.captureThread_stop = False

		self.captureThread = threading.Thread(name='video_captureThread', target=self.get_frame)
		self.captureThread.daemon = True
		self.captureThread.start()

		self.captureEvent = threading.Event()
		self.captureEvent.set()

	def __del__(self):
		self.video.release()

	def get_frame(self):
		unsuccess_cnt = 0
		frame_cnt = 0
		while not self.captureThread_stop:
			try:
				time.sleep(.01)
				success, frame = self.video.read()
				self.captureEvent.clear()
				if success:
					self.captureFrame = frame
					self.showFrame = frame
					self.captureEvent.set()
					self.streamingFPS.update(datetime.datetime.now(), False)
				else:
					self.streamingFPS.update(datetime.datetime.now(), True)
					unsuccess_cnt += 1
					frame_cnt += 0
			except cv2.error as e:
				print(e)
				unsuccess_cnt += 1

			if unsuccess_cnt > 100:
				unsuccess_cnt = 0
				self.streamingFPS = FPS()
				self.video = cv2.VideoCapture(self.url)

		print("camera thread finished.")

	def stop_camera(self):
		# capture_blocker = self.captureEvent.wait()
		# with self.captureLock:
		self.captureThread_stop = True
		print('stop camera')

	def read_frame(self):
		capture_blocker = self.captureEvent.wait()
		return self.captureFrame