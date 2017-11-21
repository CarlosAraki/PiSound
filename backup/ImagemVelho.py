import cv2
import numpy as np
import time
import  sys						#para  argumentos
import 	os						#para fifo
import threading
from multiprocessing.pool import ThreadPool
global altura
global largura
global xv1,yv1,av1
global xv2,yv2,av2
global xa2,ya2,aa2

largura = 160
altura = 120
								#from SimpleCV import *
def loopdisfarcadoverde(frame,comeco,largura):
	global xv1,yv1,av1
	av1 = 0
	i = comeco
	xv1 = 0
	yv1 = 0
	while i !=largura:  				#while para 160 pixels (tamanho original 640pixels)
		j= 0					#contador para rodar colunas em frame
		while j !=altura:  			#while para 120 pixels (tamanho original 480pixels)
			color =  frame[i][j] 	#pego pixel em posicao i,j
			dif = int(color[1])-int(color[0]) 	#diferenca do G - R
			dif2 = int(color[1])-int(color[2])	#diferenca do G - B
			if color[1] > color[0] and color[1] > color[2] and dif > 21 and dif2 > 21:
							#G>R && G>B && dif>5 && dif2>5
				yv1 = yv1+j		#posicao em y
				xv1 = xv1+i		#posicao em x
				av1 = av1+1			#area verde
			j = j+1
		i = i+1
	if av1 < 5:
		av1 = 1 					#se nao encontrar verde retorna -1,-1
		xv1 = -1
		yv1 = -1
def loopdisfarcadoverde2(frame,comeco,largura):
	global xv2,yv2,av2
	xv2 = 0
	yv2 = 0
	av2 = 0
	i = comeco
	while i !=largura:  				#while para 160 pixels (tamanho original 640pixels)
		j= 0					#contador para rodar colunas em frame
		while j !=altura:  			#while para 120 pixels (tamanho original 480pixels)
			color =  frame[i][j] 	#pego pixel em posicao i,j
			dif = int(color[1])-int(color[0]) 	#diferenca do G - R
			dif2 = int(color[1])-int(color[2])	#diferenca do G - B
			if color[1] > color[0] and color[1] > color[2] and dif > 21 and dif2 > 21:
							#G>R && G>B && dif>5 && dif2>5
				yv2 = yv2+j		#posicao em y
				xv2 = xv2+i		#posicao em x
				av2 = av2+1			#area verde
			j = j+1
		i = i+1
	if av2 < 5:
		av2 = 1 					#se nao encontrar verde retorna -1,-1
		xv2 = -1
		yv2 = -1

def loopdisfarcadoazul(frame,comeco,largura):
	x = 0
	y = 0
	a = 0
	i = comeco
	while i !=largura:  				#while para 160 pixels (tamanho original 640pixels)
		j= 0					#contador para rodar colunas em frame
		while j !=altura:  			#while para 120 pixels (tamanho original 480pixels)
			color =  frame[i][j]     	#pego pixel em posicao i,j
			dif2 = int(color[1])-int(color[2]) 	#diferenca do G - R
			dif3 = int(color[0])-int(color[2])	#diferenca do G - B
			if color[2] > color[1] and color[2] > color[0] and dif2 < -15 and dif3 < -15:
							#G>R && G>B && dif>5 && dif2>5
				y = y+j		#posicao em y
				x = x+i		#posicao em x
				a = a+1			#area verde
			j = j+1
		i = i+1
	if a < 5:
		a = 1 					#se nao encontrar verde retorna -1,-1
		x = -1
		y = -1
	return  x,y,a
def loopdisfarcadoazul2(frame,comeco,largura):
	global xa2,ya2,aa2

	xa2 = 0
	ya2 = 0
	aa2 = 0
	i = comeco
	while i !=largura:  				#while para 160 pixels (tamanho original 640pixels)
		j= 0					#contador para rodar colunas em frame
		while j !=altura:  			#while para 120 pixels (tamanho original 480pixels)
			color =  frame[i][j] 	#pego pixel em posicao i,j
			dif2 = int(color[1])-int(color[2]) 	#diferenca do G - R
			dif3 = int(color[0])-int(color[2])	#diferenca do G - B
			if color[2] > color[1] and color[2] > color[0] and dif2 < -15 and dif3 < -15:
							#G>R && G>B && dif>5 && dif2>5
				ya2 = ya2+j		#posicao em y
				xa2 = xa2+i		#posicao em x
				aa2 = aa2+1			#area verde
			j = j+1
		i = i+1
	if aa2 < 5 :
		aa2 = 1 					#se nao encontrar verde retorna -1,-1
		xa2 = -1
		ya2 = -1


						#altura  do frame
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
    nome = fifoName
    fd = os.open(nome,os.O_WRONLY)				
    ret, img = cam.read()				#capturo o frame

    #inicializa variaveis
    somaXVerde = 0
    somaYVerde = 0
    nPontosVerde = 0
    somaXAzul = 0
    somaYAzul = 0
    nPontosAzul = 0
    


    while True:						#loop de frame a frame
            comeco = time.time()				#tempo inicial
            #t1 = threading.Thread(target = loopdisfarcadoverde,args=[img,0,largura/2])
            #t2 = threading.Thread(target = loopdisfarcadoverde2,args=[img,largura/2,largura])
            #t3 = threading.Thread(target = loopdisfarcadoazul2,args=[img,largura/2,largura])
            #t1.start()
            #t2.start()
            #t3.start()
            #[xa1,ya1,aa1]=loopdisfarcadoazul(img,0,largura/2)
            #t1.join()				#segurador de ordem zero hehehehe
            #t2.join()
            #t3.join()
            #xv = (xv1+xv2)/(av1+av2)
            #yv = (yv1+yv2)/(av1+av2)
            #xa = (xa1+xa2)/(aa1+aa2)
            #ya =(ya1+ya2)/(aa1+aa2)
            #print xv,yv,xa,ya
                                                                    
            t1 = pool.apply_async(findGreenAndBlue, (img, 0, largura/2, 0, altura/2))
            t2 = pool.apply_async(findGreenAndBlue, (img, largura/2, largura, 0, altura/2))
            t3 = pool.apply_async(findGreenAndBlue, (img, 0, largura/2, altura/2, altura))
            t4 = pool.apply_async(findGreenAndBlue, (img, largura/2, largura, altura/2, altura))
            ret, img = cam.read()
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
							
