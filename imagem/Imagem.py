
from SimpleCV import *

cam = Camera(0,{"width":640 , "height":480}) #307.200 pixels

#while True:
k= 0
arq = open('fifo.txt', 'w')
img = cam.getImage()
contx = 0
conty = 0
a = 0
i = 0
while i != 640:
	j= 0
	while j !=480:
		color =  img.getPixel(i,j) #pego pixel
		#if color[1] > 100 and color[0] < 50 and color[2] < 50:
		conty = conty +j
		contx = contx+i
		a = a+1
		j = j+1
	i = i+1
# 1 -> 100% 16seg
#2 -> 100% 10 seg
# 4 -> 99% 8.69 seg 
# 8 -> 99% 8.29 seg		
if a == 0:
	a = 1

x = contx/a
y = conty/a
arq.write("%f %f"%(x,y))
arq.close()
#time.sleep(3)
