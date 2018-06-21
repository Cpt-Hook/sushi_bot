import threading
import time

import pyautogui as gui

import vision

gui.PAUSE = .05  # some systems cannot handle lower click pause
button_lock = threading.RLock()


def button_factory(coords_list):
    return [Button(*coords) for coords in coords_list]


class Button:
    prev_coords = None

    @staticmethod
    def same_coords(coords):
        if Button.prev_coords == coords:
            return True
        else:
            Button.prev_coords = coords
            return False

    def __init__(self, x, y, pause=0.0):
        self.coords = [x, y]
        self.pause = pause

    def __call__(self, *args, **kwargs):
        self.click(*args, **kwargs)

    def click(self, *args, **kwargs):
        with button_lock:
            if Button.same_coords(self.coords):
                gui.click(self.coords[0] + vision.x_pad, self.coords[1] + vision.y_pad, *args, **kwargs)
            else:
                gui.click(self.coords[0] + vision.x_pad + 1, self.coords[1] + vision.y_pad, *args, **kwargs)

        if self.pause:
            time.sleep(self.pause)


class ButtonList:
    sound = Button(314, 373)
    menu = button_factory(((300, 200), (300, 400), (300, 400), (585, 449), (337, 376)))
    next_level = button_factory(((321, 381), (321, 381)))

    food = button_factory(((31, 334), (89, 332), (37, 394), (89, 391), (43, 442), (93, 440)))
    plates = button_factory(((86, 207), (180, 211), (280, 205), (384, 211), (484, 207), (582, 211)))
    finish_food = Button(207, 383)

    phone_open = Button(589, 344)
    phone_topping = Button(528, 274)
    phone_rice = Button(528, 296)
    phone_exit = Button(586, 345)

    order_topping = button_factory(((486, 225), (572, 223), (494, 277), (572, 283), (494, 337)))
    order_rice = Button(541, 286)
    finish_delivery = Button(493, 299)


bl = ButtonList


class Food:
    # ingredient_number: amount_needed
    gunkan = {1: 1, 2: 1, 3: 2}
    california = {1: 1, 2: 1, 3: 1}
    onigiri = {1: 2, 2: 1}
    salmonroll = {1: 1, 2: 1, 4: 2}
    shrimpsushi = {1: 1, 2: 1, 0: 2}
    unagiroll = {1: 1, 2: 1, 5: 2}

    food_prices = {'gunkan': 120, 'california': 80, 'onigiri': 60, 'salmonroll': 280, 'shrimpsushi': 320,
                   'unagiroll': 320}
    ingredient_prices = {0: 350, 1: 100, 2: 100, 3: 200, 4: 300, 5: 350}
    ingredient_order_amount = (5, 10, 10, 10, 5, 5)

    last_order_time = 0

    @classmethod
    def order(cls, food):
        with button_lock:
            last_order = (time.time() - cls.last_order_time)
            if last_order < 1.5:
                button_lock.release()
                time.sleep(1.5 - last_order)
                button_lock.acquire()

            for ingredient, amount in getattr(cls, food).items():
                for i in range(amount):
                    bl.food[ingredient]()
            bl.finish_food()
            cls.last_order_time = time.time()


def order_ingredient(ingredient):
    with button_lock:
        bl.phone_open()
        if ingredient == 1:
            bl.phone_rice()
            bl.order_rice()
        else:
            bl.phone_topping()
            if ingredient == 0:
                bl.order_topping[0]()
            elif ingredient == 2:
                bl.order_topping[2]()
            elif ingredient == 3:
                bl.order_topping[3]()
            elif ingredient == 4:
                bl.order_topping[4]()
            elif ingredient == 5:
                bl.order_topping[1]()
        bl.finish_delivery()


def start_game(turn_off_sound=False):
    with button_lock:
        if turn_off_sound:
            bl.sound()
        for button in bl.menu:
            button()


def click_plate(plate_num):
    with button_lock:
        bl.plates[plate_num]()


def position():
    pos = gui.position()
    return pos[0] - vision.x_pad, pos[1] - vision.y_pad
