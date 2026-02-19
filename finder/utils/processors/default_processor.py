import re
from ..base_processor import FastenerProcessor


class DefaultProcessor(FastenerProcessor):
    """Процессор по умолчанию для строк без ключевых слов"""
    
    def can_process(self, text):
        # Проверяем, есть ли вообще ключевые слова крепежей
        fastener_keywords = [
            r'болт', r'гайк', r'шайб', r'кольц', r'винт',
            r'шпильк', r'шплинт', r'штифт', r'шпонк', r'заклепк'
        ]
        for keyword in fastener_keywords:
            if re.search(keyword, text, re.IGNORECASE):
                return False
        return True
    
    def process(self, text):
        # Возвращаем исходную строку без изменений
        return text.strip()