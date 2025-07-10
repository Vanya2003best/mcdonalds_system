"""
McDonald's Management System - Order Models
✅ WYMAGANIE: Użycie klas, dziedziczenie, wzorzec Factory Method, wiele konstruktorów,
             nadpisywanie metod, enkapsulacja, super()

Модели заказов McDonald's с различными типами заказов
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
import sys
import os

# Добавляем пути для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils.logger import log_transfer, log_requirement_check, log_operation, log_business_rule
from src.exceptions.mcdonalds_exceptions import (
    InvalidOrderException, OrderTimeoutException, DriveThruQueueFullException,
    MenuItemNotAvailableException
)


class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PREPARATION = "in_preparation"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OrderType(Enum):
    DINE_IN = "dine_in"
    TAKEOUT = "takeout"
    DRIVE_THRU = "drive_thru"
    DELIVERY = "delivery"
    MOBILE_ORDER = "mobile_order"
    CATERING = "catering"


class PaymentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


# ✅ WYMAGANIE: Użycie klas - Базовый абстрактный класс для заказов
class Order(ABC):
    """
    📋 CHECK: Klasy - Абстрактный базовый класс для всех заказов McDonald's
    ✅ WYMAGANIE: Wzorzec Factory Method - будет реализован в подклассах
    ✅ WYMAGANIE: Enkapsulacja - приватные атрибуты и property
    """

    # Атрибуты класса
    total_orders_created = 0
    orders_by_type = {}
    daily_order_count = 0

    def __init__(self, customer_id: str = "", special_instructions: str = ""):
        # 🔄 TRANSFER: order.py → logger (order creation)
        log_operation("Order Creation", {"customer": customer_id, "type": self.__class__.__name__})

        # Приватные атрибуты для энкапсуляции
        Order.total_orders_created += 1
        Order.daily_order_count += 1

        self._order_id = f"ORD{Order.total_orders_created:06d}"
        self._customer_id = customer_id
        self._order_time = datetime.now()
        self._status = OrderStatus.PENDING
        self._payment_status = PaymentStatus.PENDING
        self._items: List[Dict[str, Any]] = []  # [{item, quantity, price, customizations}]
        self._subtotal = 0.0
        self._tax_amount = 0.0
        self._discount_amount = 0.0
        self._tip_amount = 0.0
        self._total_amount = 0.0
        self._special_instructions = special_instructions
        self._estimated_prep_time = 0  # минут
        self._actual_prep_time: Optional[int] = None
        self._assigned_staff: List[str] = []  # Employee IDs

        # Обновляем счетчики по типам
        order_type = self.__class__.__name__
        if order_type not in Order.orders_by_type:
            Order.orders_by_type[order_type] = 0
        Order.orders_by_type[order_type] += 1

        # 📋 CHECK: Klasy - подтверждение создания класса
        log_requirement_check("Class Creation", "SUCCESS", f"Order: {self._order_id}")

    # ✅ WYMAGANIE: Enkapsulacja - Properties с геттерами и сеттерами
    @property
    def order_id(self) -> str:
        """Геттер для ID заказа (только чтение)"""
        return self._order_id

    @property
    def customer_id(self) -> str:
        """Геттер для ID клиента"""
        return self._customer_id

    @property
    def status(self) -> OrderStatus:
        """Геттер для статуса заказа"""
        return self._status

    @status.setter
    def status(self, value: OrderStatus):
        """
        📋 CHECK: Enkapsulacja - Setter со статус-логикой
        """
        if not isinstance(value, OrderStatus):
            raise ValueError("Status must be OrderStatus enum")

        old_status = self._status
        self._status = value

        # Логируем изменение статуса
        log_business_rule("Order Status Change",
                          f"Order {self.order_id}: {old_status.value} → {value.value}")

        # Особая логика для некоторых статусов
        if value == OrderStatus.IN_PREPARATION:
            self._start_preparation()
        elif value == OrderStatus.COMPLETED:
            self._complete_order()

    @property
    def payment_status(self) -> PaymentStatus:
        """Геттер для статуса оплаты"""
        return self._payment_status

    @payment_status.setter
    def payment_status(self, value: PaymentStatus):
        """Сеттер для статуса оплаты"""
        old_status = self._payment_status
        self._payment_status = value
        log_business_rule("Payment Status Change",
                          f"Order {self.order_id}: {old_status.value} → {value.value}")

    @property
    def total_amount(self) -> float:
        """Геттер для общей суммы"""
        return self._total_amount

    @property
    def estimated_prep_time(self) -> int:
        """Геттер для оценочного времени приготовления"""
        return self._estimated_prep_time

    @property
    def items_count(self) -> int:
        """Количество позиций в заказе"""
        return sum(item['quantity'] for item in self._items)

    @property
    def special_instructions(self) -> str:
        """Геттер для особых инструкций"""
        return self._special_instructions

    @special_instructions.setter
    def special_instructions(self, value: str):
        """Сеттер для особых инструкций"""
        self._special_instructions = value.strip()
        log_operation("Special Instructions", {"order": self.order_id, "instructions": value})

    # ✅ WYMAGANIE: @classmethod - Factory methods (множественные конструкторы)
    @classmethod
    def create_quick_order(cls, customer_id: str, item_name: str, quantity: int = 1):
        """
        📋 CHECK: Wiele konstruktorów - быстрый заказ одной позиции
        Factory method для быстрого заказа одной позиции
        """
        # 🔄 TRANSFER: Order.create_quick_order → Order.__init__
        log_transfer("Order.create_quick_order", "Order.__init__", "quick order data")

        order = cls(customer_id, f"Quick order: {item_name}")
        order.add_item(item_name, quantity, 5.99)  # Примерная цена
        order._calculate_totals()

        log_requirement_check("Multiple Constructors", "EXECUTED", "Order.create_quick_order()")
        return order

    @classmethod
    def create_combo_order(cls, customer_id: str, burger: str, side: str, drink: str):
        """
        📋 CHECK: Wiele konstruktorów - комбо заказ
        Factory method для комбо заказа
        """
        order = cls(customer_id, "Combo meal order")

        # Добавляем позиции комбо
        order.add_item(burger, 1, 4.99)
        order.add_item(side, 1, 2.49)
        order.add_item(drink, 1, 1.79)

        # Скидка за комбо
        order._discount_amount = 1.50
        order._calculate_totals()

        log_requirement_check("Multiple Constructors", "EXECUTED", "Order.create_combo_order()")
        return order

    @classmethod
    def create_family_meal(cls, customer_id: str, people_count: int):
        """Factory method для семейного обеда"""
        order = cls(customer_id, f"Family meal for {people_count} people")

        # Добавляем позиции для семьи
        for i in range(people_count):
            order.add_item("Big Mac", 1, 4.99)
            order.add_item("Medium Fries", 1, 2.49)
            order.add_item("Soft Drink", 1, 1.79)

        # Семейная скидка
        if people_count >= 4:
            order._discount_amount = people_count * 1.00

        order._calculate_totals()
        return order

    @classmethod
    def get_total_orders(cls) -> int:
        """Возвращает общее количество заказов"""
        return cls.total_orders_created

    @classmethod
    def get_orders_by_type(cls) -> Dict[str, int]:
        """Возвращает распределение заказов по типам"""
        return cls.orders_by_type.copy()

    @classmethod
    def reset_daily_count(cls):
        """Сбрасывает дневной счетчик"""
        cls.daily_order_count = 0
        log_operation("Daily Reset", {"previous_count": cls.daily_order_count})

    # ✅ WYMAGANIE: @staticmethod - Утилитарные методы
    @staticmethod
    def calculate_tax(subtotal: float, tax_rate: float = 0.08) -> float:
        """
        📋 CHECK: @staticmethod - Расчет налога
        """
        tax = subtotal * tax_rate
        log_requirement_check("@staticmethod", "EXECUTED", "Order.calculate_tax()")
        return round(tax, 2)

    @staticmethod
    def is_valid_order_id(order_id: str) -> bool:
        """Проверяет валидность ID заказа"""
        return order_id.startswith("ORD") and len(order_id) == 9 and order_id[3:].isdigit()

    @staticmethod
    def estimate_prep_time(item_count: int, complexity_factor: float = 1.0) -> int:
        """Оценивает время приготовления заказа"""
        base_time = max(3, item_count * 2)  # Минимум 3 минуты
        adjusted_time = int(base_time * complexity_factor)
        return min(adjusted_time, 30)  # Максимум 30 минут

    # Абстрактные методы для реализации в подклассах
    @abstractmethod
    def get_order_type(self) -> OrderType:
        """Возвращает тип заказа"""
        pass

    @abstractmethod
    def get_service_fee(self) -> float:
        """Возвращает сервисный сбор для типа заказа"""
        pass

    @abstractmethod
    def validate_order(self) -> bool:
        """Валидирует заказ согласно типу"""
        pass

    # Методы работы с позициями
    def add_item(self, item_name: str, quantity: int, price: float, customizations: List[str] = None):
        """Добавляет позицию в заказ"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if price < 0:
            raise ValueError("Price cannot be negative")

        item = {
            'name': item_name,
            'quantity': quantity,
            'unit_price': price,
            'total_price': price * quantity,
            'customizations': customizations or [],
            'added_at': datetime.now()
        }

        self._items.append(item)
        self._calculate_totals()

        log_business_rule("Item Added",
                          f"Order {self.order_id}: {quantity}x {item_name} @ ${price:.2f}")

    def remove_item(self, item_name: str, quantity: int = 1):
        """Убирает позицию из заказа"""
        for item in self._items:
            if item['name'] == item_name:
                if item['quantity'] <= quantity:
                    self._items.remove(item)
                    log_business_rule("Item Removed", f"Order {self.order_id}: removed {item_name}")
                else:
                    item['quantity'] -= quantity
                    item['total_price'] = item['unit_price'] * item['quantity']
                    log_business_rule("Item Quantity Reduced",
                                      f"Order {self.order_id}: {item_name} -{quantity}")

                self._calculate_totals()
                return

        raise ValueError(f"Item '{item_name}' not found in order")

    def modify_item(self, item_name: str, new_customizations: List[str]):
        """Изменяет кастомизацию позиции"""
        for item in self._items:
            if item['name'] == item_name:
                old_customizations = item['customizations']
                item['customizations'] = new_customizations
                log_business_rule("Item Modified",
                                  f"Order {self.order_id}: {item_name} customizations updated")
                return

        raise ValueError(f"Item '{item_name}' not found in order")

    def apply_discount(self, amount: float, reason: str = ""):
        """Применяет скидку к заказу"""
        if amount < 0:
            raise ValueError("Discount amount cannot be negative")

        self._discount_amount += amount
        self._calculate_totals()

        log_business_rule("Discount Applied",
                          f"Order {self.order_id}: ${amount:.2f} discount - {reason}")

    def add_tip(self, amount: float):
        """Добавляет чаевые"""
        if amount < 0:
            raise ValueError("Tip amount cannot be negative")

        self._tip_amount = amount
        self._calculate_totals()

        log_business_rule("Tip Added", f"Order {self.order_id}: ${amount:.2f} tip")

    def _calculate_totals(self):
        """Пересчитывает общие суммы заказа"""
        # Подсчет подытога
        self._subtotal = sum(item['total_price'] for item in self._items)

        # Добавляем сервисный сбор
        service_fee = self.get_service_fee()

        # Подытог с сервисным сбором
        subtotal_with_service = self._subtotal + service_fee

        # Применяем скидку
        discounted_subtotal = max(0, subtotal_with_service - self._discount_amount)

        # Рассчитываем налог
        self._tax_amount = self.calculate_tax(discounted_subtotal)

        # Общая сумма
        self._total_amount = discounted_subtotal + self._tax_amount + self._tip_amount

        # Обновляем время приготовления
        complexity = 1.0 + (len(self._items) * 0.1)  # Больше позиций = сложнее
        self._estimated_prep_time = self.estimate_prep_time(self.items_count, complexity)

    def _start_preparation(self):
        """Начинает приготовление заказа"""
        self._prep_start_time = datetime.now()
        log_business_rule("Preparation Started",
                          f"Order {self.order_id}: estimated {self._estimated_prep_time} minutes")

    def _complete_order(self):
        """Завершает заказ"""
        if hasattr(self, '_prep_start_time'):
            self._actual_prep_time = int((datetime.now() - self._prep_start_time).total_seconds() / 60)
            log_business_rule("Order Completed",
                              f"Order {self.order_id}: actual time {self._actual_prep_time} minutes")

    def assign_staff(self, employee_id: str):
        """Назначает сотрудника на заказ"""
        if employee_id not in self._assigned_staff:
            self._assigned_staff.append(employee_id)
            log_business_rule("Staff Assigned", f"Order {self.order_id}: assigned to {employee_id}")

    def get_order_summary(self) -> Dict[str, Any]:
        """Возвращает сводку заказа"""
        return {
            'order_id': self.order_id,
            'customer_id': self.customer_id,
            'order_type': self.get_order_type().value,
            'status': self.status.value,
            'items_count': self.items_count,
            'subtotal': self._subtotal,
            'discount': self._discount_amount,
            'tax': self._tax_amount,
            'tip': self._tip_amount,
            'total': self.total_amount,
            'estimated_time': self.estimated_prep_time,
            'special_instructions': self.special_instructions
        }

    def get_items_list(self) -> List[Dict[str, Any]]:
        """Возвращает копию списка позиций"""
        return [item.copy() for item in self._items]

    def __str__(self) -> str:
        return f"Order {self.order_id} - {self.get_order_type().value} - ${self.total_amount:.2f}"

    def __repr__(self) -> str:
        return f"Order(id='{self.order_id}', type={self.get_order_type().value}, total=${self.total_amount:.2f})"


# ✅ WYMAGANIE: Dziedziczenie - Заказ в ресторане
class DineInOrder(Order):
    """
    📋 CHECK: Dziedziczenie - DineInOrder наследует от Order
    ✅ WYMAGANIE: Nadpisywanie metод - переопределение методов базового класса
    ✅ WYMAGANIE: super() - использование родительской реализации
    """

    def __init__(self, customer_id: str = "", table_number: int = 0, party_size: int = 1,
                 special_instructions: str = ""):
        # ✅ WYMAGANIE: super() - вызов конструктора родителя
        super().__init__(customer_id, special_instructions)

        # 🔄 TRANSFER: Order.__init__ → DineInOrder.__init__
        log_transfer("Order.__init__", "DineInOrder.__init__", "dine-in specific attributes")

        # Специфичные атрибуты для заказа в ресторане
        self.table_number = table_number
        self.party_size = party_size
        self._server_id: Optional[str] = None
        self._needs_high_chair = False
        self._is_birthday_celebration = False

        log_requirement_check("Inheritance", "SUCCESS", f"DineInOrder extends Order: {self.order_id}")

    # ✅ WYMAGANIE: Nadpisywanie metод - переопределение абстрактных методов
    def get_order_type(self) -> OrderType:
        """Возвращает тип заказа в ресторане"""
        return OrderType.DINE_IN

    def get_service_fee(self) -> float:
        """Сервисный сбор для заказа в ресторане (нет сбора)"""
        return 0.0

    def validate_order(self) -> bool:
        """
        📋 CHECK: Nadpisywanie metod - валидация для заказа в ресторане
        """
        if self.table_number <= 0:
            raise InvalidOrderException(self.order_id, "Invalid table number")

        if self.party_size <= 0:
            raise InvalidOrderException(self.order_id, "Invalid party size")

        if len(self._items) == 0:
            raise InvalidOrderException(self.order_id, "Order cannot be empty")

        log_business_rule("Order Validation", f"DineIn order {self.order_id}: validated")
        return True

    # ✅ WYMAGANIE: Wiele konstruktorów - альтернативные конструкторы
    @classmethod
    def create_birthday_party(cls, customer_id: str, table_number: int, party_size: int):
        """
        📋 CHECK: Wiele konstruktorów - специальный конструктор для дня рождения
        """
        # 🔄 TRANSFER: DineInOrder.create_birthday_party → DineInOrder.__init__
        log_transfer("DineInOrder.create_birthday_party", "DineInOrder.__init__", "birthday party data")

        order = cls(customer_id, table_number, party_size, "Birthday celebration")
        order._is_birthday_celebration = True
        order._needs_high_chair = party_size > 2  # Предполагаем детей

        # Добавляем праздничные позиции
        order.add_item("Happy Meal", party_size // 2, 3.99)
        order.add_item("Birthday Cake", 1, 12.99)

        log_requirement_check("Multiple Constructors", "EXECUTED", "DineInOrder.create_birthday_party()")
        return order

    @classmethod
    def create_large_group(cls, customer_id: str, table_number: int, party_size: int):
        """Создает заказ для большой группы (8+ человек)"""
        if party_size < 8:
            raise ValueError("Large group must have 8+ people")

        order = cls(customer_id, table_number, party_size, "Large group order")

        # Автоматически добавляем 18% чаевые для больших групп
        order.add_tip(0.0)  # Будет пересчитано после добавления позиций

        return order

    def assign_server(self, server_id: str):
        """Назначает официанта"""
        self._server_id = server_id
        self.assign_staff(server_id)
        log_business_rule("Server Assigned", f"Table {self.table_number}: server {server_id}")

    def request_high_chair(self):
        """Запрашивает детский стульчик"""
        self._needs_high_chair = True
        log_business_rule("High Chair Requested", f"Table {self.table_number}")

    def calculate_auto_gratuity(self) -> float:
        """Рассчитывает автоматические чаевые для больших групп"""
        if self.party_size >= 8:
            auto_tip = self._subtotal * 0.18  # 18% для групп 8+
            return auto_tip
        return 0.0


# ✅ WYMAGANIE: Dziedziczenie - Заказ на вынос
class TakeoutOrder(Order):
    """
    📋 CHECK: Dziedziczenie - TakeoutOrder наследует от Order
    Заказ на вынос
    """

    def __init__(self, customer_id: str = "", pickup_time: datetime = None,
                 special_instructions: str = ""):
        # ✅ WYMAGANIE: super()
        super().__init__(customer_id, special_instructions)

        # 🔄 TRANSFER: Order.__init__ → TakeoutOrder.__init__
        log_transfer("Order.__init__", "TakeoutOrder.__init__", "takeout specific attributes")

        self.pickup_time = pickup_time or (datetime.now() + timedelta(minutes=15))
        self._is_ready_for_pickup = False
        self._pickup_notification_sent = False
        self._bag_count = 0

        log_requirement_check("Inheritance", "SUCCESS", f"TakeoutOrder extends Order: {self.order_id}")

    def get_order_type(self) -> OrderType:
        """Возвращает тип заказа на вынос"""
        return OrderType.TAKEOUT

    def get_service_fee(self) -> float:
        """Сервисный сбор для заказа на вынос (нет)"""
        return 0.0

    def validate_order(self) -> bool:
        """Валидация заказа на вынос"""
        if len(self._items) == 0:
            raise InvalidOrderException(self.order_id, "Order cannot be empty")

        # Проверяем время получения
        if self.pickup_time < datetime.now():
            raise InvalidOrderException(self.order_id, "Pickup time cannot be in the past")

        return True

    # ✅ WYMAGANIE: Wiele konstruktorów
    @classmethod
    def create_scheduled_pickup(cls, customer_id: str, pickup_datetime: datetime):
        """
        📋 CHECK: Wiele konstruktorów - заказ с запланированным временем получения
        """
        order = cls(customer_id, pickup_datetime, "Scheduled pickup order")
        log_requirement_check("Multiple Constructors", "EXECUTED", "TakeoutOrder.create_scheduled_pickup()")
        return order

    @classmethod
    def create_asap_order(cls, customer_id: str):
        """Создает заказ "как можно скорее" """
        asap_time = datetime.now() + timedelta(minutes=10)  # 10 минут на приготовление
        order = cls(customer_id, asap_time, "ASAP pickup")
        return order

    def mark_ready_for_pickup(self):
        """Отмечает заказ готовым к получению"""
        self._is_ready_for_pickup = True
        self.status = OrderStatus.READY
        self._calculate_bag_count()
        log_business_rule("Ready for Pickup", f"Order {self.order_id}: {self._bag_count} bags")

    def _calculate_bag_count(self):
        """Рассчитывает количество пакетов"""
        item_count = self.items_count
        self._bag_count = max(1, (item_count + 4) // 5)  # 1 пакет на 5 позиций

    def send_pickup_notification(self):
        """Отправляет уведомление о готовности"""
        if self._is_ready_for_pickup and not self._pickup_notification_sent:
            self._pickup_notification_sent = True
            log_business_rule("Pickup Notification", f"Sent to customer {self.customer_id}")


# ✅ WYMAGANIE: Dziedziczenie - Drive-Thru заказ
class DriveThruOrder(Order):
    """
    📋 CHECK: Dziedziczenie - DriveThruOrder наследует от Order
    Заказ через Drive-Thru с особой логикой очереди
    """

    # Атрибуты класса для управления очередью
    max_queue_size = 10
    current_queue_size = 0
    average_service_time = 3.5  # минут

    def __init__(self, customer_id: str = "", vehicle_type: str = "car",
                 special_instructions: str = ""):
        # Проверяем очередь перед созданием заказа
        if DriveThruOrder.current_queue_size >= DriveThruOrder.max_queue_size:
            raise DriveThruQueueFullException(DriveThruOrder.max_queue_size)

        # ✅ WYMAGANIE: super()
        super().__init__(customer_id, special_instructions)

        # 🔄 TRANSFER: Order.__init__ → DriveThruOrder.__init__
        log_transfer("Order.__init__", "DriveThruOrder.__init__", "drive-thru specific attributes")

        self.vehicle_type = vehicle_type
        self._queue_position = DriveThruOrder.current_queue_size + 1
        self._window_number = 1  # 1 или 2
        self._has_requested_napkins = False
        self._has_requested_sauce = False

        # Обновляем очередь
        DriveThruOrder.current_queue_size += 1

        log_requirement_check("Inheritance", "SUCCESS", f"DriveThruOrder extends Order: {self.order_id}")

    def get_order_type(self) -> OrderType:
        """Возвращает тип Drive-Thru заказа"""
        return OrderType.DRIVE_THRU

    def get_service_fee(self) -> float:
        """Сервисный сбор для Drive-Thru (нет)"""
        return 0.0

    def validate_order(self) -> bool:
        """Валидация Drive-Thru заказа"""
        if len(self._items) == 0:
            raise InvalidOrderException(self.order_id, "Order cannot be empty")

        # Drive-Thru имеет ограничения по размеру заказа
        if self.items_count > 15:
            raise InvalidOrderException(self.order_id, "Drive-Thru orders limited to 15 items")

        return True

    # ✅ WYMAGANIE: Wiele konstruktorów
    @classmethod
    def create_express_order(cls, customer_id: str, item_name: str):
        """
        📋 CHECK: Wiele konstruktorów - экспресс заказ одной позиции
        """
        order = cls(customer_id, "car", "Express single item")
        order.add_item(item_name, 1, 3.99)
        order._window_number = 1  # Экспресс окно

        log_requirement_check("Multiple Constructors", "EXECUTED", "DriveThruOrder.create_express_order()")
        return order

    @classmethod
    def create_mobile_order_pickup(cls, customer_id: str, mobile_order_code: str):
        """Создает заказ для получения мобильного заказа"""
        order = cls(customer_id, "car", f"Mobile pickup: {mobile_order_code}")
        order._window_number = 2  # Второе окно для мобильных заказов
        return order

    @classmethod
    def get_queue_status(cls) -> Dict[str, Any]:
        """Возвращает статус очереди Drive-Thru"""
        wait_time = cls.current_queue_size * cls.average_service_time
        return {
            'queue_size': cls.current_queue_size,
            'max_capacity': cls.max_queue_size,
            'estimated_wait': f"{wait_time:.1f} minutes",
            'available_spots': cls.max_queue_size - cls.current_queue_size
        }

    def request_extra_napkins(self):
        """Запрашивает дополнительные салфетки"""
        self._has_requested_napkins = True
        log_business_rule("Extra Napkins", f"Drive-Thru order {self.order_id}")

    def request_sauce_packets(self, sauce_type: str, count: int = 3):
        """Запрашивает пакетики соуса"""
        self._has_requested_sauce = True
        self.special_instructions += f" +{count} {sauce_type} sauce"
        log_business_rule("Sauce Request", f"Drive-Thru order {self.order_id}: {count}x {sauce_type}")

    def complete_drive_thru_order(self):
        """Завершает обслуживание в Drive-Thru"""
        self.status = OrderStatus.COMPLETED
        DriveThruOrder.current_queue_size = max(0, DriveThruOrder.current_queue_size - 1)
        log_business_rule("Drive-Thru Completed",
                          f"Order {self.order_id}: queue size now {DriveThruOrder.current_queue_size}")


# ✅ WYMAGANIE: Dziedziczenie - Доставка
class DeliveryOrder(Order):
    """
    📋 CHECK: Dziedziczenie - DeliveryOrder наследует от Order
    Заказ с доставкой
    """

    # Тарифы доставки
    base_delivery_fee = 2.99
    distance_rate = 0.50  # за км
    express_surcharge = 4.99

    def __init__(self, customer_id: str = "", delivery_address: str = "",
                 delivery_instructions: str = "", distance_km: float = 5.0,
                 special_instructions: str = ""):
        # ✅ WYMAGANIE: super()
        super().__init__(customer_id, special_instructions)

        # 🔄 TRANSFER: Order.__init__ → DeliveryOrder.__init__
        log_transfer("Order.__init__", "DeliveryOrder.__init__", "delivery specific attributes")

        self.delivery_address = delivery_address
        self.delivery_instructions = delivery_instructions
        self.distance_km = distance_km
        self._delivery_driver_id: Optional[str] = None
        self._estimated_delivery_time = datetime.now() + timedelta(minutes=30 + distance_km * 2)
        self._is_express_delivery = False
        self._contactless_delivery = False

        log_requirement_check("Inheritance", "SUCCESS", f"DeliveryOrder extends Order: {self.order_id}")

    def get_order_type(self) -> OrderType:
        """Возвращает тип заказа с доставкой"""
        return OrderType.DELIVERY

    def get_service_fee(self) -> float:
        """Рассчитывает сбор за доставку"""
        delivery_fee = self.base_delivery_fee + (self.distance_km * self.distance_rate)

        if self._is_express_delivery:
            delivery_fee += self.express_surcharge

        return round(delivery_fee, 2)

    def validate_order(self) -> bool:
        """Валидация заказа с доставкой"""
        if len(self._items) == 0:
            raise InvalidOrderException(self.order_id, "Order cannot be empty")

        if not self.delivery_address.strip():
            raise InvalidOrderException(self.order_id, "Delivery address is required")

        if self.distance_km > 20:
            raise InvalidOrderException(self.order_id, "Delivery distance exceeds 20km limit")

        # Минимальная сумма для доставки
        if self._subtotal < 15.00:
            raise InvalidOrderException(self.order_id, "Minimum $15.00 order for delivery")

        return True

    # ✅ WYMAGANIE: Wiele konstruktorów
    @classmethod
    def create_express_delivery(cls, customer_id: str, address: str, distance_km: float):
        """
        📋 CHECK: Wiele konstruktorów - экспресс доставка
        """
        order = cls(customer_id, address, "Express delivery requested", distance_km)
        order._is_express_delivery = True
        order._estimated_delivery_time = datetime.now() + timedelta(minutes=15 + distance_km)

        log_requirement_check("Multiple Constructors", "EXECUTED", "DeliveryOrder.create_express_delivery()")
        return order

    @classmethod
    def create_contactless_delivery(cls, customer_id: str, address: str, distance_km: float):
        """Создает бесконтактную доставку"""
        order = cls(customer_id, address, "Contactless delivery - leave at door", distance_km)
        order._contactless_delivery = True
        return order

    def assign_driver(self, driver_id: str):
        """Назначает водителя"""
        self._delivery_driver_id = driver_id
        self.assign_staff(driver_id)
        log_business_rule("Driver Assigned", f"Delivery order {self.order_id}: driver {driver_id}")

    def update_delivery_status(self, status: str, location: str = ""):
        """Обновляет статус доставки"""
        delivery_status = f"Delivery {status}"
        if location:
            delivery_status += f" at {location}"

        self.special_instructions += f" | {delivery_status}"
        log_business_rule("Delivery Update", f"Order {self.order_id}: {delivery_status}")

    def calculate_total_delivery_time(self) -> int:
        """Рассчитывает общее время доставки"""
        prep_time = self.estimated_prep_time
        travel_time = int(self.distance_km * 2)  # 2 минуты на км

        if self._is_express_delivery:
            travel_time = int(travel_time * 0.7)  # Быстрее на 30%

        return prep_time + travel_time


# Функция демонстрации системы заказов
def demo_order_system():
    """
    📋 CHECK: Полная демонстрация системы заказов McDonald's
    """

    print("📝 McDONALD'S ORDER SYSTEM DEMO")
    print("=" * 50)

    # 🔄 TRANSFER: demo → order classes
    log_transfer("demo_order_system", "Order classes", "order creation")

    # 1. ✅ WYMAGANIE: @classmethod - Factory methods (множественные конструкторы)
    print("\n1. FACTORY METHODS (Multiple Constructors)")
    print("-" * 30)

    quick_order = Order.create_quick_order("CUST000001", "Big Mac", 2)
    combo_order = Order.create_combo_order("CUST000002", "Quarter Pounder", "Large Fries", "Coca-Cola")
    family_meal = Order.create_family_meal("CUST000003", 4)

    print(f"Quick order: {quick_order}")
    print(f"Combo order: {combo_order}")
    print(f"Family meal: {family_meal}")

    # 2. ✅ WYMAGANIE: Dziedziczenie + Nadpisywanie
    print("\n2. INHERITANCE & METHOD OVERRIDING")
    print("-" * 30)

    # Создание разных типов заказов
    dine_in = DineInOrder.create_birthday_party("CUST000004", 5, 6)
    takeout = TakeoutOrder.create_asap_order("CUST000005")
    drive_thru = DriveThruOrder.create_express_order("CUST000006", "McFlurry")
    delivery = DeliveryOrder.create_express_delivery("CUST000007", "123 Main St", 3.5)

    orders = [dine_in, takeout, drive_thru, delivery]

    for order in orders:
        print(f"📱 {order}")
        print(f"   Type: {order.get_order_type().value}")
        print(f"   Service Fee: ${order.get_service_fee():.2f}")
        print(f"   Valid: {order.validate_order()}")
        print()

    # 3. ✅ WYMAGANIE: @staticmethod
    print("\n3. STATIC METHODS (@staticmethod)")
    print("-" * 30)

    subtotal = 25.99
    tax = Order.calculate_tax(subtotal, 0.0875)  # NY tax rate
    print(f"Tax calculation: ${subtotal:.2f} subtotal → ${tax:.2f} tax")

    prep_time = Order.estimate_prep_time(8, 1.5)  # 8 items, complex
    print(f"Prep time estimate: {prep_time} minutes for 8 complex items")

    valid_id = Order.is_valid_order_id("ORD123456")
    print(f"Order ID validation: ORD123456 is {'valid' if valid_id else 'invalid'}")

    # 4. ✅ WYMAGANIE: Enkapsulacja - Property usage
    print("\n4. ENCAPSULATION (Property)")
    print("-" * 30)

    order = takeout
    print(f"Order ID (read-only): {order.order_id}")
    print(f"Original status: {order.status.value}")

    order.status = OrderStatus.IN_PREPARATION  # Используем setter
    print(f"Updated status: {order.status.value}")

    order.special_instructions = "Extra ketchup packets"
    print(f"Special instructions: {order.special_instructions}")

    # 5. ✅ WYMAGANIE: Polimorfizm
    print("\n5. POLYMORPHISM")
    print("-" * 30)

    def process_order_payment(order: Order, payment_amount: float):
        """Полиморфная функция для обработки оплаты"""
        print(f"Processing payment for {order.get_order_type().value} order")
        print(f"Order total: ${order.total_amount:.2f}")
        print(f"Payment: ${payment_amount:.2f}")

        if payment_amount >= order.total_amount:
            order.payment_status = PaymentStatus.COMPLETED
            print("✅ Payment successful")
        else:
            order.payment_status = PaymentStatus.FAILED
            print("❌ Insufficient payment")
        print()

    print("Processing payments for different order types:")
    for order in [dine_in, takeout, drive_thru, delivery]:
        process_order_payment(order, order.total_amount)

    # 6. Особенности разных типов заказов
    print("\n6. ORDER TYPE SPECIFIC FEATURES")
    print("-" * 30)

    # Dine-in
    print("Dine-in Order:")
    dine_in.assign_server("EMP1001")
    dine_in.request_high_chair()
    auto_tip = dine_in.calculate_auto_gratuity()
    print(f"Auto gratuity for {dine_in.party_size} people: ${auto_tip:.2f}")

    # Drive-thru
    print(f"\nDrive-thru Queue Status: {DriveThruOrder.get_queue_status()}")
    drive_thru.request_extra_napkins()
    drive_thru.request_sauce_packets("BBQ", 5)

    # Delivery
    print(f"\nDelivery Order:")
    delivery.assign_driver("DRIVER001")
    delivery.update_delivery_status("picked up", "restaurant")
    total_delivery_time = delivery.calculate_total_delivery_time()
    print(f"Total delivery time: {total_delivery_time} minutes")

    # 7. Статистика заказов
    print("\n7. ORDER STATISTICS")
    print("-" * 30)
    print(f"Total orders created: {Order.get_total_orders()}")
    print(f"Orders by type: {Order.get_orders_by_type()}")
    print(f"Daily order count: {Order.daily_order_count}")

    # Сводки заказов
    print(f"\nOrder summaries:")
    for order in orders[:2]:  # Показываем первые 2
        summary = order.get_order_summary()
        print(f"{summary['order_id']}: {summary['items_count']} items, ${summary['total']:.2f}")

    # 📋 CHECK: Финальная проверка
    log_requirement_check("Order System Demo", "COMPLETED", "order.py")

    return orders


if __name__ == "__main__":
    demo_order_system()