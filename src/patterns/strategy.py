"""
McDonald's Management System - Strategy Pattern
✅ WYMAGANIE: Wzorzec Strategy - różne strategie rabatowe
✅ WYMAGANIE: Polimorfizm poprzez różne implementacje strategii

Паттерн Strategy для различных стратегий скидок McDonald's
"""

from abc import ABC, abstractmethod
from datetime import datetime, time
from typing import Dict, Any, List, Optional
from enum import Enum
import sys
import os

# Добавляем пути для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils.logger import log_transfer, log_requirement_check, log_operation, log_business_rule


class DiscountType(Enum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    BUY_ONE_GET_ONE = "bogo"
    COMBO_DISCOUNT = "combo"
    TIME_BASED = "time_based"
    LOYALTY_TIER = "loyalty_tier"


class CustomerSegment(Enum):
    REGULAR = "regular"
    STUDENT = "student"
    SENIOR = "senior"
    EMPLOYEE = "employee"
    VIP = "vip"
    LOYALTY_MEMBER = "loyalty_member"


# ✅ WYMAGANIE: Wzorzec Strategy - Interfejs strategii
class DiscountStrategy(ABC):
    """
    📋 CHECK: Strategy Pattern - Абстрактная стратегия скидок
    ✅ WYMAGANIE: Wzorzec Strategy - базовый интерфейс для всех стратегий скидок
    """

    def __init__(self, name: str, description: str, valid_from: datetime = None,
                 valid_until: datetime = None):
        self.name = name
        self.description = description
        self.valid_from = valid_from or datetime.now()
        self.valid_until = valid_until
        self._usage_count = 0
        self._total_savings = 0.0

        # 📋 CHECK: Strategy Pattern - подтверждение создания стратегии
        log_requirement_check("Strategy Pattern", "CREATED", f"DiscountStrategy: {name}")

    @abstractmethod
    def calculate_discount(self, order_total: float, order_items: List[Dict[str, Any]],
                           customer_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        📋 CHECK: Strategy Pattern - Основной метод стратегии
        Рассчитывает скидку для заказа

        Returns:
            Dict содержащий:
            - discount_amount: float - сумма скидки
            - discount_type: str - тип скидки
            - applicable: bool - применима ли скидка
            - reason: str - причина (если не применима)
            - details: Dict - дополнительная информация
        """
        pass

    @abstractmethod
    def is_applicable(self, order_total: float, order_items: List[Dict[str, Any]],
                      customer_data: Dict[str, Any] = None) -> bool:
        """Проверяет применимость стратегии к заказу"""
        pass

    def is_valid_time(self) -> bool:
        """Проверяет валидность по времени"""
        now = datetime.now()
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        return True

    def apply_discount(self, order_total: float, order_items: List[Dict[str, Any]],
                       customer_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        📋 CHECK: Strategy Pattern - Применение стратегии
        Применяет стратегию скидки
        """
        # 🔄 TRANSFER: strategy.py → discount calculation
        log_transfer("DiscountStrategy", "calculate_discount", f"applying {self.name}")

        if not self.is_valid_time():
            return {
                "discount_amount": 0.0,
                "discount_type": "none",
                "applicable": False,
                "reason": "Discount period expired",
                "details": {}
            }

        if not self.is_applicable(order_total, order_items, customer_data):
            return {
                "discount_amount": 0.0,
                "discount_type": "none",
                "applicable": False,
                "reason": "Discount not applicable to this order",
                "details": {}
            }

        # Вызываем конкретную реализацию
        result = self.calculate_discount(order_total, order_items, customer_data)

        if result.get("applicable", False):
            self._usage_count += 1
            self._total_savings += result.get("discount_amount", 0.0)

            log_business_rule("Discount Applied",
                              f"{self.name}: ${result.get('discount_amount', 0.0):.2f} saved")

        log_requirement_check("Strategy Pattern", "APPLIED", f"{self.name} strategy")
        return result

    def get_usage_stats(self) -> Dict[str, Any]:
        """Возвращает статистику использования стратегии"""
        return {
            "strategy_name": self.name,
            "usage_count": self._usage_count,
            "total_savings": self._total_savings,
            "average_savings": self._total_savings / max(self._usage_count, 1)
        }


# ✅ WYMAGANIE: Strategy Pattern - Конкретная стратегия процентной скидки
class PercentageDiscountStrategy(DiscountStrategy):
    """
    📋 CHECK: Strategy Pattern - Процентная скидка
    Стратегия процентной скидки
    """

    def __init__(self, name: str, percentage: float, min_order_amount: float = 0.0,
                 max_discount_amount: float = None, valid_from: datetime = None,
                 valid_until: datetime = None):
        super().__init__(name, f"{percentage}% discount", valid_from, valid_until)

        # 🔄 TRANSFER: DiscountStrategy.__init__ → PercentageDiscountStrategy.__init__
        log_transfer("DiscountStrategy.__init__", "PercentageDiscountStrategy.__init__",
                     "percentage strategy attributes")

        self.percentage = percentage
        self.min_order_amount = min_order_amount
        self.max_discount_amount = max_discount_amount

        log_requirement_check("Strategy Inheritance", "SUCCESS",
                              f"PercentageDiscountStrategy extends DiscountStrategy")

    def calculate_discount(self, order_total: float, order_items: List[Dict[str, Any]],
                           customer_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        📋 CHECK: Strategy Pattern - Реализация расчета процентной скидки
        """
        discount_amount = order_total * (self.percentage / 100.0)

        # Применяем максимальную сумму скидки если установлена
        if self.max_discount_amount:
            discount_amount = min(discount_amount, self.max_discount_amount)

        return {
            "discount_amount": round(discount_amount, 2),
            "discount_type": DiscountType.PERCENTAGE.value,
            "applicable": True,
            "reason": f"{self.percentage}% discount applied",
            "details": {
                "percentage": self.percentage,
                "original_total": order_total,
                "max_discount": self.max_discount_amount
            }
        }

    def is_applicable(self, order_total: float, order_items: List[Dict[str, Any]],
                      customer_data: Dict[str, Any] = None) -> bool:
        """Проверяет применимость процентной скидки"""
        return order_total >= self.min_order_amount


# ✅ WYMAGANIE: Strategy Pattern - Фиксированная скидка
class FixedAmountDiscountStrategy(DiscountStrategy):
    """
    📋 CHECK: Strategy Pattern - Фиксированная сумма скидки
    """

    def __init__(self, name: str, discount_amount: float, min_order_amount: float = 0.0,
                 valid_from: datetime = None, valid_until: datetime = None):
        super().__init__(name, f"${discount_amount:.2f} off", valid_from, valid_until)

        # 🔄 TRANSFER: DiscountStrategy.__init__ → FixedAmountDiscountStrategy.__init__
        log_transfer("DiscountStrategy.__init__", "FixedAmountDiscountStrategy.__init__",
                     "fixed amount strategy attributes")

        self.discount_amount = discount_amount
        self.min_order_amount = min_order_amount

        log_requirement_check("Strategy Inheritance", "SUCCESS",
                              f"FixedAmountDiscountStrategy extends DiscountStrategy")

    def calculate_discount(self, order_total: float, order_items: List[Dict[str, Any]],
                           customer_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Реализация расчета фиксированной скидки"""
        # Скидка не может быть больше суммы заказа
        actual_discount = min(self.discount_amount, order_total)

        return {
            "discount_amount": actual_discount,
            "discount_type": DiscountType.FIXED_AMOUNT.value,
            "applicable": True,
            "reason": f"${self.discount_amount:.2f} discount applied",
            "details": {
                "fixed_amount": self.discount_amount,
                "actual_discount": actual_discount,
                "original_total": order_total
            }
        }

    def is_applicable(self, order_total: float, order_items: List[Dict[str, Any]],
                      customer_data: Dict[str, Any] = None) -> bool:
        """Проверяет применимость фиксированной скидки"""
        return order_total >= self.min_order_amount


# ✅ WYMAGANIE: Strategy Pattern - Buy One Get One
class BuyOneGetOneStrategy(DiscountStrategy):
    """
    📋 CHECK: Strategy Pattern - Акция "Купи один, получи второй"
    """

    def __init__(self, name: str, target_items: List[str], discount_percentage: float = 100.0,
                 valid_from: datetime = None, valid_until: datetime = None):
        super().__init__(name, f"Buy one get one {discount_percentage}% off", valid_from, valid_until)

        # 🔄 TRANSFER: DiscountStrategy.__init__ → BuyOneGetOneStrategy.__init__
        log_transfer("DiscountStrategy.__init__", "BuyOneGetOneStrategy.__init__",
                     "BOGO strategy attributes")

        self.target_items = target_items  # Список названий позиций
        self.discount_percentage = discount_percentage  # 100% = бесплатно, 50% = полцены

        log_requirement_check("Strategy Inheritance", "SUCCESS",
                              f"BuyOneGetOneStrategy extends DiscountStrategy")

    def calculate_discount(self, order_total: float, order_items: List[Dict[str, Any]],
                           customer_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Реализация расчета BOGO скидки"""
        total_discount = 0.0
        bogo_details = []

        # Группируем позиции по названию
        item_counts = {}
        item_prices = {}

        for item in order_items:
            item_name = item.get('name', '')
            if item_name in self.target_items:
                quantity = item.get('quantity', 1)
                price = item.get('unit_price', 0.0)

                item_counts[item_name] = item_counts.get(item_name, 0) + quantity
                item_prices[item_name] = price

        # Рассчитываем скидку для каждой позиции
        for item_name, count in item_counts.items():
            if count >= 2:  # Нужно минимум 2 штуки
                free_items = count // 2  # Количество бесплатных/со скидкой
                price = item_prices[item_name]
                item_discount = free_items * price * (self.discount_percentage / 100.0)

                total_discount += item_discount
                bogo_details.append({
                    "item": item_name,
                    "bought": count,
                    "free_items": free_items,
                    "discount": item_discount
                })

        return {
            "discount_amount": round(total_discount, 2),
            "discount_type": DiscountType.BUY_ONE_GET_ONE.value,
            "applicable": total_discount > 0,
            "reason": f"BOGO {self.discount_percentage}% applied",
            "details": {
                "target_items": self.target_items,
                "discount_percentage": self.discount_percentage,
                "bogo_details": bogo_details
            }
        }

    def is_applicable(self, order_total: float, order_items: List[Dict[str, Any]],
                      customer_data: Dict[str, Any] = None) -> bool:
        """Проверяет применимость BOGO"""
        # Проверяем есть ли минимум 2 целевые позиции
        item_counts = {}
        for item in order_items:
            item_name = item.get('name', '')
            if item_name in self.target_items:
                quantity = item.get('quantity', 1)
                item_counts[item_name] = item_counts.get(item_name, 0) + quantity

        return any(count >= 2 for count in item_counts.values())


# ✅ WYMAGANIE: Strategy Pattern - Временная скидка
class TimeBasedDiscountStrategy(DiscountStrategy):
    """
    📋 CHECK: Strategy Pattern - Скидка в определенное время (Happy Hour)
    """

    def __init__(self, name: str, discount_percentage: float,
                 start_time: time, end_time: time, weekdays_only: bool = False,
                 valid_from: datetime = None, valid_until: datetime = None):
        super().__init__(name, f"{discount_percentage}% off during happy hour", valid_from, valid_until)

        # 🔄 TRANSFER: DiscountStrategy.__init__ → TimeBasedDiscountStrategy.__init__
        log_transfer("DiscountStrategy.__init__", "TimeBasedDiscountStrategy.__init__",
                     "time-based strategy attributes")

        self.discount_percentage = discount_percentage
        self.start_time = start_time
        self.end_time = end_time
        self.weekdays_only = weekdays_only

        log_requirement_check("Strategy Inheritance", "SUCCESS",
                              f"TimeBasedDiscountStrategy extends DiscountStrategy")

    def calculate_discount(self, order_total: float, order_items: List[Dict[str, Any]],
                           customer_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Реализация расчета временной скидки"""
        discount_amount = order_total * (self.discount_percentage / 100.0)

        return {
            "discount_amount": round(discount_amount, 2),
            "discount_type": DiscountType.TIME_BASED.value,
            "applicable": True,
            "reason": f"Happy Hour {self.discount_percentage}% discount",
            "details": {
                "percentage": self.discount_percentage,
                "time_period": f"{self.start_time} - {self.end_time}",
                "weekdays_only": self.weekdays_only,
                "current_time": datetime.now().time().strftime("%H:%M")
            }
        }

    def is_applicable(self, order_total: float, order_items: List[Dict[str, Any]],
                      customer_data: Dict[str, Any] = None) -> bool:
        """Проверяет применимость временной скидки"""
        now = datetime.now()
        current_time = now.time()

        # Проверяем день недели
        if self.weekdays_only and now.weekday() >= 5:  # 5=Saturday, 6=Sunday
            return False

        # Проверяем время
        if self.start_time <= self.end_time:
            # Обычный случай (например, 14:00 - 17:00)
            return self.start_time <= current_time <= self.end_time
        else:
            # Переход через полночь (например, 22:00 - 06:00)
            return current_time >= self.start_time or current_time <= self.end_time


# ✅ WYMAGANIE: Strategy Pattern - Лояльность клиентов
class LoyaltyTierDiscountStrategy(DiscountStrategy):
    """
    📋 CHECK: Strategy Pattern - Скидка на основе уровня лояльности
    """

    def __init__(self, name: str, tier_discounts: Dict[str, float],
                 valid_from: datetime = None, valid_until: datetime = None):
        super().__init__(name, "Loyalty tier discount", valid_from, valid_until)

        # 🔄 TRANSFER: DiscountStrategy.__init__ → LoyaltyTierDiscountStrategy.__init__
        log_transfer("DiscountStrategy.__init__", "LoyaltyTierDiscountStrategy.__init__",
                     "loyalty tier strategy attributes")

        self.tier_discounts = tier_discounts  # {"bronze": 5, "silver": 8, "gold": 12, "platinum": 15}

        log_requirement_check("Strategy Inheritance", "SUCCESS",
                              f"LoyaltyTierDiscountStrategy extends DiscountStrategy")

    def calculate_discount(self, order_total: float, order_items: List[Dict[str, Any]],
                           customer_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Реализация расчета скидки лояльности"""
        if not customer_data:
            return self._no_discount_result("No customer data provided")

        customer_tier = customer_data.get('loyalty_tier', '').lower()
        discount_percentage = self.tier_discounts.get(customer_tier, 0.0)

        if discount_percentage == 0:
            return self._no_discount_result(f"No discount for tier: {customer_tier}")

        discount_amount = order_total * (discount_percentage / 100.0)

        return {
            "discount_amount": round(discount_amount, 2),
            "discount_type": DiscountType.LOYALTY_TIER.value,
            "applicable": True,
            "reason": f"{customer_tier.title()} tier {discount_percentage}% discount",
            "details": {
                "customer_tier": customer_tier,
                "percentage": discount_percentage,
                "all_tiers": self.tier_discounts
            }
        }

    def is_applicable(self, order_total: float, order_items: List[Dict[str, Any]],
                      customer_data: Dict[str, Any] = None) -> bool:
        """Проверяет применимость скидки лояльности"""
        if not customer_data:
            return False

        customer_tier = customer_data.get('loyalty_tier', '').lower()
        return customer_tier in self.tier_discounts

    def _no_discount_result(self, reason: str) -> Dict[str, Any]:
        """Возвращает результат без скидки"""
        return {
            "discount_amount": 0.0,
            "discount_type": "none",
            "applicable": False,
            "reason": reason,
            "details": {}
        }


# ✅ WYMAGANIE: Strategy Pattern - Комбо скидки
class ComboDiscountStrategy(DiscountStrategy):
    """
    📋 CHECK: Strategy Pattern - Скидка на комбо меню
    """

    def __init__(self, name: str, combo_items: List[str], combo_price: float,
                 valid_from: datetime = None, valid_until: datetime = None):
        super().__init__(name, f"Combo deal for ${combo_price:.2f}", valid_from, valid_until)

        # 🔄 TRANSFER: DiscountStrategy.__init__ → ComboDiscountStrategy.__init__
        log_transfer("DiscountStrategy.__init__", "ComboDiscountStrategy.__init__",
                     "combo strategy attributes")

        self.combo_items = combo_items  # Список обязательных позиций для комбо
        self.combo_price = combo_price

        log_requirement_check("Strategy Inheritance", "SUCCESS",
                              f"ComboDiscountStrategy extends DiscountStrategy")

    def calculate_discount(self, order_total: float, order_items: List[Dict[str, Any]],
                           customer_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Реализация расчета комбо скидки"""
        # Находим цены отдельных позиций комбо
        individual_total = 0.0
        found_items = []

        for required_item in self.combo_items:
            for order_item in order_items:
                if required_item.lower() in order_item.get('name', '').lower():
                    individual_total += order_item.get('unit_price', 0.0)
                    found_items.append(order_item.get('name', ''))
                    break

        # Рассчитываем экономию
        if len(found_items) == len(self.combo_items):
            savings = individual_total - self.combo_price
            return {
                "discount_amount": max(0, round(savings, 2)),
                "discount_type": DiscountType.COMBO_DISCOUNT.value,
                "applicable": True,
                "reason": f"Combo meal discount applied",
                "details": {
                    "combo_items": self.combo_items,
                    "found_items": found_items,
                    "individual_total": individual_total,
                    "combo_price": self.combo_price,
                    "savings": savings
                }
            }

        return {
            "discount_amount": 0.0,
            "discount_type": "none",
            "applicable": False,
            "reason": f"Missing combo items. Found: {found_items}",
            "details": {
                "required_items": self.combo_items,
                "found_items": found_items
            }
        }

    def is_applicable(self, order_total: float, order_items: List[Dict[str, Any]],
                      customer_data: Dict[str, Any] = None) -> bool:
        """Проверяет наличие всех позиций для комбо"""
        found_count = 0

        for required_item in self.combo_items:
            for order_item in order_items:
                if required_item.lower() in order_item.get('name', '').lower():
                    found_count += 1
                    break

        return found_count == len(self.combo_items)


# ✅ WYMAGANIE: Strategy Pattern - Контекст использующий стратегии
class DiscountManager:
    """
    📋 CHECK: Strategy Pattern - Контекст использующий стратегии
    Менеджер скидок использующий паттерн Strategy
    """

    def __init__(self):
        self._strategies: List[DiscountStrategy] = []
        self._applied_discounts_today = 0
        self._total_savings_today = 0.0

        # 📋 CHECK: Strategy Pattern - контекст создан
        log_requirement_check("Strategy Pattern Context", "CREATED", "DiscountManager")

    def add_strategy(self, strategy: DiscountStrategy):
        """Добавляет стратегию скидки"""
        self._strategies.append(strategy)
        log_business_rule("Strategy Added", f"Added {strategy.name} to discount manager")

    def remove_strategy(self, strategy_name: str):
        """Убирает стратегию скидки"""
        self._strategies = [s for s in self._strategies if s.name != strategy_name]
        log_business_rule("Strategy Removed", f"Removed {strategy_name} from discount manager")

    def calculate_best_discount(self, order_total: float, order_items: List[Dict[str, Any]],
                                customer_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        📋 CHECK: Strategy Pattern - Использование стратегий
        Находит лучшую скидку среди всех доступных стратегий
        """
        # 🔄 TRANSFER: DiscountManager → strategies (best discount calculation)
        log_transfer("DiscountManager", "DiscountStrategy instances", "best discount search")

        best_discount = {
            "discount_amount": 0.0,
            "discount_type": "none",
            "applicable": False,
            "reason": "No applicable discounts",
            "strategy_name": "none",
            "details": {}
        }

        available_discounts = []

        # Проверяем все стратегии
        for strategy in self._strategies:
            discount_result = strategy.apply_discount(order_total, order_items, customer_data)

            if discount_result.get("applicable", False):
                discount_result["strategy_name"] = strategy.name
                available_discounts.append(discount_result)

                # Выбираем лучшую (максимальную) скидку
                if discount_result["discount_amount"] > best_discount["discount_amount"]:
                    best_discount = discount_result

        # Обновляем статистику
        if best_discount["applicable"]:
            self._applied_discounts_today += 1
            self._total_savings_today += best_discount["discount_amount"]

        log_business_rule("Best Discount Calculated",
                          f"Best: {best_discount['strategy_name']} - ${best_discount['discount_amount']:.2f}")

        # Добавляем информацию о всех доступных скидках
        best_discount["all_available"] = available_discounts

        log_requirement_check("Strategy Pattern", "EXECUTED", "Best discount calculation")
        return best_discount

    def calculate_multiple_discounts(self, order_total: float, order_items: List[Dict[str, Any]],
                                     customer_data: Dict[str, Any] = None,
                                     allow_stacking: bool = False) -> Dict[str, Any]:
        """
        Рассчитывает множественные скидки (если разрешено их совмещение)
        """
        if not allow_stacking:
            return self.calculate_best_discount(order_total, order_items, customer_data)

        total_discount = 0.0
        applied_strategies = []
        current_total = order_total

        # Применяем стратегии по очереди
        for strategy in self._strategies:
            discount_result = strategy.apply_discount(current_total, order_items, customer_data)

            if discount_result.get("applicable", False):
                discount_amount = discount_result["discount_amount"]
                total_discount += discount_amount
                current_total -= discount_amount

                applied_strategies.append({
                    "strategy": strategy.name,
                    "discount": discount_amount,
                    "type": discount_result["discount_type"]
                })

        return {
            "discount_amount": round(total_discount, 2),
            "discount_type": "stacked",
            "applicable": len(applied_strategies) > 0,
            "reason": f"Stacked {len(applied_strategies)} discounts",
            "strategy_name": "multiple",
            "details": {
                "applied_strategies": applied_strategies,
                "original_total": order_total,
                "final_total": current_total
            }
        }

    def get_available_strategies(self) -> List[str]:
        """Возвращает список доступных стратегий"""
        return [strategy.name for strategy in self._strategies]

    def get_daily_stats(self) -> Dict[str, Any]:
        """Возвращает дневную статистику скидок"""
        strategy_stats = [strategy.get_usage_stats() for strategy in self._strategies]

        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "discounts_applied": self._applied_discounts_today,
            "total_savings": self._total_savings_today,
            "active_strategies": len(self._strategies),
            "strategy_stats": strategy_stats
        }


# Функция демонстрации паттерна Strategy
def demo_strategy_pattern():
    """
    📋 CHECK: Полная демонстрация паттерна Strategy для скидок McDonald's
    """

    print("🎯 McDONALD'S STRATEGY PATTERN DEMO")
    print("=" * 50)

    # 🔄 TRANSFER: demo → strategy pattern
    log_transfer("demo_strategy_pattern", "Strategy Pattern", "strategy demonstration")

    # 1. Создание менеджера скидок
    print("\n1. DISCOUNT MANAGER CREATION")
    print("-" * 30)

    discount_manager = DiscountManager()
    print("Created DiscountManager")

    # 2. Создание различных стратегий скидок
    print("\n2. STRATEGY CREATION")
    print("-" * 30)

    # Процентная скидка
    student_discount = PercentageDiscountStrategy(
        "Student Discount", 15.0, min_order_amount=10.0, max_discount_amount=5.0
    )

    # Фиксированная скидка
    first_order_discount = FixedAmountDiscountStrategy(
        "First Order Special", 3.00, min_order_amount=15.0
    )

    # BOGO скидка
    fries_bogo = BuyOneGetOneStrategy(
        "Fries BOGO", ["French Fries"], discount_percentage=50.0
    )

    # Временная скидка (Happy Hour)
    happy_hour = TimeBasedDiscountStrategy(
        "Happy Hour", 20.0, time(14, 0), time(17, 0), weekdays_only=True
    )

    # Лояльность
    loyalty_discount = LoyaltyTierDiscountStrategy(
        "Loyalty Tiers", {"bronze": 5, "silver": 8, "gold": 12, "platinum": 15}
    )

    # Комбо скидка
    big_mac_combo = ComboDiscountStrategy(
        "Big Mac Combo", ["Big Mac", "French Fries", "Coca-Cola"], 8.99
    )

    strategies = [student_discount, first_order_discount, fries_bogo,
                  happy_hour, loyalty_discount, big_mac_combo]

    # Добавляем стратегии в менеджер
    for strategy in strategies:
        discount_manager.add_strategy(strategy)
        print(f"Added strategy: {strategy.name}")

    # 3. Создание тестовых заказов
    print("\n3. TEST ORDERS")
    print("-" * 30)

    # Заказ 1: Студенческий
    order1_items = [
        {"name": "Big Mac", "quantity": 1, "unit_price": 4.99},
        {"name": "French Fries (Medium)", "quantity": 1, "unit_price": 2.49},
        {"name": "Coca-Cola", "quantity": 1, "unit_price": 1.79}
    ]
    order1_total = sum(item["unit_price"] * item["quantity"] for item in order1_items)
    customer1_data = {"customer_type": "student", "loyalty_tier": "bronze"}

    # Заказ 2: Лояльный клиент с BOGO
    order2_items = [
        {"name": "French Fries (Large)", "quantity": 2, "unit_price": 2.99},
        {"name": "McChicken", "quantity": 1, "unit_price": 3.99}
    ]
    order2_total = sum(item["unit_price"] * item["quantity"] for item in order2_items)
    customer2_data = {"customer_type": "loyalty", "loyalty_tier": "gold"}

    # Заказ 3: Комбо меню
    order3_items = [
        {"name": "Big Mac", "quantity": 1, "unit_price": 4.99},
        {"name": "French Fries (Medium)", "quantity": 1, "unit_price": 2.49},
        {"name": "Coca-Cola", "quantity": 1, "unit_price": 1.79}
    ]
    order3_total = sum(item["unit_price"] * item["quantity"] for item in order3_items)
    customer3_data = {"customer_type": "regular"}

    orders = [
        (order1_items, order1_total, customer1_data, "Student Order"),
        (order2_items, order2_total, customer2_data, "Loyalty Customer with BOGO"),
        (order3_items, order3_total, customer3_data, "Regular Combo Order")
    ]

    # 4. Применение стратегий
    print("\n4. STRATEGY APPLICATION")
    print("-" * 30)

    for order_items, order_total, customer_data, description in orders:
        print(f"\n{description}:")
        print(f"Original total: ${order_total:.2f}")

        # Находим лучшую скидку
        best_discount = discount_manager.calculate_best_discount(
            order_total, order_items, customer_data
        )

        if best_discount["applicable"]:
            final_total = order_total - best_discount["discount_amount"]
            print(f"✅ Applied: {best_discount['strategy_name']}")
            print(f"   Discount: ${best_discount['discount_amount']:.2f}")
            print(f"   Final total: ${final_total:.2f}")
            print(f"   Reason: {best_discount['reason']}")

            # Показываем все доступные скидки
            all_available = best_discount.get("all_available", [])
            if len(all_available) > 1:
                print(f"   Other available discounts:")
                for discount in all_available:
                    if discount["strategy_name"] != best_discount["strategy_name"]:
                        print(f"     - {discount['strategy_name']}: ${discount['discount_amount']:.2f}")
        else:
            print(f"❌ No applicable discounts: {best_discount['reason']}")

    # 5. Тестирование стекинга скидок
    print("\n5. STACKED DISCOUNTS TEST")
    print("-" * 30)

    # Тестируем с разрешением стекинга
    stacked_result = discount_manager.calculate_multiple_discounts(
        order1_total, order1_items, customer1_data, allow_stacking=True
    )

    print(f"Stacked discounts for student order:")
    print(f"Original: ${order1_total:.2f}")
    print(f"Total discount: ${stacked_result['discount_amount']:.2f}")

    if stacked_result.get("details", {}).get("applied_strategies"):
        for strategy in stacked_result["details"]["applied_strategies"]:
            print(f"  - {strategy['strategy']}: ${strategy['discount']:.2f}")

    # 6. Статистика использования
    print("\n6. USAGE STATISTICS")
    print("-" * 30)

    daily_stats = discount_manager.get_daily_stats()
    print(f"Discounts applied today: {daily_stats['discounts_applied']}")
    print(f"Total savings: ${daily_stats['total_savings']:.2f}")
    print(f"Active strategies: {daily_stats['active_strategies']}")

    print("\nStrategy usage:")
    for strategy_stat in daily_stats['strategy_stats']:
        if strategy_stat['usage_count'] > 0:
            print(f"  {strategy_stat['strategy_name']}: {strategy_stat['usage_count']} uses, "
                  f"${strategy_stat['total_savings']:.2f} saved")

    # 📋 CHECK: Финальная проверка паттерна Strategy
    log_requirement_check("Strategy Pattern Demo", "COMPLETED", "strategy.py")

    return discount_manager


if __name__ == "__main__":
    demo_strategy_pattern()