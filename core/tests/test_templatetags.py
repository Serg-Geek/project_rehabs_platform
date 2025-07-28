from django.test import TestCase
from django.template import Template, Context
from django.template.defaultfilters import floatformat
from core.templatetags.russian_plural import year_plural, russian_plural


class RussianPluralTemplateTagsTest(TestCase):
    """Тесты для тегов шаблонов russian_plural.py"""
    
    def test_year_plural_filter(self):
        """Тест фильтра year_plural"""
        # Тестируем различные случаи склонения
        test_cases = [
            (1, "1 год"),
            (2, "2 года"),
            (5, "5 лет"),
            (11, "11 лет"),
            (21, "21 год"),
            (22, "22 года"),
            (25, "25 лет"),
            (31, "31 год"),
            (32, "32 года"),
            (35, "35 лет"),
            (101, "101 год"),
            (102, "102 года"),
            (105, "105 лет"),
            (111, "111 лет"),
            (121, "121 год"),
            (122, "122 года"),
            (125, "125 лет"),
        ]
        
        for number, expected in test_cases:
            with self.subTest(number=number):
                result = year_plural(number)
                self.assertEqual(result, expected)
    
    def test_year_plural_filter_invalid_input(self):
        """Тест фильтра year_plural с некорректными данными"""
        # Тестируем некорректные входные данные
        test_cases = [
            ("abc", "abc лет"),
            ("", " лет"),
            (None, "None лет"),
            ("12.5", "12.5 лет"),
        ]
        
        for value, expected in test_cases:
            with self.subTest(value=value):
                result = year_plural(value)
                self.assertEqual(result, expected)
    
    def test_russian_plural_filter(self):
        """Тест фильтра russian_plural"""
        # Тестируем различные случаи склонения
        test_cases = [
            (1, "учреждение,учреждения,учреждений", "1 учреждение"),
            (2, "учреждение,учреждения,учреждений", "2 учреждения"),
            (5, "учреждение,учреждения,учреждений", "5 учреждений"),
            (11, "учреждение,учреждения,учреждений", "11 учреждений"),
            (21, "учреждение,учреждения,учреждений", "21 учреждение"),
            (22, "учреждение,учреждения,учреждений", "22 учреждения"),
            (25, "учреждение,учреждения,учреждений", "25 учреждений"),
            (1, "врач,врача,врачей", "1 врач"),
            (2, "врач,врача,врачей", "2 врача"),
            (5, "врач,врача,врачей", "5 врачей"),
            (1, "клиника,клиники,клиник", "1 клиника"),
            (2, "клиника,клиники,клиник", "2 клиники"),
            (5, "клиника,клиники,клиник", "5 клиник"),
        ]
        
        for number, forms, expected in test_cases:
            with self.subTest(number=number, forms=forms):
                result = russian_plural(number, forms)
                self.assertEqual(result, expected)
    
    def test_russian_plural_filter_invalid_input(self):
        """Тест фильтра russian_plural с некорректными данными"""
        # Тестируем некорректные входные данные
        test_cases = [
            ("abc", "учреждение,учреждения,учреждений", "abc учреждений"),
            ("", "учреждение,учреждения,учреждений", " учреждений"),
            (None, "учреждение,учреждения,учреждений", "None учреждений"),
            ("12.5", "учреждение,учреждения,учреждений", "12.5 учреждений"),
        ]
        
        for value, forms, expected in test_cases:
            with self.subTest(value=value):
                result = russian_plural(value, forms)
                self.assertEqual(result, expected)
    
    def test_russian_plural_filter_invalid_forms(self):
        """Тест фильтра russian_plural с некорректными формами"""
        # Тестируем некорректные формы слов
        test_cases = [
            (1, "учреждение", "1 учреждение"),  # Только одна форма
            (2, "учреждение,учреждения", "2 учреждение"),  # Только две формы
            (5, "", "5 "),  # Пустая строка
            (1, "a,b,c,d", "1 a"),  # Больше трех форм
        ]
        
        for number, forms, expected in test_cases:
            with self.subTest(number=number, forms=forms):
                result = russian_plural(number, forms)
                self.assertEqual(result, expected)
    
    def test_russian_plural_filter_edge_cases(self):
        """Тест фильтра russian_plural с граничными случаями"""
        # Тестируем граничные случаи
        test_cases = [
            (0, "учреждение,учреждения,учреждений", "0 учреждений"),
            (100, "учреждение,учреждения,учреждений", "100 учреждений"),
            (1000, "учреждение,учреждения,учреждений", "1000 учреждений"),
            (1, "тест,теста,тестов", "1 тест"),
            (2, "тест,теста,тестов", "2 теста"),
            (5, "тест,теста,тестов", "5 тестов"),
        ]
        
        for number, forms, expected in test_cases:
            with self.subTest(number=number, forms=forms):
                result = russian_plural(number, forms)
                self.assertEqual(result, expected)
    
    def test_template_tags_in_context(self):
        """Тест использования тегов в контексте шаблона"""
        # Тестируем использование тегов с переменными контекста
        context = Context({
            'years': 5,
            'doctors': 3,
            'clinics': 1,
            'forms': "учреждение,учреждения,учреждений"
        })
        
        template = Template("""{% load russian_plural %}
{{ years|year_plural }}
{{ doctors|russian_plural:"врач,врача,врачей" }}
{{ clinics|russian_plural:forms }}""")
        
        result = template.render(context).strip()
        expected = "5 лет\n3 врача\n1 учреждение"
        self.assertEqual(result, expected)
    
    def test_template_tags_with_spaces(self):
        """Тест тегов с пробелами в формах"""
        # Тестируем формы с пробелами
        result = russian_plural(2, " учреждение , учреждения , учреждений ")
        self.assertEqual(result, "2 учреждения")
    
    def test_year_plural_filter_zero(self):
        """Тест фильтра year_plural с нулем"""
        result = year_plural(0)
        self.assertEqual(result, "0 лет")
    
    def test_russian_plural_filter_zero(self):
        """Тест фильтра russian_plural с нулем"""
        result = russian_plural(0, "учреждение,учреждения,учреждений")
        self.assertEqual(result, "0 учреждений") 
    
    def test_year_plural_filter_edge_cases(self):
        """Тест фильтра year_plural с граничными случаями"""
        # Тестируем граничные случаи
        test_cases = [
            (0, "0 лет"),
            (100, "100 лет"),
            (1000, "1000 лет"),
            (11, "11 лет"),
            (12, "12 лет"),
            (13, "13 лет"),
            (14, "14 лет"),
            (111, "111 лет"),
            (112, "112 лет"),
            (113, "113 лет"),
            (114, "114 лет"),
        ]
        
        for number, expected in test_cases:
            with self.subTest(number=number):
                result = year_plural(number)
                self.assertEqual(result, expected)
    
    def test_year_plural_filter_error_handling(self):
        """Тест обработки ошибок в year_plural"""
        # Тестируем некорректные входные данные
        test_cases = [
            ("abc", "abc лет"),
            ("", " лет"),
            (None, "None лет"),
            ("12.5", "12.5 лет"),
            ("-1", "-1 лет"),
            ("0.5", "0.5 лет"),
        ]
        
        for value, expected in test_cases:
            with self.subTest(value=value):
                result = year_plural(value)
                self.assertEqual(result, expected)
    
    def test_russian_plural_filter_edge_cases(self):
        """Тест фильтра russian_plural с граничными случаями"""
        # Тестируем граничные случаи
        test_cases = [
            (0, "учреждение,учреждения,учреждений", "0 учреждений"),
            (100, "учреждение,учреждения,учреждений", "100 учреждений"),
            (1000, "учреждение,учреждения,учреждений", "1000 учреждений"),
            (11, "учреждение,учреждения,учреждений", "11 учреждений"),
            (12, "учреждение,учреждения,учреждений", "12 учреждений"),
            (13, "учреждение,учреждения,учреждений", "13 учреждений"),
            (14, "учреждение,учреждения,учреждений", "14 учреждений"),
            (111, "учреждение,учреждения,учреждений", "111 учреждений"),
            (112, "учреждение,учреждения,учреждений", "112 учреждений"),
            (113, "учреждение,учреждения,учреждений", "113 учреждений"),
            (114, "учреждение,учреждения,учреждений", "114 учреждений"),
        ]
        
        for number, forms, expected in test_cases:
            with self.subTest(number=number, forms=forms):
                result = russian_plural(number, forms)
                self.assertEqual(result, expected)
    
    def test_russian_plural_filter_error_handling(self):
        """Тест обработки ошибок в russian_plural"""
        # Тестируем некорректные входные данные
        test_cases = [
            ("abc", "учреждение,учреждения,учреждений", "abc учреждений"),
            ("", "учреждение,учреждения,учреждений", " учреждений"),
            (None, "учреждение,учреждения,учреждений", "None учреждений"),
            ("12.5", "учреждение,учреждения,учреждений", "12.5 учреждений"),
            ("-1", "учреждение,учреждения,учреждений", "-1 учреждений"),
            ("0.5", "учреждение,учреждения,учреждений", "0.5 учреждений"),
        ]
        
        for value, forms, expected in test_cases:
            with self.subTest(value=value):
                result = russian_plural(value, forms)
                self.assertEqual(result, expected)
    
    def test_russian_plural_filter_invalid_forms_handling(self):
        """Тест обработки некорректных форм в russian_plural"""
        # Тестируем некорректные формы слов
        test_cases = [
            (1, "учреждение", "1 учреждение"),  # Только одна форма
            (2, "учреждение,учреждения", "2 учреждение"),  # Только две формы
            (5, "", "5 "),  # Пустая строка
            (1, "a,b,c,d", "1 a"),  # Больше трех форм
            (2, "a,b", "2 a"),  # Две формы
            (5, "a", "5 a"),  # Одна форма
        ]
        
        for number, forms, expected in test_cases:
            with self.subTest(number=number, forms=forms):
                result = russian_plural(number, forms)
                self.assertEqual(result, expected)
    
    def test_russian_plural_filter_with_spaces_and_whitespace(self):
        """Тест фильтра russian_plural с пробелами и whitespace"""
        # Тестируем формы с пробелами
        test_cases = [
            (2, " учреждение , учреждения , учреждений ", "2 учреждения"),
            (5, "  врач  ,  врача  ,  врачей  ", "5 врачей"),
            (1, "  клиника  ,  клиники  ,  клиник  ", "1 клиника"),
        ]
        
        for number, forms, expected in test_cases:
            with self.subTest(number=number, forms=forms):
                result = russian_plural(number, forms)
                self.assertEqual(result, expected)
    
    def test_year_plural_filter_zero_and_negative(self):
        """Тест фильтра year_plural с нулем и отрицательными числами"""
        test_cases = [
            (0, "0 лет"),
            (-1, "-1 лет"),
            (-5, "-5 лет"),
            (-11, "-11 лет"),
            (-21, "-21 лет"),
        ]
        
        for number, expected in test_cases:
            with self.subTest(number=number):
                result = year_plural(number)
                self.assertEqual(result, expected)
    
    def test_russian_plural_filter_zero_and_negative(self):
        """Тест фильтра russian_plural с нулем и отрицательными числами"""
        test_cases = [
            (0, "учреждение,учреждения,учреждений", "0 учреждений"),
            (-1, "учреждение,учреждения,учреждений", "-1 учреждений"),
            (-5, "учреждение,учреждения,учреждений", "-5 учреждений"),
            (-11, "учреждение,учреждения,учреждений", "-11 учреждений"),
            (-21, "учреждение,учреждения,учреждений", "-21 учреждений"),
        ]
        
        for number, forms, expected in test_cases:
            with self.subTest(number=number, forms=forms):
                result = russian_plural(number, forms)
                self.assertEqual(result, expected) 