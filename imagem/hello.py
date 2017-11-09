#!/usr/bin/env python
# -*- coding: utf-8 -*-
from SimpleCV import *

cam = Camera(0,{"width":640 , "height":480})

while True:
    arq = open('fifo.txt', 'w')
    img = cam.getImage()
    gray =  img.grayscale()
    gray.show()

    x = 1
    y = 6
    arq.write("%f %f"%(x,y))
    arq.close()
    time.sleep(3)
