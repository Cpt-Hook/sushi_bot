from time import sleep

from pyautogui import FailSafeException

from buttons import *
import vision
from pygame.time import Clock

orders = [None] * 6
running = True


class OrderingThread(threading.Thread):

    def __init__(self, ingredient, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ingredient = ingredient

    def run(self):
        if Stock.shipping[self.ingredient]:
            print(f"Ingredient {self.ingredient} already ordered")
            return

        if food_available(self.ingredient):
            print(f"Ingredient {self.ingredient} available - ordering")
            order_food(self.ingredient)
            Stock.shipped(self.ingredient)
        else:
            print(f"Ingredient {self.ingredient} not available - waiting")
            sleep(6.5)
            self.run()


class PlateClickerThread(threading.Thread):
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


class Stock:
    stock = [5, 10, 10, 10, 5, 5]
    order_amount = (5, 10, 10, 10, 5, 5)
    shipping = [False] * 6
    lock = threading.Lock()
    # ingredient_number: amount_needed
    gunkan = {1: 1, 2: 1, 3: 2}
    california = {1: 1, 2: 1, 3: 1}
    onigiri = {1: 2, 2: 1}

    @classmethod
    def shipped(cls, ingredient):
        with cls.lock:
            cls.shipping[ingredient] = True
        sleep(6.5)
        with cls.lock:
            cls.shipping[ingredient] = False
            cls.stock[ingredient] += cls.order_amount[ingredient]

    @classmethod
    def available(cls, food):
        with cls.lock:
            for ingredient, number in getattr(cls, food).items():
                if not (cls.stock[ingredient] >= number):
                    return False
            return True

    @classmethod
    def subtract(cls, food):
        with cls.lock:
            for ingredient, number in getattr(cls, food).items():
                cls.stock[ingredient] -= number

            for food_stock in cls.stock:
                assert food_stock >= 0

    @classmethod
    def missing_ingredients(cls, food):
        missing = []
        recipe = getattr(cls, food)
        with cls.lock:
            for ingredient, number in recipe.items():
                if cls.stock[ingredient] < number:
                    missing.append(ingredient)
        return missing


def new_order(food):
    if Stock.available(food):
        Food.order(food)
        Stock.subtract(food)
    else:
        missing = Stock.missing_ingredients(food)
        print(f"No food left for {food} - missing {missing}")
        for ingredient in missing:
            OrderingThread(ingredient).start()


def main():
    plate_clicker = PlateClickerThread()
    plate_clicker.setDaemon(True)

    start_game(turn_off_sound=True)
    plate_clicker.start()

    while running:
        clock = Clock()
        loop()
        clock.tick(10)


def loop():
    global orders

    current_orders = vision.get_requests()
    for i in range(6):
        if orders[i] != current_orders[i]:
            if current_orders[i] is not None:
                print(f'Customer at seat {i} - {current_orders[i]}')
                new_order(current_orders[i])

    orders = current_orders


if __name__ == '__main__':
    main()
