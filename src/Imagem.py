import cv2 
import numpy as np
import time
import  sys						
import 	os						
import threading
from multiprocessing.pool import ThreadPool


def findGreen(frameHSV, lowerGreen, upperGreen):

    maskGreen = cv2.inRange(frameHSV, lowerGreen, upperGreen)
    numOfGreen = cv2.countNonZero(maskGreen)
    if numOfGreen > 400:
        momentsGreen = cv2.moments(maskGreen)
        if(momentsGreen["m00"] != 0):
                greenX = int(momentsGreen["m10"]/momentsGreen["m00"])
                greenY = int(momentsGreen["m01"]/momentsGreen["m00"])
    else:
        greenX = -1
        greenY = -1
    
    return greenX, greenY


def findBlue(frameHSV, lowerBlue, upperBlue):

    maskBlue = cv2.inRange(frameHSV, lowerBlue, upperBlue)
    numOfBlue = cv2.countNonZero(maskBlue)
    if numOfBlue > 1200:
        momentsBlue = cv2.moments(maskBlue)
        if(momentsBlue["m00"] != 0):
                blueX = int(momentsBlue["m10"]/momentsBlue["m00"])
                blueY = int(momentsBlue["m01"]/momentsBlue["m00"])
    else:
       blueX = -1
       blueY = -1

    return blueX, blueY


def conv3Dig(number):
    numString = "000"
    if(number == -1):
        numString = ("-01")
    elif(number<10):
        numString = ("00%d" %number)
    elif(number<100):
        numString = ("0%d" %number)
    elif(number>=100):
        numString = ("%d" %number)

    return numString

def mainLoop(fifoName, width, height):
    pool = ThreadPool(processes=1)
    cap = cv2.VideoCapture(0)                        	
    #cap.set(4,width)
    #cap.set(5,height)
    fd = os.open(fifoName,os.O_WRONLY)	
    
    lowerGreen = np.array([33,80,40])
    upperGreen = np.array([102,255,255])	
    lowerBlue = np.array([110,50,50])
    upperBlue = np.array([130,255,255])

    while True:						
        ret, frame = cap.read()
        if ret == 1: 
            comeco = time.time()	
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            t1 = pool.apply_async(findGreen, (hsv, lowerGreen, upperGreen))
            t2 = pool.apply_async(findBlue, (hsv, lowerBlue, upperBlue))


            retT1 = t1.get()
            #retT2 = t2.get()
            retT2 = [-1,-1]

            #print retT1[0], retT1[1], retT2[0], retT2[1]

            arq =("%s %s %s %s "%(conv3Dig(retT1[0]),conv3Dig(retT1[1]),conv3Dig(retT2[0]),conv3Dig(retT2[1])))
            os.write(fd,arq)
            fim = time.time()				#para verificar tempo final
            tempo  = fim - comeco				
							
