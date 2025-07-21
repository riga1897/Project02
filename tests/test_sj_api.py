
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List

from src.api_modules.sj_api import SuperJobAPI
from src.config.sj_api_config import SJAPIConfig


class TestSuperJobAPI:
    """Тесты для SuperJobAPI"""

    @pytest.fixture
    def mock_config(self):
        """Фикстура для мокнутой конфигурации"""
        config = Mock(spec=SJAPIConfig)
        config.get_params.return_value = {
            "keyword": "test",
            "count": 100,
            "page": 0
        }
        return config

    @pytest.fixture
    def mock_api_connector(self):
        """Фикстура для мокнутого API коннектора"""
        connector = Mock()
        connector.headers = {}
        connector.connect.return_value = {"objects": []}
        return connector

    @pytest.fixture
    def mock_paginator(self):
        """Фикстура для мокнутого пагинатора"""
        paginator = Mock()
        paginator.paginate.return_value = []
        return paginator

    @pytest.fixture
    @patch('src.api_modules.sj_api.EnvLoader')
    @patch('src.api_modules.sj_api.APIConnector')
    @patch('src.api_modules.sj_api.Paginator')
    @patch('src.api_modules.sj_api.APIConfig')
    def sj_api(self, mock_api_config, mock_paginator_class, mock_connector_class, mock_env_loader, mock_config):
        """Фикстура для SuperJobAPI с замокнутыми зависимостями"""
        mock_env_loader.get_env_var.return_value = 'test_api_key'
        mock_connector = Mock()
        mock_connector.headers = {}
        mock_connector_class.return_value = mock_connector
        mock_paginator_class.return_value = Mock()
        
        with patch.object(SuperJobAPI, '__init__', lambda x, config=None: None):
            api = SuperJobAPI()
            api.config = mock_config
            api.connector = mock_connector
            api.paginator = Mock()
            api._CachedAPI__connect_to_api = Mock(return_value={'objects': []})
            
            return api

    def test_init_with_default_config(self):
        """Тест инициализации с конфигурацией по умолчанию"""
        with patch('src.api_modules.sj_api.EnvLoader') as mock_env, \
             patch('src.api_modules.sj_api.APIConnector') as mock_connector, \
             patch('src.api_modules.sj_api.Paginator') as mock_paginator, \
             patch('src.api_modules.sj_api.APIConfig') as mock_api_config, \
             patch('src.api_modules.sj_api.SJAPIConfig') as mock_sj_config, \
             patch('src.api_modules.sj_api.logger') as mock_logger:
            
            mock_env.get_env_var.return_value = 'test_key'
            mock_connector_instance = Mock()
            mock_connector_instance.headers = {}
            mock_connector.return_value = mock_connector_instance
            
            api = SuperJobAPI()
            
            assert api.config is not None
            assert api.connector is not None
            assert api.paginator is not None
            mock_sj_config.assert_called_once()

    def test_init_with_custom_config(self):
        """Тест инициализации с кастомной конфигурацией"""
        custom_config = Mock(spec=SJAPIConfig)
        
        with patch('src.api_modules.sj_api.EnvLoader') as mock_env, \
             patch('src.api_modules.sj_api.APIConnector') as mock_connector, \
             patch('src.api_modules.sj_api.Paginator') as mock_paginator, \
             patch('src.api_modules.sj_api.APIConfig') as mock_api_config, \
             patch('src.api_modules.sj_api.logger') as mock_logger:
            
            mock_env.get_env_var.return_value = 'test_key'
            mock_connector_instance = Mock()
            mock_connector_instance.headers = {}
            mock_connector.return_value = mock_connector_instance
            
            api = SuperJobAPI(custom_config)
            
            assert api.config == custom_config

    def test_init_with_test_api_key_warning(self):
        """Тест предупреждения при использовании тестового API ключа"""
        with patch('src.api_modules.sj_api.EnvLoader') as mock_env, \
             patch('src.api_modules.sj_api.APIConnector') as mock_connector, \
             patch('src.api_modules.sj_api.Paginator') as mock_paginator, \
             patch('src.api_modules.sj_api.APIConfig') as mock_api_config, \
             patch('src.api_modules.sj_api.SJAPIConfig') as mock_sj_config, \
             patch('src.api_modules.sj_api.logger') as mock_logger:
            
            mock_env.get_env_var.return_value = 'v3.r.137440105.example.test_tool'
            mock_connector_instance = Mock()
            mock_connector_instance.headers = {}
            mock_connector.return_value = mock_connector_instance
            
            api = SuperJobAPI()
            
            mock_logger.warning.assert_called_once()

    def test_init_with_real_api_key_info(self):
        """Тест информационного сообщения при использовании реального API ключа"""
        with patch('src.api_modules.sj_api.EnvLoader') as mock_env, \
             patch('src.api_modules.sj_api.APIConnector') as mock_connector, \
             patch('src.api_modules.sj_api.Paginator') as mock_paginator, \
             patch('src.api_modules.sj_api.APIConfig') as mock_api_config, \
             patch('src.api_modules.sj_api.SJAPIConfig') as mock_sj_config, \
             patch('src.api_modules.sj_api.logger') as mock_logger:
            
            mock_env.get_env_var.return_value = 'real_api_key'
            mock_connector_instance = Mock()
            mock_connector_instance.headers = {}
            mock_connector.return_value = mock_connector_instance
            
            api = SuperJobAPI()
            
            mock_logger.info.assert_called_once()

    def test_get_empty_response(self, sj_api):
        """Тест получения пустого ответа"""
        result = sj_api._get_empty_response()
        assert result == {'objects': []}

    def test_validate_vacancy_valid(self, sj_api):
        """Тест валидации корректной вакансии"""
        vacancy = {
            'profession': 'Python Developer',
            'link': 'https://example.com/vacancy/123'
        }
        result = sj_api._validate_vacancy(vacancy)
        assert result is True

    def test_validate_vacancy_missing_profession(self, sj_api):
        """Тест валидации вакансии без профессии"""
        vacancy = {
            'link': 'https://example.com/vacancy/123'
        }
        result = sj_api._validate_vacancy(vacancy)
        assert result is False

    def test_validate_vacancy_missing_link(self, sj_api):
        """Тест валидации вакансии без ссылки"""
        vacancy = {
            'profession': 'Python Developer'
        }
        result = sj_api._validate_vacancy(vacancy)
        assert result is False

    def test_validate_vacancy_not_dict(self, sj_api):
        """Тест валидации не-словаря"""
        assert sj_api._validate_vacancy("not a dict") is False
        assert sj_api._validate_vacancy(None) is False

    def test_connect_success(self, sj_api):
        """Тест успешного подключения"""
        test_data = {"objects": [{"profession": "test"}]}
        sj_api.connector.connect.return_value = test_data
        
        result = sj_api._SuperJobAPI__connect("http://test.com", {"param": "value"})
        
        assert result == test_data
        sj_api.connector.connect.assert_called_once_with("http://test.com", {"param": "value"})

    def test_connect_exception(self, sj_api):
        """Тест обработки исключения при подключении"""
        sj_api.connector.connect.side_effect = Exception("Connection error")
        
        with patch('src.api_modules.sj_api.logger') as mock_logger:
            result = sj_api._SuperJobAPI__connect("http://test.com", {"param": "value"})
            
            assert result == {'objects': []}
            mock_logger.error.assert_called_once()

    def test_get_vacancies_page_success(self, sj_api):
        """Тест успешного получения страницы вакансий"""
        test_data = {
            'objects': [
                {'profession': 'Python Developer', 'link': 'https://example.com/1'},
                {'profession': 'Java Developer', 'link': 'https://example.com/2'},
                {'invalid': 'vacancy'}  # Эта вакансия не пройдет валидацию
            ]
        }
        sj_api._CachedAPI__connect_to_api.return_value = test_data
        sj_api.config.get_params.return_value = {"keyword": "test", "page": 0}
        
        result = sj_api.get_vacancies_page("Python", 0)
        
        assert len(result) == 2
        assert all(item.get('source') == 'superjob.ru' for item in result)
        sj_api.config.get_params.assert_called_once_with(keyword="Python", page=0)

    def test_get_vacancies_page_empty_response(self, sj_api):
        """Тест получения пустой страницы вакансий"""
        sj_api._CachedAPI__connect_to_api.return_value = {'objects': []}
        
        result = sj_api.get_vacancies_page("Python", 0)
        
        assert result == []

    def test_get_vacancies_page_exception(self, sj_api):
        """Тест обработки исключения при получении страницы"""
        sj_api._CachedAPI__connect_to_api.side_effect = Exception("API error")
        
        with patch('src.api_modules.sj_api.logger') as mock_logger:
            result = sj_api.get_vacancies_page("Python", 0)
            
            assert result == []
            mock_logger.error.assert_called_once()

    def test_get_vacancies_success(self, sj_api):
        """Тест успешного получения всех вакансий"""
        initial_data = {'total': 100, 'objects': []}
        page_data = [{'profession': 'Python Dev', 'link': 'http://test.com'}]
        
        sj_api._CachedAPI__connect_to_api.return_value = initial_data
        sj_api.paginator.paginate.return_value = page_data
        
        with patch('src.api_modules.sj_api.logger') as mock_logger:
            result = sj_api.get_vacancies("Python")
            
            assert result == page_data
            mock_logger.info.assert_called()

    def test_get_vacancies_no_results(self, sj_api):
        """Тест получения вакансий без результатов"""
        initial_data = {'total': 0, 'objects': []}
        sj_api._CachedAPI__connect_to_api.return_value = initial_data
        
        with patch('src.api_modules.sj_api.logger') as mock_logger:
            result = sj_api.get_vacancies("NonExistent")
            
            assert result == []
            mock_logger.info.assert_called_with("No vacancies found for query")

    def test_get_vacancies_keyboard_interrupt(self, sj_api):
        """Тест прерывания получения вакансий пользователем"""
        sj_api._CachedAPI__connect_to_api.side_effect = KeyboardInterrupt()
        
        with patch('src.api_modules.sj_api.logger') as mock_logger, \
             patch('builtins.print') as mock_print:
            result = sj_api.get_vacancies("Python")
            
            assert result == []
            mock_logger.info.assert_called_with("Получение вакансий прервано пользователем")
            mock_print.assert_called_once_with("\nПолучение вакансий остановлено.")

    def test_get_vacancies_exception(self, sj_api):
        """Тест обработки исключения при получении вакансий"""
        sj_api._CachedAPI__connect_to_api.side_effect = Exception("API error")
        
        with patch('src.api_modules.sj_api.logger') as mock_logger:
            result = sj_api.get_vacancies("Python")
            
            assert result == []
            mock_logger.error.assert_called_once()

    def test_get_vacancies_with_pagination_params(self, sj_api):
        """Тест получения вакансий с параметрами пагинации"""
        initial_data = {'total': 1000, 'objects': []}
        sj_api._CachedAPI__connect_to_api.return_value = initial_data
        sj_api.paginator.paginate.return_value = []
        
        # Используем per_page вместо count чтобы избежать конфликта параметров
        result = sj_api.get_vacancies("Python", per_page=50, max_pages=5)
        
        # Проверяем, что paginator был вызван
        sj_api.paginator.paginate.assert_called_once()
        assert result == []

    def test_deduplicate_vacancies(self, sj_api):
        """Тест дедупликации вакансий"""
        vacancies = [
            {'profession': 'Dev1', 'link': 'link1'},
            {'profession': 'Dev2', 'link': 'link2'}
        ]
        
        with patch.object(sj_api.__class__.__bases__[1], '_deduplicate_vacancies') as mock_parent:
            mock_parent.return_value = vacancies
            
            result = sj_api._deduplicate_vacancies(vacancies)
            
            mock_parent.assert_called_once_with(vacancies, 'sj')
            assert result == vacancies

    def test_get_vacancies_with_deduplication(self, sj_api):
        """Тест получения вакансий с дедупликацией"""
        vacancies = [{'profession': 'Dev', 'link': 'link'}]
        
        with patch.object(sj_api, 'get_vacancies') as mock_get, \
             patch.object(sj_api, '_deduplicate_vacancies') as mock_dedup:
            mock_get.return_value = vacancies
            mock_dedup.return_value = vacancies
            
            result = sj_api.get_vacancies_with_deduplication("Python")
            
            mock_get.assert_called_once_with("Python")
            mock_dedup.assert_called_once_with(vacancies)
            assert result == vacancies

    def test_clear_cache(self, sj_api):
        """Тест очистки кэша"""
        with patch.object(sj_api.__class__.__bases__[0], 'clear_cache') as mock_parent:
            sj_api.clear_cache("test_prefix")
            mock_parent.assert_called_once_with("sj")
