"""
McDonald's Management System - Logger Module
✅ WYMAGANIE: Система логирования для отслеживания операций

Windows-совместимая система логирования
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional
import sys

# Настройка кодировки для Windows
if sys.platform.startswith('win'):
    import locale
    locale.setlocale(locale.LC_ALL, 'C')

class McDonaldsLogger:
    """
    📋 CHECK: Система логирования McDonald's
    Windows-совместимая система логирования без Unicode символов
    """

    def __init__(self, name: str = "mcdonalds_system"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Очищаем существующие handlers
        self.logger.handlers.clear()

        # Создаем папку для логов
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Файл лога с датой
        log_filename = f"{log_dir}/mcdonalds_{datetime.now().strftime('%Y%m%d')}.log"

        # Форматтер без Unicode символов (используем ASCII)
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # File handler с UTF-8 кодировкой
        try:
            file_handler = logging.FileHandler(log_filename, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not create file handler: {e}")

        # Console handler с безопасной кодировкой
        try:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)

            # Специальный форматтер для консоли (без проблемных символов)
            console_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | %(message)s',
                datefmt='%H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)

            # Устанавливаем безопасную кодировку для Windows
            if hasattr(console_handler.stream, 'reconfigure'):
                console_handler.stream.reconfigure(encoding='utf-8', errors='replace')

            self.logger.addHandler(console_handler)
        except Exception as e:
            print(f"Warning: Could not create console handler: {e}")

    def log_operation(self, operation: str, details: Dict[str, Any] = None):
        """Логирует операцию системы"""
        details_str = ""
        if details:
            details_parts = []
            for key, value in details.items():
                details_parts.append(f"{key}={value}")
            details_str = " | " + " | ".join(details_parts)

        message = f"OPERATION: {operation}{details_str}"
        self.logger.info(message)

    def log_business_rule(self, rule_name: str, description: str):
        """Логирует выполнение бизнес-правила"""
        message = f"BUSINESS RULE: {rule_name} | {description}"
        self.logger.info(message)

    def log_requirement_check(self, requirement: str, status: str, details: str = ""):
        """Логирует проверку требований"""
        details_str = f" | {details}" if details else ""
        message = f"REQUIREMENT CHECK: {requirement} | {status}{details_str}"
        self.logger.info(message)

    def log_transfer(self, from_module: str, to_module: str, data_type: str, details: str = ""):
        """Логирует передачу данных между модулями (без Unicode символов)"""
        details_str = f" | {details}" if details else ""
        # Заменяем Unicode стрелку на ASCII
        message = f"TRANSFER: {from_module} -> {to_module} | {data_type}{details_str}"
        self.logger.info(message)

    def log_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """Логирует ошибки"""
        context_str = ""
        if context:
            context_parts = []
            for key, value in context.items():
                context_parts.append(f"{key}={value}")
            context_str = " | Context: " + ", ".join(context_parts)

        message = f"ERROR: {error_type} | {error_message}{context_str}"
        self.logger.error(message)

    def log_performance(self, operation: str, duration_ms: float, additional_data: Dict[str, Any] = None):
        """Логирует показатели производительности"""
        additional_str = ""
        if additional_data:
            additional_parts = []
            for key, value in additional_data.items():
                additional_parts.append(f"{key}={value}")
            additional_str = " | " + " | ".join(additional_parts)

        message = f"PERFORMANCE: {operation} | {duration_ms:.2f}ms{additional_str}"
        self.logger.info(message)


# Глобальный экземпляр логгера
mcdonalds_logger = McDonaldsLogger()

# Удобные функции для использования
def log_operation(operation: str, details: Dict[str, Any] = None):
    """Удобная функция для логирования операций"""
    mcdonalds_logger.log_operation(operation, details)

def log_business_rule(rule_name: str, description: str):
    """Удобная функция для логирования бизнес-правил"""
    mcdonalds_logger.log_business_rule(rule_name, description)

def log_requirement_check(requirement: str, status: str, details: str = ""):
    """Удобная функция для проверки требований"""
    mcdonalds_logger.log_requirement_check(requirement, status, details)

def log_transfer(from_module: str, to_module: str, data_type: str, details: str = ""):
    """Удобная функция для логирования передач данных"""
    mcdonalds_logger.log_transfer(from_module, to_module, data_type, details)

def log_error(error_type: str, error_message: str, context: Dict[str, Any] = None):
    """Удобная функция для логирования ошибок"""
    mcdonalds_logger.log_error(error_type, error_message, context)

def log_performance(operation: str, duration_ms: float, additional_data: Dict[str, Any] = None):
    """Удобная функция для логирования производительности"""
    mcdonalds_logger.log_performance(operation, duration_ms, additional_data)


# Демонстрация системы логирования
def demo_logging_system():
    """Демонстрация всех возможностей системы логирования"""
    print("📋 McDONALD'S LOGGING SYSTEM DEMO")
    print("=" * 50)

    # Тестируем все типы логов
    log_operation("System Startup", {"version": "1.0", "environment": "demo"})
    log_business_rule("Order Validation", "Order must contain at least one item")
    log_requirement_check("OOP Requirements", "SUCCESS", "All 11 requirements implemented")
    log_transfer("OrderService", "PaymentProcessor", "payment data", "transaction_id=TXN123")
    log_error("ValidationError", "Invalid customer ID format", {"customer_id": "INVALID", "expected_format": "CUST######"})
    log_performance("Order Processing", 150.75, {"orders_count": 5, "avg_time_per_order": 30.15})

    print("\n✅ All logging functions tested successfully!")
    print("📁 Check the 'logs' folder for log files")


if __name__ == "__main__":
    demo_logging_system()