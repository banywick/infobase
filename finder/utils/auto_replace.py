import re

class TransformationString:
    @staticmethod
    def screw(input_text):
        # Удаляем префиксы DEL_ или del_
        input_text = re.sub(r'^DEL_|^del_', '', input_text.strip())
        original_text = input_text
        
        # Определяем тип из текста
        if re.search(r'болт', input_text, re.IGNORECASE):
            fastener_type = "болт"
        elif re.search(r'винт', input_text, re.IGNORECASE):
            fastener_type = "винт"
        else:
            fastener_type = "винт"  # по умолчанию
        
        # Паттерны в порядке приоритета
        
        # 1. ГОСТ форматы с М и десятичным диаметром: "Винт 2.М2,5-6gх10.68.013 ГОСТ 17473-80"
        pattern_gost_m_decimal = r'[АаВв]?\.?[МM](\d+(?:[.,]\d+)?)[\-\s\w\d]*[XХxх](\d+)(?:[.,]\d+)?[\.\d\s]*(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_m_decimal, input_text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace(',', '.')
            length = match.group(2)  # Берем только целую часть
            standard = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 2. ГОСТ форматы с М и целым диаметром: "Винт 2.М2-6gх12.48.013 ГОСТ 17473-80"
        pattern_gost_m_int = r'[АаВв]?\.?[МM](\d+)[\-\s\w\d]*[XХxх](\d+)(?:[.,]\d+)?[\.\d\s]*(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_m_int, input_text, re.IGNORECASE)
        if match:
            diameter = match.group(1)
            length = match.group(2)  # Берем только целую часть
            standard = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 3. ГОСТ форматы с диапазоном и десятичными числами: "Винт 2-2,5х12.01.019 ГОСТ 11652-80"
        pattern_gost_range_decimal = r'(\d+)[\-\s]+(\d+(?:[.,]\d+)?)[XХxх](\d+)(?:[.,]\d+)?[\.\d\s]*(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_range_decimal, input_text, re.IGNORECASE)
        if match:
            # Берем ВТОРОЕ число из диапазона (2-2,5 → берем 2,5)
            diameter = match.group(2).replace(',', '.')
            length = match.group(3)  # Берем только целую часть
            standard = match.group(4)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 4. ГОСТ форматы с диапазоном и целыми числами: "Винт 2-3х10.01.019 ГОСТ 10620-80"
        pattern_gost_range_int = r'(\d+)[\-\s]+(\d+)[XХxх](\d+)(?:[.,]\d+)?[\.\d\s]*(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_range_int, input_text, re.IGNORECASE)
        if match:
            # Берем ВТОРОЕ число из диапазона (2-3 → берем 3)
            diameter = match.group(2)
            length = match.group(3)  # Берем только целую часть
            standard = match.group(4)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 5. ГОСТ форматы с целым числом и х: "Винт 5х20.01.019 ГОСТ 11650-80"
        pattern_gost_int = r'(\d+)[XХxх](\d+)(?:[.,]\d+)?[\.\d\s]*(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_int, input_text, re.IGNORECASE)
        if match:
            diameter = match.group(1)
            length = match.group(2)  # Берем только целую часть
            standard = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 6. ГОСТ форматы с десятичным числом и х: "Винт 2,5х08.01.019 ГОСТ 11652-80"
        pattern_gost_decimal = r'(\d+[.,]\d+)[XХxх](\d+)(?:[.,]\d+)?[\.\d\s]*(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_decimal, input_text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace(',', '.')
            length = match.group(2)  # Берем только целую часть
            standard = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 7. DIN/ГОСТ форматы с М: "Болт DIN 6921 M16x140-10.9-St/Zn"
        pattern_din_m = r'(?:DIN|din|ГОСТ|гост)[\s\-]*(\d+)[\s\-]*[МM](\d+(?:[.,]\d+)?)[\s]*[xхX*][\s]*(\d+)(?:[.,]\d+)?'
        match = re.search(pattern_din_m, input_text, re.IGNORECASE)
        if match:
            standard = match.group(1)
            diameter = match.group(2).replace(',', '.')
            length = match.group(3)  # Берем только целую часть
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 8. Простые форматы с М и ГОСТом: "DEL_Винт М12-6gx30.66.019 ГОСТ 11738-84"
        pattern_simple_m_gost = r'[МM](\d+(?:[.,]\d+)?)[\-\s\w\d]*[XХxх*](\d+)(?:[.,]\d+)?[\.\d\s]*(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_simple_m_gost, input_text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace(',', '.')
            length = match.group(2)  # Берем только целую часть
            standard = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 9. DIN форматы с ST: "DEL_Винт DIN 968 ST4,2x16-A2-20H-C-H"
        pattern_din_st = r'(?:DIN|din)[\s\-]*(\d+)[\s\-]*(?:ST|st)[\s]*(\d+(?:[.,]\d+)?)[\s]*[xхX][\s]*(\d+)(?:[.,]\d+)?'
        match = re.search(pattern_din_st, input_text, re.IGNORECASE)
        if match:
            standard = match.group(1)
            diameter = match.group(2).replace(',', '.')
            length = match.group(3)  # Берем только целую часть
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 10. Обычные DIN форматы: "DEL_Винт DIN 912 M5x8-8.8-St/Zn"
        pattern_din = r'(?:DIN|din)[\s\-]*(\d+)[\s\-]*[МM]?(\d+(?:[.,]\d+)?)[\s]*[xхX*][\s]*(\d+)(?:[.,]\d+)?'
        match = re.search(pattern_din, input_text, re.IGNORECASE)
        if match:
            standard = match.group(1)
            diameter = match.group(2).replace(',', '.')
            length = match.group(3)  # Берем только целую часть
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 11. ST форматы без DIN: "ST4,2x16"
        pattern_st = r'(?:ST|st)[\s]*(\d+(?:[.,]\d+)?)[\s]*[xхX][\s]*(\d+)(?:[.,]\d+)?'
        match = re.search(pattern_st, input_text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace(',', '.')
            length = match.group(2)  # Берем только целую часть
            return f"{fastener_type} {diameter}*{length}"
        
        # 12. ISO/СТБ ISO форматы: "СТБ ISO 4762-2017 М5х12-8.8-A3L"
        pattern_iso = r'(?:СТБ\s*ISO|ISO|ГОСТ\s*Р\s*ИСО)[\s\-\.\d]*[МM](\d+(?:[.,]\d+)?)[\s]*[xхX*][\s]*(\d+)(?:[.,]\d+)?'
        match = re.search(pattern_iso, input_text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace(',', '.')
            length = match.group(2)  # Берем только целую часть
            # Извлекаем стандарт
            std_match = re.search(r'(?:СТБ\s*ISO\s*(\d+)|ISO\s*(\d+)|ГОСТ\s*Р\s*ИСО\s*(\d+))', input_text, re.IGNORECASE)
            standard = ''
            if std_match:
                for i in range(1, 4):
                    if std_match.group(i):
                        standard = std_match.group(i)
                        break
            if standard:
                return f"{fastener_type} {diameter}*{length} {standard}"
            return f"{fastener_type} {diameter}*{length}"
        
        # 13. Простые форматы с М без ГОСТа: "Винт М3х10"
        pattern_simple_m = r'[МM](\d+(?:[.,]\d+)?)[\-\s\w\d]*[XХxх*](\d+)(?:[.,]\d+)?'
        match = re.search(pattern_simple_m, input_text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace(',', '.')
            length = match.group(2)  # Берем только целую часть
            # Ищем ГОСТ отдельно
            gost_match = re.search(r'(?:ГОСТ|гост)[\s\-]*(\d+)', input_text, re.IGNORECASE)
            if gost_match:
                return f"{fastener_type} {diameter}*{length} {gost_match.group(1)}"
            return f"{fastener_type} {diameter}*{length}"
        
        # 14. Простые форматы без М с ГОСТом: "Винт 3х10.01.019 ГОСТ 11652-80"
        pattern_simple_gost = r'(\d+(?:[.,]\d+)?)[\s]*[xхX*][\s]*(\d+)(?:[.,]\d+)?[\.\d\s]*(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_simple_gost, input_text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace(',', '.')
            length = match.group(2)  # Берем только целую часть
            standard = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 15. Простые форматы без М без ГОСТа: "Винт 3х10"
        pattern_simple = r'(\d+(?:[.,]\d+)?)[\s]*[xхX*][\s]*(\d+)(?:[.,]\d+)?'
        match = re.search(pattern_simple, input_text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace(',', '.')
            length = match.group(2)  # Берем только целую часть
            return f"{fastener_type} {diameter}*{length}"
        
        # 16. Форматы с диапазоном: "Винт 2-4х14"
        pattern_range = r'(\d+)\s*-\s*(\d+)\s*[xхX]\s*(\d+)(?:[.,]\d+)?'
        match = re.search(pattern_range, input_text, re.IGNORECASE)
        if match:
            diameter = match.group(2)  # Берем второй диаметр из диапазона
            length = match.group(3)  # Берем только целую часть
            return f"{fastener_type} {diameter}*{length}"
        
        # 17. Только М и диаметр: "DEL_Винт М3" → "винт 3" (без звездочки!)
        pattern_m_only = r'[МM](\d+(?:[.,]\d+)?)(?![xхX*\d])'
        match = re.search(pattern_m_only, input_text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace(',', '.')
            return f"{fastener_type} {diameter}"
        
        # 18. ГОСТ с другим форматом: "Винт 7006-1215 ГОСТ 9052-69"
        pattern_gost_other = r'(\d+[\-\s]\d+)[\s]*(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_other, input_text, re.IGNORECASE)
        if match:
            article = match.group(1)
            standard = match.group(2)
            return f"{fastener_type} {article} {standard}"
        
        # 19. Форматы с артикулами: "Винт 09 67 000 9924"
        pattern_article = r'(?:Винт|Болт)\s+(\d[\d\s]+\d)'
        match = re.search(pattern_article, input_text, re.IGNORECASE)
        if match:
            article = re.sub(r'\s+', '', match.group(1))
            return f"{fastener_type} {article}"
        
        # 20. ОСТ форматы: "Винт 3-10-Кд-ОСТ 1 31538-80"
        pattern_ost = r'(\d+[\-\d\w\.]*)[\s]*(?:ОСТ|ост)[\s\d\-\.]*'
        match = re.search(pattern_ost, input_text, re.IGNORECASE)
        if match:
            article = match.group(1)
            return f"{fastener_type} {article}"
        
        # Если ничего не найдено
        return f"{original_text}+"

# Тестирование
test_cases = [
    ("Болт DIN 6921 M16x140-10.9-St/Zn", "болт 16*140 6921"),
    ("Болт DIN 933 M10x40-8.8-St/Zn", "болт 10*40 933"),
    ("Винт А2.М4-6gх16.66.019 ГОСТ 17473-80", "винт 4*16 17473"),
    ("Винт 2.М2,5-6gх10.68.013 ГОСТ 17473-80", "винт 2.5*10 17473"),
    ("Винт 2.М2-6gх12.48.013 ГОСТ 17473-80", "винт 2*12 17473"),
    ("Винт 2.М6-6gх20.48 ГОСТ 17473-80", "винт 6*20 17473"),
    ("Винт 2-2,5х12.01.019 ГОСТ 11652-80", "винт 2.5*12 11652"),
    ("Винт 2-3х10.01.019 ГОСТ 10620-80", "винт 3*10 10620"),
    ("Винт 3х10.01.019 ГОСТ 11652-80", "винт 3*10 11652"),
    ("Винт 5х20.01.019 ГОСТ 11650-80", "винт 5*20 11650"),
    ("Винт 2,5х08.01.019 ГОСТ 11652-80", "винт 2.5*8 11652"),
    ("DEL_Винт DIN 912 M5x8-8.8-St/Zn", "винт 5*8 912"),
    ("DEL_Винт DIN 968 ST4,2x16-A2-20H-C-H", "винт 4.2*16 968"),
    ("DEL_Винт М12-6gx30.66.019 ГОСТ 11738-84", "винт 12*30 11738"),
    ("Винт М3х10", "винт 3*10"),
    ("Винт 2-4х14", "винт 4*14"),
    ("Винт М3", "винт 3"),
    ("Болт М12х60", "болт 12*60"),
    ("Болт 10х50", "болт 10*50"),
]

print("Тестирование преобразования винтов и болтов:")
print("=" * 90)
for i, (test, expected) in enumerate(test_cases, 1):
    result = TransformationString.screw(test)
    status = "✓" if result == expected else "✗"
    print(f"{i:2}. {test:<70} → {result:<25} {status} (ожидалось: {expected})")