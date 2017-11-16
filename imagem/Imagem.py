from SimpleCV import Camera,Image
import time
import  sys						#para  argumentos
import 	os						#para fifo
import threading

global largura = 160						#largura do frame
global altura = 120
global xv,yv
								#from SimpleCV import *

def loopdisfarcadoverde(frame):
	contx = 0
	conty = 0
	a = 0
	while i !=largura:  				#while para 160 pixels (tamanho original 640pixels)
		j= 0					#contador para rodar colunas em frame
		while j !=altura:  			#while para 120 pixels (tamanho original 480pixels)
			color =  frame.getPixel(i,j) 	#pego pixel em posicao i,j
			dif = color[1]-color[0] 	#diferenca do G - R
			dif2 = color[1]-color[2]	#diferenca do G - B
			if color[1] > color[0] and color[1] > color[2] and dif > 5 and dif2 > 5:
							#G>R && G>B && dif>5 && dif2>5
				conty = conty+j		#posicao em y
				contx = contx+i		#posicao em x
				a = a+1			#area verde
			j = j+1
		i = i+1
	if a == 0:
		a = 1 					#se nao encontrar verde retorna -1,-1
		contx = -1
		conty = -1
	img.show()
	xv = contx/a					#x do centroide
	yv = conty/a					#y do centroide

def loopdisfarcadoazul(frame):
	contx = 0
	conty = 0
	a = 0
	while i !=largura:  				#while para 160 pixels (tamanho original 640pixels)
		j= 0					#contador para rodar colunas em frame
		while j !=altura:  			#while para 120 pixels (tamanho original 480pixels)
			color =  frame.getPixel(i,j) 	#pego pixel em posicao i,j
			dif2 = color[1]-color[2]	#diferenca do G - B
			dif3 = color[0]-color[2]	#diferenca do R - B
			if color[2] > color[1] and color[2] > color[0] and dif2 < -5 and dif3 < -5:
							#G>R && G>B && dif>5 && dif2>5
				conty = conty+j		#posicao em y
				contx = contx+i		#posicao em x
				a = a+1			#area verde
				img[i,j]=(0,255,0) 	#para ver se esta pegando verde
			j = j+1
		i = i+1
	if a == 0:
		a = 1 					#se nao encontrar verde retorna -1,-1
		contx = -1
		conty = -1
	x = contx/a					#x do centroide
	y = conty/a					#y do centroide
	return  x,y

						#altura  do frame


cam = Camera(0,{"width":largura ,"height":altura}) 	#original  {"width":640 , "height":480}) #307.200 pixels
nome_arq = sys.argv					#nome do arquivo
#if nome_arq[1] == none
#	nome_arq = "fifo"
fd = os.open(nome,os.O_RDWR)				#abrir gravar e fechar arquivo demora 7xE-4s


while True:						#loop de frame a frame
	comeco = time.time()				#tempo inicial
	img = cam.getImage()				#capturo o frame
	t1 = threading.Thread(target = loopdisfarcadoverde,args=[img])
	t1.start()
	[xa,ya]=loopdisfarcadoazul(img)
	t1.join()				#segurador de ordem zero hehehehe

							#time.sleep(4)
							#abrir o arquivo da fifo
	arq =("%f%f%f%f"%(xv,yv,xa,ya))
	os.write(fd,arq)				#fecho o arquivo
	fim = time.time()				#para verificar tempo final
	tempo  = fim - comeco				#tempo do loop
	print tempo
							#del cam #caso nao tiver loop devemos desligar a camera
