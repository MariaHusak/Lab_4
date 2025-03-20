from abc import ABC, abstractmethod
from pymongo import MongoClient


class OrderDatabase:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OrderDatabase, cls).__new__(cls)
            cls._instance.client = MongoClient("mongodb://localhost:27017/")
            cls._instance.db = cls._instance.client["restaurant"]
            cls._instance.orders_collection = cls._instance.db["orders"]
        return cls._instance

    def add_order(self, order):
        self.orders_collection.insert_one({"order": order})

    def get_orders(self):
        return [order["order"] for order in self.orders_collection.find()]


class KitchenNotifier:
    def __init__(self):
        self.subscribers = []

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)

    def notify(self, order):
        for subscriber in self.subscribers:
            subscriber.update(order)


class Chef:
    def update(self, order):
        print(f"Chef received new order: {order}")


class Order(ABC):
    @abstractmethod
    def process(self):
        pass


class RegularOrder(Order):
    def __init__(self, client, dishes):
        self.client = client
        self.dishes = dishes

    def process(self):
        return f"Regular order for {self.client}: {', '.join(self.dishes)}"


class BulkOrder(Order):
    def __init__(self, client, dishes, quantity):
        self.client = client
        self.dishes = dishes
        self.quantity = quantity

    def process(self):
        return f"Bulk order for {self.client}: {', '.join(self.dishes)} x{self.quantity}"


class OrderFactory:
    @staticmethod
    def create_order(order_type, client, dishes, quantity=None):
        if order_type == "regular":
            return RegularOrder(client, dishes)
        elif order_type == "bulk":
            return BulkOrder(client, dishes, quantity)
        else:
            raise ValueError("Unknown order type")
