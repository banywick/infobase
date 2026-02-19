import re
from ..base_processor import FastenerProcessor


class PinProcessor(FastenerProcessor):
    """Процессор для штифтов"""
    
    def can_process(self, text):
        return bool(re.search(r'штифт', text, re.IGNORECASE))
    
    def process(self, text):
        # Удаляем префиксы DEL_ или del_
        text = self.remove_del_prefix(text)
        
        # ==============================================
        # ЛОГИКА ДЛЯ ШТИФТОВ
        # ==============================================
        
        fastener_type = "штифт"
        
        # Проверяем на специальные типы штифтов
        if re.search(r'упорный', text, re.IGNORECASE):
            match = re.search(r'штифт\s+упорный\s+(\S+)', text, re.IGNORECASE)
            if match:
                return f"{fastener_type} упорный {match.group(1)}"
            return text
        
        # 1. Специальный случай: "Штифт 3,0х14" -> "штифт 3*14"
        pattern_zero_decimal = r'(\d+),0[хxХ](\d+)'
        match = re.search(pattern_zero_decimal, text)
        if match:
            diameter = match.group(1)  # Берем только целую часть
            length = match.group(2)
            std_match = re.search(r'(?:ГОСТ|гост)[\s\-]*(\d+)', text, re.IGNORECASE)
            if std_match:
                return f"{fastener_type} {diameter}*{length} {std_match.group(1)}"
            return f"{fastener_type} {diameter}*{length}"
        
        # 2. Случай с "m" в размере: "Штифт 3m6х25" -> "штифт 3*25"
        pattern_m_in_size = r'(\d+)m\d+[хxХ](\d+)'
        match = re.search(pattern_m_in_size, text, re.IGNORECASE)
        if match:
            diameter = match.group(1)  # Берем первую цифру (до m)
            length = match.group(2)
            std_match = re.search(r'(?:ГОСТ|гост)[\s\-]*(\d+)', text, re.IGNORECASE)
            if std_match:
                return f"{fastener_type} {diameter}*{length} {std_match.group(1)}"
            return f"{fastener_type} {diameter}*{length}"
        
        # 3. Специальный случай: "Штифт 2.10х24" -> "штифт 10*24"
        pattern_double_number = r'(\d+)\.(\d+)[хxХ](\d+)'
        match = re.search(pattern_double_number, text)
        if match:
            diameter = match.group(2)  # Берем число после точки
            length = match.group(3)
            std_match = re.search(r'(?:ГОСТ|гост)[\s\-]*(\d+)', text, re.IGNORECASE)
            if std_match:
                return f"{fastener_type} {diameter}*{length} {std_match.group(1)}"
            return f"{fastener_type} {diameter}*{length}"
        
        # 4. ГОСТ форматы с точкой после диаметра: "Штифт 1.5х8 Хим.Окс.прм. ГОСТ 24296-93"
        pattern_gost_with_dot = r'(\d+(?:[.,]\d+)?)[\.]?[хxХ](\d+)(?:[\.\d\s\w]*)(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_with_dot, text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace('.', ',')  # Заменяем точку на запятую для десятичных
            # Убираем ,0 если есть
            diameter = re.sub(r',0$', '', diameter)
            length = match.group(2)
            standard = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 5. ГОСТ форматы с десятичной запятой: "Штифт 2,5х20.019 ГОСТ 3128-70"
        pattern_gost_comma = r'(\d+,\d+)[хxХ](\d+)(?:[\.\d\s]*)(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_comma, text, re.IGNORECASE)
        if match:
            diameter = match.group(1)
            # Убираем ,0 если есть
            diameter = re.sub(r',0$', '', diameter)
            length = match.group(2)
            standard = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 6. ГОСТ форматы простые: "Штифт 12х30.Хим.Окс.прм ГОСТ 3128-70"
        pattern_gost_simple = r'(\d+)[хxХ](\d+)(?:[\.\d\s\w]*)(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_simple, text, re.IGNORECASE)
        if match:
            diameter = match.group(1)
            length = match.group(2)
            standard = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 7. ГОСТ форматы с префиксом А: "Штифт А.6х55.60С2 ГОСТ 14229-93"
        pattern_gost_with_a = r'А\.?(\d+)[хxХ](\d+)(?:[\.\d\s\w]*)(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_with_a, text, re.IGNORECASE)
        if match:
            diameter = match.group(1)
            length = match.group(2)
            standard = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 8. DIN форматы: "Штифт DIN 11023 8x42"
        pattern_din = r'(?:DIN|din)[\s\-]*(\d+)[\s\-]*(\d+)[xхX](\d+)'
        match = re.search(pattern_din, text, re.IGNORECASE)
        if match:
            standard = match.group(1)
            diameter = match.group(2)
            length = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 9. DIN форматы с префиксом: "Штифт конический DIN 1 5х36"
        pattern_din_with_prefix = r'(?:DIN|din)[\s\-]*(\d+)[\s\-]*(\d+)[хxХ](\d+)'
        match = re.search(pattern_din_with_prefix, text, re.IGNORECASE)
        if match:
            standard = match.group(1)
            diameter = match.group(2)
            length = match.group(3)
            if re.search(r'конический', text, re.IGNORECASE):
                return f"{fastener_type} конический {diameter}*{length} {standard}"
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 10. Простые форматы с размером и ГОСТом отдельно
        pattern_simple_with_gost = r'(\d+(?:[.,]\d+)?)[хxХ](\d+)(?:[\.\d\s\w]*?)(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_simple_with_gost, text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace('.', ',')
            # Убираем ,0 если есть
            diameter = re.sub(r',0$', '', diameter)
            length = match.group(2)
            standard = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 11. Простые форматы с размером (без ГОСТа)
        pattern_simple = r'(\d+(?:[.,]\d+)?)[хxХ](\d+)'
        match = re.search(pattern_simple, text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace('.', ',')
            # Убираем ,0 если есть
            diameter = re.sub(r',0$', '', diameter)
            length = match.group(2)
            gost_match = re.search(r'(?:ГОСТ|гост)[\s\-]*(\d+)', text, re.IGNORECASE)
            if gost_match:
                return f"{fastener_type} {diameter}*{length} {gost_match.group(1)}"
            return f"{fastener_type} {diameter}*{length}"
        
        # 12. Специальный случай: "Штифт упорный K0631.1820684"
        pattern_special_article = r'штифт\s+упорный\s+([A-Z]\d+\.\d+)'
        match = re.search(pattern_special_article, text, re.IGNORECASE)
        if match:
            article = match.group(1)
            return f"{fastener_type} упорный {article}"
        
        # 13. Форматы с артикулами
        pattern_article = r'штифт\s+([A-Z]?\d+[\d\.\-]*)'
        match = re.search(pattern_article, text, re.IGNORECASE)
        if match and not re.search(r'х', text):
            article = match.group(1)
            if re.search(r'конический', text, re.IGNORECASE):
                return f"{fastener_type} конический {article}"
            return f"{fastener_type} {article}"
        
        # Если ничего не найдено для штифтов, но есть слово "конический"
        if re.search(r'конический', text, re.IGNORECASE):
            std_match = re.search(r'(?:DIN|din)[\s\-]*(\d+)', text, re.IGNORECASE)
            size_match = re.search(r'(\d+)[хxХ](\d+)', text, re.IGNORECASE)
            if std_match and size_match:
                return f"{fastener_type} конический {size_match.group(1)}*{size_match.group(2)} {std_match.group(1)}"
            return text
        
        return text


# Примеры для тестирования
if __name__ == "__main__":
    processor = PinProcessor()
    
    test_cases = [
        "Штифт 3,0х14 Хим.Окс.прм ГОСТ 24296-93",
        "Штифт 3m6х25.Ц9.хр ГОСТ 3128-70",
        "Штифт 1.5х8 Хим.Окс.прм. ГОСТ 24296-93",
        "Штифт 2,5х20.019 ГОСТ 3128-70",
        "Штифт 2.10х24.Хим.Окс.прм ГОСТ 3128-70",
        "Штифт 3.6х22.Ц9.хр ГОСТ 3128-70",
        "Штифт DIN 11023 8x42",
    ]
    
    for test in test_cases:
        result = processor.process(test)
        print(f"Вход: {test}")
        print(f"Выход: {result}")
        print("-" * 50)