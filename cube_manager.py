import time
import os
import sys
import threading
import psutil
import subprocess


from grove import adc

from pyPS4Controller.controller import Controller
from pyPS4Controller.event_mapping.DefaultMapping import DefaultMapping
from led_matrix import *

EXIT = False
UNDER_VOLTAGE = False
VOLTAGE_THRESHOLD = 1250
OVER_TEMP = False

GAMEPROCNAME = "cube_games"
GAME_CMDS = ["python3", "/home/pi/devel/ledcube/cube_games.py"]
DISPLAYPROCNAME = "displays.py"
DISPLAY_CMDS = ["python3", "/home/pi/devel/ledcube/displays.py"]
DEMO_STR = "/home/pi/rpi-rgb-led-matrix/examples-api-use/demo --led-rows=64 --led-cols=64 --led-slowdown-gpio=4 --led-chain=6 --led-gpio-mapping=adafruit-hat-pwm -D "
DEMOPROCNAME = "demo"
POWEROFF = False


# My voltages
# 1.3 == 11
# 1.25 == 10.5  # using a 3s so lowest I want to go is 1.26
# 1.08 == 9
# 0.96 == 8.0


class CubeController(Controller):
    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)

        self.R1_pressed = False
        self.L1_pressed = False

        self.game_running = False
        self.display_running = False
        self.demo_running = False
        self.proc = None

    def stop_all(self):
        self.stop_games()
        self.stop_demo()
        self.stop_display()

    def on_options_press(self):
        self.start_games()

    def on_share_press(self):
        self.stop_all()

    def on_square_press(self):
        self.stop_all()
        self.start_demo("7")

    def on_circle_press(self):
        self.stop_all()
        self.start_demo("10")

    def on_triangle_press(self):
        self.stop_all()
        self.start_demo("11")

    def on_x_press(self):
        self.stop_all()
        self.start_display("gol")

    def on_left_arrow_press(self):
        self.stop_all()
        self.start_display("rgol")

    def on_L1_press(self):
        global POWEROFF
        if self.R1_pressed:
            print("Setting poweroff")
            POWEROFF = True
        else:
            self.L1_pressed = True

    def on_L1_release(self):
        self.L1_pressed = False

    def on_R1_press(self):
        global POWEROFF
        if self.L1_pressed:
            print("Setting poweroff")
            POWEROFF = True
        else:
            self.R1_pressed = True

    def on_R1_release(self):
        self.R1_pressed = False

    # ToDo: Consolidate this code
    @staticmethod
    def is_games_running():
        global GAMEPROCNAME
        for proc in psutil.process_iter():
            if "python" in proc.name():
                for component in proc.cmdline():
                    if GAMEPROCNAME in component:
                        return True

    @staticmethod
    def is_display_running():
        global DISPLAYPROCNAME
        for proc in psutil.process_iter():
            if "python" in proc.name():
                for component in proc.cmdline():
                    if DISPLAYPROCNAME in component:
                        return True

    @staticmethod
    def is_demo_running():
        global DEMOPROCNAME
        for proc in psutil.process_iter():
                for component in proc.cmdline():
                    if DEMOPROCNAME in component:
                        return True

    def start_games(self):
        global GAME_CMDS
        if self.game_running:
            self.stop_games()
        self.game_running = True
        subprocess.Popen(GAME_CMDS)
        time.sleep(1)
        if not self.is_games_running():
            raise OSError

    def start_display(self, display_type):
        global DISPLAY_CMDS
        if self.display_running:
            self.stop_display()
        display_cmds = []
        display_cmds.extend(DISPLAY_CMDS)
        display_cmds.append(display_type)
        self.proc = subprocess.Popen(display_cmds)
        time.sleep(1)
        if not self.is_display_running():
            raise OSError

    def start_demo(self, demo_numb):
        global DEMO_STR
        self.demo_running = True
        subprocess.Popen(DEMO_STR + demo_numb, shell=True)

    @staticmethod
    def stop_process(name):
        os.system(f"sudo killall -9 {name}")

    def stop_games(self):
        global GAMEPROCNAME
        print("Stopping games")
        self.stop_process(GAMEPROCNAME)
        self.game_running = True

    def stop_display(self):
        global DISPLAYPROCNAME
        if self.proc:
            print("Stopping display")
            os.system(f"sudo kill -9 {self.proc.pid}")
            self.proc = None
            self.display_running = False

    def stop_demo(self):
        global DEMOPROCNAME
        self.stop_process(DEMOPROCNAME)
        self.demo_running = False


class MyEventDefinition(DefaultMapping):

    def __init__(self, button_id, button_type, value, connecting_using_ds4drv, overflow, debug=False):
        """
        For 3Bh2b format, all the data that can distinguish buttons in in the overflow tuple
        :param button_id: Just a placeholder in the signature
        :param button_type: Just a placeholder in the signature
        :param value:  Just a placeholder in the signature
        :param connecting_using_ds4drv: Just a placeholder in the signature
        :param overflow: TUPLE aka (0, 1, 8) aka (value, type_id, button_id)
        :param debug: BOOLEAN
        """
        self.button_id = overflow[2]
        self.button_type = overflow[1]
        self.value = overflow[0]
        self.connecting_using_ds4drv = connecting_using_ds4drv
        self.overflow = overflow
        if debug:
            print("button_id: {} button_type: {} value: {} overflow: {}"
                  .format(self.button_id, self.button_type, self.value, self.overflow))
        DefaultMapping.__init__(self, self.button_id, self.button_type, self.value, connecting_using_ds4drv)

    def triangle_pressed(self):
        return self.button_id == 3 and self.button_type == 1 and self.value == 1

    def triangle_released(self):
        return self.button_id == 3 and self.button_type == 1 and self.value == 0

    def square_pressed(self):
        return self.button_id == 2 and self.button_type == 1 and self.value == 1

    def square_released(self):
        return self.button_id == 2 and self.button_type == 1 and self.value == 0

    def circle_pressed(self):
        return self.button_id == 1 and self.button_type == 1 and self.value == 1

    def circle_released(self):
        return self.button_id == 1 and self.button_type == 1 and self.value == 0

    def x_pressed(self):
        return self.button_id == 0 and self.button_type == 1 and self.value == 1

    def x_released(self):
        return self.button_id == 0 and self.button_type == 1 and self.value == 0

    def options_pressed(self):
        return self.button_id == 7 and self.button_type == 1 and self.value == 1

    def options_released(self):
        return self.button_id == 7 and self.button_type == 1 and self.value == 0

    def share_pressed(self):
        return self.button_id == 6 and self.button_type == 1 and self.value == 1

    def share_released(self):
        return self.button_id == 6 and self.button_type == 1 and self.value == 0

    def L3_pressed(self):
        return self.button_id == 9 and self.button_type == 1 and self.value == 1

    def L3_released(self):
        return self.button_id == 9 and self.button_type == 1 and self.value == 0

    def R3_pressed(self):
        return self.button_id == 10 and self.button_type == 1 and self.value == 1

    def R3_released(self):
        return self.button_id == 10 and self.button_type == 1 and self.value == 0

    def playstation_button_pressed(self):
        return self.button_id == 8 and self.button_type == 1 and self.value == 1

    def playstation_button_released(self):
        return self.button_id == 8 and self.button_type == 1 and self.value == 0


def check_temperature():
    global OVER_TEMP


def check_voltage():
    global UNDER_VOLTAGE, EXIT
    analog = adc.ADC()
    battery_sensor = 6
    while not UNDER_VOLTAGE and not EXIT:
        time.sleep(1)
        voltage = analog.read_voltage(battery_sensor)
        if voltage < 1250:
            UNDER_VOLTAGE = True


def flash_message(message, offset=8):
    image = Image.new("RGB", (6 * 64, 64))
    draw = ImageDraw.Draw(image)
    matrix = RGBMatrix(options=options)
    for idx in range(offset, 383, 64):
        draw.multiline_text((idx, 25), message, fill=(255, 0, 0))
    for _ in range(10):
        matrix.Clear()
        time.sleep(0.3)
        matrix.SetImage(image, 0, 0)
        time.sleep(0.8)


def shutdown_system():
    flash_message("OFF", 25)
    os.system("/home/pi/power_down.sh")


def main():
    global POWEROFF
    cube_controller = CubeController(interface='/dev/input/js0', connecting_using_ds4drv=False,
                                     event_definition=MyEventDefinition)
    # cube_controller.debug = True
    monitor = threading.Thread(target=cube_controller.listen, kwargs={'timeout': 60*10})
    monitor.start()

    # Wait 2 minutes before we make our first check
    print("\nWaiting a couple of minutes before we start checking vitals...")
    # time.sleep(120)
    # Monitor Voltage
    check_volt_thread = threading.Thread(target=check_voltage, args=())
    check_volt_thread.start()
    # Monitor Temperature
    # check_temp_thread = threading.Thread(target=check_temperature, args=())
    # check_temp_thread.start()
    while True:

        if UNDER_VOLTAGE:
            cube_controller.stop_games()
            flash_message("Low Volt!")
            shutdown_system()
        # if OVER_TEMP:
        #     print("Over Temp!")
        if POWEROFF:
            flash_message("OFF", 25)
            shutdown_system()
        time.sleep(0.25)



if __name__ == "__main__":
    main()
