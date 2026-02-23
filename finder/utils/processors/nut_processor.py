import re
from ..base_processor import FastenerProcessor


class NutProcessor(FastenerProcessor):
    """Процессор для гаек"""
    
    def can_process(self, text):
        return bool(re.search(r'гайк|контргайк|рым-гайк', text, re.IGNORECASE))
    
    def process(self, text):
        # Удаляем префиксы DEL_ или del_
        text = self.remove_del_prefix(text)
        
        # ==============================================
        # ЛОГИКА ДЛЯ ГАЕК
        # ==============================================
        
        # Определяем тип гайки
        if re.search(r'контргайк', text, re.IGNORECASE):
            fastener_type = "контргайка"
        elif re.search(r'рым-гайк', text, re.IGNORECASE):
            fastener_type = "рым-гайка"
        elif re.search(r'гайка-заклепк', text, re.IGNORECASE):
            fastener_type = "гайка-заклепка"
        elif re.search(r'накидн', text, re.IGNORECASE):
            fastener_type = "гайка накидная"
        elif re.search(r'клепальн', text, re.IGNORECASE):
            fastener_type = "гайка клепальная"
        elif re.search(r'фланцев', text, re.IGNORECASE):
            fastener_type = "гайка фланцевая"
        elif re.search(r'шестигранн', text, re.IGNORECASE):
            fastener_type = "гайка шестигранная"
        elif re.search(r'барашков', text, re.IGNORECASE):
            fastener_type = "гайка барашковая"
        elif re.search(r'приварн', text, re.IGNORECASE):
            fastener_type = "гайка приварная"
        elif re.search(r'врезн', text, re.IGNORECASE):
            fastener_type = "гайка врезная"
        elif re.search(r'квадратн', text, re.IGNORECASE):
            fastener_type = "гайка квадратная"
        elif re.search(r'корончат', text, re.IGNORECASE):
            fastener_type = "гайка корончатая"
        elif re.search(r'запрессовочн', text, re.IGNORECASE):
            fastener_type = "гайка запрессовочная"
        else:
            fastener_type = "гайка"
        
        # 1. Специальный случай: Гайка 7003-0301 ГОСТ 8918-69 -> "гайка 7003 0301 8918"
        pattern_gost_with_hyphen = r'(\d+)[\-](\d+)(?:\s+ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_with_hyphen, text, re.IGNORECASE)
        if match:
            part1 = match.group(1)
            part2 = match.group(2)
            standard = match.group(3)
            return f"{fastener_type} {part1} {part2} {standard}"
        
        # 2. Форматы с дробными размерами: "Гайка 3/8\"" -> "гайка *3/8*"
        pattern_fraction = r'(\d+)/(\d+)"'
        match = re.search(pattern_fraction, text, re.IGNORECASE)
        if match:
            numerator = match.group(1)
            denominator = match.group(2)
            return f"{fastener_type} *{numerator}/{denominator}*"
        
        # 3. DIN форматы с размером через точку: "Гайка M2.5 DIN 934 А4" -> "гайка *2.5* 934"
        pattern_din_with_dot = r'[МM](\d+\.\d+)\s+(?:DIN|din)[\s\-]*(\d+)'
        match = re.search(pattern_din_with_dot, text, re.IGNORECASE)
        if match:
            diameter = match.group(1)  # Сохраняем точку
            standard = match.group(2)
            return f"{fastener_type} *{diameter}* {standard}"
        
        # 4. DIN форматы с одинарным размером через запятую: "Гайка DIN 1624 M4-A2" -> "гайка *4 1624"
        pattern_din_single_comma = r'(?:DIN|din)[\s\-]*(\d+).*?[МM](\d+,\d+)'
        match = re.search(pattern_din_single_comma, text, re.IGNORECASE)
        if match:
            standard = match.group(1)
            diameter = match.group(2)  # Сохраняем запятую
            return f"{fastener_type} *{diameter}* {standard}"
        
        # 5. DIN форматы с одинарным размером: "Гайка DIN 1624 M4-A2" -> "гайка *4 1624"
        pattern_din_single = r'(?:DIN|din)[\s\-]*(\d+).*?[МM](\d+)'
        match = re.search(pattern_din_single, text, re.IGNORECASE)
        if match:
            standard = match.group(1)
            diameter = match.group(2)
            return f"{fastener_type} *{diameter} {standard}"
        
        # 6. DIN форматы с двойным размером: "Гайка DIN 934 M20x1,5-8" -> "гайка *20*1,5* 934"
        pattern_din_double = r'(?:DIN|din)[\s\-]*(\d+).*?[МM](\d+)[xхX](\d+(?:[.,]\d+)?)'
        match = re.search(pattern_din_double, text, re.IGNORECASE)
        if match:
            standard = match.group(1)
            main_size = match.group(2)
            thread = match.group(3).replace('.', ',')
            return f"{fastener_type} *{main_size}*{thread}* {standard}"
        
        # 7. EN форматы: "Гайка EN 1661-M12-10-A3L" -> "гайка *12 1661"
        pattern_en = r'(?:EN|en)[\s\-]*(\d+)[\-][МM](\d+)'
        match = re.search(pattern_en, text, re.IGNORECASE)
        if match:
            standard = match.group(1)
            diameter = match.group(2)
            return f"{fastener_type} *{diameter} {standard}"
        
        # 8. ГОСТ форматы с двойным размером: "Гайка 2 М22х1,5-6H.05.019 ГОСТ 11871-88" -> "гайка *22*1,5* 11871"
        pattern_gost_double = r'(?:\d+\s+)?[МM](\d+)[xхX](\d+(?:[.,]\d+)?).*?(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_double, text, re.IGNORECASE)
        if match:
            main_size = match.group(1)
            thread = match.group(2).replace('.', ',')
            standard = match.group(3)
            return f"{fastener_type} *{main_size}*{thread}* {standard}"
        
        # 9. ГОСТ форматы с одинарным размером: "Гайка М10-6H.5.019 ГОСТ 5915-70" -> "гайка *10 5915"
        pattern_gost_single = r'[МM](\d+)(?:[xхX][\d,]+)?[\-\s\w\.]*?(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_single, text, re.IGNORECASE)
        if match:
            diameter = match.group(1)
            standard = match.group(2)
            return f"{fastener_type} *{diameter} {standard}"
        
        # 10. ОСТ форматы: "Гайка 8-Ц ОСТ1 33059-80" -> "гайка 8 33059"
        pattern_ost = r'(\d+)[\-][^\s]+\s+(?:ОСТ|ост)\d*[\s\-]*(\d+)'
        match = re.search(pattern_ost, text, re.IGNORECASE)
        if match:
            size = match.group(1)
            standard = match.group(2)
            return f"{fastener_type} {size} {standard}"
        
        # 11. Форматы с артикулами: "Гайка 05004110" -> "гайка 05004110"
        pattern_article = r'гайк[аи]?\s+(\d{5,})'
        match = re.search(pattern_article, text, re.IGNORECASE)
        if match and not re.search(r'[МM]', text):
            article = match.group(1)
            return f"{fastener_type} {article}"
        
        # 12. Специальные форматы с артикулами: "Гайка 072-PM"
        pattern_article_with_hyphen = r'гайк[аи]?\s+(\d+[\-][A-Z]+)'
        match = re.search(pattern_article_with_hyphen, text, re.IGNORECASE)
        if match:
            article = match.group(1)
            return f"{fastener_type} {article}"
        
        # 13. Форматы с префиксом 2: "Гайка 2М12-6Н.04.019 ГОСТ 5919-73" -> "гайка *12 5919"
        pattern_with_prefix = r'(?:\d+\s*)?[МM](\d+).*?(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_with_prefix, text, re.IGNORECASE)
        if match:
            diameter = match.group(1)
            standard = match.group(2)
            return f"{fastener_type} *{diameter} {standard}"
        
        # 14. Клепальные гайки: "Гайка клепальная 23M08CO301" -> "гайка клепальная 23M08CO301"
        if fastener_type == "гайка клепальная":
            match = re.search(r'клепальная\s+(\S+)', text, re.IGNORECASE)
            if match:
                code = match.group(1)
                return f"{fastener_type} {code}"
        
        # 15. Накидные гайки: "Гайка накидная M10LCFX" -> "гайка накидная M10LCFX"
        if fastener_type == "гайка накидная":
            match = re.search(r'накидная\s+(\S+)', text, re.IGNORECASE)
            if match:
                code = match.group(1)
                return f"{fastener_type} {code}"
        
        # 16. Гайки-заклепки: "Гайка-заклепка M4 23307040230" -> "гайка-заклепка M4 23307040230"
        if fastener_type == "гайка-заклепка":
            match = re.search(r'гайка-заклепка\s+([МM]\d+(?:\s+\d+)?)', text, re.IGNORECASE)
            if match:
                code = match.group(1)
                return f"{fastener_type} {code}"
        
        # 17. Простые М форматы с точкой: "Гайка M2.5" -> "гайка *2.5*"
        pattern_m_dot = r'[МM](\d+\.\d+)'
        match = re.search(pattern_m_dot, text, re.IGNORECASE)
        if match:
            diameter = match.group(1)
            # Проверяем, есть ли стандарт
            std_match = re.search(r'(?:ГОСТ|гост|DIN|din)[\s\-]*(\d+)', text, re.IGNORECASE)
            if std_match:
                standard = std_match.group(1)
                return f"{fastener_type} *{diameter}* {standard}"
            return f"{fastener_type} *{diameter}*"
        
        # 18. Простые М форматы с запятой: "Гайка M2,5" -> "гайка *2,5*"
        pattern_m_comma = r'[МM](\d+,\d+)'
        match = re.search(pattern_m_comma, text, re.IGNORECASE)
        if match:
            diameter = match.group(1)
            # Проверяем, есть ли стандарт
            std_match = re.search(r'(?:ГОСТ|гост|DIN|din)[\s\-]*(\d+)', text, re.IGNORECASE)
            if std_match:
                standard = std_match.group(1)
                return f"{fastener_type} *{diameter}* {standard}"
            return f"{fastener_type} *{diameter}*"
        
        # 19. Простые М форматы: "Гайка М10" -> "гайка *10"
        pattern_m_simple = r'[МM](\d+)'
        match = re.search(pattern_m_simple, text, re.IGNORECASE)
        if match:
            diameter = match.group(1)
            # Проверяем, есть ли стандарт
            std_match = re.search(r'(?:ГОСТ|гост|DIN|din)[\s\-]*(\d+)', text, re.IGNORECASE)
            if std_match:
                standard = std_match.group(1)
                return f"{fastener_type} *{diameter} {standard}"
            return f"{fastener_type} *{diameter}"
        
        # Если ничего не найдено, возвращаем исходный текст
        return text


# Примеры для тестирования
if __name__ == "__main__":
    processor = NutProcessor()
    
    test_cases = [
        "Гайка M2.5 DIN 934 А4",
        "Гайка M2,5 DIN 934 А4",
        "Гайка DIN 1624 M4-A2",
        "Гайка DIN 934 M20x1,5-8",
        "Гайка 2 М22х1,5-6H.05.019 ГОСТ 11871-88",
        "Гайка М10-6H.5.019 ГОСТ 5915-70",
        "Гайка 7003-0301 ГОСТ 8918-69",
        "Гайка 3/8\"",
    ]
    
    for test in test_cases:
        result = processor.process(test)
        print(f"Вход: {test}")
        print(f"Выход: {result}")
        print("-" * 50)