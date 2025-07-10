"""
McDonald's Management System - Order Service
✅ WYMAGANIE: Serwisy - warstwa biznesowa do zarządzania zamówieniami
✅ WYMAGANIE: Integracja wszystkich wzorców i komponentów

Сервис управления заказами McDonald's
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import sys
import os

# Добавляем пути для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils.logger import log_transfer, log_requirement_check, log_operation, log_business_rule
from src.exceptions.mcdonalds_exceptions import *
from src.models.order import Order, OrderStatus, OrderType
from src.models.payment import Payment, PaymentStatus
from src.models.customer import Customer, CustomerType
from src.models.menu import MenuItem
from src.patterns.factory import OrderFactoryManager, OrderFactory
from src.patterns.strategy import DiscountManager, DiscountStrategy
from src.patterns.observer import OrderTracker, OrderObserver, NotificationType


class OrderServiceError(McDonaldsException):
    """Исключения сервиса заказов"""
    pass


class OrderPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


class OrderValidationResult:
    """Результат валидации заказа"""

    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []

    def add_error(self, error: str):
        """Добавляет ошибку валидации"""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str):
        """Добавляет предупреждение валидации"""
        self.warnings.append(warning)


class OrderService:
    """
    📋 CHECK: Serwisy - Основной сервис управления заказами
    ✅ WYMAGANIE: Integracja wzorców - использует Factory, Strategy, Observer

    Сервис для управления жизненным циклом заказов McDonald's
    """

    def __init__(self, restaurant_id: str):
        self.restaurant_id = restaurant_id

        # Интеграция с паттернами
        self._factory_manager: Optional[OrderFactoryManager] = None
        self._discount_manager: Optional[DiscountManager] = None
        self._order_tracker: Optional[OrderTracker] = None

        # Хранилища данных
        self._active_orders: Dict[str, Order] = {}
        self._completed_orders: List[Order] = []
        self._order_queue: List[str] = []  # Order IDs по приоритету
        self._order_history: List[Dict[str, Any]] = []

        # Конфигурация сервиса
        self._max_active_orders = 50
        self._order_timeout_minutes = 30
        self._priority_weights = {
            OrderPriority.CRITICAL: 5,
            OrderPriority.URGENT: 4,
            OrderPriority.HIGH: 3,
            OrderPriority.NORMAL: 2,
            OrderPriority.LOW: 1
        }

        # Статистика
        self._orders_processed_today = 0
        self._total_revenue_today = 0.0
        self._service_metrics = {
            "average_preparation_time": 0.0,
            "customer_satisfaction": 4.5,
            "order_accuracy": 98.5
        }

        # 📋 CHECK: Serwisy - сервис создан
        log_requirement_check("Service Layer", "CREATED", f"OrderService: {restaurant_id}")

        # 🔄 TRANSFER: order_service.py → logger (service initialization)
        log_transfer("OrderService", "system initialization", "order service setup")

    # ===== КОНФИГУРАЦИЯ И ИНТЕГРАЦИЯ =====

    def configure_factory_manager(self, factory_manager: OrderFactoryManager):
        """
        📋 CHECK: Integracja wzorców - подключение Factory Manager
        """
        self._factory_manager = factory_manager
        log_business_rule("Factory Integration", f"OrderService connected to {factory_manager.restaurant_id}")
        log_requirement_check("Pattern Integration", "FACTORY_CONNECTED", "OrderService ↔ Factory")

    def configure_discount_manager(self, discount_manager: DiscountManager):
        """
        📋 CHECK: Integracja wzorców - подключение Discount Manager (Strategy)
        """
        self._discount_manager = discount_manager
        log_business_rule("Strategy Integration", "OrderService connected to DiscountManager")
        log_requirement_check("Pattern Integration", "STRATEGY_CONNECTED", "OrderService ↔ Strategy")

    def configure_order_tracker(self, order_tracker: OrderTracker):
        """
        📋 CHECK: Integracja wzorców - подключение Order Tracker (Observer)
        """
        self._order_tracker = order_tracker
        log_business_rule("Observer Integration", "OrderService connected to OrderTracker")
        log_requirement_check("Pattern Integration", "OBSERVER_CONNECTED", "OrderService ↔ Observer")

    # ===== СОЗДАНИЕ И ВАЛИДАЦИЯ ЗАКАЗОВ =====

    def create_order(self, order_type: OrderType, customer_id: str = "",
                     menu_items: List[Dict[str, Any]] = None, **kwargs) -> Order:
        """
        📋 CHECK: Serwisy - главный метод создания заказа
        Создает новый заказ используя Factory Method
        """
        # 🔄 TRANSFER: OrderService → Factory Manager (order creation request)
        log_transfer("OrderService", "OrderFactoryManager", f"create {order_type.value} order")

        # Проверяем ограничения
        if len(self._active_orders) >= self._max_active_orders:
            raise OrderServiceError("Maximum active orders limit reached", "ORDER_LIMIT_EXCEEDED")

        if not self._factory_manager:
            raise OrderServiceError("Factory manager not configured", "FACTORY_NOT_CONFIGURED")

        # Создаем заказ через Factory Manager
        order = self._factory_manager.create_order(order_type, customer_id, **kwargs)

        # Добавляем позиции меню если указаны
        if menu_items:
            for item_data in menu_items:
                self._add_menu_item_to_order(order, item_data)

        # Валидируем заказ
        validation_result = self.validate_order(order)
        if not validation_result.is_valid:
            raise OrderServiceError(f"Order validation failed: {validation_result.errors}", "VALIDATION_FAILED")

        # Рассчитываем скидки если есть Discount Manager
        if self._discount_manager and customer_id:
            self._apply_discounts_to_order(order, customer_id)

        # Добавляем в активные заказы
        self._active_orders[order.order_id] = order

        # Добавляем в очередь по приоритету
        priority = self._calculate_order_priority(order, kwargs.get('customer_data', {}))
        self._add_to_priority_queue(order.order_id, priority)

        # Уведомляем через Observer
        if self._order_tracker:
            order_data = self._prepare_order_data_for_notification(order)
            self._order_tracker.track_order(order.order_id, order_data)

        # Логируем создание
        log_business_rule("Order Created",
                          f"Service created {order_type.value} order {order.order_id}")

        return order

    def validate_order(self, order: Order) -> OrderValidationResult:
        """
        📋 CHECK: Walidacja - валидация заказа
        Комплексная валидация заказа
        """
        result = OrderValidationResult(True)

        # Базовая валидация
        if not order.order_id:
            result.add_error("Order ID is required")

        if order.items_count == 0:
            result.add_error("Order must contain at least one item")

        if order.total_amount <= 0:
            result.add_error("Order total must be positive")

        # Валидация по типу заказа
        try:
            order.validate_order()
        except Exception as e:
            result.add_error(f"Order type validation failed: {str(e)}")

        # Проверка времени для завтраков
        if hasattr(order, '_items'):
            breakfast_items = [item for item in order.get_items_list()
                               if 'breakfast' in item.get('name', '').lower()]
            if breakfast_items and not self._is_breakfast_time():
                result.add_warning("Breakfast items may not be available outside breakfast hours")

        # Проверка лимитов заказа
        if order.items_count > 20:
            result.add_warning("Large order may require additional preparation time")

        if order.total_amount > 100.0:
            result.add_warning("High-value order may require manager approval")

        log_business_rule("Order Validation",
                          f"Order {order.order_id}: {'VALID' if result.is_valid else 'INVALID'}")

        return result

    def _add_menu_item_to_order(self, order: Order, item_data: Dict[str, Any]):
        """Добавляет позицию меню к заказу"""
        item_name = item_data.get('name', '')
        quantity = item_data.get('quantity', 1)
        price = item_data.get('price', 0.0)
        customizations = item_data.get('customizations', [])

        order.add_item(item_name, quantity, price, customizations)

        log_business_rule("Item Added",
                          f"Order {order.order_id}: {quantity}x {item_name}")

    def _apply_discounts_to_order(self, order: Order, customer_id: str):
        """Применяет скидки к заказу используя Strategy pattern"""
        if not self._discount_manager:
            return

        # 🔄 TRANSFER: OrderService → DiscountManager (discount calculation)
        log_transfer("OrderService", "DiscountManager", f"discount calculation for {order.order_id}")

        # Получаем данные клиента (в реальном приложении из базы данных)
        customer_data = self._get_customer_data(customer_id)

        # Рассчитываем лучшую скидку
        order_items = order.get_items_list()
        discount_result = self._discount_manager.calculate_best_discount(
            order.total_amount, order_items, customer_data
        )

        if discount_result.get("applicable", False):
            discount_amount = discount_result["discount_amount"]
            order.apply_discount(discount_amount, discount_result["reason"])

            log_business_rule("Discount Applied",
                              f"Order {order.order_id}: ${discount_amount:.2f} discount via {discount_result['strategy_name']}")

    # ===== УПРАВЛЕНИЕ ЖИЗНЕННЫМ ЦИКЛОМ ЗАКАЗА =====

    def update_order_status(self, order_id: str, new_status: OrderStatus,
                            additional_data: Dict[str, Any] = None) -> bool:
        """
        📋 CHECK: Serwisy - обновление статуса заказа
        Обновляет статус заказа и уведомляет наблюдателей
        """
        if order_id not in self._active_orders:
            log_business_rule("Status Update Failed", f"Order {order_id} not found")
            return False

        order = self._active_orders[order_id]
        old_status = order.status

        # Обновляем статус
        order.status = new_status

        # Уведомляем через Observer
        if self._order_tracker:
            self._order_tracker.update_order_status(order_id, new_status.value, additional_data)

        # Обрабатываем особые статусы
        if new_status == OrderStatus.COMPLETED:
            self._complete_order(order_id)
        elif new_status == OrderStatus.CANCELLED:
            self._cancel_order(order_id)

        log_business_rule("Order Status Updated",
                          f"Order {order_id}: {old_status.value} → {new_status.value}")

        return True

    def process_payment(self, order_id: str, payment: Payment) -> bool:
        """
        📋 CHECK: Serwisy - обработка платежа
        📋 CHECK: Polimorfizm - полиморфная обработка разных типов платежей
        """
        if order_id not in self._active_orders:
            raise OrderServiceError(f"Order {order_id} not found", "ORDER_NOT_FOUND")

        order = self._active_orders[order_id]

        # 🔄 TRANSFER: OrderService → Payment (polymorphic processing)
        log_transfer("OrderService", "Payment", f"process payment for {order_id}")

        # Проверяем сумму платежа
        if payment.amount < order.total_amount:
            raise PaymentProcessingException(
                payment.get_payment_method().value,
                payment.amount,
                f"Insufficient payment: need ${order.total_amount:.2f}, got ${payment.amount:.2f}"
            )

        try:
            # Полиморфно обрабатываем платеж
            success = payment.process_payment()

            if success:
                order.payment_status = PaymentStatus.COMPLETED
                order.status = OrderStatus.CONFIRMED

                # Обновляем статистику
                self._total_revenue_today += payment.net_amount

                # Уведомляем через Observer
                if self._order_tracker:
                    self._order_tracker.notify(
                        NotificationType.PAYMENT_PROCESSED,
                        {
                            "order_id": order_id,
                            "payment_method": payment.get_payment_method().value,
                            "amount": payment.amount
                        }
                    )

                log_business_rule("Payment Processed",
                                  f"Order {order_id}: {payment.get_payment_method().value} ${payment.amount:.2f}")

                return True
            else:
                order.payment_status = PaymentStatus.FAILED
                return False

        except Exception as e:
            order.payment_status = PaymentStatus.FAILED
            log_business_rule("Payment Failed", f"Order {order_id}: {str(e)}")
            raise

    def _complete_order(self, order_id: str):
        """Завершает заказ"""
        if order_id in self._active_orders:
            order = self._active_orders[order_id]

            # Перемещаем в завершенные
            self._completed_orders.append(order)
            del self._active_orders[order_id]

            # Убираем из очереди
            if order_id in self._order_queue:
                self._order_queue.remove(order_id)

            # Обновляем статистику
            self._orders_processed_today += 1

            # Завершаем отслеживание
            if self._order_tracker:
                self._order_tracker.complete_order_tracking(order_id)

            log_business_rule("Order Completed", f"Order {order_id} moved to completed")

    def _cancel_order(self, order_id: str):
        """Отменяет заказ"""
        if order_id in self._active_orders:
            order = self._active_orders[order_id]

            # Если платеж был обработан, может потребоваться возврат
            if order.payment_status == PaymentStatus.COMPLETED:
                log_business_rule("Refund Required", f"Order {order_id} cancellation may require refund")

            # Убираем из активных и очереди
            del self._active_orders[order_id]
            if order_id in self._order_queue:
                self._order_queue.remove(order_id)

            log_business_rule("Order Cancelled", f"Order {order_id} cancelled")

    # ===== УПРАВЛЕНИЕ ОЧЕРЕДЬЮ И ПРИОРИТЕТАМИ =====

    def _calculate_order_priority(self, order: Order, customer_data: Dict[str, Any]) -> OrderPriority:
        """Рассчитывает приоритет заказа"""
        priority = OrderPriority.NORMAL

        # VIP клиенты
        customer_type = customer_data.get('customer_type', '')
        if customer_type == CustomerType.VIP.value:
            priority = OrderPriority.URGENT
        elif customer_type == CustomerType.LOYALTY_MEMBER.value:
            priority = OrderPriority.HIGH

        # Тип заказа
        if order.get_order_type() == OrderType.DELIVERY:
            if priority.value < OrderPriority.HIGH.value:
                priority = OrderPriority.HIGH

        # Размер заказа
        if order.items_count > 10:
            if priority.value < OrderPriority.HIGH.value:
                priority = OrderPriority.HIGH

        # Время ожидания
        creation_time = getattr(order, '_order_time', datetime.now())
        wait_time = datetime.now() - creation_time
        if wait_time > timedelta(minutes=15):
            priority = OrderPriority.URGENT

        return priority

    def _add_to_priority_queue(self, order_id: str, priority: OrderPriority):
        """Добавляет заказ в очередь по приоритету"""
        # Находим правильную позицию для вставки
        insert_position = len(self._order_queue)

        for i, existing_order_id in enumerate(self._order_queue):
            existing_order = self._active_orders.get(existing_order_id)
            if existing_order:
                existing_priority = self._calculate_order_priority(existing_order, {})
                if priority.value > existing_priority.value:
                    insert_position = i
                    break

        self._order_queue.insert(insert_position, order_id)

        log_business_rule("Queue Updated",
                          f"Order {order_id} added to queue at position {insert_position + 1} ({priority.name})")

    def get_next_order_for_preparation(self) -> Optional[Order]:
        """Возвращает следующий заказ для приготовления"""
        if not self._order_queue:
            return None

        # Берем заказ с наивысшим приоритетом
        next_order_id = self._order_queue[0]
        if next_order_id in self._active_orders:
            order = self._active_orders[next_order_id]

            # Обновляем статус на "в приготовлении"
            if order.status == OrderStatus.CONFIRMED:
                self.update_order_status(next_order_id, OrderStatus.IN_PREPARATION)
                self._order_queue.remove(next_order_id)

                log_business_rule("Order Started", f"Order {next_order_id} started preparation")
                return order

        return None

    # ===== АНАЛИТИКА И ОТЧЕТЫ =====

    def get_service_statistics(self) -> Dict[str, Any]:
        """
        📋 CHECK: Serwisy - статистика сервиса
        Возвращает подробную статистику сервиса
        """
        # Статистика по заказам
        active_by_status = {}
        active_by_type = {}

        for order in self._active_orders.values():
            status = order.status.value
            order_type = order.get_order_type().value

            active_by_status[status] = active_by_status.get(status, 0) + 1
            active_by_type[order_type] = active_by_type.get(order_type, 0) + 1

        # Средние показатели
        total_orders = len(self._completed_orders)
        avg_order_value = self._total_revenue_today / max(total_orders, 1)

        return {
            "restaurant_id": self.restaurant_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "active_orders": {
                "total": len(self._active_orders),
                "by_status": active_by_status,
                "by_type": active_by_type,
                "queue_length": len(self._order_queue)
            },
            "completed_orders": {
                "total": len(self._completed_orders),
                "today": self._orders_processed_today
            },
            "financial": {
                "total_revenue_today": self._total_revenue_today,
                "average_order_value": avg_order_value,
                "orders_processed": self._orders_processed_today
            },
            "performance": {
                "service_metrics": self._service_metrics,
                "max_active_orders": self._max_active_orders,
                "order_timeout_minutes": self._order_timeout_minutes
            },
            "integrations": {
                "factory_manager_connected": self._factory_manager is not None,
                "discount_manager_connected": self._discount_manager is not None,
                "order_tracker_connected": self._order_tracker is not None
            }
        }

    def generate_hourly_report(self) -> Dict[str, Any]:
        """Генерирует почасовой отчет"""
        current_hour = datetime.now().hour

        # В реальном приложении данные брались бы из базы данных
        hourly_data = {
            "hour": current_hour,
            "orders_created": len(self._active_orders) + len(self._completed_orders),
            "orders_completed": len(self._completed_orders),
            "revenue": self._total_revenue_today,
            "average_prep_time": self._service_metrics["average_preparation_time"],
            "customer_satisfaction": self._service_metrics["customer_satisfaction"]
        }

        return hourly_data

    # ===== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ =====

    def _get_customer_data(self, customer_id: str) -> Dict[str, Any]:
        """Получает данные клиента (заглушка)"""
        # В реальном приложении данные брались бы из базы данных клиентов
        return {
            "customer_id": customer_id,
            "customer_type": "regular",
            "loyalty_tier": "bronze"
        }

    def _prepare_order_data_for_notification(self, order: Order) -> Dict[str, Any]:
        """Подготавливает данные заказа для уведомлений"""
        return {
            "customer_id": order.customer_id,
            "order_type": order.get_order_type().value,
            "total_amount": order.total_amount,
            "items_count": order.items_count,
            "estimated_prep_time": order.estimated_prep_time,
            "special_instructions": order.special_instructions
        }

    def _is_breakfast_time(self) -> bool:
        """Проверяет время завтрака"""
        current_time = datetime.now().time()
        breakfast_end = datetime.strptime("10:30", "%H:%M").time()
        return current_time <= breakfast_end

    # ===== ОПЕРАЦИИ УПРАВЛЕНИЯ =====

    def cancel_order(self, order_id: str, reason: str = "") -> bool:
        """Отменяет заказ"""
        if order_id not in self._active_orders:
            return False

        self.update_order_status(order_id, OrderStatus.CANCELLED, {"reason": reason})
        return True

    def mark_order_ready(self, order_id: str) -> bool:
        """Отмечает заказ готовым"""
        if order_id not in self._active_orders:
            return False

        self.update_order_status(order_id, OrderStatus.READY, {"ready_time": datetime.now()})
        return True

    def get_order_by_id(self, order_id: str) -> Optional[Order]:
        """Получает заказ по ID"""
        return self._active_orders.get(order_id)

    def get_orders_by_status(self, status: OrderStatus) -> List[Order]:
        """Получает заказы по статусу"""
        return [order for order in self._active_orders.values() if order.status == status]

    def get_orders_by_type(self, order_type: OrderType) -> List[Order]:
        """Получает заказы по типу"""
        return [order for order in self._active_orders.values()
                if order.get_order_type() == order_type]

    def cleanup_expired_orders(self):
        """Очищает просроченные заказы"""
        current_time = datetime.now()
        expired_orders = []

        for order_id, order in self._active_orders.items():
            order_time = getattr(order, '_order_time', current_time)
            if current_time - order_time > timedelta(minutes=self._order_timeout_minutes):
                expired_orders.append(order_id)

        for order_id in expired_orders:
            self.cancel_order(order_id, "Order timeout")
            log_business_rule("Order Expired", f"Order {order_id} cancelled due to timeout")

        return len(expired_orders)


# Демонстрация работы сервиса
def demo_order_service():
    """
    📋 CHECK: Полная демонстрация сервиса управления заказами
    """

    print("🎛️ McDONALD'S ORDER SERVICE DEMO")
    print("=" * 50)

    # 🔄 TRANSFER: demo → order service
    log_transfer("demo_order_service", "OrderService", "service demonstration")

    # 1. Создание сервиса
    print("\n1. ORDER SERVICE CREATION")
    print("-" * 30)

    order_service = OrderService("MCD0001")
    print(f"Created OrderService for restaurant: {order_service.restaurant_id}")

    # 2. Конфигурация интеграций (заглушки)
    print("\n2. SERVICE INTEGRATION")
    print("-" * 30)

    # Создаем заглушки для демонстрации
    from src.patterns.factory import OrderFactoryManager, DineInOrderFactory, DriveThruOrderFactory
    from src.patterns.strategy import DiscountManager, PercentageDiscountStrategy
    from src.patterns.observer import OrderTracker

    # Factory Manager
    factory_manager = OrderFactoryManager("MCD0001")
    dine_in_factory = DineInOrderFactory("DINEIN_001", "MCD0001")
    drive_thru_factory = DriveThruOrderFactory("DRIVETHRU_001", "MCD0001")

    factory_manager.register_factory(OrderType.DINE_IN, dine_in_factory)
    factory_manager.register_factory(OrderType.DRIVE_THRU, drive_thru_factory)

    order_service.configure_factory_manager(factory_manager)
    print("✅ Factory Manager configured")

    # Discount Manager
    discount_manager = DiscountManager()
    student_discount = PercentageDiscountStrategy("Student Discount", 15.0, min_order_amount=10.0)
    discount_manager.add_strategy(student_discount)

    order_service.configure_discount_manager(discount_manager)
    print("✅ Discount Manager configured")

    # Order Tracker
    order_tracker = OrderTracker("MCD0001")
    order_service.configure_order_tracker(order_tracker)
    print("✅ Order Tracker configured")

    # 3. Создание заказов
    print("\n3. ORDER CREATION")
    print("-" * 30)

    # Простой Dine-In заказ
    menu_items1 = [
        {"name": "Big Mac", "quantity": 1, "price": 4.99},
        {"name": "French Fries", "quantity": 1, "price": 2.49},
        {"name": "Coca-Cola", "quantity": 1, "price": 1.79}
    ]

    order1 = order_service.create_order(
        OrderType.DINE_IN,
        customer_id="CUST001",
        menu_items=menu_items1,
        party_size=2,
        customer_data={"customer_type": "student"}
    )
    print(f"Created dine-in order: {order1.order_id} (${order1.total_amount:.2f})")

    # Drive-Thru заказ
    menu_items2 = [
        {"name": "Quarter Pounder", "quantity": 1, "price": 5.49},
        {"name": "Large Fries", "quantity": 1, "price": 2.99}
    ]

    order2 = order_service.create_order(
        OrderType.DRIVE_THRU,
        customer_id="CUST002",
        menu_items=menu_items2,
        vehicle_type="car",
        customer_data={"customer_type": "vip"}
    )
    print(f"Created drive-thru order: {order2.order_id} (${order2.total_amount:.2f})")

    # 4. Обработка платежей
    print("\n4. PAYMENT PROCESSING")
    print("-" * 30)

    from src.models.payment import CashPayment, CardPayment

    # Платеж за первый заказ
    payment1 = CashPayment.create_exact_change(order1.total_amount)
    success1 = order_service.process_payment(order1.order_id, payment1)
    print(f"Payment for {order1.order_id}: {'SUCCESS' if success1 else 'FAILED'}")

    # Платеж за второй заказ
    payment2 = CardPayment.create_contactless_payment(order2.total_amount, "TOKEN123")
    success2 = order_service.process_payment(order2.order_id, payment2)
    print(f"Payment for {order2.order_id}: {'SUCCESS' if success2 else 'FAILED'}")

    # 5. Управление очередью
    print("\n5. ORDER QUEUE MANAGEMENT")
    print("-" * 30)

    # Получаем следующий заказ для приготовления
    next_order = order_service.get_next_order_for_preparation()
    if next_order:
        print(f"Next order for preparation: {next_order.order_id}")

        # Симулируем приготовление
        order_service.mark_order_ready(next_order.order_id)
        print(f"Order {next_order.order_id} marked as ready")

        # Завершаем заказ
        order_service.update_order_status(next_order.order_id, OrderStatus.COMPLETED)
        print(f"Order {next_order.order_id} completed")

    # 6. Статистика сервиса
    print("\n6. SERVICE STATISTICS")
    print("-" * 30)

    stats = order_service.get_service_statistics()
    print(f"Restaurant: {stats['restaurant_id']}")
    print(f"Active orders: {stats['active_orders']['total']}")
    print(f"Completed orders: {stats['completed_orders']['total']}")
    print(f"Total revenue today: ${stats['financial']['total_revenue_today']:.2f}")
    print(f"Average order value: ${stats['financial']['average_order_value']:.2f}")

    print("\nIntegrations:")
    for integration, connected in stats['integrations'].items():
        status = "✅ Connected" if connected else "❌ Not connected"
        print(f"  {integration}: {status}")

    # 7. Почасовой отчет
    print("\n7. HOURLY REPORT")
    print("-" * 30)

    hourly_report = order_service.generate_hourly_report()
    print(f"Hour: {hourly_report['hour']}:00")
    print(f"Orders created: {hourly_report['orders_created']}")
    print(f"Orders completed: {hourly_report['orders_completed']}")
    print(f"Revenue: ${hourly_report['revenue']:.2f}")
    print(f"Customer satisfaction: {hourly_report['customer_satisfaction']:.1f}/5.0")

    # 📋 CHECK: Финальная проверка сервиса
    log_requirement_check("Order Service Demo", "COMPLETED", "order_service.py")

    return order_service


if __name__ == "__main__":
    demo_order_service()