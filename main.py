from time import sleep

from pyautogui import FailSafeException

from buttons import *
import vision
from pygame.time import Clock

orders = [None] * 6
running = True


def dish_clicker():
    global running
    try:
        while running:
            click_plates()
            sleep(2)
    except FailSafeException:
        running = False
        raise


def main():
    thread = threading.Thread(target=dish_clicker)
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
            Food.order(current_orders[i])
    orders = current_orders


if __name__ == '__main__':
    main()
