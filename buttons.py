import pyautogui as gui
import time
import vision
from vision import x_pad, y_pad
import threading

gui.PAUSE = .05


def button_factory(coords_list):
    return [Button(*coords) for coords in coords_list]


class Button:
    prev_coords = None
    lock = threading.Lock()

    @staticmethod
    def same_coords(coords):
        if Button.prev_coords == coords:
            return True
        else:
            Button.prev_coords = coords
            return False

    def __init__(self, x, y, pause=0):
        self.coords = [x, y]
        self.pause = pause

    def __call__(self, *args, **kwargs):
        self.click(*args, **kwargs)

    def click(self, *args, **kwargs):
        with Button.lock:
            if Button.same_coords(self.coords):
                gui.click(self.coords[0] + x_pad, self.coords[1] + y_pad, *args, **kwargs)
            else:
                gui.click(self.coords[0] + x_pad + 1, self.coords[1] + y_pad, *args, **kwargs)

        if self.pause:
            time.sleep(self.pause)


class ButtonList:
    sound = Button(314, 373)
    menu = button_factory([(300, 200), (300, 400), (300, 400), (585, 449), (337, 376)])

    food = button_factory([(31, 334), (89, 332), (37, 394), (89, 391), (43, 442), (93, 440)])
    plates = button_factory([(86, 207), (180, 211), (280, 205), (384, 211), (484, 207), (582, 211)])
    finish_food = Button(207, 383, pause=1.1)

    phone_open = Button(589, 344)
    phone_topping = Button(528, 274)
    phone_rice = Button(528, 296)
    phone_exit = Button(586, 345)

    order_topping = button_factory([(486, 225), (572, 223), (494, 277), (572, 283), (494, 337)])
    order_rice = Button(541, 286)
    finish_delivery = Button(493, 299)


bl = ButtonList


class Food:
    @staticmethod
    def order(name):
        return Food.make_california() if name == 'california' \
            else Food.make_gunkan() if name == 'gunkan' \
            else Food.make_onigiri() if name == 'onigiri' \
            else None

    @staticmethod
    def make_onigiri():
        bl.food[1]()
        bl.food[1]()
        bl.food[2]()
        bl.finish_food()

    @staticmethod
    def make_california():
        bl.food[1]()
        bl.food[2]()
        bl.food[3]()
        bl.finish_food()

    @staticmethod
    def make_gunkan():
        bl.food[1]()
        bl.food[2]()
        bl.food[3]()
        bl.food[3]()
        bl.finish_food()


def food_available(num):
    bl.phone_open()
    if num == 1:
        bl.phone_rice()
    else:
        bl.phone_topping()
    image = vision.grab_screen()
    bl.phone_exit()

    def rice():
        return image.getpixel((545, 284)) != (127, 127, 127)

    def shrimp():
        return image.getpixel((495, 223)) != (127, 71, 47)

    def unagi():
        return image.getpixel((575, 227)) != (94, 49, 8)

    def nori():
        return image.getpixel((495, 277)) != (33, 30, 11)

    def fish_egg():
        return image.getpixel((575, 277)) != (101, 13, 13)

    def salmon():
        return image.getpixel((493, 331)) != (127, 71, 47)

    return {0: shrimp, 1: rice, 2: nori, 3: fish_egg, 4: salmon, 5: unagi}[num]()


def order_food(num):
    bl.phone_open()
    if num == 1:
        bl.phone_rice()
        bl.order_rice()
    else:
        bl.phone_topping()
        if num == 0:
            bl.order_topping[0]()
        elif num == 2:
            bl.order_topping[2]()
        elif num == 3:
            bl.order_topping[3]()
        elif num == 4:
            bl.order_topping[4]()
        elif num == 5:
            bl.order_topping[1]()
    bl.finish_delivery()


def click_plates():
    for button in ButtonList.plates:
        button.click()


def position():
    pos = gui.position()
    return pos[0] - x_pad, pos[1] - y_pad
