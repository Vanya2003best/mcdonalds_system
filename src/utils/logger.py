"""
McDonald's Management System - Logging Utility
Централизованная система логирования для отслеживания передачи данных
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional


class McDonaldsLogger:
    """
    Централизованный логгер для McDonald's системы
    🚨 LOG: Все операции системы логируются через этот класс
    """

    _instance: Optional['McDonaldsLogger'] = None
    _initialized = False

    def __new__(cls):
        """Singleton pattern для логгера"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.setup_logger()
            McDonaldsLogger._initialized = True

    def setup_logger(self):
        """Настройка логгера"""
        # Создание директории для логов
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)

        # Настройка форматирования
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(module)s | %(message)s'
        )

        # Настройка файлового логгера
        file_handler = logging.FileHandler(
            f"{log_dir}/mcdonalds_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler.setFormatter(formatter)

        # Настройка консольного логгера
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Создание главного логгера
        self.logger = logging.getLogger('McDonald')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def log_transfer(self, from_module: str, to_module: str, data_type: str, details: str = ""):
        """
        🔄 TRANSFER: Логирование передачи данных между модулями
        """
        message = f"TRANSFER: {from_module} → {to_module} | {data_type}"
        if details:
            message += f" | {details}"
        self.logger.info(message)

    def log_requirement_check(self, requirement: str, status: str, location: str):
        """
        📋 CHECK: Логирование проверки выманий OOP
        """
        self.logger.info(f"REQUIREMENT CHECK: {requirement} | {status} | {location}")

    def log_operation(self, operation: str, details: Dict[str, Any] = None):
        """
        🚨 LOG: Логирование операций системы
        """
        message = f"OPERATION: {operation}"
        if details:
            details_str = " | ".join([f"{k}={v}" for k, v in details.items()])
            message += f" | {details_str}"
        self.logger.info(message)

    def log_error(self, error: str, exception: Exception = None):
        """Логирование ошибок"""
        message = f"ERROR: {error}"
        if exception:
            message += f" | Exception: {str(exception)}"
        self.logger.error(message)

    def log_business_rule(self, rule: str, result: str):
        """Логирование бизнес-правил McDonald's"""
        self.logger.info(f"BUSINESS RULE: {rule} | Result: {result}")


# Глобальный экземпляр логгера
mcdonalds_logger = McDonaldsLogger()


# Удобные функции для использования в других модулях
def log_transfer(from_module: str, to_module: str, data_type: str, details: str = ""):
    """🔄 TRANSFER: Логирование передачи данных"""
    mcdonalds_logger.log_transfer(from_module, to_module, data_type, details)


def log_requirement_check(requirement: str, status: str, location: str):
    """📋 CHECK: Логирование проверки требований"""
    mcdonalds_logger.log_requirement_check(requirement, status, location)


def log_operation(operation: str, details: Dict[str, Any] = None):
    """🚨 LOG: Логирование операций"""
    mcdonalds_logger.log_operation(operation, details)


def log_error(error: str, exception: Exception = None):
    """Логирование ошибок"""
    mcdonalds_logger.log_error(error, exception)


def log_business_rule(rule: str, result: str):
    """Логирование бизнес-правил"""
    mcdonalds_logger.log_business_rule(rule, result)


if __name__ == "__main__":
    # Тест логгера
    log_operation("Logger Test", {"module": "logger.py", "status": "OK"})
    log_transfer("logger.py", "test_module", "test_data", "Testing transfer logging")
    log_requirement_check("Logging System", "IMPLEMENTED", "utils/logger.py")