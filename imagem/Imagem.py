from SimpleCV import Camera,Image
import time
#from SimpleCV import *
largura = 160						#largura do frame
altura = 120						#altura  do frame
cam = Camera(0,{"width":largura ,"height":altura}) 	#original  {"width":640 , "height":480}) #307.200 pixels
nome_arq = "fifo"					#nome do arquivo
arq = open(nome_arq,'w')				#zero o arquivo
arq.close()

while True:						#loop de frame a frame
	comeco = time.time()				#tempo inicial
	arq = open(nome_arq, 'a')			#abrir o arquivo da fifo
	img = cam.getImage()				#capturo o frame
	contx = 0					#contador para posicoes x dos pixels verdes
	conty = 0					#contador para posicoes y dos pixels verdes
	a = 0						#contador de numero de pixels em calculo de centroide
	i = 0						#contador para  rodar linha no frame
	while i !=largura:  				#while para 160 pixels (tamanho original 640pixels)
		j= 0					#contador para rodar colunas em frame
		while j !=altura:  			#while para 120 pixels (tamanho original 480pixels)
			color =  img.getPixel(i,j) 	#pego pixel em posicao i,j
			dif = color[1]-color[0] 	#diferenca do G - R
			dif2 = color[1]-color[2]	#diferenca do G - B
			if color[1] > color[0] and color[1] > color[2] and dif > 5 and dif2 > 5:
							#G>R && G>B && dif>5 && dif2>5
				conty = conty+j		#posicao em y
				contx = contx+i		#posicao em x
				a = a+1			#area verde
							#img[i,j]=(0,255,0) #para ver se esta pegando verde
			j = j+1
		i = i+1
	if a == 0:
		a = 1 					#se nao encontrar verde retorna -1,-1
		contx = -1
		conty = -1
							#img.show()
	x = contx/a					#x do centroide
	y = conty/a					#y do centroide
							#time.sleep(4)
	arq.write("%f %f \n"%(x,y))			#escrevo x,y do centroide na fifo
	arq.close()					#fecho o arquivo
	fim = time.time()				#para verificar tempo final
	tempo  = fim - comeco				#tempo do loop
	print tempo
							#del cam #caso nao tiver loop devemos desligar a camera
