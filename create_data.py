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

def write_log(msg):
	#LOG_FILENAME = 'log.txt'
	LOG_FILENAME = '/home/lifetech/face/log/log.txt'
	logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)

	now = datetime.datetime.now()

	logging.info(now.strftime("%Y-%m-%d %H:%M:%S") + ": " + msg)

	print(now.strftime("%Y-%m-%d %H:%M:%S") + ": " + msg)	

def capture():
	haar_file = '/home/lifetech/face/haarcascade_frontalface_default.xml'

	# All the faces data will be 
	# present this folder 
	datasets = '/home/lifetech/face/datasets'


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
	face_cascade = cv2.CascadeClassifier(haar_file) 
	webcam = cv2.VideoCapture(0) 

	# The program loops until it has 30 images of the face. 

	while True: 
		(_, im) = webcam.read() 
		gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) 
		faces = face_cascade.detectMultiScale(gray, 1.3, 4) 		
		if len(faces) > 0:
			write_log('Find face: ' + str(len(faces)))
			for (x, y, w, h) in faces: 
				#cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 0), 2) 
				face = gray[y:y + h, x:x + w] 
				face_resize = cv2.resize(face, (width, height)) 
				#cv2.imwrite('% s/% s.png' % (path, count), face_resize)
				cv2.imwrite('% s/% s.png' % (path, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")), face_resize)  

			time.sleep(0.5)
		#cv2.imshow('OpenCV', im) 
		#key = cv2.waitKey(10) 
		# if key == 27: 
			# break
		time.sleep(0.3)

def compare():
	while True:
		try:
			while len(glob.glob("/home/lifetech/face/datasets/vivek/*.png")) > 0:				
				for file in glob.glob("/home/lifetech/face/datasets/vivek/*.png"):
					try:
						# Replace sourceFile and targetFile with the image files you want to compare.
						#sourceFile='/home/lifetech/face/datasets/vivek/2019-05-29 16:52:15.837067.png'
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
						
						for faceMatch in response['FaceMatches']:
							position = faceMatch['Face']['BoundingBox']
							confidence = str(faceMatch['Face']['Confidence'])
							write_log('The face at ' +
								   str(position['Left']) + ' ' +
								   str(position['Top']) +
								   ' matches with ' + confidence + '% confidence')

						imageSource.close()
						#imageTarget.close()
						if confidence >= 90:
							pos = getPosition(position['Left'], position['Top'], 200, 300, 600, 300)										
							str_date = parse(os.path.basename(sourceFile).replace('.png',''))
							
							write_log('Hi ' + str(getEmpNameByFacePos(pos)) + ', Your checkin time: ' + str_date.strftime("%Y-%m-%d %H:%M:%S"))
							#write_log('Your checkin time: ' + str_date.strftime("%Y-%m-%d %H:%M:%S"))
							checkinface(pos, str_date.strftime("%Y-%m-%d %H:%M:%S"))
							shutil.move(sourceFile, "/home/lifetech/face/datasets/vivek/ok/")
						else:
							write_log('Image not match in data.')
							shutil.move(sourceFile, "/home/lifetech/face/datasets/vivek/unknow/")
					except Exception as e:
						write_log('Exception message 1: ' + str(e))
						shutil.move(sourceFile, "/home/lifetech/face/datasets/vivek/ufo/")
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
	return myResponse.content

def getEmpNameByFacePos(positionNumber):
	try:
		url = "http://192.168.80.167:5000/getEmpNameByFacePos/" + str(positionNumber)
		myResponse = requests.get(url, verify=True)
		#return myResponse.content.decode("utf8")	
		return myResponse.content
	except Exception as e:
		write_log('[getEmpNameByFacePos]-Exception message: ' + str(e))	
			
write_log("Start camera with OpenCV Version: {}".format(cv2.__version__))

#Start capture thread
write_log('Start capture thread')
#capture()
t1 = threading.Thread(None, capture, None)
t1.start() 

write_log('Start compare thread')
t2 = threading.Thread(None, compare, None)
t2.start() 
#compare()
#t1 = threading.Thread(None, capture, None)
#t1.start() 
#shutil.move("/home/lifetech/face/datasets/vivek/2019-05-29 17:02:29.894378.png", "/home/lifetech/face/datasets/vivek/ok/")
#print(len(glob.glob("/home/lifetech/face/datasets/vivek/*.png")))
#for file in glob.glob("/home/lifetech/face/datasets/vivek/*.png"):
#	print(file)
