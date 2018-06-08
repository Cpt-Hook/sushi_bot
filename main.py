from time import sleep

from pyautogui import FailSafeException

from buttons import *
import vision
from pygame.time import Clock

orders = [None] * 6
running = True


class Stock:
    stock = [5, 10, 10, 10, 5, 5]

    @classmethod
    def available(cls, food):
        if food == 'gunkan':
            return cls.stock[1] >= 1 and cls.stock[2] >= 1 and cls.stock[3] >= 2
        elif food == 'california':
            return cls.stock[1] >= 1 and cls.stock[2] >= 1 and cls.stock[3] >= 1
        elif food == 'onigiri':
            return cls.stock[1] >= 2 and cls.stock[2] >= 1
        else:
            raise ValueError

    @classmethod
    def subtract(cls, food):
        if food == 'gunkan':
            cls.stock[1] -= 1
            cls.stock[2] -= 1
            cls.stock[3] -= 2
        elif food == 'california':
            cls.stock[1] -= 1
            cls.stock[2] -= 1
            cls.stock[3] -= 1
        elif food == 'onigiri':
            cls.stock[1] -= 2
            cls.stock[2] -= 1
        else:
            raise ValueError

        for food_stock in cls.stock:
            assert food_stock >= 0


class MyThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self):
        global running
        try:
            while running:
                click_plates()
                sleep(2)
        except FailSafeException:
            running = False
            raise


def main():
    thread = MyThread()
    thread.setDaemon(True)
    thread.start()

    while running:
        clock = Clock()
        loop()
        clock.tick(10)


def loop():
    global orders
    current_orders = vision.get_requests()
    for i in range(6):
        if orders[i] != current_orders[i]:
            print(f'Customer at seat {i} - {current_orders[i] if current_orders[i] else "left"}')
            if Stock.available(current_orders[i]):
                Food.order(current_orders[i])
            else:
                pass # //TODO
    orders = current_orders


if __name__ == '__main__':
    main()
