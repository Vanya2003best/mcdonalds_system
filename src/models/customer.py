"""
McDonald's Management System - Customer Models
✅ WYMAGANIE: Użycie klas, dziedziczenie, enkapsulacja, @classmethod, @staticmethod

Модели клиентов McDonald's с программой лояльности
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from enum import Enum
import sys
import os

# Добавляем пути для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils.logger import log_transfer, log_requirement_check, log_operation, log_business_rule
from src.exceptions.mcdonalds_exceptions import McDonaldsException


class CustomerType(Enum):
    REGULAR = "regular"
    LOYALTY_MEMBER = "loyalty_member"
    VIP = "vip"
    EMPLOYEE = "employee"


class LoyaltyTier(Enum):
    BRONZE = "bronze"  # 0-499 points
    SILVER = "silver"  # 500-1999 points
    GOLD = "gold"  # 2000-4999 points
    PLATINUM = "platinum"  # 5000+ points


class CustomerException(McDonaldsException):
    """Исключения связанные с клиентами"""
    pass


class InsufficientLoyaltyPointsException(CustomerException):
    """Исключение при недостатке баллов лояльности"""

    def __init__(self, required: int, available: int, customer_id: str):
        self.required = required
        self.available = available
        self.customer_id = customer_id
        message = f"Customer {customer_id}: need {required} points, have {available}"
        super().__init__(message, "INSUFFICIENT_LOYALTY_POINTS",
                         {"required": required, "available": available, "customer": customer_id})


# ✅ WYMAGANIE: Użycie klas - Базовый класс для всех клиентов
class Customer(ABC):
    """
    📋 CHECK: Klasy - Абстрактный базовый класс для всех клиентов McDonald's
    ✅ WYMAGANIE: Enkapsulacja - использование property и приватных атрибутов
    """

    # Атрибуты класса
    total_customers = 0
    customers_by_type = {}

    def __init__(self, name: str, phone: str = "", email: str = ""):
        # 🔄 TRANSFER: customer.py → logger (customer creation)
        log_operation("Customer Creation", {"name": name, "type": self.__class__.__name__})

        # Приватные атрибуты для энкапсуляции
        self._name = name
        self._phone = phone
        self._email = email
        self._customer_id = f"CUST{Customer.total_customers + 1:06d}"
        self._registration_date = datetime.now()
        self._order_history: List[str] = []  # Order IDs
        self._total_spent = 0.0
        self._is_active = True
        self._preferences = {}

        # Обновляем счетчики
        Customer.total_customers += 1
        customer_type = self.__class__.__name__
        if customer_type not in Customer.customers_by_type:
            Customer.customers_by_type[customer_type] = 0
        Customer.customers_by_type[customer_type] += 1

        # 📋 CHECK: Klasy - подтверждение создания класса
        log_requirement_check("Class Creation", "SUCCESS", f"Customer: {name}")

    # ✅ WYMAGANIE: Enkapsulacja - Properties with validation
    @property
    def name(self) -> str:
        """Геттер для имени клиента"""
        return self._name

    @name.setter
    def name(self, value: str):
        """
        📋 CHECK: Enkapsulacja - Setter с валидацией имени
        """
        if not value or not value.strip():
            raise ValueError("Customer name cannot be empty")
        old_name = self._name
        self._name = value.strip()
        log_operation("Customer Name Change", {"old": old_name, "new": self._name})

    @property
    def customer_id(self) -> str:
        """Геттер для ID клиента (только чтение)"""
        return self._customer_id

    @property
    def phone(self) -> str:
        """Геттер для телефона"""
        return self._phone

    @phone.setter
    def phone(self, value: str):
        """Сеттер для телефона с валидацией"""
        if value and not self._is_valid_phone(value):
            raise ValueError("Invalid phone number format")
        self._phone = value
        log_operation("Phone Update", {"customer": self.customer_id, "phone": value})

    @property
    def email(self) -> str:
        """Геттер для email"""
        return self._email

    @email.setter
    def email(self, value: str):
        """Сеттер для email с валидацией"""
        if value and not self._is_valid_email(value):
            raise ValueError("Invalid email format")
        self._email = value
        log_operation("Email Update", {"customer": self.customer_id, "email": value})

    @property
    def total_spent(self) -> float:
        """Геттер для общей суммы покупок"""
        return self._total_spent

    @property
    def order_count(self) -> int:
        """Количество заказов"""
        return len(self._order_history)

    @property
    def is_active(self) -> bool:
        """Статус активности клиента"""
        return self._is_active

    @is_active.setter
    def is_active(self, value: bool):
        """Сеттер для статуса активности"""
        self._is_active = bool(value)
        status = "ACTIVE" if value else "INACTIVE"
        log_business_rule("Customer Status", f"{self.name}: {status}")

    # ✅ WYMAGANIE: @staticmethod - Утилитарные методы валидации
    @staticmethod
    def _is_valid_phone(phone: str) -> bool:
        """
        📋 CHECK: @staticmethod - Валидация номера телефона
        """
        # Простая валидация: только цифры, минимум 10 символов
        digits_only = ''.join(filter(str.isdigit, phone))
        return len(digits_only) >= 10

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Валидация email"""
        return "@" in email and "." in email.split("@")[-1]

    @staticmethod
    def generate_customer_id() -> str:
        """Генерирует новый ID клиента"""
        return f"CUST{Customer.total_customers + 1:06d}"

    # ✅ WYMAGANIE: @classmethod - Factory methods
    @classmethod
    def create_walk_in_customer(cls, name: str):
        """
        📋 CHECK: @classmethod - Создание клиента без регистрации
        Factory method для клиента без регистрации
        """
        # 🔄 TRANSFER: Customer.create_walk_in_customer → Customer.__init__
        log_transfer("Customer.create_walk_in_customer", "Customer.__init__", "walk-in customer data")

        customer = cls(name)
        customer._preferences["service_type"] = "walk_in"

        log_requirement_check("@classmethod", "EXECUTED", "Customer.create_walk_in_customer()")
        return customer

    @classmethod
    def get_total_customers(cls) -> int:
        """Возвращает общее количество клиентов"""
        return cls.total_customers

    @classmethod
    def get_customers_by_type(cls) -> Dict[str, int]:
        """Возвращает распределение клиентов по типам"""
        return cls.customers_by_type.copy()

    # Абстрактные методы
    @abstractmethod
    def get_discount_rate(self) -> float:
        """Возвращает процент скидки для клиента"""
        pass

    @abstractmethod
    def get_customer_type(self) -> CustomerType:
        """Возвращает тип клиента"""
        pass

    # Обычные методы
    def add_order(self, order_id: str, amount: float):
        """Добавляет заказ в историю"""
        self._order_history.append(order_id)
        self._total_spent += amount
        log_business_rule("Order Added", f"Customer {self.name}: Order {order_id} for ${amount:.2f}")

    def set_preference(self, key: str, value: Any):
        """Устанавливает предпочтение клиента"""
        self._preferences[key] = value
        log_operation("Preference Set", {"customer": self.customer_id, "preference": key, "value": value})

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Получает предпочтение клиента"""
        return self._preferences.get(key, default)

    def get_order_history(self) -> List[str]:
        """Возвращает копию истории заказов"""
        return self._order_history.copy()

    def __str__(self) -> str:
        return f"{self.name} ({self.customer_id}) - {self.get_customer_type().value}"

    def __repr__(self) -> str:
        return f"Customer(name='{self.name}', id='{self.customer_id}', type={self.get_customer_type().value})"


# ✅ WYMAGANIE: Dziedziczenie - Обычный клиент
class RegularCustomer(Customer):
    """
    📋 CHECK: Dziedziczenie - RegularCustomer наследует от Customer
    Обычный клиент без особых привилегий
    """

    def __init__(self, name: str, phone: str = "", email: str = ""):
        # ✅ WYMAGANIE: super() - вызов конструктора родителя
        super().__init__(name, phone, email)

        # 🔄 TRANSFER: Customer.__init__ → RegularCustomer.__init__
        log_transfer("Customer.__init__", "RegularCustomer.__init__", "regular customer attributes")

        # Специфичные атрибуты обычного клиента
        self._visit_count = 0

        log_requirement_check("Inheritance", "SUCCESS", f"RegularCustomer extends Customer: {name}")

    def get_discount_rate(self) -> float:
        """Обычные клиенты не получают скидку"""
        return 0.0

    def get_customer_type(self) -> CustomerType:
        """Возвращает тип обычного клиента"""
        return CustomerType.REGULAR

    def visit_restaurant(self):
        """Отмечает посещение ресторана"""
        self._visit_count += 1
        log_business_rule("Restaurant Visit", f"Regular customer {self.name}: visit #{self._visit_count}")

    def get_visit_count(self) -> int:
        """Возвращает количество посещений"""
        return self._visit_count


# ✅ WYMAGANIE: Dziedziczenie - Клиент с программой лояльности
class LoyaltyCustomer(Customer):
    """
    📋 CHECK: Dziedziczenie - LoyaltyCustomer наследует от Customer
    Клиент участвующий в программе лояльности McDonald's
    """

    def __init__(self, name: str, phone: str = "", email: str = ""):
        # ✅ WYMAGANIE: super()
        super().__init__(name, phone, email)

        # 🔄 TRANSFER: Customer.__init__ → LoyaltyCustomer.__init__
        log_transfer("Customer.__init__", "LoyaltyCustomer.__init__", "loyalty customer attributes")

        # Атрибуты программы лояльности
        self._loyalty_points = 0
        self._tier = LoyaltyTier.BRONZE
        self._app_registered = True
        self._points_earned_today = 0
        self._points_redeemed_total = 0
        self._tier_benefits_used = 0

        log_requirement_check("Inheritance", "SUCCESS", f"LoyaltyCustomer extends Customer: {name}")

    # ✅ WYMAGANIE: Enkapsulacja - дополнительные properties
    @property
    def loyalty_points(self) -> int:
        """Геттер для баллов лояльности"""
        return self._loyalty_points

    @property
    def tier(self) -> LoyaltyTier:
        """Геттер для уровня лояльности"""
        return self._tier

    def get_discount_rate(self) -> float:
        """Скидка зависит от уровня лояльности"""
        discount_rates = {
            LoyaltyTier.BRONZE: 0.05,  # 5%
            LoyaltyTier.SILVER: 0.08,  # 8%
            LoyaltyTier.GOLD: 0.12,  # 12%
            LoyaltyTier.PLATINUM: 0.15  # 15%
        }
        return discount_rates.get(self._tier, 0.0)

    def get_customer_type(self) -> CustomerType:
        """Возвращает тип клиента программы лояльности"""
        return CustomerType.LOYALTY_MEMBER

    # ✅ WYMAGANIE: @classmethod - специальные конструкторы для лояльности
    @classmethod
    def create_app_signup(cls, name: str, phone: str, email: str):
        """
        📋 CHECK: @classmethod - Регистрация через мобильное приложение
        """
        # 🔄 TRANSFER: LoyaltyCustomer.create_app_signup → LoyaltyCustomer.__init__
        log_transfer("LoyaltyCustomer.create_app_signup", "LoyaltyCustomer.__init__", "app signup data")

        customer = cls(name, phone, email)
        customer._loyalty_points = 100  # Бонус за регистрацию
        customer.set_preference("signup_source", "mobile_app")
        customer.set_preference("notifications", True)

        log_requirement_check("@classmethod", "EXECUTED", "LoyaltyCustomer.create_app_signup()")
        log_business_rule("App Signup", f"{name}: registered with 100 bonus points")

        return customer

    @classmethod
    def migrate_from_regular(cls, regular_customer: RegularCustomer):
        """Переводит обычного клиента в программу лояльности"""
        loyalty_customer = cls(regular_customer.name, regular_customer.phone, regular_customer.email)

        # Переносим историю
        loyalty_customer._order_history = regular_customer._order_history.copy()
        loyalty_customer._total_spent = regular_customer._total_spent

        # Начисляем баллы за прошлые покупки (1 балл за $1)
        retroactive_points = int(regular_customer._total_spent)
        loyalty_customer._loyalty_points = retroactive_points
        loyalty_customer._update_tier()

        log_business_rule("Loyalty Migration",
                          f"{regular_customer.name}: migrated with {retroactive_points} retroactive points")

        return loyalty_customer

    def earn_points(self, amount: float, bonus_multiplier: float = 1.0):
        """Начисляет баллы за покупку"""
        base_points = int(amount)  # 1 балл за $1
        bonus_points = int(base_points * (bonus_multiplier - 1.0))
        total_points = base_points + bonus_points

        self._loyalty_points += total_points
        self._points_earned_today += total_points

        old_tier = self._tier
        self._update_tier()

        log_business_rule("Points Earned",
                          f"{self.name}: +{total_points} points (${amount:.2f} purchase)")

        if old_tier != self._tier:
            log_business_rule("Tier Upgrade", f"{self.name}: {old_tier.value} → {self._tier.value}")

    def redeem_points(self, points: int, item_description: str = "reward"):
        """Тратит баллы на награды"""
        if points > self._loyalty_points:
            raise InsufficientLoyaltyPointsException(points, self._loyalty_points, self.customer_id)

        self._loyalty_points -= points
        self._points_redeemed_total += points

        # Пересчитываем уровень (может понизиться)
        old_tier = self._tier
        self._update_tier()

        log_business_rule("Points Redeemed",
                          f"{self.name}: -{points} points for {item_description}")

        if old_tier != self._tier:
            log_business_rule("Tier Downgrade", f"{self.name}: {old_tier.value} → {self._tier.value}")

    def _update_tier(self):
        """Обновляет уровень лояльности на основе баллов"""
        if self._loyalty_points >= 5000:
            self._tier = LoyaltyTier.PLATINUM
        elif self._loyalty_points >= 2000:
            self._tier = LoyaltyTier.GOLD
        elif self._loyalty_points >= 500:
            self._tier = LoyaltyTier.SILVER
        else:
            self._tier = LoyaltyTier.BRONZE

    def get_tier_benefits(self) -> List[str]:
        """Возвращает список привилегий уровня"""
        benefits = {
            LoyaltyTier.BRONZE: [
                "5% discount on orders",
                "Birthday reward",
                "Exclusive offers"
            ],
            LoyaltyTier.SILVER: [
                "8% discount on orders",
                "Free fries every 10th visit",
                "Priority customer service",
                "Early access to new items"
            ],
            LoyaltyTier.GOLD: [
                "12% discount on orders",
                "Free menu item monthly",
                "Skip the line service",
                "Double points on Fridays"
            ],
            LoyaltyTier.PLATINUM: [
                "15% discount on orders",
                "Free meal quarterly",
                "VIP customer service",
                "Triple points weekends",
                "Exclusive platinum events"
            ]
        }
        return benefits.get(self._tier, [])

    def use_tier_benefit(self, benefit: str):
        """Использует привилегию уровня"""
        available_benefits = self.get_tier_benefits()
        if benefit not in [b.lower() for b in available_benefits]:
            raise ValueError(f"Benefit '{benefit}' not available for {self._tier.value} tier")

        self._tier_benefits_used += 1
        log_business_rule("Benefit Used", f"{self.name} ({self._tier.value}): {benefit}")


# ✅ WYMAGANIE: Dziedziczenie - VIP клиент
class VIPCustomer(LoyaltyCustomer):
    """
    📋 CHECK: Dziedziczenie - VIPCustomer наследует от LoyaltyCustomer (многоуровневое наследование)
    VIP клиент с максимальными привилегиями
    """

    def __init__(self, name: str, phone: str = "", email: str = "",
                 vip_code: str = "", assigned_manager: str = ""):
        # ✅ WYMAGANIE: super() - многоуровневое наследование
        super().__init__(name, phone, email)

        # 🔄 TRANSFER: LoyaltyCustomer.__init__ → VIPCustomer.__init__
        log_transfer("LoyaltyCustomer.__init__", "VIPCustomer.__init__", "VIP customer attributes")

        # VIP атрибуты
        self.vip_code = vip_code
        self.assigned_manager = assigned_manager
        self._vip_since = datetime.now()
        self._concierge_requests = 0
        self._private_events_attended = 0

        # VIP клиенты автоматически получают платиновый статус
        self._tier = LoyaltyTier.PLATINUM
        self._loyalty_points = max(self._loyalty_points, 10000)  # Минимум 10К баллов

        log_requirement_check("Inheritance", "SUCCESS", f"VIPCustomer extends LoyaltyCustomer: {name}")

    def get_discount_rate(self) -> float:
        """VIP клиенты получают максимальную скидку"""
        return 0.20  # 20% скидка

    def get_customer_type(self) -> CustomerType:
        """Возвращает VIP тип клиента"""
        return CustomerType.VIP

    # ✅ WYMAGANIE: @classmethod - VIP конструкторы
    @classmethod
    def create_celebrity_vip(cls, name: str, phone: str, manager: str):
        """
        📋 CHECK: @classmethod - Создание VIP для знаменитостей
        """
        vip_code = f"CELEB{cls.total_customers + 1:04d}"
        vip = cls(name, phone, "", vip_code, manager)
        vip._loyalty_points = 50000  # Много баллов для знаменитостей
        vip.set_preference("privacy_protection", True)
        vip.set_preference("special_requests", True)

        log_requirement_check("@classmethod", "EXECUTED", "VIPCustomer.create_celebrity_vip()")
        return vip

    @classmethod
    def create_corporate_vip(cls, name: str, company: str, email: str):
        """Создает корпоративного VIP"""
        vip_code = f"CORP{cls.total_customers + 1:04d}"
        vip = cls(name, "", email, vip_code)
        vip.set_preference("company", company)
        vip.set_preference("billing", "corporate")
        vip.set_preference("bulk_orders", True)

        return vip

    def request_concierge_service(self, request: str) -> bool:
        """Запрашивает услуги консьержа"""
        self._concierge_requests += 1
        log_business_rule("Concierge Request", f"VIP {self.name}: {request}")

        # VIP всегда получают консьерж сервис
        return True

    def attend_private_event(self, event_name: str):
        """Посещает частное мероприятие"""
        self._private_events_attended += 1
        log_business_rule("Private Event", f"VIP {self.name}: attended {event_name}")

    def get_vip_privileges(self) -> List[str]:
        """Возвращает VIP привилегии"""
        return [
            "20% discount on all orders",
            "Personal manager service",
            "Concierge requests",
            "Private dining reservations",
            "Exclusive menu items",
            "Skip all lines",
            "Free delivery anywhere",
            "Custom order preparations",
            "Private event invitations",
            "Unlimited points earning"
        ]


# ✅ WYMAGANIE: Dziedziczenie - Сотрудник как клиент
class EmployeeCustomer(Customer):
    """
    📋 CHECK: Dziedziczenie - EmployeeCustomer для сотрудников McDonald's
    Сотрудники McDonald's получающие скидки
    """

    def __init__(self, name: str, employee_id: str, department: str, phone: str = ""):
        # ✅ WYMAGANIE: super()
        super().__init__(name, phone)

        # 🔄 TRANSFER: Customer.__init__ → EmployeeCustomer.__init__
        log_transfer("Customer.__init__", "EmployeeCustomer.__init__", "employee customer attributes")

        self.employee_id = employee_id
        self.department = department
        self._employee_discount = 0.50  # 50% скидка для сотрудников
        self._family_discount = 0.25  # 25% скидка для семьи
        self._shift_meal_used = False

        log_requirement_check("Inheritance", "SUCCESS", f"EmployeeCustomer extends Customer: {name}")

    def get_discount_rate(self) -> float:
        """Сотрудники получают большую скидку"""
        return self._employee_discount

    def get_customer_type(self) -> CustomerType:
        """Возвращает тип сотрудника"""
        return CustomerType.EMPLOYEE

    def use_shift_meal(self):
        """Использует бесплатную еду во время смены"""
        if self._shift_meal_used:
            raise ValueError("Shift meal already used today")

        self._shift_meal_used = True
        log_business_rule("Shift Meal", f"Employee {self.name}: used daily shift meal")

    def reset_shift_meal(self):
        """Сбрасывает статус смены (новый день)"""
        self._shift_meal_used = False

    def get_family_discount_rate(self) -> float:
        """Скидка для семьи сотрудника"""
        return self._family_discount


# Функция демонстрации системы клиентов
def demo_customer_system():
    """
    📋 CHECK: Полная демонстрация системы клиентов McDonald's
    """

    print("👥 McDONALD'S CUSTOMER SYSTEM DEMO")
    print("=" * 50)

    # 🔄 TRANSFER: demo → customer classes
    log_transfer("demo_customer_system", "Customer classes", "customer creation")

    # 1. ✅ WYMAGANIE: @classmethod - Factory methods
    print("\n1. FACTORY METHODS (@classmethod)")
    print("-" * 30)

    walk_in = Customer.create_walk_in_customer("John Doe")
    app_signup = LoyaltyCustomer.create_app_signup("Sarah Wilson", "+1234567890", "sarah@email.com")
    celebrity_vip = VIPCustomer.create_celebrity_vip("Famous Actor", "+1987654321", "Manager Smith")

    print(f"Walk-in: {walk_in}")
    print(f"App signup: {app_signup}")
    print(f"Celebrity VIP: {celebrity_vip}")

    # 2. ✅ WYMAGANIE: Dziedziczenie + Nadpisywanie
    print("\n2. INHERITANCE & METHOD OVERRIDING")
    print("-" * 30)

    # Создание разных типов клиентов
    regular = RegularCustomer("Mike Johnson", "+1555123456")
    loyalty = LoyaltyCustomer("Emma Davis", "+1555654321", "emma@email.com")
    vip = VIPCustomer("Robert King", "+1555999888", "robert@vip.com", "VIP001", "Manager Johnson")
    employee = EmployeeCustomer("Alice Staff", "EMP1001", "Kitchen", "+1555111222")

    customers = [regular, loyalty, vip, employee]

    for customer in customers:
        print(f"👤 {customer}")
        print(f"   Discount: {customer.get_discount_rate() * 100:.1f}%")
        print(f"   Type: {customer.get_customer_type().value}")

    # 3. ✅ WYMAGANIE: Enkapsulacja - Property usage
    print("\n3. ENCAPSULATION (Property)")
    print("-" * 30)

    print(f"Loyalty customer points: {loyalty.loyalty_points}")
    loyalty.earn_points(25.99)  # Покупка на $25.99
    print(f"After purchase points: {loyalty.loyalty_points}")

    # Обновляем контактную информацию
    loyalty.email = "new_emma@email.com"
    print(f"Updated email: {loyalty.email}")

    # 4. ✅ WYMAGANIE: Полиморфизм
    print("\n4. POLYMORPHISM")
    print("-" * 30)

    def process_customer_order(customer: Customer, amount: float):
        """Полиморфная функция для обработки заказа"""
        discount = customer.get_discount_rate()
        final_amount = amount * (1 - discount)

        print(f"Customer: {customer.name}")
        print(f"Original: ${amount:.2f}, Discount: {discount * 100:.1f}%, Final: ${final_amount:.2f}")

        customer.add_order(f"ORD{len(customer.get_order_history()) + 1:03d}", final_amount)
        return final_amount

    print("Processing orders for different customer types:")
    order_amount = 15.99
    for customer in [regular, loyalty, vip, employee]:
        final = process_customer_order(customer, order_amount)
        print(f"Saved: ${order_amount - final:.2f}\n")

    # 5. Лояльность и VIP функции
    print("\n5. LOYALTY & VIP FEATURES")
    print("-" * 30)

    # Лояльность
    print("Loyalty Customer Features:")
    print(f"Tier: {loyalty.tier.value}")
    print(f"Benefits: {len(loyalty.get_tier_benefits())} available")

    loyalty.earn_points(50.00, bonus_multiplier=2.0)  # Двойные баллы
    print(f"After bonus earning: {loyalty.loyalty_points} points")

    # VIP
    print(f"\nVIP Customer Features:")
    print(f"VIP Code: {vip.vip_code}")
    print(f"Privileges: {len(vip.get_vip_privileges())} total")

    vip.request_concierge_service("Reserve private dining room")
    vip.attend_private_event("New Menu Tasting")

    # Сотрудник
    print(f"\nEmployee Customer:")
    print(f"Employee ID: {employee.employee_id}")
    print(f"Department: {employee.department}")
    employee.use_shift_meal()

    # 6. Статистика
    print("\n6. CUSTOMER STATISTICS")
    print("-" * 30)
    print(f"Total customers: {Customer.get_total_customers()}")
    print(f"Customers by type: {Customer.get_customers_by_type()}")

    # 📋 CHECK: Финальная проверка
    log_requirement_check("Customer System Demo", "COMPLETED", "customer.py")

    return customers


if __name__ == "__main__":
    demo_customer_system()