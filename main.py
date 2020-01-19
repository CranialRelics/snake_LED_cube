#!/usr/bin/env python

# (This is an example similar to an example from the Adafruit fork
#  to show the similarities. Most important difference currently is, that
#  this library wants RGB mode.)
#
# A more complex RGBMatrix example works with the Python Imaging Library,
# demonstrating a few graphics primitives and image loading.
# Note that PIL graphics do not have an immediate effect on the display --
# image is drawn into a separate buffer, which is then copied to the matrix
# using the SetImage() function (see examples below).
# Requires rgbmatrix.so present in the same directory.

# PIL Image module (create or load images) is explained here:
# http://effbot.org/imagingbook/image.htm
# PIL ImageDraw module (draw shapes to images) explained here:
# http://effbot.org/imagingbook/imagedraw.htm

from PIL import Image
from PIL import ImageDraw
import time
from rgbmatrix import RGBMatrix, RGBMatrixOptions

# Configuration for the matrix
options = RGBMatrixOptions()
options.parallel = 1
options.hardware_mapping = 'adafruit-hat-pwm'  # If you have an Adafruit HAT: 'adafruit-hat'
options.chain_length = 6
options.rows = 64
options.cols = 64
options.brightness = 100  # This seems to be 0 to 100

matrix = RGBMatrix(options = options)

# RGB example w/graphics prims.
# Note, only "RGB" mode is supported currently.
image = Image.new("RGB", (64, 6*64))  # Can be larger than matrix if wanted!!
draw = ImageDraw.Draw(image)  # Declare Draw instance before prims
pixels = image.load()
# Draw some shapes into image (no immediate effect on matrix)...
# for i in range(image.size[0]):
#     for j in range(image.size[1]):
#         if j % 2 == 0:
#             continue
#         pixels[i, j] = (i,j, 100)
# image.show()
# matrix.Clear()
# matrix.SetImage(image)
draw.rectangle((0, 0, 32, 32), fill=(255, 255, 0), outline=(0, 0, 255))
draw.line((0, 0, 31, 31), fill=(255, 0, 0))
# draw.bitmap()
# draw.line((0, 31, 31, 0), fill=(0, 255, 0))
# draw.rectangle((0, 0, 0, 0), fill=(255, 255, 0), outline=(0, 0, 255))


# # Then scroll image across matrix...
# for _ in range(10):
#     for n in range(0, 64*6):  # Start off top-left, move off bottom-right
#         matrix.Clear()
#         matrix.SetImage(image, n, 0)
#         time.sleep(0.05)

import sys,tty,termios
class _Getch:
    def __call__(self):
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(3)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

def get(x, y):
        inkey = _Getch()
        while(1):
                k=inkey()
                if k!='':break
        if 'q' in k:
            sys.exit()
        elif k=='\x1b[A' or 'w' in k:
            y += 1
            # return 'up'
            return x, y
        elif k=='\x1b[B' or 's' in k:
            y -= 1
            # return  "down"
            return x, y
        elif k=='\x1b[C' or 'd' in k:
            x += 1
            # return  "right"
            return x, y
        elif k=='\x1b[D' or 'a' in k:
            x -= 1
            # return  "left"
            return x, y
        # else:
        #     print("not an arrow key!")
        #     # sys.exit()


x = 0
y = 0
matrix.SetImage(image, y, x)
print('b')
try:
    while True:
            x, y = get(x, y)
            matrix.Clear()
            matrix.SetImage(image, y, x)
            time.sleep(0.05)
except KeyboardInterrupt:
    pass

matrix.Clear()