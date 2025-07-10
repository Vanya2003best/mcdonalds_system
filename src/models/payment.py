"""
McDonald's Management System - Payment Models
✅ WYMAGANIE: Polimorfizm - różne metody płatności z tym samym interfejsem
✅ WYMAGANIE: Dziedziczenie, nadpisywanie metод, enkapsulacja, @classmethod, @staticmethod

Модели платежных систем McDonald's с полиморфизмом
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union
from enum import Enum
import sys
import os
import random
import string

# Добавляем пути для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils.logger import log_transfer, log_requirement_check, log_operation, log_business_rule
from src.exceptions.mcdonalds_exceptions import (
    PaymentProcessingException, InsufficientFundsException, McDonaldsException
)


class PaymentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethod(Enum):
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    MOBILE_PAY = "mobile_pay"
    GIFT_CARD = "gift_card"
    LOYALTY_POINTS = "loyalty_points"
    CONTACTLESS = "contactless"
    SPLIT_PAYMENT = "split_payment"


class CurrencyType(Enum):
    USD = "USD"
    EUR = "EUR"
    PLN = "PLN"
    CAD = "CAD"


class PaymentException(McDonaldsException):
    """Базовое исключение для платежей"""
    pass


class CardDeclinedException(PaymentException):
    """Исключение при отклонении карты"""

    def __init__(self, card_last_four: str, reason: str):
        self.card_last_four = card_last_four
        self.reason = reason
        message = f"Card ending in {card_last_four} declined: {reason}"
        super().__init__(message, "CARD_DECLINED", {"card": card_last_four, "reason": reason})


class InsufficientGiftCardBalanceException(PaymentException):
    """Исключение при недостатке средств на подарочной карте"""

    def __init__(self, required: float, available: float, card_number: str):
        self.required = required
        self.available = available
        self.card_number = card_number
        message = f"Gift card {card_number}: need ${required:.2f}, have ${available:.2f}"
        super().__init__(message, "INSUFFICIENT_GIFT_CARD_BALANCE",
                         {"required": required, "available": available, "card": card_number})


# ✅ WYMAGANIE: Użycie klas + Polimorfizm - Базовый абстрактный класс для всех платежей
class Payment(ABC):
    """
    📋 CHECK: Polimorfizm - Абстрактный базовый класс для всех методов оплаты
    ✅ WYMAGANIE: Polimorfizm - одинаковый интерфейс для разных типов платежей
    """

    # Атрибуты класса
    total_payments_processed = 0
    total_amount_processed = 0.0
    payments_by_method = {}
    daily_transaction_limit = 10000.0

    def __init__(self, amount: float, currency: CurrencyType = CurrencyType.USD,
                 order_id: str = "", description: str = ""):
        # 🔄 TRANSFER: payment.py → logger (payment creation)
        log_operation("Payment Creation", {
            "amount": amount,
            "currency": currency.value,
            "method": self.__class__.__name__
        })

        # Валидация суммы
        if amount <= 0:
            raise ValueError("Payment amount must be positive")

        # Приватные атрибуты для энкапсуляции
        self._amount = amount
        self._currency = currency
        self._order_id = order_id
        self._description = description
        self._payment_id = self._generate_payment_id()
        self._status = PaymentStatus.PENDING
        self._created_at = datetime.now()
        self._processed_at: Optional[datetime] = None
        self._transaction_fee = 0.0
        self._exchange_rate = 1.0
        self._refund_amount = 0.0
        self._metadata: Dict[str, Any] = {}

        # Обновляем счетчики класса
        Payment.total_payments_processed += 1
        Payment.total_amount_processed += amount

        payment_method = self.__class__.__name__
        if payment_method not in Payment.payments_by_method:
            Payment.payments_by_method[payment_method] = 0
        Payment.payments_by_method[payment_method] += 1

        # 📋 CHECK: Klasy - подтверждение создания класса
        log_requirement_check("Class Creation", "SUCCESS", f"Payment: {self._payment_id}")

    # ✅ WYMAGANIE: Enkapsulacja - Properties
    @property
    def payment_id(self) -> str:
        """Геттер для ID платежа (только чтение)"""
        return self._payment_id

    @property
    def amount(self) -> float:
        """Геттер для суммы платежа"""
        return self._amount

    @property
    def currency(self) -> CurrencyType:
        """Геттер для валюты"""
        return self._currency

    @property
    def status(self) -> PaymentStatus:
        """Геттер для статуса платежа"""
        return self._status

    @status.setter
    def status(self, value: PaymentStatus):
        """
        📋 CHECK: Enkapsulacja - Setter со статус-логикой
        """
        if not isinstance(value, PaymentStatus):
            raise ValueError("Status must be PaymentStatus enum")

        old_status = self._status
        self._status = value

        # Особая логика для изменения статуса
        if value in [PaymentStatus.COMPLETED, PaymentStatus.CAPTURED]:
            self._processed_at = datetime.now()

        log_business_rule("Payment Status Change",
                          f"Payment {self.payment_id}: {old_status.value} → {value.value}")

    @property
    def order_id(self) -> str:
        """Геттер для ID заказа"""
        return self._order_id

    @property
    def transaction_fee(self) -> float:
        """Геттер для комиссии"""
        return self._transaction_fee

    @property
    def net_amount(self) -> float:
        """Чистая сумма после комиссии"""
        return self._amount - self._transaction_fee

    # ✅ WYMAGANIE: @staticmethod - Утилитарные методы
    @staticmethod
    def _generate_payment_id() -> str:
        """
        📋 CHECK: @staticmethod - Генерация ID платежа
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        payment_id = f"PAY{timestamp}{random_suffix}"

        log_requirement_check("@staticmethod", "EXECUTED", "Payment._generate_payment_id()")
        return payment_id

    @staticmethod
    def validate_amount(amount: float, min_amount: float = 0.01, max_amount: float = 9999.99) -> bool:
        """Валидирует сумму платежа"""
        return min_amount <= amount <= max_amount

    @staticmethod
    def convert_currency(amount: float, from_currency: CurrencyType,
                         to_currency: CurrencyType) -> float:
        """Конвертирует валюту (упрощенная версия)"""
        # Упрощенные курсы валют
        rates = {
            (CurrencyType.USD, CurrencyType.EUR): 0.85,
            (CurrencyType.USD, CurrencyType.PLN): 3.90,
            (CurrencyType.USD, CurrencyType.CAD): 1.25,
            (CurrencyType.EUR, CurrencyType.USD): 1.18,
            (CurrencyType.PLN, CurrencyType.USD): 0.26,
            (CurrencyType.CAD, CurrencyType.USD): 0.80
        }

        if from_currency == to_currency:
            return amount

        rate = rates.get((from_currency, to_currency), 1.0)
        converted = amount * rate

        log_operation("Currency Conversion", {
            "amount": amount,
            "from": from_currency.value,
            "to": to_currency.value,
            "rate": rate,
            "result": converted
        })

        return round(converted, 2)

    @staticmethod
    def calculate_processing_fee(amount: float, fee_percentage: float = 0.029) -> float:
        """Рассчитывает комиссию за обработку"""
        return round(amount * fee_percentage, 2)

    # ✅ WYMAGANIE: @classmethod - Factory methods
    @classmethod
    def get_total_processed(cls) -> Dict[str, Union[int, float]]:
        """
        📋 CHECK: @classmethod - Статистика обработанных платежей
        """
        log_requirement_check("@classmethod", "EXECUTED", "Payment.get_total_processed()")
        return {
            "count": cls.total_payments_processed,
            "total_amount": cls.total_amount_processed,
            "by_method": cls.payments_by_method.copy()
        }

    @classmethod
    def create_refund_payment(cls, original_payment: 'Payment', refund_amount: float, reason: str):
        """Создает возвратный платеж"""
        if refund_amount > original_payment.amount:
            raise ValueError("Refund amount cannot exceed original payment")

        # Создаем возвратный платеж
        refund = cls(refund_amount, original_payment.currency, original_payment.order_id,
                     f"Refund: {reason}")
        refund._status = PaymentStatus.REFUNDED
        refund._metadata["original_payment_id"] = original_payment.payment_id
        refund._metadata["refund_reason"] = reason

        return refund

    # ✅ WYMAGANIE: Polimorfizm - Абстрактные методы с одинаковым интерфейсом
    @abstractmethod
    def process_payment(self) -> bool:
        """
        📋 CHECK: Polimorfizm - Основной полиморфный метод обработки платежа
        Обрабатывает платеж. Каждый подкласс реализует по-своему
        """
        pass

    @abstractmethod
    def get_payment_method(self) -> PaymentMethod:
        """Возвращает метод платежа"""
        pass

    @abstractmethod
    def validate_payment_data(self) -> bool:
        """Валидирует данные платежа"""
        pass

    @abstractmethod
    def calculate_fees(self) -> float:
        """Рассчитывает комиссии за платеж"""
        pass

    # Общие методы
    def add_metadata(self, key: str, value: Any):
        """Добавляет метаданные к платежу"""
        self._metadata[key] = value
        log_operation("Metadata Added", {"payment": self.payment_id, "key": key})

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Получает метаданные"""
        return self._metadata.get(key, default)

    def cancel_payment(self, reason: str = "Customer request"):
        """Отменяет платеж"""
        if self._status in [PaymentStatus.COMPLETED, PaymentStatus.CAPTURED]:
            raise PaymentProcessingException(self.get_payment_method().value, self.amount,
                                             "Cannot cancel completed payment")

        self._status = PaymentStatus.CANCELLED
        self._metadata["cancellation_reason"] = reason
        log_business_rule("Payment Cancelled", f"{self.payment_id}: {reason}")

    def get_payment_summary(self) -> Dict[str, Any]:
        """Возвращает сводку платежа"""
        return {
            "payment_id": self.payment_id,
            "method": self.get_payment_method().value,
            "amount": self.amount,
            "currency": self.currency.value,
            "status": self.status.value,
            "transaction_fee": self.transaction_fee,
            "net_amount": self.net_amount,
            "order_id": self.order_id,
            "created_at": self._created_at.isoformat(),
            "processed_at": self._processed_at.isoformat() if self._processed_at else None
        }

    def __str__(self) -> str:
        return f"Payment {self.payment_id} - {self.get_payment_method().value} - ${self.amount:.2f}"

    def __repr__(self) -> str:
        return f"Payment(id='{self.payment_id}', method={self.get_payment_method().value}, amount=${self.amount:.2f})"


# ✅ WYMAGANIE: Dziedziczenie + Polimorfizm - Оплата наличными
class CashPayment(Payment):
    """
    📋 CHECK: Dziedziczenie - CashPayment наследует от Payment
    📋 CHECK: Polimorfizm - Реализует process_payment() по-своему
    Оплата наличными деньгами
    """

    def __init__(self, amount: float, cash_tendered: float, currency: CurrencyType = CurrencyType.USD,
                 order_id: str = "", description: str = ""):
        # ✅ WYMAGANIE: super() - вызов конструктора родителя
        super().__init__(amount, currency, order_id, description)

        # 🔄 TRANSFER: Payment.__init__ → CashPayment.__init__
        log_transfer("Payment.__init__", "CashPayment.__init__", "cash specific attributes")

        # Специфичные для наличных атрибуты
        self.cash_tendered = cash_tendered
        self._change_amount = max(0, cash_tendered - amount)
        self._cashier_id: Optional[str] = None
        self._register_number: Optional[int] = None

        # Валидация
        if cash_tendered < amount:
            raise InsufficientFundsException(amount, cash_tendered)

        log_requirement_check("Inheritance", "SUCCESS", f"CashPayment extends Payment: {self.payment_id}")

    # ✅ WYMAGANIE: Polimorfizm - Реализация абстрактного метода
    def process_payment(self) -> bool:
        """
        📋 CHECK: Polimorfizm - Уникальная реализация для наличных
        """
        try:
            # Валидируем данные
            if not self.validate_payment_data():
                raise PaymentProcessingException("cash", self.amount, "Invalid payment data")

            # Обрабатываем наличные
            self.status = PaymentStatus.PROCESSING

            # Рассчитываем комиссии (для наличных нет)
            self._transaction_fee = self.calculate_fees()

            # Симулируем обработку
            log_business_rule("Cash Processing",
                              f"Tendered: ${self.cash_tendered:.2f}, Change: ${self._change_amount:.2f}")

            # Завершаем платеж
            self.status = PaymentStatus.COMPLETED

            log_business_rule("Payment Processed", f"Cash payment {self.payment_id} completed")
            return True

        except Exception as e:
            self.status = PaymentStatus.FAILED
            log_business_rule("Payment Failed", f"Cash payment {self.payment_id}: {str(e)}")
            raise PaymentProcessingException("cash", self.amount, str(e))

    def get_payment_method(self) -> PaymentMethod:
        """Возвращает метод оплаты наличными"""
        return PaymentMethod.CASH

    def validate_payment_data(self) -> bool:
        """Валидирует данные наличной оплаты"""
        if self.cash_tendered < self.amount:
            return False
        if self.amount <= 0:
            return False
        return True

    def calculate_fees(self) -> float:
        """Для наличных нет комиссий"""
        return 0.0

    # ✅ WYMAGANIE: Wiele konstruktorów - альтернативные конструкторы
    @classmethod
    def create_exact_change(cls, amount: float, currency: CurrencyType = CurrencyType.USD):
        """
        📋 CHECK: Wiele konstruktorów - точная сумма без сдачи
        """
        payment = cls(amount, amount, currency, "", "Exact change payment")
        log_requirement_check("Multiple Constructors", "EXECUTED", "CashPayment.create_exact_change()")
        return payment

    @classmethod
    def create_large_bill_payment(cls, amount: float, bill_denomination: int):
        """Создает платеж крупной купюрой"""
        if bill_denomination < amount:
            raise ValueError("Bill denomination must be larger than amount")

        payment = cls(amount, bill_denomination, CurrencyType.USD, "",
                      f"Payment with ${bill_denomination} bill")
        return payment

    def assign_cashier(self, cashier_id: str, register_number: int):
        """Назначает кассира и кассу"""
        self._cashier_id = cashier_id
        self._register_number = register_number
        self.add_metadata("cashier_id", cashier_id)
        self.add_metadata("register", register_number)
        log_business_rule("Cashier Assigned",
                          f"Cash payment {self.payment_id}: {cashier_id} at register {register_number}")

    @property
    def change_amount(self) -> float:
        """Сумма сдачи"""
        return self._change_amount


# ✅ WYMAGANIE: Dziedziczenie + Polimorfizm - Банковская карта
class CardPayment(Payment):
    """
    📋 CHECK: Dziedziczenie - CardPayment наследует от Payment
    📋 CHECK: Polimorfizm - Своя реализация process_payment()
    Оплата банковской картой (кредитной или дебетовой)
    """

    def __init__(self, amount: float, card_number: str, cardholder_name: str,
                 expiry_month: int, expiry_year: int, cvv: str,
                 currency: CurrencyType = CurrencyType.USD, order_id: str = ""):
        # ✅ WYMAGANIE: super()
        super().__init__(amount, currency, order_id, "Card payment")

        # 🔄 TRANSFER: Payment.__init__ → CardPayment.__init__
        log_transfer("Payment.__init__", "CardPayment.__init__", "card specific attributes")

        # Специфичные для карт атрибуты
        self._card_number = card_number  # Будем хранить только последние 4 цифры
        self.cardholder_name = cardholder_name
        self.expiry_month = expiry_month
        self.expiry_year = expiry_year
        self._cvv = cvv  # Приватный CVV
        self._card_type = self._detect_card_type(card_number)
        self._authorization_code: Optional[str] = None
        self._merchant_id = "MCDONALDS_001"

        # Маскируем номер карты
        self._masked_card_number = self._mask_card_number(card_number)

        log_requirement_check("Inheritance", "SUCCESS", f"CardPayment extends Payment: {self.payment_id}")

    # ✅ WYMAGANIE: Polimorfizm - Уникальная реализация для карт
    def process_payment(self) -> bool:
        """
        📋 CHECK: Polimorfizm - Обработка карточного платежа
        """
        try:
            # Валидируем данные карты
            if not self.validate_payment_data():
                raise CardDeclinedException(self._get_last_four(), "Invalid card data")

            self.status = PaymentStatus.PROCESSING

            # Симулируем авторизацию
            self._authorization_code = self._simulate_authorization()
            if not self._authorization_code:
                raise CardDeclinedException(self._get_last_four(), "Authorization failed")

            self.status = PaymentStatus.AUTHORIZED

            # Рассчитываем комиссии
            self._transaction_fee = self.calculate_fees()

            # Симулируем захват средств
            if self._simulate_capture():
                self.status = PaymentStatus.COMPLETED
                log_business_rule("Card Payment Processed",
                                  f"Card ending in {self._get_last_four()}: ${self.amount:.2f}")
                return True
            else:
                raise PaymentProcessingException("card", self.amount, "Capture failed")

        except (CardDeclinedException, PaymentProcessingException):
            self.status = PaymentStatus.FAILED
            raise
        except Exception as e:
            self.status = PaymentStatus.FAILED
            raise PaymentProcessingException("card", self.amount, str(e))

    def get_payment_method(self) -> PaymentMethod:
        """Возвращает метод карточной оплаты"""
        return PaymentMethod.CREDIT_CARD if self._card_type in ["visa", "mastercard",
                                                                "amex"] else PaymentMethod.DEBIT_CARD

    def validate_payment_data(self) -> bool:
        """Валидирует данные карты"""
        # Проверяем длину номера карты
        if len(self._card_number.replace(" ", "")) < 13:
            return False

        # Проверяем срок действия
        now = datetime.now()
        if self.expiry_year < now.year or (self.expiry_year == now.year and self.expiry_month < now.month):
            return False

        # Проверяем CVV
        if len(self._cvv) < 3:
            return False

        return True

    def calculate_fees(self) -> float:
        """Рассчитывает комиссии для карт"""
        # Разные ставки для разных типов карт
        fee_rates = {
            "visa": 0.029,  # 2.9%
            "mastercard": 0.029,  # 2.9%
            "amex": 0.035,  # 3.5%
            "discover": 0.032,  # 3.2%
            "unknown": 0.030  # 3.0%
        }

        rate = fee_rates.get(self._card_type, 0.030)
        return round(self.amount * rate, 2)

    # ✅ WYMAGANIE: @staticmethod - Утилитарные методы для карт
    @staticmethod
    def _detect_card_type(card_number: str) -> str:
        """
        📋 CHECK: @staticmethod - Определение типа карты
        """
        cleaned = card_number.replace(" ", "").replace("-", "")

        if cleaned.startswith("4"):
            return "visa"
        elif cleaned.startswith(("51", "52", "53", "54", "55")) or cleaned.startswith("22"):
            return "mastercard"
        elif cleaned.startswith(("34", "37")):
            return "amex"
        elif cleaned.startswith("6011") or cleaned.startswith("65"):
            return "discover"
        else:
            return "unknown"

    @staticmethod
    def _mask_card_number(card_number: str) -> str:
        """Маскирует номер карты"""
        cleaned = card_number.replace(" ", "").replace("-", "")
        if len(cleaned) >= 4:
            return f"****-****-****-{cleaned[-4:]}"
        return "****-****-****-****"

    # ✅ WYMAGANIE: Wiele konstruktorów
    @classmethod
    def create_contactless_payment(cls, amount: float, card_token: str, currency: CurrencyType = CurrencyType.USD):
        """
        📋 CHECK: Wiele konstruktorów - бесконтактная оплата
        """
        # Создаем упрощенный платеж для бесконтактной оплаты
        payment = cls(amount, "****-****-****-0000", "CONTACTLESS", 12, 2025, "000", currency)
        payment.add_metadata("payment_type", "contactless")
        payment.add_metadata("card_token", card_token)

        log_requirement_check("Multiple Constructors", "EXECUTED", "CardPayment.create_contactless_payment()")
        return payment

    @classmethod
    def create_recurring_payment(cls, amount: float, saved_card_id: str):
        """Создает повторяющийся платеж с сохраненной картой"""
        payment = cls(amount, "****-****-****-0000", "SAVED CARD", 12, 2025, "000")
        payment.add_metadata("payment_type", "recurring")
        payment.add_metadata("saved_card_id", saved_card_id)
        return payment

    def _simulate_authorization(self) -> Optional[str]:
        """Симулирует авторизацию платежа"""
        # Простая симуляция - 95% успех
        if random.random() < 0.95:
            auth_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            self.add_metadata("authorization_code", auth_code)
            return auth_code
        return None

    def _simulate_capture(self) -> bool:
        """Симулирует захват средств"""
        # 98% успех для захвата после авторизации
        return random.random() < 0.98

    def _get_last_four(self) -> str:
        """Возвращает последние 4 цифры карты"""
        return self._card_number[-4:] if len(self._card_number) >= 4 else "0000"

    @property
    def masked_card_number(self) -> str:
        """Маскированный номер карты"""
        return self._masked_card_number

    @property
    def card_type(self) -> str:
        """Тип карты"""
        return self._card_type


# ✅ WYMAGANIE: Dziedziczenie + Polimorfizm - Мобильная оплата
class MobilePayment(Payment):
    """
    📋 CHECK: Dziedziczenie - MobilePayment наследует от Payment
    📋 CHECK: Polimorfizm - Своя реализация process_payment()
    Мобильная оплата (Apple Pay, Google Pay, Samsung Pay)
    """

    def __init__(self, amount: float, mobile_provider: str, device_id: str,
                 currency: CurrencyType = CurrencyType.USD, order_id: str = ""):
        # ✅ WYMAGANIE: super()
        super().__init__(amount, currency, order_id, f"{mobile_provider} payment")

        # 🔄 TRANSFER: Payment.__init__ → MobilePayment.__init__
        log_transfer("Payment.__init__", "MobilePayment.__init__", "mobile payment attributes")

        self.mobile_provider = mobile_provider  # "apple_pay", "google_pay", "samsung_pay"
        self.device_id = device_id
        self._biometric_verified = False
        self._token_used: Optional[str] = None

        log_requirement_check("Inheritance", "SUCCESS", f"MobilePayment extends Payment: {self.payment_id}")

    # ✅ WYMAGANIE: Polimorfizm - Уникальная реализация для мобильных платежей
    def process_payment(self) -> bool:
        """
        📋 CHECK: Polimorfizm - Обработка мобильного платежа
        """
        try:
            # Валидируем мобильный платеж
            if not self.validate_payment_data():
                raise PaymentProcessingException("mobile", self.amount, "Invalid mobile payment data")

            self.status = PaymentStatus.PROCESSING

            # Проверяем биометрику
            if not self._verify_biometrics():
                raise PaymentProcessingException("mobile", self.amount, "Biometric verification failed")

            # Генерируем токен
            self._token_used = self._generate_payment_token()

            # Рассчитываем комиссии
            self._transaction_fee = self.calculate_fees()

            # Обрабатываем через мобильный провайдер
            if self._process_with_provider():
                self.status = PaymentStatus.COMPLETED
                log_business_rule("Mobile Payment Processed",
                                  f"{self.mobile_provider} payment: ${self.amount:.2f}")
                return True
            else:
                raise PaymentProcessingException("mobile", self.amount, "Provider processing failed")

        except Exception as e:
            self.status = PaymentStatus.FAILED
            raise PaymentProcessingException("mobile", self.amount, str(e))

    def get_payment_method(self) -> PaymentMethod:
        """Возвращает метод мобильной оплаты"""
        return PaymentMethod.MOBILE_PAY

    def validate_payment_data(self) -> bool:
        """Валидирует данные мобильного платежа"""
        valid_providers = ["apple_pay", "google_pay", "samsung_pay", "android_pay"]
        if self.mobile_provider.lower() not in valid_providers:
            return False

        if not self.device_id or len(self.device_id) < 10:
            return False

        return True

    def calculate_fees(self) -> float:
        """Комиссии для мобильных платежей (обычно ниже чем у карт)"""
        return round(self.amount * 0.025, 2)  # 2.5%

    # ✅ WYMAGANIE: Wiele konstruktorów
    @classmethod
    def create_apple_pay(cls, amount: float, touch_id: str, currency: CurrencyType = CurrencyType.USD):
        """
        📋 CHECK: Wiele konstruktorów - Apple Pay платеж
        """
        payment = cls(amount, "apple_pay", touch_id, currency)
        payment.add_metadata("biometric_type", "touch_id")

        log_requirement_check("Multiple Constructors", "EXECUTED", "MobilePayment.create_apple_pay()")
        return payment

    @classmethod
    def create_google_pay(cls, amount: float, android_id: str, currency: CurrencyType = CurrencyType.USD):
        """Google Pay платеж"""
        payment = cls(amount, "google_pay", android_id, currency)
        payment.add_metadata("biometric_type", "fingerprint")
        return payment

    def _verify_biometrics(self) -> bool:
        """Симулирует биометрическую верификацию"""
        # 97% успех для биометрики
        self._biometric_verified = random.random() < 0.97
        self.add_metadata("biometric_verified", self._biometric_verified)
        return self._biometric_verified

    def _generate_payment_token(self) -> str:
        """Генерирует токен платежа"""
        token = f"TKN{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
        self.add_metadata("payment_token", token)
        return token

    def _process_with_provider(self) -> bool:
        """Симулирует обработку через мобильного провайдера"""
        # 96% успех для мобильных платежей
        return random.random() < 0.96


# ✅ WYMAGANIE: Dziedziczenie + Polimorfizm - Подарочная карта
class GiftCardPayment(Payment):
    """
    📋 CHECK: Dziedziczenie - GiftCardPayment наследует от Payment
    📋 CHECK: Polimorfizm - Своя реализация process_payment()
    Оплата подарочной картой McDonald's
    """

    def __init__(self, amount: float, gift_card_number: str, balance: float,
                 currency: CurrencyType = CurrencyType.USD, order_id: str = ""):
        # ✅ WYMAGANIE: super()
        super().__init__(amount, currency, order_id, "Gift card payment")

        # 🔄 TRANSFER: Payment.__init__ → GiftCardPayment.__init__
        log_transfer("Payment.__init__", "GiftCardPayment.__init__", "gift card attributes")

        self.gift_card_number = gift_card_number
        self._current_balance = balance
        self._remaining_balance = balance - amount

        # Проверяем достаточность средств
        if balance < amount:
            raise InsufficientGiftCardBalanceException(amount, balance, gift_card_number)

        log_requirement_check("Inheritance", "SUCCESS", f"GiftCardPayment extends Payment: {self.payment_id}")

    # ✅ WYMAGANIE: Polimorfizm - Уникальная реализация для подарочных карт
    def process_payment(self) -> bool:
        """
        📋 CHECK: Polimorfizm - Обработка платежа подарочной картой
        """
        try:
            if not self.validate_payment_data():
                raise PaymentProcessingException("gift_card", self.amount, "Invalid gift card")

            self.status = PaymentStatus.PROCESSING

            # Проверяем баланс еще раз
            if self._current_balance < self.amount:
                raise InsufficientGiftCardBalanceException(self.amount, self._current_balance, self.gift_card_number)

            # Списываем средства
            self._remaining_balance = self._current_balance - self.amount

            # Комиссии
            self._transaction_fee = self.calculate_fees()

            self.status = PaymentStatus.COMPLETED
            log_business_rule("Gift Card Payment",
                              f"Card {self.gift_card_number}: ${self.amount:.2f}, remaining: ${self._remaining_balance:.2f}")
            return True

        except Exception as e:
            self.status = PaymentStatus.FAILED
            raise PaymentProcessingException("gift_card", self.amount, str(e))

    def get_payment_method(self) -> PaymentMethod:
        """Возвращает метод подарочной карты"""
        return PaymentMethod.GIFT_CARD

    def validate_payment_data(self) -> bool:
        """Валидирует подарочную карту"""
        # Проверяем формат номера карты
        if len(self.gift_card_number) != 16:
            return False

        # Проверяем что это цифры
        if not self.gift_card_number.isdigit():
            return False

        return True

    def calculate_fees(self) -> float:
        """Для подарочных карт McDonald's нет комиссий"""
        return 0.0

    # ✅ WYMAGANIE: Wiele konstruktorów
    @classmethod
    def create_from_card_scan(cls, amount: float, scanned_data: str):
        """
        📋 CHECK: Wiele konstruktorów - создание из отсканированных данных
        """
        # Парсим отсканированные данные (упрощенная версия)
        card_number = scanned_data[:16] if len(scanned_data) >= 16 else "1234567890123456"
        balance = 50.00  # Симулируем запрос баланса

        payment = cls(amount, card_number, balance)
        payment.add_metadata("scan_source", "barcode_scanner")

        log_requirement_check("Multiple Constructors", "EXECUTED", "GiftCardPayment.create_from_card_scan()")
        return payment

    @property
    def remaining_balance(self) -> float:
        """Остаток на карте после платежа"""
        return self._remaining_balance

    def check_balance(self) -> float:
        """Проверяет текущий баланс карты"""
        return self._current_balance


# ✅ WYMAGANIE: Polimorfizm - Функция использующая полиморфизм
def process_payment_polymorphic(payment: Payment) -> Dict[str, Any]:
    """
    📋 CHECK: Polimorfizm - Полиморфная функция обработки любого типа платежа
    Полиморфная функция - работает с любым типом платежа одинаково
    """
    log_operation("Polymorphic Payment Processing", {
        "payment_id": payment.payment_id,
        "method": payment.get_payment_method().value,
        "amount": payment.amount
    })

    try:
        # Один и тот же интерфейс для всех типов платежей
        success = payment.process_payment()

        result = {
            "success": success,
            "payment_id": payment.payment_id,
            "method": payment.get_payment_method().value,
            "amount": payment.amount,
            "status": payment.status.value,
            "transaction_fee": payment.transaction_fee,
            "net_amount": payment.net_amount
        }

        # Добавляем специфичную информацию в зависимости от типа
        if isinstance(payment, CashPayment):
            result["change"] = payment.change_amount
        elif isinstance(payment, CardPayment):
            result["card_type"] = payment.card_type
            result["masked_card"] = payment.masked_card_number
        elif isinstance(payment, MobilePayment):
            result["provider"] = payment.mobile_provider
        elif isinstance(payment, GiftCardPayment):
            result["remaining_balance"] = payment.remaining_balance

        log_business_rule("Polymorphic Success", f"Payment {payment.payment_id} processed successfully")
        return result

    except Exception as e:
        log_business_rule("Polymorphic Failure", f"Payment {payment.payment_id} failed: {str(e)}")
        return {
            "success": False,
            "payment_id": payment.payment_id,
            "method": payment.get_payment_method().value,
            "error": str(e),
            "status": payment.status.value
        }


# Функция демонстрации системы платежей
def demo_payment_system():
    """
    📋 CHECK: Полная демонстрация системы платежей McDonald's с полиморфизмом
    """

    print("💳 McDONALD'S PAYMENT SYSTEM DEMO")
    print("=" * 50)

    # 🔄 TRANSFER: demo → payment classes
    log_transfer("demo_payment_system", "Payment classes", "payment creation")

    # 1. ✅ WYMAGANIE: Polimorfizm - Создание разных типов платежей
    print("\n1. POLYMORPHISM - Different Payment Types")
    print("-" * 30)

    # Создаем разные типы платежей
    cash_payment = CashPayment.create_exact_change(15.99)
    card_payment = CardPayment.create_contactless_payment(23.45, "CTLS_TOKEN_123")
    mobile_payment = MobilePayment.create_apple_pay(18.75, "TOUCH_ID_456")
    gift_card_payment = GiftCardPayment.create_from_card_scan(12.50, "1234567890123456789")

    payments = [cash_payment, card_payment, mobile_payment, gift_card_payment]

    # 2. ✅ WYMAGANIE: Polimorfizm - Полиморфная обработка
    print("\n2. POLYMORPHIC PROCESSING")
    print("-" * 30)

    for payment in payments:
        print(f"Processing: {payment}")
        result = process_payment_polymorphic(payment)  # Одна функция для всех типов!

        if result["success"]:
            print(f"✅ Success: {result['method']} - ${result['amount']:.2f}")
            print(f"   Fee: ${result['transaction_fee']:.2f}, Net: ${result['net_amount']:.2f}")

            # Показываем специфичную информацию
            if "change" in result:
                print(f"   Change: ${result['change']:.2f}")
            elif "card_type" in result:
                print(f"   Card: {result['card_type']} {result['masked_card']}")
            elif "provider" in result:
                print(f"   Provider: {result['provider']}")
            elif "remaining_balance" in result:
                print(f"   Remaining balance: ${result['remaining_balance']:.2f}")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
        print()

    # 3. ✅ WYMAGANIE: @classmethod и @staticmethod
    print("\n3. CLASS AND STATIC METHODS")
    print("-" * 30)

    # @classmethod
    total_stats = Payment.get_total_processed()
    print(f"Total payments processed: {total_stats['count']}")
    print(f"Total amount: ${total_stats['total_amount']:.2f}")
    print(f"By method: {total_stats['by_method']}")

    # @staticmethod
    converted_amount = Payment.convert_currency(100.0, CurrencyType.USD, CurrencyType.EUR)
    print(f"Currency conversion: $100.00 USD = €{converted_amount:.2f} EUR")

    processing_fee = Payment.calculate_processing_fee(50.0, 0.035)
    print(f"Processing fee for $50.00 at 3.5%: ${processing_fee:.2f}")

    # 4. ✅ WYMAGANIE: Enkapsulacja - Property usage
    print("\n4. ENCAPSULATION (Properties)")
    print("-" * 30)

    payment = card_payment
    print(f"Payment ID (read-only): {payment.payment_id}")
    print(f"Original status: {payment.status.value}")

    # Изменяем статус через setter
    payment.status = PaymentStatus.PROCESSING
    print(f"Updated status: {payment.status.value}")

    print(f"Transaction fee: ${payment.transaction_fee:.2f}")
    print(f"Net amount: ${payment.net_amount:.2f}")

    # 5. Специфичные функции разных типов платежей
    print("\n5. TYPE-SPECIFIC FEATURES")
    print("-" * 30)

    # Наличные
    cash_large = CashPayment.create_large_bill_payment(8.99, 20)
    print(f"Large bill payment: ${cash_large.amount:.2f} with $20, change: ${cash_large.change_amount:.2f}")

    # Карта
    card_type = CardPayment._detect_card_type("4111111111111111")
    print(f"Card type detection: 4111111111111111 is {card_type}")

    # Подарочная карта
    gift_balance = gift_card_payment.check_balance()
    print(f"Gift card balance check: ${gift_balance:.2f}")

    # 6. Обработка ошибок
    print("\n6. ERROR HANDLING")
    print("-" * 30)

    try:
        # Попытка оплаты без достаточных средств
        insufficient_cash = CashPayment(25.00, 20.00)  # Недостаточно наличных
    except InsufficientFundsException as e:
        print(f"❌ Insufficient funds: {e}")

    try:
        # Попытка с недостаточным балансом подарочной карты
        insufficient_gift = GiftCardPayment(100.00, "1111222233334444", 50.00)
    except InsufficientGiftCardBalanceException as e:
        print(f"❌ Gift card insufficient: {e}")

    # 7. Статистика платежей
    print("\n7. PAYMENT STATISTICS")
    print("-" * 30)

    for payment in payments:
        summary = payment.get_payment_summary()
        print(f"{summary['payment_id']}: {summary['method']} - ${summary['amount']:.2f} ({summary['status']})")

    # 📋 CHECK: Финальная проверка полиморфизма
    log_requirement_check("Polymorphism Demo", "COMPLETED", "payment.py")
    log_requirement_check("Payment System Demo", "COMPLETED", "payment.py")

    return payments


if __name__ == "__main__":
    demo_payment_system()