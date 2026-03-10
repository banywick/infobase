import re

from ..base_processor import FastenerProcessor  # Относительный импорт


class ScrewBoltProcessor(FastenerProcessor):
    """Процессор для винтов и болтов"""
    
    def can_process(self, text):
        return bool(re.search(r'винт|болт', text, re.IGNORECASE))
    
    def process(self, text):
        # Удаляем префиксы DEL_ или del_
        text = re.sub(r'^DEL_|^del_', '', text.strip())
        
        # Определяем точный тип
        if re.search(r'болт', text, re.IGNORECASE):
            fastener_type = "болт"
        else:
            fastener_type = "винт"
        
        # ==============================================
        # ЛОГИКА ДЛЯ ВИНТОВ И БОЛТОВ
        # ==============================================
        
        # 1. ГОСТ ISO форматы с дефисом в стандарте: "Винт ГОСТ ISO 7380-2 М3х6-08.8.А2"
        pattern_gost_iso_hyphen = r'(?:ГОСТ\s*ISO|ГОСТ\s*Р\s*ИСО|ГОСТ\s*Р\s*ISO)[\s\-]*(\d+[\-\d]*)[\s\-]*[МM](\d+(?:[.,]\d+)?)[\s]*[xхX*][\s]*(\d+)(?:[.,]\d+)?'
        match = re.search(pattern_gost_iso_hyphen, text, re.IGNORECASE)
        if match:
            standard = match.group(1)
            diameter = match.group(2).replace(',', '.')
            length = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 2. ISO/СТБ ISO форматы: "СТБ ISO 4762-2017 М5х12-8.8-A3L"
        pattern_iso = r'(?:СТБ\s*ISO|ISO|ГОСТ\s*Р\s*ИСО)[\s\-\.\d]*[МM](\d+(?:[.,]\d+)?)[\s]*[xхX*][\s]*(\d+)(?:[.,]\d+)?'
        match = re.search(pattern_iso, text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace(',', '.')
            length = match.group(2)
            std_match = re.search(r'(?:СТБ\s*ISO\s*(\d+[\-\d]*)|ISO\s*(\d+[\-\d]*)|ГОСТ\s*Р\s*ИСО\s*(\d+[\-\d]*))', text, re.IGNORECASE)
            standard = ''
            if std_match:
                for i in range(1, 4):
                    if std_match.group(i):
                        standard = std_match.group(i)
                        break
            if standard:
                return f"{fastener_type} {diameter}*{length} {standard}"
            return f"{fastener_type} {diameter}*{length}"
        
        # 3. ГОСТ форматы с М и десятичным диаметром: "Винт 2.М2,5-6gх10.68.013 ГОСТ 17473-80"
        pattern_gost_m_decimal = r'[АаВв]?\.?[МM](\d+(?:[.,]\d+)?)[\-\s\w\d]*[XХxх](\d+)(?:[.,]\d+)?[\.\d\s]*(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_m_decimal, text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace('.', ',')
            length = match.group(2)
            standard = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 4. ГОСТ форматы с М и целым диаметром: "Винт 2.М2-6gх12.48.013 ГОСТ 17473-80"
        pattern_gost_m_int = r'[АаВв]?\.?[МM](\d+)[\-\s\w\d]*[XХxх](\d+)(?:[.,]\d+)?[\.\d\s]*(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_m_int, text, re.IGNORECASE)
        if match:
            diameter = match.group(1)
            length = match.group(2)
            standard = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 5. ГОСТ форматы с диапазоном и десятичными числами: "Винт 2-2,5х12.01.019 ГОСТ 11652-80"
        pattern_gost_range_decimal = r'(\d+)[\-\s]+(\d+(?:[.,]\d+)?)[XХxх](\d+)(?:[.,]\d+)?[\.\d\s]*(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_range_decimal, text, re.IGNORECASE)
        if match:
            diameter = match.group(2).replace(',', '.')
            length = match.group(3)
            standard = match.group(4)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 6. ГОСТ форматы с диапазоном и целыми числами: "Винт 2-3х10.01.019 ГОСТ 10620-80"
        pattern_gost_range_int = r'(\d+)[\-\s]+(\d+)[XХxх](\d+)(?:[.,]\d+)?[\.\d\s]*(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_range_int, text, re.IGNORECASE)
        if match:
            diameter = match.group(2)
            length = match.group(3)
            standard = match.group(4)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 7. ГОСТ форматы с целым числом и х: "Винт 5х20.01.019 ГОСТ 11650-80"
        pattern_gost_int = r'(\d+)[XХxх](\d+)(?:[.,]\d+)?[\.\d\s]*(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_int, text, re.IGNORECASE)
        if match:
            diameter = match.group(1)
            length = match.group(2)
            standard = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 8. ГОСТ форматы с десятичным числом и х: "Винт 2,5х08.01.019 ГОСТ 11652-80"
        pattern_gost_decimal = r'(\d+[.,]\d+)[XХxх](\d+)(?:[.,]\d+)?[\.\d\s]*(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_decimal, text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace(',', '.')
            length = match.group(2)
            standard = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 9. DIN/ГОСТ форматы с М: "Болт DIN 6921 M16x140-10.9-St/Zn"
        pattern_din_m = r'(?:DIN|din|ГОСТ|гост)[\s\-]*(\d+)[\s\-]*[МM](\d+(?:[.,]\d+)?)[\s]*[xхX*][\s]*(\d+)(?:[.,]\d+)?'
        match = re.search(pattern_din_m, text, re.IGNORECASE)
        if match:
            standard = match.group(1)
            diameter = match.group(2).replace(',', '.')
            length = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 10. Простые форматы с М и ГОСТом: "DEL_Винт М12-6gx30.66.019 ГОСТ 11738-84"
        pattern_simple_m_gost = r'[МM](\d+(?:[.,]\d+)?)[\-\s\w\d]*[XХxх*](\d+)(?:[.,]\d+)?[\.\d\s]*(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_simple_m_gost, text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace(',', '.')
            length = match.group(2)
            standard = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 11. DIN форматы с ST: "DEL_Винт DIN 968 ST4,2x16-A2-20H-C-H"
        pattern_din_st = r'(?:DIN|din)[\s\-]*(\d+)[\s\-]*(?:ST|st)[\s]*(\d+(?:[.,]\d+)?)[\s]*[xхX][\s]*(\d+)(?:[.,]\d+)?'
        match = re.search(pattern_din_st, text, re.IGNORECASE)
        if match:
            standard = match.group(1)
            diameter = match.group(2).replace(',', '.')
            length = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 12. Обычные DIN форматы: "DEL_Винт DIN 912 M5x8-8.8-St/Zn"
        pattern_din = r'(?:DIN|din)[\s\-]*(\d+)[\s\-]*[МM]?(\d+(?:[.,]\d+)?)[\s]*[xхX*][\s]*(\d+)(?:[.,]\d+)?'
        match = re.search(pattern_din, text, re.IGNORECASE)
        if match:
            standard = match.group(1)
            diameter = match.group(2).replace(',', '.')
            length = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 13. ST форматы без DIN: "ST4,2x16"
        pattern_st = r'(?:ST|st)[\s]*(\d+(?:[.,]\d+)?)[\s]*[xхX][\s]*(\d+)(?:[.,]\d+)?'
        match = re.search(pattern_st, text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace(',', '.')
            length = match.group(2)
            return f"{fastener_type} {diameter}*{length}"
        
        # 14. Простые форматы с М без ГОСТа: "Винт М3х10"
        pattern_simple_m = r'[МM](\d+(?:[.,]\d+)?)[\-\s\w\d]*[XХxх*](\d+)(?:[.,]\d+)?'
        match = re.search(pattern_simple_m, text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace(',', '.')
            length = match.group(2)
            gost_match = re.search(r'(?:ГОСТ|гост)[\s\-]*(\d+)', text, re.IGNORECASE)
            if gost_match:
                return f"{fastener_type} {diameter}*{length} {gost_match.group(1)}"
            return f"{fastener_type} {diameter}*{length}"
        
        # 15. Простые форматы без М с ГОСТом: "Винт 3х10.01.019 ГОСТ 11652-80"
        pattern_simple_gost = r'(\d+(?:[.,]\d+)?)[\s]*[xхX*][\s]*(\d+)(?:[.,]\d+)?[\.\d\s]*(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_simple_gost, text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace(',', '.')
            length = match.group(2)
            standard = match.group(3)
            return f"{fastener_type} {diameter}*{length} {standard}"
        
        # 16. Простые форматы без М без ГОСТа: "Винт 3х10"
        pattern_simple = r'(\d+(?:[.,]\d+)?)[\s]*[xхX*][\s]*(\d+)(?:[.,]\d+)?'
        match = re.search(pattern_simple, text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace(',', '.')
            length = match.group(2)
            return f"{fastener_type} {diameter}*{length}"
        
        # 17. Форматы с диапазоном: "Винт 2-4х14"
        pattern_range = r'(\d+)\s*-\s*(\d+)\s*[xхX]\s*(\d+)(?:[.,]\d+)?'
        match = re.search(pattern_range, text, re.IGNORECASE)
        if match:
            diameter = match.group(2)
            length = match.group(3)
            return f"{fastener_type} {diameter}*{length}"
        
        # 18. Только М и диаметр: "DEL_Винт М3"
        pattern_m_only = r'[МM](\d+(?:[.,]\d+)?)(?![xхX*\d])'
        match = re.search(pattern_m_only, text, re.IGNORECASE)
        if match:
            diameter = match.group(1).replace(',', '.')
            return f"{fastener_type} {diameter}"
        
        # 19. ГОСТ с другим форматом: "Винт 7006-1215 ГОСТ 9052-69"
        pattern_gost_other = r'(\d+[\-\s]\d+)[\s]*(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_other, text, re.IGNORECASE)
        if match:
            article = match.group(1)
            standard = match.group(2)
            return f"{fastener_type} {article} {standard}"
        
        # 20. Форматы с артикулами: "Винт 09 67 000 9924"
        pattern_article = r'(?:Винт|Болт)\s+(\d[\d\s]+\d)'
        match = re.search(pattern_article, text, re.IGNORECASE)
        if match:
            article = re.sub(r'\s+', '', match.group(1))
            return f"{fastener_type} {article}"
        
        # 21. ОСТ форматы: "Винт 3-10-Кд-ОСТ 1 31538-80"
        pattern_ost = r'(\d+[\-\d\w\.]*)[\s]*(?:ОСТ|ост)[\s\d\-\.]*'
        match = re.search(pattern_ost, text, re.IGNORECASE)
        if match:
            article = match.group(1)
            return f"{fastener_type} {article}"
        
        return text