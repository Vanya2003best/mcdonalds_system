"""
McDonald's Management System - Custom Exceptions
✅ WYMAGANIE: Utworzenie i użycie swojego wyjątku (własna klasa dziedziąca z Exception)

Все кастомные исключения для системы McDonald's
"""

from typing import Optional, Any
import sys
import os

# Добавляем путь для импорта утилит
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils.logger import log_error, log_requirement_check


# ✅ WYMAGANIE: Dziedziczenie - все исключения наследуются от базового класса
class McDonaldsException(Exception):
    """
    📋 CHECK: Własne wyjątki - базовый класс для всех исключений McDonald's
    Базовое исключение для всей системы McDonald's
    """

    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Any] = None):
        self.message = message
        self.error_code = error_code or "MCDONALDS_ERROR"
        self.details = details
        super().__init__(self.message)

        # 🚨 LOG: Логируем создание исключения
        log_error(f"McDonaldsException created: {self.error_code}", self)

    def __str__(self):
        return f"[{self.error_code}] {self.message}"


# ✅ WYMAGANIE: Dziedziczenie - Menu related exceptions
class MenuException(McDonaldsException):
    """Исключения связанные с меню"""
    pass


class MenuItemNotAvailableException(MenuException):
    """
    📋 CHECK: Własne wyjątki - наследование от McDonaldsException
    Исключение когда позиция меню недоступна
    """

    def __init__(self, item_name: str, reason: str = "Item temporarily unavailable"):
        self.item_name = item_name
        self.reason = reason
        message = f"Menu item '{item_name}' is not available: {reason}"
        super().__init__(message, "MENU_ITEM_UNAVAILABLE", {"item": item_name, "reason": reason})


class InsufficientIngredientsException(MenuException):
    """Исключение при нехватке ингредиентов"""

    def __init__(self, ingredient: str, required: int, available: int):
        self.ingredient = ingredient
        self.required = required
        self.available = available
        message = f"Insufficient {ingredient}: need {required}, have {available}"
        super().__init__(message, "INSUFFICIENT_INGREDIENTS",
                         {"ingredient": ingredient, "required": required, "available": available})


# ✅ WYMAGANIE: Dziedziczenie - Order related exceptions
class OrderException(McDonaldsException):
    """Исключения связанные с заказами"""
    pass


class InvalidOrderException(OrderException):
    """Исключение при некорректном заказе"""

    def __init__(self, order_id: str, reason: str):
        self.order_id = order_id
        self.reason = reason
        message = f"Invalid order {order_id}: {reason}"
        super().__init__(message, "INVALID_ORDER", {"order_id": order_id, "reason": reason})


class OrderTimeoutException(OrderException):
    """Исключение при истечении времени заказа"""

    def __init__(self, order_id: str, timeout_minutes: int):
        self.order_id = order_id
        self.timeout_minutes = timeout_minutes
        message = f"Order {order_id} timed out after {timeout_minutes} minutes"
        super().__init__(message, "ORDER_TIMEOUT", {"order_id": order_id, "timeout": timeout_minutes})


class DriveThruQueueFullException(OrderException):
    """Исключение когда очередь Drive-Thru переполнена"""

    def __init__(self, max_capacity: int):
        self.max_capacity = max_capacity
        message = f"Drive-Thru queue is full (max capacity: {max_capacity})"
        super().__init__(message, "DRIVE_THRU_QUEUE_FULL", {"max_capacity": max_capacity})


# ✅ WYMAGANIE: Dziedziczenie - Payment related exceptions
class PaymentException(McDonaldsException):
    """Исключения связанные с оплатой"""
    pass


class PaymentProcessingException(PaymentException):
    """Исключение при обработке платежа"""

    def __init__(self, payment_method: str, amount: float, reason: str):
        self.payment_method = payment_method
        self.amount = amount
        self.reason = reason
        message = f"Payment failed: {payment_method} for ${amount:.2f} - {reason}"
        super().__init__(message, "PAYMENT_FAILED",
                         {"method": payment_method, "amount": amount, "reason": reason})


class InsufficientFundsException(PaymentException):
    """Исключение при недостатке средств"""

    def __init__(self, required: float, available: float):
        self.required = required
        self.available = available
        message = f"Insufficient funds: need ${required:.2f}, have ${available:.2f}"
        super().__init__(message, "INSUFFICIENT_FUNDS",
                         {"required": required, "available": available})


# ✅ WYMAGANIE: Dziedziczenie - Staff related exceptions
class StaffException(McDonaldsException):
    """Исключения связанные с персоналом"""
    pass


class UnauthorizedAccessException(StaffException):
    """Исключение при неавторизованном доступе"""

    def __init__(self, employee_id: str, action: str, required_level: str):
        self.employee_id = employee_id
        self.action = action
        self.required_level = required_level
        message = f"Employee {employee_id} not authorized for '{action}' (requires {required_level})"
        super().__init__(message, "UNAUTHORIZED_ACCESS",
                         {"employee": employee_id, "action": action, "required": required_level})


class ShiftOverlapException(StaffException):
    """Исключение при пересечении смен"""

    def __init__(self, employee_id: str, shift_time: str):
        self.employee_id = employee_id
        self.shift_time = shift_time
        message = f"Shift overlap detected for employee {employee_id} at {shift_time}"
        super().__init__(message, "SHIFT_OVERLAP", {"employee": employee_id, "time": shift_time})


# ✅ WYMAGANIE: Dziedziczenie - Kitchen related exceptions
class KitchenException(McDonaldsException):
    """Исключения связанные с кухней"""
    pass


class EquipmentFailureException(KitchenException):
    """Исключение при поломке оборудования"""

    def __init__(self, equipment_name: str, failure_type: str):
        self.equipment_name = equipment_name
        self.failure_type = failure_type
        message = f"Equipment failure: {equipment_name} - {failure_type}"
        super().__init__(message, "EQUIPMENT_FAILURE",
                         {"equipment": equipment_name, "failure": failure_type})


class FoodSafetyException(KitchenException):
    """Исключение при нарушении безопасности пищи"""

    def __init__(self, issue: str, severity: str = "HIGH"):
        self.issue = issue
        self.severity = severity
        message = f"Food safety violation ({severity}): {issue}"
        super().__init__(message, "FOOD_SAFETY_VIOLATION", {"issue": issue, "severity": severity})


# McDonald's специфичные исключения
class HappyMealToyOutOfStockException(McDonaldsException):
    """Исключение когда игрушки для Happy Meal закончились"""

    def __init__(self, toy_name: str):
        self.toy_name = toy_name
        message = f"Happy Meal toy '{toy_name}' is out of stock"
        super().__init__(message, "HAPPY_MEAL_TOY_OUT_OF_STOCK", {"toy": toy_name})


class McCafeEquipmentDownException(McDonaldsException):
    """Исключение когда оборудование McCafe не работает"""

    def __init__(self, equipment: str, estimated_fix_time: int):
        self.equipment = equipment
        self.estimated_fix_time = estimated_fix_time
        message = f"McCafe {equipment} is down (estimated fix: {estimated_fix_time} minutes)"
        super().__init__(message, "MCCAFE_EQUIPMENT_DOWN",
                         {"equipment": equipment, "fix_time": estimated_fix_time})


# Функция для демонстрации использования исключений
def test_exceptions():
    """
    📋 CHECK: Własne wyjątki - демонстрация использования всех кастомных исключений
    Тестовая функция для демонстрации всех исключений
    """

    # 🔄 TRANSFER: exceptions → logger (log_requirement_check)
    log_requirement_check("Custom Exceptions", "TESTING", "mcdonalds_exceptions.py")

    print("🧪 Testing McDonald's Custom Exceptions...")

    exceptions_to_test = [
        (MenuItemNotAvailableException, ("Big Mac", "Out of beef patties")),
        (InsufficientIngredientsException, ("cheese", 5, 2)),
        (InvalidOrderException, ("ORD123", "Contains discontinued item")),
        (OrderTimeoutException, ("ORD124", 15)),
        (DriveThruQueueFullException, (10,)),
        (PaymentProcessingException, ("Credit Card", 12.99, "Card declined")),
        (InsufficientFundsException, (15.50, 10.25)),
        (UnauthorizedAccessException, ("EMP001", "modify_prices", "Manager")),
        (ShiftOverlapException, ("EMP002", "14:00-22:00")),
        (EquipmentFailureException, ("Fryer #1", "Temperature sensor malfunction")),
        (FoodSafetyException, ("Temperature too high in fridge #2", "CRITICAL")),
        (HappyMealToyOutOfStockException, ("Pokemon Pikachu",)),
        (McCafeEquipmentDownException, ("Espresso Machine", 30))
    ]

    for exception_class, args in exceptions_to_test:
        try:
            raise exception_class(*args)
        except McDonaldsException as e:
            print(f"✅ {exception_class.__name__}: {e}")
            # 🚨 LOG: Логируем тестирование исключения
            log_requirement_check("Exception Hierarchy", "WORKING",
                                  f"{exception_class.__name__} in mcdonalds_exceptions.py")

    print("\n📋 CHECK: Все кастомные исключения протестированы успешно!")


if __name__ == "__main__":
    test_exceptions()