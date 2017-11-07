
from SimpleCV import *

cam = Camera()

#while True:
img = cam.getImage()
disp = Display()
img.save(disp)
