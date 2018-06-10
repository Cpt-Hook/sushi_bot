from time import sleep

from pygame.time import Clock

from buttons import *

running = True
lock = threading.Lock()


class FoodThread(threading.Thread):

    def __init__(self, food, name, *args, **kwargs):
        super().__init__(name=name, *args, **kwargs)
        self.food = food

    def run(self):
        with lock:
            if Stock.available(self.food):
                print(f"Making order: {self.getName()}")
                Food.order(self.food)
                Stock.subtract(self.food)
            else:
                while not Stock.available(self.food):
                    lock.release()
                    Stock.new_stock_event.wait()
                    lock.acquire()
                print(f"Making order: {self.getName()}")
                Food.order(self.food)
                Stock.subtract(self.food)


class OrderingThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self):
        while True:
            with lock:
                for ingredient in range(6):
                    if Stock.stock[ingredient] < 3 and not Stock.shipping[ingredient]:
                        if ingredient_available(ingredient):
                            print(f"Ordering {ingredient}")
                            order_ingredient(ingredient)
                            Stock.shipped(ingredient)
            sleep(2)


class Stock:
    new_stock_event = threading.Event()
    stock = [5, 10, 10, 10, 5, 5]
    order_amount = (5, 10, 10, 10, 5, 5)
    shipping = [False] * 6

    # ingredient_number: amount_needed
    gunkan = {1: 1, 2: 1, 3: 2}
    california = {1: 1, 2: 1, 3: 1}
    onigiri = {1: 2, 2: 1}

    @classmethod
    def shipped(cls, ingredient):
        def arrived():
            with lock:
                print(f"Ingredient {ingredient} arrived")
                cls.shipping[ingredient] = False
                cls.stock[ingredient] += cls.order_amount[ingredient]
                cls.new_stock_event.set()
                cls.new_stock_event.clear()

        cls.shipping[ingredient] = True
        threading.Timer(6.5, arrived).start()

    @classmethod
    def available(cls, food):
        for ingredient, number in getattr(cls, food).items():
            if not (cls.stock[ingredient] >= number):
                return False
        return True

    @classmethod
    def subtract(cls, food):
        for ingredient, number in getattr(cls, food).items():
            cls.stock[ingredient] -= number

        for food_stock in cls.stock:
            assert food_stock >= 0


def main(turn_off_sound=True):
    print("Starting Sushi go round bot")
    ordering_thread = OrderingThread()
    ordering_thread.setDaemon(True)

    print("Entering game")
    start_game(turn_off_sound)
    ordering_thread.start()

    try:
        while running:
            clock = Clock()
            loop()
            clock.tick(20)
    except KeyboardInterrupt:
        print("Exiting bot")


order_num = 0
orders = [None] * 6


def loop():
    global orders, order_num

    current_orders = vision.get_requests()
    for i in range(6):
        if orders[i] != current_orders[i]:
            if current_orders[i] is not None:
                print(f'Customer at seat {i}, order id: {current_orders[i]}_{order_num}')
                FoodThread(current_orders[i], name=f'{current_orders[i]}_{order_num}').start()
                order_num += 1
            else:
                threading.Timer(5.5, click_plate, [i]).start()

    orders = current_orders


if __name__ == '__main__':
    main()
