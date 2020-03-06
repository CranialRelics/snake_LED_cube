import os
from evdev import InputDevice, categorize, ecodes

AUTOFORWARD = False



class Controller:
    def __init__(self, devID='/dev/input/event0'):
        if not os.path.exists(devID):
            raise OSError("Cannot find controller!")
        self.devID = devID
        self.gamepad = InputDevice(devID)
        self.counter = 0

        self.left_right_code = 16
        self.left_right_values = [-1, 0, 1]
        self.up_down_code = 17
        self.up_down_values = [-1, 0, 1]
        self.square_code = 307
        self.auto_forward = AUTOFORWARD
        self.up_set = False

    def read(self):
        try:
            events = self.gamepad.read()
            for event in events:
                if event.type == ecodes.EV_KEY and event.value == 1 and event.code == 17:
                    pass
                elif event.code == self.left_right_code and event.value == -1:
                    return "left"
                elif event.code == self.left_right_code and event.value == 1:
                    return "right"
                elif event.code == self.up_down_code and event.value == -1:
                    if self.auto_forward:
                        self.up_set = True
                    return "up"
                elif event.code == self.up_down_code and event.value == 1:
                    return "down"

                if event.code == self.square_code and event.value == 1 and self.auto_forward:
                    self.auto_forward = False
                elif event.code == self.square_code and event.value == 1 and not self.auto_forward:
                    self.auto_forward = True
                if self.auto_forward:
                    if event.code == self.up_down_code and event.value == 0:
                        self.up_set = False

        except Exception as err:
            if self.up_set == True and self.auto_forward:
                return "up"
            else:
                return False


def main():
    controller = Controller()
    import time
    while True:
        data = controller.read()
        if data:
            print(data)
        time.sleep(0.01)