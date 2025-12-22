import re

class TransformationString:
    @staticmethod
    def screw(input_text):
        # Удаляем префиксы DEL_ или del_
        input_text = re.sub(r'^DEL_|^del_', '', input_text.strip())

        # Регулярные выражения для извлечения диаметра, длины и стандарта
        patterns = [
            # ГОСТ-форматы: "Винт А.М2-6gх10.36.013 ГОСТ 17473-80"
            (r'[Аа]?\.?[МM](\d+(?:[.,]\d+)?)[\-\s\w]*[XХx](\d+)[\.\d]*\s*ГОСТ\s*(\d+)', (1, 2, 3)),
            # DIN-форматы: "Винт DIN 912 M2x12-A4"
            (r'DIN\s*(\d+)\s*[M]\s*(\d+(?:[.,]\d+)?)[xх](\d+)', (2, 3, 1)),
            # Форматы типа "Винт 2.М2-6gх12.48.013 ГОСТ 17473-80"
            (r'[Аа]?\.?[МM](\d+(?:[.,]\d+)?)[\-\s\w]*[XХx](\d+)[\.\d]*\s*ГОСТ\s*(\d+)', (1, 2, 3)),
            # Форматы типа "Винт 2-4х14.01.019"
            (r'(\d+)\s*\-\s*(\d+)\s*[XХx]\s*(\d+)', (2, 3, '')),
            # Форматы типа "Винт 3х10.01.019"
            (r'(\d+)\s*[XХx]\s*(\d+)', (1, 2, '')),
            # Форматы типа "Винт М3*10"
            (r'[МM](\d+)\s*[\*]\s*(\d+)', (1, 2, '')),
            # Форматы типа "Винт М3х10"
            (r'[МM](\d+)\s*[XХx]\s*(\d+)', (1, 2, '')),
            # Форматы типа "Винт 3*10"
            (r'(?<![\d\-])(\d+)\s*[\*]\s*(\d+)(?![\d\-])', (1, 2, '')),
            # Форматы типа "Винт 3х10"
            (r'(?<![\d\-])(\d+)\s*[XХx]\s*(\d+)(?![\d\-])', (1, 2, '')),
            # Форматы с дробными числами "3.5х10"
            (r'(\d+[\.\,]\d+)\s*[XХx]\s*(\d+)', (1, 2, '')),
            # Форматы с артикулами "Винт 09 67 000 9924"
            (r'Винт\s+(\d+\s*\d+)', ('', '', '')),
        ]

        # Поиск по всем регулярным выражениям
        for pattern, (diameter_group, length_group, standard_group) in patterns:
            match = re.search(pattern, input_text)
            if match:
                diameter = match.group(diameter_group)
                length = match.group(length_group)
                standard = match.group(standard_group) if standard_group else ''

                # Нормализация диаметра и длины
                diameter = diameter.replace(',', '.')
                length = length.replace(',', '.')

                # Формируем результат
                return f"винт {diameter}*{length} {standard}"

        # Если не подошло ни одно регулярное выражение
        return f"{input_text}+"
