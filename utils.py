import sys

import tty
import termios

# _Getch and get() are useful for doing keyboard control of cube
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


def get():
        inkey = _Getch()
        while True:
                k = inkey()
                if k != '':
                    break
        if 'q' in k:
            sys.exit()
        elif k == '\x1b[A' or 'w' in k:
            # return 'up'
            return 2
        elif k == '\x1b[B' or 's' in k:
            # return  "down"
            return 3
        elif k == '\x1b[C' or 'd' in k:
            # return  "right"
            return 0
        elif k == '\x1b[D' or 'a' in k:
            # return  "left"
            return 1
        else:
            return None


class LEDCubeMap:
    def __init__(self, rows, cols, pixel_input_map):
        self.rows = rows
        self.cols = cols
        self.max_x = rows - 1
        self.max_y = cols - 1
        self.pixels = pixel_input_map
        self.pixel_map = {}

    def blank(self):
        for i in range(self.rows):
            for j in range(self.cols):
                self.pixels[i, j] = (0, 0, 0)

    def set_map_point(self, x, y, color=(255, 255, 255)):
        try:
            self.pixels[x, y] = color
        except IndexError:
            print(f"Error! X: {x} Y: {y}")
            raise IndexError

    def unset_map_point(self, x, y):
        self.pixels[x, y] = (0, 0, 0)

    def position(self, x, y):

        if x > self.max_x:
            x = x % self.rows
        elif x < 0:
            x = x % self.rows
        if y > self.max_y:
            y = y % self.cols
        elif y < 0:
            y = y % self.cols
        self.blank()
        self.pixels[x, y] = (255, 255, 255)
        print(x, y)
        return x, y
