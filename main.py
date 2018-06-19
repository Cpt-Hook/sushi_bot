from pygame.time import Clock

import gameinfo as gi
import vision
import threading
import time
import math
from pyautogui import FailSafeException

lock = gi.threading.Lock()
running = True
check_ingredients_event = threading.Event()


class FoodThread(threading.Thread):

    def __init__(self, food, name, *args, **kwargs):
        super().__init__(name=name, *args, **kwargs)
        self.food = food

    def run(self):
        try:
            with lock:
                while not stock.food_available(self.food):
                    lock.release()
                    stock.new_stock_event.wait()
                    lock.acquire()
                print(f"Making order: {self.getName()}")
                gi.Food.order(self.food)
                stock.subtract_food(self.food)
                check_ingredients_event.set()
                check_ingredients_event.clear()
        except FailSafeException:
            global running
            running = False
            raise


class OrderingThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = True

    def run(self):
        try:
            print("Ordering thread started")
            while self.running:
                with lock:
                    for ingredient in range(6):
                        if stock.stock[ingredient] < 3 and not stock.shipping[ingredient]:
                            if stock.ingredient_available(ingredient):
                                gi.order_ingredient(ingredient)
                                stock.shipped(ingredient)
                                print(f"Ordering {ingredient}, balance is now {stock.money}$")
                check_ingredients_event.wait()
            print("Ordering thread exited")
        except FailSafeException:
            global running
            running = False
            raise


class Stock:

    def __init__(self):
        self.new_stock_event = threading.Event()
        self.stock = [5, 10, 10, 10, 5, 5]
        self.money = 0
        self.shipping = [False] * 6

    def shipped(self, ingredient):
        def arrived():
            with lock:
                self.shipping[ingredient] = False
                self.stock[ingredient] += gi.Food.ingredient_order_amount[ingredient]
                self.new_stock_event.set()
                self.new_stock_event.clear()
                print(f"Ingredient {ingredient} arrived")

        self.shipping[ingredient] = True
        self.money -= gi.Food.ingredient_prices[ingredient]
        timer = gi.threading.Timer(6.1, arrived)
        timer.setDaemon(True)
        timer.start()

    def food_available(self, food):
        for ingredient, amount in getattr(gi.Food, food).items():
            if not (self.stock[ingredient] >= amount):
                return False
        return True

    def ingredient_available(self, ingredient):
        return self.money >= gi.Food.ingredient_prices[ingredient]

    def add_money(self, food):
        with lock:
            self.money += gi.Food.food_prices[food]
            print(f"Added {gi.Food.food_prices[food]}$ for {food}, balance is now {self.money}$")
            check_ingredients_event.set()
            check_ingredients_event.clear()

    def subtract_food(self, food):
        for ingredient, amount in getattr(gi.Food, food).items():
            self.stock[ingredient] -= amount

        for food_stock in self.stock:
            assert food_stock >= 0


stock: Stock


def plate_timer(plate_num, food):
    stock.add_money(food)
    gi.click_plate(plate_num)


def solve_level(last_level=False):
    def loop():
        nonlocal orders, order_num

        current_orders = vision.get_requests()
        for i in range(6):
            if orders[i] != current_orders[i]:
                if current_orders[i] is not None:
                    print(f'Customer at seat {i}, order id: {current_orders[i]}_{order_num}')
                    FoodThread(current_orders[i], name=f'{current_orders[i]}_{order_num}').start()
                    order_num += 1
                else:
                    timer = threading.Timer(5.1, plate_timer, [i, orders[i]])
                    timer.setDaemon(True)
                    timer.start()

        orders = current_orders

    global stock
    order_num = 0
    orders = [None] * 6

    stock = Stock()
    ordering_thread = OrderingThread()
    ordering_thread.setDaemon(True)

    ordering_thread.start()

    last_check = time.time()
    while running:
        clock = Clock()
        loop()
        clock.tick(30)

        if (time.time() - last_check) > 5:
            if gi.vision.level_ended():
                ordering_thread.running = False
                check_ingredients_event.set()
                check_ingredients_event.clear()
                ordering_thread.join()
                if not last_level:
                    for button in gi.bl.next_level:
                        button()
                return
            last_check = time.time()


def start(find_window=True, turn_off_sound=True, stop_at_level=math.inf):
    level = 1
    print("Starting Sushi go round bot")
    if find_window:
        print("Finding windows position.")
        if vision.set_window_coords():
            print(f"Game positions found: ([{vision.x_pad},{vision.y_pad}],"
                  f"[{vision.x_pad+vision.width},{vision.y_pad+vision.height}])")
        else:
            print(f"Game position not found. Using default: ([{vision.x_pad},{vision.y_pad}],"
                  f"[{vision.x_pad+vision.width},{vision.y_pad+vision.height}])")
    try:
        gi.start_game(turn_off_sound)
        while running and level <= stop_at_level:
            start_time = time.time()
            print(f"Level: {level} started")
            solve_level(level == stop_at_level)
            level += 1
            print(f"Level ended in {time.time() - start_time} seconds")
            print("\n"*2)
    except KeyboardInterrupt:
        pass
    print("Exiting bot")


if __name__ == '__main__':
    start()
