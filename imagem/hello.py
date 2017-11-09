#!/usr/bin/env python
# -*- coding: utf-8 -*-
from SimpleCV import *

cam = Camera(0,{"width":640 , "height":480}) #307.200 pixels

while True:
    arq = open('fifo.txt', 'w')
    img = cam.getImage()
    color =  img.getPixel(0,0) #pego pixel
    gray.show()

    x = 1
    y = 6
    arq.write("%f %f"%(x,y))
    arq.close()
    time.sleep(3)
