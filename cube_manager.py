import time
import os
import sys
import threading
import psutil
import subprocess


from grove import adc

from control_pad import Controller
from led_matrix import *

EXIT = False
UNDER_VOLTAGE = False
VOLTAGE_THRESHOLD = 1250
OVER_TEMP = False

GAMEPROCNAME = "cube_games"
GAME_CMDS = ["python3", "/home/pi/devel/ledcube/cube_games.py"]
DEMO_STR = "/home/pi/rpi-rgb-led-matrix/examples-api-use/demo --led-rows=64 --led-cols=64 --led-slowdown-gpio=4 --led-chain=6 --led-gpio-mapping=adafruit-hat-pwm -D "
DEMOPROCNAME = "demo"


# My voltages
# 1.3 == 11
# 1.25 == 10.5  # using a 3s so lowest I want to go is 1.26
# 1.08 == 9
# 0.96 == 8.0


# elif choice == "temp":
# image = Image.new("RGB", (6 * 64, 64))
# draw = ImageDraw.Draw(image)
# for idx in range(8, 383, 64):
#     draw.multiline_text((idx, 25), f"Over Temp! Exiting!", fill=(255, 0, 0))
#     for _ in range(5):
#         matrix.SetImage(image, 0, 0)
#         time.sleep(0.6)
#         matrix.Clear()
#         time.sleep(0.2)


class CubeController:
    def __init__(self):
        self.remote_controller = Controller()
        monitor = threading.Thread(target=self.monitor, args=())
        monitor.start()

    def monitor(self):
        while not EXIT:
            data = self.remote_controller.read()
            if data:
                print(data)
            time.sleep(0.5)
            if data == "start":
                self.start_games()
            elif data == "select":
                self.stop_games()
                self.stop_demo()
            elif data == "square":
                self.stop_demo()
                self.start_demo("7")
            elif data == "circle":
                self.stop_demo()
                self.start_demo("10")
            elif data == "triangle":
                self.stop_demo()
                self.start_demo("11")

    @staticmethod
    def games_running():
        global GAMEPROCNAME
        for proc in psutil.process_iter():
            if "python" in proc.name():
                for component in proc.cmdline():
                    if GAMEPROCNAME in component:
                        return True

    @staticmethod
    def demo_running():
        global DEMOPROCNAME
        for proc in psutil.process_iter():
                for component in proc.cmdline():
                    if DEMOPROCNAME in component:
                        return True

    def start_games(self):
        if not self.games_running():
            global GAME_CMDS
            subprocess.Popen(GAME_CMDS)
        time.sleep(1)
        if not self.games_running():
            raise OSError

    @staticmethod
    def start_demo(demo_numb):
        global DEMO_STR
        subprocess.Popen(DEMO_STR + demo_numb, shell=True)

    @staticmethod
    def stop_process(name):
        for proc in psutil.process_iter():
            for component in proc.cmdline():
                if name in component:
                    proc.kill()
                    return

    def stop_games(self):
        global GAMEPROCNAME
        self.stop_process(GAMEPROCNAME)

    def stop_demo(self):
        global DEMOPROCNAME
        self.stop_process(DEMOPROCNAME)
        self.stop_process(DEMOPROCNAME)


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


def shutdown(message):
    image = Image.new("RGB", (6 * 64, 64))
    draw = ImageDraw.Draw(image)
    matrix = RGBMatrix(options=options)
    for idx in range(8, 383, 64):
        draw.multiline_text((idx, 25), message, fill=(255, 0, 0))
    for _ in range(10):
        matrix.Clear()
        time.sleep(0.3)
        matrix.SetImage(image, 0, 0)
        time.sleep(0.8)
    sys.exit()


def main():
    cube_controller = CubeController()
    # Wait 2 minutes before we make our first check
    print("Waiting a couple of minutes before we start checking")
    time.sleep(120)
    # Monitor Voltage
    check_volt_thread = threading.Thread(target=check_voltage, args=())
    check_volt_thread.start()
    # Monitor Temperature
    # check_temp_thread = threading.Thread(target=check_temperature, args=())
    # check_temp_thread.start()
    while True:

        if UNDER_VOLTAGE:
            cube_controller.stop_games()
            shutdown("Low Volt!")
        # if OVER_TEMP:
        #     print("Over Temp!")


if __name__ == "__main__":
    main()
