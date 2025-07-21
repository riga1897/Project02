
from unittest.mock import Mock, patch

import pytest

from src.vacancies.models import Vacancy
from src.vacancies.parsers.hh_parser import HHParser


class TestHHParser:
    """Тесты для парсера HeadHunter"""

    @pytest.fixture
    def parser(self):
        """Фикстура парсера HH"""
        with patch('src.vacancies.parsers.hh_parser.FileCache'):
            return HHParser("test_cache_dir")

    def test_init(self):
        """Тест инициализации парсера"""
        with patch('src.vacancies.parsers.hh_parser.FileCache') as mock_cache:
            parser = HHParser("custom_cache")
            mock_cache.assert_called_once_with("custom_cache")
            assert parser.base_url == "https://api.hh.ru/vacancies"

    def test_init_default_cache_dir(self):
        """Тест инициализации с директорией кеша по умолчанию"""
        with patch('src.vacancies.parsers.hh_parser.FileCache') as mock_cache:
            parser = HHParser()
            mock_cache.assert_called_once_with("data/cache/hh")

    def test_parse_vacancies_with_cache(self, parser):
        """Тест парсинга вакансий с использованием кеша"""
        cached_data = {"data": [{"id": "123", "name": "Test"}]}
        parser.cache.load_response.return_value = cached_data
        
        with patch.object(parser, '_parse_items', return_value=[Mock()]) as mock_parse:
            result = parser.parse_vacancies({"text": "python"})
            
        parser.cache.load_response.assert_called_once_with("hh", {"text": "python"})
        mock_parse.assert_called_once_with([{"id": "123", "name": "Test"}])
        parser.cache.save_response.assert_not_called()
        assert len(result) == 1

    def test_parse_vacancies_without_cache(self, parser):
        """Тест парсинга вакансий без кеша"""
        parser.cache.load_response.return_value = None
        
        with patch.object(parser, '_fetch_from_api', return_value=[{"id": "456"}]) as mock_fetch, \
             patch.object(parser, '_parse_items', return_value=[Mock()]) as mock_parse:
            
            result = parser.parse_vacancies({"text": "python"})
            
        mock_fetch.assert_called_once()
        parser.cache.save_response.assert_called_once_with("hh", {"text": "python"}, [{"id": "456"}])
        mock_parse.assert_called_once_with([{"id": "456"}])
        assert len(result) == 1

    def test_fetch_from_api(self, parser):
        """Тест заглушки для API"""
        result = parser._fetch_from_api()
        assert result == []

    def test_parse_items_success(self, parser):
        """Тест успешного парсинга элементов"""
        raw_data = [
            {
                'id': '123',
                'name': 'Python Developer',
                'alternate_url': 'https://hh.ru/test',
                'snippet': {
                    'requirement': 'Python опыт',
                    'responsibility': 'Разработка'
                }
            }
        ]
        
        mock_vacancy = Mock(spec=Vacancy)
        mock_vacancy.raw_data = raw_data[0]
        mock_vacancy.requirements = 'Python опыт'
        mock_vacancy.responsibilities = 'Разработка'
        
        with patch('src.vacancies.parsers.hh_parser.Vacancy.from_dict', return_value=mock_vacancy), \
             patch.object(parser, 'convert_to_unified_format', return_value=mock_vacancy) as mock_convert:
            
            result = parser._parse_items(raw_data)
            
        assert len(result) == 1
        mock_convert.assert_called_once_with(mock_vacancy)

    def test_parse_items_with_debug_ids(self, parser):
        """Тест парсинга с отладочными ID"""
        raw_data = [
            {
                'id': '122732917',  # Один из отладочных ID
                'name': 'Test Job',
                'snippet': {
                    'requirement': 'Test requirement',
                    'responsibility': 'Test responsibility'
                }
            }
        ]
        
        mock_vacancy = Mock(spec=Vacancy)
        mock_vacancy.raw_data = raw_data[0]
        mock_vacancy.requirements = 'Test requirement'
        mock_vacancy.responsibilities = 'Test responsibility'
        
        with patch('src.vacancies.parsers.hh_parser.Vacancy.from_dict', return_value=mock_vacancy), \
             patch.object(parser, 'convert_to_unified_format', return_value=mock_vacancy), \
             patch('builtins.print') as mock_print:
            
            result = parser._parse_items(raw_data)
            
        # Проверяем, что отладочная информация была выведена
        mock_print.assert_called()
        assert len(result) == 1

    @patch('src.vacancies.parsers.hh_parser.logger')
    def test_parse_items_with_exception(self, mock_logger, parser):
        """Тест обработки исключения при парсинге"""
        raw_data = [{'id': '123', 'name': 'Test'}]
        
        with patch('src.vacancies.parsers.hh_parser.Vacancy.from_dict', side_effect=Exception("Parse error")):
            result = parser._parse_items(raw_data)
            
        assert len(result) == 0
        mock_logger.warning.assert_called_once_with("Ошибка парсинга HH вакансии: Parse error")

    def test_parse_items_with_non_dict_snippet(self, parser):
        """Тест парсинга с snippet не в виде словаря"""
        raw_data = [
            {
                'id': '123',
                'name': 'Test Job',
                'snippet': 'string snippet'  # Не словарь
            }
        ]
        
        mock_vacancy = Mock(spec=Vacancy)
        mock_vacancy.raw_data = raw_data[0]
        
        with patch('src.vacancies.parsers.hh_parser.Vacancy.from_dict', return_value=mock_vacancy), \
             patch.object(parser, 'convert_to_unified_format', return_value=mock_vacancy):
            
            result = parser._parse_items(raw_data)
            
        assert len(result) == 1

    def test_convert_to_unified_format_with_alternate_url(self, parser):
        """Тест конвертации с alternate_url"""
        mock_vacancy = Mock(spec=Vacancy)
        mock_vacancy.vacancy_id = '123'
        mock_vacancy.title = 'Python Developer'
        mock_vacancy.salary = Mock()
        mock_vacancy.salary.to_dict.return_value = {'from': 50000, 'to': 100000}
        mock_vacancy.description = 'Test description'
        mock_vacancy.requirements = 'Python'
        mock_vacancy.responsibilities = 'Development'
        mock_vacancy.employer = {'name': 'Test Company'}
        mock_vacancy.experience = 'От 1 года'
        mock_vacancy.employment = 'Полная занятость'
        mock_vacancy.schedule = 'Полный день'
        mock_vacancy.published_at = Mock()
        mock_vacancy.published_at.isoformat.return_value = '2023-01-01T10:00:00'
        mock_vacancy.skills = [{'name': 'Python'}]
        mock_vacancy.detailed_description = 'Detailed'
        mock_vacancy.benefits = 'Benefits'
        mock_vacancy.source = 'hh.ru'
        mock_vacancy.raw_data = {'alternate_url': 'https://hh.ru/vacancy/123'}
        
        result = parser.convert_to_unified_format(mock_vacancy)
        
        assert isinstance(result, Vacancy)
        assert result.vacancy_id == '123'
        assert result.title == 'Python Developer'
        assert result.url == 'https://hh.ru/vacancy/123'

    def test_convert_to_unified_format_with_url_fallback(self, parser):
        """Тест конвертации с fallback на url"""
        mock_vacancy = Mock(spec=Vacancy)
        mock_vacancy.vacancy_id = '456'
        mock_vacancy.title = 'Java Developer'
        mock_vacancy.salary = None
        mock_vacancy.description = 'Java job'
        mock_vacancy.requirements = 'Java'
        mock_vacancy.responsibilities = 'Java development'
        mock_vacancy.employer = None
        mock_vacancy.experience = None
        mock_vacancy.employment = None
        mock_vacancy.schedule = None
        mock_vacancy.published_at = None
        mock_vacancy.skills = []
        mock_vacancy.detailed_description = None
        mock_vacancy.benefits = None
        mock_vacancy.source = 'hh.ru'
        mock_vacancy.raw_data = {'url': 'https://api.hh.ru/vacancies/456'}
        
        result = parser.convert_to_unified_format(mock_vacancy)
        
        assert result.vacancy_id == '456'
        assert result.url == 'https://api.hh.ru/vacancies/456'
        assert result.salary.amount_from == 0 and result.salary.amount_to == 0
        assert result.published_at is None

    def test_convert_to_unified_format_no_urls(self, parser):
        """Тест конвертации без URL"""
        mock_vacancy = Mock(spec=Vacancy)
        mock_vacancy.vacancy_id = '789'
        mock_vacancy.title = 'Developer'
        mock_vacancy.salary = None
        mock_vacancy.description = 'Job'
        mock_vacancy.requirements = None
        mock_vacancy.responsibilities = None
        mock_vacancy.employer = None
        mock_vacancy.experience = None
        mock_vacancy.employment = None
        mock_vacancy.schedule = None
        mock_vacancy.published_at = None
        mock_vacancy.skills = None
        mock_vacancy.detailed_description = None
        mock_vacancy.benefits = None
        mock_vacancy.source = 'hh.ru'
        mock_vacancy.raw_data = {}
        
        result = parser.convert_to_unified_format(mock_vacancy)
        
        assert result.url == ''
        assert result.skills == []

    def test_convert_to_unified_format_no_raw_data(self, parser):
        """Тест конвертации без raw_data"""
        mock_vacancy = Mock(spec=Vacancy)
        mock_vacancy.vacancy_id = '999'
        mock_vacancy.title = 'Developer'
        mock_vacancy.salary = None
        mock_vacancy.description = 'Job'
        mock_vacancy.requirements = None
        mock_vacancy.responsibilities = None
        mock_vacancy.employer = None
        mock_vacancy.experience = None
        mock_vacancy.employment = None
        mock_vacancy.schedule = None
        mock_vacancy.published_at = None
        mock_vacancy.skills = None
        mock_vacancy.detailed_description = None
        mock_vacancy.benefits = None
        mock_vacancy.source = 'hh.ru'
        mock_vacancy.raw_data = None
        
        result = parser.convert_to_unified_format(mock_vacancy)
        
        assert result.url == ''
