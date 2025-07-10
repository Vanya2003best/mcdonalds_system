"""
McDonald's Management System - Staff Models
✅ WYMAGANIE: Dziedziczenie, nadpisywanie atrybutów i metod, super(), @classmethod, @staticmethod

Модели персонала McDonald's с полной иерархией и ролями
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta, time
from typing import List, Dict, Optional, Any, Set
from enum import Enum
import sys
import os

# Добавляем пути для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils.logger import log_transfer, log_requirement_check, log_operation, log_business_rule
from src.exceptions.mcdonalds_exceptions import UnauthorizedAccessException, ShiftOverlapException


# Перечисления для ролей и уровней доступа
class StaffRole(Enum):
    CREW_MEMBER = "crew_member"
    CASHIER = "cashier"
    KITCHEN_STAFF = "kitchen_staff"
    DRIVE_THRU = "drive_thru"
    MAINTENANCE = "maintenance"
    SHIFT_MANAGER = "shift_manager"
    ASSISTANT_MANAGER = "assistant_manager"
    GENERAL_MANAGER = "general_manager"
    FRANCHISE_OWNER = "franchise_owner"


class AccessLevel(Enum):
    BASIC = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    MANAGEMENT = 4
    EXECUTIVE = 5


class ShiftType(Enum):
    MORNING = "morning"  # 6:00 - 14:00
    AFTERNOON = "afternoon"  # 14:00 - 22:00
    NIGHT = "night"  # 22:00 - 6:00
    BREAKFAST = "breakfast"  # 5:00 - 11:00


# ✅ WYMAGANIE: Użycie klas - Базовый класс для всего персонала
class Staff(ABC):
    """
    📋 CHECK: Klasy - Абстрактный базовый класс для всего персонала McDonald's
    ✅ WYMAGANIE: Atrybuty w klasach - атрибуты класса, которые будут переопределяться
    """

    # ✅ WYMAGANIE: Atrybuty w klasach - атрибуты класса для переопределения в подклассах
    base_salary = 15.00  # Базовая почасовая ставка в долларах
    department = "general"
    required_access_level = AccessLevel.BASIC
    default_shift_hours = 8

    # Глобальные счетчики
    total_employees = 0
    employees_by_role = {}

    def __init__(self, name: str, employee_id: str, role: StaffRole,
                 hire_date: datetime = None, phone: str = ""):
        # 🔄 TRANSFER: staff.py → logger (employee creation)
        log_operation("Employee Creation", {"name": name, "role": role.value, "id": employee_id})

        # Основные атрибуты
        self.name = name
        self.employee_id = employee_id
        self.role = role
        self.hire_date = hire_date or datetime.now()
        self.phone = phone

        # Рабочие атрибуты
        self._hourly_rate = self.base_salary
        self._access_level = self.required_access_level
        self._is_active = True
        self._total_hours_worked = 0
        self._shift_schedule: List[Dict] = []
        self._performance_rating = 3.0  # 1-5 scale

        # Обновляем счетчики класса
        Staff.total_employees += 1
        if role.value not in Staff.employees_by_role:
            Staff.employees_by_role[role.value] = 0
        Staff.employees_by_role[role.value] += 1

        # 📋 CHECK: Klasy - подтверждение создания класса
        log_requirement_check("Class Creation", "SUCCESS", f"Staff: {name} ({role.value})")

    # ✅ WYMAGANIE: Enkapsulacja - Properties with getters and setters
    @property
    def hourly_rate(self) -> float:
        """Геттер для почасовой ставки"""
        return self._hourly_rate

    @hourly_rate.setter
    def hourly_rate(self, value: float):
        """
        📋 CHECK: Enkapsulacja - Setter с валидацией ставки
        """
        if value < 10.0:  # Минимальная зарплата
            raise ValueError("Hourly rate cannot be below $10.00")
        old_rate = self._hourly_rate
        self._hourly_rate = value
        log_business_rule("Salary Change", f"{self.name}: ${old_rate:.2f} → ${value:.2f}/hour")

    @property
    def access_level(self) -> AccessLevel:
        """Геттер для уровня доступа"""
        return self._access_level

    @access_level.setter
    def access_level(self, level: AccessLevel):
        """Сеттер для уровня доступа с валидацией"""
        if level.value < self.required_access_level.value:
            raise UnauthorizedAccessException(
                self.employee_id,
                f"set_access_level({level.name})",
                self.required_access_level.name
            )
        self._access_level = level
        log_business_rule("Access Level Change", f"{self.name}: {level.name}")

    @property
    def is_active(self) -> bool:
        """Геттер для статуса активности"""
        return self._is_active

    @is_active.setter
    def is_active(self, value: bool):
        """Сеттер для статуса активности"""
        self._is_active = bool(value)
        status = "ACTIVE" if value else "INACTIVE"
        log_business_rule("Employment Status", f"{self.name}: {status}")

    # ✅ WYMAGANIE: Nadpisywanie metod - метод, который будет переопределяться в подклассах
    def work(self) -> str:
        """
        📋 CHECK: Nadpisywanie metod - базовый метод work(), переопределяемый в подклассах
        Базовый метод работы, переопределяется в подклассах
        """
        return f"{self.name} ({self.role.value}) is working at McDonald's"

    # Абстрактный метод, который должен быть реализован в подклассах
    @abstractmethod
    def get_permissions(self) -> List[str]:
        """Возвращает список разрешений для роли"""
        pass

    # ✅ WYMAGANIE: @classmethod - Альтернативные конструкторы
    @classmethod
    def create_new_hire(cls, name: str, employee_id: str, role: StaffRole,
                        start_date: datetime = None):
        """
        📋 CHECK: @classmethod - Factory method для новых сотрудников
        Factory method для создания нового сотрудника
        """
        # 🔄 TRANSFER: staff.py → Staff.__init__ (new hire data)
        log_transfer("Staff.create_new_hire", "Staff.__init__", "new hire data")

        start_date = start_date or datetime.now()
        employee = cls(name, employee_id, role, start_date)

        # Настройка для новичка
        employee._performance_rating = 2.5  # Стартовый рейтинг
        employee.add_training_requirement("Orientation")
        employee.add_training_requirement("Food Safety")

        log_requirement_check("@classmethod", "EXECUTED", "Staff.create_new_hire()")
        log_business_rule("New Hire", f"{name} hired as {role.value}")

        return employee

    @classmethod
    def create_transfer_employee(cls, name: str, employee_id: str, role: StaffRole,
                                 previous_location: str, experience_years: int):
        """Factory method для переведенного сотрудника"""
        employee = cls(name, employee_id, role)

        # Бонус за опыт
        experience_bonus = min(experience_years * 0.50, 5.00)  # Максимум $5 бонуса
        employee._hourly_rate = cls.base_salary + experience_bonus
        employee._performance_rating = min(3.0 + (experience_years * 0.2), 5.0)

        log_business_rule("Transfer Employee",
                          f"{name} transferred from {previous_location} with {experience_years} years experience")

        return employee

    @classmethod
    def get_total_employees(cls) -> int:
        """Возвращает общее количество сотрудников"""
        return cls.total_employees

    @classmethod
    def get_employees_by_role(cls) -> Dict[str, int]:
        """Возвращает распределение сотрудников по ролям"""
        return cls.employees_by_role.copy()

    # ✅ WYMAGANIE: @staticmethod - Утилитарные методы
    @staticmethod
    def calculate_weekly_salary(hourly_rate: float, hours_worked: float,
                                overtime_hours: float = 0) -> float:
        """
        📋 CHECK: @staticmethod - Расчет недельной зарплаты
        Статический метод для расчета недельной зарплаты
        """
        log_requirement_check("@staticmethod", "EXECUTED", "Staff.calculate_weekly_salary()")

        regular_pay = hourly_rate * hours_worked
        overtime_pay = overtime_hours * hourly_rate * 1.5  # Полуторная оплата за сверхурочные
        total = regular_pay + overtime_pay

        # 🚨 LOG: Логируем расчет зарплаты
        log_operation("Salary Calculation", {
            "hourly_rate": hourly_rate,
            "regular_hours": hours_worked,
            "overtime_hours": overtime_hours,
            "regular_pay": regular_pay,
            "overtime_pay": overtime_pay,
            "total": total
        })

        return total

    @staticmethod
    def is_valid_employee_id(employee_id: str) -> bool:
        """Проверяет валидность ID сотрудника (формат: EMP + 4 цифры)"""
        if not employee_id.startswith("EMP") or len(employee_id) != 7:
            return False
        try:
            int(employee_id[3:])  # Проверяем что последние 4 символа - цифры
            return True
        except ValueError:
            return False

    @staticmethod
    def get_shift_times(shift_type: ShiftType) -> tuple:
        """Возвращает время начала и конца смены"""
        shift_times = {
            ShiftType.MORNING: (time(6, 0), time(14, 0)),
            ShiftType.AFTERNOON: (time(14, 0), time(22, 0)),
            ShiftType.NIGHT: (time(22, 0), time(6, 0)),
            ShiftType.BREAKFAST: (time(5, 0), time(11, 0))
        }
        return shift_times.get(shift_type, (time(9, 0), time(17, 0)))

    # Методы для работы с сменами и обучением
    def add_shift(self, date: datetime, shift_type: ShiftType, hours: float):
        """Добавляет смену в расписание"""
        shift = {
            "date": date,
            "shift_type": shift_type,
            "hours": hours,
            "completed": False
        }
        self._shift_schedule.append(shift)
        log_business_rule("Shift Scheduled", f"{self.name}: {shift_type.value} on {date.strftime('%Y-%m-%d')}")

    def complete_shift(self, date: datetime):
        """Отмечает смену как выполненную"""
        for shift in self._shift_schedule:
            if shift["date"].date() == date.date() and not shift["completed"]:
                shift["completed"] = True
                self._total_hours_worked += shift["hours"]
                log_business_rule("Shift Completed", f"{self.name}: +{shift['hours']} hours")
                break

    def add_training_requirement(self, training_name: str):
        """Добавляет требование обучения"""
        if not hasattr(self, '_training_requirements'):
            self._training_requirements = []
        if training_name not in self._training_requirements:
            self._training_requirements.append(training_name)
            log_business_rule("Training Required", f"{self.name}: {training_name}")

    def get_monthly_hours(self) -> float:
        """Возвращает отработанные часы за текущий месяц"""
        current_month = datetime.now().month
        monthly_hours = 0
        for shift in self._shift_schedule:
            if shift["date"].month == current_month and shift["completed"]:
                monthly_hours += shift["hours"]
        return monthly_hours

    def update_performance_rating(self, new_rating: float):
        """Обновляет рейтинг производительности"""
        if not 1.0 <= new_rating <= 5.0:
            raise ValueError("Performance rating must be between 1.0 and 5.0")
        old_rating = self._performance_rating
        self._performance_rating = new_rating
        log_business_rule("Performance Update", f"{self.name}: {old_rating:.1f} → {new_rating:.1f}")

    def __str__(self) -> str:
        return f"{self.name} - {self.role.value} (${self.hourly_rate:.2f}/hr)"

    def __repr__(self) -> str:
        return f"Staff(name='{self.name}', role={self.role.value}, id='{self.employee_id}')"


# ✅ WYMAGANIE: Dziedziczenie - Кассир наследует от Staff
class Cashier(Staff):
    """
    📋 CHECK: Dziedziczenie - Cashier наследует от Staff
    ✅ WYMAGANIE: Nadpisywanie atrybutów - переопределение атрибутов класса
    ✅ WYMAGANIE: super() - использование родительской реализации
    """

    # ✅ WYMAGANIE: Nadpisywanie atrybutów - переопределение атрибутов базового класса
    base_salary = 16.50  # Выше базовой ставки
    department = "front_counter"
    required_access_level = AccessLevel.BASIC
    default_shift_hours = 8

    def __init__(self, name: str, employee_id: str, hire_date: datetime = None,
                 register_number: int = 1, languages: List[str] = None):
        # ✅ WYMAGANIE: super() - вызов конструктора родительского класса
        super().__init__(name, employee_id, StaffRole.CASHIER, hire_date)

        # 🔄 TRANSFER: Staff.__init__ → Cashier.__init__ (cashier specific data)
        log_transfer("Staff.__init__", "Cashier.__init__", "cashier-specific attributes")

        # Специфичные для кассира атрибуты
        self.register_number = register_number
        self.languages = languages or ["English"]
        self._transactions_processed = 0
        self._daily_sales = 0.0
        self._customer_satisfaction = 4.0  # 1-5 scale

        # Обновляем ставку для кассира
        self._hourly_rate = self.base_salary

        # 📋 CHECK: Dziedziczenie - подтверждение наследования
        log_requirement_check("Inheritance", "SUCCESS", f"Cashier extends Staff: {name}")

    # ✅ WYMAGANIE: Nadpisywanie metод - переопределение метода work()
    def work(self) -> str:
        """
        📋 CHECK: Nadpisywanie metод - переопределенный метод work() для кассира
        """
        # ✅ WYMAGANIE: super() - использование реализации родителя + дополнительная логика
        base_work = super().work()
        return f"{base_work} - serving customers at register #{self.register_number}"

    def get_permissions(self) -> List[str]:
        """Разрешения для кассира"""
        return [
            "process_orders",
            "handle_payments",
            "issue_refunds",
            "view_menu",
            "print_receipts",
            "handle_coupons"
        ]

    # Специфичные методы для кассира
    def process_transaction(self, amount: float):
        """Обрабатывает транзакцию"""
        self._transactions_processed += 1
        self._daily_sales += amount
        log_business_rule("Transaction Processed",
                          f"Cashier {self.name}: ${amount:.2f} (Total: {self._transactions_processed})")

    def switch_register(self, new_register: int):
        """Переключает на другую кассу"""
        old_register = self.register_number
        self.register_number = new_register
        log_business_rule("Register Switch", f"{self.name}: Register #{old_register} → #{new_register}")

    def get_daily_performance(self) -> Dict[str, Any]:
        """Возвращает показатели работы за день"""
        return {
            "transactions": self._transactions_processed,
            "sales": self._daily_sales,
            "avg_transaction": self._daily_sales / max(self._transactions_processed, 1),
            "satisfaction": self._customer_satisfaction
        }


# ✅ WYMAGANIE: Dziedziczenie - Кухонный персонал
class KitchenStaff(Staff):
    """
    📋 CHECK: Dziedziczenie - KitchenStaff наследует от Staff
    Кухонный персонал McDonald's
    """

    # ✅ WYMAGANIE: Nadpisywanie atrybutów
    base_salary = 17.00  # Выше из-за навыков
    department = "kitchen"
    required_access_level = AccessLevel.INTERMEDIATE
    default_shift_hours = 8

    def __init__(self, name: str, employee_id: str, station: str = "grill",
                 certifications: List[str] = None, hire_date: datetime = None):
        # ✅ WYMAGANIE: super()
        super().__init__(name, employee_id, StaffRole.KITCHEN_STAFF, hire_date)

        # 🔄 TRANSFER: Staff.__init__ → KitchenStaff.__init__
        log_transfer("Staff.__init__", "KitchenStaff.__init__", "kitchen-specific attributes")

        self.station = station  # grill, fryer, assembly, prep
        self.certifications = certifications or ["Food Safety"]
        self._orders_completed = 0
        self._avg_prep_time = 5.0  # minutes
        self._food_waste_score = 95.0  # percentage (higher is better)

        # Обновляем ставку
        self._hourly_rate = self.base_salary

        log_requirement_check("Inheritance", "SUCCESS", f"KitchenStaff extends Staff: {name}")

    # ✅ WYMAGANIE: Nadpisywanie metод
    def work(self) -> str:
        """Переопределенный метод работы для кухни"""
        base_work = super().work()
        return f"{base_work} - cooking at {self.station} station"

    def get_permissions(self) -> List[str]:
        """Разрешения для кухонного персонала"""
        base_permissions = [
            "access_kitchen",
            "view_orders",
            "mark_orders_complete",
            "access_inventory",
            "use_equipment"
        ]

        # Дополнительные разрешения в зависимости от станции
        if self.station == "grill":
            base_permissions.extend(["operate_grill", "cook_meat"])
        elif self.station == "fryer":
            base_permissions.extend(["operate_fryer", "cook_fries"])
        elif self.station == "assembly":
            base_permissions.extend(["assemble_burgers", "package_orders"])

        return base_permissions

    def complete_order(self, order_id: str, prep_time: float):
        """Завершает приготовление заказа"""
        self._orders_completed += 1

        # Обновляем среднее время приготовления
        self._avg_prep_time = ((self._avg_prep_time * (
                    self._orders_completed - 1)) + prep_time) / self._orders_completed

        log_business_rule("Order Completed",
                          f"Kitchen {self.name}: Order {order_id} in {prep_time:.1f}min")

    def change_station(self, new_station: str):
        """Переводит на другую станцию"""
        valid_stations = ["grill", "fryer", "assembly", "prep", "drive_thru"]
        if new_station not in valid_stations:
            raise ValueError(f"Invalid station: {new_station}")

        old_station = self.station
        self.station = new_station
        log_business_rule("Station Change", f"{self.name}: {old_station} → {new_station}")

    def add_certification(self, certification: str):
        """Добавляет сертификацию"""
        if certification not in self.certifications:
            self.certifications.append(certification)
            # Бонус к зарплате за дополнительные сертификации
            if len(self.certifications) > 2:
                self._hourly_rate += 0.25
            log_business_rule("Certification Added", f"{self.name}: +{certification}")


# ✅ WYMAGANIE: Dziedziczenie - Менеджер смены
class ShiftManager(Staff):
    """
    📋 CHECK: Dziedziczenie - ShiftManager наследует от Staff
    Менеджер смены McDonald's с дополнительными полномочиями
    """

    # ✅ WYMAGANIE: Nadpisywanie atrybutów
    base_salary = 22.00  # Значительно выше
    department = "management"
    required_access_level = AccessLevel.MANAGEMENT
    default_shift_hours = 10  # Более длинные смены

    def __init__(self, name: str, employee_id: str, managed_shifts: List[ShiftType] = None,
                 team_size: int = 15, hire_date: datetime = None):
        # ✅ WYMAGANIE: super()
        super().__init__(name, employee_id, StaffRole.SHIFT_MANAGER, hire_date)

        # 🔄 TRANSFER: Staff.__init__ → ShiftManager.__init__
        log_transfer("Staff.__init__", "ShiftManager.__init__", "manager-specific attributes")

        self.managed_shifts = managed_shifts or [ShiftType.MORNING]
        self.team_size = team_size
        self._managed_employees: List[str] = []  # Employee IDs
        self._shift_performance = {}
        self._can_authorize_refunds = True
        self._can_modify_schedules = True

        # Менеджерская ставка
        self._hourly_rate = self.base_salary
        self._access_level = AccessLevel.MANAGEMENT

        log_requirement_check("Inheritance", "SUCCESS", f"ShiftManager extends Staff: {name}")

    # ✅ WYMAGANIE: Nadpisywanie метод
    def work(self) -> str:
        """Переопределенный метод работы для менеджера"""
        base_work = super().work()
        shifts = ", ".join([shift.value for shift in self.managed_shifts])
        return f"{base_work} - managing {shifts} shifts with {self.team_size} team members"

    def get_permissions(self) -> List[str]:
        """Расширенные разрешения для менеджера"""
        return [
            "manage_staff",
            "authorize_refunds",
            "modify_schedules",
            "access_reports",
            "handle_complaints",
            "authorize_discounts",
            "manage_inventory",
            "open_close_restaurant",
            "handle_emergencies",
            "train_employees"
        ]

    # ✅ WYMAGANIE: Klasa zawierająca więcej niż jeden konstruktor - альтернативные конструкторы
    @classmethod
    def create_night_manager(cls, name: str, employee_id: str):
        """
        📋 CHECK: Wiele konstruktorów - специальный конструктор для ночного менеджера
        Создает менеджера ночной смены с особыми настройками
        """
        # 🔄 TRANSFER: ShiftManager.create_night_manager → ShiftManager.__init__
        log_transfer("ShiftManager.create_night_manager", "ShiftManager.__init__", "night manager data")

        manager = cls(name, employee_id, [ShiftType.NIGHT], team_size=8)
        manager._hourly_rate += 2.00  # Ночная доплата
        manager.add_training_requirement("Night Operations")
        manager.add_training_requirement("Security Procedures")

        log_requirement_check("Multiple Constructors", "EXECUTED", "ShiftManager.create_night_manager()")
        return manager

    @classmethod
    def create_breakfast_manager(cls, name: str, employee_id: str):
        """Создает менеджера утренней/завтрак смены"""
        manager = cls(name, employee_id, [ShiftType.BREAKFAST, ShiftType.MORNING], team_size=12)
        manager.add_training_requirement("Breakfast Menu")
        manager.add_training_requirement("Morning Rush Management")
        return manager

    @classmethod
    def promote_from_cashier(cls, cashier: Cashier):
        """Продвигает кассира до менеджера смены"""
        if cashier._performance_rating < 4.0:
            raise ValueError("Cashier must have performance rating of 4.0+ for promotion")

        manager = cls(cashier.name, cashier.employee_id, team_size=10)
        manager._total_hours_worked = cashier._total_hours_worked
        manager._performance_rating = cashier._performance_rating

        log_business_rule("Promotion", f"{cashier.name}: Cashier → Shift Manager")
        return manager

    # Методы управления
    def add_team_member(self, employee_id: str):
        """Добавляет сотрудника в команду"""
        if employee_id not in self._managed_employees:
            self._managed_employees.append(employee_id)
            log_business_rule("Team Addition", f"Manager {self.name}: +{employee_id}")

    def authorize_refund(self, amount: float, reason: str) -> bool:
        """Авторизует возврат средств"""
        if not self._can_authorize_refunds:
            raise UnauthorizedAccessException(self.employee_id, "authorize_refund", "MANAGEMENT")

        # Лимиты на возврат
        max_refund = 50.00 if amount <= 50.00 else None
        if max_refund and amount > max_refund:
            log_business_rule("Refund Denied", f"Amount ${amount:.2f} exceeds limit ${max_refund:.2f}")
            return False

        log_business_rule("Refund Authorized", f"Manager {self.name}: ${amount:.2f} - {reason}")
        return True

    def evaluate_shift_performance(self, shift_date: datetime, metrics: Dict[str, float]):
        """Оценивает производительность смены"""
        self._shift_performance[shift_date.strftime("%Y-%m-%d")] = metrics

        # Расчет общего скора
        avg_score = sum(metrics.values()) / len(metrics)
        log_business_rule("Shift Evaluation",
                          f"Manager {self.name}: {shift_date.strftime('%Y-%m-%d')} scored {avg_score:.1f}")


# ✅ WYMAGANIE: Dziedziczenie - Генеральный менеджер
class GeneralManager(ShiftManager):
    """
    📋 CHECK: Dziedziczenie - GeneralManager наследует от ShiftManager (многоуровневое наследование)
    Генеральный менеджер McDonald's с максимальными полномочиями
    """

    # ✅ WYMAGANIE: Nadpisywanie atrybutów
    base_salary = 28.00  # Самая высокая ставка
    department = "executive_management"
    required_access_level = AccessLevel.EXECUTIVE
    default_shift_hours = 12  # Самые длинные смены

    def __init__(self, name: str, employee_id: str, region: str = "Metro",
                 restaurants_managed: int = 1, hire_date: datetime = None):
        # ✅ WYMAGANIE: super() - многоуровневое наследование
        super().__init__(name, employee_id, list(ShiftType), team_size=50, hire_date=hire_date)

        # 🔄 TRANSFER: ShiftManager.__init__ → GeneralManager.__init__
        log_transfer("ShiftManager.__init__", "GeneralManager.__init__", "GM-specific attributes")

        self.region = region
        self.restaurants_managed = restaurants_managed
        self._budget_authority = 10000.00  # Максимальная сумма решений
        self._can_hire_fire = True
        self._quarterly_targets = {}

        # Обновляем роль и доступ
        self.role = StaffRole.GENERAL_MANAGER
        self._hourly_rate = self.base_salary
        self._access_level = AccessLevel.EXECUTIVE

        log_requirement_check("Inheritance", "SUCCESS", f"GeneralManager extends ShiftManager: {name}")

    # ✅ WYMAGANIE: Nadpisywanie метод
    def work(self) -> str:
        """Переопределенный метод работы для генерального менеджера"""
        # ✅ WYMAGANIE: super() - использование реализации родителя
        base_work = super().work()
        return f"{base_work} - overseeing {self.restaurants_managed} restaurant(s) in {self.region} region"

    def get_permissions(self) -> List[str]:
        """Максимальные разрешения для генерального менеджера"""
        # Получаем базовые разрешения менеджера смены
        base_permissions = super().get_permissions()

        # Добавляем специальные разрешения GM
        gm_permissions = [
            "hire_employees",
            "terminate_employees",
            "set_salaries",
            "approve_budgets",
            "access_financials",
            "modify_menu_prices",
            "authorize_large_refunds",
            "manage_suppliers",
            "plan_promotions",
            "access_corporate_data"
        ]

        return base_permissions + gm_permissions

    # Специальные методы для GM
    def hire_employee(self, staff: Staff) -> bool:
        """Нанимает нового сотрудника"""
        if not self._can_hire_fire:
            raise UnauthorizedAccessException(self.employee_id, "hire_employee", "EXECUTIVE")

        log_business_rule("Employee Hired", f"GM {self.name}: hired {staff.name} as {staff.role.value}")
        return True

    def set_quarterly_target(self, metric: str, target: float):
        """Устанавливает квартальные цели"""
        self._quarterly_targets[metric] = target
        log_business_rule("Quarterly Target", f"GM {self.name}: {metric} = {target}")

    def approve_budget(self, amount: float, category: str) -> bool:
        """Утверждает бюджет"""
        if amount > self._budget_authority:
            log_business_rule("Budget Denied", f"Amount ${amount:.2f} exceeds authority ${self._budget_authority:.2f}")
            return False

        log_business_rule("Budget Approved", f"GM {self.name}: ${amount:.2f} for {category}")
        return True


# Функция демонстрации системы персонала
def demo_staff_system():
    """
    📋 CHECK: Полная демонстрация системы персонала McDonald's
    Демонстрация всех классов персонала и их возможностей
    """

    print("👥 McDONALD'S STAFF SYSTEM DEMO")
    print("=" * 50)

    # 🔄 TRANSFER: demo → staff classes (создание объектов)
    log_transfer("demo_staff_system", "Staff classes", "employee creation")

    # 1. ✅ WYMAGANIE: @classmethod - Factory methods
    print("\n1. FACTORY METHODS (@classmethod)")
    print("-" * 30)

    new_cashier = Staff.create_new_hire("Alice Johnson", "EMP1001", StaffRole.CASHIER)
    transfer_cook = Staff.create_transfer_employee("Carlos Rodriguez", "EMP1002",
                                                   StaffRole.KITCHEN_STAFF, "Downtown Location", 3)

    print(f"New hire: {new_cashier}")
    print(f"Transfer: {transfer_cook}")

    # 2. ✅ WYMAGANIE: Dziedziczenie + Nadpisywanie
    print("\n2. INHERITANCE & METHOD OVERRIDING")
    print("-" * 30)

    # Создание персонала разных уровней
    cashier = Cashier("Emma Davis", "EMP1003", register_number=2, languages=["English", "Spanish"])
    kitchen_staff = KitchenStaff("Mike Wilson", "EMP1004", station="grill",
                                 certifications=["Food Safety", "Grill Master"])
    night_manager = ShiftManager.create_night_manager("Sarah Kim", "EMP1005")
    gm = GeneralManager("Robert Chen", "EMP1006", region="North Metro", restaurants_managed=3)

    staff_members = [cashier, kitchen_staff, night_manager, gm]

    for staff in staff_members:
        print(f"👤 {staff.work()}")
        print(f"   Salary: ${staff.hourly_rate:.2f}/hour")
        print(f"   Access Level: {staff.access_level.name}")
        print(f"   Permissions: {len(staff.get_permissions())} total")

    # 3. ✅ WYMAGANIE: @staticmethod
    print("\n3. STATIC METHODS (@staticmethod)")
    print("-" * 30)

    weekly_salary = Staff.calculate_weekly_salary(16.50, 40, 5)  # 40 regular + 5 overtime
    print(f"Weekly salary example: ${weekly_salary:.2f}")

    print(f"Valid ID 'EMP1234': {Staff.is_valid_employee_id('EMP1234')}")
    print(f"Invalid ID 'ABC123': {Staff.is_valid_employee_id('ABC123')}")

    morning_times = Staff.get_shift_times(ShiftType.MORNING)
    print(f"Morning shift: {morning_times[0]} - {morning_times[1]}")

    # 4. ✅ WYMAGANIE: Enkapsulacja - Property usage
    print("\n4. ENCAPSULATION (Property)")
    print("-" * 30)

    print(f"Cashier original rate: ${cashier.hourly_rate:.2f}")
    cashier.hourly_rate = 17.50  # Используем setter
    print(f"Cashier new rate: ${cashier.hourly_rate:.2f}")

    cashier.access_level = AccessLevel.INTERMEDIATE  # Повышение уровня доступа
    print(f"Cashier access level: {cashier.access_level.name}")

    # 5. ✅ WYMAGANIE: Polimorfizm - одна функция, разные типы
    print("\n5. POLYMORPHISM")
    print("-" * 30)

    def show_employee_info(employee: Staff):
        """Полиморфная функция - работает со всеми типами сотрудников"""
        print(f"Employee: {employee.name}")
        print(f"Work description: {employee.work()}")
        print(f"Permissions count: {len(employee.get_permissions())}")
        print()

    print("Polymorphic function working with different employee types:")
    for staff in [cashier, kitchen_staff, night_manager, gm]:
        show_employee_info(staff)

    # 6. Операции с персоналом
    print("\n6. STAFF OPERATIONS")
    print("-" * 30)

    # Кассир обрабатывает транзакции
    cashier.process_transaction(25.99)
    cashier.process_transaction(18.50)

    # Кухонный персонал завершает заказы
    kitchen_staff.complete_order("ORD123", 4.5)
    kitchen_staff.add_certification("Advanced Grill")

    # Менеджер авторизует возврат
    refund_approved = night_manager.authorize_refund(15.00, "Wrong order")
    print(f"Refund authorized: {refund_approved}")

    # GM утверждает бюджет
    budget_approved = gm.approve_budget(5000.00, "Equipment upgrade")
    print(f"Budget approved: {budget_approved}")

    # 7. Статистика
    print("\n7. STAFF STATISTICS")
    print("-" * 30)
    print(f"Total employees: {Staff.get_total_employees()}")
    print(f"Employees by role: {Staff.get_employees_by_role()}")

    # Производительность кассира
    performance = cashier.get_daily_performance()
    print(f"Cashier performance: {performance}")

    # 📋 CHECK: Финальная проверка всех требований
    log_requirement_check("Staff System Demo", "COMPLETED", "staff.py")

    return staff_members


if __name__ == "__main__":
    demo_staff_system()