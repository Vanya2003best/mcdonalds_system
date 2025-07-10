"""
McDonald's Management System - Observer Pattern
✅ WYMAGANIE: Wzorzec Observer - powiadomienia o zamówieniach
✅ WYMAGANIE: Polimorfizm poprzez różnych obserwatorów

Паттерн Observer для системы уведомлений McDonald's
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set
from enum import Enum
import sys
import os

# Добавляем пути для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils.logger import log_transfer, log_requirement_check, log_operation, log_business_rule


class NotificationType(Enum):
    ORDER_CREATED = "order_created"
    ORDER_CONFIRMED = "order_confirmed"
    ORDER_IN_PREPARATION = "order_in_preparation"
    ORDER_READY = "order_ready"
    ORDER_COMPLETED = "order_completed"
    ORDER_CANCELLED = "order_cancelled"
    PAYMENT_PROCESSED = "payment_processed"
    PAYMENT_FAILED = "payment_failed"
    KITCHEN_ALERT = "kitchen_alert"
    DRIVE_THRU_ALERT = "drive_thru_alert"
    CUSTOMER_ARRIVAL = "customer_arrival"
    STAFF_ALERT = "staff_alert"


class NotificationPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class NotificationChannel(Enum):
    MOBILE_APP = "mobile_app"
    SMS = "sms"
    EMAIL = "email"
    KITCHEN_DISPLAY = "kitchen_display"
    POS_SYSTEM = "pos_system"
    DRIVE_THRU_SPEAKER = "drive_thru_speaker"
    STAFF_PAGER = "staff_pager"
    DIGITAL_BOARD = "digital_board"


# ✅ WYMAGANIE: Wzorzec Observer - Интерфейс Subject (наблюдаемый объект)
class OrderNotificationSubject(ABC):
    """
    📋 CHECK: Observer Pattern - Subject interface
    ✅ WYMAGANIE: Wzorzec Observer - интерфейс для наблюдаемых объектов
    """

    def __init__(self):
        self._observers: Set['OrderObserver'] = set()
        self._notification_history: List[Dict[str, Any]] = []

        # 📋 CHECK: Observer Pattern - Subject создан
        log_requirement_check("Observer Pattern Subject", "CREATED", self.__class__.__name__)

    @abstractmethod
    def attach(self, observer: 'OrderObserver'):
        """
        📋 CHECK: Observer Pattern - Attach method
        Подписывает наблюдателя на уведомления
        """
        pass

    @abstractmethod
    def detach(self, observer: 'OrderObserver'):
        """
        📋 CHECK: Observer Pattern - Detach method
        Отписывает наблюдателя от уведомлений
        """
        pass

    @abstractmethod
    def notify(self, notification_type: NotificationType, data: Dict[str, Any]):
        """
        📋 CHECK: Observer Pattern - Notify method
        Уведомляет всех наблюдателей о событии
        """
        pass


# ✅ WYMAGANIE: Wzorzec Observer - Интерфейс Observer (наблюдатель)
class OrderObserver(ABC):
    """
    📋 CHECK: Observer Pattern - Observer interface
    ✅ WYMAGANIE: Wzorzec Observer - интерфейс для наблюдателей
    """

    def __init__(self, observer_id: str, name: str):
        self.observer_id = observer_id
        self.name = name
        self._is_active = True
        self._notification_count = 0
        self._last_notification_time: Optional[datetime] = None

        # 📋 CHECK: Observer Pattern - Observer создан
        log_requirement_check("Observer Pattern Observer", "CREATED", f"{name} ({observer_id})")

    @abstractmethod
    def update(self, subject: OrderNotificationSubject, notification_type: NotificationType,
               data: Dict[str, Any]):
        """
        📋 CHECK: Observer Pattern - Update method
        ✅ WYMAGANIE: Wzorzec Observer - метод обновления для получения уведомлений
        """
        pass

    @abstractmethod
    def get_notification_channels(self) -> List[NotificationChannel]:
        """Возвращает каналы уведомлений для наблюдателя"""
        pass

    def is_interested_in(self, notification_type: NotificationType, data: Dict[str, Any]) -> bool:
        """Проверяет заинтересован ли наблюдатель в данном типе уведомления"""
        return True  # По умолчанию заинтересован во всех

    def set_active(self, active: bool):
        """Активирует/деактивирует наблюдателя"""
        self._is_active = active
        status = "ACTIVE" if active else "INACTIVE"
        log_business_rule("Observer Status", f"{self.name}: {status}")

    def get_stats(self) -> Dict[str, Any]:
        """Возвращает статистику наблюдателя"""
        return {
            "observer_id": self.observer_id,
            "name": self.name,
            "is_active": self._is_active,
            "notification_count": self._notification_count,
            "last_notification": self._last_notification_time.isoformat() if self._last_notification_time else None
        }


# ✅ WYMAGANIE: Wzorzec Observer - Конкретная реализация Subject
class OrderTracker(OrderNotificationSubject):
    """
    📋 CHECK: Observer Pattern - Concrete Subject
    Конкретная реализация Subject для отслеживания заказов
    """

    def __init__(self, restaurant_id: str):
        super().__init__()

        # 🔄 TRANSFER: OrderNotificationSubject.__init__ → OrderTracker.__init__
        log_transfer("OrderNotificationSubject.__init__", "OrderTracker.__init__",
                     "order tracking attributes")

        self.restaurant_id = restaurant_id
        self._active_orders: Dict[str, Dict[str, Any]] = {}
        self._notification_queue: List[Dict[str, Any]] = []
        self._auto_notify_enabled = True

        log_requirement_check("Observer Inheritance", "SUCCESS",
                              f"OrderTracker extends OrderNotificationSubject")

    def attach(self, observer: OrderObserver):
        """
        📋 CHECK: Observer Pattern - Attach implementation
        Подписывает наблюдателя
        """
        self._observers.add(observer)
        log_business_rule("Observer Attached",
                          f"{observer.name} subscribed to {self.restaurant_id}")

        # Уведомляем о подписке
        self._add_to_history("observer_attached", {
            "observer_id": observer.observer_id,
            "observer_name": observer.name,
            "channels": [ch.value for ch in observer.get_notification_channels()]
        })

    def detach(self, observer: OrderObserver):
        """
        📋 CHECK: Observer Pattern - Detach implementation
        Отписывает наблюдателя
        """
        self._observers.discard(observer)
        log_business_rule("Observer Detached",
                          f"{observer.name} unsubscribed from {self.restaurant_id}")

        self._add_to_history("observer_detached", {
            "observer_id": observer.observer_id,
            "observer_name": observer.name
        })

    def notify(self, notification_type: NotificationType, data: Dict[str, Any]):
        """
        📋 CHECK: Observer Pattern - Notify implementation
        Уведомляет всех подписанных наблюдателей
        """
        # 🔄 TRANSFER: OrderTracker → observers (notification broadcast)
        log_transfer("OrderTracker", "OrderObserver instances", f"notification: {notification_type.value}")

        if not self._auto_notify_enabled:
            self._queue_notification(notification_type, data)
            return

        notification_data = {
            "type": notification_type,
            "data": data,
            "timestamp": datetime.now(),
            "restaurant_id": self.restaurant_id,
            "notification_id": f"NOT{len(self._notification_history) + 1:06d}"
        }

        # Уведомляем всех активных наблюдателей
        notified_count = 0
        for observer in self._observers:
            if observer._is_active and observer.is_interested_in(notification_type, data):
                try:
                    observer.update(self, notification_type, notification_data)
                    observer._notification_count += 1
                    observer._last_notification_time = datetime.now()
                    notified_count += 1
                except Exception as e:
                    log_business_rule("Notification Failed",
                                      f"Failed to notify {observer.name}: {str(e)}")

        # Сохраняем в историю
        self._add_to_history(notification_type.value, {
            **data,
            "notified_observers": notified_count,
            "total_observers": len(self._observers)
        })

        log_business_rule("Notification Sent",
                          f"{notification_type.value}: notified {notified_count}/{len(self._observers)} observers")

        log_requirement_check("Observer Pattern", "EXECUTED", f"Notification: {notification_type.value}")

    def _queue_notification(self, notification_type: NotificationType, data: Dict[str, Any]):
        """Добавляет уведомление в очередь"""
        self._notification_queue.append({
            "type": notification_type,
            "data": data,
            "queued_at": datetime.now()
        })
        log_business_rule("Notification Queued", f"{notification_type.value} queued")

    def process_notification_queue(self):
        """Обрабатывает очередь уведомлений"""
        while self._notification_queue:
            notification = self._notification_queue.pop(0)
            self.notify(notification["type"], notification["data"])

    def _add_to_history(self, event_type: str, data: Dict[str, Any]):
        """Добавляет событие в историю"""
        self._notification_history.append({
            "timestamp": datetime.now(),
            "event_type": event_type,
            "data": data
        })

    # Методы для работы с заказами
    def track_order(self, order_id: str, order_data: Dict[str, Any]):
        """Начинает отслеживание заказа"""
        self._active_orders[order_id] = {
            **order_data,
            "tracked_since": datetime.now(),
            "status_changes": []
        }

        # Уведомляем о новом заказе
        self.notify(NotificationType.ORDER_CREATED, {
            "order_id": order_id,
            "customer_id": order_data.get("customer_id"),
            "order_type": order_data.get("order_type"),
            "total_amount": order_data.get("total_amount"),
            "items_count": order_data.get("items_count", 0)
        })

    def update_order_status(self, order_id: str, new_status: str, additional_data: Dict[str, Any] = None):
        """Обновляет статус заказа и уведомляет наблюдателей"""
        if order_id not in self._active_orders:
            log_business_rule("Order Update Failed", f"Order {order_id} not being tracked")
            return

        old_status = self._active_orders[order_id].get("status", "unknown")
        self._active_orders[order_id]["status"] = new_status
        self._active_orders[order_id]["status_changes"].append({
            "from": old_status,
            "to": new_status,
            "timestamp": datetime.now(),
            "data": additional_data or {}
        })

        # Определяем тип уведомления на основе статуса
        notification_type_mapping = {
            "confirmed": NotificationType.ORDER_CONFIRMED,
            "in_preparation": NotificationType.ORDER_IN_PREPARATION,
            "ready": NotificationType.ORDER_READY,
            "completed": NotificationType.ORDER_COMPLETED,
            "cancelled": NotificationType.ORDER_CANCELLED
        }

        notification_type = notification_type_mapping.get(new_status.lower(), NotificationType.ORDER_CONFIRMED)

        # Подготавливаем данные для уведомления
        notification_data = {
            "order_id": order_id,
            "old_status": old_status,
            "new_status": new_status,
            "customer_id": self._active_orders[order_id].get("customer_id"),
            "order_type": self._active_orders[order_id].get("order_type"),
            **(additional_data or {})
        }

        # Отправляем уведомление
        self.notify(notification_type, notification_data)

    def complete_order_tracking(self, order_id: str):
        """Завершает отслеживание заказа"""
        if order_id in self._active_orders:
            completed_order = self._active_orders.pop(order_id)
            log_business_rule("Order Tracking Completed", f"Stopped tracking {order_id}")

    def get_tracking_summary(self) -> Dict[str, Any]:
        """Возвращает сводку отслеживания"""
        return {
            "restaurant_id": self.restaurant_id,
            "active_orders": len(self._active_orders),
            "total_observers": len(self._observers),
            "active_observers": sum(1 for obs in self._observers if obs._is_active),
            "notifications_sent": len(self._notification_history),
            "queued_notifications": len(self._notification_queue)
        }


# ✅ WYMAGANIE: Dziedziczenie + Observer - Наблюдатель для кухни
class KitchenDisplayObserver(OrderObserver):
    """
    📋 CHECK: Observer Pattern - Kitchen display observer
    📋 CHECK: Dziedziczenie - KitchenDisplayObserver наследует от OrderObserver
    Наблюдатель для кухонного дисплея
    """

    def __init__(self, observer_id: str, station: str = "main_kitchen"):
        # ✅ WYMAGANIE: super() - вызов конструктора родителя
        super().__init__(observer_id, f"Kitchen Display ({station})")

        # 🔄 TRANSFER: OrderObserver.__init__ → KitchenDisplayObserver.__init__
        log_transfer("OrderObserver.__init__", "KitchenDisplayObserver.__init__",
                     "kitchen display attributes")

        self.station = station
        self._priority_orders: List[str] = []
        self._preparation_queue: List[Dict[str, Any]] = []
        self._display_capacity = 12  # Максимум заказов на экране

        log_requirement_check("Observer Inheritance", "SUCCESS",
                              f"KitchenDisplayObserver extends OrderObserver")

    def update(self, subject: OrderNotificationSubject, notification_type: NotificationType,
               data: Dict[str, Any]):
        """
        📋 CHECK: Observer Pattern - Kitchen display update implementation
        Обрабатывает уведомления для кухонного дисплея
        """
        order_id = data["data"].get("order_id")
        notification_data = data["data"]

        # Обрабатываем различные типы уведомлений
        if notification_type == NotificationType.ORDER_CONFIRMED:
            self._add_to_preparation_queue(order_id, notification_data)

        elif notification_type == NotificationType.ORDER_IN_PREPARATION:
            self._update_preparation_status(order_id, "preparing")

        elif notification_type == NotificationType.ORDER_READY:
            self._mark_order_ready(order_id)

        elif notification_type == NotificationType.ORDER_COMPLETED:
            self._remove_from_display(order_id)

        elif notification_type == NotificationType.KITCHEN_ALERT:
            self._handle_kitchen_alert(notification_data)

        # Логируем получение уведомления
        log_business_rule("Kitchen Display Updated",
                          f"Station {self.station}: {notification_type.value} for order {order_id}")

    def get_notification_channels(self) -> List[NotificationChannel]:
        """Каналы уведомлений для кухонного дисплея"""
        return [NotificationChannel.KITCHEN_DISPLAY, NotificationChannel.STAFF_PAGER]

    def is_interested_in(self, notification_type: NotificationType, data: Dict[str, Any]) -> bool:
        """Кухня заинтересована в заказах и кухонных алертах"""
        kitchen_notifications = {
            NotificationType.ORDER_CONFIRMED,
            NotificationType.ORDER_IN_PREPARATION,
            NotificationType.ORDER_READY,
            NotificationType.ORDER_COMPLETED,
            NotificationType.KITCHEN_ALERT
        }
        return notification_type in kitchen_notifications

    def _add_to_preparation_queue(self, order_id: str, order_data: Dict[str, Any]):
        """Добавляет заказ в очередь приготовления"""
        # Проверяем приоритет (VIP, большие заказы)
        is_priority = (
                order_data.get("customer_type") == "vip" or
                order_data.get("items_count", 0) > 5 or
                order_data.get("order_type") == "delivery"
        )

        queue_item = {
            "order_id": order_id,
            "customer_id": order_data.get("customer_id"),
            "order_type": order_data.get("order_type"),
            "items_count": order_data.get("items_count", 0),
            "estimated_prep_time": order_data.get("estimated_prep_time", 5),
            "is_priority": is_priority,
            "added_at": datetime.now(),
            "status": "queued"
        }

        # Добавляем в приоритетную очередь или обычную
        if is_priority:
            self._priority_orders.append(order_id)
            self._preparation_queue.insert(0, queue_item)  # В начало
        else:
            self._preparation_queue.append(queue_item)

        # Ограничиваем размер дисплея
        if len(self._preparation_queue) > self._display_capacity:
            self._preparation_queue = self._preparation_queue[:self._display_capacity]

        log_business_rule("Order Queued",
                          f"Kitchen {self.station}: Order {order_id} {'(PRIORITY)' if is_priority else ''}")

    def _update_preparation_status(self, order_id: str, status: str):
        """Обновляет статус приготовления"""
        for item in self._preparation_queue:
            if item["order_id"] == order_id:
                item["status"] = status
                item["status_updated_at"] = datetime.now()
                break

    def _mark_order_ready(self, order_id: str):
        """Отмечает заказ готовым"""
        self._update_preparation_status(order_id, "ready")

        # Убираем из приоритетных если был там
        if order_id in self._priority_orders:
            self._priority_orders.remove(order_id)

    def _remove_from_display(self, order_id: str):
        """Убирает заказ с дисплея"""
        self._preparation_queue = [item for item in self._preparation_queue
                                   if item["order_id"] != order_id]

        if order_id in self._priority_orders:
            self._priority_orders.remove(order_id)

    def _handle_kitchen_alert(self, alert_data: Dict[str, Any]):
        """Обрабатывает кухонные алерты"""
        alert_type = alert_data.get("alert_type")
        message = alert_data.get("message", "Kitchen alert")

        log_business_rule("Kitchen Alert", f"Station {self.station}: {alert_type} - {message}")

    def get_current_queue(self) -> List[Dict[str, Any]]:
        """Возвращает текущую очередь приготовления"""
        return self._preparation_queue.copy()


# ✅ WYMAGANIE: Dziedziczenie + Observer - Мобильное приложение клиента
class CustomerMobileObserver(OrderObserver):
    """
    📋 CHECK: Observer Pattern - Customer mobile app observer
    📋 CHECK: Dziedziczenie - CustomerMobileObserver наследует от OrderObserver
    Наблюдатель для мобильного приложения клиента
    """

    def __init__(self, observer_id: str, customer_id: str, phone_number: str = "",
                 push_notifications_enabled: bool = True):
        # ✅ WYMAGANIE: super()
        super().__init__(observer_id, f"Mobile App ({customer_id})")

        # 🔄 TRANSFER: OrderObserver.__init__ → CustomerMobileObserver.__init__
        log_transfer("OrderObserver.__init__", "CustomerMobileObserver.__init__",
                     "mobile app attributes")

        self.customer_id = customer_id
        self.phone_number = phone_number
        self.push_notifications_enabled = push_notifications_enabled
        self._order_updates: List[Dict[str, Any]] = []
        self._loyalty_notifications: List[Dict[str, Any]] = []

        log_requirement_check("Observer Inheritance", "SUCCESS",
                              f"CustomerMobileObserver extends OrderObserver")

    def update(self, subject: OrderNotificationSubject, notification_type: NotificationType,
               data: Dict[str, Any]):
        """
        📋 CHECK: Observer Pattern - Mobile app update implementation
        Обрабатывает уведомления для мобильного приложения
        """
        notification_data = data["data"]
        order_id = notification_data.get("order_id")
        customer_id = notification_data.get("customer_id")

        # Фильтруем только уведомления для этого клиента
        if customer_id and customer_id != self.customer_id:
            return

        # Создаем уведомление для приложения
        app_notification = {
            "notification_id": data.get("notification_id"),
            "type": notification_type.value,
            "timestamp": data.get("timestamp"),
            "order_id": order_id,
            "title": self._get_notification_title(notification_type),
            "message": self._get_notification_message(notification_type, notification_data),
            "priority": self._get_notification_priority(notification_type),
            "read": False
        }

        # Сохраняем уведомление
        if notification_type in [NotificationType.ORDER_CREATED, NotificationType.ORDER_CONFIRMED,
                                 NotificationType.ORDER_IN_PREPARATION, NotificationType.ORDER_READY,
                                 NotificationType.ORDER_COMPLETED]:
            self._order_updates.append(app_notification)
        else:
            self._loyalty_notifications.append(app_notification)

        # Отправляем push-уведомление если включено
        if self.push_notifications_enabled:
            self._send_push_notification(app_notification)

        log_business_rule("Mobile App Notified",
                          f"Customer {self.customer_id}: {notification_type.value}")

    def get_notification_channels(self) -> List[NotificationChannel]:
        """Каналы для мобильного приложения"""
        channels = [NotificationChannel.MOBILE_APP]
        if self.phone_number:
            channels.append(NotificationChannel.SMS)
        return channels

    def is_interested_in(self, notification_type: NotificationType, data: Dict[str, Any]) -> bool:
        """Клиент заинтересован в уведомлениях о своих заказах"""
        # Проверяем что это уведомление для этого клиента
        customer_id = data.get("customer_id")
        if customer_id and customer_id != self.customer_id:
            return False

        # Интересуемся всеми уведомлениями о заказах
        return notification_type in [
            NotificationType.ORDER_CREATED,
            NotificationType.ORDER_CONFIRMED,
            NotificationType.ORDER_IN_PREPARATION,
            NotificationType.ORDER_READY,
            NotificationType.ORDER_COMPLETED,
            NotificationType.ORDER_CANCELLED,
            NotificationType.PAYMENT_PROCESSED,
            NotificationType.PAYMENT_FAILED
        ]

    def _get_notification_title(self, notification_type: NotificationType) -> str:
        """Возвращает заголовок уведомления"""
        titles = {
            NotificationType.ORDER_CREATED: "Order Placed",
            NotificationType.ORDER_CONFIRMED: "Order Confirmed",
            NotificationType.ORDER_IN_PREPARATION: "Order Being Prepared",
            NotificationType.ORDER_READY: "Order Ready!",
            NotificationType.ORDER_COMPLETED: "Order Complete",
            NotificationType.ORDER_CANCELLED: "Order Cancelled",
            NotificationType.PAYMENT_PROCESSED: "Payment Successful",
            NotificationType.PAYMENT_FAILED: "Payment Failed"
        }
        return titles.get(notification_type, "McDonald's Update")

    def _get_notification_message(self, notification_type: NotificationType,
                                  data: Dict[str, Any]) -> str:
        """Генерирует сообщение уведомления"""
        order_id = data.get("order_id", "")

        messages = {
            NotificationType.ORDER_CREATED: f"Your order {order_id} has been placed successfully.",
            NotificationType.ORDER_CONFIRMED: f"Your order {order_id} has been confirmed and payment processed.",
            NotificationType.ORDER_IN_PREPARATION: f"Your order {order_id} is being prepared in our kitchen.",
            NotificationType.ORDER_READY: f"Your order {order_id} is ready for pickup!",
            NotificationType.ORDER_COMPLETED: f"Your order {order_id} has been completed. Thank you!",
            NotificationType.ORDER_CANCELLED: f"Your order {order_id} has been cancelled.",
            NotificationType.PAYMENT_PROCESSED: f"Payment for order {order_id} was successful.",
            NotificationType.PAYMENT_FAILED: f"Payment for order {order_id} failed. Please try again."
        }

        return messages.get(notification_type, f"Update for your order {order_id}")

    def _get_notification_priority(self, notification_type: NotificationType) -> NotificationPriority:
        """Определяет приоритет уведомления"""
        high_priority = {
            NotificationType.ORDER_READY,
            NotificationType.ORDER_CANCELLED,
            NotificationType.PAYMENT_FAILED
        }

        if notification_type in high_priority:
            return NotificationPriority.HIGH
        else:
            return NotificationPriority.NORMAL

    def _send_push_notification(self, notification: Dict[str, Any]):
        """Симулирует отправку push-уведомления"""
        log_business_rule("Push Notification Sent",
                          f"To {self.customer_id}: {notification['title']}")

    def get_recent_notifications(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Возвращает последние уведомления"""
        all_notifications = self._order_updates + self._loyalty_notifications
        all_notifications.sort(key=lambda x: x["timestamp"], reverse=True)
        return all_notifications[:limit]

    def mark_notification_as_read(self, notification_id: str):
        """Отмечает уведомление как прочитанное"""
        for notification in self._order_updates + self._loyalty_notifications:
            if notification.get("notification_id") == notification_id:
                notification["read"] = True
                break


# ✅ WYMAGANIE: Dziedziczenie + Observer - Drive-Thru система
class DriveThruObserver(OrderObserver):
    """
    📋 CHECK: Observer Pattern - Drive-thru observer
    📋 CHECK: Dziedziczenie - DriveThruObserver наследует от OrderObserver
    Наблюдатель для системы Drive-Thru
    """

    def __init__(self, observer_id: str, lane_number: int = 1):
        # ✅ WYMAGANIE: super()
        super().__init__(observer_id, f"Drive-Thru Lane {lane_number}")

        # 🔄 TRANSFER: OrderObserver.__init__ → DriveThruObserver.__init__
        log_transfer("OrderObserver.__init__", "DriveThruObserver.__init__",
                     "drive-thru attributes")

        self.lane_number = lane_number
        self._current_queue: List[Dict[str, Any]] = []
        self._max_queue_size = 10
        self._average_service_time = 180  # секунд

        log_requirement_check("Observer Inheritance", "SUCCESS",
                              f"DriveThruObserver extends OrderObserver")

    def update(self, subject: OrderNotificationSubject, notification_type: NotificationType,
               data: Dict[str, Any]):
        """
        📋 CHECK: Observer Pattern - Drive-thru update implementation
        Обрабатывает уведомления для Drive-Thru
        """
        notification_data = data["data"]
        order_id = notification_data.get("order_id")
        order_type = notification_data.get("order_type")

        # Обрабатываем только Drive-Thru заказы
        if order_type != "drive_thru":
            return

        if notification_type == NotificationType.ORDER_CREATED:
            self._add_to_queue(order_id, notification_data)

        elif notification_type == NotificationType.ORDER_READY:
            self._notify_order_ready(order_id)

        elif notification_type == NotificationType.ORDER_COMPLETED:
            self._remove_from_queue(order_id)

        elif notification_type == NotificationType.DRIVE_THRU_ALERT:
            self._handle_drive_thru_alert(notification_data)

        log_business_rule("Drive-Thru Updated",
                          f"Lane {self.lane_number}: {notification_type.value} for order {order_id}")

    def get_notification_channels(self) -> List[NotificationChannel]:
        """Каналы для Drive-Thru"""
        return [NotificationChannel.DRIVE_THRU_SPEAKER, NotificationChannel.POS_SYSTEM]

    def is_interested_in(self, notification_type: NotificationType, data: Dict[str, Any]) -> bool:
        """Drive-Thru заинтересован в Drive-Thru заказах"""
        order_type = data.get("order_type")

        # Интересуемся только Drive-Thru заказами и алертами
        drive_thru_notifications = {
            NotificationType.ORDER_CREATED,
            NotificationType.ORDER_READY,
            NotificationType.ORDER_COMPLETED,
            NotificationType.DRIVE_THRU_ALERT
        }

        return (notification_type in drive_thru_notifications and
                (order_type == "drive_thru" or notification_type == NotificationType.DRIVE_THRU_ALERT))

    def _add_to_queue(self, order_id: str, order_data: Dict[str, Any]):
        """Добавляет заказ в очередь Drive-Thru"""
        if len(self._current_queue) >= self._max_queue_size:
            log_business_rule("Drive-Thru Queue Full", f"Lane {self.lane_number} at capacity")
            return

        queue_item = {
            "order_id": order_id,
            "customer_id": order_data.get("customer_id"),
            "items_count": order_data.get("items_count", 0),
            "estimated_wait": len(self._current_queue) * self._average_service_time,
            "added_at": datetime.now(),
            "position": len(self._current_queue) + 1
        }

        self._current_queue.append(queue_item)

        log_business_rule("Drive-Thru Queue Added",
                          f"Lane {self.lane_number}: Order {order_id} at position {queue_item['position']}")

    def _notify_order_ready(self, order_id: str):
        """Уведомляет о готовности заказа"""
        for item in self._current_queue:
            if item["order_id"] == order_id:
                item["ready_at"] = datetime.now()
                position = item["position"]
                log_business_rule("Drive-Thru Order Ready",
                                  f"Lane {self.lane_number}: Order {order_id} ready at position {position}")
                break

    def _remove_from_queue(self, order_id: str):
        """Убирает заказ из очереди"""
        self._current_queue = [item for item in self._current_queue
                               if item["order_id"] != order_id]

        # Обновляем позиции в очереди
        for i, item in enumerate(self._current_queue):
            item["position"] = i + 1

        log_business_rule("Drive-Thru Queue Completed",
                          f"Lane {self.lane_number}: Order {order_id} completed, {len(self._current_queue)} remaining")

    def _handle_drive_thru_alert(self, alert_data: Dict[str, Any]):
        """Обрабатывает алерты Drive-Thru"""
        alert_type = alert_data.get("alert_type")
        message = alert_data.get("message", "Drive-Thru alert")

        log_business_rule("Drive-Thru Alert", f"Lane {self.lane_number}: {alert_type} - {message}")

    def get_queue_status(self) -> Dict[str, Any]:
        """Возвращает статус очереди"""
        return {
            "lane_number": self.lane_number,
            "queue_length": len(self._current_queue),
            "max_capacity": self._max_queue_size,
            "estimated_wait_time": len(self._current_queue) * self._average_service_time,
            "current_queue": self._current_queue.copy()
        }


# Функция демонстрации паттерна Observer
def demo_observer_pattern():
    """
    📋 CHECK: Полная демонстрация паттерна Observer для системы уведомлений McDonald's
    """

    print("👁️ McDONALD'S OBSERVER PATTERN DEMO")
    print("=" * 50)

    # 🔄 TRANSFER: demo → observer pattern
    log_transfer("demo_observer_pattern", "Observer Pattern", "observer demonstration")

    # 1. Создание Subject (наблюдаемого объекта)
    print("\n1. ORDER TRACKER CREATION (Subject)")
    print("-" * 30)

    order_tracker = OrderTracker("MCD0001")
    print(f"Created OrderTracker for restaurant: {order_tracker.restaurant_id}")

    # 2. Создание различных наблюдателей
    print("\n2. OBSERVERS CREATION")
    print("-" * 30)

    # Кухонный дисплей
    kitchen_display = KitchenDisplayObserver("KITCHEN_001", "main_kitchen")

    # Мобильное приложение клиентов
    customer_app1 = CustomerMobileObserver("MOBILE_001", "CUST000001", "+1234567890")
    customer_app2 = CustomerMobileObserver("MOBILE_002", "CUST000002", "+1987654321")

    # Drive-Thru система
    drive_thru = DriveThruObserver("DRIVETHRU_001", lane_number=1)

    observers = [kitchen_display, customer_app1, customer_app2, drive_thru]

    for observer in observers:
        print(f"Created observer: {observer.name}")
        print(f"  Channels: {[ch.value for ch in observer.get_notification_channels()]}")

    # 3. Подписка наблюдателей
    print("\n3. ATTACHING OBSERVERS")
    print("-" * 30)

    for observer in observers:
        order_tracker.attach(observer)
        print(f"Attached: {observer.name}")

    tracking_summary = order_tracker.get_tracking_summary()
    print(f"Total observers: {tracking_summary['total_observers']}")
    print(f"Active observers: {tracking_summary['active_observers']}")

    # 4. Создание и отслеживание заказов
    print("\n4. ORDER TRACKING AND NOTIFICATIONS")
    print("-" * 30)

    # Заказ 1: Dine-in для клиента 1
    order1_data = {
        "customer_id": "CUST000001",
        "order_type": "dine_in",
        "total_amount": 15.99,
        "items_count": 3,
        "estimated_prep_time": 8
    }

    print("Creating dine-in order...")
    order_tracker.track_order("ORD000001", order1_data)

    # Заказ 2: Drive-Thru для клиента 2
    order2_data = {
        "customer_id": "CUST000002",
        "order_type": "drive_thru",
        "total_amount": 12.50,
        "items_count": 2,
        "estimated_prep_time": 5
    }

    print("Creating drive-thru order...")
    order_tracker.track_order("ORD000002", order2_data)

    # 5. Обновление статусов заказов
    print("\n5. ORDER STATUS UPDATES")
    print("-" * 30)

    status_updates = [
        ("ORD000001", "confirmed", {"payment_method": "credit_card"}),
        ("ORD000002", "confirmed", {"payment_method": "cash"}),
        ("ORD000001", "in_preparation", {"assigned_cook": "EMP1004"}),
        ("ORD000002", "in_preparation", {"assigned_cook": "EMP1005"}),
        ("ORD000001", "ready", {"pickup_location": "counter"}),
        ("ORD000002", "ready", {"lane_number": 1}),
        ("ORD000001", "completed", {"satisfaction_rating": 5}),
        ("ORD000002", "completed", {"service_time": 180})
    ]

    for order_id, status, additional_data in status_updates:
        print(f"Updating {order_id} to {status}...")
        order_tracker.update_order_status(order_id, status, additional_data)
        print()

    # 6. Проверка уведомлений у наблюдателей
    print("\n6. OBSERVER NOTIFICATIONS CHECK")
    print("-" * 30)

    # Кухонный дисплей
    print("Kitchen Display Queue:")
    kitchen_queue = kitchen_display.get_current_queue()
    for item in kitchen_queue:
        print(f"  {item['order_id']}: {item['status']} ({'PRIORITY' if item['is_priority'] else 'NORMAL'})")

    # Мобильные приложения
    print(f"\nCustomer App 1 notifications:")
    notifications1 = customer_app1.get_recent_notifications(5)
    for notif in notifications1:
        print(f"  {notif['timestamp'].strftime('%H:%M:%S')}: {notif['title']} - {notif['message']}")

    print(f"\nCustomer App 2 notifications:")
    notifications2 = customer_app2.get_recent_notifications(5)
    for notif in notifications2:
        print(f"  {notif['timestamp'].strftime('%H:%M:%S')}: {notif['title']} - {notif['message']}")

    # Drive-Thru
    print(f"\nDrive-Thru Queue Status:")
    queue_status = drive_thru.get_queue_status()
    print(f"  Queue length: {queue_status['queue_length']}")
    print(f"  Estimated wait: {queue_status['estimated_wait_time']} seconds")

    # 7. Тестирование отписки наблюдателя
    print("\n7. OBSERVER DETACHMENT TEST")
    print("-" * 30)

    print("Detaching customer app 1...")
    order_tracker.detach(customer_app1)

    # Создаем новый заказ
    order3_data = {
        "customer_id": "CUST000003",
        "order_type": "takeout",
        "total_amount": 8.99,
        "items_count": 1
    }

    print("Creating new takeout order after detachment...")
    order_tracker.track_order("ORD000003", order3_data)
    order_tracker.update_order_status("ORD000003", "confirmed")

    # Проверяем что отписанный наблюдатель не получил уведомление
    new_notifications1 = customer_app1.get_recent_notifications(10)
    new_notifications2 = customer_app2.get_recent_notifications(10)

    print(f"Customer App 1 (detached) notifications: {len(new_notifications1)}")
    print(f"Customer App 2 (still attached) notifications: {len(new_notifications2)}")

    # 8. Статистика наблюдателей
    print("\n8. OBSERVER STATISTICS")
    print("-" * 30)

    for observer in observers:
        stats = observer.get_stats()
        print(f"{stats['name']}:")
        print(f"  Active: {stats['is_active']}")
        print(f"  Notifications received: {stats['notification_count']}")
        print(f"  Last notification: {stats['last_notification']}")
        print()

    # 9. Итоговая статистика отслеживания
    print("\n9. TRACKING SUMMARY")
    print("-" * 30)

    final_summary = order_tracker.get_tracking_summary()
    print(f"Restaurant: {final_summary['restaurant_id']}")
    print(f"Active orders: {final_summary['active_orders']}")
    print(f"Total observers: {final_summary['total_observers']}")
    print(f"Active observers: {final_summary['active_observers']}")
    print(f"Notifications sent: {final_summary['notifications_sent']}")

    # 📋 CHECK: Финальная проверка паттерна Observer
    log_requirement_check("Observer Pattern Demo", "COMPLETED", "observer.py")

    return order_tracker, observers


if __name__ == "__main__":
    demo_observer_pattern()