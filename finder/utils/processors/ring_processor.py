import re
from ..base_processor import FastenerProcessor


class RingProcessor(FastenerProcessor):
    """Процессор для колец"""
    
    def can_process(self, text):
        return bool(re.search(r'кольц', text, re.IGNORECASE))
    
    def process(self, text):
        text = self.remove_del_prefix(text)
        # TODO: Добавить паттерны для колец
        return text