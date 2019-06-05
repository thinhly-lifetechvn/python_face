# Creating database 
# It captures images and stores them in datasets 
# folder under the folder name of sub_data 
import cv2, sys, numpy, os 
from datetime import datetime
import time
import logging
import requests
import datetime
import threading
import json
import boto3
import glob
import shutil
import math
from dateutil.parser import parse
import dlib
import imutils

def write_log(msg):
	LOG_FILENAME = '/home/lifetech/python_face/log/log.txt'
	logging.basicConfig(handlers=[logging.FileHandler(LOG_FILENAME, 'a', 'utf-8')], level=logging.INFO)

	now = datetime.datetime.now()

	logging.info(now.strftime("%Y-%m-%d %H:%M:%S") + ": " + msg)

	print(now.strftime("%Y-%m-%d %H:%M:%S") + ": " + msg)	

def capture():
	#haar_file = '/home/lifetech/python_face/haarcascade_frontalface_default.xml'

	# All the faces data will be 
	# present this folder 
	datasets = '/home/lifetech/python_face/datasets'


	# These are sub data sets of folder, 
	# for my faces I've used my name you can 
	# change the label here 
	sub_data = 'vivek'	

	path = os.path.join(datasets, sub_data) 
	if not os.path.isdir(path): 
		os.mkdir(path) 

	# defining the size of images 
	(width, height) = (130, 100)	 

	#'0' is used for my webcam, 
	# if you've any other camera 
	# attached use '1' like this 
	#face_cascade = cv2.CascadeClassifier(haar_file) 
	webcam = cv2.VideoCapture(0) 
	
	detector = dlib.get_frontal_face_detector()

	while True: 
		(_, im) = webcam.read() 

		im = imutils.resize(im, width=400)

		gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) 

		faces = detector(gray, 1)
		
		if len(faces) > 0:
			write_log("Number of faces detected: {}".format(len(faces)))
		#	cv2.imwrite('% s/% s.png' % (path, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")), im)  
			for i, d in enumerate(faces):
				write_log("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
					i, d.left(), d.top(), d.right(), d.bottom()))
				#w = d.right() - d.left()
				#h = d.bottom() - d.top()
				#print("Width {}: Heigh: {}".format(w, h))	
				face = gray[d.top():d.bottom(), d.left():d.right()] 
				
				#face_resize = cv2.resize(face, (width, height)) 
				#face_resize = imutils.resize(face, width=150) 

				cv2.imwrite('% s/% s.png' % (path, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")), face)  
			
		#time.sleep(0.3)

def compare():
	while True:
		try:
			while len(glob.glob("/home/lifetech/python_face/datasets/vivek/*.png")) > 0:	
				# checkinname = ''			
				for file in glob.glob("/home/lifetech/python_face/datasets/vivek/*.png"):
					try:
						# Replace sourceFile and targetFile with the image files you want to compare.
						#sourceFile='/home/lifetech/python_face/datasets/vivek/2019-05-29 16:52:15.837067.png'
						sourceFile = file
						#targetFile='https://s3.amazonaws.com/lifetech-face/Data.jpg'
						client=boto3.client('rekognition')					

						fileName='Data.jpg'
						bucket='lifetech-face'
					 
						imageSource=open(sourceFile,'rb')
						#imageTarget=open(targetFile,'rb')
						#imageTarget=Image={'S3Object':{'Bucket':bucket,'Name':fileName}}

						response=client.compare_faces(SimilarityThreshold=70,
													  SourceImage={'Bytes': imageSource.read()},
													  TargetImage={'S3Object':{'Bucket':bucket,'Name':fileName}})
						if len(response['FaceMatches']) > 0:
							for faceMatch in response['FaceMatches']:
								position = faceMatch['Face']['BoundingBox']
								confidence = str(faceMatch['Face']['Confidence'])
								write_log('The face at ' +
									str(position['Left']) + ' ' +
									str(position['Top']) +
									' matches with ' + confidence + '% confidence')

							imageSource.close()
							#imageTarget.close()
							if float(confidence) >= 90:
								pos = getPosition(position['Left'], position['Top'], 200, 300, 600, 300)										
								str_date = parse(os.path.basename(sourceFile).replace('.png',''))
								name = getEmpNameByFacePos(pos)
								# if checkinname != name:
								# 	checkinname = name
								write_log('Hi ' + name + ', Your checkin time: ' + str_date.strftime("%Y-%m-%d %H:%M:%S"))
								#write_log('Your checkin time: ' + str_date.strftime("%Y-%m-%d %H:%M:%S"))
								checkinface(pos, str_date.strftime("%Y-%m-%d %H:%M:%S"))
								shutil.move(sourceFile, "/home/lifetech/python_face/datasets/vivek/ok/")
							else:
								write_log('Image not match in data.')
								shutil.move(sourceFile, "/home/lifetech/python_face/datasets/vivek/unknow/")
						else:
							write_log('Image not match in data.')
							shutil.move(sourceFile, "/home/lifetech/python_face/datasets/vivek/unknow/")
					except Exception as e:
						write_log('Exception message 1: ' + str(e))
						shutil.move(sourceFile, "/home/lifetech/python_face/datasets/vivek/ufo/")
		except Exception as e:
			write_log('Exception message 2: ' + str(e))	
			
		#write_log('Sleep 1 seconds.')				
		#time.sleep(1)

def getPosition(left, top, imgW, imgH, width, height):
	pos = 0
	#width = 2000 (10 person)
	#height = 3000 (10 person)
	#imgW = 200
	#imgH = 300
	
	p_left  = left * width
	p_top  = top * height
	
	index_x = math.floor(p_left / imgW)
	index_y = math.floor(p_top / imgH)
	
	pos = (index_x + 1) + (height / imgH * index_y)
	write_log('Image position: ' + str(p_left) + '-' + str(p_top) + ' POS: ' + str(int(pos)))
	
	return int(pos)

def checkinface(positionNumber, str_date):
	url = "http://192.168.80.167:5000/checkinface/" + str(positionNumber) + '/' + str_date
	myResponse = requests.get(url, verify=True)
	return myResponse.content.decode("utf8")

def getEmpNameByFacePos(positionNumber):
	url = "http://192.168.80.167:5000/getEmpNameByFacePos/" + str(positionNumber)
	myResponse = requests.get(url, verify=True)
	return myResponse.content.decode("utf8")

			
write_log("Start camera with OpenCV Version: {}".format(cv2.__version__))
write_log("Face detection with Dlib Version: {}".format(dlib.__version__))

#Start capture thread
write_log('Start capture thread')
#capture()
# t1 = threading.Thread(None, capture, None)
# t1.start() 
threading.Thread(target=capture).start()

write_log('Start compare thread')
# t2 = threading.Thread(None, compare, None)
# t2.start() 
threading.Thread(target=compare).start()
#compare()
#t1 = threading.Thread(None, capture, None)
#t1.start() 
#shutil.move("/home/lifetech/python_face/datasets/vivek/2019-05-29 17:02:29.894378.png", "/home/lifetech/python_face/datasets/vivek/ok/")
#print(len(glob.glob("/home/lifetech/python_face/datasets/vivek/*.png")))
#for file in glob.glob("/home/lifetech/python_face/datasets/vivek/*.png"):
#	print(file)
