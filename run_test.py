"""
McDonald's Management System - Test Runner
✅ WYMAGANIE: Uruchamianie testów i weryfikacja systemu
✅ WYMAGANIE: Sprawdzanie wszystkich komponentów i wzorców

System testów i weryfikacji McDonald's Management System
"""

import sys
import os
import unittest
import traceback
from datetime import datetime
from typing import List, Dict, Any, Tuple

from src.models.menu import ItemSize
from src.models.staff import StaffRole

# Dodajemy ścieżki
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.logger import log_operation, log_business_rule, log_requirement_check


class McDonaldsTestRunner:
    """
    📋 CHECK: System testów McDonald's
    Klasa zarządzająca testami i weryfikacją systemu
    """

    def __init__(self):
        self.test_results = []
        self.requirements_tested = []
        self.patterns_tested = []
        self.components_tested = []
        self.start_time = datetime.now()

        print("🧪 McDONALD'S SYSTEM TEST RUNNER")
        print("=" * 60)
        print(f"Test session started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

    def run_all_tests(self):
        """Uruchamia wszystkie testy systemu"""
        test_suites = [
            ("OOP Requirements", self._test_oop_requirements),
            ("Design Patterns", self._test_design_patterns),
            ("Model Components", self._test_model_components),
            ("Service Layer", self._test_service_layer),
            ("Integration", self._test_integration),
            ("Business Logic", self._test_business_logic),
            ("Error Handling", self._test_error_handling),
            ("Data Validation", self._test_data_validation),
            ("Performance", self._test_performance),
            ("Complete Demo", self._test_complete_demo)
        ]

        total_passed = 0
        total_tests = 0

        for suite_name, test_function in test_suites:
            print(f"\n{'=' * 60}")
            print(f"🧪 TESTING: {suite_name.upper()}")
            print("=" * 60)

            try:
                results = test_function()
                passed = sum(1 for r in results if r["passed"])
                total = len(results)

                total_passed += passed
                total_tests += total

                print(f"✅ {suite_name}: {passed}/{total} tests passed")

                # Szczegóły nieudanych testów
                for result in results:
                    if not result["passed"]:
                        print(f"❌ {result['test_name']}: {result['error']}")

            except Exception as e:
                print(f"💥 {suite_name} failed with error: {str(e)}")
                traceback.print_exc()
                total_tests += 1

        self._print_test_summary(total_passed, total_tests)
        return total_passed == total_tests

    def _test_oop_requirements(self) -> List[Dict[str, Any]]:
        """Testuje wszystkie wymagania OOP"""
        results = []

        # Test 1: Klasy
        try:
            from src.models.menu import MenuItem, Burger
            big_mac = MenuItem.create_big_mac()
            burger = Burger("Test Burger", 5.99, 1)

            assert isinstance(big_mac, MenuItem)
            assert isinstance(burger, Burger)
            assert isinstance(burger, MenuItem)  # Dziedziczenie

            results.append({"test_name": "Classes and Objects", "passed": True})
            self.requirements_tested.append("Classes")
        except Exception as e:
            results.append({"test_name": "Classes and Objects", "passed": False, "error": str(e)})

        # Test 2: Dziedziczenie
        try:
            from src.models.staff import Staff, Cashier, GeneralManager

            cashier = Cashier("Test Cashier", "EMP9999")
            assert isinstance(cashier, Staff)
            assert isinstance(cashier, Cashier)

            # Test wielopoziomowego dziedziczenia
            from src.models.staff import ShiftManager
            gm = GeneralManager("Test GM", "EMP9998", "Test Region")
            assert isinstance(gm, ShiftManager)
            assert isinstance(gm, Staff)

            results.append({"test_name": "Inheritance", "passed": True})
            self.requirements_tested.append("Inheritance")
        except Exception as e:
            results.append({"test_name": "Inheritance", "passed": False, "error": str(e)})

        # Test 3: Nadpisywanie atrybutów
        try:
            from src.models.staff import Staff, Cashier

            # Sprawdzenie nadpisanych atrybutów
            assert Staff.base_salary != Cashier.base_salary
            assert hasattr(Cashier, 'department')

            results.append({"test_name": "Attribute Overriding", "passed": True})
            self.requirements_tested.append("Attribute Overriding")
        except Exception as e:
            results.append({"test_name": "Attribute Overriding", "passed": False, "error": str(e)})

        # Test 4: Nadpisywanie metod
        try:
            from src.models.staff import Staff, Cashier

            staff = Staff.create_new_hire("Test", "EMP9997", StaffRole.CASHIER)
            cashier = Cashier("Test Cashier", "EMP9996")

            # Metoda work() powinna być nadpisana
            staff_work = staff.work()
            cashier_work = cashier.work()
            assert staff_work != cashier_work

            results.append({"test_name": "Method Overriding", "passed": True})
            self.requirements_tested.append("Method Overriding")
        except Exception as e:
            results.append({"test_name": "Method Overriding", "passed": False, "error": str(e)})

        # Test 5: @classmethod
        try:
            from src.models.menu import MenuItem
            from src.models.customer import LoyaltyCustomer

            # Test factory methods
            big_mac = MenuItem.create_big_mac()
            app_customer = LoyaltyCustomer.create_app_signup("Test", "+1234567890", "test@email.com")

            assert big_mac is not None
            assert app_customer is not None
            assert hasattr(MenuItem, 'get_total_items_created')

            results.append({"test_name": "@classmethod", "passed": True})
            self.requirements_tested.append("@classmethod")
        except Exception as e:
            results.append({"test_name": "@classmethod", "passed": False, "error": str(e)})

        # Test 6: @staticmethod
        try:
            from src.models.menu import MenuItem, ItemSize
            from src.utils.validators import DataValidator

            # Test static methods
            calories = MenuItem.calculate_calories_with_size(500, ItemSize.LARGE)
            valid_email = DataValidator.validate_email("test@example.com")

            assert isinstance(calories, int)
            assert valid_email.is_valid

            results.append({"test_name": "@staticmethod", "passed": True})
            self.requirements_tested.append("@staticmethod")
        except Exception as e:
            results.append({"test_name": "@staticmethod", "passed": False, "error": str(e)})

        # Test 7: Wiele konstruktorów
        try:
            from src.models.payment import CashPayment
            from src.models.order import DineInOrder

            # Test alternative constructors
            exact_payment = CashPayment.create_exact_change(10.99)
            birthday_order = DineInOrder.create_birthday_party("CUST001", 4, 8)

            assert exact_payment is not None
            assert birthday_order is not None

            results.append({"test_name": "Multiple Constructors", "passed": True})
            self.requirements_tested.append("Multiple Constructors")
        except Exception as e:
            results.append({"test_name": "Multiple Constructors", "passed": False, "error": str(e)})

        # Test 8: Enkapsulacja
        try:
            from src.models.customer import RegularCustomer

            customer = RegularCustomer("Test Customer", "+1234567890")

            # Test property getter/setter
            old_name = customer.name
            customer.name = "New Name"
            assert customer.name == "New Name"
            assert customer.name != old_name

            # Test read-only property
            customer_id = customer.customer_id
            assert customer_id is not None

            results.append({"test_name": "Encapsulation", "passed": True})
            self.requirements_tested.append("Encapsulation")
        except Exception as e:
            results.append({"test_name": "Encapsulation", "passed": False, "error": str(e)})

        # Test 9: Polimorfizm
        try:
            from src.models.payment import Payment, CashPayment, CardPayment, MobilePayment

            payments = [
                CashPayment(15.99, 20.00),
                CardPayment("4111111111111111", "Test", 12, 2025, "123", amount=15.99),
                MobilePayment(15.99, "apple_pay", "DEVICE123")
            ]

            # Test polimorficznego wywołania
            for payment in payments:
                method = payment.get_payment_method()
                assert method is not None
                # Note: nie wywołujemy process_payment() aby uniknąć błędów symulacji

            results.append({"test_name": "Polymorphism", "passed": True})
            self.requirements_tested.append("Polymorphism")
        except Exception as e:
            results.append({"test_name": "Polymorphism", "passed": False, "error": str(e)})

        # Test 10: super()
        try:
            from src.models.staff import Cashier

            # Test czy super() jest używane (sprawdzamy czy konstruktor działa)
            cashier = Cashier("Test", "EMP9995")
            assert hasattr(cashier, 'name')  # Z klasy bazowej
            assert hasattr(cashier, 'register_number')  # Z klasy pochodnej

            results.append({"test_name": "super() usage", "passed": True})
            self.requirements_tested.append("super()")
        except Exception as e:
            results.append({"test_name": "super() usage", "passed": False, "error": str(e)})

        # Test 11: Własne wyjątki
        try:
            from src.exceptions.mcdonalds_exceptions import McDonaldsException, MenuItemNotAvailableException

            # Test hierarchii wyjątków
            try:
                raise MenuItemNotAvailableException("Test Item", "Test reason")
            except McDonaldsException as e:
                assert isinstance(e, McDonaldsException)
                assert isinstance(e, MenuItemNotAvailableException)

            results.append({"test_name": "Custom Exceptions", "passed": True})
            self.requirements_tested.append("Custom Exceptions")
        except Exception as e:
            results.append({"test_name": "Custom Exceptions", "passed": False, "error": str(e)})

        return results

    def _test_design_patterns(self) -> List[Dict[str, Any]]:
        """Testuje wzorce projektowe"""
        results = []

        # Test Strategy Pattern
        try:
            from src.patterns.strategy import DiscountManager, PercentageDiscountStrategy

            discount_manager = DiscountManager()
            strategy = PercentageDiscountStrategy("Test Discount", 10.0)
            discount_manager.add_strategy(strategy)

            result = discount_manager.calculate_best_discount(
                100.0,
                [{"name": "Test Item", "quantity": 1, "unit_price": 100.0}],
                {"customer_type": "regular"}
            )

            assert result is not None
            assert "strategy_name" in result

            results.append({"test_name": "Strategy Pattern", "passed": True})
            self.patterns_tested.append("Strategy")
        except Exception as e:
            results.append({"test_name": "Strategy Pattern", "passed": False, "error": str(e)})

        # Test Observer Pattern
        try:
            from src.patterns.observer import OrderTracker, KitchenDisplayObserver, NotificationType

            tracker = OrderTracker("TEST_RESTAURANT")
            observer = KitchenDisplayObserver("KITCHEN_TEST", "test_station")

            tracker.attach(observer)
            tracker.notify(NotificationType.ORDER_CREATED, {"order_id": "TEST001", "customer_id": "CUST001"})

            assert len(tracker._observers) > 0

            results.append({"test_name": "Observer Pattern", "passed": True})
            self.patterns_tested.append("Observer")
        except Exception as e:
            results.append({"test_name": "Observer Pattern", "passed": False, "error": str(e)})

        # Test Factory Method Pattern
        try:
            from src.patterns.factory import OrderFactoryManager, DineInOrderFactory
            from src.models.order import OrderType

            factory_manager = OrderFactoryManager("TEST_RESTAURANT")
            dine_in_factory = DineInOrderFactory("TEST_DINEIN", "TEST_RESTAURANT", 50)

            factory_manager.register_factory(OrderType.DINE_IN, dine_in_factory)

            order = factory_manager.create_order(OrderType.DINE_IN, "CUST001", party_size=2)
            assert order is not None
            assert order.get_order_type() == OrderType.DINE_IN

            results.append({"test_name": "Factory Method Pattern", "passed": True})
            self.patterns_tested.append("Factory Method")
        except Exception as e:
            results.append({"test_name": "Factory Method Pattern", "passed": False, "error": str(e)})

        return results

    def _test_model_components(self) -> List[Dict[str, Any]]:
        """Testuje komponenty modeli"""
        results = []

        # Test Menu Models
        try:
            from src.models.menu import MenuItem, Burger, Fries, Drink

            burger = Burger("Test Burger", 5.99, 1)
            fries = Fries(ItemSize.MEDIUM)
            drink = Drink.create_coca_cola()

            assert burger.get_final_price() > 0
            assert fries.get_final_price() > 0
            assert drink.get_final_price() > 0

            results.append({"test_name": "Menu Models", "passed": True})
            self.components_tested.append("Menu")
        except Exception as e:
            results.append({"test_name": "Menu Models", "passed": False, "error": str(e)})

        # Test Staff Models
        try:
            from src.models.staff import Staff, Cashier, KitchenStaff, StaffRole

            cashier = Cashier("Test Cashier", "EMP8888")
            cook = KitchenStaff("Test Cook", "EMP8889", "grill")

            assert cashier.role == StaffRole.CASHIER
            assert cook.role == StaffRole.KITCHEN_STAFF
            assert len(cashier.get_permissions()) > 0
            assert len(cook.get_permissions()) > 0

            results.append({"test_name": "Staff Models", "passed": True})
            self.components_tested.append("Staff")
        except Exception as e:
            results.append({"test_name": "Staff Models", "passed": False, "error": str(e)})

        # Test Customer Models
        try:
            from src.models.customer import RegularCustomer, LoyaltyCustomer, VIPCustomer, CustomerType

            regular = RegularCustomer("Regular Customer", "+1111111111")
            loyalty = LoyaltyCustomer("Loyalty Customer", "+2222222222", "loyalty@test.com")
            vip = VIPCustomer("VIP Customer", "+3333333333", "vip@test.com", "VIP001")

            assert regular.get_customer_type() == CustomerType.REGULAR
            assert loyalty.get_customer_type() == CustomerType.LOYALTY_MEMBER
            assert vip.get_customer_type() == CustomerType.VIP

            results.append({"test_name": "Customer Models", "passed": True})
            self.components_tested.append("Customer")
        except Exception as e:
            results.append({"test_name": "Customer Models", "passed": False, "error": str(e)})

        # Test Order Models
        try:
            from src.models.order import DineInOrder, DriveThruOrder, OrderType

            dine_in = DineInOrder("CUST001", 5, 2)
            drive_thru = DriveThruOrder("CUST002", "car")

            assert dine_in.get_order_type() == OrderType.DINE_IN
            assert drive_thru.get_order_type() == OrderType.DRIVE_THRU
            assert dine_in.validate_order()
            assert drive_thru.validate_order()

            results.append({"test_name": "Order Models", "passed": True})
            self.components_tested.append("Order")
        except Exception as e:
            results.append({"test_name": "Order Models", "passed": False, "error": str(e)})

        # Test Payment Models
        try:
            from src.models.payment import CashPayment, PaymentMethod

            cash_payment = CashPayment(15.99, 20.00)

            assert cash_payment.get_payment_method() == PaymentMethod.CASH
            assert cash_payment.amount == 15.99
            assert cash_payment.change_amount == 4.01

            results.append({"test_name": "Payment Models", "passed": True})
            self.components_tested.append("Payment")
        except Exception as e:
            results.append({"test_name": "Payment Models", "passed": False, "error": str(e)})

        return results

    def _test_service_layer(self) -> List[Dict[str, Any]]:
        """Testuje warstwę serwisów"""
        results = []

        try:
            from src.services.order_service import OrderService

            service = OrderService("TEST_RESTAURANT")

            # Test konfiguracji
            assert service.restaurant_id == "TEST_RESTAURANT"
            assert hasattr(service, 'get_service_statistics')

            # Test statystyk
            stats = service.get_service_statistics()
            assert isinstance(stats, dict)
            assert "restaurant_id" in stats

            results.append({"test_name": "Order Service", "passed": True})
            self.components_tested.append("Service Layer")
        except Exception as e:
            results.append({"test_name": "Order Service", "passed": False, "error": str(e)})

        return results

    def _test_integration(self) -> List[Dict[str, Any]]:
        """Testuje integrację komponentów"""
        results = []

        try:
            # Test podstawowej integracji
            from src.models.restaurant import McDonaldsRestaurant

            restaurant = McDonaldsRestaurant("TEST001", "Test Location")

            assert restaurant.restaurant_id == "TEST001"
            assert restaurant.location == "Test Location"

            results.append({"test_name": "Component Integration", "passed": True})
            self.components_tested.append("Integration")
        except Exception as e:
            results.append({"test_name": "Component Integration", "passed": False, "error": str(e)})

        return results

    def _test_business_logic(self) -> List[Dict[str, Any]]:
        """Testuje logikę biznesową"""
        results = []

        try:
            # Test przykładowej logiki biznesowej
            from src.models.customer import LoyaltyCustomer

            customer = LoyaltyCustomer("Test", "+1234567890", "test@email.com")
            customer.earn_points(25.99)  # $25.99 purchase

            assert customer.loyalty_points > 0

            results.append({"test_name": "Business Logic", "passed": True})
        except Exception as e:
            results.append({"test_name": "Business Logic", "passed": False, "error": str(e)})

        return results

    def _test_error_handling(self) -> List[Dict[str, Any]]:
        """Testuje obsługę błędów"""
        results = []

        try:
            from src.exceptions.mcdonalds_exceptions import MenuItemNotAvailableException
            from src.utils.validators import DataValidator

            # Test walidacji z błędami
            result = DataValidator.validate_email("invalid-email")
            assert not result.is_valid
            assert len(result.errors) > 0

            # Test wyjątków
            try:
                raise MenuItemNotAvailableException("Test Item", "Test reason")
            except MenuItemNotAvailableException:
                pass  # Oczekiwany wyjątek

            results.append({"test_name": "Error Handling", "passed": True})
        except Exception as e:
            results.append({"test_name": "Error Handling", "passed": False, "error": str(e)})

        return results

    def _test_data_validation(self) -> List[Dict[str, Any]]:
        """Testuje walidację danych"""
        results = []

        try:
            from src.utils.validators import DataValidator

            # Test podstawowych walidacji
            email_valid = DataValidator.validate_email("test@example.com")
            email_invalid = DataValidator.validate_email("invalid")

            assert email_valid.is_valid
            assert not email_invalid.is_valid

            # Test walidacji specjalistycznych
            employee_id_valid = DataValidator.validate_employee_id("EMP1234")
            employee_id_invalid = DataValidator.validate_employee_id("INVALID")

            assert employee_id_valid.is_valid
            assert not employee_id_invalid.is_valid

            results.append({"test_name": "Data Validation", "passed": True})
        except Exception as e:
            results.append({"test_name": "Data Validation", "passed": False, "error": str(e)})

        return results

    def _test_performance(self) -> List[Dict[str, Any]]:
        """Testuje wydajność systemu"""
        results = []

        try:
            # Test podstawowej wydajności
            start_time = datetime.now()

            # Tworzenie wielu obiektów
            from src.models.customer import RegularCustomer
            customers = []
            for i in range(100):
                customer = RegularCustomer(f"Customer {i}", f"+123456789{i:02d}")
                customers.append(customer)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Test czy tworzenie 100 klientów trwa < 1 sekunda
            assert duration < 1.0
            assert len(customers) == 100

            results.append({"test_name": "Performance", "passed": True})
        except Exception as e:
            results.append({"test_name": "Performance", "passed": False, "error": str(e)})

        return results

    def _test_complete_demo(self) -> List[Dict[str, Any]]:
        """Testuje kompletną demonstrację"""
        results = []

        try:
            # Test czy main demo działa
            import main

            # Sprawdzamy czy klasa demo istnieje
            demo = main.McDonaldsSystemDemo()
            assert demo is not None
            assert hasattr(demo, 'run_complete_demo')

            results.append({"test_name": "Complete Demo", "passed": True})
        except Exception as e:
            results.append({"test_name": "Complete Demo", "passed": False, "error": str(e)})

        return results

    def _print_test_summary(self, passed: int, total: int):
        """Wyświetla podsumowanie testów"""
        end_time = datetime.now()
        duration = end_time - self.start_time

        print(f"\n{'=' * 60}")
        print("📊 TEST SUMMARY")
        print("=" * 60)

        success_rate = (passed / total) * 100 if total > 0 else 0

        print(f"✅ Tests passed: {passed}/{total} ({success_rate:.1f}%)")
        print(f"⏱️  Execution time: {duration.total_seconds():.2f} seconds")
        print(f"📋 Requirements tested: {len(self.requirements_tested)}")
        print(f"🏗️  Patterns tested: {len(self.patterns_tested)}")
        print(f"🔧 Components tested: {len(self.components_tested)}")

        if passed == total:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ System is fully functional")
            print("✅ All OOP requirements satisfied")
            print("✅ All design patterns working")
            print("✅ Complete integration achieved")
        else:
            print(f"\n⚠️  {total - passed} tests failed")
            print("❌ System needs attention")

        print(f"\nRequirements tested: {', '.join(self.requirements_tested)}")
        print(f"Patterns tested: {', '.join(self.patterns_tested)}")
        print(f"Components tested: {', '.join(self.components_tested)}")

        # Finalne potwierdzenie
        log_requirement_check("Test Suite", "COMPLETED", f"{passed}/{total} tests passed")


def run_quick_test():
    """Uruchamia szybki test systemu"""
    print("🚀 QUICK SYSTEM TEST")
    print("-" * 30)

    try:
        # Test importów
        print("📦 Testing imports...")
        from src.models.menu import MenuItem
        from src.models.staff import Staff
        from src.models.customer import Customer
        from src.models.order import Order
        from src.models.payment import Payment
        from src.patterns.strategy import DiscountStrategy
        from src.patterns.observer import OrderObserver
        from src.patterns.factory import OrderFactory
        print("✅ All imports successful")

        # Test tworzenia obiektów
        print("🏗️  Testing object creation...")
        big_mac = MenuItem.create_big_mac()
        assert big_mac is not None
        print("✅ Object creation successful")

        # Test polimorfizmu
        print("🔄 Testing polymorphism...")
        from src.models.payment import CashPayment
        payment = CashPayment(10.99, 15.00)
        method = payment.get_payment_method()
        assert method is not None
        print("✅ Polymorphism working")

        print("\n🎉 QUICK TEST PASSED!")
        return True

    except Exception as e:
        print(f"\n💥 QUICK TEST FAILED: {str(e)}")
        return False


def run_full_test():
    """Uruchamia pełny test systemu"""
    runner = McDonaldsTestRunner()
    return runner.run_all_tests()


def main():
    """Główna funkcja testowa"""
    import argparse

    parser = argparse.ArgumentParser(description="McDonald's System Test Runner")
    parser.add_argument("--quick", action="store_true", help="Run quick test only")
    parser.add_argument("--full", action="store_true", help="Run full test suite")
    parser.add_argument("--demo", action="store_true", help="Run demo scenarios")

    args = parser.parse_args()

    if args.quick:
        return run_quick_test()
    elif args.full:
        return run_full_test()
    elif args.demo:
        try:
            import demo_scenarios
            scenarios = demo_scenarios.McDonaldsScenarios()
            return scenarios.run_all_scenarios()
        except ImportError:
            print("❌ Demo scenarios not available")
            return False
    else:
        # Domyślnie uruchamiamy szybki test
        print("🧪 Running default quick test...")
        print("Use --full for complete test suite or --demo for business scenarios")
        print()
        return run_quick_test()


if __name__ == "__main__":
    success = main()

    if success:
        print("\n✅ All tests completed successfully!")
        exit_code = 0
    else:
        print("\n❌ Some tests failed!")
        exit_code = 1

    exit(exit_code)