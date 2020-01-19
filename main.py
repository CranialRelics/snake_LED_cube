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


# draw = ImageDraw.Draw(image)  # Declare Draw instance before prims
# Draw some shapes into image (no immediate effect on matrix)...
# draw.rectangle((0, 0, 32, 32), fill=(255, 255, 0), outline=(0, 0, 255))
# draw.line((0, 0, 31, 31), fill=(255, 0, 0))
# draw.bitmap()
# draw.line((0, 31, 31, 0), fill=(0, 255, 0))
# draw.rectangle((0, 0, 0, 0), fill=(255, 255, 0), outline=(0, 0, 255))


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


class Snake:
    def __init__(self):
        self.x = []
        self.y = []
        self.step = 1
        self.length = 3
        self.direction = 0

        for i in range(0, self.length):
            self.x.append(0)
            self.y.append(0)

        self.updateCount = 0
        self.updateCountMax = 2

    def update(self):
        self.updateCount += 1
        if self.updateCount > self.updateCountMax:

            # update previous positions
            for i in range(self.length - 1, 0, -1):
                print("self.x[" + str(i) + "] = self.x[" + str(i - 1) + "]")
                self.x[i] = self.x[i - 1]
                self.y[i] = self.y[i - 1]

            # update position of head of snake
            if self.direction == 0:
                self.x[0] = self.x[0] + self.step
            if self.direction == 1:
                self.x[0] = self.x[0] - self.step
            if self.direction == 2:
                self.y[0] = self.y[0] - self.step
            if self.direction == 3:
                self.y[0] = self.y[0] + self.step

            self.updateCount = 0


    def move_right(self):
        self.direction = 0

    def move_left(self):
        self.direction = 1

    def move_up(self):
        self.direction = 2

    def move_down(self):
        self.direction = 3

    def draw(self):
        pass



class LEDCubeMap:
    def __init__(self,rows, cols, pixel_map):
        self.rows = rows
        self.cols = cols
        self.rows = 64
        self.cols = 64
        self.pixels = pixel_map

    def blank(self):
        for i in range(self.rows):
            for j in range(self.cols):
                self.pixels[i, j] = (0, 0, 0)

    def position(self, x, y):
        print(x, y)
        if x > self.rows:
            x = x % self.rows
        elif x < 0:
            x = x % self.rows
            # x += self.rows
        if y > self.cols:
            y = y % self.cols
        elif y < 0:
            y = y % self.cols
            # y += self.cols
        self.blank()
        self.pixels[x, y] = (255, 255, 255)



def main():
    matrix = RGBMatrix(options=options)

    image = Image.new("RGB", (6 * 64, 64))  # Can be larger than matrix if wanted!!

    pixels = image.load()
    # for i in range(image.size[0]):
    #     for j in range(image.size[1]):
    #         if j % 2 == 0:
    #             continue
    #         pixels[i, j] = (i * 2, j * 2, 255)

    cube_map = LEDCubeMap(rows=image.size[0], cols=image.size[1], pixel_map=pixels)
    x = 0
    y = 0
    image.show()
    while True:
        x, y = get(x, y)
        cube_map.position(x, y)
        matrix.Clear()
        matrix.SetImage(image)




if __name__ == "__main__":
    main()