from SimpleCV import *

cam = Camera(0,{"width":640 , "height":480}) #307.200 pixels

while True:
    k= 0
    arq = open('fifo.txt', 'w')
    img = cam.getImage()


    for i = 0 to 639
        for j = 0 to 479
            color =  img.getPixel(i,j) #pego pixel
            if color[1] > 200 and color[0] < 50 and color[2] < 50
                pos[k]=  (i,j)
    #gray.show()

    x = 1
    y = 6
    arq.write("%f %f"%(x,y))
    arq.close()
    time.sleep(3)
