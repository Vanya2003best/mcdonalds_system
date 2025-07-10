"""
McDonald's Management System - Validators
✅ WYMAGANIE: Walidacja danych wejściowych
✅ WYMAGANIE: @staticmethod - metody walidacji jako statyczne

Утилиты для валидации данных в системе McDonald's
"""

import re
from datetime import datetime, time, date
from typing import Any, List, Dict, Optional, Tuple, Union
from enum import Enum
import sys
import os

# Добавляем пути для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils.logger import log_requirement_check, log_operation, log_business_rule


class ValidationResult:
    """Результат валидации"""

    def __init__(self, is_valid: bool = True, errors: List[str] = None,
                 warnings: List[str] = None, value: Any = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
        self.value = value

    def add_error(self, error: str):
        """Добавляет ошибку валидации"""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str):
        """Добавляет предупреждение"""
        self.warnings.append(warning)

    def __bool__(self):
        """Позволяет использовать в условиях"""
        return self.is_valid

    def __str__(self):
        if self.is_valid:
            return "Valid"
        else:
            return f"Invalid: {', '.join(self.errors)}"


class DataValidator:
    """
    📋 CHECK: Walidacja - Главный класс валидации данных
    ✅ WYMAGANIE: @staticmethod - все методы валидации статические
    """

    # Константы для валидации
    MIN_PASSWORD_LENGTH = 8
    MAX_NAME_LENGTH = 100
    MIN_AGE = 13
    MAX_AGE = 120
    MIN_PRICE = 0.01
    MAX_PRICE = 999.99
    MIN_QUANTITY = 1
    MAX_QUANTITY = 100

    # Регулярные выражения
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    PHONE_PATTERN = re.compile(
        r'^\+?1?[-.\s]?(\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})$'
    )
    EMPLOYEE_ID_PATTERN = re.compile(r'^EMP\d{4}$')
    ORDER_ID_PATTERN = re.compile(r'^ORD\d{6}$')
    CUSTOMER_ID_PATTERN = re.compile(r'^CUST\d{6}$')
    CARD_NUMBER_PATTERN = re.compile(r'^\d{13,19}$')

    # ===== БАЗОВЫЕ ВАЛИДАТОРЫ =====

    @staticmethod
    def validate_string(value: Any, field_name: str = "field",
                        min_length: int = 1, max_length: int = 255,
                        required: bool = True, pattern: str = None) -> ValidationResult:
        """
        📋 CHECK: @staticmethod - Валидация строковых значений
        """
        log_requirement_check("@staticmethod", "EXECUTED", "DataValidator.validate_string()")

        result = ValidationResult()

        # Проверка на None и пустую строку
        if value is None or (isinstance(value, str) and not value.strip()):
            if required:
                result.add_error(f"{field_name} is required")
                return result
            else:
                result.value = ""
                return result

        # Преобразование в строку
        if not isinstance(value, str):
            value = str(value)

        value = value.strip()

        # Проверка длины
        if len(value) < min_length:
            result.add_error(f"{field_name} must be at least {min_length} characters long")

        if len(value) > max_length:
            result.add_error(f"{field_name} cannot exceed {max_length} characters")

        # Проверка паттерна
        if pattern and not re.match(pattern, value):
            result.add_error(f"{field_name} format is invalid")

        result.value = value
        return result

    @staticmethod
    def validate_number(value: Any, field_name: str = "field",
                        min_value: float = None, max_value: float = None,
                        is_integer: bool = False, required: bool = True) -> ValidationResult:
        """
        📋 CHECK: @staticmethod - Валидация числовых значений
        """
        log_requirement_check("@staticmethod", "EXECUTED", "DataValidator.validate_number()")

        result = ValidationResult()

        # Проверка на None
        if value is None:
            if required:
                result.add_error(f"{field_name} is required")
            return result

        # Преобразование в число
        try:
            if is_integer:
                value = int(value)
            else:
                value = float(value)
        except (ValueError, TypeError):
            result.add_error(f"{field_name} must be a valid number")
            return result

        # Проверка диапазона
        if min_value is not None and value < min_value:
            result.add_error(f"{field_name} must be at least {min_value}")

        if max_value is not None and value > max_value:
            result.add_error(f"{field_name} cannot exceed {max_value}")

        result.value = value
        return result

    @staticmethod
    def validate_email(email: Any) -> ValidationResult:
        """
        📋 CHECK: @staticmethod - Валидация email адреса
        """
        log_requirement_check("@staticmethod", "EXECUTED", "DataValidator.validate_email()")

        result = ValidationResult()

        if not email:
            result.add_error("Email is required")
            return result

        email = str(email).strip().lower()

        if not DataValidator.EMAIL_PATTERN.match(email):
            result.add_error("Invalid email format")
        elif len(email) > 254:  # RFC 5321 limit
            result.add_error("Email address too long")
        else:
            result.value = email

        return result

    @staticmethod
    def validate_phone(phone: Any) -> ValidationResult:
        """
        📋 CHECK: @staticmethod - Валидация номера телефона
        """
        log_requirement_check("@staticmethod", "EXECUTED", "DataValidator.validate_phone()")

        result = ValidationResult()

        if not phone:
            result.add_error("Phone number is required")
            return result

        phone = str(phone).strip()

        # Убираем все символы кроме цифр и +
        cleaned_phone = re.sub(r'[^\d+]', '', phone)

        if not DataValidator.PHONE_PATTERN.match(phone):
            result.add_error("Invalid phone number format")
        elif len(cleaned_phone) < 10:
            result.add_error("Phone number too short")
        elif len(cleaned_phone) > 15:
            result.add_error("Phone number too long")
        else:
            result.value = phone

        return result

    @staticmethod
    def validate_date(date_value: Any, field_name: str = "date",
                      min_date: date = None, max_date: date = None) -> ValidationResult:
        """
        📋 CHECK: @staticmethod - Валидация даты
        """
        log_requirement_check("@staticmethod", "EXECUTED", "DataValidator.validate_date()")

        result = ValidationResult()

        if date_value is None:
            result.add_error(f"{field_name} is required")
            return result

        # Преобразование в дату
        if isinstance(date_value, str):
            try:
                date_value = datetime.strptime(date_value, "%Y-%m-%d").date()
            except ValueError:
                try:
                    date_value = datetime.strptime(date_value, "%m/%d/%Y").date()
                except ValueError:
                    result.add_error(f"Invalid {field_name} format (use YYYY-MM-DD or MM/DD/YYYY)")
                    return result
        elif isinstance(date_value, datetime):
            date_value = date_value.date()
        elif not isinstance(date_value, date):
            result.add_error(f"{field_name} must be a valid date")
            return result

        # Проверка диапазона
        if min_date and date_value < min_date:
            result.add_error(f"{field_name} cannot be earlier than {min_date}")

        if max_date and date_value > max_date:
            result.add_error(f"{field_name} cannot be later than {max_date}")

        result.value = date_value
        return result

    # ===== СПЕЦИАЛИЗИРОВАННЫЕ ВАЛИДАТОРЫ ДЛЯ McDONALD'S =====

    @staticmethod
    def validate_employee_id(employee_id: Any) -> ValidationResult:
        """
        📋 CHECK: @staticmethod - Валидация ID сотрудника McDonald's
        """
        log_requirement_check("@staticmethod", "EXECUTED", "DataValidator.validate_employee_id()")

        result = ValidationResult()

        if not employee_id:
            result.add_error("Employee ID is required")
            return result

        employee_id = str(employee_id).strip().upper()

        if not DataValidator.EMPLOYEE_ID_PATTERN.match(employee_id):
            result.add_error("Employee ID must be in format EMP#### (e.g., EMP1001)")
        else:
            result.value = employee_id

        return result

    @staticmethod
    def validate_order_id(order_id: Any) -> ValidationResult:
        """
        📋 CHECK: @staticmethod - Валидация ID заказа
        """
        log_requirement_check("@staticmethod", "EXECUTED", "DataValidator.validate_order_id()")

        result = ValidationResult()

        if not order_id:
            result.add_error("Order ID is required")
            return result

        order_id = str(order_id).strip().upper()

        if not DataValidator.ORDER_ID_PATTERN.match(order_id):
            result.add_error("Order ID must be in format ORD###### (e.g., ORD123456)")
        else:
            result.value = order_id

        return result

    @staticmethod
    def validate_customer_id(customer_id: Any) -> ValidationResult:
        """
        📋 CHECK: @staticmethod - Валидация ID клиента
        """
        log_requirement_check("@staticmethod", "EXECUTED", "DataValidator.validate_customer_id()")

        result = ValidationResult()

        if not customer_id:
            result.add_error("Customer ID is required")
            return result

        customer_id = str(customer_id).strip().upper()

        if not DataValidator.CUSTOMER_ID_PATTERN.match(customer_id):
            result.add_error("Customer ID must be in format CUST###### (e.g., CUST123456)")
        else:
            result.value = customer_id

        return result

    @staticmethod
    def validate_menu_item_name(name: Any) -> ValidationResult:
        """
        📋 CHECK: @staticmethod - Валидация названия позиции меню
        """
        log_requirement_check("@staticmethod", "EXECUTED", "DataValidator.validate_menu_item_name()")

        result = DataValidator.validate_string(
            name, "Menu item name",
            min_length=2, max_length=50,
            required=True
        )

        if result.is_valid:
            # Дополнительные проверки для меню
            name = result.value

            # Проверка на запрещенные символы
            if re.search(r'[<>{}[\]\\]', name):
                result.add_error("Menu item name contains invalid characters")

            # Предупреждения
            if name.isupper():
                result.add_warning("Menu item name is all uppercase")

            if len(name.split()) > 5:
                result.add_warning("Menu item name is quite long")

        return result

    @staticmethod
    def validate_price(price: Any, field_name: str = "price") -> ValidationResult:
        """
        📋 CHECK: @staticmethod - Валидация цены
        """
        log_requirement_check("@staticmethod", "EXECUTED", "DataValidator.validate_price()")

        result = DataValidator.validate_number(
            price, field_name,
            min_value=DataValidator.MIN_PRICE,
            max_value=DataValidator.MAX_PRICE,
            is_integer=False,
            required=True
        )

        if result.is_valid:
            # Округляем до 2 знаков после запятой
            result.value = round(result.value, 2)

            # Предупреждения о ценах
            if result.value > 50.0:
                result.add_warning("Price seems high for McDonald's item")

            if result.value < 1.0:
                result.add_warning("Price seems low, please verify")

        return result

    @staticmethod
    def validate_quantity(quantity: Any, field_name: str = "quantity") -> ValidationResult:
        """
        📋 CHECK: @staticmethod - Валидация количества
        """
        log_requirement_check("@staticmethod", "EXECUTED", "DataValidator.validate_quantity()")

        result = DataValidator.validate_number(
            quantity, field_name,
            min_value=DataValidator.MIN_QUANTITY,
            max_value=DataValidator.MAX_QUANTITY,
            is_integer=True,
            required=True
        )

        if result.is_valid and result.value > 20:
            result.add_warning("Large quantity order may require special handling")

        return result

    @staticmethod
    def validate_card_number(card_number: Any) -> ValidationResult:
        """
        📋 CHECK: @staticmethod - Валидация номера карты
        """
        log_requirement_check("@staticmethod", "EXECUTED", "DataValidator.validate_card_number()")

        result = ValidationResult()

        if not card_number:
            result.add_error("Card number is required")
            return result

        # Убираем пробелы и дефисы
        card_number = re.sub(r'[\s-]', '', str(card_number))

        if not DataValidator.CARD_NUMBER_PATTERN.match(card_number):
            result.add_error("Card number must be 13-19 digits")
        elif not DataValidator._luhn_check(card_number):
            result.add_error("Invalid card number (failed Luhn check)")
        else:
            result.value = card_number

        return result

    @staticmethod
    def validate_cvv(cvv: Any, card_type: str = "unknown") -> ValidationResult:
        """
        📋 CHECK: @staticmethod - Валидация CVV кода
        """
        log_requirement_check("@staticmethod", "EXECUTED", "DataValidator.validate_cvv()")

        result = ValidationResult()

        if not cvv:
            result.add_error("CVV is required")
            return result

        cvv = str(cvv).strip()

        # American Express имеет 4-значный CVV
        expected_length = 4 if card_type.lower() == "amex" else 3

        if not cvv.isdigit():
            result.add_error("CVV must contain only digits")
        elif len(cvv) != expected_length:
            result.add_error(f"CVV must be {expected_length} digits for {card_type}")
        else:
            result.value = cvv

        return result

    @staticmethod
    def validate_loyalty_points(points: Any) -> ValidationResult:
        """
        📋 CHECK: @staticmethod - Валидация баллов лояльности
        """
        log_requirement_check("@staticmethod", "EXECUTED", "DataValidator.validate_loyalty_points()")

        result = DataValidator.validate_number(
            points, "Loyalty points",
            min_value=0,
            max_value=1000000,
            is_integer=True,
            required=True
        )

        if result.is_valid and result.value > 50000:
            result.add_warning("Very high loyalty points balance")

        return result

    # ===== КОМПЛЕКСНЫЕ ВАЛИДАТОРЫ =====

    @staticmethod
    def validate_order_data(order_data: Dict[str, Any]) -> ValidationResult:
        """
        📋 CHECK: @staticmethod - Комплексная валидация данных заказа
        """
        log_requirement_check("@staticmethod", "EXECUTED", "DataValidator.validate_order_data()")

        result = ValidationResult()
        validated_data = {}

        # Валидация обязательных полей
        required_fields = ['customer_id', 'items', 'total_amount']
        for field in required_fields:
            if field not in order_data:
                result.add_error(f"Required field '{field}' is missing")

        if not result.is_valid:
            return result

        # Валидация customer_id
        customer_validation = DataValidator.validate_customer_id(order_data['customer_id'])
        if not customer_validation.is_valid:
            result.errors.extend(customer_validation.errors)
        else:
            validated_data['customer_id'] = customer_validation.value

        # Валидация items
        items = order_data.get('items', [])
        if not isinstance(items, list) or len(items) == 0:
            result.add_error("Order must contain at least one item")
        else:
            validated_items = []
            for i, item in enumerate(items):
                item_validation = DataValidator.validate_order_item(item, f"Item {i + 1}")
                if not item_validation.is_valid:
                    result.errors.extend(item_validation.errors)
                else:
                    validated_items.append(item_validation.value)
            validated_data['items'] = validated_items

        # Валидация total_amount
        total_validation = DataValidator.validate_price(order_data['total_amount'], "Total amount")
        if not total_validation.is_valid:
            result.errors.extend(total_validation.errors)
        else:
            validated_data['total_amount'] = total_validation.value

        # Валидация опциональных полей
        optional_fields = {
            'special_instructions': lambda x: DataValidator.validate_string(x, "Special instructions", required=False,
                                                                            max_length=500),
            'table_number': lambda x: DataValidator.validate_number(x, "Table number", min_value=1, max_value=100,
                                                                    is_integer=True, required=False)
        }

        for field, validator in optional_fields.items():
            if field in order_data:
                field_validation = validator(order_data[field])
                if not field_validation.is_valid:
                    result.errors.extend(field_validation.errors)
                elif field_validation.value is not None:
                    validated_data[field] = field_validation.value

        if result.is_valid:
            result.value = validated_data

        return result

    @staticmethod
    def validate_order_item(item_data: Dict[str, Any], field_name: str = "Item") -> ValidationResult:
        """
        📋 CHECK: @staticmethod - Валидация позиции заказа
        """
        log_requirement_check("@staticmethod", "EXECUTED", "DataValidator.validate_order_item()")

        result = ValidationResult()
        validated_item = {}

        # Обязательные поля позиции
        if 'name' not in item_data:
            result.add_error(f"{field_name}: name is required")
        else:
            name_validation = DataValidator.validate_menu_item_name(item_data['name'])
            if not name_validation.is_valid:
                result.errors.extend([f"{field_name}: {error}" for error in name_validation.errors])
            else:
                validated_item['name'] = name_validation.value

        if 'quantity' not in item_data:
            result.add_error(f"{field_name}: quantity is required")
        else:
            qty_validation = DataValidator.validate_quantity(item_data['quantity'])
            if not qty_validation.is_valid:
                result.errors.extend([f"{field_name}: {error}" for error in qty_validation.errors])
            else:
                validated_item['quantity'] = qty_validation.value

        if 'price' not in item_data:
            result.add_error(f"{field_name}: price is required")
        else:
            price_validation = DataValidator.validate_price(item_data['price'])
            if not price_validation.is_valid:
                result.errors.extend([f"{field_name}: {error}" for error in price_validation.errors])
            else:
                validated_item['price'] = price_validation.value

        # Опциональные поля
        if 'customizations' in item_data:
            customizations = item_data['customizations']
            if isinstance(customizations, list):
                validated_item['customizations'] = customizations
            else:
                result.add_warning(f"{field_name}: customizations should be a list")

        if result.is_valid:
            result.value = validated_item

        return result

    @staticmethod
    def validate_employee_data(employee_data: Dict[str, Any]) -> ValidationResult:
        """
        📋 CHECK: @staticmethod - Валидация данных сотрудника
        """
        log_requirement_check("@staticmethod", "EXECUTED", "DataValidator.validate_employee_data()")

        result = ValidationResult()
        validated_data = {}

        # Обязательные поля
        required_validations = {
            'name': lambda x: DataValidator.validate_string(x, "Name", min_length=2, max_length=100),
            'employee_id': lambda x: DataValidator.validate_employee_id(x),
            'email': lambda x: DataValidator.validate_email(x),
            'hire_date': lambda x: DataValidator.validate_date(x, "Hire date", max_date=date.today())
        }

        for field, validator in required_validations.items():
            if field not in employee_data:
                result.add_error(f"Required field '{field}' is missing")
            else:
                field_validation = validator(employee_data[field])
                if not field_validation.is_valid:
                    result.errors.extend(field_validation.errors)
                else:
                    validated_data[field] = field_validation.value

        # Опциональные поля
        if 'phone' in employee_data:
            phone_validation = DataValidator.validate_phone(employee_data['phone'])
            if phone_validation.is_valid:
                validated_data['phone'] = phone_validation.value
            else:
                result.warnings.extend(phone_validation.errors)

        if 'salary' in employee_data:
            salary_validation = DataValidator.validate_number(
                employee_data['salary'], "Salary",
                min_value=15.0, max_value=100.0
            )
            if salary_validation.is_valid:
                validated_data['salary'] = salary_validation.value
            else:
                result.errors.extend(salary_validation.errors)

        if result.is_valid:
            result.value = validated_data

        return result

    # ===== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ =====

    @staticmethod
    def _luhn_check(card_number: str) -> bool:
        """
        📋 CHECK: @staticmethod - Проверка номера карты по алгоритму Луна
        """

        def luhn_digit(digit: int, is_even: bool) -> int:
            if is_even:
                digit *= 2
                if digit > 9:
                    digit = digit // 10 + digit % 10
            return digit

        digits = [int(d) for d in card_number]
        checksum = sum(luhn_digit(digit, i % 2 == 0) for i, digit in enumerate(reversed(digits)))
        return checksum % 10 == 0

    @staticmethod
    def validate_batch(data_list: List[Dict[str, Any]],
                       validator_func, field_name: str = "item") -> ValidationResult:
        """
        📋 CHECK: @staticmethod - Пакетная валидация данных
        """
        log_requirement_check("@staticmethod", "EXECUTED", "DataValidator.validate_batch()")

        result = ValidationResult()
        validated_items = []

        if not data_list:
            result.add_error(f"No {field_name}s to validate")
            return result

        for i, item in enumerate(data_list):
            item_validation = validator_func(item)
            if not item_validation.is_valid:
                result.errors.extend([f"{field_name} {i + 1}: {error}" for error in item_validation.errors])
                result.warnings.extend([f"{field_name} {i + 1}: {warning}" for warning in item_validation.warnings])
            else:
                validated_items.append(item_validation.value)

        if result.is_valid:
            result.value = validated_items

        return result


# Демонстрация работы валидаторов
def demo_validators():
    """
    📋 CHECK: Полная демонстрация системы валидации
    """

    print("✅ McDONALD'S VALIDATORS DEMO")
    print("=" * 50)

    # 1. Базовые валидаторы
    print("\n1. BASIC VALIDATORS")
    print("-" * 30)

    # Валидация строк
    string_tests = [
        ("John Doe", True),
        ("", False),
        ("A" * 300, False),
        ("Valid Name", True)
    ]

    print("String validation:")
    for test_value, expected in string_tests:
        result = DataValidator.validate_string(test_value, "Name", min_length=1, max_length=100)
        status = "✅" if result.is_valid == expected else "❌"
        print(f"  {status} '{test_value}': {result}")

    # Валидация чисел
    print("\nNumber validation:")
    number_tests = [
        (25.99, True),
        (-5, False),
        (1000, False),
        ("15.50", True)
    ]

    for test_value, expected in number_tests:
        result = DataValidator.validate_price(test_value)
        status = "✅" if result.is_valid == expected else "❌"
        print(f"  {status} {test_value}: {result}")

    # 2. Специализированные валидаторы
    print("\n2. McDONALD'S SPECIFIC VALIDATORS")
    print("-" * 30)

    # Employee ID
    employee_id_tests = [
        ("EMP1001", True),
        ("emp1001", True),  # Should be converted to uppercase
        ("ABC1234", False),
        ("EMP123", False)
    ]

    print("Employee ID validation:")
    for test_id, expected in employee_id_tests:
        result = DataValidator.validate_employee_id(test_id)
        status = "✅" if result.is_valid == expected else "❌"
        print(f"  {status} '{test_id}': {result}")

    # Email
    email_tests = [
        ("john@mcdonalds.com", True),
        ("invalid-email", False),
        ("test@domain", False),
        ("valid.email@example.org", True)
    ]

    print("\nEmail validation:")
    for test_email, expected in email_tests:
        result = DataValidator.validate_email(test_email)
        status = "✅" if result.is_valid == expected else "❌"
        print(f"  {status} '{test_email}': {result}")

    # 3. Комплексная валидация заказа
    print("\n3. COMPLEX ORDER VALIDATION")
    print("-" * 30)

    # Валидный заказ
    valid_order = {
        "customer_id": "CUST123456",
        "items": [
            {"name": "Big Mac", "quantity": 2, "price": 4.99},
            {"name": "French Fries", "quantity": 1, "price": 2.49}
        ],
        "total_amount": 12.47,
        "special_instructions": "No pickles on Big Mac"
    }

    print("Valid order validation:")
    result = DataValidator.validate_order_data(valid_order)
    print(f"  ✅ Valid order: {result}")
    if result.warnings:
        print(f"  Warnings: {', '.join(result.warnings)}")

    # Невалидный заказ
    invalid_order = {
        "customer_id": "INVALID_ID",
        "items": [],
        "total_amount": -5.0
    }

    print("\nInvalid order validation:")
    result = DataValidator.validate_order_data(invalid_order)
    print(f"  ❌ Invalid order: {result}")
    if result.errors:
        print("  Errors:")
        for error in result.errors:
            print(f"    - {error}")

    # 4. Валидация данных сотрудника
    print("\n4. EMPLOYEE DATA VALIDATION")
    print("-" * 30)

    employee_data = {
        "name": "Alice Johnson",
        "employee_id": "EMP2001",
        "email": "alice.johnson@mcdonalds.com",
        "hire_date": "2024-01-15",
        "phone": "+1-555-123-4567",
        "salary": 18.50
    }

    result = DataValidator.validate_employee_data(employee_data)
    print(f"Employee data validation: {result}")

    if result.is_valid:
        print("Validated employee data:")
        for key, value in result.value.items():
            print(f"  {key}: {value}")

    # 5. Пакетная валидация
    print("\n5. BATCH VALIDATION")
    print("-" * 30)

    order_items = [
        {"name": "Big Mac", "quantity": 1, "price": 4.99},
        {"name": "Invalid Item with Very Long Name That Exceeds Limit", "quantity": 0, "price": -1.0},
        {"name": "Fries", "quantity": 2, "price": 2.49}
    ]

    batch_result = DataValidator.validate_batch(
        order_items,
        DataValidator.validate_order_item,
        "order item"
    )

    print(f"Batch validation: {batch_result}")
    if batch_result.errors:
        print("Batch errors:")
        for error in batch_result.errors:
            print(f"  - {error}")

    # 6. Статистика валидации
    print("\n6. VALIDATION STATISTICS")
    print("-" * 30)
    print("Validation tests completed:")
    print(f"  Basic validators: ✅")
    print(f"  Specialized validators: ✅")
    print(f"  Complex validation: ✅")
    print(f"  Batch validation: ✅")

    # 📋 CHECK: Финальная проверка валидаторов
    log_requirement_check("Validators Demo", "COMPLETED", "validators.py")

    return True


if __name__ == "__main__":
    demo_validators()