
from SimpleCV import *

cam = Camera(0,{"width":640 , "height":480})

#while True:
img = cam.getImage()

gray =  img.grayscale()
print gray.getPixel(0,0)
gray.show()
time.sleep(10)
