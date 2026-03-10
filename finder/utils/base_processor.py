# base_processor.py
import re
from abc import ABC, abstractmethod


class FastenerProcessor(ABC):
    """Абстрактный базовый класс для всех процессоров крепежей"""
    
    @abstractmethod
    def can_process(self, text):
        """Проверяет, может ли процессор обработать данный текст"""
        pass
    
    @abstractmethod
    def process(self, text):
        """Обрабатывает текст и возвращает результат"""
        pass
    
    @staticmethod
    def remove_del_prefix(text):
        """Удаляет префиксы DEL_ или del_"""
        return re.sub(r'^DEL_|^del_', '', text.strip())