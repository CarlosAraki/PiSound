
from SimpleCV import *

cam = Camera()

#while True:
img = cam.getImage()
img2 = img.greyscale()
img2.show()
