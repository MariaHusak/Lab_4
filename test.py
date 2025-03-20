import unittest
from unittest.mock import patch, MagicMock
from main import *


class TestOrderDatabase(unittest.TestCase):
    @patch('main.MongoClient')
    def test_add_order(self, MockMongoClient):
        mock_db = MockMongoClient.return_value["restaurant"]
        mock_orders_collection = mock_db["orders"]
        order_db = OrderDatabase()
        order_db.add_order("Pizza")
        mock_orders_collection.insert_one.assert_called_once_with({"order": "Pizza"})

    @patch('main.MongoClient')
    def test_get_orders(self, MockMongoClient):
        OrderDatabase._instance = None
        mock_db = MockMongoClient.return_value["restaurant"]
        mock_orders_collection = mock_db["orders"]
        mock_orders_collection.find.return_value = [{"order": "Pizza"}, {"order": "Pasta"}]
        order_db = OrderDatabase()
        orders = order_db.get_orders()
        self.assertEqual(orders, ["Pizza", "Pasta"])


class TestKitchenNotifier(unittest.TestCase):
    def test_notify(self):
        chef = MagicMock()
        notifier = KitchenNotifier()
        notifier.subscribe(chef)
        notifier.notify("Pizza")
        chef.update.assert_called_once_with("Pizza")


class TestOrderFactory(unittest.TestCase):
    def test_create_regular_order(self):
        order = OrderFactory.create_order("regular", "John Doe", ["Pizza", "Pasta"])
        self.assertIsInstance(order, RegularOrder)
        self.assertEqual(order.process(), "Regular order for John Doe: Pizza, Pasta")

    def test_create_bulk_order(self):
        order = OrderFactory.create_order("bulk", "John Doe", ["Pizza", "Pasta"], 10)
        self.assertIsInstance(order, BulkOrder)
        self.assertEqual(order.process(), "Bulk order for John Doe: Pizza, Pasta x10")

    def test_create_order_invalid_type(self):
        with self.assertRaises(ValueError):
            OrderFactory.create_order("invalid", "John Doe", ["Pizza", "Pasta"])


class TestSingletonPattern(unittest.TestCase):
    def test_ensures_single_instance(self):
        instance1 = OrderDatabase()
        instance2 = OrderDatabase()
        self.assertIs(instance1, instance2)


class TestObserverPattern(unittest.TestCase):
    def test_notifies_all_subscribers(self):
        chef1 = MagicMock()
        chef2 = MagicMock()
        notifier = KitchenNotifier()
        notifier.subscribe(chef1)
        notifier.subscribe(chef2)
        notifier.notify("Burger")
        chef1.update.assert_called_once_with("Burger")
        chef2.update.assert_called_once_with("Burger")


class TestChef(unittest.TestCase):
    def test_update_receives_order(self):
        chef = Chef()
        with patch('builtins.print') as mocked_print:
            chef.update("Pizza")
            mocked_print.assert_called_once_with("Chef received new order: Pizza")

    def test_update_receives_multiple_orders(self):
        chef = Chef()
        with patch('builtins.print') as mocked_print:
            chef.update("Pizza")
            chef.update("Pasta")
            self.assertEqual(mocked_print.call_count, 2)
            mocked_print.assert_any_call("Chef received new order: Pizza")
            mocked_print.assert_any_call("Chef received new order: Pasta")

if __name__ == '__main__':
    unittest.main()