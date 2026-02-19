import re
from ..base_processor import FastenerProcessor


class NutProcessor(FastenerProcessor):
    """Процессор для гаек"""
    
    def can_process(self, text):
        return bool(re.search(r'гайк', text, re.IGNORECASE))
    
    def process(self, text):
        text = self.remove_del_prefix(text)
        # TODO: Добавить паттерны для гаек
        return text