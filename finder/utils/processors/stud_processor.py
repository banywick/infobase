import re
from ..base_processor import FastenerProcessor


class StudProcessor(FastenerProcessor):
    """Процессор для шпилек"""
    
    def can_process(self, text):
        return bool(re.search(r'шпильк', text, re.IGNORECASE))
    
    def process(self, text):
        # Удаляем префиксы DEL_ или del_
        text = self.remove_del_prefix(text)
        
        # ==============================================
        # ЛОГИКА ДЛЯ ШПИЛЕК
        # ==============================================
        
        fastener_type = "шпилька"
        
        # Проверяем на специальные типы
        is_wooden = bool(re.search(r'деревянная', text, re.IGNORECASE))
        is_press = bool(re.search(r'запрессовочная', text, re.IGNORECASE))
        is_ring = bool(re.search(r'с кольцом', text, re.IGNORECASE))
        
        if is_wooden:
            fastener_type = "шпилька деревянная"
        elif is_press:
            fastener_type = "шпилька запрессовочная"
        elif is_ring:
            fastener_type = "шпилька с кольцом"
        
        # 1. Специальный случай: "Шпилька с кольцом 82-16-200-16"
        if is_ring:
            pattern_ring = r'шпилька\s+с\s+кольцом\s+(\d+)[\-](\d+)[\-](\d+)[\-](\d+)'
            match = re.search(pattern_ring, text, re.IGNORECASE)
            if match:
                return f"{fastener_type} {match.group(1)} {match.group(2)} {match.group(3)} {match.group(4)}"
        
        # 2. Специальный случай: "Шпилька 82-11-180-16"
        pattern_four_numbers = r'шпильк[аи]?\s+(\d+)[\-](\d+)[\-](\d+)[\-](\d+)'
        match = re.search(pattern_four_numbers, text, re.IGNORECASE)
        if match:
            return f"{fastener_type} {match.group(1)} {match.group(2)} {match.group(3)} {match.group(4)}"
        
        # 3. ГОСТ форматы с префиксом "2 М": "Шпилька 2 М12-6gх45.019 ГОСТ 22040-76"
        pattern_gost_with_number = r'(?:\d+\s+)?[МM](\d+)[\-\s\w]*[хxХ](\d+)(?:[\.\d\s]*)(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_with_number, text, re.IGNORECASE)
        if match:
            diameter = match.group(1)
            length = match.group(2)
            standard = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 4. ГОСТ форматы с префиксом В: "Шпилька В.М12-6gх40.58.А.019 ГОСТ 22034-76"
        pattern_gost_with_v = r'В\.?[МM](\d+)[\-\s\w]*[хxХ](\d+)(?:[\.\d\s\w]*)(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_with_v, text, re.IGNORECASE)
        if match:
            diameter = match.group(1)
            length = match.group(2)
            standard = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 5. DIN форматы: "Шпилька DIN 835 M8x30-A2"
        pattern_din = r'(?:DIN|din)[\s\-]*(\d+)[\s\-]*[МM](\d+)[xхX](\d+)'
        match = re.search(pattern_din, text, re.IGNORECASE)
        if match:
            standard = match.group(1)
            diameter = match.group(2)
            length = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 6. DIN форматы без длины: "Шпилька DIN 975 M16"
        pattern_din_no_length = r'(?:DIN|din)[\s\-]*(\d+)[\s\-]*[МM](\d+)'
        match = re.search(pattern_din_no_length, text, re.IGNORECASE)
        if match:
            standard = match.group(1)
            diameter = match.group(2)
            return f"{fastener_type} *{diameter} {standard}"
        
        # 7. ISO форматы: "Шпилька ISO 13918-PT M6x25-4,8-CU"
        pattern_iso = r'(?:ISO)[\s\-]*(\d+)[\-\w]*[МM](\d+)[xхX](\d+)'
        match = re.search(pattern_iso, text, re.IGNORECASE)
        if match:
            standard = match.group(1)
            diameter = match.group(2)
            length = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 8. CHA форматы: "Шпилька CHA-M3-16"
        pattern_cha = r'CHA[\-][МM](\d+)[\-](\d+)'
        match = re.search(pattern_cha, text, re.IGNORECASE)
        if match:
            diameter = match.group(1)
            length = match.group(2)
            return f"{fastener_type} {diameter}*{length}"
        
        # 9. DIN деревянные: "Шпилька деревянная DIN 68150-1-AM-5x20-form A"
        pattern_din_wooden = r'(?:DIN|din)[\s\-]*(\d+)[\-\d\w]*[МM]?(\d+)[xхX](\d+)'
        match = re.search(pattern_din_wooden, text, re.IGNORECASE)
        if match and is_wooden:
            standard = match.group(1)
            diameter = match.group(2)
            length = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 10. Форматы с артикулом: "Шпилька резьбовая M3x12 B04040"
        pattern_with_article = r'[МM](\d+)[xхX](\d+)\s+([A-Z]\d+)'
        match = re.search(pattern_with_article, text, re.IGNORECASE)
        if match:
            diameter = match.group(1)
            length = match.group(2)
            article = match.group(3)
            return f"{fastener_type} {diameter}*{length} {article}"
        
        # 11. Простые М форматы: "Шпилька М3х16"
        pattern_simple_m = r'[МM](\d+)[xхX](\d+)'
        match = re.search(pattern_simple_m, text, re.IGNORECASE)
        if match:
            diameter = match.group(1)
            length = match.group(2)
            # Проверяем, есть ли ГОСТ отдельно
            gost_match = re.search(r'(?:ГОСТ|гост)[\s\-]*(\d+)', text, re.IGNORECASE)
            if gost_match:
                return f"{fastener_type} {diameter}*{length} {gost_match.group(1)}"
            return f"{fastener_type} {diameter}*{length}"
        
        # 12. Специальный случай для запрессовочных: "Шпилька запрессовочная CHC-M5-16"
        if is_press:
            pattern_press = r'CHC[\-][МM](\d+)[\-](\d+)'
            match = re.search(pattern_press, text, re.IGNORECASE)
            if match:
                return f"{fastener_type} {match.group(1)}*{match.group(2)}"
            return text
        
        # Если ничего не найдено, возвращаем исходный текст
        return text


# Примеры для тестирования
if __name__ == "__main__":
    processor = StudProcessor()
    
    test_cases = [
        "Шпилька В.М12-6gх40.58.А.019 ГОСТ 22034-76",
        "Шпилька 2 М12-6gх45.019 ГОСТ 22040-76",
        "Шпилька 82-11-180-16",
        "Шпилька CHA-M3-16",
        "Шпилька DIN 835 M8x30-A2",
        "Шпилька DIN 975 M16",
        "Шпилька ISO 13918-PT M6x25-4,8-CU",
        "Шпилька В.М10-6gх40.58.А.05 ГОСТ 22034-76",
        "Шпилька запрессовочная CHC-M5-16",
        "Шпилька резьбовая M3x12 B04040",
        "Шпилька с кольцом 82-16-200-16",
        "Шпилька деревянная DIN 68150-1-AM-5x20-form A",
    ]
    
    for test in test_cases:
        result = processor.process(test)
        print(f"Вход: {test}")
        print(f"Выход: {result}")
        print("-" * 50)