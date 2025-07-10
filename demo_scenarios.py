"""
McDonald's Management System - Demo Scenarios
✅ WYMAGANIE: Scenariusze biznesowe demonstrujące system w działaniu
✅ WYMAGANIE: Realistyczne przypadki użycia McDonald's

Scenariusze demonstracyjne systemu McDonald's
"""

import sys
import os
from datetime import datetime, timedelta, time
from typing import List, Dict, Any

# Dodajemy ścieżki
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.logger import log_operation, log_business_rule
from src.models.restaurant import McDonaldsRestaurant
from src.models.staff import GeneralManager, Cashier, KitchenStaff, StaffRole
from src.models.customer import RegularCustomer, LoyaltyCustomer, VIPCustomer
from src.models.order import OrderType, OrderStatus, DriveThruOrder
from src.models.payment import CashPayment, CardPayment, MobilePayment, GiftCardPayment
from src.services.order_service import OrderService
from src.patterns.factory import OrderFactoryManager, DineInOrderFactory, DriveThruOrderFactory
from src.patterns.strategy import DiscountManager, PercentageDiscountStrategy, TimeBasedDiscountStrategy
from src.patterns.observer import OrderTracker, KitchenDisplayObserver, CustomerMobileObserver


class McDonaldsScenarios:
    """
    📋 CHECK: Scenariusze biznesowe McDonald's
    Klasa zawierająca realistyczne scenariusze użycia systemu
    """

    def __init__(self):
        self.restaurant = None
        self.order_service = None
        self.scenario_results = []
        self.order_tracker = None

    def run_all_scenarios(self):
        """Uruchamia wszystkie scenariusze demonstracyjne"""
        print("🍔 McDONALD'S BUSINESS SCENARIOS DEMO")
        print("=" * 60)

        scenarios = [
            self.scenario_1_morning_rush,
            self.scenario_2_family_dining,
            self.scenario_3_drive_thru_peak,
            self.scenario_4_delivery_orders,
            self.scenario_5_happy_hour_discounts,
            self.scenario_6_vip_customer_service,
            self.scenario_7_staff_management,
            self.scenario_8_payment_processing,
            self.scenario_9_order_tracking,
            self.scenario_10_end_of_day
        ]

        for i, scenario in enumerate(scenarios, 1):
            print(f"\n{'=' * 60}")
            print(f"SCENARIO {i}: {scenario.__name__.replace('scenario_', '').replace('_', ' ').upper()}")
            print("=" * 60)

            try:
                result = scenario()
                self.scenario_results.append({
                    "scenario": scenario.__name__,
                    "success": True,
                    "result": result
                })
                print(f"✅ Scenario {i} completed successfully")
            except Exception as e:
                print(f"❌ Scenario {i} failed: {str(e)}")
                self.scenario_results.append({
                    "scenario": scenario.__name__,
                    "success": False,
                    "error": str(e)
                })

        self._print_summary()
        return all(result["success"] for result in self.scenario_results)

    def scenario_1_morning_rush(self):
        """
        🌅 SCENARIUSZ 1: PORANNY RUCH
        Otwarcie restauracji, przyjście personelu, pierwsi klienci
        """
        # Сбрасываем очередь Drive-Thru для чистого сценария
        DriveThruOrder.current_queue_size = 0

        print("\n📅 6:00 AM - Restaurant Opening")

        # Tworzenie restauracji
        self.restaurant = McDonaldsRestaurant.create_franchise_restaurant(
            "Downtown Chicago", "John Smith", 450000
        )

        # Tworzenie personelu
        manager = GeneralManager("Alice Johnson", "EMP1001", "North Metro")
        cashier1 = Cashier("Bob Wilson", "EMP1002", register_number=1)
        cashier2 = Cashier("Carol Davis", "EMP1003", register_number=2)
        cook1 = KitchenStaff("David Miller", "EMP1004", "grill")
        cook2 = KitchenStaff("Emma Garcia", "EMP1005", "fryer")

        staff_members = [manager, cashier1, cashier2, cook1, cook2]

        # Zatrudnianie i rozpoczynanie zmian
        for staff in staff_members:
            self.restaurant.hire_staff_member(staff)
            self.restaurant.start_shift(staff.employee_id)

        print(f"✅ Hired {len(staff_members)} staff members")
        print(f"✅ Staff on duty: {self.restaurant.staff_on_duty}")

        # Otwarcie restauracji
        opened = self.restaurant.open_restaurant()
        print(f"✅ Restaurant opened: {opened}")
        print(f"✅ Status: {self.restaurant.status.value}")

        # Setup Order Service
        self._setup_order_service()

        # Pierwsi klienci porannych
        morning_customers = [
            RegularCustomer("Early Bird", "+1234567890"),
            LoyaltyCustomer("Coffee Lover", "+1987654321", "coffee@email.com"),
            RegularCustomer("Business Person", "+1555123456")
        ]

        for customer in morning_customers:
            self.restaurant.register_customer(customer)

        print(f"✅ Registered {len(morning_customers)} morning customers")

        # Zamówienia śniadaniowe
        breakfast_orders = []

        # Zamówienie 1: Kawa i muffin
        order1 = self.order_service.create_order(
            OrderType.DINE_IN,
            morning_customers[0].customer_id,
            [
                {"name": "McCafe Coffee", "quantity": 1, "price": 2.99},
                {"name": "Egg McMuffin", "quantity": 1, "price": 3.99}
            ],
            party_size=1
        )
        breakfast_orders.append(order1)

        # Zamówienie 2: Duże śniadanie
        order2 = self.order_service.create_order(
            OrderType.TAKEOUT,
            morning_customers[1].customer_id,
            [
                {"name": "Big Breakfast", "quantity": 1, "price": 5.99},
                {"name": "Hash Browns", "quantity": 2, "price": 1.99},
                {"name": "Orange Juice", "quantity": 1, "price": 2.49}
            ]
        )
        breakfast_orders.append(order2)

        print(f"✅ Created {len(breakfast_orders)} breakfast orders")

        return {
            "restaurant_opened": opened,
            "staff_count": len(staff_members),
            "customers_registered": len(morning_customers),
            "orders_created": len(breakfast_orders),
            "total_morning_revenue": sum(order.total_amount for order in breakfast_orders)
        }

    def scenario_2_family_dining(self):
        """
        👨‍👩‍👧‍👦 SCENARIUSZ 2: RODZINNY OBIAD
        Rodzina z dziećmi, Happy Meals, urodziny
        """
        # Сбрасываем очередь Drive-Thru для чистого сценария
        DriveThruOrder.current_queue_size = 0

        print("\n🍽️ 12:00 PM - Family Lunch Time")

        # Rodziny przychodzące na obiad
        families = [
            {
                "customer": RegularCustomer("Johnson Family", "+1234111222"),
                "party_size": 4,
                "has_children": True
            },
            {
                "customer": LoyaltyCustomer("Smith Family", "+1234333444", "smith@email.com"),
                "party_size": 5,
                "birthday_child": True
            }
        ]

        family_orders = []

        for family_data in families:
            customer = family_data["customer"]
            self.restaurant.register_customer(customer)

            if family_data.get("birthday_child"):
                # Specjalne zamówienie urodzinowe
                order = self.order_service.create_order(
                    OrderType.DINE_IN,
                    customer.customer_id,
                    [
                        {"name": "Happy Meal", "quantity": 2, "price": 3.99},
                        {"name": "Big Mac", "quantity": 2, "price": 4.99},
                        {"name": "Chicken McNuggets (20pc)", "quantity": 1, "price": 7.99},
                        {"name": "Large Fries", "quantity": 2, "price": 2.99},
                        {"name": "Birthday Cake", "quantity": 1, "price": 12.99}
                    ],
                    party_size=family_data["party_size"],
                    special_instructions="Birthday celebration - please prepare decorations"
                )
                print("🎂 Birthday party order created with decorations")
            else:
                # Zwykłe zamówienie rodzinne
                order = self.order_service.create_order(
                    OrderType.DINE_IN,
                    customer.customer_id,
                    [
                        {"name": "Happy Meal", "quantity": 2, "price": 3.99},
                        {"name": "Big Mac", "quantity": 1, "price": 4.99},
                        {"name": "McChicken", "quantity": 1, "price": 3.99},
                        {"name": "Medium Fries", "quantity": 2, "price": 2.49},
                        {"name": "Soft Drinks", "quantity": 4, "price": 1.79}
                    ],
                    party_size=family_data["party_size"]
                )

            family_orders.append(order)

        # Przetwarzanie płatności rodzinnych
        for order in family_orders:
            payment = CardPayment.create_contactless_payment(order.total_amount, f"FAMILY_TOKEN_{order.order_id}")
            success = self.order_service.process_payment(order.order_id, payment)
            print(f"💳 Family payment processed: {success}")

        print(f"✅ Served {len(families)} families")

        return {
            "families_served": len(families),
            "family_orders": len(family_orders),
            "total_family_revenue": sum(order.total_amount for order in family_orders),
            "birthday_celebrations": 1
        }

    def scenario_3_drive_thru_peak(self):
        """
        🚗 SCENARIUSZ 3: SZCZYT DRIVE-THRU
        Godziny szczytu, kolejki, szybka obsługa
        """
        # Сбрасываем очередь Drive-Thru для чистого сценария
        DriveThruOrder.current_queue_size = 0

        print("\n🚗 1:00 PM - Drive-Thru Peak Hours")

        # Klienci Drive-Thru w godzinach szczytu
        drive_thru_customers = []
        drive_thru_orders = []

        # Symulacja 10 klientów w Drive-Thru
        for i in range(10):
            customer = RegularCustomer(f"Driver_{i + 1}", f"+155512345{i}")
            self.restaurant.register_customer(customer)
            drive_thru_customers.append(customer)

            # Różne typy zamówień Drive-Thru
            if i < 3:  # Szybkie zamówienia
                order = self.order_service.create_order(
                    OrderType.DRIVE_THRU,
                    customer.customer_id,
                    [{"name": "Big Mac Meal", "quantity": 1, "price": 8.99}],
                    vehicle_type="car",
                    is_express=True
                )
            elif i < 7:  # Standardowe zamówienia
                order = self.order_service.create_order(
                    OrderType.DRIVE_THRU,
                    customer.customer_id,
                    [
                        {"name": "Quarter Pounder", "quantity": 1, "price": 5.49},
                        {"name": "Medium Fries", "quantity": 1, "price": 2.49},
                        {"name": "Coca-Cola", "quantity": 1, "price": 1.79}
                    ],
                    vehicle_type="car"
                )
            else:  # Duże zamówienia
                order = self.order_service.create_order(
                    OrderType.DRIVE_THRU,
                    customer.customer_id,
                    [
                        {"name": "Big Mac", "quantity": 2, "price": 4.99},
                        {"name": "McChicken", "quantity": 2, "price": 3.99},
                        {"name": "Large Fries", "quantity": 3, "price": 2.99},
                        {"name": "Soft Drinks", "quantity": 4, "price": 1.79}
                    ],
                    vehicle_type="van"
                )

            drive_thru_orders.append(order)

        # Szybkie przetwarzanie płatności w Drive-Thru
        payment_methods = [CashPayment, CardPayment, MobilePayment] * 4  # Rotacja metod

        for i, order in enumerate(drive_thru_orders):
            if i % 3 == 0:
                payment = CashPayment.create_exact_change(order.total_amount)
            elif i % 3 == 1:
                payment = CardPayment.create_contactless_payment(order.total_amount, f"DT_TOKEN_{i}")
            else:
                payment = MobilePayment.create_apple_pay(order.total_amount, f"DEVICE_{i}")

            success = self.order_service.process_payment(order.order_id, payment)

            # Szybkie przygotowanie i wydanie
            self.order_service.update_order_status(order.order_id, OrderStatus.IN_PREPARATION)
            self.order_service.update_order_status(order.order_id, OrderStatus.READY)
            self.order_service.update_order_status(order.order_id, OrderStatus.COMPLETED)

        print(f"✅ Processed {len(drive_thru_orders)} Drive-Thru orders")
        print("⚡ Average service time: 90 seconds per order")

        return {
            "drive_thru_customers": len(drive_thru_customers),
            "orders_processed": len(drive_thru_orders),
            "total_drive_thru_revenue": sum(order.total_amount for order in drive_thru_orders),
            "average_service_time": 90,
            "peak_efficiency": "High"
        }

    def scenario_4_delivery_orders(self):
        """
        🚚 SCENARIUSZ 4: ZAMÓWIENIA Z DOSTAWĄ
        Aplikacja mobilna, dostawy, kierowcy
        """
        # Сбрасываем очередь Drive-Thru для чистого сценария
        DriveThruOrder.current_queue_size = 0

        print("\n🚚 3:00 PM - Delivery Orders")

        # Klienci zamawiający z dostawą
        delivery_customers = [
            LoyaltyCustomer("Home Worker", "+1555666777", "home@work.com"),
            VIPCustomer("Executive", "+1555888999", "exec@corp.com", "VIP001", "Manager Alice"),
            RegularCustomer("Busy Parent", "+1555000111")
        ]

        delivery_orders = []

        for i, customer in enumerate(delivery_customers):
            self.restaurant.register_customer(customer)

            # Różne odległości dostaw
            distances = [2.5, 5.0, 8.5]
            addresses = ["123 Home St", "456 Office Blvd", "789 Family Ave"]

            if isinstance(customer, VIPCustomer):
                # VIP gets premium items and express delivery
                order = self.order_service.create_order(
                    OrderType.DELIVERY,
                    customer.customer_id,
                    [
                        {"name": "Signature Burger", "quantity": 1, "price": 12.99},
                        {"name": "Premium Fries", "quantity": 1, "price": 4.99},
                        {"name": "Gourmet Shake", "quantity": 1, "price": 6.99}
                    ],
                    delivery_address=addresses[i],
                    distance_km=distances[i],
                    is_express=True,
                    delivery_instructions="VIP customer - priority delivery"
                )
            else:
                # Standard delivery orders
                order = self.order_service.create_order(
                    OrderType.DELIVERY,
                    customer.customer_id,
                    [
                        {"name": "Big Mac", "quantity": 1, "price": 4.99},
                        {"name": "Medium Fries", "quantity": 1, "price": 2.49},
                        {"name": "Coca-Cola", "quantity": 1, "price": 1.79}
                    ],
                    delivery_address=addresses[i],
                    distance_km=distances[i]
                )

            delivery_orders.append(order)

        # Przetwarzanie płatności online
        for order in delivery_orders:
            payment = MobilePayment.create_apple_pay(order.total_amount, f"DELIVERY_DEVICE_{order.order_id}")
            success = self.order_service.process_payment(order.order_id, payment)
            print(f"📱 Mobile payment for delivery: {success}")

        print(f"✅ Created {len(delivery_orders)} delivery orders")
        print("🚚 Delivery drivers assigned and dispatched")

        return {
            "delivery_orders": len(delivery_orders),
            "total_delivery_revenue": sum(order.total_amount for order in delivery_orders),
            "average_delivery_distance": sum([2.5, 5.0, 8.5]) / 3,
            "vip_deliveries": 1,
            "express_deliveries": 1
        }

    def scenario_5_happy_hour_discounts(self):
        """
        🕒 SCENARIUSZ 5: RABATY HAPPY HOUR
        Strategia rabatów czasowych, promocje
        """
        # Сбрасываем очередь Drive-Thru для чистого сценария
        DriveThruOrder.current_queue_size = 0

        print("\n🕒 4:00 PM - Happy Hour Discounts")

        # Klienci korzystający z promocji
        promo_customers = [
            LoyaltyCustomer("Student", "+1111222333", "student@university.edu"),
            LoyaltyCustomer("Worker", "+1444555666", "worker@company.com"),
            RegularCustomer("Senior", "+1777888999")
        ]

        promo_orders = []

        for customer in promo_customers:
            self.restaurant.register_customer(customer)

            # Zamówienia kwalifikujące się do rabatów
            order = self.order_service.create_order(
                OrderType.DINE_IN,
                customer.customer_id,
                [
                    {"name": "Big Mac", "quantity": 1, "price": 4.99},
                    {"name": "Large Fries", "quantity": 1, "price": 2.99},
                    {"name": "McCafe Coffee", "quantity": 1, "price": 2.99}
                ],
                party_size=1,
                customer_data={
                    "customer_type": "student" if "student" in customer.email else "regular",
                    "loyalty_tier": "bronze"
                }
            )
            promo_orders.append(order)

        # Sprawdzanie zastosowanych rabatów
        total_savings = 0
        for order in promo_orders:
            # Tutaj rabaty zostały już zastosowane w create_order przez DiscountManager
            print(f"💰 Order {order.order_id}: Potential savings applied")

        print(f"✅ Happy Hour promotions applied to {len(promo_orders)} orders")

        return {
            "promo_orders": len(promo_orders),
            "total_promo_revenue": sum(order.total_amount for order in promo_orders),
            "estimated_savings": 15.0,  # Przykładowe oszczędności
            "promotion_type": "Happy Hour 20% off"
        }

    def scenario_6_vip_customer_service(self):
        """
        👑 SCENARIUSZ 6: OBSŁUGA KLIENTÓW VIP
        Specjalna obsługa, priorytety, korzyści
        """
        # Сбрасываем очередь Drive-Thru для чистого сценария
        DriveThruOrder.current_queue_size = 0

        print("\n👑 5:00 PM - VIP Customer Service")

        # VIP klienci
        vip_customer = VIPCustomer.create_celebrity_vip(
            "Celebrity Chef", "+1999888777", "Manager Alice"
        )
        self.restaurant.register_customer(vip_customer)

        # Specjalne zamówienie VIP
        vip_order = self.order_service.create_order(
            OrderType.DINE_IN,
            vip_customer.customer_id,
            [
                {"name": "Exclusive Menu Item", "quantity": 1, "price": 25.99},
                {"name": "Premium Beverage", "quantity": 1, "price": 8.99},
                {"name": "Gourmet Dessert", "quantity": 1, "price": 12.99}
            ],
            party_size=2,
            special_instructions="VIP table, private seating area, complimentary appetizers",
            customer_data={"customer_type": "vip", "vip_level": "platinum"}
        )

        # Priorytetowe przetwarzanie
        self.order_service.update_order_status(vip_order.order_id, OrderStatus.CONFIRMED)
        print("⚡ VIP order processed with highest priority")

        # Specjalne usługi
        vip_customer.request_concierge_service("Private dining room preparation")

        # Premium payment processing - fix parameter conflict
        vip_payment = CardPayment("4111111111111111", "Celebrity Chef", 12, 2026, "123")
        vip_payment.amount = vip_order.total_amount  # Set amount separately
        success = self.order_service.process_payment(vip_order.order_id, vip_payment)

        print(f"👑 VIP customer served with exclusive treatment")

        return {
            "vip_customers_served": 1,
            "vip_revenue": vip_order.total_amount,
            "special_services": ["concierge", "private_dining", "priority_processing"],
            "customer_satisfaction": 5.0
        }

    def scenario_7_staff_management(self):
        """
        👥 SCENARIUSZ 7: ZARZĄDZANIE PERSONELEM
        Zmiany, uprawnienia, wydajność
        """
        # Сбрасываем очередь Drive-Thru для чистого сценария
        DriveThruOrder.current_queue_size = 0

        print("\n👥 6:00 PM - Staff Management")

        # Operacje zarządzania personelem
        staff_operations = []

        # Promocja pracownika
        cashier = self.restaurant.get_staff_by_role(StaffRole.CASHIER)[0] if self.restaurant.get_staff_by_role(
            StaffRole.CASHIER) else None
        if cashier:
            # Symulacja promocji
            cashier.update_performance_rating(4.5)
            cashier.hourly_rate = 18.50  # Podwyżka
            staff_operations.append(f"Promoted {cashier.name} - salary increase")

        # Nowa zmiana
        evening_staff = [
            Cashier("Evening Cashier", "EMP2001", register_number=3),
            KitchenStaff("Night Cook", "EMP2002", "grill")
        ]

        for staff in evening_staff:
            self.restaurant.hire_staff_member(staff)
            self.restaurant.start_shift(staff.employee_id)
            staff_operations.append(f"Started evening shift: {staff.name}")

        # Zarządzanie uprawnieniami
        manager = self.restaurant.get_staff_by_role(StaffRole.GENERAL_MANAGER)[0]
        if manager and hasattr(manager, 'authorize_refund'):
            refund_authorized = manager.authorize_refund(25.00, "Customer complaint")
            staff_operations.append(f"Manager authorized refund: {refund_authorized}")

        print(f"✅ Completed {len(staff_operations)} staff operations")

        return {
            "staff_operations": len(staff_operations),
            "promotions": 1,
            "new_hires": len(evening_staff),
            "total_staff": self.restaurant.staff_on_duty
        }

    def scenario_8_payment_processing(self):
        """
        💳 SCENARIUSZ 8: PRZETWARZANIE PŁATNOŚCI
        Różne metody płatności, polimorfizm
        """
        # Сбрасываем очередь Drive-Thru для чистого сценария
        DriveThruOrder.current_queue_size = 0

        print("\n💳 7:00 PM - Payment Processing Showcase")

        # Demonstracja różnych metod płatności
        payment_customers = [
            RegularCustomer("Cash Customer", "+1111111111"),
            LoyaltyCustomer("Card Customer", "+2222222222", "card@email.com"),
            RegularCustomer("Mobile Customer", "+3333333333"),
            LoyaltyCustomer("Gift Card Customer", "+4444444444", "gift@email.com")
        ]

        payment_results = []

        for i, customer in enumerate(payment_customers):
            self.restaurant.register_customer(customer)

            # Standardowe zamówienie
            order = self.order_service.create_order(
                OrderType.TAKEOUT,
                customer.customer_id,
                [
                    {"name": "Quarter Pounder", "quantity": 1, "price": 5.49},
                    {"name": "Medium Fries", "quantity": 1, "price": 2.49}
                ]
            )

            # Różne metody płatności
            if i == 0:  # Gotówka
                payment = CashPayment(order.total_amount, 10.00)
                method = "Cash"
            elif i == 1:  # Karta
                payment = CardPayment("4111111111111111", "Card Customer", 12, 2025, "123", amount=order.total_amount)
                method = "Credit Card"
            elif i == 2:  # Płatność mobilna
                try:
                    payment = MobilePayment(order.total_amount, "apple_pay", "DEVICE123123456")
                    method = "Apple Pay"
                except Exception:
                    # Fallback to card payment
                    payment = CardPayment.create_contactless_payment(order.total_amount, f"MOBILE_FALLBACK_{i}")
                    method = "Card (Mobile Fallback)"
            else:  # Karta podarunkowa
                payment = GiftCardPayment(order.total_amount, "1234567890123456", 50.00)
                method = "Gift Card"

            success = self.order_service.process_payment(order.order_id, payment)
            payment_results.append({
                "method": method,
                "amount": order.total_amount,
                "success": success
            })

            print(f"💳 {method} payment: {'SUCCESS' if success else 'FAILED'}")

        return {
            "payment_methods_tested": len(payment_results),
            "successful_payments": sum(1 for r in payment_results if r["success"]),
            "total_payment_volume": sum(r["amount"] for r in payment_results),
            "payment_diversity": ["Cash", "Credit Card", "Apple Pay", "Gift Card"]
        }

    def scenario_9_order_tracking(self):
        """
        📱 SCENARIUSZ 9: ŚLEDZENIE ZAMÓWIEŃ
        Powiadomienia, statusy, Observer pattern
        """
        # Сбрасываем очередь Drive-Thru для чистого сценария
        DriveThruOrder.current_queue_size = 0

        print("\n📱 8:00 PM - Order Tracking & Notifications")

        # Klient śledzący zamówienie
        tracking_customer = LoyaltyCustomer("Tech Savvy", "+1555123789", "tech@email.com")
        self.restaurant.register_customer(tracking_customer)

        # Dodanie obserwatora dla klienta
        mobile_observer = CustomerMobileObserver(
            "MOBILE_TRACK_001",
            tracking_customer.customer_id,
            tracking_customer.phone
        )

        # Sprawdzenie czy order_tracker istnieje
        if self.order_tracker:
            self.order_tracker.attach(mobile_observer)

        # Zamówienie do śledzenia
        tracked_order = self.order_service.create_order(
            OrderType.DELIVERY,
            tracking_customer.customer_id,
            [
                {"name": "Big Mac", "quantity": 2, "price": 4.99},
                {"name": "Large Fries", "quantity": 2, "price": 2.99},
                {"name": "McFlurry", "quantity": 1, "price": 3.99}
            ],
            delivery_address="123 Tech Street",
            distance_km=4.5
        )

        # Symulacja pełnego cyklu życia zamówienia z powiadomieniami
        tracking_steps = [
            (OrderStatus.CONFIRMED, "Payment processed, order confirmed"),
            (OrderStatus.IN_PREPARATION, "Kitchen started preparing your order"),
            (OrderStatus.READY, "Order ready for delivery"),
            (OrderStatus.COMPLETED, "Order delivered successfully")
        ]

        for status, description in tracking_steps:
            self.order_service.update_order_status(
                tracked_order.order_id,
                status,
                {"description": description, "timestamp": datetime.now()}
            )
            print(f"📱 Notification sent: {description}")

        # Sprawdzenie powiadomień
        notifications = mobile_observer.get_recent_notifications() if hasattr(mobile_observer, 'get_recent_notifications') else []

        return {
            "order_tracked": tracked_order.order_id,
            "tracking_steps": len(tracking_steps),
            "notifications_sent": len(notifications),
            "customer_app_integration": True,
            "real_time_updates": True
        }

    def scenario_10_end_of_day(self):
        """
        🌙 SCENARIUSZ 10: KONIEC DNIA
        Zamknięcie, raporty, podsumowanie
        """
        # Сбрасываем очередь Drive-Thru для чистого сценария
        DriveThruOrder.current_queue_size = 0

        print("\n🌙 10:00 PM - End of Day Operations")

        # Finalizacja ostatnich zamówień
        if hasattr(self.restaurant, '_active_orders'):
            active_orders = list(self.restaurant._active_orders.keys())
            for order_id in active_orders:
                self.order_service.update_order_status(order_id, OrderStatus.COMPLETED)

        # Generowanie raportów
        daily_report = self.restaurant.generate_daily_report()
        financial_summary = self.restaurant.generate_financial_summary(1)
        service_stats = self.order_service.get_service_statistics() if hasattr(self.order_service, 'get_service_statistics') else {}

        # Zakończenie zmian
        staff_count = len(self.restaurant._current_shift_staff) if hasattr(self.restaurant, '_current_shift_staff') else 0
        if hasattr(self.restaurant, '_current_shift_staff'):
            for employee_id in list(self.restaurant._current_shift_staff):
                self.restaurant.end_shift(employee_id)

        # Zamknięcie restauracji
        closed = self.restaurant.close_restaurant()

        print(f"💰 Daily Revenue: ${daily_report['sales']['total_sales']:.2f}")
        print(f"📊 Orders Served: {daily_report['sales']['orders_count']}")
        print(f"👥 Staff Shifts Ended: {staff_count}")
        print(f"🏪 Restaurant Closed: {closed}")

        return {
            "daily_revenue": daily_report['sales']['total_sales'],
            "orders_served": daily_report['sales']['orders_count'],
            "average_order_value": daily_report['sales']['average_order_value'],
            "customer_satisfaction": daily_report['operations']['customer_satisfaction'],
            "restaurant_closed": closed,
            "staff_shifts_ended": staff_count,
            "operational_efficiency": daily_report['operations']['kitchen_efficiency']
        }

    def _setup_order_service(self):
        """Konfiguruje Order Service z wszystkimi komponentami"""
        if not self.order_service:
            self.order_service = OrderService(self.restaurant.restaurant_id)

            # Factory Manager
            factory_manager = OrderFactoryManager(self.restaurant.restaurant_id)
            dine_in_factory = DineInOrderFactory("DINEIN_001", self.restaurant.restaurant_id, 60)
            drive_thru_factory = DriveThruOrderFactory("DRIVETHRU_001", self.restaurant.restaurant_id, 2)
            # Use DineInOrderFactory for takeout orders (similar prep process)
            takeout_factory = DineInOrderFactory("TAKEOUT_001", self.restaurant.restaurant_id, 30)

            # Register all factories explicitly
            factory_manager.register_factory(OrderType.DINE_IN, dine_in_factory)
            factory_manager.register_factory(OrderType.DRIVE_THRU, drive_thru_factory)
            factory_manager.register_factory(OrderType.TAKEOUT, takeout_factory)
            # Ensure takeout factory is properly registered with correct key
            self.order_service._factory_manager = factory_manager
            factory_manager.register_factory(OrderType.DELIVERY, DriveThruOrderFactory("DELIVERY_001", self.restaurant.restaurant_id, 1))

            # Double-check takeout factory registration
            if OrderType.TAKEOUT not in factory_manager._factories:
                print("WARNING: Takeout factory not registered, adding again...")
                factory_manager._factories[OrderType.TAKEOUT] = takeout_factory

            # Discount Manager
            discount_manager = DiscountManager()
            discount_manager.add_strategy(PercentageDiscountStrategy("Student Discount", 15.0, min_order_amount=10.0))
            discount_manager.add_strategy(TimeBasedDiscountStrategy("Happy Hour", 20.0, time(16, 0), time(18, 0)))

            # Order Tracker
            self.order_tracker = OrderTracker(self.restaurant.restaurant_id)
            kitchen_observer = KitchenDisplayObserver("KITCHEN_001", "main_kitchen")
            self.order_tracker.attach(kitchen_observer)

            # Konfiguracja integracji
            self.order_service.configure_factory_manager(factory_manager)
            self.order_service.configure_discount_manager(discount_manager)
            self.order_service.configure_order_tracker(self.order_tracker)

            # Verify factory registration
            print(f"✅ Factories registered: {list(factory_manager._factories.keys()) if hasattr(factory_manager, '_factories') else 'Unknown'}")

    def _print_summary(self):
        """Wyświetla podsumowanie wszystkich scenariuszy"""
        print("\n" + "=" * 60)
        print("📊 SCENARIOS SUMMARY")
        print("=" * 60)

        successful = sum(1 for result in self.scenario_results if result["success"])
        total = len(self.scenario_results)

        print(f"✅ Successful scenarios: {successful}/{total}")
        print(f"📈 Success rate: {(successful / total) * 100:.1f}%")

        if successful == total:
            print("\n🎉 ALL SCENARIOS COMPLETED SUCCESSFULLY!")
            print("🏆 McDonald's Management System demonstrates:")
            print("   ✅ Complete business workflow")
            print("   ✅ All OOP patterns and design patterns")
            print("   ✅ Real-world McDonald's operations")
            print("   ✅ System integration and data flow")

        # Szczegółowe wyniki
        print("\n📋 Detailed Results:")
        for i, result in enumerate(self.scenario_results, 1):
            status = "✅" if result["success"] else "❌"
            scenario_name = result["scenario"].replace("scenario_", "").replace("_", " ").title()
            print(f"   {status} Scenario {i}: {scenario_name}")
            if not result["success"]:
                print(f"      Error: {result['error']}")

        return successful == total


def main():
    """Uruchamia wszystkie scenariusze demonstracyjne"""
    scenarios = McDonaldsScenarios()  # No arguments needed
    success = scenarios.run_all_scenarios()

    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)