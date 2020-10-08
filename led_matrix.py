
from PIL import Image
from PIL import ImageDraw
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

font = graphics.Font()
font.LoadFont("/home/pi/rpi-rgb-led-matrix/fonts/7x13.bdf")

# Configuration for the matrix
options = RGBMatrixOptions()
options.parallel = 1
options.hardware_mapping = 'adafruit-hat-pwm'  # If you have an Adafruit HAT: 'adafruit-hat'
options.chain_length = 6
options.rows = 64
options.cols = 64
options.brightness = 80  # This seems to be 0 to 100
options.gpio_slowdown = 4