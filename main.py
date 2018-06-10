from pygame.time import Clock

from buttons import *

lock = threading.Lock()


class FoodThread(threading.Thread):

    def __init__(self, food, name, *args, **kwargs):
        super().__init__(name=name, *args, **kwargs)
        self.food = food

    def run(self):
        with lock:
            if stock.available(self.food):
                print(f"Making order: {self.getName()}")
                Food.order(self.food)
                stock.subtract(self.food)
            else:
                while not stock.available(self.food):
                    lock.release()
                    stock.new_stock_event.wait()
                    lock.acquire()
                print(f"Making order: {self.getName()}")
                Food.order(self.food)
                stock.subtract(self.food)


class OrderingThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = True

    def run(self):
        print("Ordering thread started")
        while self.running:
            with lock:
                for ingredient in range(6):
                    if stock.stock[ingredient] < 3 and not stock.shipping[ingredient]:
                        if ingredient_available(ingredient):
                            print(f"Ordering {ingredient}")
                            order_ingredient(ingredient)
                            stock.shipped(ingredient)
            time.sleep(1)
        print("Ordering thread exited")


class Stock:
    order_amount = (5, 10, 10, 10, 5, 5)

    def __init__(self):
        self.new_stock_event = threading.Event()
        self.stock = [5, 10, 10, 10, 5, 5]
        self.shipping = [False] * 6

    def shipped(self, ingredient):
        def arrived():
            with lock:
                print(f"Ingredient {ingredient} arrived")
                self.shipping[ingredient] = False
                self.stock[ingredient] += Stock.order_amount[ingredient]
                self.new_stock_event.set()
                self.new_stock_event.clear()

        self.shipping[ingredient] = True
        timer = threading.Timer(6.25, arrived)
        timer.setDaemon(True)
        timer.start()

    def available(self, food):
        for ingredient, amount in getattr(Food, food).items():
            if not (self.stock[ingredient] >= amount):
                return False
        return True

    def subtract(self, food):
        for ingredient, amount in getattr(Food, food).items():
            self.stock[ingredient] -= amount

        for food_stock in self.stock:
            assert food_stock >= 0


stock: Stock


def init(turn_off_sound=True):
    level = 1
    print("Starting Sushi go round bot")
    try:
        start_game(turn_off_sound)
        while True:
            print(f"Level: {level} started")
            level += 1
            solve_level()
    except KeyboardInterrupt:
        print("Exiting bot")


def solve_level():
    global stock
    stock = Stock()
    ordering_thread = OrderingThread()
    ordering_thread.setDaemon(True)

    ordering_thread.start()

    start_time = time.time()
    last_check = time.time()
    while True:
        clock = Clock()
        loop()
        clock.tick(20)

        if (time.time() - last_check) > 5:
            if vision.level_ended():
                print(f"Level ended in {time.time() - start_time} seconds")
                ordering_thread.running = False
                ordering_thread.join()
                for button in bl.next_level:
                    button()
                return
            last_check = time.time()


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
                timer = threading.Timer(5.25, click_plate, [i])
                timer.setDaemon(True)
                timer.start()

    orders = current_orders


if __name__ == '__main__':
    init(turn_off_sound=True)
