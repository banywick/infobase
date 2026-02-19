import re
from ..base_processor import FastenerProcessor


class CotterPinProcessor(FastenerProcessor):
    """Процессор для шплинтов"""
    
    def can_process(self, text):
        return bool(re.search(r'шплинт', text, re.IGNORECASE))
    
    def process(self, text):
        # Удаляем префиксы DEL_ или del_
        text = self.remove_del_prefix(text)
        
        # ==============================================
        # ЛОГИКА ДЛЯ ШПЛИНТОВ
        # ==============================================
        
        fastener_type = "шплинт"
        
        # 1. DIN форматы с Form: "Шплинт DIN 11024 8 Form D"
        pattern_din_int = r'(?:DIN|din)[\s\-]*(\d+)[\s\-]*(\d+)\s+Form'
        match = re.search(pattern_din_int, text, re.IGNORECASE)
        if match:
            standard = match.group(1)
            diameter = match.group(2)
            return f"{fastener_type} *{diameter} {standard}"
        
        # 2. DIN форматы с десятичным размером: "Шплинт DIN 11024 6.3 Form D"
        pattern_din_decimal = r'(?:DIN|din)[\s\-]*(\d+)[\s\-]*(\d+(?:[.,]\d+)?)\s+Form'
        match = re.search(pattern_din_decimal, text, re.IGNORECASE)
        if match:
            standard = match.group(1)
            diameter = match.group(2).replace('.', ',')
            return f"{fastener_type} *{diameter}* {standard}"
        
        # 3. ГОСТ форматы: "Шплинт 6,3х45.019 ГОСТ 397-79"
        pattern_gost = r'(\d+(?:[.,]\d+)?)[хxХ](\d+)(?:[\.\d\s]*)(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost, text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace('.', ',')
            length = match.group(2)
            standard = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 4. ГОСТ форматы с дополнительными точками: "Шплинт 2,5х22.2.016 ГОСТ 397-79"
        pattern_gost_complex = r'(\d+(?:[.,]\d+)?)[хxХ](\d+)[\.\d]*?(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_complex, text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace('.', ',')
            length = match.group(2)
            standard = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 5. Специальный случай: "Шплинт 1х6.3.033 ГОСТ 397-79" -> "1*6 397"
        pattern_gost_round = r'(\d+)[хxХ](\d+)[\.]\d+[\.\d]*?(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_round, text, re.IGNORECASE)
        if match:
            diameter = match.group(1)
            length = match.group(2)  # Берем целую часть длины
            standard = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 6. Формат с размером и артикулом в скобках: "Шплинт 5x36 (258069)"
        pattern_with_brackets = r'(\d+(?:[.,]\d+)?)[xхX](\d+)\s*\((\d+)\)'
        match = re.search(pattern_with_brackets, text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace('.', ',')
            length = match.group(2)
            article = match.group(3)
            return f"{fastener_type} {diameter}x{length} ({article})"
        
        # 7. Формат с размером и артикулом: "Шплинт 2х16 258013"
        pattern_with_article = r'(\d+(?:[.,]\d+)?)[хxХ](\d+)\s+(\d{5,})'
        match = re.search(pattern_with_article, text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace('.', ',')
            length = match.group(2)
            article = match.group(3)
            return f"{fastener_type} {diameter}x{length} {article}"
        
        # 8. Простой формат с размером: "Шплинт 3,2х22 Ц9хр ГОСТ 397-79"
        pattern_simple = r'(\d+(?:[.,]\d+)?)[хxХ](\d+)'
        match = re.search(pattern_simple, text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace('.', ',')
            length = match.group(2)
            # Проверяем, есть ли ГОСТ отдельно
            gost_match = re.search(r'(?:ГОСТ|гост)[\s\-]*(\d+)', text, re.IGNORECASE)
            if gost_match:
                return f"{fastener_type} {diameter}*{length} {gost_match.group(1)}"
            return f"{fastener_type} {diameter}x{length}"
        
        # 9. DIN форматы без Form (если не подошли предыдущие)
        pattern_din_any = r'(?:DIN|din)[\s\-]*(\d+)[\s\-]*(\d+(?:[.,]\d+)?)'
        match = re.search(pattern_din_any, text, re.IGNORECASE)
        if match:
            standard = match.group(1)
            diameter = match.group(2).replace('.', ',')
            # Проверяем, есть ли десятичная часть
            if re.search(r'[.,]', diameter):
                return f"{fastener_type} *{diameter}* {standard}"
            else:
                return f"{fastener_type} *{diameter} {standard}"
        
        # Если ничего не найдено, возвращаем исходный текст
        return text


# Примеры для тестирования
if __name__ == "__main__":
    processor = CotterPinProcessor()
    
    test_cases = [
        "Шплинт DIN 11024 8 Form D",
        "Шплинт DIN 11024 6.3 Form D",
        "Шплинт 6,3х45.019 ГОСТ 397-79",
        "Шплинт 5x36 (258069)",
        "Шплинт 3,2х22 Ц9хр ГОСТ 397-79",
        "Шплинт 2х16 258013",
        "Шплинт 2,5х22.2.016 ГОСТ 397-79",
        "Шплинт 1х6.3.033 ГОСТ 397-79",
        "Шплинт 1,2х100 258250",
    ]
    
    for test in test_cases:
        result = processor.process(test)
        print(f"Вход: {test}")
        print(f"Выход: {result}")
        print("-" * 50)