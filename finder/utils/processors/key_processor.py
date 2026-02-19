import re
from ..base_processor import FastenerProcessor


class KeyProcessor(FastenerProcessor):
    """Процессор для шпонок"""
    
    def can_process(self, text):
        return bool(re.search(r'шпонк', text, re.IGNORECASE))
    
    def process(self, text):
        # Удаляем префиксы DEL_ или del_
        text = self.remove_del_prefix(text)
        
        # ==============================================
        # ЛОГИКА ДЛЯ ШПОНОК
        # ==============================================
        
        fastener_type = "шпонка"
        
        # 1. Специальный случай: "Шпонка 3-14х9х24 ГОСТ 23360-78" -> "шпонка 14*9*24 23360"
        pattern_range_first = r'(\d+)[\-](\d+)[хxХ](\d+)[хxХ](\d+)'
        match = re.search(pattern_range_first, text, re.IGNORECASE)
        if match:
            first = match.group(1)
            width = match.group(2)      # Берем второе число (после дефиса) как ширину
            height = match.group(3)
            length = match.group(4)
            std_match = re.search(r'(?:ГОСТ|гост)[\s\-]*(\d+)', text, re.IGNORECASE)
            if std_match:
                return f"{fastener_type} {width}*{height}*{length} {std_match.group(1)}"
            return f"{fastener_type} {width}*{height}*{length}"
        
        # 2. Стандартный формат: "Шпонка 16х10х50 ГОСТ 23360-78"
        pattern_standard = r'(\d+)[хxХ](\d+)[хxХ](\d+)'
        match = re.search(pattern_standard, text, re.IGNORECASE)
        if match:
            width = match.group(1)
            height = match.group(2)
            length = match.group(3)
            std_match = re.search(r'(?:ГОСТ|гост)[\s\-]*(\d+)', text, re.IGNORECASE)
            if std_match:
                return f"{fastener_type} {width}*{height}*{length} {std_match.group(1)}"
            return f"{fastener_type} {width}*{height}*{length}"
        
        # 3. Формат с двумя размерами: "Шпонка 5х7,5 ГОСТ 24071-97"
        pattern_two_sizes = r'(\d+(?:[.,]\d+)?)[хxХ](\d+(?:[.,]\d+)?)'
        match = re.search(pattern_two_sizes, text, re.IGNORECASE)
        if match:
            width = match.group(1).replace('.', ',')
            height = match.group(2).replace('.', ',')
            std_match = re.search(r'(?:ГОСТ|гост)[\s\-]*(\d+)', text, re.IGNORECASE)
            if std_match:
                return f"{fastener_type} {width}*{height} {std_match.group(1)}"
            return f"{fastener_type} {width}*{height}"
        
        # 4. Формат с размером и ГОСТом без "х" между размерами (если нужно)
        pattern_with_gost = r'(\d+(?:[.,]\d+)?)[хxХ](\d+(?:[.,]\d+)?)(?:[хxХ](\d+))?(?:[\.\d\s\w]*)(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_with_gost, text, re.IGNORECASE)
        if match:
            width = match.group(1).replace('.', ',')
            height = match.group(2).replace('.', ',')
            length = match.group(3) if match.group(3) else ""
            standard = match.group(4)
            
            if length:
                return f"{fastener_type} {width}*{height}*{length} {standard}"
            else:
                return f"{fastener_type} {width}*{height} {standard}"
        
        # 5. Простой формат с тремя размерами без ГОСТа
        pattern_simple_three = r'(\d+(?:[.,]\d+)?)[хxХ](\d+(?:[.,]\d+)?)[хxХ](\d+)'
        match = re.search(pattern_simple_three, text, re.IGNORECASE)
        if match:
            width = match.group(1).replace('.', ',')
            height = match.group(2).replace('.', ',')
            length = match.group(3)
            return f"{fastener_type} {width}*{height}*{length}"
        
        # 6. Простой формат с двумя размерами без ГОСТа
        pattern_simple_two = r'(\d+(?:[.,]\d+)?)[хxХ](\d+(?:[.,]\d+)?)'
        match = re.search(pattern_simple_two, text, re.IGNORECASE)
        if match:
            width = match.group(1).replace('.', ',')
            height = match.group(2).replace('.', ',')
            return f"{fastener_type} {width}*{height}"
        
        # 7. Формат с артикулом (если есть цифры после "шпонка")
        pattern_article = r'шпонк[аи]?\s+(\d+[\d\s\-]*)'
        match = re.search(pattern_article, text, re.IGNORECASE)
        if match and not re.search(r'х', text):
            article = re.sub(r'\s+', '', match.group(1))
            return f"{fastener_type} {article}"
        
        # Если ничего не найдено, возвращаем исходный текст
        return text


# Примеры для тестирования
if __name__ == "__main__":
    processor = KeyProcessor()
    
    test_cases = [
        "Шпонка 16х10х50 ГОСТ 23360-78",
        "Шпонка 3-14х9х24 ГОСТ 23360-78",
        "Шпонка 5х7,5 ГОСТ 24071-97",
        "Шпонка 8х7х22 ГОСТ 23360-78",
        "Шпонка 10х8х32 ГОСТ 23360-78",
        "Шпонка 4х4х10",
        "Шпонка 6х6х18 ГОСТ 23360-78",
        "Шпонка 12х8х40",
    ]
    
    for test in test_cases:
        result = processor.process(test)
        print(f"Вход: {test}")
        print(f"Выход: {result}")
        print("-" * 50)