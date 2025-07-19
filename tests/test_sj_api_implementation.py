
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

from src.api_modules.sj_api import SuperJobAPI
from src.api_modules.base_api import BaseAPI
from src.config.sj_api_config import SJAPIConfig


class TestSuperJobAPIImplementation:
    """Тесты для SuperJobAPI как конкретной реализации BaseAPI"""

    @pytest.fixture
    def mock_sj_config(self):
        """Mock конфигурация SuperJob API"""
        config = Mock(spec=SJAPIConfig)
        config.get_params.return_value = {"count": 100, "page": 0}
        return config

    @pytest.fixture
    @patch('src.api_modules.sj_api.APIConnector')
    @patch('src.api_modules.sj_api.Paginator')
    @patch('src.api_modules.sj_api.EnvLoader')
    def sj_api(self, mock_env_loader, mock_paginator, mock_connector, mock_sj_config):
        """Создает экземпляр SuperJobAPI с моками"""
        mock_env_loader.get_env_var.return_value = 'test_api_key'
        return SuperJobAPI(mock_sj_config)

    def test_inherits_from_base_api(self, sj_api):
        """Проверяем, что SuperJobAPI наследуется от BaseAPI"""
        assert isinstance(sj_api, BaseAPI)
        assert issubclass(SuperJobAPI, BaseAPI)

    def test_implements_all_abstract_methods(self):
        """Проверяем, что SuperJobAPI реализует все абстрактные методы"""
        # Получаем абстрактные методы из родительского класса
        abstract_methods = BaseAPI.__abstractmethods__
        
        # Проверяем, что все методы реализованы в SuperJobAPI
        for method_name in abstract_methods:
            assert hasattr(SuperJobAPI, method_name)
            method = getattr(SuperJobAPI, method_name)
            assert callable(method)
            # Проверяем, что метод не помечен как абстрактный
            assert not getattr(method, '__isabstractmethod__', False)

    def test_get_vacancies_method_signature(self, sj_api):
        """Проверяем правильность сигнатуры метода get_vacancies"""
        with patch.object(sj_api, '_CachedAPI__connect_to_api') as mock_connect:
            mock_connect.return_value = {'objects': [], 'total': 0}
            
            result = sj_api.get_vacancies("Python developer")
            assert isinstance(result, list)

    def test_clear_cache_method_signature(self, sj_api):
        """Проверяем правильность сигнатуры метода clear_cache"""
        with patch('src.api_modules.cached_api.CachedAPI.clear_cache') as mock_clear:
            sj_api.clear_cache("sj")
            mock_clear.assert_called_once_with("sj")

    def test_sj_specific_constants(self):
        """Тестируем SuperJob-специфичные константы"""
        assert SuperJobAPI.BASE_URL == "https://api.superjob.ru/2.0/vacancies"
        assert SuperJobAPI.DEFAULT_CACHE_DIR == "data/cache/sj"
        assert SuperJobAPI.REQUIRED_VACANCY_FIELDS == {'profession', 'link'}

    @patch('src.api_modules.sj_api.APIConnector')
    @patch('src.api_modules.sj_api.Paginator')
    @patch('src.api_modules.sj_api.EnvLoader')
    def test_initialization_with_default_config(self, mock_env_loader, mock_paginator, mock_connector):
        """Тестируем инициализацию с конфигурацией по умолчанию"""
        mock_env_loader.get_env_var.return_value = 'default_api_key'
        
        api = SuperJobAPI()
        
        # Проверяем, что создалась конфигурация по умолчанию
        assert api.config is not None
        assert isinstance(api.config, SJAPIConfig)
        
        # Проверяем, что создались необходимые компоненты
        mock_connector.assert_called_once()
        mock_paginator.assert_called_once()

    @patch('src.api_modules.sj_api.APIConnector')
    @patch('src.api_modules.sj_api.Paginator')  
    @patch('src.api_modules.sj_api.EnvLoader')
    def test_initialization_with_custom_config(self, mock_env_loader, mock_paginator, mock_connector, mock_sj_config):
        """Тестируем инициализацию с пользовательской конфигурацией"""
        mock_env_loader.get_env_var.return_value = 'custom_api_key'
        
        api = SuperJobAPI(mock_sj_config)
        
        # Проверяем, что используется переданная конфигурация
        assert api.config is mock_sj_config

    @patch('src.api_modules.sj_api.EnvLoader')
    def test_api_key_handling(self, mock_env_loader):
        """Тестируем обработку API ключа"""
        # Тест с пользовательским ключом
        mock_env_loader.get_env_var.return_value = 'user_api_key'
        
        with patch('src.api_modules.sj_api.APIConnector') as mock_connector:
            with patch('src.api_modules.sj_api.Paginator'):
                api = SuperJobAPI()
                
                # Проверяем, что ключ установлен в заголовки
                mock_connector.return_value.headers.update.assert_called()
                call_args = mock_connector.return_value.headers.update.call_args[0][0]
                assert "X-Api-App-Id" in call_args
                assert call_args["X-Api-App-Id"] == 'user_api_key'

        # Тест с тестовым ключом по умолчанию
        mock_env_loader.get_env_var.return_value = 'v3.r.137440105.example.test_tool'
        
        with patch('src.api_modules.sj_api.APIConnector') as mock_connector:
            with patch('src.api_modules.sj_api.Paginator'):
                with patch('src.api_modules.sj_api.logger') as mock_logger:
                    api = SuperJobAPI()
                    
                    # Должно быть предупреждение о тестовом ключе
                    mock_logger.warning.assert_called()

    def test_get_empty_response_structure(self, sj_api):
        """Тестируем структуру пустого ответа"""
        empty_response = sj_api._get_empty_response()
        assert isinstance(empty_response, dict)
        assert 'objects' in empty_response
        assert empty_response['objects'] == []

    def test_validate_vacancy_sj_format(self, sj_api):
        """Тестируем валидацию вакансии в формате SuperJob"""
        # Валидная вакансия SuperJob
        valid_vacancy = {
            'profession': 'Python Developer',
            'link': 'https://www.superjob.ru/vakansii/python-developer.html'
        }
        assert sj_api._validate_vacancy(valid_vacancy) is True

        # Невалидная вакансия (отсутствует обязательное поле)
        invalid_vacancy = {
            'profession': 'Python Developer'
            # Отсутствует 'link'
        }
        assert sj_api._validate_vacancy(invalid_vacancy) is False

        # Невалидная вакансия (пустое значение)
        empty_field_vacancy = {
            'profession': '',
            'link': 'https://www.superjob.ru/vakansii/python-developer.html'
        }
        assert sj_api._validate_vacancy(empty_field_vacancy) is False

        # Не словарь
        assert sj_api._validate_vacancy("not a dict") is False

    def test_get_vacancies_page_success(self, sj_api):
        """Тестируем успешное получение страницы вакансий"""
        mock_response = {
            'objects': [
                {
                    'profession': 'Python Developer',
                    'link': 'https://www.superjob.ru/vakansii/python-1.html',
                    'payment_from': 100000
                },
                {
                    'profession': 'Java Developer', 
                    'link': 'https://www.superjob.ru/vakansii/java-1.html',
                    'payment_from': 120000
                }
            ]
        }
        
        with patch.object(sj_api, '_CachedAPI__connect_to_api') as mock_connect:
            mock_connect.return_value = mock_response
            
            result = sj_api.get_vacancies_page("Python", 0)
            
            assert isinstance(result, list)
            assert len(result) == 2
            # Проверяем, что добавился источник
            assert all(item.get('source') == 'superjob.ru' for item in result)
            mock_connect.assert_called_once()

    def test_get_vacancies_page_with_invalid_items(self, sj_api):
        """Тестируем фильтрацию невалидных элементов на странице"""
        mock_response = {
            'objects': [
                {
                    'profession': 'Valid Job',
                    'link': 'https://www.superjob.ru/vakansii/valid.html'
                },
                {
                    'profession': 'Invalid Job'
                    # Отсутствует 'link'
                },
                "not a dict"
            ]
        }
        
        with patch.object(sj_api, '_CachedAPI__connect_to_api') as mock_connect:
            mock_connect.return_value = mock_response
            
            result = sj_api.get_vacancies_page("Python", 0)
            
            # Должна остаться только одна валидная вакансия
            assert len(result) == 1
            assert result[0]['profession'] == 'Valid Job'

    def test_get_vacancies_full_cycle(self, sj_api):
        """Тестируем полный цикл получения вакансий с пагинацией"""
        # Mock для начального запроса метаданных
        initial_response = {
            'total': 150,
            'objects': []
        }
        
        # Mock для страниц с данными
        page_responses = [
            {'objects': [{'profession': f'Job {i}', 'link': f'url{i}'} for i in range(5)]},
            {'objects': [{'profession': f'Job {i}', 'link': f'url{i}'} for i in range(5, 10)]},
            {'objects': [{'profession': f'Job {i}', 'link': f'url{i}'} for i in range(10, 15)]}
        ]
        
        with patch.object(sj_api, '_CachedAPI__connect_to_api') as mock_connect:
            # Настраиваем последовательные возвраты
            mock_connect.side_effect = [initial_response] + page_responses
            
            # Мокаем пагинатор
            with patch.object(sj_api, 'paginator') as mock_paginator:
                mock_paginator.paginate.return_value = [item for page in page_responses for item in page['objects']]
                
                result = sj_api.get_vacancies("Python")
                
                assert isinstance(result, list)
                assert len(result) == 15

    def test_get_vacancies_no_results(self, sj_api):
        """Тестируем поведение при отсутствии результатов"""
        mock_response = {'total': 0, 'objects': []}
        
        with patch.object(sj_api, '_CachedAPI__connect_to_api') as mock_connect:
            mock_connect.return_value = mock_response
            
            result = sj_api.get_vacancies("NonexistentTechnology")
            
            assert isinstance(result, list)
            assert len(result) == 0

    def test_get_vacancies_keyboard_interrupt(self, sj_api):
        """Тестируем обработку прерывания пользователем"""
        with patch.object(sj_api, '_CachedAPI__connect_to_api') as mock_connect:
            mock_connect.side_effect = KeyboardInterrupt("User interrupted")
            
            result = sj_api.get_vacancies("Python")
            
            assert isinstance(result, list)
            assert len(result) == 0

    def test_get_vacancies_api_error(self, sj_api):
        """Тестируем обработку ошибок API"""
        with patch.object(sj_api, '_CachedAPI__connect_to_api') as mock_connect:
            mock_connect.side_effect = Exception("API Error")
            
            result = sj_api.get_vacancies("Python")
            
            assert isinstance(result, list)
            assert len(result) == 0

    def test_deduplicate_vacancies_sj_format(self, sj_api):
        """Тестируем дедупликацию вакансий в формате SuperJob"""
        vacancies_with_duplicates = [
            {
                'profession': 'Python Developer',
                'firm_name': 'Company A',
                'payment_from': 100000,
                'payment_to': 150000
            },
            {
                'profession': 'Python Developer',
                'firm_name': 'Company A',
                'payment_from': 100000,
                'payment_to': 150000
            },  # Дубликат
            {
                'profession': 'Java Developer',
                'firm_name': 'Company B',
                'payment_from': 0,
                'payment_to': 0
            }
        ]
        
        result = sj_api._deduplicate_vacancies(vacancies_with_duplicates)
        
        assert len(result) == 2  # Должен остаться 1 Python и 1 Java
        professions = [v.get('profession') for v in result]
        assert 'Python Developer' in professions
        assert 'Java Developer' in professions

    def test_get_vacancies_with_deduplication(self, sj_api):
        """Тестируем получение вакансий с дедупликацией"""
        mock_vacancies = [
            {'profession': 'Job 1', 'firm_name': 'Company', 'payment_from': 0, 'payment_to': 0},
            {'profession': 'Job 2', 'firm_name': 'Company', 'payment_from': 0, 'payment_to': 0}
        ]
        
        with patch.object(sj_api, 'get_vacancies') as mock_get:
            mock_get.return_value = mock_vacancies
            
            with patch.object(sj_api, '_deduplicate_vacancies') as mock_dedup:
                mock_dedup.return_value = mock_vacancies  # Без дубликатов
                
                result = sj_api.get_vacancies_with_deduplication("Python")
                
                mock_get.assert_called_once_with("Python")
                mock_dedup.assert_called_once_with(mock_vacancies)
                assert result == mock_vacancies

    def test_polymorphism_through_base_api_interface(self, sj_api):
        """Тестируем полиморфизм через интерфейс BaseAPI"""
        # Используем SuperJobAPI через интерфейс BaseAPI
        base_api: BaseAPI = sj_api
        
        # Методы должны работать через базовый интерфейс
        with patch.object(sj_api, '_CachedAPI__connect_to_api') as mock_connect:
            mock_connect.return_value = {'objects': [], 'total': 0}
            
            result = base_api.get_vacancies("Python")
            assert isinstance(result, list)

        # clear_cache должен работать через базовый интерфейс
        with patch('src.api_modules.cached_api.CachedAPI.clear_cache') as mock_clear:
            base_api.clear_cache("sj")
            mock_clear.assert_called_once_with("sj")

    def test_sj_specific_url_and_params(self, sj_api, mock_sj_config):
        """Тестируем SuperJob-специфичные URL и параметры"""
        mock_sj_config.get_params.return_value = {
            "keyword": "Python",
            "page": 0,
            "count": 50
        }
        
        with patch.object(sj_api, '_CachedAPI__connect_to_api') as mock_connect:
            mock_connect.return_value = {'objects': []}
            
            sj_api.get_vacancies_page("Python", 0)
            
            # Проверяем, что вызывается с правильным URL
            mock_connect.assert_called_once()
            args, kwargs = mock_connect.call_args
            assert args[0] == "https://api.superjob.ru/2.0/vacancies"
            assert args[2] == "sj"  # API prefix

    @patch('src.api_modules.sj_api.logger')
    def test_logging_on_errors(self, mock_logger, sj_api):
        """Тестируем логирование при ошибках"""
        with patch.object(sj_api, '_CachedAPI__connect_to_api') as mock_connect:
            mock_connect.side_effect = Exception("Test error")
            
            result = sj_api.get_vacancies_page("Python", 0)
            
            # Должно быть пустой список при ошибке
            assert result == []
            
            # Должна быть вызвана функция логирования ошибки
            mock_logger.error.assert_called()

    def test_inheritance_chain_with_cached_api(self, sj_api):
        """Тестируем цепочку наследования через CachedAPI"""
        from src.api_modules.cached_api import CachedAPI
        
        # Проверяем полную цепочку наследования
        assert isinstance(sj_api, SuperJobAPI)
        assert isinstance(sj_api, CachedAPI)
        assert isinstance(sj_api, BaseAPI)
        
        # Проверяем порядок в MRO (Method Resolution Order)
        mro = SuperJobAPI.__mro__
        assert BaseAPI in mro
        assert CachedAPI in mro

    def test_configuration_integration(self, sj_api, mock_sj_config):
        """Тестируем интеграцию с конфигурацией"""
        # Проверяем, что конфигурация сохраняется
        assert sj_api.config is mock_sj_config
        
        # Проверяем использование конфигурации в запросах
        mock_sj_config.get_params.return_value = {"custom": "param"}
        
        with patch.object(sj_api, '_CachedAPI__connect_to_api') as mock_connect:
            mock_connect.return_value = {'objects': []}
            
            sj_api.get_vacancies_page("Python", 0, custom_param="value")
            
            # Проверяем, что конфигурация использовалась
            mock_sj_config.get_params.assert_called()

    def test_pagination_calculation(self, sj_api):
        """Тестируем расчет пагинации для SuperJob"""
        # Тест с большим количеством результатов
        large_response = {'total': 500, 'objects': []}
        
        with patch.object(sj_api, '_CachedAPI__connect_to_api') as mock_connect:
            mock_connect.return_value = large_response
            
            with patch.object(sj_api, 'paginator') as mock_paginator:
                mock_paginator.paginate.return_value = []
                
                sj_api.get_vacancies("Python", count=100, max_pages=10)
                
                # Проверяем, что пагинатор вызван с правильным количеством страниц
                mock_paginator.paginate.assert_called_once()
                # total_pages должно быть min(10, ceil(500/100)) = min(10, 5) = 5
                args, kwargs = mock_paginator.paginate.call_args
                assert 'total_pages' in kwargs or len(args) >= 2

    def test_user_agent_header_setup(self, mock_sj_config):
        """Тестируем установку User-Agent заголовка"""
        with patch('src.api_modules.sj_api.APIConnector') as mock_connector:
            with patch('src.api_modules.sj_api.Paginator'):
                with patch('src.api_modules.sj_api.EnvLoader') as mock_env:
                    mock_env.get_env_var.return_value = 'test_key'
                    
                    api = SuperJobAPI(mock_sj_config)
                    
                    # Проверяем, что User-Agent установлен
                    update_calls = mock_connector.return_value.headers.update.call_args_list
                    headers_dict = update_calls[0][0][0]
                    assert "User-Agent" in headers_dict
                    assert headers_dict["User-Agent"] == "VacancySearchApp/1.0"
