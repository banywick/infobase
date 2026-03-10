import re
from ..base_processor import FastenerProcessor


class RingProcessor(FastenerProcessor):
    """Процессор для колец"""
    
    def can_process(self, text):
        return bool(re.search(r'кольц', text, re.IGNORECASE))
    
    def process(self, text):
        # Удаляем префиксы DEL_ или del_
        text = self.remove_del_prefix(text)
        
        # ==============================================
        # ЛОГИКА ДЛЯ КОЛЕЦ
        # ==============================================
        
        fastener_type = "кольцо"
        
        # Проверяем на специальные типы
        is_o_ring = bool(re.search(r'O-ring|O-кольцо', text, re.IGNORECASE))
        is_stop = bool(re.search(r'стопорное', text, re.IGNORECASE))
        is_cut = bool(re.search(r'врезное', text, re.IGNORECASE))
        is_bayonet = bool(re.search(r'байонетное', text, re.IGNORECASE))
        
        if is_o_ring:
            fastener_type = "кольцо O-ring"
        elif is_stop:
            fastener_type = "кольцо стопорное"
        elif is_cut:
            fastener_type = "кольцо врезное"
        elif is_bayonet:
            fastener_type = "кольцо байонетное"
        
        # 1. Самый простой паттерн для А и В (высший приоритет)
        # "Кольцо А5 ГОСТ 13942-86" -> "кольцо *5 13942"
        pattern_ab_simple = r'кольц[ао]\s+([AАBВ])(\d+)(?:\s+ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_ab_simple, text, re.IGNORECASE)
        if match and not (is_cut or is_bayonet):
            diameter = match.group(2)
            standard = match.group(3)
            return f"{fastener_type} *{diameter} {standard}"
        
        # 2. Паттерн для А и В с точкой и доп. символами
        # "Кольцо А10.Ц6 ГОСТ 13942-86" -> "кольцо *10 13942"
        pattern_ab_dot = r'кольц[ао]\s+([AАBВ])(\d+)[\.][^\s]+(?:\s+ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_ab_dot, text, re.IGNORECASE)
        if match and not (is_cut or is_bayonet):
            diameter = match.group(2)
            standard = match.group(3)
            return f"{fastener_type} *{diameter} {standard}"
        
        # 3. Паттерн для А и В с любыми символами между
        # "Кольцо А90.60С2А.Кд6.хр ГОСТ 13941-86" -> "кольцо *90 13941"
        pattern_ab_complex = r'кольц[ао]\s+([AАBВ])(\d+)[\.\d\w\.]+(?:\s+ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_ab_complex, text, re.IGNORECASE)
        if match and not (is_cut or is_bayonet):
            diameter = match.group(2)
            standard = match.group(3)
            return f"{fastener_type} *{diameter} {standard}"
        
        # 4. Универсальный паттерн для А и В (если не сработали выше)
        # Ищет А или В, потом цифры, потом где-то ГОСТ
        pattern_ab_universal = r'([AАBВ])(\d+).*?(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_ab_universal, text, re.IGNORECASE)
        if match and not (is_cut or is_bayonet) and not re.search(r'врезное|байонетное', text, re.IGNORECASE):
            diameter = match.group(2)
            standard = match.group(3)
            return f"{fastener_type} *{diameter} {standard}"
        
        # 5. ГОСТ форматы с тремя числами: "Кольцо 003-006-19 ГОСТ 9833-73"
        pattern_gost_three = r'(\d+)[\-](\d+)[\-](\d+).*?(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_three, text, re.IGNORECASE)
        if match:
            return f"{fastener_type} {match.group(1)} {match.group(2)} {match.group(3)} {match.group(4)}"
        
        # 6. ГОСТ форматы с четырьмя числами: "Кольцо 005-009-25-2-2 ГОСТ 18829-2017"
        pattern_gost_four = r'(\d+)[\-](\d+)[\-](\d+)[\-](\d+)[\-](\d+).*?(?:ГОСТ|гост)[\s\-]*(\d+)'
        match = re.search(pattern_gost_four, text, re.IGNORECASE)
        if match:
            return f"{fastener_type} {match.group(1)} {match.group(2)} {match.group(3)} {match.group(4)} {match.group(5)} {match.group(6)}"
        
        # 7. DIN 3771 форматы
        pattern_din_3771 = r'(?:DIN|din)[\s\-]*(\d+)[\s\-]*(\d+(?:[.,]\d+)?)[xхX](\d+(?:[.,]\d+)?)[\-]([A-Z])[\-]([A-Z0-9]+)'
        match = re.search(pattern_din_3771, text, re.IGNORECASE)
        if match:
            standard = match.group(1)
            diameter = match.group(2).replace('.', ',')
            cross_section = match.group(3).replace('.', ',')
            material_code = match.group(4)
            material = match.group(5)
            return f"{fastener_type} {standard} {diameter} {cross_section} {material_code} {material}"
        
        # 8. DIN 3869 форматы
        pattern_din_3869 = r'(?:DIN|din)[\s\-]*(\d+)[\s\-]*(\d+(?:[.,]\d+)?)[xхX](\d+(?:[.,]\d+)?)[xхX](\d+(?:[.,]\d+)?)[\-]([A-Z0-9]+)'
        match = re.search(pattern_din_3869, text, re.IGNORECASE)
        if match:
            standard = match.group(1)
            inner_d = match.group(2).replace('.', ',')
            outer_d = match.group(3).replace('.', ',')
            cross_section = match.group(4).replace('.', ',')
            material = match.group(5)
            return f"{fastener_type} {standard} {inner_d} {outer_d} {cross_section} {material}"
        
        # 9. DIN 7993: "Кольцо DIN 7993 A 6"
        pattern_din_7993 = r'(?:DIN|din)[\s\-]*(\d+)[\s\-]*([A-Z])\s*(\d+)'
        match = re.search(pattern_din_7993, text, re.IGNORECASE)
        if match:
            standard = match.group(1)
            diameter = match.group(3)
            return f"{fastener_type} {standard} *{diameter}"
        
        # 10. O-ring форматы
        pattern_o_ring = r'O-ring\s+(\d+)[xхX](\d+(?:[.,]\d+)?).*?ISO[\s\-]*(\d+)'
        match = re.search(pattern_o_ring, text, re.IGNORECASE)
        if match:
            diameter = match.group(1)
            cross_section = match.group(2).replace('.', ',')
            standard = match.group(3)
            return f"{fastener_type} {diameter} {cross_section} {standard}"
        
        # 11. SE форматы
        pattern_se = r'SE[\-]([A-Z]+)[\-](\d+)[\-](\d+(?:[.,]\d+)?)[xхX](\d+(?:[.,]\d+)?)[\-]([A-Z0-9]+)[\-](\d+)'
        match = re.search(pattern_se, text, re.IGNORECASE)
        if match:
            series = match.group(1)
            code = match.group(2)
            inner_d = match.group(3).replace('.', ',')
            cross_section = match.group(4).replace('.', ',')
            material = match.group(5)
            variant = match.group(6)
            return f"{fastener_type} {series} {code} {inner_d} {cross_section} {material} {variant}"
        
        # 12. Кольцо байонетное
        if is_bayonet:
            pattern_bayonet = r'байонетное.*?арт\.?\s*([A-Z]+)\s*(\d+[\.]\d+)'
            match = re.search(pattern_bayonet, text, re.IGNORECASE)
            if match:
                prefix = match.group(1)
                article = match.group(2)
                return f"{fastener_type} {prefix} {article}"
        
        # 13. Кольцо врезное
        if is_cut:
            pattern_cut = r'врезное\s+([A-Z]?)(\d+)[/](\d+)'
            match = re.search(pattern_cut, text, re.IGNORECASE)
            if match:
                prefix = match.group(1)
                article = match.group(2)
                size = match.group(3)
                if prefix:
                    return f"{fastener_type} {prefix}{article} {size}"
                return f"{fastener_type} {article} {size}"
            
            pattern_cut_text = r'врезное\s+([A-Z]\d+[A-Z]+)'
            match = re.search(pattern_cut_text, text, re.IGNORECASE)
            if match:
                code = match.group(1)
                numbers = re.findall(r'\d+', code)
                letters = re.findall(r'[A-Z]+', code)
                if numbers and letters:
                    return f"{fastener_type} {numbers[0]} {''.join(letters)}"
                return f"{fastener_type} {code}"
        
        # 14. Стопорные кольца
        if is_stop:
            pattern_stop = r'(?:DIN|din)[\s\-]*(\d+)[\s\-]*(\d+)[xхX](\d+)'
            match = re.search(pattern_stop, text, re.IGNORECASE)
            if match:
                standard = match.group(1)
                diameter = match.group(2)
                thickness = match.group(3)
                return f"{fastener_type} {standard} {diameter} {thickness}"
        
        # Если ничего не найдено, возвращаем исходный текст
        return text


# Примеры для тестирования
if __name__ == "__main__":
    processor = RingProcessor()
    
    test_cases = [
        "Кольцо А5 ГОСТ 13942-86",
        "Кольцо А10 ГОСТ 13942-86",
        "Кольцо А100 ГОСТ 13942-86",
        "Кольцо B5 ГОСТ 13942-86",
        "Кольцо B10 ГОСТ 13942-86",
        "Кольцо B100 ГОСТ 13942-86",
        "Кольцо А10.Ц6 ГОСТ 13942-86",
        "Кольцо А10.Ц9.хр ГОСТ 13942-86",
        "Кольцо А12.Хим.Окс.прм. ГОСТ 13942-86",
        "Кольцо А90.60С2А.Кд6.хр ГОСТ 13941-86",
        "Кольцо А5.019 ГОСТ 13942-86",
        "Кольцо А5.Ц6.хр ГОСТ 13942-86",
        "Кольцо В10.019 ГОСТ 13940-86",
        "Кольцо В10.Ц9.хр ГОСТ 13942-86",
    ]
    
    for test in test_cases:
        result = processor.process(test)
        print(f"Вход: {test}")
        print(f"Выход: {result}")
        print("-" * 50)