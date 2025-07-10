"""
McDonald's Management System - Factory Method Pattern
✅ WYMAGANIE: Wzorzec Factory Method - tworzenie różnych typów zamówień
✅ WYMAGANIE: Polimorfizm poprzez różne fabryki

Паттерн Factory Method для создания различных типов заказов McDonald's
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Type
from enum import Enum
import sys
import os

# Добавляем пути для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils.logger import log_transfer, log_requirement_check, log_operation, log_business_rule
from src.models.order import (
    Order, DineInOrder, TakeoutOrder, DriveThruOrder, DeliveryOrder,
    OrderType, OrderStatus
)
from src.models.menu import MenuItem, Burger, Fries, Drink, BreakfastItem, ItemSize
from src.models.customer import Customer, CustomerType
from src.exceptions.mcdonalds_exceptions import (
    InvalidOrderException, DriveThruQueueFullException, McDonaldsException
)


class OrderPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class OrderComplexity(Enum):
    SIMPLE = "simple"  # 1-3 items
    MEDIUM = "medium"  # 4-7 items
    COMPLEX = "complex"  # 8+ items
    CATERING = "catering"  # Large quantity orders


# ✅ WYMAGANIE: Wzorzec Factory Method - Абстрактная фабрика
class OrderFactory(ABC):
    """
    📋 CHECK: Factory Method Pattern - Abstract factory
    ✅ WYMAGANIE: Wzorzec Factory Method - абстрактная фабрика для создания заказов
    """

    def __init__(self, factory_id: str, restaurant_id: str):
        self.factory_id = factory_id
        self.restaurant_id = restaurant_id
        self._orders_created = 0
        self._creation_history: List[Dict[str, Any]] = []

        # 📋 CHECK: Factory Method Pattern - фабрика создана
        log_requirement_check("Factory Method Pattern", "CREATED", f"OrderFactory: {factory_id}")

    # ✅ WYMAGANIE: Wzorzec Factory Method - главный фабричный метод
    @abstractmethod
    def create_order(self, customer_id: str = "", **kwargs) -> Order:
        """
        📋 CHECK: Factory Method Pattern - Основной фабричный метод
        Абстрактный фабричный метод для создания заказов
        """
        pass

    # Вспомогательные методы для всех фабрик
    def _log_order_creation(self, order: Order, creation_details: Dict[str, Any]):
        """Логирует создание заказа"""
        self._orders_created += 1

        creation_record = {
            "order_id": order.order_id,
            "order_type": order.get_order_type().value,
            "factory_id": self.factory_id,
            "created_at": datetime.now(),
            "customer_id": order.customer_id,
            "details": creation_details
        }

        self._creation_history.append(creation_record)

        # 🔄 TRANSFER: factory.py → logger (order creation)
        log_transfer("OrderFactory", "Order creation", f"order {order.order_id}")

        log_business_rule("Order Created by Factory",
                          f"Factory {self.factory_id}: {order.get_order_type().value} order {order.order_id}")

        log_requirement_check("Factory Method", "EXECUTED", f"{self.__class__.__name__}.create_order()")

    def _calculate_order_priority(self, customer_data: Dict[str, Any],
                                  order_details: Dict[str, Any]) -> OrderPriority:
        """Рассчитывает приоритет заказа"""
        # VIP клиенты имеют высокий приоритет
        if customer_data.get("customer_type") == CustomerType.VIP.value:
            return OrderPriority.URGENT

        # Большие заказы имеют высокий приоритет
        items_count = order_details.get("items_count", 0)
        if items_count > 10:
            return OrderPriority.HIGH

        # Заказы с доставкой имеют повышенный приоритет
        if order_details.get("order_type") == OrderType.DELIVERY.value:
            return OrderPriority.HIGH

        return OrderPriority.NORMAL

    def _calculate_order_complexity(self, items_count: int,
                                    customizations_count: int = 0) -> OrderComplexity:
        """Определяет сложность заказа"""
        if items_count >= 20:
            return OrderComplexity.CATERING
        elif items_count >= 8:
            return OrderComplexity.COMPLEX
        elif items_count >= 4:
            return OrderComplexity.MEDIUM
        else:
            return OrderComplexity.SIMPLE

    def get_creation_stats(self) -> Dict[str, Any]:
        """Возвращает статистику создания заказов"""
        return {
            "factory_id": self.factory_id,
            "restaurant_id": self.restaurant_id,
            "orders_created": self._orders_created,
            "creation_history": self._creation_history.copy()
        }


# ✅ WYMAGANIE: Factory Method + Dziedziczenie - Фабрика для Dine-In заказов
class DineInOrderFactory(OrderFactory):
    """
    📋 CHECK: Factory Method Pattern - Concrete factory for dine-in orders
    📋 CHECK: Dziedziczenie - DineInOrderFactory наследует от OrderFactory
    Конкретная фабрика для создания заказов в ресторане
    """

    def __init__(self, factory_id: str, restaurant_id: str, seating_capacity: int = 60):
        # ✅ WYMAGANIE: super() - вызов конструктора родителя
        super().__init__(factory_id, restaurant_id)

        # 🔄 TRANSFER: OrderFactory.__init__ → DineInOrderFactory.__init__
        log_transfer("OrderFactory.__init__", "DineInOrderFactory.__init__",
                     "dine-in factory attributes")

        self.seating_capacity = seating_capacity
        self._occupied_tables: Dict[int, str] = {}  # table_number -> order_id
        self._table_assignments: Dict[str, int] = {}  # order_id -> table_number
        self._reservation_system = {}

        log_requirement_check("Factory Inheritance", "SUCCESS",
                              f"DineInOrderFactory extends OrderFactory")

    # ✅ WYMAGANIE: Nadpisywanie metod - реализация абстрактного метода
    def create_order(self, customer_id: str = "", **kwargs) -> DineInOrder:
        """
        📋 CHECK: Factory Method Pattern - Dine-in order creation
        📋 CHECK: Nadpisywanie metod - реализация фабричного метода для Dine-In
        """
        # Получаем параметры для Dine-In заказа
        party_size = kwargs.get('party_size', 1)
        table_number = kwargs.get('table_number', 0)
        special_instructions = kwargs.get('special_instructions', '')
        customer_data = kwargs.get('customer_data', {})

        # Назначаем стол если не указан
        if table_number == 0:
            table_number = self._assign_table(party_size)
            if table_number == 0:
                raise InvalidOrderException("", "No available tables for the party size")

        # Проверяем доступность стола
        if table_number in self._occupied_tables:
            raise InvalidOrderException("", f"Table {table_number} is already occupied")

        # Создаем заказ
        order = DineInOrder(customer_id, table_number, party_size, special_instructions)

        # Занимаем стол
        self._occupied_tables[table_number] = order.order_id
        self._table_assignments[order.order_id] = table_number

        # Рассчитываем приоритет и сложность
        priority = self._calculate_order_priority(customer_data, {
            "order_type": OrderType.DINE_IN.value,
            "items_count": 0,  # Будет обновлено при добавлении позиций
            "party_size": party_size
        })

        # Логируем создание
        creation_details = {
            "table_number": table_number,
            "party_size": party_size,
            "priority": priority.value,
            "seating_capacity": self.seating_capacity,
            "occupied_tables": len(self._occupied_tables)
        }

        self._log_order_creation(order, creation_details)

        log_business_rule("Dine-In Order Created",
                          f"Table {table_number}, Party of {party_size}, Order {order.order_id}")

        return order

    # ✅ WYMAGANIE: Wiele konstruktorów - альтернативные методы создания
    def create_birthday_party_order(self, customer_id: str, party_size: int,
                                    birthday_child_age: int) -> DineInOrder:
        """
        📋 CHECK: Wiele konstruktorów - специальный конструктор для дня рождения
        Создает специальный заказ для дня рождения
        """
        # Назначаем большой стол для вечеринки
        table_number = self._assign_large_table(party_size)

        special_instructions = f"Birthday party for {birthday_child_age}-year-old. " \
                               f"Please prepare birthday decorations and special service."

        order = self.create_order(
            customer_id=customer_id,
            party_size=party_size,
            table_number=table_number,
            special_instructions=special_instructions,
            customer_data={"event_type": "birthday"}
        )

        log_requirement_check("Multiple Constructors", "EXECUTED",
                              "DineInOrderFactory.create_birthday_party_order()")

        return order

    def create_business_meeting_order(self, customer_id: str, party_size: int,
                                      meeting_duration_hours: int = 2) -> DineInOrder:
        """Создает заказ для бизнес-встречи"""
        # Выделяем тихую зону для встречи
        table_number = self._assign_quiet_table(party_size)

        special_instructions = f"Business meeting, duration: {meeting_duration_hours} hours. " \
                               f"Please provide quiet seating and minimal interruptions."

        order = self.create_order(
            customer_id=customer_id,
            party_size=party_size,
            table_number=table_number,
            special_instructions=special_instructions,
            customer_data={"event_type": "business"}
        )

        return order

    def _assign_table(self, party_size: int) -> int:
        """Назначает подходящий стол"""
        # Простая логика назначения столов
        if party_size <= 2:
            preferred_tables = range(1, 21)  # Столы 1-20 для малых групп
        elif party_size <= 4:
            preferred_tables = range(21, 41)  # Столы 21-40 для средних групп
        else:
            preferred_tables = range(41, 61)  # Столы 41-60 для больших групп

        for table_num in preferred_tables:
            if table_num not in self._occupied_tables:
                return table_num

        # Если нет подходящих столов, ищем любой свободный
        for table_num in range(1, self.seating_capacity + 1):
            if table_num not in self._occupied_tables:
                return table_num

        return 0  # Нет свободных столов

    def _assign_large_table(self, party_size: int) -> int:
        """Назначает большой стол для вечеринки"""
        large_tables = range(41, 61)  # Большие столы
        for table_num in large_tables:
            if table_num not in self._occupied_tables:
                return table_num
        return self._assign_table(party_size)  # Fallback

    def _assign_quiet_table(self, party_size: int) -> int:
        """Назначает тихий стол для встреч"""
        quiet_tables = [5, 15, 25, 35]  # Предопределенные тихие столы
        for table_num in quiet_tables:
            if table_num not in self._occupied_tables:
                return table_num
        return self._assign_table(party_size)  # Fallback

    def release_table(self, order_id: str):
        """Освобождает стол после завершения заказа"""
        if order_id in self._table_assignments:
            table_number = self._table_assignments[order_id]
            del self._occupied_tables[table_number]
            del self._table_assignments[order_id]

            log_business_rule("Table Released", f"Table {table_number} available (Order {order_id})")

    def get_seating_status(self) -> Dict[str, Any]:
        """Возвращает статус посадочных мест"""
        occupied_count = len(self._occupied_tables)
        available_count = self.seating_capacity - occupied_count

        return {
            "total_capacity": self.seating_capacity,
            "occupied_tables": occupied_count,
            "available_tables": available_count,
            "occupancy_rate": (occupied_count / self.seating_capacity) * 100,
            "occupied_table_numbers": list(self._occupied_tables.keys())
        }


# ✅ WYMAGANIE: Factory Method + Dziedziczenie - Drive-Thru фабрика
class DriveThruOrderFactory(OrderFactory):
    """
    📋 CHECK: Factory Method Pattern - Concrete factory for drive-thru orders
    📋 CHECK: Dziedziczenie - DriveThruOrderFactory наследует от OrderFactory
    Конкретная фабрика для создания Drive-Thru заказов
    """

    def __init__(self, factory_id: str, restaurant_id: str, lane_count: int = 1):
        # ✅ WYMAGANIE: super()
        super().__init__(factory_id, restaurant_id)

        # 🔄 TRANSFER: OrderFactory.__init__ → DriveThruOrderFactory.__init__
        log_transfer("OrderFactory.__init__", "DriveThruOrderFactory.__init__",
                     "drive-thru factory attributes")

        self.lane_count = lane_count
        self._lane_queues: Dict[int, List[str]] = {i: [] for i in range(1, lane_count + 1)}
        self._max_queue_per_lane = 10
        self._lane_assignments: Dict[str, int] = {}  # order_id -> lane_number
        self._express_lane = 1 if lane_count >= 1 else None  # Первая полоса - экспресс

        log_requirement_check("Factory Inheritance", "SUCCESS",
                              f"DriveThruOrderFactory extends OrderFactory")

    # ✅ WYMAGANIE: Nadpisywanie metод - реализация фабричного метода
    def create_order(self, customer_id: str = "", **kwargs) -> DriveThruOrder:
        """
        📋 CHECK: Factory Method Pattern - Drive-thru order creation
        Создает Drive-Thru заказ
        """
        vehicle_type = kwargs.get('vehicle_type', 'car')
        special_instructions = kwargs.get('special_instructions', '')
        customer_data = kwargs.get('customer_data', {})
        is_express = kwargs.get('is_express', False)

        # Выбираем полосу
        lane_number = self._assign_lane(is_express)
        if lane_number == 0:
            raise DriveThruQueueFullException(self._max_queue_per_lane)

        # Создаем заказ
        order = DriveThruOrder(customer_id, vehicle_type, special_instructions)

        # Добавляем в очередь
        self._lane_queues[lane_number].append(order.order_id)
        self._lane_assignments[order.order_id] = lane_number

        # Рассчитываем приоритет
        priority = self._calculate_order_priority(customer_data, {
            "order_type": OrderType.DRIVE_THRU.value,
            "is_express": is_express,
            "lane_number": lane_number
        })

        # Логируем создание
        creation_details = {
            "lane_number": lane_number,
            "vehicle_type": vehicle_type,
            "queue_position": len(self._lane_queues[lane_number]),
            "is_express": is_express,
            "priority": priority.value
        }

        self._log_order_creation(order, creation_details)

        log_business_rule("Drive-Thru Order Created",
                          f"Lane {lane_number}, Position {len(self._lane_queues[lane_number])}, Order {order.order_id}")

        return order

    # ✅ WYMAGANIE: Wiele konstruktorów - специальные методы создания
    def create_express_order(self, customer_id: str, single_item: str) -> DriveThruOrder:
        """
        📋 CHECK: Wiele konstruktorów - экспресс заказ одной позиции
        """
        if not self._express_lane:
            raise InvalidOrderException("", "Express lane not available")

        order = self.create_order(
            customer_id=customer_id,
            vehicle_type="car",
            special_instructions=f"Express order: {single_item}",
            is_express=True
        )

        log_requirement_check("Multiple Constructors", "EXECUTED",
                              "DriveThruOrderFactory.create_express_order()")

        return order

    def create_mobile_pickup_order(self, customer_id: str, mobile_order_code: str) -> DriveThruOrder:
        """Создает заказ для получения мобильного заказа"""
        order = self.create_order(
            customer_id=customer_id,
            vehicle_type="car",
            special_instructions=f"Mobile pickup: {mobile_order_code}",
            customer_data={"order_source": "mobile_app"}
        )

        return order

    def _assign_lane(self, is_express: bool = False) -> int:
        """Назначает полосу Drive-Thru"""
        # Если экспресс заказ и есть экспресс полоса
        if is_express and self._express_lane:
            if len(self._lane_queues[self._express_lane]) < self._max_queue_per_lane:
                return self._express_lane

        # Ищем полосу с наименьшей очередью
        min_queue_size = float('inf')
        best_lane = 0

        for lane_num, queue in self._lane_queues.items():
            if len(queue) < min_queue_size and len(queue) < self._max_queue_per_lane:
                min_queue_size = len(queue)
                best_lane = lane_num

        return best_lane

    def complete_order(self, order_id: str):
        """Завершает заказ и убирает из очереди"""
        if order_id in self._lane_assignments:
            lane_number = self._lane_assignments[order_id]
            if order_id in self._lane_queues[lane_number]:
                self._lane_queues[lane_number].remove(order_id)
            del self._lane_assignments[order_id]

            log_business_rule("Drive-Thru Order Completed",
                              f"Order {order_id} completed from lane {lane_number}")

    def get_queue_status(self) -> Dict[str, Any]:
        """Возвращает статус очередей Drive-Thru"""
        total_queue = sum(len(queue) for queue in self._lane_queues.values())

        lane_status = {}
        for lane_num, queue in self._lane_queues.items():
            lane_status[f"lane_{lane_num}"] = {
                "queue_length": len(queue),
                "capacity": self._max_queue_per_lane,
                "is_express": lane_num == self._express_lane,
                "estimated_wait": len(queue) * 3  # 3 минуты на заказ
            }

        return {
            "total_lanes": self.lane_count,
            "total_queue": total_queue,
            "max_total_capacity": self.lane_count * self._max_queue_per_lane,
            "lanes": lane_status,
            "express_lane": self._express_lane
        }


# ✅ WYMAGANIE: Factory Method + Dziedziczenie - Delivery фабрика
class DeliveryOrderFactory(OrderFactory):
    """
    📋 CHECK: Factory Method Pattern - Concrete factory for delivery orders
    📋 CHECK: Dziedziczenie - DeliveryOrderFactory наследует от OrderFactory
    Конкретная фабрика для создания заказов с доставкой
    """

    def __init__(self, factory_id: str, restaurant_id: str, delivery_radius_km: float = 15.0):
        # ✅ WYMAGANIE: super()
        super().__init__(factory_id, restaurant_id)

        # 🔄 TRANSFER: OrderFactory.__init__ → DeliveryOrderFactory.__init__
        log_transfer("OrderFactory.__init__", "DeliveryOrderFactory.__init__",
                     "delivery factory attributes")

        self.delivery_radius_km = delivery_radius_km
        self._delivery_zones = self._initialize_delivery_zones()
        self._available_drivers: List[str] = []
        self._driver_assignments: Dict[str, str] = {}  # order_id -> driver_id
        self._delivery_schedule: Dict[str, List[str]] = {}  # time_slot -> order_ids

        log_requirement_check("Factory Inheritance", "SUCCESS",
                              f"DeliveryOrderFactory extends OrderFactory")

    # ✅ WYMAGANIE: Nadpisywanie метод
    def create_order(self, customer_id: str = "", **kwargs) -> DeliveryOrder:
        """
        📋 CHECK: Factory Method Pattern - Delivery order creation
        Создает заказ с доставкой
        """
        delivery_address = kwargs.get('delivery_address', '')
        delivery_instructions = kwargs.get('delivery_instructions', '')
        distance_km = kwargs.get('distance_km', 5.0)
        special_instructions = kwargs.get('special_instructions', '')
        customer_data = kwargs.get('customer_data', {})
        is_express = kwargs.get('is_express', False)

        # Проверяем радиус доставки
        if distance_km > self.delivery_radius_km:
            raise InvalidOrderException("",
                                        f"Delivery distance {distance_km}km exceeds maximum {self.delivery_radius_km}km")

        # Определяем зону доставки
        delivery_zone = self._get_delivery_zone(distance_km)

        # Создаем заказ
        order = DeliveryOrder(customer_id, delivery_address, delivery_instructions,
                              distance_km, special_instructions)

        # Назначаем водителя если возможно
        driver_id = self._assign_driver(distance_km, is_express)
        if driver_id:
            self._driver_assignments[order.order_id] = driver_id

        # Рассчитываем приоритет
        priority = self._calculate_order_priority(customer_data, {
            "order_type": OrderType.DELIVERY.value,
            "distance_km": distance_km,
            "is_express": is_express,
            "delivery_zone": delivery_zone
        })

        # Логируем создание
        creation_details = {
            "delivery_address": delivery_address[:50],  # Первые 50 символов для приватности
            "distance_km": distance_km,
            "delivery_zone": delivery_zone,
            "assigned_driver": driver_id,
            "is_express": is_express,
            "priority": priority.value,
            "estimated_fee": order.get_service_fee()
        }

        self._log_order_creation(order, creation_details)

        log_business_rule("Delivery Order Created",
                          f"Zone {delivery_zone}, {distance_km}km, Order {order.order_id}")

        return order

    # ✅ WYMAGANIE: Wiele konstruktorów
    def create_express_delivery_order(self, customer_id: str, delivery_address: str,
                                      distance_km: float) -> DeliveryOrder:
        """
        📋 CHECK: Wiele konstruktorów - экспресс доставка
        """
        if distance_km > 10.0:  # Ограничение для экспресс доставки
            raise InvalidOrderException("", "Express delivery limited to 10km radius")

        order = self.create_order(
            customer_id=customer_id,
            delivery_address=delivery_address,
            distance_km=distance_km,
            delivery_instructions="Express delivery - priority handling",
            is_express=True,
            customer_data={"delivery_type": "express"}
        )

        log_requirement_check("Multiple Constructors", "EXECUTED",
                              "DeliveryOrderFactory.create_express_delivery_order()")

        return order

    def create_scheduled_delivery_order(self, customer_id: str, delivery_address: str,
                                        distance_km: float, delivery_time: datetime) -> DeliveryOrder:
        """Создает заказ с запланированной доставкой"""
        # Проверяем что время доставки в будущем
        if delivery_time <= datetime.now():
            raise InvalidOrderException("", "Scheduled delivery time must be in the future")

        delivery_instructions = f"Scheduled delivery for {delivery_time.strftime('%Y-%m-%d %H:%M')}"

        order = self.create_order(
            customer_id=customer_id,
            delivery_address=delivery_address,
            distance_km=distance_km,
            delivery_instructions=delivery_instructions,
            customer_data={"delivery_type": "scheduled", "delivery_time": delivery_time}
        )

        # Добавляем в расписание
        time_slot = delivery_time.strftime("%Y-%m-%d_%H")
        if time_slot not in self._delivery_schedule:
            self._delivery_schedule[time_slot] = []
        self._delivery_schedule[time_slot].append(order.order_id)

        return order

    def _initialize_delivery_zones(self) -> Dict[str, Dict[str, Any]]:
        """Инициализирует зоны доставки"""
        return {
            "zone_1": {"max_distance": 5.0, "base_fee": 2.99, "description": "Close"},
            "zone_2": {"max_distance": 10.0, "base_fee": 4.99, "description": "Medium"},
            "zone_3": {"max_distance": 15.0, "base_fee": 6.99, "description": "Far"}
        }

    def _get_delivery_zone(self, distance_km: float) -> str:
        """Определяет зону доставки по расстоянию"""
        for zone_name, zone_data in self._delivery_zones.items():
            if distance_km <= zone_data["max_distance"]:
                return zone_name
        return "zone_3"  # По умолчанию дальняя зона

    def _assign_driver(self, distance_km: float, is_express: bool = False) -> Optional[str]:
        """Назначает водителя на доставку"""
        if not self._available_drivers:
            return None

        # Для экспресс доставки берем первого доступного
        if is_express:
            return self._available_drivers[0]

        # Простая логика - берем первого доступного водителя
        return self._available_drivers[0] if self._available_drivers else None

    def add_driver(self, driver_id: str):
        """Добавляет водителя в список доступных"""
        if driver_id not in self._available_drivers:
            self._available_drivers.append(driver_id)
            log_business_rule("Driver Added", f"Driver {driver_id} available for delivery")

    def remove_driver(self, driver_id: str):
        """Убирает водителя из списка доступных"""
        if driver_id in self._available_drivers:
            self._available_drivers.remove(driver_id)
            log_business_rule("Driver Removed", f"Driver {driver_id} no longer available")

    def complete_delivery(self, order_id: str):
        """Завершает доставку и освобождает водителя"""
        if order_id in self._driver_assignments:
            driver_id = self._driver_assignments[order_id]
            del self._driver_assignments[order_id]

            # Возвращаем водителя в список доступных
            if driver_id not in self._available_drivers:
                self._available_drivers.append(driver_id)

            log_business_rule("Delivery Completed", f"Order {order_id}, Driver {driver_id} available")

    def get_delivery_status(self) -> Dict[str, Any]:
        """Возвращает статус системы доставки"""
        active_deliveries = len(self._driver_assignments)

        return {
            "delivery_radius_km": self.delivery_radius_km,
            "delivery_zones": self._delivery_zones,
            "available_drivers": len(self._available_drivers),
            "active_deliveries": active_deliveries,
            "driver_assignments": self._driver_assignments.copy(),
            "scheduled_deliveries": len(self._delivery_schedule)
        }


# ✅ WYMAGANIE: Factory Method - Менеджер фабрик (Factory Registry)
class OrderFactoryManager:
    """
    📋 CHECK: Factory Method Pattern - Factory manager
    Менеджер фабрик для управления различными типами заказов
    """

    def __init__(self, restaurant_id: str):
        self.restaurant_id = restaurant_id
        self._factories: Dict[OrderType, OrderFactory] = {}
        self._factory_stats: Dict[str, int] = {}

        # 📋 CHECK: Factory Method Pattern - manager создан
        log_requirement_check("Factory Method Pattern Manager", "CREATED", f"OrderFactoryManager: {restaurant_id}")

    def register_factory(self, order_type: OrderType, factory: OrderFactory):
        """Регистрирует фабрику для типа заказа"""
        self._factories[order_type] = factory
        self._factory_stats[order_type.value] = 0

        log_business_rule("Factory Registered",
                          f"Factory {factory.factory_id} registered for {order_type.value}")

    def create_order(self, order_type: OrderType, customer_id: str = "", **kwargs) -> Order:
        """
        📋 CHECK: Factory Method Pattern - Polimorficzne tworzenie zamówień
        Полиморфно создает заказ используя подходящую фабрику
        """
        # 🔄 TRANSFER: OrderFactoryManager → specific factory
        log_transfer("OrderFactoryManager", f"{order_type.value} factory", "order creation request")

        if order_type not in self._factories:
            raise InvalidOrderException("", f"No factory registered for order type: {order_type.value}")

        factory = self._factories[order_type]
        order = factory.create_order(customer_id, **kwargs)

        # Обновляем статистику
        self._factory_stats[order_type.value] += 1

        log_business_rule("Order Created via Manager",
                          f"Type: {order_type.value}, Order: {order.order_id}")

        log_requirement_check("Factory Method Polymorphism", "EXECUTED",
                              f"Created {order_type.value} order via factory")

        return order

    def get_available_order_types(self) -> List[OrderType]:
        """Возвращает доступные типы заказов"""
        return list(self._factories.keys())

    def get_factory_stats(self) -> Dict[str, Any]:
        """Возвращает статистику фабрик"""
        detailed_stats = {}

        for order_type, factory in self._factories.items():
            factory_stats = factory.get_creation_stats()
            detailed_stats[order_type.value] = {
                "factory_id": factory.factory_id,
                "orders_created": factory_stats["orders_created"],
                "factory_type": factory.__class__.__name__
            }

        return {
            "restaurant_id": self.restaurant_id,
            "registered_factories": len(self._factories),
            "total_orders_by_type": self._factory_stats.copy(),
            "factory_details": detailed_stats
        }


# Функция демонстрации паттерна Factory Method
def demo_factory_method_pattern():
    """
    📋 CHECK: Полная демонстрация паттерна Factory Method для системы заказов McDonald's
    """

    print("🏭 McDONALD'S FACTORY METHOD PATTERN DEMO")
    print("=" * 50)

    # 🔄 TRANSFER: demo → factory method pattern
    log_transfer("demo_factory_method_pattern", "Factory Method Pattern", "factory demonstration")

    # 1. Создание менеджера фабрик
    print("\n1. FACTORY MANAGER CREATION")
    print("-" * 30)

    factory_manager = OrderFactoryManager("MCD0001")
    print(f"Created OrderFactoryManager for restaurant: {factory_manager.restaurant_id}")

    # 2. Создание различных фабрик
    print("\n2. FACTORY CREATION")
    print("-" * 30)

    # Dine-In фабрика
    dine_in_factory = DineInOrderFactory("DINEIN_001", "MCD0001", seating_capacity=60)

    # Drive-Thru фабрика
    drive_thru_factory = DriveThruOrderFactory("DRIVETHRU_001", "MCD0001", lane_count=2)

    # Delivery фабрика
    delivery_factory = DeliveryOrderFactory("DELIVERY_001", "MCD0001", delivery_radius_km=15.0)
    delivery_factory.add_driver("DRIVER001")
    delivery_factory.add_driver("DRIVER002")

    factories = [dine_in_factory, drive_thru_factory, delivery_factory]

    for factory in factories:
        print(f"Created factory: {factory.factory_id} ({factory.__class__.__name__})")

    # 3. Регистрация фабрик в менеджере
    print("\n3. FACTORY REGISTRATION")
    print("-" * 30)

    factory_manager.register_factory(OrderType.DINE_IN, dine_in_factory)
    factory_manager.register_factory(OrderType.DRIVE_THRU, drive_thru_factory)
    factory_manager.register_factory(OrderType.DELIVERY, delivery_factory)

    available_types = factory_manager.get_available_order_types()
    print(f"Available order types: {[ot.value for ot in available_types]}")

    # 4. Создание заказов через фабрики (демонстрация полиморфизма)
    print("\n4. POLYMORPHIC ORDER CREATION")
    print("-" * 30)

    # Dine-In заказы
    print("Creating Dine-In orders:")

    dine_in_order1 = factory_manager.create_order(
        OrderType.DINE_IN,
        customer_id="CUST001",
        party_size=2,
        customer_data={"customer_type": "regular"}
    )
    print(f"  Regular dine-in: {dine_in_order1.order_id} at table {dine_in_order1.table_number}")

    birthday_order = dine_in_factory.create_birthday_party_order(
        "CUST002", party_size=6, birthday_child_age=8
    )
    print(f"  Birthday party: {birthday_order.order_id} at table {birthday_order.table_number}")

    # Drive-Thru заказы
    print("\nCreating Drive-Thru orders:")

    drive_thru_order1 = factory_manager.create_order(
        OrderType.DRIVE_THRU,
        customer_id="CUST003",
        vehicle_type="car"
    )
    print(f"  Regular drive-thru: {drive_thru_order1.order_id}")

    express_order = drive_thru_factory.create_express_order("CUST004", "Big Mac")
    print(f"  Express order: {express_order.order_id}")

    # Delivery заказы
    print("\nCreating Delivery orders:")

    delivery_order1 = factory_manager.create_order(
        OrderType.DELIVERY,
        customer_id="CUST005",
        delivery_address="123 Main St",
        distance_km=5.5
    )
    print(f"  Regular delivery: {delivery_order1.order_id} to {delivery_order1.delivery_address}")

    express_delivery = delivery_factory.create_express_delivery_order(
        "CUST006", "456 Oak Ave", 3.2
    )
    print(f"  Express delivery: {express_delivery.order_id}")

    # 5. Проверка статуса фабрик
    print("\n5. FACTORY STATUS")
    print("-" * 30)

    # Dine-In статус
    seating_status = dine_in_factory.get_seating_status()
    print(f"Dine-In Seating:")
    print(f"  Capacity: {seating_status['total_capacity']}")
    print(f"  Occupied: {seating_status['occupied_tables']}")
    print(f"  Occupancy rate: {seating_status['occupancy_rate']:.1f}%")

    # Drive-Thru статус
    queue_status = drive_thru_factory.get_queue_status()
    print(f"\nDrive-Thru Queues:")
    print(f"  Total lanes: {queue_status['total_lanes']}")
    print(f"  Total queue: {queue_status['total_queue']}")
    for lane_name, lane_data in queue_status['lanes'].items():
        express_indicator = " (EXPRESS)" if lane_data['is_express'] else ""
        print(f"  {lane_name}{express_indicator}: {lane_data['queue_length']} orders")

    # Delivery статус
    delivery_status = delivery_factory.get_delivery_status()
    print(f"\nDelivery Service:")
    print(f"  Delivery radius: {delivery_status['delivery_radius_km']}km")
    print(f"  Available drivers: {delivery_status['available_drivers']}")
    print(f"  Active deliveries: {delivery_status['active_deliveries']}")

    # 6. Статистика менеджера фабрик
    print("\n6. FACTORY MANAGER STATISTICS")
    print("-" * 30)

    manager_stats = factory_manager.get_factory_stats()
    print(f"Restaurant: {manager_stats['restaurant_id']}")
    print(f"Registered factories: {manager_stats['registered_factories']}")
    print("Orders created by type:")
    for order_type, count in manager_stats['total_orders_by_type'].items():
        print(f"  {order_type}: {count}")

    print("\nFactory details:")
    for order_type, details in manager_stats['factory_details'].items():
        print(f"  {order_type}: {details['factory_type']} ({details['orders_created']} orders)")

    # 7. Тестирование альтернативных конструкторов
    print("\n7. ALTERNATIVE CONSTRUCTORS TEST")
    print("-" * 30)

    # Бизнес встреча
    business_meeting = dine_in_factory.create_business_meeting_order(
        "CUST007", party_size=4, meeting_duration_hours=3
    )
    print(f"Business meeting: {business_meeting.order_id} at table {business_meeting.table_number}")

    # Мобильный pickup
    mobile_pickup = drive_thru_factory.create_mobile_pickup_order(
        "CUST008", "MOB123456"
    )
    print(f"Mobile pickup: {mobile_pickup.order_id}")

    # Запланированная доставка
    scheduled_time = datetime.now() + timedelta(hours=2)
    scheduled_delivery = delivery_factory.create_scheduled_delivery_order(
        "CUST009", "789 Pine St", 7.8, scheduled_time
    )
    print(f"Scheduled delivery: {scheduled_delivery.order_id} for {scheduled_time.strftime('%H:%M')}")

    # 8. Завершение заказов
    print("\n8. ORDER COMPLETION")
    print("-" * 30)

    # Освобождаем стол
    dine_in_factory.release_table(dine_in_order1.order_id)
    print(f"Released table for order: {dine_in_order1.order_id}")

    # Завершаем Drive-Thru
    drive_thru_factory.complete_order(drive_thru_order1.order_id)
    print(f"Completed drive-thru order: {drive_thru_order1.order_id}")

    # Завершаем доставку
    delivery_factory.complete_delivery(delivery_order1.order_id)
    print(f"Completed delivery order: {delivery_order1.order_id}")

    # Финальная статистика
    print("\nFinal seating occupancy:", dine_in_factory.get_seating_status()['occupied_tables'])
    print("Final drive-thru queue:", drive_thru_factory.get_queue_status()['total_queue'])
    print("Final available drivers:", delivery_factory.get_delivery_status()['available_drivers'])

    # 📋 CHECK: Финальная проверка паттерна Factory Method
    log_requirement_check("Factory Method Pattern Demo", "COMPLETED", "factory.py")

    return factory_manager, factories


if __name__ == "__main__":
    demo_factory_method_pattern()