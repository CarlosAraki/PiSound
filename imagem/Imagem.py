from SimpleCV import Camera,Image
import time
import  sys						#para  argumentos
import 	os						#para fifo
import threading
global altura
global xv1,yv1,av1
global xv2,yv2,av2
global xa2,ya2,aa2
								#from SimpleCV import *
largura = 160
altura = 120
def loopdisfarcadoverde(frame,comeco,largura):
	global xv1,yv1,av1
	av1 = 0
	i = comeco
	xv1 = 0
	yv1 = 0
	while i !=largura:  				#while para 160 pixels (tamanho original 640pixels)
		j= 0					#contador para rodar colunas em frame
		while j !=altura:  			#while para 120 pixels (tamanho original 480pixels)
			color =  frame.getPixel(i,j) 	#pego pixel em posicao i,j
			dif = color[1]-color[0] 	#diferenca do G - R
			dif2 = color[1]-color[2]	#diferenca do G - B
			if color[1] > color[0] and color[1] > color[2] and dif > 21 and dif2 > 21:
							#G>R && G>B && dif>5 && dif2>5
				yv1 = yv1+j		#posicao em y
				xv1 = xv1+i		#posicao em x
				av1 = av1+1			#area verde
#				del img[i,j]
			j = j+1
		i = i+1
	if av1 < 30:
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
			color =  frame.getPixel(i,j) 	#pego pixel em posicao i,j
			dif = color[1]-color[0] 	#diferenca do G - R
			dif2 = color[1]-color[2]	#diferenca do G - B
			if color[1] > color[0] and color[1] > color[2] and dif > 21 and dif2 > 21:
							#G>R && G>B && dif>5 && dif2>5
				yv2 = yv2+j		#posicao em y
				xv2 = xv2+i		#posicao em x
				av2 = av2+1			#area verde
#				del img[i,j]
			j = j+1
		i = i+1
	if av2 < 30:
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
			color =  frame.getPixel(i,j) 	#pego pixel em posicao i,j
			dif2 = color[1]-color[2]	#diferenca do G - B
			dif3 = color[0]-color[2]	#diferenca do R - B
			if color[2] > color[1] and color[2] > color[0] and dif2 < -5 and dif3 < -5:
							#G>R && G>B && dif>5 && dif2>5
				y = y+j		#posicao em y
				x = x+i		#posicao em x
				a = a+1			#area verde
#				img[i,j]=(0,0,255) 	#para ver se esta pegando verde
			j = j+1
		i = i+1
	if a < 30 :					#menor que 30 pixels é zero eruido
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
			color =  frame.getPixel(i,j) 	#pego pixel em posicao i,j
			dif2 = color[1]-color[2]	#diferenca do G - B
			dif3 = color[0]-color[2]	#diferenca do R - B
			if color[2] > color[1] and color[2] > color[0] and dif2 < -5 and dif3 < -5:
							#G>R && G>B && dif>5 && dif2>5
				ya2 = ya2+j		#posicao em y
				xa2 = xa2+i		#posicao em x
				aa2 = aa2+1			#area verde
#				img[i,j]=(0,0,255) 	#para ver se esta pegando verde
			j = j+1
		i = i+1
	if aa2 < 30 :					#menor que 30 pixels é zero eruido
		aa2 = 1 					#se nao encontrar verde retorna -1,-1
		xa2 = -1
		ya2 = -1


						#altura  do frame


cam = Camera(0,{"width":largura ,"height":altura}) 	#original  {"width":640 , "height":480}) #307.200 pixels
nome_arq = sys.argv					#nome do arquivo
#if nome_arq[1] == none
#	nome_arq = "fifo"
nome = nome_arq[1]
fd = os.open(nome,os.O_RDWR)				#abrir gravar e fechar arquivo demora 7xE-4s


while True:						#loop de frame a frame
	comeco = time.time()				#tempo inicial
	img = cam.getImage()				#capturo o frame
	t1 = threading.Thread(target = loopdisfarcadoverde,args=[img,1,largura/2])
	t2 = threading.Thread(target = loopdisfarcadoverde2,args=[img,largura/2,largura])
	t3 = threading.Thread(target = loopdisfarcadoazul2,args=[img,largura/2,largura])

	t1.start()
	t2.start()
	t3.start()
	[xa1,ya1,aa1]=loopdisfarcadoazul(img)
	t1.join()				#segurador de ordem zero hehehehe
	t2.join()
	t3.join()
	xv = (xv1+xv2)/(av1+av2)
	yv = (yv1+yv2)/(av1+av2)
	xa = (xa1+xa2)/(aa1+aa2)
	ya =(ya1+ya2)/(aa1+aa2)
							#time.sleep(4)
								#abrir o arquivo da fifo
	arq =("%d %d %d %d "%(xv,yv,xa,ya))
	os.write(fd,arq)
	fim = time.time()				#para verificar tempo final
	tempo  = fim - comeco				#tempo do loop
	print tempo
							#del cam #caso nao tiver loop devemos desligar a camera
