import re
from ..base_processor import FastenerProcessor


class WasherProcessor(FastenerProcessor):
    """Процессор для шайб"""
    
    def can_process(self, text):
        return bool(re.search(r'шайб', text, re.IGNORECASE))
    
    def process(self, text):
        text = self.remove_del_prefix(text)
        # TODO: Добавить паттерны для шайб
        return text