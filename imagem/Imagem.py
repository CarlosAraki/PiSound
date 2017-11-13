from SimpleCV import Camera,Image,Color
import time
#from SimpleCV import *
cam = Camera(0,{"width":320 , "height":240})  # {"width":640 , "height":480}) #307.200 pixels

#while True:
k= 0
arq = open('fifo.txt', 'w')
img = cam.getImage()
contx = 0
conty = 0
a = 0
i = 0
while i !=320:   # 640:
	j= 0
	while j !=240:  # 480:
		color =  img.getPixel(i,j) #pego pixel
		#if color[1] > 150  and color[0] < 140 and color[2] < 140:
		dif = color[1]-color[0] 
		dif2 = color[1]-color[2]
		if color[1] > color[0] and color[1] > color[2] and dif > 5 and dif2 > 5:
			conty = conty+j
			contx = contx+i
			a = a+1
			img[i,j]=(0,255,0) #para ver se esta pegando verde
		j = j+1
	i = i+1
# 1 -> 100% 16seg
#2 -> 100% 10 seg
# 4 -> 99% 8.69 seg 
# 8 -> 99% 8.29 seg	
#if color[1] > 200 and color[0] > 200 and color[2] > 200: -> se utilizarmos uma mao com luz	
if a == 0:
	a = 1
img.show()
x = contx/a
y = conty/a
time.sleep(4)
arq.write("%f %f"%(x,y))
arq.close()
del cam
