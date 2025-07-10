# 🍟 McDonald's Management System

**Kompleksowy system zarządzania restauracją McDonald's demonstrujący wszystkie wzorce OOP i wzorce projektowe**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![OOP](https://img.shields.io/badge/OOP-11%2F11%20Requirements-green.svg)](#wymagania-oop)
[![Design Patterns](https://img.shields.io/badge/Design%20Patterns-3%2F3%20Implemented-green.svg)](#wzorce-projektowe)
[![Tests](https://img.shields.io/badge/Tests-Passing-green.svg)](#testy)

## 📋 Spis treści

- [Opis projektu](#opis-projektu)
- [Wymagania OOP](#wymagania-oop)
- [Wzorce projektowe](#wzorce-projektowe)
- [Struktura projektu](#struktura-projektu)
- [Instalacja i uruchomienie](#instalacja-i-uruchomienie)
- [Demonstracja](#demonstracja)
- [Dokumentacja komponentów](#dokumentacja-komponentów)
- [Testy](#testy)
- [Scenariusze biznesowe](#scenariusze-biznesowe)

## 🎯 Opis projektu

McDonald's Management System to kompleksowa aplikacja demonstracyjna implementująca wszystkie wymagane wzorce programowania obiektowego oraz wzorce projektowe. System symuluje rzeczywiste operacje restauracji McDonald's, w tym:

- 🍔 **Zarządzanie menu** - pozycje, ceny, składniki, dostępność
- 👥 **System personelu** - role, uprawnienia, zmany, zarządzanie
- 👤 **Obsługa klientów** - rejestracja, program lojalnościowy, VIP
- 📝 **Przetwarzanie zamówień** - różne typy, statusy, śledzenie
- 💳 **System płatności** - gotówka, karty, płatności mobilne, polimorfizm
- 🏪 **Operacje restauracji** - otwarcie/zamknięcie, raporty, analityka

### ✨ Kluczowe cechy

- ✅ **Wszystkie 11 wymagań OOP** - klasy, dziedziczenie, polimorfizm, enkapsulacja
- ✅ **3 wzorce projektowe** - Strategy, Observer, Factory Method
- ✅ **Pełna integracja** - wszystkie komponenty współpracują
- ✅ **Realistyczne scenariusze** - prawdziwe przypadki użycia McDonald's
- ✅ **System logowania** - pełne śledzenie operacji
- ✅ **Walidacja danych** - bezpieczne przetwarzanie
- ✅ **Testy jednostkowe** - weryfikacja funkcjonalności

## 📚 Wymagania OOP

### ✅ Wszystkie 11 wymagań zaimplementowane

| # | Wymaganie | Status | Implementacja |
|---|-----------|--------|---------------|
| 1 | **Użycie klas** | ✅ | Wszystkie modele jako klasy (`models/`) |
| 2 | **Dziedziczenie** | ✅ | `Burger(MenuItem)`, `Cashier(Staff)`, etc. |
| 3 | **Nadpisywanie atrybutów** | ✅ | `base_salary`, `department` w podklasach |
| 4 | **Nadpisywanie metod** | ✅ | `work()`, `get_final_price()` w podklasach |
| 5 | **@classmethod** | ✅ | `create_big_mac()`, `create_app_signup()` |
| 6 | **@staticmethod** | ✅ | `calculate_calories()`, `validate_email()` |
| 7 | **Wiele konstruktorów** | ✅ | `create_exact_change()`, `create_birthday_party()` |
| 8 | **Enkapsulacja** | ✅ | `@property` getters/setters, prywatne atrybuty |
| 9 | **Polimorfizm** | ✅ | `process_payment()` - różne implementacje |
| 10 | **super()** | ✅ | Wszystkie konstruktory i metody podklas |
| 11 | **Własne wyjątki** | ✅ | Hierarchia `McDonaldsException` |

### 🔍 Przykłady implementacji

```python
# Dziedziczenie + nadpisywanie metod + super()
class Burger(MenuItem):
    def get_final_price(self, size: ItemSize = ItemSize.MEDIUM) -> float:
        base = self.base_price
        if self.patty_count > 1:
            base += (self.patty_count - 1) * 1.50
        return base

# @classmethod - wiele konstruktorów
@classmethod
def create_big_mac(cls):
    ingredients = ["special sauce", "lettuce", "cheese"]
    return cls("Big Mac", 4.99, MenuCategory.BURGERS, ingredients, 550)

# Polimorfizm - jeden interfejs, różne implementacje
def process_any_payment(payment: Payment) -> bool:
    return payment.process_payment()  # Polimorficzne wywołanie

# Enkapsulacja - properties
@property
def name(self) -> str:
    return self._name

@name.setter
def name(self, value: str):
    if not value.strip():
        raise ValueError("Name cannot be empty")
    self._name = value.strip()
```

## 🏗️ Wzorce projektowe

### 1. 🎯 Strategy Pattern (`patterns/strategy.py`)

**Cel:** Różne strategie naliczania rabatów

```python
# Abstrakcyjna strategia
class DiscountStrategy(ABC):
    @abstractmethod
    def calculate_discount(self, order_total: float, order_items: List[Dict]) -> Dict[str, Any]:
        pass

# Konkretne strategie
class PercentageDiscountStrategy(DiscountStrategy):
    def calculate_discount(self, order_total, order_items, customer_data):
        return {"discount_amount": order_total * (self.percentage / 100.0)}

class TimeBasedDiscountStrategy(DiscountStrategy):
    def calculate_discount(self, order_total, order_items, customer_data):
        if self._is_happy_hour():
            return {"discount_amount": order_total * 0.20}  # 20% off
        return {"discount_amount": 0.0}

# Kontekst
class DiscountManager:
    def calculate_best_discount(self, order_total, order_items, customer_data):
        best_discount = {"discount_amount": 0.0}
        for strategy in self._strategies:
            result = strategy.apply_discount(order_total, order_items, customer_data)
            if result["discount_amount"] > best_discount["discount_amount"]:
                best_discount = result
        return best_discount
```

**Zalety:**
- ✅ Łatwe dodawanie nowych strategii rabatowych
- ✅ Enkapsulacja algorytmów rabatowych
- ✅ Wybór najlepszej strategii w runtime

### 2. 👁️ Observer Pattern (`patterns/observer.py`)

**Cel:** System powiadomień o statusie zamówień

```python
# Subject (Observable)
class OrderTracker(OrderNotificationSubject):
    def notify(self, notification_type: NotificationType, data: Dict):
        for observer in self._observers:
            if observer._is_active:
                observer.update(self, notification_type, data)

# Observer interface
class OrderObserver(ABC):
    @abstractmethod
    def update(self, subject: OrderNotificationSubject, notification_type: NotificationType, data: Dict):
        pass

# Concrete Observers
class KitchenDisplayObserver(OrderObserver):
    def update(self, subject, notification_type, data):
        if notification_type == NotificationType.ORDER_CONFIRMED:
            self._add_to_preparation_queue(data["order_id"])

class CustomerMobileObserver(OrderObserver):
    def update(self, subject, notification_type, data):
        self._send_push_notification(notification_type, data)
```

**Zalety:**
- ✅ Luźne powiązanie między zamówieniami a systemami powiadomień
- ✅ Automatyczne powiadomienia wszystkich zainteresowanych
- ✅ Łatwe dodawanie nowych typów obserwatorów

### 3. 🏭 Factory Method Pattern (`patterns/factory.py`)

**Cel:** Tworzenie różnych typów zamówień

```python
# Abstract Factory
class OrderFactory(ABC):
    @abstractmethod
    def create_order(self, customer_id: str = "", **kwargs) -> Order:
        pass

# Concrete Factories
class DineInOrderFactory(OrderFactory):
    def create_order(self, customer_id: str = "", **kwargs) -> DineInOrder:
        table_number = self._assign_table(kwargs.get('party_size', 1))
        return DineInOrder(customer_id, table_number, kwargs.get('party_size', 1))

class DriveThruOrderFactory(OrderFactory):
    def create_order(self, customer_id: str = "", **kwargs) -> DriveThruOrder:
        lane_number = self._assign_lane()
        return DriveThruOrder(customer_id, kwargs.get('vehicle_type', 'car'))

# Factory Manager
class OrderFactoryManager:
    def create_order(self, order_type: OrderType, customer_id: str, **kwargs) -> Order:
        factory = self._factories[order_type]
        return factory.create_order(customer_id, **kwargs)
```

**Zalety:**
- ✅ Enkapsulacja logiki tworzenia obiektów
- ✅ Łatwe dodawanie nowych typów zamówień
- ✅ Pojedyncza odpowiedzialność każdej fabryki

## 📁 Struktura projektu

```
mcdonalds_system/
├── 📁 src/
│   ├── 📁 models/                  # Modele danych
│   │   ├── menu.py                 # System menu (MenuItem, Burger, Fries, Drink)
│   │   ├── staff.py                # Personel (Staff, Cashier, Manager)
│   │   ├── customer.py             # Klienci (Customer, Loyalty, VIP)
│   │   ├── order.py                # Zamówienia (Order, DineIn, DriveThru, Delivery)
│   │   ├── payment.py              # Płatności (Payment, Cash, Card, Mobile)
│   │   └── restaurant.py           # Główna klasa restauracji
│   ├── 📁 services/
│   │   └── order_service.py        # Warstwa biznesowa zamówień
│   ├── 📁 patterns/
│   │   ├── strategy.py             # Strategy Pattern - rabaty
│   │   ├── observer.py             # Observer Pattern - powiadomienia
│   │   └── factory.py              # Factory Method - tworzenie zamówień
│   ├── 📁 exceptions/
│   │   └── mcdonalds_exceptions.py # Własne wyjątki
│   └── 📁 utils/
│       ├── validators.py           # Walidacja danych
│       └── logger.py               # System logowania
├── 📁 tests/
│   └── ...                         # Testy jednostkowe
├── 📁 docs/
│   ├── README.md                   # Ten plik
│   └── REQUIREMENTS_CHECK.md       # Szczegółowa lista kontrolna
├── main.py                         # Główna aplikacja demonstracyjna
├── demo_scenarios.py               # Scenariusze biznesowe McDonald's
├── run_tests.py                    # Uruchamianie testów
└── requirements.txt                # Zależności Python
```

## 🚀 Instalacja i uruchomienie

### Wymagania systemowe

- Python 3.8+
- Brak zewnętrznych zależności (pure Python)

### Instalacja

```bash
# Klonowanie projektu
git clone <repository-url>
cd mcdonalds_system

# Instalacja zależności (opcjonalne - projekt używa tylko standardowej biblioteki)
pip install -r requirements.txt

# Sprawdzenie instalacji
python --version
```

### Uruchomienie

```bash
# Główna demonstracja systemu
python main.py

# Scenariusze biznesowe McDonald's
python demo_scenarios.py

# Szybki test systemu
python run_tests.py --quick

# Pełny test systemu
python run_tests.py --full

# Testy scenariuszy biznesowych
python run_tests.py --demo
```

## 🎬 Demonstracja

### Główna aplikacja (`main.py`)

Kompletna demonstracja wszystkich komponentów:

```bash
python main.py
```

**Co demonstruje:**
- ✅ Wszystkie 11 wymagań OOP
- ✅ 3 wzorce projektowe
- ✅ Integrację komponentów
- ✅ Scenariusze biznesowe
- ✅ Polimorfizm w działaniu

**Przykładowe wyjście:**
```
🍟 MCDONALD'S MANAGEMENT SYSTEM
============================================================
Demo started at: 2024-01-15 10:30:00
Integrating all components and design patterns...

🚀 STARTING COMPLETE SYSTEM DEMONSTRATION
============================================================

🏗️  SYSTEM INITIALIZATION
----------------------------------------
✅ Restaurant created: MCD0001
✅ Order Service initialized
✅ Factory Manager created
✅ Discount Manager created
✅ Order Tracker created

🔧 COMPONENT CONFIGURATION
----------------------------------------
✅ Factory patterns configured
✅ Strategy patterns configured
✅ Observer patterns configured
✅ Order Service integration complete

🎯 OOP PATTERNS DEMONSTRATION
----------------------------------------

1. CLASSES
   Class instance: Big Mac - $4.99 (burgers) (MenuItem)

2. INHERITANCE
   Inheritance: Demo Burger - $5.99 (burgers) (Burger → MenuItem)
   Inheritance: Demo Cashier - cashier (Cashier → Staff)

3. ATTRIBUTE OVERRIDING
   MenuItem base_salary: 1
   Burger default_prep_time: 6

[... continues with all OOP requirements ...]

📋 FINAL SYSTEM REPORT
============================================================

🏪 RESTAURANT STATISTICS
   Restaurant Status: closed
   Active Orders: 0
   Staff Members: 5
   Customers: 9
   Orders Processed: 8
   Payments Processed: 8

✅ OOP REQUIREMENTS CHECKED: 11
   ✅ Classes and Objects
   ✅ Inheritance
   [... all 11 requirements ...]

🏗️  DESIGN PATTERNS: 3
   ✅ Strategy Pattern
   ✅ Observer Pattern
   ✅ Factory Method Pattern

🎉 ALL REQUIREMENTS SUCCESSFULLY DEMONSTRATED
```

### Scenariusze biznesowe (`demo_scenarios.py`)

Realistyczne scenariusze operacji McDonald's:

```bash
python demo_scenarios.py
```

**10 scenariuszy:**
1. 🌅 **Poranny ruch** - otwarcie, personel, pierwsi klienci
2. 👨‍👩‍👧‍👦 **Rodzinny obiad** - Happy Meals, urodziny
3. 🚗 **Szczyt Drive-Thru** - kolejki, szybka obsługa
4. 🚚 **Zamówienia z dostawą** - aplikacja, kierowcy
5. 🕒 **Rabaty Happy Hour** - promocje czasowe
6. 👑 **Obsługa VIP** - specjalna obsługa
7. 👥 **Zarządzanie personelem** - zmiany, uprawnienia
8. 💳 **Przetwarzanie płatności** - polimorfizm metod
9. 📱 **Śledzenie zamówień** - powiadomienia real-time
10. 🌙 **Koniec dnia** - zamknięcie, raporty

## 📖 Dokumentacja komponentów

### 🍔 Models (`src/models/`)

#### Menu System (`menu.py`)
- **MenuItem** - bazowa klasa pozycji menu
- **Burger** - hamburgery z kotletami i dodatkami  
- **Fries** - frytki w różnych rozmiarach
- **Drink** - napoje zimne i gorące (McCafe)
- **BreakfastItem** - pozycje śniadaniowe (dostępne do 10:30)

**Kluczowe cechy:**
- Hierarchia dziedziczenia z nadpisywaniem
- @classmethod factory methods (`create_big_mac()`)
- @staticmethod utility methods (`calculate_calories()`)
- Enkapsulacja z property getters/setters
- Walidacja czasu dla śniadań

#### Staff System (`staff.py`)
- **Staff** - bazowa klasa pracownika
- **Cashier** - kasjer z numerem kasy
- **KitchenStaff** - personel kuchni ze stanowiskiem
- **ShiftManager** - menedżer zmiany
- **GeneralManager** - menedżer generalny

**Kluczowe cechy:**
- Wielopoziomowe dziedziczenie (GM → ShiftManager → Staff)
- Nadpisywanie atrybutów (`base_salary`, `department`)
- Nadpisywanie metod (`work()`, `get_permissions()`)
- System uprawnień i ról
- Zarządzanie zmianami

#### Customer System (`customer.py`)
- **Customer** - bazowa klasa klienta
- **RegularCustomer** - zwykły klient
- **LoyaltyCustomer** - klient z programem lojalnościowym
- **VIPCustomer** - klient VIP z konciergiem
- **EmployeeCustomer** - pracownik jako klient

**Kluczowe cechy:**
- Program lojalnościowy z poziomami (Bronze/Silver/Gold/Platinum)
- Factory methods dla różnych typów rejestracji
- VIP usługi i priorytety
- Enkapsulacja danych osobowych

#### Order System (`order.py`)
- **Order** - bazowa klasa zamówienia
- **DineInOrder** - zamówienie w restauracji
- **TakeoutOrder** - zamówienie na wynos
- **DriveThruOrder** - zamówienie Drive-Thru
- **DeliveryOrder** - zamówienie z dostawą

**Kluczowe cechy:**
- Factory methods dla różnych scenariuszy
- Walidacja specyficzna dla typu zamówienia
- Śledzenie statusu i czasu przygotowania
- Integracja z systemem płatności

#### Payment System (`payment.py`)
- **Payment** - bazowa klasa płatności
- **CashPayment** - płatność gotówką
- **CardPayment** - płatność kartą
- **MobilePayment** - płatność mobilna (Apple Pay, Google Pay)
- **GiftCardPayment** - płatność kartą podarunkową

**Kluczowe cechy:**
- **POLIMORFIZM** - `process_payment()` różnie implementowane
- Walidacja danych płatności (Luhn algorithm dla kart)
- Factory methods dla różnych scenariuszy
- Obsługa błędów i wyjątków

### ⚙️ Services (`src/services/`)

#### Order Service (`order_service.py`)
Warstwa biznesowa integrująca wszystkie komponenty:

```python
class OrderService:
    def create_order(self, order_type: OrderType, customer_id: str, **kwargs) -> Order:
        # Używa Factory Method dla tworzenia
        order = self._factory_manager.create_order(order_type, customer_id, **kwargs)
        
        # Używa Strategy Pattern dla rabatów
        if self._discount_manager:
            self._apply_discounts_to_order(order, customer_id)
            
        # Używa Observer Pattern dla powiadomień
        if self._order_tracker:
            self._order_tracker.track_order(order.order_id, order_data)
            
        return order
```

### 🏗️ Patterns (`src/patterns/`)

Implementacje wzorców projektowych z pełną dokumentacją i przykładami użycia.

### 🛡️ Utils (`src/utils/`)

#### Validators (`validators.py`)
System walidacji z @staticmethod:

```python
class DataValidator:
    @staticmethod
    def validate_email(email: Any) -> ValidationResult:
        # Walidacja email z regex
        
    @staticmethod  
    def validate_employee_id(employee_id: Any) -> ValidationResult:
        # Format EMP#### (e.g., EMP1001)
        
    @staticmethod
    def validate_order_data(order_data: Dict[str, Any]) -> ValidationResult:
        # Kompleksowa walidacja zamówienia
```

#### Logger (`logger.py`)
System logowania śledzi:
- 🔄 Transfer danych między komponentami
- 📋 Sprawdzenie wymagań OOP
- 🚨 Operacje biznesowe
- ⚠️ Błędy i wyjątki

## 🧪 Testy

### Uruchomienie testów

```bash
# Szybki test (podstawowa funkcjonalność)
python run_tests.py --quick

# Pełny test (wszystkie komponenty)
python run_tests.py --full

# Test scenariuszy biznesowych
python run_tests.py --demo
```

### Pokrycie testów

- ✅ **OOP Requirements** - wszystkie 11 wymagań
- ✅ **Design Patterns** - Strategy, Observer, Factory Method
- ✅ **Model Components** - Menu, Staff, Customer, Order, Payment
- ✅ **Service Layer** - OrderService integration
- ✅ **Integration** - component cooperation
- ✅ **Business Logic** - McDonald's specific logic
- ✅ **Error Handling** - exceptions and validation
- ✅ **Data Validation** - input validation
- ✅ **Performance** - basic performance checks
- ✅ **Complete Demo** - end-to-end functionality

### Przykładowe wyniki testów

```
🧪 McDONALD'S SYSTEM TEST RUNNER
============================================================

🧪 TESTING: OOP REQUIREMENTS
============================================================
✅ Classes and Objects
✅ Inheritance  
✅ Attribute Overriding
✅ Method Overriding
✅ @classmethod
✅ @staticmethod
✅ Multiple Constructors
✅ Encapsulation
✅ Polymorphism
✅ super() usage
✅ Custom Exceptions
✅ OOP Requirements: 11/11 tests passed

📊 TEST SUMMARY
============================================================
✅ Tests passed: 85/85 (100.0%)
⏱️  Execution time: 2.34 seconds
📋 Requirements tested: 11
🏗️  Patterns tested: 3
🔧 Components tested: 8

🎉 ALL TESTS PASSED!
✅ System is fully functional
✅ All OOP requirements satisfied
✅ All design patterns working
✅ Complete integration achieved
```

## 🏪 Scenariusze biznesowe

Sistem zawiera 10 realistycznych scenariuszy operacji McDonald's:

### 🌅 Scenariusz 1: Poranny ruch
- Otwarcie restauracji o 6:00
- Zatrudnienie i rozpoczęcie zmian personelu
- Pierwsi klienci i zamówienia śniadaniowe
- Setup wszystkich systemów

### 👨‍👩‍👧‍👦 Scenariusz 2: Rodzinny obiad  
- Rodziny z dziećmi
- Happy Meals i zabawki
- Specjalne zamówienia urodzinowe
- Obsługa większych grup

### 🚗 Scenariusz 3: Szczyt Drive-Thru
- Godziny szczytu 13:00-14:00
- 10 pojazdów w kolejce
- Różne metody płatności
- Optymalizacja czasu obsługi

### 🚚 Scenariusz 4: Zamówienia z dostawą
- Aplikacja mobilna
- Kierowcy i routing
- VIP dostawy ekspresowe
- Śledzenie w czasie rzeczywistym

### 🕒 Scenariusz 5: Happy Hour (16:00-18:00)
- Promocje czasowe (Strategy Pattern)
- Rabaty studenckie
- BOGO oferty
- Lojalnościowe punkty

### 👑 Scenariusz 6: Obsługa VIP
- Klienci Celebrity
- Prywatne stoły
- Usługi concierge
- Priorytetowe przetwarzanie

### 👥 Scenariusz 7: Zarządzanie personelem
- Promocje pracowników
- Zmiana wieczorna
- Autoryzacja menedżerska
- Uprawnienia i role

### 💳 Scenariusz 8: Przetwarzanie płatności
- **Demonstracja polimorfizmu**
- Gotówka, karty, Apple Pay, karty podarunkowe
- Jeden interfejs, różne implementacje
- Obsługa błędów płatności

### 📱 Scenariusz 9: Śledzenie zamówień
- **Observer Pattern w działaniu**
- Powiadomienia push
- Aktualizacje statusu w czasie rzeczywistym
- Integracja z aplikacją mobilną

### 🌙 Scenariusz 10: Koniec dnia
- Finalizacja zamówień
- Generowanie raportów
- Zamykanie kas
- Statystyki sprzedaży

## 🔍 Sprawdzenie wymagań

Szczegółowa lista kontrolna znajduje się w [`docs/REQUIREMENTS_CHECK.md`](docs/REQUIREMENTS_CHECK.md).

### Podsumowanie sprawdzenia

| Kategoria | Wymagane | Zrealizowane | Status |
|-----------|----------|--------------|--------|
| **OOP podstawowe** | 11 | 11 | ✅ 100% |
| **Wzorce projektowe** | 3 | 3 | ✅ 100% |
| **Integracja** | - | Pełna | ✅ 100% |
| **Demonstracja** | - | Kompletna | ✅ 100% |
| **Testy** | - | Passing | ✅ 100% |
| **Dokumentacja** | - | Kompletna | ✅ 100% |

## 🤝 Wkład i rozwój

### Architektura systemu

System został zaprojektowany z myślą o:
- **Modularności** - każdy komponent ma swoją odpowiedzialność
- **Rozszerzalności** - łatwe dodawanie nowych funkcji
- **Testowalności** - pełne pokrycie testami
- **Dokumentacji** - jasne API i przykłady użycia

### Wzorce użyte

1. **MVC Architecture** - separacja logiki biznesowej
2. **Dependency Injection** - luźne powiązania
3. **Factory Method** - tworzenie obiektów
4. **Strategy Pattern** - algorytmy rabatowe
5. **Observer Pattern** - system powiadomień
6. **Singleton** - logger i konfiguracja

### Możliwości rozwoju

- 🔮 **GUI Interface** - graficzny interfejs użytkownika
- 🌐 **Web API** - REST API dla aplikacji mobilnych
- 🗄️ **Database Integration** - PostgreSQL/MongoDB
- 📊 **Advanced Analytics** - ML dla predykcji sprzedaży
- 🔐 **Authentication** - system logowania i autoryzacji
- 🌍 **Multi-restaurant** - sieć restauracji
- 📱 **Mobile App** - dedykowana aplikacja mobilna


---

## 🎉 Podsumowanie

**McDonald's Management System** to kompletna implementacja wszystkich wymaganych wzorców OOP i wzorców projektowych w kontekście realistycznego systemu biznesowego. System demonstruje:

- ✅ **Wszystkie 11 wymagań OOP** - w pełni zaimplementowane i przetestowane
- ✅ **3 wzorce projektowe** - Strategy, Observer, Factory Method
- ✅ **Integrację komponentów** - wszystkie części współpracują
- ✅ **Scenariusze biznesowe** - 10 realistycznych przypadków użycia McDonald's
- ✅ **System testów** - pełna weryfikacja funkcjonalności
- ✅ **Dokumentację** - szczegółowe opisy i przykłady
