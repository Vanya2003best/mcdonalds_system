"""
McDonald's Management System - Menu Models
✅ WYMAGANIE: Użycie klas, dziedziczenie, nadpisywanie atrybutów i metod,
             @classmethod, @staticmethod, enkapsulacja, super()

Модели меню McDonald's с полной иерархией наследования
"""

from abc import ABC, abstractmethod
from datetime import datetime, time
from typing import List, Dict, Optional, Any
from enum import Enum
import sys
import os

# Добавляем пути для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils.logger import log_transfer, log_requirement_check, log_operation, log_business_rule
from src.exceptions.mcdonalds_exceptions import MenuItemNotAvailableException, InsufficientIngredientsException


# Перечисления для категорий и размеров
class MenuCategory(Enum):
    BURGERS = "burgers"
    CHICKEN = "chicken"
    SIDES = "sides"
    DRINKS = "drinks"
    DESSERTS = "desserts"
    BREAKFAST = "breakfast"
    MCCAFE = "mccafe"
    HAPPY_MEAL = "happy_meal"


class ItemSize(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    EXTRA_LARGE = "extra_large"


# ✅ WYMAGANIE: Użycie klas - Базовая абстрактная класса для всех позиций меню
class MenuItem(ABC):
    """
    📋 CHECK: Klasy - Абстрактная базовая класса для всех позиций меню McDonald's
    ✅ WYMAGANIE: Enkapsulacja - Использование property, getters, setters
    ✅ WYMAGANIE: @classmethod, @staticmethod
    """

    # ✅ WYMAGANIE: Atrybuty w klasach - атрибуты класса для счетчиков
    total_items_created = 0
    available_categories = list(MenuCategory)

    def __init__(self, name: str, base_price: float, category: MenuCategory,
                 ingredients: List[str] = None, calories: int = 0):
        # 🔄 TRANSFER: menu.py → logger (log_operation)
        log_operation("MenuItem Creation", {"name": name, "category": category.value})

        # Приватные атрибуты для энкапсуляции
        self._name = name
        self._base_price = base_price
        self._category = category
        self._ingredients = ingredients or []
        self._calories = calories
        self._available = True
        self._preparation_time = 5  # базовое время в минутах
        self._nutritional_info = {}

        # Инкремент счетчика созданных позиций
        MenuItem.total_items_created += 1

        # 📋 CHECK: Klasy - подтверждение создания класса
        log_requirement_check("Class Creation", "SUCCESS", f"MenuItem: {name}")

    # ✅ WYMAGANIE: Enkapsulacja - Property with getter and setter
    @property
    def name(self) -> str:
        """Геттер для названия позиции"""
        return self._name

    @name.setter
    def name(self, value: str):
        """
        📋 CHECK: Enkapsulacja - Setter с валидацией
        Сеттер для названия с валидацией
        """
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")
        old_name = self._name
        self._name = value.strip()
        # 🚨 LOG: Логируем изменение названия
        log_operation("Name Change", {"old": old_name, "new": self._name})

    @property
    def base_price(self) -> float:
        """Геттер для базовой цены"""
        return self._base_price

    @base_price.setter
    def base_price(self, value: float):
        """
        📋 CHECK: Enkapsulacja - Price validation
        Сеттер для цены с валидацией
        """
        if value < 0:
            raise ValueError("Price cannot be negative")
        old_price = self._base_price
        self._base_price = value
        log_business_rule("Price Change", f"{self.name}: ${old_price:.2f} → ${value:.2f}")

    @property
    def available(self) -> bool:
        """Геттер для доступности"""
        return self._available

    @available.setter
    def available(self, value: bool):
        """Сеттер для доступности"""
        self._available = bool(value)
        status = "AVAILABLE" if value else "UNAVAILABLE"
        log_business_rule("Availability Change", f"{self.name}: {status}")

    @property
    def calories(self) -> int:
        """Геттер для калорий"""
        return self._calories

    @calories.setter
    def calories(self, value: int):
        """Сеттер для калорий с валидацией"""
        if value < 0:
            raise ValueError("Calories cannot be negative")
        self._calories = value

    @property
    def ingredients(self) -> List[str]:
        """Геттер для ингредиентов"""
        return self._ingredients.copy()  # Возвращаем копию для безопасности

    # ✅ WYMAGANIE: @classmethod - Альтернативные конструкторы
    @classmethod
    def create_big_mac(cls):
        """
        📋 CHECK: @classmethod - Factory method для Big Mac
        Factory method для создания Big Mac
        """
        # 🔄 TRANSFER: menu.py → MenuItem.__init__ (create_big_mac data)
        log_transfer("menu.py", "MenuItem.__init__", "Big Mac creation data")

        ingredients = ["special sauce", "lettuce", "cheese", "pickles", "onions", "sesame seed bun", "beef patty"]
        big_mac = cls("Big Mac", 4.99, MenuCategory.BURGERS, ingredients, 550)
        big_mac._preparation_time = 8

        log_requirement_check("@classmethod", "EXECUTED", "MenuItem.create_big_mac()")
        return big_mac

    @classmethod
    def create_happy_meal(cls, main_item: str, drink: str = "Apple Juice", toy: str = "Random"):
        """Factory method для Happy Meal"""
        ingredients = [main_item, drink, "apple slices", toy]
        happy_meal = cls(f"Happy Meal ({main_item})", 3.99, MenuCategory.HAPPY_MEAL, ingredients, 400)
        return happy_meal

    @classmethod
    def get_total_items_created(cls) -> int:
        """Возвращает общее количество созданных позиций"""
        return cls.total_items_created

    # ✅ WYMAGANIE: @staticmethod - Утилитарные методы без привязки к экземпляру
    @staticmethod
    def calculate_calories_with_size(base_calories: int, size: ItemSize) -> int:
        """
        📋 CHECK: @staticmethod - Расчет калорий в зависимости от размера
        Статический метод для расчета калорий в зависимости от размера
        """
        log_requirement_check("@staticmethod", "EXECUTED", "MenuItem.calculate_calories_with_size()")

        size_multipliers = {
            ItemSize.SMALL: 0.8,
            ItemSize.MEDIUM: 1.0,
            ItemSize.LARGE: 1.3,
            ItemSize.EXTRA_LARGE: 1.6
        }

        multiplier = size_multipliers.get(size, 1.0)
        result = int(base_calories * multiplier)

        # 🚨 LOG: Логируем расчет калорий
        log_operation("Calorie Calculation", {
            "base": base_calories,
            "size": size.value,
            "multiplier": multiplier,
            "result": result
        })

        return result

    @staticmethod
    def is_breakfast_time() -> bool:
        """Проверяет, время ли завтрака (до 10:30)"""
        now = datetime.now().time()
        breakfast_end = time(10, 30)  # 10:30 AM
        return now <= breakfast_end

    @staticmethod
    def calculate_discount_price(original_price: float, discount_percent: float) -> float:
        """Рассчитывает цену со скидкой"""
        if not 0 <= discount_percent <= 100:
            raise ValueError("Discount percent must be between 0 and 100")
        return original_price * (1 - discount_percent / 100)

    # Абстрактные методы, которые должны быть реализованы в подклассах
    @abstractmethod
    def get_final_price(self, size: ItemSize = ItemSize.MEDIUM) -> float:
        """Рассчитывает финальную цену с учетом размера"""
        pass

    @abstractmethod
    def get_preparation_time(self) -> int:
        """Возвращает время приготовления в минутах"""
        pass

    # Обычные методы
    def add_ingredient(self, ingredient: str):
        """Добавляет ингредиент"""
        if ingredient not in self._ingredients:
            self._ingredients.append(ingredient)
            log_business_rule("Ingredient Added", f"{self.name}: +{ingredient}")

    def remove_ingredient(self, ingredient: str):
        """Убирает ингредиент"""
        if ingredient in self._ingredients:
            self._ingredients.remove(ingredient)
            log_business_rule("Ingredient Removed", f"{self.name}: -{ingredient}")

    def __str__(self) -> str:
        return f"{self.name} - ${self.base_price:.2f} ({self._category.value})"

    def __repr__(self) -> str:
        return f"MenuItem(name='{self.name}', price=${self.base_price:.2f}, category={self._category.value})"


# ✅ WYMAGANIE: Dziedziczenie - Класс Burger наследует от MenuItem
class Burger(MenuItem):
    """
    📋 CHECK: Dziedziczenie - Burger наследует от MenuItem
    ✅ WYMAGANIE: Nadpisywanie atrybutów i metod w klasach potomnych
    ✅ WYMAGANIE: super() - использование родительской реализации
    """

    # ✅ WYMAGANIE: Nadpisywanie atrybutów - переопределение атрибутов класса
    default_preparation_time = 6  # минут (переопределено из базового 5)
    category_name = "McDonald's Burgers"

    def __init__(self, name: str, base_price: float, patty_count: int = 1,
                 has_cheese: bool = True, ingredients: List[str] = None):
        # ✅ WYMAGANIE: super() - вызов конструктора родительского класса
        super().__init__(name, base_price, MenuCategory.BURGERS, ingredients)

        # 🔄 TRANSFER: menu.py → Burger.__init__ (burger specific data)
        log_transfer("MenuItem.__init__", "Burger.__init__", "burger-specific attributes")

        # Специфичные для бургера атрибуты
        self.patty_count = patty_count
        self.has_cheese = has_cheese
        self._is_signature = False

        # Переопределяем время приготовления
        self._preparation_time = self.default_preparation_time + (patty_count - 1) * 2

        # 📋 CHECK: Dziedziczenie - подтверждение наследования
        log_requirement_check("Inheritance", "SUCCESS", f"Burger extends MenuItem: {name}")

    # ✅ WYMAGANIE: Nadpisywanie metod - переопределение методов родителя
    def get_final_price(self, size: ItemSize = ItemSize.MEDIUM) -> float:
        """
        📋 CHECK: Nadpisywanie metod - переопределенный метод расчета цены
        Переопределенный метод расчета финальной цены для бургера
        """
        # Базовая цена из родительского класса
        base = self.base_price

        # Добавка за дополнительные котлеты
        if self.patty_count > 1:
            base += (self.patty_count - 1) * 1.50

        # Добавка за сыр
        if self.has_cheese:
            base += 0.50

        # Множитель за размер (для бургеров размер влияет на фри и напиток в комбо)
        size_multiplier = {
            ItemSize.SMALL: 0.9,
            ItemSize.MEDIUM: 1.0,
            ItemSize.LARGE: 1.2
        }.get(size, 1.0)

        final_price = base * size_multiplier

        # 🚨 LOG: Логируем расчет цены
        log_operation("Burger Price Calculation", {
            "base_price": self.base_price,
            "patties": self.patty_count,
            "has_cheese": self.has_cheese,
            "size": size.value,
            "final_price": final_price
        })

        return final_price

    def get_preparation_time(self) -> int:
        """Переопределенный метод времени приготовления"""
        # ✅ WYMAGANIE: super() - использование реализации родителя плюс дополнительная логика
        base_time = self._preparation_time

        # Дополнительное время для signature бургеров
        if self._is_signature:
            base_time += 2

        return base_time

    # Специфичные методы для бургеров
    def make_signature(self):
        """Делает бургер signature (премиум)"""
        self._is_signature = True
        self.base_price += 2.00
        log_business_rule("Signature Upgrade", f"{self.name} upgraded to signature")

    def add_extra_patty(self):
        """Добавляет дополнительную котлету"""
        self.patty_count += 1
        self._preparation_time += 2
        log_business_rule("Extra Patty", f"{self.name}: now {self.patty_count} patties")

    def __str__(self) -> str:
        """Переопределенное строковое представление"""
        cheese_info = "with cheese" if self.has_cheese else "no cheese"
        patty_info = f"{self.patty_count} patty" if self.patty_count == 1 else f"{self.patty_count} patties"
        return f"{self.name} ({patty_info}, {cheese_info}) - ${self.get_final_price():.2f}"


# ✅ WYMAGANIE: Dziedziczenie - Класс Fries наследует от MenuItem
class Fries(MenuItem):
    """
    📋 CHECK: Dziedziczenie - Fries (картошка фри) наследует от MenuItem
    McDonald's картошка фри с разными размерами
    """

    # ✅ WYMAGANIE: Nadpisywanie atrybutów - переопределение атрибутов класса
    default_preparation_time = 3  # Быстрее чем бургеры
    category_name = "McDonald's Fries & Sides"

    def __init__(self, size: ItemSize = ItemSize.MEDIUM, seasoning: str = "salt"):
        # ✅ WYMAGANIE: super() - вызов родительского конструктора
        name = f"French Fries ({size.value.title()})"
        base_price = self._get_price_by_size(size)
        ingredients = ["potato", "vegetable oil", seasoning]

        super().__init__(name, base_price, MenuCategory.SIDES, ingredients)

        # 🔄 TRANSFER: MenuItem.__init__ → Fries.__init__ (size and seasoning data)
        log_transfer("MenuItem.__init__", "Fries.__init__", "fries-specific attributes")

        self.size = size
        self.seasoning = seasoning
        self._preparation_time = self.default_preparation_time

        log_requirement_check("Inheritance", "SUCCESS", f"Fries extends MenuItem: {name}")

    @staticmethod
    def _get_price_by_size(size: ItemSize) -> float:
        """Возвращает базовую цену в зависимости от размера"""
        price_map = {
            ItemSize.SMALL: 1.99,
            ItemSize.MEDIUM: 2.49,
            ItemSize.LARGE: 2.99,
            ItemSize.EXTRA_LARGE: 3.49
        }
        return price_map.get(size, 2.49)

    # ✅ WYMAGANIE: Nadpisywanie metод - переопределение метода
    def get_final_price(self, size: ItemSize = None) -> float:
        """
        📋 CHECK: Nadpisywanie metod - переопределенный расчет цены для фри
        """
        # Для фри размер уже учтен в base_price
        final_price = self.base_price

        # Премиум за особые приправы
        premium_seasonings = ["truffle", "parmesan", "cajun"]
        if self.seasoning.lower() in premium_seasonings:
            final_price += 0.75

        log_operation("Fries Price Calculation", {
            "size": self.size.value,
            "seasoning": self.seasoning,
            "base_price": self.base_price,
            "final_price": final_price
        })

        return final_price

    def get_preparation_time(self) -> int:
        """Время приготовления фри"""
        return self._preparation_time

    def upgrade_size(self, new_size: ItemSize):
        """Увеличивает размер фри"""
        if new_size.value > self.size.value:
            old_size = self.size
            self.size = new_size
            self._name = f"French Fries ({new_size.value.title()})"
            self.base_price = self._get_price_by_size(new_size)

            log_business_rule("Size Upgrade", f"Fries: {old_size.value} → {new_size.value}")


# ✅ WYMAGANIE: Dziedziczenie - Класс Drink наследует от MenuItem
class Drink(MenuItem):
    """
    📋 CHECK: Dziedziczenie - Drink наследует от MenuItem
    McDonald's напитки (газировка, кофе, соки)
    """

    # ✅ WYMAGANIE: Nadpisywanie atrybutów
    default_preparation_time = 2  # Самое быстрое приготовление
    category_name = "McDonald's Beverages"

    def __init__(self, name: str, size: ItemSize = ItemSize.MEDIUM,
                 is_hot: bool = False, has_caffeine: bool = False):
        # ✅ WYMAGANIE: super()
        base_price = self._get_price_by_size(size)
        category = MenuCategory.MCCAFE if is_hot else MenuCategory.DRINKS

        super().__init__(name, base_price, category)

        # 🔄 TRANSFER: MenuItem.__init__ → Drink.__init__ (drink attributes)
        log_transfer("MenuItem.__init__", "Drink.__init__", "drink-specific attributes")

        self.size = size
        self.is_hot = is_hot
        self.has_caffeine = has_caffeine
        self._ice_level = "normal" if not is_hot else "none"
        self._preparation_time = self.default_preparation_time

        # Горячие напитки готовятся дольше
        if is_hot:
            self._preparation_time += 3

        log_requirement_check("Inheritance", "SUCCESS", f"Drink extends MenuItem: {name}")

    @staticmethod
    def _get_price_by_size(size: ItemSize) -> float:
        """Базовая цена напитка по размеру"""
        price_map = {
            ItemSize.SMALL: 1.49,
            ItemSize.MEDIUM: 1.79,
            ItemSize.LARGE: 2.09,
            ItemSize.EXTRA_LARGE: 2.39
        }
        return price_map.get(size, 1.79)

    # ✅ WYMAGANIE: Nadpisywanie metод
    def get_final_price(self, size: ItemSize = None) -> float:
        """
        📋 CHECK: Nadpisywanie metод - расчет цены напитка
        """
        final_price = self.base_price

        # Премиум за горячие напитки McCafe
        if self.is_hot and self.has_caffeine:
            final_price += 1.00

        log_operation("Drink Price Calculation", {
            "name": self.name,
            "size": self.size.value,
            "is_hot": self.is_hot,
            "has_caffeine": self.has_caffeine,
            "final_price": final_price
        })

        return final_price

    def get_preparation_time(self) -> int:
        """Время приготовления напитка"""
        return self._preparation_time

    # ✅ WYMAGANIE: @classmethod - специфичные factory methods для напитков
    @classmethod
    def create_coca_cola(cls, size: ItemSize = ItemSize.MEDIUM):
        """Factory method для Coca-Cola"""
        drink = cls("Coca-Cola", size, is_hot=False, has_caffeine=True)
        drink.add_ingredient("coca-cola syrup")
        drink.add_ingredient("carbonated water")
        return drink

    @classmethod
    def create_mccafe_coffee(cls, coffee_type: str = "Latte", size: ItemSize = ItemSize.MEDIUM):
        """Factory method для McCafe кофе"""
        name = f"McCafe {coffee_type}"
        drink = cls(name, size, is_hot=True, has_caffeine=True)
        drink.add_ingredient("espresso")
        drink.add_ingredient("milk")
        if coffee_type.lower() == "cappuccino":
            drink.add_ingredient("foam")
        return drink

    def set_ice_level(self, level: str):
        """Устанавливает уровень льда (no ice, light, normal, extra)"""
        valid_levels = ["none", "light", "normal", "extra"]
        if level.lower() in valid_levels:
            self._ice_level = level.lower()
            log_business_rule("Ice Level", f"{self.name}: {level} ice")


# ✅ WYMAGANIE: Dziedziczenie - Специальный класс для завтраков
class BreakfastItem(MenuItem):
    """
    📋 CHECK: Dziedziczenie - BreakfastItem для завтраков McDonald's
    Специальный класс для завтраков McDonald's (доступны до 10:30)
    """

    # ✅ WYMAGANIE: Nadpisywanie atrybutów
    default_preparation_time = 7  # Завтраки готовятся дольше
    category_name = "McDonald's Breakfast"

    def __init__(self, name: str, base_price: float, has_egg: bool = False,
                 has_sausage: bool = False, ingredients: List[str] = None):
        # ✅ WYMAGANIE: super()
        super().__init__(name, base_price, MenuCategory.BREAKFAST, ingredients)

        # 🔄 TRANSFER: MenuItem.__init__ → BreakfastItem.__init__
        log_transfer("MenuItem.__init__", "BreakfastItem.__init__", "breakfast attributes")

        self.has_egg = has_egg
        self.has_sausage = has_sausage
        self._preparation_time = self.default_preparation_time

        log_requirement_check("Inheritance", "SUCCESS", f"BreakfastItem extends MenuItem: {name}")

    # ✅ WYMAGANIE: Nadpisywanie metод
    def get_final_price(self, size: ItemSize = ItemSize.MEDIUM) -> float:
        """Расчет цены завтрака"""
        final_price = self.base_price

        # Дополнительная плата за яйцо и колбасу
        if self.has_egg:
            final_price += 1.00
        if self.has_sausage:
            final_price += 1.50

        return final_price

    def get_preparation_time(self) -> int:
        """Время приготовления завтрака"""
        return self._preparation_time

    @property
    def available(self) -> bool:
        """
        📋 CHECK: Enkapsulacja - переопределенное свойство с бизнес-логикой
        Завтраки доступны только до 10:30
        """
        if not self.is_breakfast_time():
            return False
        return self._available

    @available.setter
    def available(self, value: bool):
        """Сеттер учитывающий время завтрака"""
        if value and not self.is_breakfast_time():
            log_business_rule("Breakfast Availability", f"{self.name}: Not breakfast time, forcing unavailable")
            self._available = False
        else:
            self._available = bool(value)


# Функция для демонстрации всех возможностей меню
def demo_menu_system():
    """
    📋 CHECK: Полная демонстрация системы меню McDonald's
    Демонстрация всех классов меню и их возможностей
    """

    print("🍟 McDONALD'S MENU SYSTEM DEMO")
    print("=" * 50)

    # 🔄 TRANSFER: demo → menu classes (создание объектов)
    log_transfer("demo_menu_system", "MenuItem classes", "menu item creation")

    # 1. ✅ WYMAGANIE: @classmethod - Factory methods
    print("\n1. FACTORY METHODS (@classmethod)")
    print("-" * 30)

    big_mac = MenuItem.create_big_mac()
    happy_meal = MenuItem.create_happy_meal("Chicken McNuggets", "Milk", "Pokemon Card")

    print(f"Created: {big_mac}")
    print(f"Created: {happy_meal}")

    # 2. ✅ WYMAGANIE: Dziedziczenie + Nadpisywanie
    print("\n2. INHERITANCE & METHOD OVERRIDING")
    print("-" * 30)

    # Создание бургера
    quarter_pounder = Burger("Quarter Pounder", 5.49, patty_count=1, has_cheese=True)
    quarter_pounder.make_signature()

    # Создание фри
    large_fries = Fries(ItemSize.LARGE, "salt")

    # Создание напитков
    coke = Drink.create_coca_cola(ItemSize.LARGE)
    coffee = Drink.create_mccafe_coffee("Cappuccino", ItemSize.MEDIUM)

    # Создание завтрака
    egg_mcmuffin = BreakfastItem("Egg McMuffin", 3.99, has_egg=True, has_sausage=True)

    menu_items = [quarter_pounder, large_fries, coke, coffee, egg_mcmuffin]

    for item in menu_items:
        print(f"📱 {item}")
        print(f"   Final Price: ${item.get_final_price():.2f}")
        print(f"   Prep Time: {item.get_preparation_time()} minutes")
        print(f"   Available: {item.available}")

    # 3. ✅ WYMAGANIE: @staticmethod
    print("\n3. STATIC METHODS (@staticmethod)")
    print("-" * 30)

    base_calories = 550
    for size in ItemSize:
        calories = MenuItem.calculate_calories_with_size(base_calories, size)
        print(f"Big Mac {size.value}: {calories} calories")

    # 4. ✅ WYMAGANIE: Enkapsulacja - Property usage
    print("\n4. ENCAPSULATION (Property)")
    print("-" * 30)

    print(f"Quarter Pounder original price: ${quarter_pounder.base_price:.2f}")
    quarter_pounder.base_price = 6.99  # Используем setter
    print(f"Quarter Pounder new price: ${quarter_pounder.base_price:.2f}")

    # 5. Счетчики классов
    print("\n5. CLASS ATTRIBUTES")
    print("-" * 30)
    print(f"Total menu items created: {MenuItem.get_total_items_created()}")
    print(f"Available categories: {[cat.value for cat in MenuItem.available_categories]}")

    # 📋 CHECK: Финальная проверка всех требований
    log_requirement_check("Menu System Demo", "COMPLETED", "menu.py")

    return menu_items


if __name__ == "__main__":
    demo_menu_system()