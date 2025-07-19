
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

from src.api_modules.hh_api import HeadHunterAPI
from src.api_modules.base_api import BaseAPI
from src.config.api_config import APIConfig


class TestHeadHunterAPIImplementation:
    """Тесты для HeadHunterAPI как конкретной реализации BaseAPI"""

    @pytest.fixture
    def mock_config(self):
        """Mock конфигурация API"""
        config = Mock(spec=APIConfig)
        config.hh_config = Mock()
        config.hh_config.get_params.return_value = {"per_page": 100}
        config.get_pagination_params.return_value = {"max_pages": 20}
        return config

    @pytest.fixture
    @patch('src.api_modules.hh_api.APIConnector')
    @patch('src.api_modules.hh_api.Paginator')
    def hh_api(self, mock_paginator, mock_connector, mock_config):
        """Создает экземпляр HeadHunterAPI с моками"""
        return HeadHunterAPI(mock_config)

    def test_inherits_from_base_api(self, hh_api):
        """Проверяем, что HeadHunterAPI наследуется от BaseAPI"""
        assert isinstance(hh_api, BaseAPI)
        assert issubclass(HeadHunterAPI, BaseAPI)

    def test_implements_all_abstract_methods(self):
        """Проверяем, что HeadHunterAPI реализует все абстрактные методы"""
        # Получаем абстрактные методы из родительского класса
        abstract_methods = BaseAPI.__abstractmethods__
        
        # Проверяем, что все методы реализованы в HeadHunterAPI
        for method_name in abstract_methods:
            assert hasattr(HeadHunterAPI, method_name)
            method = getattr(HeadHunterAPI, method_name)
            assert callable(method)
            # Проверяем, что метод не помечен как абстрактный
            assert not getattr(method, '__isabstractmethod__', False)

    def test_get_vacancies_method_signature(self, hh_api):
        """Проверяем правильность сигнатуры метода get_vacancies"""
        with patch.object(hh_api, '_CachedAPI__connect_to_api') as mock_connect:
            mock_connect.return_value = {'items': [], 'found': 0, 'pages': 1}
            
            result = hh_api.get_vacancies("Python developer")
            assert isinstance(result, list)

    def test_clear_cache_method_signature(self, hh_api):
        """Проверяем правильность сигнатуры метода clear_cache"""
        with patch('src.api_modules.cached_api.CachedAPI.clear_cache') as mock_clear:
            hh_api.clear_cache("hh")
            mock_clear.assert_called_once_with("hh")

    def test_hh_specific_constants(self):
        """Тестируем HH-специфичные константы"""
        assert HeadHunterAPI.BASE_URL == "https://api.hh.ru/vacancies"
        assert HeadHunterAPI.DEFAULT_CACHE_DIR == "data/cache/hh"
        assert HeadHunterAPI.REQUIRED_VACANCY_FIELDS == {'name', 'alternate_url', 'salary'}

    @patch('src.api_modules.hh_api.APIConnector')
    @patch('src.api_modules.hh_api.Paginator')
    def test_initialization_with_default_config(self, mock_paginator, mock_connector):
        """Тестируем инициализацию с конфигурацией по умолчанию"""
        api = HeadHunterAPI()
        
        # Проверяем, что создалась конфигурация по умолчанию
        assert api._config is not None
        assert isinstance(api._config, APIConfig)
        
        # Проверяем, что создались необходимые компоненты
        mock_connector.assert_called_once_with(api._config)
        mock_paginator.assert_called_once()

    @patch('src.api_modules.hh_api.APIConnector')
    @patch('src.api_modules.hh_api.Paginator')
    def test_initialization_with_custom_config(self, mock_paginator, mock_connector, mock_config):
        """Тестируем инициализацию с пользовательской конфигурацией"""
        api = HeadHunterAPI(mock_config)
        
        # Проверяем, что используется переданная конфигурация
        assert api._config is mock_config
        
        # Проверяем, что создались необходимые компоненты с правильной конфигурацией
        mock_connector.assert_called_once_with(mock_config)

    def test_get_empty_response_structure(self, hh_api):
        """Тестируем структуру пустого ответа"""
        empty_response = hh_api._get_empty_response()
        assert isinstance(empty_response, dict)
        assert 'items' in empty_response
        assert empty_response['items'] == []

    def test_validate_vacancy_hh_format(self, hh_api):
        """Тестируем валидацию вакансии в формате HH"""
        # Валидная вакансия HH
        valid_vacancy = {
            'name': 'Python Developer',
            'alternate_url': 'https://hh.ru/vacancy/12345',
            'salary': {'from': 100000, 'to': 150000, 'currency': 'RUR'}
        }
        assert hh_api._validate_vacancy(valid_vacancy) is True

        # Невалидная вакансия (отсутствует обязательное поле)
        invalid_vacancy = {
            'name': 'Python Developer',
            'salary': {'from': 100000, 'to': 150000, 'currency': 'RUR'}
            # Отсутствует 'alternate_url'
        }
        assert hh_api._validate_vacancy(invalid_vacancy) is False

        # Не словарь
        assert hh_api._validate_vacancy("not a dict") is False

    def test_get_vacancies_page_success(self, hh_api):
        """Тестируем успешное получение страницы вакансий"""
        mock_response = {
            'items': [
                {
                    'name': 'Python Developer',
                    'alternate_url': 'https://hh.ru/vacancy/1',
                    'salary': {'from': 100000, 'to': 150000}
                },
                {
                    'name': 'Java Developer',
                    'alternate_url': 'https://hh.ru/vacancy/2',
                    'salary': {'from': 120000, 'to': 180000}
                }
            ]
        }
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api') as mock_connect:
            mock_connect.return_value = mock_response
            
            result = hh_api.get_vacancies_page("Python", 0)
            
            assert isinstance(result, list)
            assert len(result) == 2
            mock_connect.assert_called_once()

    def test_get_vacancies_page_with_invalid_items(self, hh_api):
        """Тестируем фильтрацию невалидных элементов на странице"""
        mock_response = {
            'items': [
                {
                    'name': 'Valid Job',
                    'alternate_url': 'https://hh.ru/vacancy/1',
                    'salary': None
                },
                {
                    'name': 'Invalid Job',
                    # Отсутствует 'alternate_url'
                    'salary': None
                },
                "not a dict"
            ]
        }
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api') as mock_connect:
            mock_connect.return_value = mock_response
            
            result = hh_api.get_vacancies_page("Python", 0)
            
            # Должна остаться только одна валидная вакансия
            assert len(result) == 1
            assert result[0]['name'] == 'Valid Job'

    def test_get_vacancies_full_cycle(self, hh_api):
        """Тестируем полный цикл получения вакансий с пагинацией"""
        # Mock для начального запроса метаданных
        initial_response = {
            'found': 150,
            'pages': 3,
            'items': []
        }
        
        # Mock для страниц с данными
        page_responses = [
            {'items': [{'name': f'Job {i}', 'alternate_url': f'url{i}', 'salary': None} for i in range(5)]},
            {'items': [{'name': f'Job {i}', 'alternate_url': f'url{i}', 'salary': None} for i in range(5, 10)]},
            {'items': [{'name': f'Job {i}', 'alternate_url': f'url{i}', 'salary': None} for i in range(10, 15)]}
        ]
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api') as mock_connect:
            # Настраиваем последовательные возвраты
            mock_connect.side_effect = [initial_response] + page_responses
            
            # Мокаем пагинатор
            with patch.object(hh_api, '_paginator') as mock_paginator:
                mock_paginator.paginate.return_value = [item for page in page_responses for item in page['items']]
                
                result = hh_api.get_vacancies("Python")
                
                assert isinstance(result, list)
                assert len(result) == 15

    def test_get_vacancies_no_results(self, hh_api):
        """Тестируем поведение при отсутствии результатов"""
        mock_response = {'found': 0, 'pages': 0, 'items': []}
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api') as mock_connect:
            mock_connect.return_value = mock_response
            
            result = hh_api.get_vacancies("NonexistentTechnology")
            
            assert isinstance(result, list)
            assert len(result) == 0

    def test_get_vacancies_keyboard_interrupt(self, hh_api):
        """Тестируем обработку прерывания пользователем"""
        with patch.object(hh_api, '_CachedAPI__connect_to_api') as mock_connect:
            mock_connect.side_effect = KeyboardInterrupt("User interrupted")
            
            result = hh_api.get_vacancies("Python")
            
            assert isinstance(result, list)
            assert len(result) == 0

    def test_get_vacancies_api_error(self, hh_api):
        """Тестируем обработку ошибок API"""
        with patch.object(hh_api, '_CachedAPI__connect_to_api') as mock_connect:
            mock_connect.side_effect = Exception("API Error")
            
            result = hh_api.get_vacancies("Python")
            
            assert isinstance(result, list)
            assert len(result) == 0

    def test_deduplicate_vacancies_hh_format(self, hh_api):
        """Тестируем дедупликацию вакансий в формате HH"""
        vacancies_with_duplicates = [
            {
                'name': 'Python Developer',
                'employer': {'name': 'Company A'},
                'salary': {'from': 100000, 'to': 150000}
            },
            {
                'name': 'Python Developer',
                'employer': {'name': 'Company A'},
                'salary': {'from': 100000, 'to': 150000}
            },  # Дубликат
            {
                'name': 'Java Developer',
                'employer': {'name': 'Company B'},
                'salary': None
            }
        ]
        
        result = hh_api._deduplicate_vacancies(vacancies_with_duplicates)
        
        assert len(result) == 2  # Должен остаться 1 Python и 1 Java
        titles = [v.get('name') for v in result]
        assert 'Python Developer' in titles
        assert 'Java Developer' in titles

    def test_get_vacancies_with_deduplication(self, hh_api):
        """Тестируем получение вакансий с дедупликацией"""
        mock_vacancies = [
            {'name': 'Job 1', 'employer': {'name': 'Company'}, 'salary': None},
            {'name': 'Job 2', 'employer': {'name': 'Company'}, 'salary': None}
        ]
        
        with patch.object(hh_api, 'get_vacancies') as mock_get:
            mock_get.return_value = mock_vacancies
            
            with patch.object(hh_api, '_deduplicate_vacancies') as mock_dedup:
                mock_dedup.return_value = mock_vacancies  # Без дубликатов
                
                result = hh_api.get_vacancies_with_deduplication("Python")
                
                mock_get.assert_called_once_with("Python")
                mock_dedup.assert_called_once_with(mock_vacancies)
                assert result == mock_vacancies

    def test_polymorphism_through_base_api_interface(self, hh_api):
        """Тестируем полиморфизм через интерфейс BaseAPI"""
        # Используем HeadHunterAPI через интерфейс BaseAPI
        base_api: BaseAPI = hh_api
        
        # Методы должны работать через базовый интерфейс
        with patch.object(hh_api, '_CachedAPI__connect_to_api') as mock_connect:
            mock_connect.return_value = {'items': [], 'found': 0, 'pages': 1}
            
            result = base_api.get_vacancies("Python")
            assert isinstance(result, list)

        # clear_cache должен работать через базовый интерфейс
        with patch('src.api_modules.cached_api.CachedAPI.clear_cache') as mock_clear:
            base_api.clear_cache("hh")
            mock_clear.assert_called_once_with("hh")

    def test_hh_specific_url_and_params(self, hh_api, mock_config):
        """Тестируем HH-специфичные URL и параметры"""
        mock_config.hh_config.get_params.return_value = {
            "text": "Python",
            "page": 0,
            "per_page": 50
        }
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api') as mock_connect:
            mock_connect.return_value = {'items': []}
            
            hh_api.get_vacancies_page("Python", 0)
            
            # Проверяем, что вызывается с правильным URL
            mock_connect.assert_called_once()
            args, kwargs = mock_connect.call_args
            assert args[0] == "https://api.hh.ru/vacancies"
            assert args[2] == "hh"  # API prefix

    @patch('src.api_modules.hh_api.logger')
    def test_logging_on_errors(self, mock_logger, hh_api):
        """Тестируем логирование при ошибках"""
        with patch.object(hh_api, '_CachedAPI__connect_to_api') as mock_connect:
            mock_connect.side_effect = Exception("Test error")
            
            result = hh_api.get_vacancies_page("Python", 0)
            
            # Должно быть пустой список при ошибке
            assert result == []
            
            # Должна быть вызвана функция логирования ошибки
            mock_logger.error.assert_called()

    def test_inheritance_chain_with_cached_api(self, hh_api):
        """Тестируем цепочку наследования через CachedAPI"""
        from src.api_modules.cached_api import CachedAPI
        
        # Проверяем полную цепочку наследования
        assert isinstance(hh_api, HeadHunterAPI)
        assert isinstance(hh_api, CachedAPI)
        assert isinstance(hh_api, BaseAPI)
        
        # Проверяем порядок в MRO (Method Resolution Order)
        mro = HeadHunterAPI.__mro__
        assert BaseAPI in mro
        assert CachedAPI in mro

    def test_configuration_integration(self, hh_api, mock_config):
        """Тестируем интеграцию с конфигурацией"""
        # Проверяем, что конфигурация сохраняется
        assert hh_api._config is mock_config
        
        # Проверяем использование конфигурации в запросах
        mock_config.hh_config.get_params.return_value = {"custom": "param"}
        mock_config.get_pagination_params.return_value = {"max_pages": 5}
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api') as mock_connect:
            mock_connect.return_value = {'items': [], 'found': 0, 'pages': 1}
            
            hh_api.get_vacancies_page("Python", 0, custom_param="value")
            
            # Проверяем, что конфигурация использовалась
            mock_config.hh_config.get_params.assert_called()
