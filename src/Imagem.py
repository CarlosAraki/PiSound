import cv2
import numpy as np
import time
import  sys						#para  argumentos
import 	os						#para fifo
import threading
from multiprocessing.pool import ThreadPool

def findGreenAndBlue(frame, xInicial, xFinal, yInicial, yFinal):
    somaXVerde = 0
    somaYVerde = 0
    nPontosVerde = 0
    somaXAzul = 0
    somaYAzul = 0
    nPontosAzul = 0

    i = xInicial
    while i != xFinal:
        j = yInicial
        while j!= yFinal:
            pixel = frame[i][j]
            difGrRe = int(pixel[1]) - int(pixel[0])
            difGrBl = int(pixel[1]) - int(pixel[2])
            difReBl = int(pixel[0]) - int(pixel[2])
            if difGrRe > 20 and difGrBl > 20:
                somaXVerde = somaXVerde + i
                somaYVerde = somaYVerde + j
                nPontosVerde = nPontosVerde + 1
            if difGrBl < -20 and difReBl < -20:
                somaXAzul = somaXAzul + i
                somaYAzul = somaYAzul + j
                nPontosAzul = nPontosAzul + 1
            j = j+1
        i = i+1
    return somaXVerde, somaYVerde, nPontosVerde, somaXAzul, somaYAzul, nPontosAzul


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

def mainLoop(fifoName,aLargura, aAltura):
    pool = ThreadPool(processes=4)
    largura = aLargura
    altura = aAltura
    cam = cv2.VideoCapture(0)                        	
    cam.set(4,largura)
    cam.set(5,altura)
    fd = os.open(fifoName,os.O_WRONLY)				
    ret, frame = cam.read()			       

    #inicializa variaveis
    somaXVerde = 0
    somaYVerde = 0
    nPontosVerde = 0
    somaXAzul = 0
    somaYAzul = 0
    nPontosAzul = 0

    while True:						
            comeco = time.time()				

            t1 = pool.apply_async(findGreenAndBlue, (frame, 0, largura/2, 0, altura/2))
            t2 = pool.apply_async(findGreenAndBlue, (frame, largura/2, largura, 0, altura/2))
            t3 = pool.apply_async(findGreenAndBlue, (frame, 0, largura/2, altura/2, altura))
            t4 = pool.apply_async(findGreenAndBlue, (frame, largura/2, largura, altura/2, altura))
            ret, frame = cam.read()
            retT1 = t1.get()
            retT2 = t2.get()
            retT3 = t3.get()
            retT4 = t4.get()
            nPontosVerde = retT1[2]+retT2[2]+retT3[2]+retT4[2]
            nPontosAzul = retT1[5]+retT2[5]+retT3[5]+retT4[5]

            if nPontosVerde>5:
                somaXVerde = retT1[0]+retT2[0]+retT3[0]+retT4[0]
                somaYVerde = retT1[1]+retT2[1]+retT3[1]+retT4[1]
                xVerde = somaXVerde/nPontosVerde
                yVerde = somaYVerde/nPontosVerde
            else:
                xVerde = -1
                yVerde = -1
                
            if nPontosAzul>5:
                somaXAzul = retT1[3]+retT2[3]+retT3[3]+retT4[3]
                somaYAzul = retT1[4]+retT2[4]+retT3[4]+retT4[4]
                xAzul = somaXAzul/nPontosAzul
                yAzul = somaYAzul/nPontosAzul
            else:
                xAzul = -1
                yAzul = -1
                
            print xVerde, yVerde, xAzul, yAzul

            arq =("%s %s %s %s "%(conv3Dig(xVerde),conv3Dig(yVerde),conv3Dig(xAzul),conv3Dig(yAzul)))
            os.write(fd,arq)
            fim = time.time()				#para verificar tempo final
            tempo  = fim - comeco				
            print tempo
							
