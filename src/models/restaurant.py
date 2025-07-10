"""
McDonald's Management System - Restaurant Model
✅ WYMAGANIE: Główna klasa łącząca wszystkie komponenty systemu
✅ WYMAGANIE: Użycie wszystkich wzorców projektowych i mechanizmów OOP

Главный класс ресторана McDonald's интегрирующий все компоненты системы
"""

from datetime import datetime, time, timedelta
from typing import List, Dict, Optional, Any, Tuple, Set
from enum import Enum
import sys
import os

# Добавляем пути для импорта всех компонентов
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils.logger import log_transfer, log_requirement_check, log_operation, log_business_rule
from src.exceptions.mcdonalds_exceptions import *
from src.models.menu import MenuItem, Burger, Fries, Drink, BreakfastItem, MenuCategory, ItemSize
from src.models.staff import Staff, Cashier, KitchenStaff, ShiftManager, GeneralManager, StaffRole, AccessLevel
from src.models.customer import Customer, RegularCustomer, LoyaltyCustomer, VIPCustomer, CustomerType
from src.models.order import Order, DineInOrder, TakeoutOrder, DriveThruOrder, DeliveryOrder, OrderStatus, OrderType
from src.models.payment import Payment, CashPayment, CardPayment, MobilePayment, GiftCardPayment, PaymentStatus


class RestaurantStatus(Enum):
    CLOSED = "closed"
    OPENING = "opening"
    OPEN = "open"
    BUSY = "busy"
    CLOSING = "closing"
    MAINTENANCE = "maintenance"
    EMERGENCY_CLOSED = "emergency_closed"


class OperationHours(Enum):
    BREAKFAST_START = time(5, 0)  # 5:00 AM
    BREAKFAST_END = time(10, 30)  # 10:30 AM
    LUNCH_START = time(10, 30)  # 10:30 AM
    LUNCH_END = time(16, 0)  # 4:00 PM
    DINNER_START = time(16, 0)  # 4:00 PM
    DINNER_END = time(23, 0)  # 11:00 PM
    LATE_NIGHT_START = time(23, 0)  # 11:00 PM
    LATE_NIGHT_END = time(5, 0)  # 5:00 AM


# ✅ WYMAGANIE: Główna klasa - McDonald's Restaurant
class McDonaldsRestaurant:
    """
    📋 CHECK: Główna klasa - Главный класс ресторана McDonald's
    ✅ WYMAGANIE: Integracja wszystkich komponentów systemu

    Центральный класс управляющий всеми аспектами ресторана McDonald's:
    - Меню и позиции
    - Персонал и смены
    - Клиенты и лояльность
    - Заказы и платежи
    - Операционные процессы
    """

    # Атрибуты класса
    total_restaurants = 0
    franchise_network = {}
    corporate_standards = {
        "max_wait_time": 90,  # seconds
        "food_safety_temp": 165,  # Fahrenheit
        "customer_satisfaction_target": 4.5,  # out of 5
        "employee_retention_target": 0.85  # 85%
    }

    def __init__(self, restaurant_id: str, location: str, franchise_owner: str = "",
                 seating_capacity: int = 60, drive_thru_lanes: int = 1):
        # 🔄 TRANSFER: restaurant.py → logger (restaurant creation)
        log_operation("Restaurant Creation", {
            "id": restaurant_id,
            "location": location,
            "owner": franchise_owner
        })

        # Основные атрибуты ресторана
        self.restaurant_id = restaurant_id
        self.location = location
        self.franchise_owner = franchise_owner
        self.seating_capacity = seating_capacity
        self.drive_thru_lanes = drive_thru_lanes

        # Операционные атрибуты
        self._status = RestaurantStatus.CLOSED
        self._opened_at: Optional[datetime] = None
        self._daily_sales = 0.0
        self._customer_count_today = 0
        self._orders_served_today = 0

        # Компоненты системы
        self._menu_items: Dict[str, MenuItem] = {}
        self._staff_members: Dict[str, Staff] = {}
        self._customers: Dict[str, Customer] = {}
        self._active_orders: Dict[str, Order] = {}
        self._completed_orders: List[Order] = []
        self._payment_history: List[Payment] = []

        # Текущие операции
        self._current_shift_staff: Set[str] = set()
        self._kitchen_queue: List[str] = []  # Order IDs
        self._drive_thru_queue: List[str] = []  # Order IDs
        self._waiting_customers: Dict[int, str] = {}  # table_number -> customer_id

        # Инвентарь и ресурсы
        self._inventory: Dict[str, int] = {}
        self._equipment_status: Dict[str, str] = {}
        self._daily_specials: List[str] = []

        # Обновляем глобальные счетчики
        McDonaldsRestaurant.total_restaurants += 1
        if franchise_owner:
            if franchise_owner not in McDonaldsRestaurant.franchise_network:
                McDonaldsRestaurant.franchise_network[franchise_owner] = []
            McDonaldsRestaurant.franchise_network[franchise_owner].append(restaurant_id)

        # Инициализируем стандартное меню и персонал
        self._initialize_standard_menu()
        self._initialize_basic_inventory()
        self._initialize_equipment()

        # 📋 CHECK: Główna klasa - подтверждение создания
        log_requirement_check("Main Class Creation", "SUCCESS", f"McDonaldsRestaurant: {restaurant_id}")

    # ✅ WYMAGANIE: Enkapsulacja - Properties для состояния ресторана
    @property
    def status(self) -> RestaurantStatus:
        """Текущий статус ресторана"""
        return self._status

    @status.setter
    def status(self, value: RestaurantStatus):
        """
        📋 CHECK: Enkapsulacja - Setter с бизнес-логикой
        """
        old_status = self._status
        self._status = value

        # Логика при изменении статуса
        if value == RestaurantStatus.OPEN and old_status == RestaurantStatus.OPENING:
            self._opened_at = datetime.now()
            log_business_rule("Restaurant Opened", f"{self.restaurant_id} opened for business")
        elif value == RestaurantStatus.CLOSED:
            self._process_end_of_day()

        log_business_rule("Status Change", f"{self.restaurant_id}: {old_status.value} → {value.value}")

    @property
    def is_open(self) -> bool:
        """Проверяет открыт ли ресторан"""
        return self._status in [RestaurantStatus.OPEN, RestaurantStatus.BUSY]

    @property
    def daily_sales(self) -> float:
        """Продажи за день"""
        return self._daily_sales

    @property
    def active_orders_count(self) -> int:
        """Количество активных заказов"""
        return len(self._active_orders)

    @property
    def staff_on_duty(self) -> int:
        """Количество персонала на смене"""
        return len(self._current_shift_staff)

    # ✅ WYMAGANIE: @classmethod - Factory methods для ресторанов
    @classmethod
    def create_franchise_restaurant(cls, location: str, owner: str, investment: float):
        """
        📋 CHECK: @classmethod - Создание франчайзи ресторана
        """
        restaurant_id = f"MCD{cls.total_restaurants + 1:04d}"

        # Размер ресторана зависит от инвестиций
        if investment >= 500000:
            seating = 80
            drive_thru = 2
        elif investment >= 300000:
            seating = 60
            drive_thru = 1
        else:
            seating = 40
            drive_thru = 0

        restaurant = cls(restaurant_id, location, owner, seating, drive_thru)
        restaurant._add_metadata("investment_amount", investment)
        restaurant._add_metadata("restaurant_type", "franchise")

        log_requirement_check("@classmethod", "EXECUTED", "McDonaldsRestaurant.create_franchise_restaurant()")
        log_business_rule("Franchise Created", f"{location} franchise by {owner}: ${investment:,.2f}")

        return restaurant

    @classmethod
    def create_corporate_restaurant(cls, location: str, market_size: str = "medium"):
        """Создает корпоративный ресторан"""
        restaurant_id = f"CORP{cls.total_restaurants + 1:04d}"

        size_config = {
            "small": (40, 1),
            "medium": (60, 1),
            "large": (100, 2),
            "flagship": (150, 3)
        }

        seating, drive_thru = size_config.get(market_size, (60, 1))

        restaurant = cls(restaurant_id, location, "McDonald's Corporation", seating, drive_thru)
        restaurant._add_metadata("restaurant_type", "corporate")
        restaurant._add_metadata("market_size", market_size)

        return restaurant

    @classmethod
    def get_franchise_stats(cls) -> Dict[str, Any]:
        """Возвращает статистику по франчайзи"""
        return {
            "total_restaurants": cls.total_restaurants,
            "franchise_owners": len(cls.franchise_network),
            "franchise_network": cls.franchise_network.copy(),
            "corporate_standards": cls.corporate_standards.copy()
        }

    # ✅ WYMAGANIE: @staticmethod - Утилитарные методы
    @staticmethod
    def calculate_optimal_staff_count(expected_customers: int, average_service_time: float) -> Dict[str, int]:
        """
        📋 CHECK: @staticmethod - Расчет оптимального количества персонала
        """
        # Расчет на основе теории очередей
        cashiers_needed = max(2, int(expected_customers * average_service_time / 3600))  # per hour
        kitchen_staff_needed = max(3, int(cashiers_needed * 1.5))
        managers_needed = max(1, int((cashiers_needed + kitchen_staff_needed) / 8))

        staff_plan = {
            "cashiers": cashiers_needed,
            "kitchen_staff": kitchen_staff_needed,
            "managers": managers_needed,
            "total": cashiers_needed + kitchen_staff_needed + managers_needed
        }

        log_requirement_check("@staticmethod", "EXECUTED", "McDonaldsRestaurant.calculate_optimal_staff_count()")
        return staff_plan

    @staticmethod
    def validate_restaurant_id(restaurant_id: str) -> bool:
        """Валидирует ID ресторана"""
        if not restaurant_id:
            return False
        return (restaurant_id.startswith("MCD") or restaurant_id.startswith("CORP")) and len(restaurant_id) >= 7

    @staticmethod
    def calculate_break_even_point(fixed_costs: float, variable_cost_per_order: float,
                                   average_order_value: float) -> int:
        """Рассчитывает точку безубыточности"""
        if average_order_value <= variable_cost_per_order:
            return -1  # Невозможно достичь безубыточности

        contribution_margin = average_order_value - variable_cost_per_order
        break_even_orders = int(fixed_costs / contribution_margin)

        return break_even_orders

    # ===== МЕНЮ И ИНВЕНТАРЬ =====

    def _initialize_standard_menu(self):
        """Инициализирует стандартное меню McDonald's"""
        # 🔄 TRANSFER: restaurant.py → menu items (standard menu initialization)
        log_transfer("McDonaldsRestaurant", "MenuItem classes", "standard menu setup")

        # Создаем стандартные позиции меню
        big_mac = MenuItem.create_big_mac()
        quarter_pounder = Burger("Quarter Pounder with Cheese", 5.49, 1, True)
        mcchicken = Burger("McChicken", 3.99, 1, False, ["chicken patty", "lettuce", "mayo"])

        fries_small = Fries(ItemSize.SMALL)
        fries_medium = Fries(ItemSize.MEDIUM)
        fries_large = Fries(ItemSize.LARGE)

        coke = Drink.create_coca_cola(ItemSize.MEDIUM)
        coffee = Drink.create_mccafe_coffee("Latte", ItemSize.LARGE)

        # Добавляем в меню
        menu_items = [big_mac, quarter_pounder, mcchicken, fries_small, fries_medium,
                      fries_large, coke, coffee]

        for item in menu_items:
            self._menu_items[item.name] = item

        log_business_rule("Menu Initialized", f"{len(menu_items)} standard items added")

    def add_menu_item(self, item: MenuItem):
        """Добавляет позицию в меню"""
        self._menu_items[item.name] = item
        log_business_rule("Menu Item Added", f"{self.restaurant_id}: {item.name}")

    def remove_menu_item(self, item_name: str):
        """Убирает позицию из меню"""
        if item_name in self._menu_items:
            del self._menu_items[item_name]
            log_business_rule("Menu Item Removed", f"{self.restaurant_id}: {item_name}")

    def get_available_menu_items(self) -> List[MenuItem]:
        """Возвращает доступные позиции меню"""
        available = []
        for item in self._menu_items.values():
            if item.available:
                # Проверяем время для завтраков
                if isinstance(item, BreakfastItem) and not MenuItem.is_breakfast_time():
                    continue
                available.append(item)
        return available

    def update_inventory(self, ingredient: str, quantity: int):
        """Обновляет инвентарь"""
        self._inventory[ingredient] = self._inventory.get(ingredient, 0) + quantity
        log_business_rule("Inventory Updated", f"{ingredient}: +{quantity} (total: {self._inventory[ingredient]})")

    def _initialize_basic_inventory(self):
        """Инициализирует базовый инвентарь"""
        basic_inventory = {
            "beef_patty": 200,
            "chicken_patty": 150,
            "cheese": 300,
            "lettuce": 100,
            "tomato": 80,
            "onion": 90,
            "pickles": 200,
            "fries": 500,
            "coca_cola_syrup": 50,
            "coffee_beans": 20,
            "milk": 30
        }

        self._inventory.update(basic_inventory)
        log_business_rule("Inventory Initialized", f"{len(basic_inventory)} items stocked")

    # ===== ПЕРСОНАЛ =====

    def hire_staff_member(self, staff: Staff) -> bool:
        """Нанимает сотрудника"""
        if staff.employee_id in self._staff_members:
            log_business_rule("Hire Failed", f"Employee {staff.employee_id} already exists")
            return False

        self._staff_members[staff.employee_id] = staff
        log_business_rule("Staff Hired", f"{self.restaurant_id}: {staff.name} ({staff.role.value})")
        return True

    def terminate_staff_member(self, employee_id: str, reason: str = ""):
        """Увольняет сотрудника"""
        if employee_id in self._staff_members:
            staff = self._staff_members[employee_id]
            staff.is_active = False
            del self._staff_members[employee_id]

            # Убираем с текущей смены
            self._current_shift_staff.discard(employee_id)

            log_business_rule("Staff Terminated", f"{staff.name}: {reason}")

    def start_shift(self, employee_id: str) -> bool:
        """Начинает смену сотрудника"""
        if employee_id not in self._staff_members:
            return False

        staff = self._staff_members[employee_id]
        if not staff.is_active:
            return False

        self._current_shift_staff.add(employee_id)
        log_business_rule("Shift Started", f"{staff.name} started shift at {self.restaurant_id}")
        return True

    def end_shift(self, employee_id: str) -> bool:
        """Заканчивает смену сотрудника"""
        if employee_id in self._current_shift_staff:
            self._current_shift_staff.remove(employee_id)
            staff = self._staff_members[employee_id]
            log_business_rule("Shift Ended", f"{staff.name} ended shift")
            return True
        return False

    def get_staff_by_role(self, role: StaffRole) -> List[Staff]:
        """Возвращает персонал по роли"""
        return [staff for staff in self._staff_members.values() if staff.role == role and staff.is_active]

    # ===== КЛИЕНТЫ =====

    def register_customer(self, customer: Customer):
        """Регистрирует клиента"""
        self._customers[customer.customer_id] = customer
        log_business_rule("Customer Registered", f"{customer.name} ({customer.get_customer_type().value})")

    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Получает клиента по ID"""
        return self._customers.get(customer_id)

    def get_vip_customers(self) -> List[VIPCustomer]:
        """Возвращает VIP клиентов"""
        return [customer for customer in self._customers.values()
                if isinstance(customer, VIPCustomer)]

    # ===== ЗАКАЗЫ =====

    def create_order(self, order_type: OrderType, customer_id: str = "", **kwargs) -> Order:
        """
        📋 CHECK: Wzorzec Factory Method - Создание заказов разных типов
        Factory method для создания заказов
        """
        # 🔄 TRANSFER: restaurant.py → order classes (order creation)
        log_transfer("McDonaldsRestaurant", "Order classes", "order creation request")

        # Factory logic для создания правильного типа заказа
        if order_type == OrderType.DINE_IN:
            order = DineInOrder(customer_id, kwargs.get('table_number', 1),
                                kwargs.get('party_size', 1), kwargs.get('special_instructions', ''))
        elif order_type == OrderType.TAKEOUT:
            order = TakeoutOrder(customer_id, kwargs.get('pickup_time'),
                                 kwargs.get('special_instructions', ''))
        elif order_type == OrderType.DRIVE_THRU:
            order = DriveThruOrder(customer_id, kwargs.get('vehicle_type', 'car'),
                                   kwargs.get('special_instructions', ''))
        elif order_type == OrderType.DELIVERY:
            order = DeliveryOrder(customer_id, kwargs.get('address', ''),
                                  kwargs.get('delivery_instructions', ''),
                                  kwargs.get('distance_km', 5.0),
                                  kwargs.get('special_instructions', ''))
        else:
            raise ValueError(f"Unsupported order type: {order_type}")

        # Добавляем в активные заказы
        self._active_orders[order.order_id] = order

        log_business_rule("Order Created", f"{order_type.value} order {order.order_id}")
        log_requirement_check("Factory Method", "EXECUTED", f"Order creation: {order_type.value}")

        return order

    def add_item_to_order(self, order_id: str, item_name: str, quantity: int = 1,
                          customizations: List[str] = None):
        """Добавляет позицию к заказу"""
        if order_id not in self._active_orders:
            raise InvalidOrderException(order_id, "Order not found")

        if item_name not in self._menu_items:
            raise MenuItemNotAvailableException(item_name, "Item not on menu")

        order = self._active_orders[order_id]
        menu_item = self._menu_items[item_name]

        # Проверяем доступность
        if not menu_item.available:
            raise MenuItemNotAvailableException(item_name, "Item temporarily unavailable")

        # Добавляем в заказ
        price = menu_item.get_final_price()
        order.add_item(item_name, quantity, price, customizations)

        log_business_rule("Item Added to Order", f"Order {order_id}: {quantity}x {item_name}")

    def process_order_payment(self, order_id: str, payment: Payment) -> bool:
        """
        📋 CHECK: Polimorfizm - Обработка платежей разных типов
        """
        if order_id not in self._active_orders:
            raise InvalidOrderException(order_id, "Order not found")

        order = self._active_orders[order_id]

        # Проверяем сумму
        if payment.amount < order.total_amount:
            raise PaymentProcessingException(payment.get_payment_method().value,
                                             payment.amount, "Insufficient payment amount")

        # Обрабатываем платеж полиморфно
        try:
            success = payment.process_payment()
            if success:
                order.payment_status = PaymentStatus.COMPLETED
                order.status = OrderStatus.CONFIRMED

                # Добавляем в очередь кухни
                self._kitchen_queue.append(order_id)

                # Сохраняем платеж
                self._payment_history.append(payment)
                self._daily_sales += payment.net_amount

                log_business_rule("Payment Processed",
                                  f"Order {order_id}: {payment.get_payment_method().value} ${payment.amount:.2f}")
                return True
            else:
                order.payment_status = PaymentStatus.FAILED
                return False

        except Exception as e:
            order.payment_status = PaymentStatus.FAILED
            log_business_rule("Payment Failed", f"Order {order_id}: {str(e)}")
            return False

    def complete_order(self, order_id: str):
        """Завершает заказ"""
        if order_id not in self._active_orders:
            return False

        order = self._active_orders[order_id]
        order.status = OrderStatus.COMPLETED

        # Перемещаем в завершенные
        self._completed_orders.append(order)
        del self._active_orders[order_id]

        # Убираем из очередей
        if order_id in self._kitchen_queue:
            self._kitchen_queue.remove(order_id)

        self._orders_served_today += 1

        log_business_rule("Order Completed", f"Order {order_id} completed")
        return True

    # ===== ОПЕРАЦИИ РЕСТОРАНА =====

    def open_restaurant(self) -> bool:
        """Открывает ресторан"""
        if self._status != RestaurantStatus.CLOSED:
            log_business_rule("Open Failed", f"{self.restaurant_id} not in closed status")
            return False

        # Проверяем готовность
        if not self._check_opening_readiness():
            return False

        self.status = RestaurantStatus.OPENING

        # Процедуры открытия
        self._initialize_equipment()
        self._prepare_for_service()

        self.status = RestaurantStatus.OPEN
        return True

    def close_restaurant(self) -> bool:
        """Закрывает ресторан"""
        if not self.is_open:
            return False

        self.status = RestaurantStatus.CLOSING

        # Завершаем активные заказы
        self._finish_remaining_orders()

        # Процедуры закрытия
        self._end_all_shifts()
        self._process_end_of_day()

        self.status = RestaurantStatus.CLOSED
        return True

    def _check_opening_readiness(self) -> bool:
        """Проверяет готовность к открытию"""
        # Проверяем персонал
        if len(self._current_shift_staff) < 3:
            log_business_rule("Opening Check Failed", "Insufficient staff")
            return False

        # Проверяем оборудование
        critical_equipment = ["grill", "fryer", "pos_system", "coffee_machine"]
        for equipment in critical_equipment:
            if self._equipment_status.get(equipment) != "operational":
                log_business_rule("Opening Check Failed", f"{equipment} not operational")
                return False

        # Проверяем инвентарь
        critical_ingredients = ["beef_patty", "fries", "coca_cola_syrup"]
        for ingredient in critical_ingredients:
            if self._inventory.get(ingredient, 0) < 50:
                log_business_rule("Opening Check Failed", f"Low {ingredient} inventory")
                return False

        log_business_rule("Opening Check Passed", f"{self.restaurant_id} ready to open")
        return True

    def _initialize_equipment(self):
        """Инициализирует оборудование"""
        equipment = {
            "grill": "operational",
            "fryer": "operational",
            "pos_system": "operational",
            "coffee_machine": "operational",
            "ice_cream_machine": "maintenance",  # Классическая шутка McDonald's
            "drive_thru_system": "operational",
            "registers": "operational"
        }

        self._equipment_status.update(equipment)
        log_business_rule("Equipment Initialized", f"{len(equipment)} pieces of equipment")

    def _prepare_for_service(self):
        """Подготавливает к обслуживанию"""
        # Сбрасываем дневные счетчики
        self._customer_count_today = 0
        self._orders_served_today = 0
        self._daily_sales = 0.0

        # Очищаем очереди
        self._kitchen_queue.clear()
        self._drive_thru_queue.clear()

        log_business_rule("Service Prepared", f"{self.restaurant_id} ready for customers")

    def _finish_remaining_orders(self):
        """Завершает оставшиеся заказы"""
        for order_id in list(self._active_orders.keys()):
            order = self._active_orders[order_id]
            if order.status in [OrderStatus.CONFIRMED, OrderStatus.IN_PREPARATION]:
                self.complete_order(order_id)

    def _end_all_shifts(self):
        """Завершает все смены"""
        for employee_id in list(self._current_shift_staff):
            self.end_shift(employee_id)

    def _process_end_of_day(self):
        """Обрабатывает конец дня"""
        # Генерируем дневной отчет
        daily_report = self.generate_daily_report()

        # Сохраняем метаданные дня
        self._add_metadata(f"daily_report_{datetime.now().strftime('%Y%m%d')}", daily_report)

        log_business_rule("End of Day",
                          f"{self.restaurant_id}: ${self._daily_sales:.2f} sales, {self._orders_served_today} orders")

    # ===== ОТЧЕТЫ И АНАЛИТИКА =====

    def generate_daily_report(self) -> Dict[str, Any]:
        """Генерирует дневной отчет"""
        # Статистика по заказам
        order_types = {}
        payment_methods = {}

        for order in self._completed_orders:
            order_type = order.get_order_type().value
            order_types[order_type] = order_types.get(order_type, 0) + 1

        for payment in self._payment_history:
            method = payment.get_payment_method().value
            payment_methods[method] = payment_methods.get(method, 0) + 1

        report = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "restaurant_id": self.restaurant_id,
            "sales": {
                "total_sales": self._daily_sales,
                "orders_count": self._orders_served_today,
                "customers_served": self._customer_count_today,
                "average_order_value": self._daily_sales / max(self._orders_served_today, 1)
            },
            "orders": {
                "by_type": order_types,
                "total_completed": len(self._completed_orders),
                "active_orders": len(self._active_orders)
            },
            "payments": {
                "by_method": payment_methods,
                "total_transactions": len(self._payment_history)
            },
            "staff": {
                "total_staff": len(self._staff_members),
                "on_duty_peak": max(len(self._current_shift_staff), 0),
                "by_role": {role.value: len(self.get_staff_by_role(role))
                            for role in StaffRole}
            },
            "operations": {
                "hours_open": self._calculate_hours_open(),
                "kitchen_efficiency": self._calculate_kitchen_efficiency(),
                "customer_satisfaction": self._estimate_customer_satisfaction()
            }
        }

        return report

    def generate_financial_summary(self, period_days: int = 7) -> Dict[str, Any]:
        """Генерирует финансовую сводку"""
        # Упрощенная версия - в реальности бы брали данные из БД
        estimated_daily_costs = {
            "staff_wages": len(self._staff_members) * 120,  # $120 per staff per day
            "food_costs": self._daily_sales * 0.30,  # 30% food cost
            "utilities": 200,  # $200 per day
            "rent": 300,  # $300 per day
            "other": 150  # $150 other costs
        }

        total_daily_costs = sum(estimated_daily_costs.values())
        daily_profit = self._daily_sales - total_daily_costs

        return {
            "period": f"{period_days} days",
            "revenue": self._daily_sales * period_days,
            "costs": {
                "daily": estimated_daily_costs,
                "total": total_daily_costs * period_days
            },
            "profit": {
                "daily": daily_profit,
                "total": daily_profit * period_days,
                "margin": (daily_profit / max(self._daily_sales, 1)) * 100
            }
        }

    def _calculate_hours_open(self) -> float:
        """Рассчитывает часы работы"""
        if self._opened_at:
            return (datetime.now() - self._opened_at).total_seconds() / 3600
        return 0.0

    def _calculate_kitchen_efficiency(self) -> float:
        """Рассчитывает эффективность кухни"""
        if not self._completed_orders:
            return 0.0

        total_prep_time = sum(order.estimated_prep_time for order in self._completed_orders)
        average_prep_time = total_prep_time / len(self._completed_orders)

        # Эффективность = 100% если среднее время <= 5 минут
        target_time = 5.0
        efficiency = min(100, (target_time / max(average_prep_time, 1)) * 100)
        return round(efficiency, 1)

    def _estimate_customer_satisfaction(self) -> float:
        """Оценивает удовлетворенность клиентов"""
        # Упрощенная оценка на основе времени ожидания и эффективности
        kitchen_efficiency = self._calculate_kitchen_efficiency()
        wait_time_factor = 100 - min(50, len(self._kitchen_queue) * 5)

        satisfaction = (kitchen_efficiency + wait_time_factor) / 2 / 20  # Scale to 5.0
        return min(5.0, max(1.0, satisfaction))

    # ===== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ =====

    def _add_metadata(self, key: str, value: Any):
        """Добавляет метаданные ресторана"""
        if not hasattr(self, '_metadata'):
            self._metadata = {}
        self._metadata[key] = value

    def get_current_status_summary(self) -> Dict[str, Any]:
        """Возвращает текущую сводку состояния"""
        return {
            "restaurant_id": self.restaurant_id,
            "location": self.location,
            "status": self._status.value,
            "is_open": self.is_open,
            "daily_sales": self._daily_sales,
            "orders_today": self._orders_served_today,
            "customers_today": self._customer_count_today,
            "active_orders": len(self._active_orders),
            "kitchen_queue": len(self._kitchen_queue),
            "staff_on_duty": len(self._current_shift_staff),
            "seating_capacity": self.seating_capacity,
            "drive_thru_lanes": self.drive_thru_lanes
        }

    def __str__(self) -> str:
        return f"McDonald's {self.restaurant_id} ({self.location}) - {self._status.value}"

    def __repr__(self) -> str:
        return f"McDonaldsRestaurant(id='{self.restaurant_id}', location='{self.location}', status={self._status.value})"


# Функция демонстрации полной системы ресторана
def demo_restaurant_system():
    """
    📋 CHECK: Полная демонстрация интегрированной системы ресторана McDonald's
    """

    print("🏪 McDONALD'S RESTAURANT SYSTEM DEMO")
    print("=" * 60)

    # 🔄 TRANSFER: demo → restaurant system
    log_transfer("demo_restaurant_system", "McDonaldsRestaurant", "full system demonstration")

    # 1. Создание ресторана
    print("\n1. RESTAURANT CREATION")
    print("-" * 30)

    restaurant = McDonaldsRestaurant.create_franchise_restaurant(
        "Downtown Chicago", "John Smith", 450000
    )
    print(f"Created: {restaurant}")

    # 2. Найм персонала
    print("\n2. STAFF HIRING")
    print("-" * 30)

    # Создаем и нанимаем персонал
    manager = GeneralManager("Alice Johnson", "EMP1001", "North Metro", 1)
    cashier1 = Cashier("Bob Wilson", "EMP1002", register_number=1)
    cashier2 = Cashier("Carol Davis", "EMP1003", register_number=2)
    cook1 = KitchenStaff("David Miller", "EMP1004", "grill")
    cook2 = KitchenStaff("Emma Garcia", "EMP1005", "fryer")

    staff_members = [manager, cashier1, cashier2, cook1, cook2]

    for staff in staff_members:
        restaurant.hire_staff_member(staff)
        restaurant.start_shift(staff.employee_id)
        print(f"Hired and started shift: {staff.name} ({staff.role.value})")

    # 3. Открытие ресторана
    print("\n3. RESTAURANT OPERATIONS")
    print("-" * 30)

    opened = restaurant.open_restaurant()
    print(f"Restaurant opened: {opened}")
    print(f"Status: {restaurant.status.value}")
    print(f"Staff on duty: {restaurant.staff_on_duty}")

    # 4. Регистрация клиентов
    print("\n4. CUSTOMER REGISTRATION")
    print("-" * 30)

    # Создаем разных типов клиентов
    regular_customer = RegularCustomer("John Doe", "+1234567890")
    loyalty_customer = LoyaltyCustomer.create_app_signup("Sarah Wilson", "+1987654321", "sarah@email.com")
    vip_customer = VIPCustomer.create_celebrity_vip("Famous Person", "+1555999888", "Manager Alice")

    customers = [regular_customer, loyalty_customer, vip_customer]

    for customer in customers:
        restaurant.register_customer(customer)
        print(f"Registered: {customer}")

    # 5. Создание и обработка заказов
    print("\n5. ORDER PROCESSING")
    print("-" * 30)

    # Создаем разные типы заказов
    dine_in_order = restaurant.create_order(OrderType.DINE_IN, regular_customer.customer_id,
                                            table_number=5, party_size=2)
    drive_thru_order = restaurant.create_order(OrderType.DRIVE_THRU, loyalty_customer.customer_id,
                                               vehicle_type="car")
    delivery_order = restaurant.create_order(OrderType.DELIVERY, vip_customer.customer_id,
                                             address="123 VIP Street", distance_km=3.0)

    orders = [dine_in_order, drive_thru_order, delivery_order]

    # Добавляем позиции к заказам
    for order in orders:
        restaurant.add_item_to_order(order.order_id, "Big Mac", 1)
        restaurant.add_item_to_order(order.order_id, "French Fries (Medium)", 1)
        restaurant.add_item_to_order(order.order_id, "Coca-Cola", 1)
        print(f"Created order {order.order_id}: {order.get_order_type().value} - ${order.total_amount:.2f}")

    # 6. Обработка платежей (демонстрация полиморфизма)
    print("\n6. PAYMENT PROCESSING (Polymorphism)")
    print("-" * 30)

    # Создаем разные типы платежей
    cash_payment = CashPayment.create_exact_change(dine_in_order.total_amount)
    card_payment = CardPayment.create_contactless_payment(drive_thru_order.total_amount, "TOKEN123")
    mobile_payment = MobilePayment.create_apple_pay(delivery_order.total_amount, "DEVICE456")

    payments = [
        (dine_in_order.order_id, cash_payment),
        (drive_thru_order.order_id, card_payment),
        (delivery_order.order_id, mobile_payment)
    ]

    for order_id, payment in payments:
        success = restaurant.process_order_payment(order_id, payment)
        print(f"Payment for {order_id}: {payment.get_payment_method().value} - {'SUCCESS' if success else 'FAILED'}")

    # 7. Завершение заказов
    print("\n7. ORDER COMPLETION")
    print("-" * 30)

    for order in orders:
        restaurant.complete_order(order.order_id)
        print(f"Completed order: {order.order_id}")

    # 8. Генерация отчетов
    print("\n8. REPORTS AND ANALYTICS")
    print("-" * 30)

    daily_report = restaurant.generate_daily_report()
    print(f"Daily Sales: ${daily_report['sales']['total_sales']:.2f}")
    print(f"Orders Served: {daily_report['sales']['orders_count']}")
    print(f"Average Order Value: ${daily_report['sales']['average_order_value']:.2f}")
    print(f"Kitchen Efficiency: {daily_report['operations']['kitchen_efficiency']:.1f}%")
    print(f"Customer Satisfaction: {daily_report['operations']['customer_satisfaction']:.1f}/5.0")

    financial_summary = restaurant.generate_financial_summary(1)
    print(f"Daily Profit: ${financial_summary['profit']['daily']:.2f}")
    print(f"Profit Margin: {financial_summary['profit']['margin']:.1f}%")

    # 9. Статус системы
    print("\n9. SYSTEM STATUS")
    print("-" * 30)

    status_summary = restaurant.get_current_status_summary()
    print(f"Restaurant Status: {status_summary['status']}")
    print(f"Active Orders: {status_summary['active_orders']}")
    print(f"Staff on Duty: {status_summary['staff_on_duty']}")
    print(f"Daily Sales: ${status_summary['daily_sales']:.2f}")

    franchise_stats = McDonaldsRestaurant.get_franchise_stats()
    print(f"Total Restaurants: {franchise_stats['total_restaurants']}")
    print(f"Franchise Owners: {franchise_stats['franchise_owners']}")

    # 10. Закрытие ресторана
    print("\n10. RESTAURANT CLOSING")
    print("-" * 30)

    closed = restaurant.close_restaurant()
    print(f"Restaurant closed: {closed}")
    print(f"Final status: {restaurant.status.value}")

    # 📋 CHECK: Финальная проверка интеграции
    log_requirement_check("Restaurant System Integration", "COMPLETED", "restaurant.py")
    log_requirement_check("Full System Demo", "COMPLETED", "McDonald's Management System")

    return restaurant


if __name__ == "__main__":
    demo_restaurant_system()