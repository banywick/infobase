import re
from ..base_processor import FastenerProcessor


class WasherProcessor(FastenerProcessor):
    """Процессор для шайб"""
    
    def can_process(self, text):
        return bool(re.search(r'шайб', text, re.IGNORECASE))
    
    def process(self, text):
        # Удаляем префиксы DEL_ или del_
        text = self.remove_del_prefix(text)
        
        # ==============================================
        # ЛОГИКА ДЛЯ ШАЙБ
        # ==============================================
        
        fastener_type = "шайба"
        
        # Проверяем на специальные типы
        is_reduced = bool(re.search(r'уменьш', text, re.IGNORECASE))
        is_reinforced = bool(re.search(r'усиленн', text, re.IGNORECASE))
        
        if is_reduced:
            fastener_type = "шайба уменьш"
        elif is_reinforced:
            fastener_type = "шайба усиленная"
        
        # 1. DIN форматы с размером после DIN и запятой в конце
        # "Шайба усиленная 2,7, DIN 9021 A4" -> "шайба *2,7* 9021"
        pattern_din_comma_end = r'(\d+(?:[.,]\d+)?)[,]\s+(?:DIN|din)[\s\-]*(\d+)'
        match = re.search(pattern_din_comma_end, text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace('.', ',')
            standard = match.group(2)
            if re.search(r'[.,]', diameter):
                return f"{fastener_type} *{diameter}* {standard}"
            else:
                return f"{fastener_type} *{diameter} {standard}"
        
        # 2. DIN форматы с размером после DIN
        # "Шайба 2,2 DIN 433 A2" -> "шайба *2,2* 433"
        pattern_din_size_first = r'(\d+(?:[.,]\d+)?)\s+(?:DIN|din)[\s\-]*(\d+)'
        match = re.search(pattern_din_size_first, text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace('.', ',')
            standard = match.group(2)
            if re.search(r'[.,]', diameter):
                return f"{fastener_type} *{diameter}* {standard}"
            else:
                return f"{fastener_type} *{diameter} {standard}"
        
        # 3. DIN форматы с B префиксом: "Шайба B2 A4 DIN 127" -> "шайба *2 127"
        pattern_din_b_prefix = r'[BВ](\d+)\s+[A-Z0-9]+\s+(?:DIN|din)[\s\-]*(\d+)'
        match = re.search(pattern_din_b_prefix, text, re.IGNORECASE)
        if match:
            diameter = match.group(1)
            standard = match.group(2)
            return f"{fastener_type} *{diameter} {standard}"
        
        # 4. DIN форматы с М префиксом: "Шайба М 2,5 DIN 127 оц." -> "шайба *2,5* 127"
        pattern_din_m_prefix = r'[МM]\s*(\d+(?:[.,]\d+)?)\s+(?:DIN|din)[\s\-]*(\d+)'
        match = re.search(pattern_din_m_prefix, text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace('.', ',')
            standard = match.group(2)
            if re.search(r'[.,]', diameter):
                return f"{fastener_type} *{diameter}* {standard}"
            else:
                return f"{fastener_type} *{diameter} {standard}"
        
        # 5. DIN форматы с A префиксом: "Шайба A2,2 A4 140HV DIN 125" -> "шайба *2,2* 125"
        pattern_din_a_prefix = r'[AА](\d+(?:[.,]\d+)?)\s+[A-Z0-9]+\s+(?:DIN|din)[\s\-]*(\d+)'
        match = re.search(pattern_din_a_prefix, text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace('.', ',')
            standard = match.group(2)
            if re.search(r'[.,]', diameter):
                return f"{fastener_type} *{diameter}* {standard}"
            else:
                return f"{fastener_type} *{diameter} {standard}"
        
        # 6. DIN форматы с размером в конце: "Шайба м2.2 DIN 433 А2" -> "шайба *2.2* 433"
        pattern_din_size_any = r'[МM]?(\d+(?:[.,]\d+)?)\s+(?:DIN|din)[\s\-]*(\d+)'
        match = re.search(pattern_din_size_any, text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace('.', ',')
            standard = match.group(2)
            if re.search(r'[.,]', diameter):
                return f"{fastener_type} *{diameter}* {standard}"
            else:
                return f"{fastener_type} *{diameter} {standard}"
        
        # 7. Простые DIN форматы: "Шайба DIN 125 А2 2,2"
        pattern_din_reverse = r'(?:DIN|din)[\s\-]*(\d+).*?(\d+(?:[.,]\d+)?)'
        match = re.search(pattern_din_reverse, text, re.IGNORECASE)
        if match:
            standard = match.group(1)
            diameter = match.group(2).replace('.', ',')
            if re.search(r'[.,]', diameter):
                return f"{fastener_type} *{diameter}* {standard}"
            else:
                return f"{fastener_type} *{diameter} {standard}"
        
        # 8. Универсальный паттерн для DIN
        pattern_din_universal = r'(?:DIN|din)[\s\-]*(\d+).*?(\d+(?:[.,]\d+)?)'
        match = re.search(pattern_din_universal, text, re.IGNORECASE)
        if match:
            standard = match.group(1)
            diameter = match.group(2).replace('.', ',')
            if re.search(r'[.,]', diameter):
                return f"{fastener_type} *{diameter}* {standard}"
            else:
                return f"{fastener_type} *{diameter} {standard}"
        
        # 9. ГОСТ форматы для шайб (если появятся)
        pattern_gost = r'(\d+(?:[.,]\d+)?)\s*(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost, text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace('.', ',')
            standard = match.group(2)
            if re.search(r'[.,]', diameter):
                return f"{fastener_type} {diameter} {standard}"
            else:
                return f"{fastener_type} {diameter} {standard}"
        
        # Если ничего не найдено, возвращаем исходный текст
        return text


# Примеры для тестирования
if __name__ == "__main__":
    processor = WasherProcessor()
    
    test_cases = [
        "Шайба усиленная 2,7, DIN 9021 A4",
        "Шайба 2,2 DIN 433 A2",
        "Шайба B2 A4 DIN 127",
        "Шайба М 2,5 DIN 127 оц.",
        "Шайба уменьш нерж 1,5 DIN 433 A2",
        "Шайба A2,2 A4 140HV DIN 125",
        "Шайба м2.2 DIN 433 А2",
        "Шайба DIN 125 А2 2,2",
    ]
    
    for test in test_cases:
        result = processor.process(test)
        print(f"Вход: {test}")
        print(f"Выход: {result}")
        print("-" * 50)