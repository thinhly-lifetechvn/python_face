# Creating database 
# It captures images and stores them in datasets 
# folder under the folder name of sub_data 
import cv2, sys, numpy, os 
from datetime import datetime
import time
import dlib

print("opencv Version: {}".format(cv2.__version__))
print("dlib Version: {}".format(dlib.__version__))

haar_file = 'haarcascade_frontalface_default.xml'

# All the faces data will be 
# present this folder 
datasets = 'datasets'


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
	gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) 
	#faces = face_cascade.detectMultiScale(gray, 1.3, 4) 

	faces = detector(im, 1)
	
	print("Number of faces detected: {}".format(len(faces)))
	if len(faces) > 0:
	#	cv2.imwrite('% s/% s.png' % (path, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")), im)  
		for i, d in enumerate(faces):
			print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
				i, d.left(), d.top(), d.right(), d.bottom()))
			w = d.right() - d.left()
			h = d.bottom() - d.top()

			print("Width {}: Heigh: {}".format(
				w, h))	
			face = gray[d.top():d.bottom(), d.left():d.right()] 
			
			face_resize = cv2.resize(face, (width, height)) 
			cv2.imwrite('% s/% s.png' % (path, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")), face)  
	    
    #print('Find face: ' + str(len(faces)))
	#if len(faces) > 0:
	#	for i, d in enumerate(faces):
			#cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 0), 2) 
			#face = gray[y:y + h, x:x + w] 
			#face_resize = cv2.resize(face, (width, height)) 
			#cv2.imwrite('% s/% s.png' % (path, count), face_resize)
			#cv2.imwrite('% s/% s.png' % (path, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")), face_resize)  

	# 	time.sleep(0.3)
	#cv2.imshow('OpenCV', im) 
	key = cv2.waitKey(10) 
	if key == 27: 
		break
	time.sleep(0.3)
