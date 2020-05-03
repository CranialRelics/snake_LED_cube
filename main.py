import random
import time
from collections import namedtuple

from PIL import Image
from PIL import ImageDraw
import time
from rgbmatrix import RGBMatrix, RGBMatrixOptions

from control_pad import Controller

from grove import imu9250

# Configuration for the matrix
options = RGBMatrixOptions()
options.parallel = 1
options.hardware_mapping = 'adafruit-hat-pwm'  # If you have an Adafruit HAT: 'adafruit-hat'
options.chain_length = 6
options.rows = 64
options.cols = 64
options.brightness = 100  # This seems to be 0 to 100

TIME_STEP_LENGTH = 0.2


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

def get():
        inkey = _Getch()
        while(1):
                k=inkey()
                if k!='':break
        if 'q' in k:
            sys.exit()
        elif k=='\x1b[A' or 'w' in k:
            # return 'up'
            return 2
        elif k=='\x1b[B' or 's' in k:
            # return  "down"
            return 3
        elif k=='\x1b[C' or 'd' in k:
            # return  "right"
            return 0
        elif k=='\x1b[D' or 'a' in k:
            # return  "left"
            return 1
        else:
            return None

class SensorState:
    def __init__(self):
        self.x_states = []
        self.y_states = []
        self.z_states = []
        self.x = 0
        self.y = 0
        self.z = 0

    def update(self, states):
        self.x_states.append(states['x'])
        self.y_states.append(states['y'])
        self.z_states.append(states['z'])
        if len(self.x_states) > 4:
            self.x_states.pop(0)
        if len(self.y_states) > 4:
            self.y_states.pop(0)
        if len(self.z_states) > 4:
            self.z_states.pop(0)

    def get_states(self):
        self.x = sum(self.x_states) / len(self.x_states)
        self.y = sum(self.y_states) / len(self.y_states)
        self.z = sum(self.z_states) / len(self.z_states)
        return self.x, self.y, self.z


class Snake:
    def __init__(self, cube_map, use_controller=False, imu=None):
        self.cube_map = cube_map
        self.imu = imu
        if use_controller:
            self.controller = Controller()
        else:
            self.controller = None

        self.side_up = 'n'
        self.acl_state = SensorState()
        self.gyro_state = SensorState()

        self.x = []
        self.y = []
        self.step = 1
        self.length = 3
        self.control = 0
        self.score = 0

        self.found_food = False
        self.food_x = None
        self.food_y = None
        self.new_food_pos()


        # Starting points
        self.x = [32, 31, 31]
        self.y = [32, 32, 32]
        self.x_pos = 32
        self.y_pos = 32

        self.face = "t"
        self.direction = "e"
        self.directions = ['u', 'd', 'n', 'e', 's', 'w']
        self.updateCount = 0
        self.updateCountMax = 0
        # Top NE(0,0) NW(0,63) SW(63, 63) SE(63, 0)
        # North TE(192,63) TW(192,0) BE(255,63) BW(255,0)
        # East ST(128,63) NT(128,0) BS(191,63) BN(191,0)
        # South TW(64,63) TE(64,0) BE(127,0) BW(127,63)
        # West TN(256,63) TS(256,0) BN(319,63) BS(319,0)
        # Bottom NW(320,63) NE(383,63) SW(320,0) SE(383,0)

        Pixel = namedtuple("Pixel", "x y")
        Corner = namedtuple("Corner", "edges pixels")
        Face = namedtuple("Face", "corners edges")

        self.change_direction_map = {
            'tnr':'e',
            'tnl': 'w',
            'tsr': 'w',
            'tsl': 'e',
            'ter': 's',
            'tel': 'n',
            'twr': 'n',
            'twl': 's',

            'bnr': 'w',
            'bnl': 'e',
            'bsr': 'e',
            'bsl': 'w',
            'ber': 'n',
            'bel': 's',
            'bwr': 's',
            'bwl': 'n',

            'ner': 't',
            'nel': 'b',
            'nwr': 'b',
            'nwl': 't',
            'ntr': 'w',
            'ntl': 'e',
            'nbr': 'e',
            'nbl': 'w',

            'ser': 'b',
            'sel': 't',
            'swr': 't',
            'swl': 'b',
            'str': 'e',
            'stl': 'w',
            'sbr': 'w',
            'sbl': 'e',

            'etr': 'n',
            'etl': 's',
            'ebr': 's',
            'ebl': 'n',
            'enr': 'b',
            'enl': 't',
            'esr': 't',
            'esl': 'b',

            'wtr': 's',
            'wtl': 'n',
            'wbr': 'n',
            'wbl': 's',
            'wnr': 't',
            'wnl': 'b',
            'wsr': 'b',
            'wsl': 't',

        }
        self.transition_map = {}
        # keys are [single char for face][single char for direction][x coord][y coord]:(x,y)
        # Top transitions

        for i in range(64):
            # Top North
            self.transition_map[f"tn0.{i}"] = (192, 63 - i, 'nb')
            self.transition_map[f"nt192.{63 - i}"] = (0, i, 'ts')
            # Top West
            self.transition_map[f"tw{i}.63"] = (256, 63 - i, 'wb')
            self.transition_map[f"wt256.{63 - i}"] = (i, 63, 'te')
            # Top East
            self.transition_map[f"te{i}.0"] = (128, i, 'eb')
            self.transition_map[f"et128.{i}"] = (i, 0, 'tw')
            # Top South
            self.transition_map[f"ts63.{i}"] = (64, i, 'sb')
            self.transition_map[f"st64.{i}"] = (63, i, 'tn')
            # North East
            self.transition_map[f"ne{i+192}.63"] = (128 + i, 0, 'es')
            self.transition_map[f"en{128 + i}.0"] = (i+192, 63, 'nw')
            # North West
            self.transition_map[f"nw{i+192}.0"] = (256 + i, 63, 'ws')
            self.transition_map[f"wn{256 + i}.63"] = (i+192, 0, 'ne')
            # South West
            self.transition_map[f"sw{i+64}.63"] = (256 + i, 0, 'wn')
            self.transition_map[f"ws{256 + i}.0"] = (i+64, 63, 'se')
            # South East
            self.transition_map[f"se{i+64}.0"] = (i+128, 63, 'en')
            self.transition_map[f"es{i+128}.63"] = (i+64, 0, 'sw')
            # Bottom North
            self.transition_map[f"bn{i+320}.63"] = (255, i, 'nt')
            self.transition_map[f"nb255.{i}"] = (i+320, 63, 'bs')
            # Bottom East
            self.transition_map[f"be383.{i}"] = (191, 63 - i, 'et')
            self.transition_map[f"eb191.{63 - i}"] = (383, i, 'bw')
            # Bottom West
            self.transition_map[f"bw320.{i}"] = (319, i, 'wt')
            self.transition_map[f"wb319.{i}"] = (320, i, 'be')
            # Bottom South
            self.transition_map[f"bs{320+i}.0"] = (127, 63 - i, 'st')
            self.transition_map[f"sb127.{63 - i}"] = (320+i, 0, 'bn')

        self.coord_map = {
                            "tn": "xd",
                            "nt": "xd",
                            "tw": "yu",
                            "wt": "xd",
                            "te": "yd",
                            "et": "xd",
                            "ts": "xu",
                            "st": "xd",
                            "ne": "yu",
                            "en": "yd",
                            "nw": "yd",
                            "wn": "yu",
                            "sw": "yu",
                            "ws": "yd",
                            "se": "yd",
                            "es": "yu",
                            "bn": "yu",
                            "nb": "xu",
                            "be": "xu",
                            "eb": "xu",
                            "bw": "xd",
                            "wb": "xu",
                            "bs": "yd",
                            "sb": "xu"
                          }

    def new_food_pos(self):
        while True:
            self.food_x = random.randint(0,319) # (0, 319) to exclude bottom, (0, 383) to include bottom
            self.food_y = random.randint(0,63)
            if self.food_x not in self.x:
                if self.food_y not in self.y:
                    break
        self.cube_map.set_map_point(self.food_x, self.food_y, color=(0,255,0))


    def get_side_up(self):
        accl = self.imu.readAccel()
        gyro = self.imu.readGyro()
        self.acl_state.update(accl)
        self.gyro_state.update(gyro)
        gx, gy, gz = self.gyro_state.get_states()
        if gx < 20 and gy < 20 and gz < 20:
            ax, ay, az = self.acl_state.get_states()
            if az > 0.9:
                self.side_up = 't'
            elif az < -0.9:
                self.side_up = 'b'
            elif ax > 0.4 and ay > 0.4:
                self.side_up = 'e'
            elif ax < -0.4 and ay < -0.4:
                self.side_up = 'w'
            elif ax < -0.4 and ay > 0.4:
                self.side_up = 'n'
            elif ax > 0.4 and ay < -0.4:
                self.side_up = 's'
        else:
            print("rotating!")




    def update(self):
        self.updateCount += 1
        if self.updateCount > self.updateCountMax:
            if self.controller is not None:
                pad_direction = self.controller.read()
                if pad_direction == "left":
                    self.direction = self.change_direction_map[f"{self.face}{self.direction}l"]
                    # print(f"On face {self.face} going {self.direction}")
                elif pad_direction == "right":
                    self.direction = self.change_direction_map[f"{self.face}{self.direction}r"]
            else:
                self.get_side_up()
                if self.side_up != self.face:
                    self.direction = self.side_up


                # print(f"On face {self.face} going {self.direction}")
                # Uncomment this to make the game stop every cycle without input
                # elif pad_direction == "up":
                #     pass
                # else:
                #     return

            new_face = False
            try:
                position_key = f"{self.face}{self.direction}{self.x_pos}.{self.y_pos}"
                new_x, new_y, face_change = self.transition_map[position_key]
                self.x_pos = new_x
                self.x.append(new_x)
                self.y_pos = new_y
                self.y.append(new_y)
                self.face = face_change[0]
                self.direction = face_change[1]
                # print(f"On face {self.face} going {self.direction}")
                new_face = True
            except KeyError:
                pass
            if not new_face:
                try:
                    direction = self.coord_map[self.face + self.direction]
                    if direction == "yu":
                        self.y_pos += self.step
                        self.y.append(self.y_pos)
                        self.x.append(self.x_pos)
                    elif direction == "yd":
                        self.y_pos -= self.step
                        self.y.append(self.y_pos)
                        self.x.append(self.x_pos)
                    elif direction == "xu":
                        self.x_pos += self.step
                        self.x.append(self.x_pos)
                        self.y.append(self.y_pos)
                    elif direction == "xd":
                        self.x_pos -= self.step
                        self.x.append(self.x_pos)
                        self.y.append(self.y_pos)
                    else:
                        raise TypeError
                except KeyError:
                    x = 1/2
            x = 3
            # print(f"On face {self.face} going {self.direction}")
            # print(f"X: {self.x_pos} Y: {self.y_pos}")

            if self.x_pos == self.food_x and self.y_pos == self.food_y:
                # Food found!!!
                self.cube_map.set_map_point(self.x_pos, self.y_pos)
                self.new_food_pos()
                self.score += 1
                print(f"Found food! Score: {self.score}")
            else:
                # update previous positions
                self.cube_map.unset_map_point(self.x[0], self.y[0])
                self.x.pop(0)
                self.y.pop(0)
                self.cube_map.set_map_point(self.x_pos, self.y_pos)
                # for i in range(self.length):
                #     self.cube_map.set_map_point(self.x[i], self.y[i])

            self.updateCount = 0



class LEDCubeMap:
    def __init__(self,rows, cols, pixel_input_map):
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


def main():
    # ToDo: Setup battery voltage read
    # ToDo: Setup menu system
    # ToDo: Setup temperature tracking

    imu = imu9250.MPU9250()
    if imu.checkDataReady():
        print("IMU Ready")
    else:
        print("IMU Not Ready!")
        sys.exit()

    matrix = RGBMatrix(options=options)
    image = Image.new("RGB", (6 * 64, 64))
    pixels = image.load()
    cube_map = LEDCubeMap(rows=image.size[0], cols=image.size[1], pixel_input_map=pixels)
    snake = Snake(cube_map, use_controller=False, imu=imu)
    image.show()
    last_time = time.process_time()
    while True:
        new_time = time.process_time()
        if new_time - last_time > TIME_STEP_LENGTH:
            last_time = time.process_time()
            snake.update()
            matrix.Clear()
            matrix.SetImage(image)




if __name__ == "__main__":
    main()