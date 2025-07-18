
"""
Тесты для модуля sj_parser
"""

import pytest
from src.vacancies.parsers.sj_parser import SuperJobParser
from src.vacancies.sj_models import SuperJobVacancy


class TestSuperJobParser:
    """Тесты для класса SuperJobParser"""
    
    @pytest.fixture
    def parser(self):
        """Фикстура для создания экземпляра парсера"""
        return SuperJobParser()
    
    @pytest.fixture
    def sample_sj_data(self):
        """Образец данных SuperJob"""
        return {
            'id': 123,
            'profession': 'Python Developer',
            'link': 'https://superjob.ru/vacancy/123',
            'payment_from': 100000,
            'payment_to': 150000,
            'currency': 'rub',
            'candidat': 'Разработка на Python',
            'work': 'Удаленная работа',
            'experience': {'title': 'От 3 до 6 лет'},
            'firm_name': 'Tech Company',
            'town': {'title': 'Москва'}
        }
    
    @pytest.fixture
    def sample_sj_vacancy(self, sample_sj_data):
        """Образец SuperJob вакансии"""
        return SuperJobVacancy(
            id=sample_sj_data['id'],
            profession=sample_sj_data['profession'],
            link=sample_sj_data['link'],
            payment_from=sample_sj_data['payment_from'],
            payment_to=sample_sj_data['payment_to'],
            currency=sample_sj_data['currency'],
            candidat=sample_sj_data['candidat'],
            work=sample_sj_data['work'],
            experience=sample_sj_data['experience'],
            firm_name=sample_sj_data['firm_name'],
            town=sample_sj_data['town']
        )
    
    def test_parse_vacancies_single(self, parser, sample_sj_data):
        """Тест парсинга одной вакансии"""
        data = [sample_sj_data]
        
        result = parser.parse_vacancies(data)
        
        assert len(result) == 1
        assert isinstance(result[0], SuperJobVacancy)
        assert result[0].id == 123
        assert result[0].profession == 'Python Developer'
    
    def test_parse_vacancies_multiple(self, parser, sample_sj_data):
        """Тест парсинга нескольких вакансий"""
        data = [sample_sj_data, {**sample_sj_data, 'id': 456, 'profession': 'Java Developer'}]
        
        result = parser.parse_vacancies(data)
        
        assert len(result) == 2
        assert result[0].id == 123
        assert result[1].id == 456
        assert result[1].profession == 'Java Developer'
    
    def test_parse_vacancies_empty(self, parser):
        """Тест парсинга пустого списка"""
        result = parser.parse_vacancies([])
        
        assert len(result) == 0
    
    def test_parse_vacancies_minimal_data(self, parser):
        """Тест парсинга с минимальными данными"""
        data = [{
            'id': 789,
            'profession': 'Test Job',
            'link': 'https://test.com'
        }]
        
        result = parser.parse_vacancies(data)
        
        assert len(result) == 1
        assert result[0].id == 789
        assert result[0].profession == 'Test Job'
        assert result[0].payment_from is None
        assert result[0].payment_to is None
    
    def test_convert_to_unified_format_with_salary(self, parser, sample_sj_vacancy):
        """Тест конвертации в унифицированный формат с зарплатой"""
        result = parser.convert_to_unified_format(sample_sj_vacancy)
        
        assert result['id'] == '123'
        assert result['name'] == 'Python Developer'
        assert result['alternate_url'] == 'https://superjob.ru/vacancy/123'
        assert result['salary']['from'] == 100000
        assert result['salary']['to'] == 150000
        assert result['salary']['currency'] == 'RUR'
        assert result['snippet']['responsibility'] == 'Разработка на Python'
        assert result['employer']['name'] == 'Tech Company'
        assert result['area']['name'] == 'Москва'
        assert result['experience']['name'] == 'От 3 до 6 лет'
    
    def test_convert_to_unified_format_without_salary(self, parser, sample_sj_vacancy):
        """Тест конвертации в унифицированный формат без зарплаты"""
        sample_sj_vacancy.payment_from = None
        sample_sj_vacancy.payment_to = None
        
        result = parser.convert_to_unified_format(sample_sj_vacancy)
        
        assert result['salary'] is None
    
    def test_convert_to_unified_format_only_from_salary(self, parser, sample_sj_vacancy):
        """Тест конвертации с только нижней границей зарплаты"""
        sample_sj_vacancy.payment_to = None
        
        result = parser.convert_to_unified_format(sample_sj_vacancy)
        
        assert result['salary']['from'] == 100000
        assert result['salary']['to'] is None
    
    def test_convert_to_unified_format_only_to_salary(self, parser, sample_sj_vacancy):
        """Тест конвертации с только верхней границей зарплаты"""
        sample_sj_vacancy.payment_from = None
        
        result = parser.convert_to_unified_format(sample_sj_vacancy)
        
        assert result['salary']['from'] is None
        assert result['salary']['to'] == 150000
    
    def test_convert_to_unified_format_currency_conversion(self, parser, sample_sj_vacancy):
        """Тест конвертации валюты"""
        sample_sj_vacancy.currency = 'USD'
        
        result = parser.convert_to_unified_format(sample_sj_vacancy)
        
        assert result['salary']['currency'] == 'USD'
    
    def test_convert_to_unified_format_empty_strings(self, parser, sample_sj_vacancy):
        """Тест конвертации с пустыми строками"""
        sample_sj_vacancy.candidat = ''
        sample_sj_vacancy.work = ''
        sample_sj_vacancy.firm_name = ''
        
        result = parser.convert_to_unified_format(sample_sj_vacancy)
        
        assert result['snippet']['responsibility'] == ''
        assert result['employer']['name'] == ''
    
    def test_convert_to_unified_format_none_values(self, parser, sample_sj_vacancy):
        """Тест конвертации с None значениями"""
        sample_sj_vacancy.experience = None
        sample_sj_vacancy.town = None
        sample_sj_vacancy.firm_name = None
        
        result = parser.convert_to_unified_format(sample_sj_vacancy)
        
        assert result['experience']['name'] == 'Не указан'
        assert result['area']['name'] == 'Не указан'
        assert result['employer']['name'] == 'Не указано'
    
    def test_convert_to_unified_format_dict_values(self, parser, sample_sj_vacancy):
        """Тест конвертации со словарными значениями"""
        sample_sj_vacancy.experience = {'title': 'От 1 до 3 лет'}
        sample_sj_vacancy.town = {'title': 'Санкт-Петербург'}
        
        result = parser.convert_to_unified_format(sample_sj_vacancy)
        
        assert result['experience']['name'] == 'От 1 до 3 лет'
        assert result['area']['name'] == 'Санкт-Петербург'
    
    def test_convert_to_unified_format_string_values(self, parser, sample_sj_vacancy):
        """Тест конвертации со строковыми значениями"""
        sample_sj_vacancy.experience = 'Опыт работы от 5 лет'
        sample_sj_vacancy.town = 'Екатеринбург'
        
        result = parser.convert_to_unified_format(sample_sj_vacancy)
        
        assert result['experience']['name'] == 'Опыт работы от 5 лет'
        assert result['area']['name'] == 'Екатеринбург'
    
    def test_convert_to_unified_format_missing_fields(self, parser):
        """Тест конвертации с отсутствующими полями"""
        minimal_vacancy = SuperJobVacancy(
            id=999,
            profession='Minimal Job',
            link='https://minimal.com'
        )
        
        result = parser.convert_to_unified_format(minimal_vacancy)
        
        assert result['id'] == '999'
        assert result['name'] == 'Minimal Job'
        assert result['alternate_url'] == 'https://minimal.com'
        assert result['salary'] is None
        assert result['snippet']['responsibility'] == 'Не указано'
        assert result['employer']['name'] == 'Не указано'
        assert result['area']['name'] == 'Не указан'
        assert result['experience']['name'] == 'Не указан'
