from SimpleCV import Camera,Image
import time
import  sys						#para  argumentos
import 	os						#para fifo

							#from SimpleCV import *
largura = 160						#largura do frame
altura = 120						#altura  do frame
cam = Camera(0,{"width":largura ,"height":altura}) 	#original  {"width":640 , "height":480}) #307.200 pixels
nome_arq = sys.argv					#nome do arquivo
							#abrir gravar e fechar arquivo demora 7xE-4s
print 4
while True:						#loop de frame a frame
	comeco = time.time()				#tempo inicial
	img = cam.getImage()				#capturo o frame
	contxr = 0					#contador para posicoes x  dos pixels vermelhos
	contyr = 0					#contador para posicoes y dos  pixels vermelhos
	contx = 0					#contador para posicoes x dos pixels verdes
	conty = 0					#contador para posicoes y dos pixels verdes
	ar= 0						#contador de numero de pixels vermelhos para centroide
	a = 0						#contador de numero de pixels em calculo de centroide
	i = 0						#contador para  rodar linha no frame
	while i !=largura:  				#while para 160 pixels (tamanho original 640pixels)
		j= 0					#contador para rodar colunas em frame
		while j !=altura:  			#while para 120 pixels (tamanho original 480pixels)
			color =  img.getPixel(i,j) 	#pego pixel em posicao i,j
			dif = color[1]-color[0] 	#diferenca do G - R
			dif2 = color[1]-color[2]	#diferenca do G - B
			dif3 = color[0]-color[2]	#diferenca do R - B
			if color[1] > color[0] and color[1] > color[2] and dif > 5 and dif2 > 5:
							#G>R && G>B && dif>5 && dif2>5
				conty = conty+j		#posicao em y
				contx = contx+i		#posicao em x
				a = a+1			#area verde
				img[i,j]=(0,255,0) 	#para ver se esta pegando verde
#			if color[0] > color[1] and color[0] > color[2] and dif < -5 and dif3 >5:
							#R>G &&R>B && dif <-5 and dif3 > 5
#				contyr = contyr+j
#				contxr = contxr+i
#				ar = ar+1
#				img[i,j] = (255,0,0)	#para ver se esta pegando vermelho
			j = j+1
		i = i+1
	if a == 0:
		a = 1 					#se nao encontrar verde retorna -1,-1
		contx = -1
		conty = -1
#	if ar == 0:
#		ar = 1
#		contxr = -1
#		contyr = -1 
	img.show()
	x = contx/a					#x do centroide
	y = conty/a					#y do centroide
#	xr = contxr/ar
#	yr = contyr/ar
							#time.sleep(4)
							#abrir o arquivo da fifo
	arq =("%f %f"%(x,y))	
#	arq.write("%f %f %f %f"%(x,y,xr,yr))		#escrevo x,y do centroide na fifo
	os.write(nome_arq,arq)				#fecho o arquivo
	fim = time.time()				#para verificar tempo final
	tempo  = fim - comeco				#tempo do loop
	print tempo
							#del cam #caso nao tiver loop devemos desligar a camera
