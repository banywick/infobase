# from .base_processor import FastenerProcessor
from .processors import *


class TransformationString:
    """Основной класс для обработки строк с крепежами"""
    
    def __init__(self):
        # Регистрируем все процессоры в порядке приоритета
        self.processors = [
            ScrewBoltProcessor(),
            RivetProcessor(),
            PinProcessor(),
            KeyProcessor(),
            CotterPinProcessor(),
            StudProcessor(),
            RingProcessor(),
            WasherProcessor(),
            NutProcessor(),
            DefaultProcessor()  # Всегда последний
        ]
    
    def process(self, input_text):
        """
        Обрабатывает входную строку, выбирая подходящий процессор
        
        Args:
            input_text (str): Входная строка для обработки
            
        Returns:
            str: Обработанная строка
        """
        if not input_text or not isinstance(input_text, str):
            return input_text
        
        # Ищем первый подходящий процессор
        for processor in self.processors:
            if processor.can_process(input_text):
                return processor.process(input_text)
        
        # Если ничего не подошло (хотя DefaultProcessor должен подойти всегда)
        return input_text.strip()
    
    # Для обратной совместимости
    @staticmethod
    def screw(input_text):
        ts = TransformationString()
        return ts.process(input_text)