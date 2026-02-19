import re
from ..base_processor import FastenerProcessor


class RivetProcessor(FastenerProcessor):
    """Процессор для заклепок"""
    
    def can_process(self, text):
        return bool(re.search(r'заклепк|ЗВК', text, re.IGNORECASE))
    
    def process(self, text):
        # Удаляем префиксы DEL_ или del_
        text = self.remove_del_prefix(text)
        
        # ==============================================
        # ЛОГИКА ДЛЯ ЗАКЛЕПОК
        # ==============================================
        
        # Определяем точный тип
        if re.search(r'гайка-заклепка', text, re.IGNORECASE):
            fastener_type = "гайка-заклепка"
        elif re.search(r'заклепка-болт', text, re.IGNORECASE):
            fastener_type = "заклепка-болт"
        else:
            fastener_type = "заклепка"
        
        # 1. Специальный случай: Заклепка-болт с артикулом (возвращаем как есть)
        if fastener_type == "заклепка-болт":
            match = re.search(r'заклепка-болт\s+(\S+)', text, re.IGNORECASE)
            if match:
                return f"{fastener_type} {match.group(1)}"
            return text
        
        # 2. Специальный случай: Гайка-заклепка с размером M и артикулом
        if fastener_type == "гайка-заклепка":
            match = re.search(r'гайка-заклепка\s+[МM](\d+)\s+(\d+)', text, re.IGNORECASE)
            if match:
                diameter = match.group(1)
                article = match.group(2)
                return f"{fastener_type} M{diameter} {article}"
            
            match = re.search(r'гайка-заклепка.*?[МM](\d+)(?:[хxХ](\d+(?:[.,]\d+)?))?', text, re.IGNORECASE)
            if match:
                diameter = match.group(1)
                length = match.group(2) if match.group(2) else ""
                if length:
                    return f"{fastener_type} {diameter}*{length}"
                return f"{fastener_type} {diameter}"
            return text
        
        # 3. DIN EN ISO со слепой заклепкой (с сохранением запятой)
        pattern_din_iso_blind = r'(?:DIN\s*EN\s*ISO|DIN\s*ISO)[\s\-]*(\d+)[\s\-]*(\d+(?:[.,]\d+)?)[xхX](\d+)'
        match = re.search(pattern_din_iso_blind, text, re.IGNORECASE)
        if match and re.search(r'слепая', text, re.IGNORECASE):
            standard = match.group(1)
            diameter = match.group(2)  # НЕ заменяем запятую на точку
            length = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 4. ОСТ форматы: "Заклепка 5-20-Ан.Окс. ОСТ 1 34087-80"
        pattern_ost = r'(\d+)[\-\s]+(\d+)[\-\s]+[А-Яа-я\.]+[\s]*(?:ОСТ|ост)[\s\d\-]*(\d+)'
        match = re.search(pattern_ost, text, re.IGNORECASE)
        if match:
            diameter = match.group(1)
            length = match.group(2)
            standard = match.group(3)
            return f"{fastener_type} {diameter}-{length} {standard}"
        
        # 5. DIN форматы со слепой заклепкой с буквенным префиксом
        pattern_din_with_prefix = r'(?:DIN|din)[\s\-]*(\d+)[\s\-]*[A-Za-z]*(\d+)[хxХ](\d+)'
        match = re.search(pattern_din_with_prefix, text, re.IGNORECASE)
        if match:
            standard = match.group(1)
            diameter = match.group(2)
            length = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 6. DIN форматы с М размером
        pattern_din_m = r'(?:DIN|din)[\s\-]*(\d+)[\s\-]*[МM](\d+)'
        match = re.search(pattern_din_m, text, re.IGNORECASE)
        if match:
            standard = match.group(1)
            diameter = match.group(2)
            return f"{fastener_type} {diameter} {standard}"
        
        # 7. ГОСТ Р ИСО со слепой заклепкой (с сохранением запятой)
        pattern_gost_iso_blind = r'(?:ГОСТ\s*Р\s*ИСО|ГОСТ\s*ISO)[\s\-]*(\d+)[\-\d\s]*(\d+(?:[.,]\d+)?)[хxХ](\d+)'
        match = re.search(pattern_gost_iso_blind, text, re.IGNORECASE)
        if match and re.search(r'слепая', text, re.IGNORECASE):
            standard = match.group(1)
            diameter = match.group(2)  # НЕ заменяем запятую на точку
            length = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 8. ГОСТ форматы с точкой и запятой (СОХРАНЯЕМ запятую)
        pattern_gost_dot = r'(\d+(?:[.,]\d+)?)[хxХ](\d+)[\.\d]*(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_dot, text, re.IGNORECASE)
        if match:
            diameter = match.group(1)  # СОХРАНЯЕМ запятую как есть
            length = match.group(2)
            standard = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 9. ГОСТ форматы без точки
        pattern_gost_simple = r'(\d+(?:[.,]\d+)?)[хxХ](\d+)[\s]*(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_simple, text, re.IGNORECASE)
        if match:
            diameter = match.group(1)  # СОХРАНЯЕМ запятую
            length = match.group(2)
            standard = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 10. DIN форматы (с сохранением запятой)
        pattern_din = r'(?:DIN|din)[\s\-]*(\d+)[\s\-]*(\d+(?:[.,]\d+)?)[xхX](\d+)'
        match = re.search(pattern_din, text, re.IGNORECASE)
        if match:
            standard = match.group(1)
            diameter = match.group(2)  # СОХРАНЯЕМ запятую
            length = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 11. СТБ форматы (с сохранением запятой)
        pattern_stb = r'(?:ЗВК|СТБ)[\-\s]*(\d+(?:[.,]\d+)?)[xхX](\d+)[\s]*(?:СТБ)[\s\-]*(\d+)'
        match = re.search(pattern_stb, text, re.IGNORECASE)
        if match:
            diameter = match.group(1)  # СОХРАНЯЕМ запятую
            length = match.group(2)
            standard = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 12. Форматы с артикулом после размера
        pattern_size_with_article = r'(\d+(?:[.,]\d+)?)[хxХ](\d+)[\s]+(\d{5,})'
        match = re.search(pattern_size_with_article, text, re.IGNORECASE)
        if match:
            diameter = match.group(1)  # СОХРАНЯЕМ запятую
            length = match.group(2)
            article = match.group(3)
            return f"{fastener_type} {diameter}*{length} {article}"
        
        # 13. Простые форматы с размером (с сохранением запятой)
        pattern_simple = r'(\d+(?:[.,]\d+)?)[хxХ](\d+)(?:[.,]\d+)?'
        match = re.search(pattern_simple, text, re.IGNORECASE)
        if match:
            diameter = match.group(1)  # СОХРАНЯЕМ запятую
            length = match.group(2)
            gost_match = re.search(r'(?:ГОСТ|гост)[\s\-]*(\d+)', text, re.IGNORECASE)
            if gost_match:
                return f"{fastener_type} {diameter}*{length} {gost_match.group(1)}"
            return f"{fastener_type} {diameter}*{length}"
        
        # 14. Форматы с М размером (с сохранением запятой)
        pattern_m = r'[МM](\d+(?:[.,]\d+)?)(?:[xхX](\d+(?:[.,]\d+)?))?'
        match = re.search(pattern_m, text, re.IGNORECASE)
        if match:
            diameter = match.group(1)  # СОХРАНЯЕМ запятую
            length = match.group(2) if match.group(2) else None
            if length:
                length = length  # СОХРАНЯЕМ запятую в длине
                return f"{fastener_type} {diameter}*{length}"
            else:
                return f"{fastener_type} {diameter}"
        
        # 15. Форматы с артикулами (только цифры)
        pattern_article_only = r'(?:заклепк[аи]?|ЗВК)[\s]+(\d{5,})'
        match = re.search(pattern_article_only, text, re.IGNORECASE)
        if match:
            article = match.group(1)
            return f"{fastener_type} {article}"
        
        # 16. Форматы с артикулом после текста
        pattern_article_with_art = r'арт\.?\s*(\d+)'
        match = re.search(pattern_article_with_art, text, re.IGNORECASE)
        if match:
            article = match.group(1)
            size_match = re.search(r'(\d+(?:[.,]\d+)?)[хxХ](\d+)', text, re.IGNORECASE)
            if size_match:
                diameter = size_match.group(1)  # СОХРАНЯЕМ запятую
                length = size_match.group(2)
                return f"{fastener_type} {diameter}*{length} {article}"
            return f"{fastener_type} {article}"
        
        # 17. Специальный формат
        pattern_special_m = r'[МM](\d+(?:[.,]\d+)?)[xхX](\d+(?:[.,]\d+)?)[/\d]*\s+арт\.?\s*(\w+\d+)'
        match = re.search(pattern_special_m, text, re.IGNORECASE)
        if match:
            diameter = match.group(1)  # СОХРАНЯЕМ запятую
            length = match.group(2)    # СОХРАНЯЕМ запятую
            article = match.group(3)
            return f"{fastener_type} {diameter}*{length} {article}"
        
        # 18. Формат с артикулом в начале
        pattern_just_numbers = r'^(\d{5,})$'
        match = re.search(pattern_just_numbers, text.strip())
        if match:
            return f"{fastener_type} {match.group(1)}"
        
        return text


# Примеры для тестирования
if __name__ == "__main__":
    processor = RivetProcessor()
    
    test_cases = [
        "Заклепка \"слепая\" DIN EN ISO 15977 3,2x8-AIA/St",
        "Заклепка \"слепая\" ГОСТ Р ИСО 15977-2017-4х12-AIA/St-L",
        "Заклепка 2,5х7.31 ГОСТ 10300-80",
        "Заклепка 5-20-Ан.Окс. ОСТ 1 34087-80",
        "Заклепка DIN 7338 A3х8-St-St-A1",
        "Заклепка DIN 9315 М8",
        "Гайка-заклепка M5 23307050230",
        "Заклепка-болт 29M064015",
    ]
    
    for test in test_cases:
        result = processor.process(test)
        print(f"Вход: {test}")
        print(f"Выход: {result}")
        print("-" * 50)