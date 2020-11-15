import cv2
from glob import glob
import numpy as np
import pickle
from sklearn.preprocessing import normalize
from sklearn.neural_network import MLPClassifier
import sys
from collections import Counter
from os import listdir
import pandas as pd
import os
from time import gmtime, strftime

#list for wrongly classified 
img_list = []
classi = []
check_list = []
#takes an image and returns array with all digits pixels in it
def val(im, filename, erode_t=1):
	#copy becuase will be edited
	img = im.copy()

	#make an output, convert to grayscale and apply thresh-hold
	out = np.zeros(im.shape,np.uint8)
	gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
	thresh = cv2.adaptiveThreshold(gray,255,1,1,11,2)
	# cv2.imshow('thresh', thresh)
	if erode_t == 1:
		kernel = np.ones((2,2),np.uint8)
		dilation = cv2.dilate(thresh,kernel,iterations = 1)
		erode = cv2.erode(dilation, kernel, iterations = 2)
		contours,hierarchy = cv2.findContours(erode,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
	elif erode_t == 2:
		kernel = np.ones((2,2),np.uint8)
		dilation = cv2.dilate(thresh,kernel,iterations = 1)
		erode = cv2.erode(dilation, kernel, iterations = 1)
		contours,hierarchy = cv2.findContours(erode,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
	elif erode_t == 3:
		kernel = np.ones((2,2),np.uint8)
		dilation = cv2.dilate(thresh,kernel,iterations = 1)
		contours,hierarchy = cv2.findContours(dilation,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
	else:
		contours,hierarchy = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)

	#create empty return list
	samples =  np.empty((0,100))

	#for every contour if area large enoug to be digit add the box to list
	li = []
	for cnt in contours:
		if cv2.contourArea(cnt)>20:
			[x,y,w,h] = cv2.boundingRect(cnt)
			li.append([x,y,w,h])
	#sort list so it read from right to left
	li = sorted(li,key=lambda x: x[0], reverse=True)
	#loop over all digits
	for i in li:
		#unpack data
		x,y,w,h = i[0], i[1], i[2], i[3]

		#check if large enough to be digit but small enough to ignore rest
		if  h>16 and h<30 and w<40 and w>9:
			# print(w,h)

		#draw rectangle with thresh-hold and shape correct form
			if erode_t == 1:
				cv2.rectangle(im,(x-1,y-1),(x+w-1,y+h-1),(0,255,0),1)
				roi = thresh[y-1:y+h-1,x-1:x+w-1]
			else:
				cv2.rectangle(im,(x,y),(x+w,y+h),(0,255,0),1)
				roi = thresh[y:y+h,x:x+w]
			roismall = cv2.resize(roi,(10,10))
			sample = roismall.reshape((1,100))
			samples = np.append(samples,sample,0)

			#if user wants images shown
			if show_img:
				cv2.namedWindow('View Power',cv2.WINDOW_NORMAL)
				cv2.resizeWindow('View Power', 1600,600)
				cv2.imshow('View Power', im)
				#show for 100 ms and check if exit called (esc key)
				key = cv2.waitKey(0)
				if key == ord('q'):
					sys.exit()
				#print what the NN would classify the digits as
				print(int(classify(samples)))
	#if full number lower than 10m, add to wrongly classified list
	try:
		classification = classify(samples)
		if len(classification) < 9 and erode_t != 4:
			erode_t += 1
			return val(img, filename, erode_t)
		if int(classification) < 20000000 and len(classification) > 4 or int(classification) > 450000000:
			if np.sum(img) not in check_list:
				print("HH")
				img_list.append(img)
				check_list.append(np.sum(img))
				classi.append(filename)
				return None
			return False
		if len(classification) not in (8,9,10):
			return False
	except:
		return False

	#return all digits found
	return samples

#get list of found digits and runs it through NN
def classify(data):
	clas = []

	#run every found digit through NN
	for i in data:
		clas.append(int(clf.predict([i])[0]))

	#reverse list and add all together in 1 integer to find final power
	clas.reverse()
	clas = map(str, clas)
	clas = ''.join(clas)
	return clas


filename = 'finalized_model.sav'
clf = pickle.load(open(filename, 'rb'))

#check if user wants to see image classification animation
# show_img = input("Want to show all images being classified? y/n ")
# if show_img == 'y':
#     show_img = True
# else:
show_img = False
count = 0
#ask user which kingdom to check
# vs = cv2.VideoCapture('video0.mov')
dirs = listdir('TestingPictures/')
for kingdom in dirs:
	print(kingdom)
	power = []
	img_list = []
	path = 'TestingPictures/' + kingdom + '/'
	for filename in sorted(os.listdir(path)):
		if filename.endswith(".jpg") or filename.endswith(".png") or filename.endswith(".PNG") or filename.endswith(".JPG"):
			print(filename)
			print(len(img_list))

			img = cv2.imread(path + filename)
			# check to see if we have reached the end of the stream
			if img is None:
				break
			img = cv2.resize(img, (1728, 1080))
			y,x,_ = img.shape
			img = img[int(y/4):y-int(y/20), int(x/1.5):x]
			# cv2.imshow('1', img)
			# cv2.waitKey(0)
			# break
			gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
			thresh = cv2.adaptiveThreshold(gray,255,1,1,11,2)

			#find conours
			contours,hierarchy = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
			#create empty return list
			samples =  np.empty((0,100))

			#for every contour if area large enoug to be digit add the box to list
			li = []
			for cnt in contours:
				if cv2.contourArea(cnt)>2000:# and cv2.contourArea(cnt)<3000:
					[x,y,w,h] = cv2.boundingRect(cnt)
					li.append([x,y,w,h])
			#sort list so it read from right to left
			li = sorted(li,key=lambda x: x[0], reverse=True)
			#loop over all digits
			for i in li:
				#unpack data
				x,y,w,h = i[0], i[1], i[2], i[3]

				#check if large enough to be digit but small enough to ignore rest
				if  w<200 and h<50:
					#draw rectangle with thresh-hold and shape correct form
					# cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
					im = img[y-10:y+h+10, x-10:x+w+10]
					# cv2.imshow('1', im)
					# cv2.waitKey(0)
					data = val(im.copy(), filename)
					if data is not None and not isinstance(data, bool):

					# try:
						power.append(int(classify(data)))
					else:
						if np.sum(im) not in check_list:
							count += 1
							# print("HHHH",count)
							img_list.append(im)
							check_list.append(np.sum(im))
					# except:
						# pass

	power = list(set(power))
	print(count)
	#handle wrongly classified cases 
	print(f"Could not read {len(img_list)} numbers. They will be shown to you, type them please!")
	print("You can use enter to submit number and backspace to delete and escape to quit")

	#loop over all wrongly classified images and let user enter power manually
	# img_list_dict = {48:0, 49:1, 50:2, 51:3, 52:4, 53:5, 54:6, 55:7, 56:8, 57:9}
	# for index, im in enumerate(img_list): 
	# 	add = ""
	# 	while True:
	# 		cv2.imshow('View Power', im)
	# 		print(classi[index])
	# 		key = cv2.waitKey(0)
	# 		back = False
	# 		if key == 27:
	# 			sys.exit()
	# 		elif key == 8:
	# 			back = True
	# 		elif key == 13:
	# 			print('\n')
	# 			break
	# 		elif key == ord('q'):
	# 			break
	# 		elif key in img_list_dict.keys():
	# 			number = img_list_dict[key]

	# 		if not back:
	# 			add = add + str(number)
	# 		else:
	# 			add = add[:-1]
	# 		print(add)
	# 	power.append(int(add))

	#sort whole power list from large to small
	sorted_list = sorted(power, reverse=True)
	df = pd.DataFrame(columns=['Power', 'Date'])
	sorted_list.append(sum(sorted_list))

	df['Power'] = sorted_list
	df['Index'] = df.index

	df['Index'].iloc[-1] = 'Total'
	# df = df.reset_index(drop=True)
	date = strftime("%Y-%m-%d %H:%M:%S", gmtime())

	df = df[['Index', 'Power', 'Date']]
	df['Date'] = date
	
	# df.index.name = 'Index'
	df.to_excel(path + kingdom + '_list.xlsx', index=False)