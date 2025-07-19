import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
from src.api_modules.base_api import BaseAPI
from src.api_modules.hh_api import HeadHunterAPI
from src.api_modules.sj_api import SuperJobAPI
from src.api_modules.unified_api import UnifiedAPI
from src.api_modules.get_api import APIConnector
from src.api_modules.cached_api import CachedAPI
from src.config.api_config import APIConfig
import sys
from pathlib import Path

# Добавляем путь к исходному коду
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestBaseAPI:

    def test_init_with_config(self):
        config = APIConfig(user_agent='TestApp')

        # Создаем мок класс, наследующий от BaseAPI
        class MockAPI(BaseAPI):
            def get_vacancies(self, search_query: str, **kwargs):
                return []

            def clear_cache(self):
                pass

        api = MockAPI(config)
        assert api.config.user_agent == 'TestApp'

    def test_init_without_config(self):
        # Создаем мок класс, наследующий от BaseAPI
        class MockAPI(BaseAPI):
            def get_vacancies(self, search_query: str, **kwargs):
                return []

            def clear_cache(self):
                pass

        api = MockAPI()
        assert api.config.user_agent == "MyVacancyApp/1.0"

    def test_abstract_methods(self):
        # Тест что абстрактные методы действительно абстрактные
        with pytest.raises(TypeError):
            BaseAPI()  # Нельзя создать экземпляр абстрактного класса


class TestCachedAPI:

    @pytest.fixture
    def cached_api_mock(self, tmp_path):
        """Мок CachedAPI для тестирования"""
        class MockCachedAPI(CachedAPI):
            def _get_empty_response(self):
                return {'items': []}

            def _validate_vacancy(self, vacancy):
                return True

            def get_vacancies_page(self, search_query, page=0, **kwargs):
                return [{'id': f'{page}_1', 'name': 'Test'}]

            def get_vacancies(self, search_query, **kwargs):
                return [{'id': '1', 'name': 'Test'}]

        return MockCachedAPI(str(tmp_path))

    def test_init_cache(self, cached_api_mock):
        assert cached_api_mock.cache_dir.exists()
        assert hasattr(cached_api_mock, 'cache')

    def test_clear_cache(self, cached_api_mock):
        cached_api_mock.clear_cache("test")
        # Проверяем что метод выполняется без ошибок
        assert True

    @patch('src.api_modules.cached_api.FileCache')
    def test_cache_operations(self, mock_cache, cached_api_mock):
        # Тестируем кэширование
        mock_cache_instance = mock_cache.return_value
        mock_cache_instance.load_response.return_value = None

        # Вызываем защищенный метод через имя с мангулированием
        result = cached_api_mock._CachedAPI__connect_to_api("http://test.com", {}, "test")
        assert isinstance(result, dict)

    @patch('src.api_modules.cached_api.FileCache')
    def test_cache_hit(self, mock_cache, cached_api_mock):
        # Тестируем получение данных из кэша
        mock_cache_instance = mock_cache.return_value
        mock_cache_instance.load_response.return_value = {'data': {'items': [{'test': 'cached'}]}}

        # Мокаем кэш экземпляра
        cached_api_mock.cache = mock_cache_instance

        result = cached_api_mock._CachedAPI__connect_to_api("http://test.com", {}, "test")
        assert result == {'items': [{'test': 'cached'}]}

    def test_clear_cache_error(self, cached_api_mock):
        # Тестируем обработку ошибок при очистке кэша
        with patch.object(cached_api_mock.cache, 'clear', side_effect=Exception("Clear error")):
            cached_api_mock.clear_cache("test")
            # Проверяем что ошибка обрабатывается без исключения
            assert True

    def test_abstract_methods_cached_api(self):
        # Тест абстрактных методов CachedAPI
        from src.api_modules.cached_api import CachedAPI

        # Проверяем что нельзя создать экземпляр абстрактного класса
        with pytest.raises(TypeError, match="Can't instantiate abstract class CachedAPI"):
            CachedAPI("test_dir")

    @patch('src.api_modules.cached_api.FileCache')
    def test_cache_connect_api_error_handling(self, mock_cache, cached_api_mock):
        # Тестируем обработку ошибок в __connect_to_api
        mock_cache_instance = mock_cache.return_value
        mock_cache_instance.load_response.return_value = None

        # Мокаем connector чтобы бросить исключение
        with patch.object(cached_api_mock, 'connector') as mock_connector:
            mock_connector.connect.side_effect = Exception("API Error")

            result = cached_api_mock._CachedAPI__connect_to_api("http://test.com", {}, "test")
            assert result == {'items': []}  # Должен вернуть пустой ответ



# Добавляем путь к исходному коду
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestHeadHunterAPI:

    @pytest.fixture
    def hh_api(self):
        from src.config.api_config import APIConfig
        config = APIConfig(user_agent='TestApp')
        return HeadHunterAPI(config)

    def test_init(self, hh_api):
        assert hh_api is not None
        assert hh_api._config.user_agent == 'TestApp'

    def test_validate_vacancy(self, hh_api):
        valid_vacancy = {
            'name': 'Test Job',
            'alternate_url': 'https://test.com',
            'salary': {'from': 100000}
        }
        invalid_vacancy = {'name': 'Test Job'}

        assert hh_api._validate_vacancy(valid_vacancy) is True
        assert hh_api._validate_vacancy(invalid_vacancy) is False

    def test_get_empty_response(self, hh_api):
        result = hh_api._get_empty_response()
        assert result == {'items': []}

    @patch('src.api_modules.hh_api.HeadHunterAPI._CachedAPI__connect_to_api')
    def test_get_vacancies_page_success(self, mock_connect, hh_api):
        mock_connect.return_value = {
            'items': [
                {'name': 'Test', 'alternate_url': 'url', 'salary': {}},
                {'invalid': 'vacancy'}  # Будет отфильтрована
            ]
        }

        result = hh_api.get_vacancies_page("Python", 0)
        assert len(result) == 1
        assert result[0]['name'] == 'Test'

    @patch('src.api_modules.hh_api.HeadHunterAPI._CachedAPI__connect_to_api')
    def test_get_vacancies_page_error(self, mock_connect, hh_api):
        mock_connect.side_effect = Exception("Error")

        result = hh_api.get_vacancies_page("Python", 0)
        assert result == []

    @patch('src.api_modules.hh_api.HeadHunterAPI._CachedAPI__connect_to_api')
    def test_get_vacancies_no_found(self, mock_connect, hh_api):
        mock_connect.return_value = {'found': 0, 'items': []}

        result = hh_api.get_vacancies("Python")
        assert result == []

    @patch('src.api_modules.hh_api.HeadHunterAPI.get_vacancies_page')
    @patch('src.api_modules.hh_api.HeadHunterAPI._CachedAPI__connect_to_api')
    def test_get_vacancies_with_pagination(self, mock_connect, mock_get_page, hh_api):
        mock_connect.return_value = {
            'found': 100,
            'pages': 5,
            'items': []
        }
        mock_get_page.return_value = [{'name': 'Test', 'alternate_url': 'url', 'salary': {}}]

        result = hh_api.get_vacancies("Python")
        assert isinstance(result, list)

    @patch('requests.get')
    def test_get_vacancies_success(self, mock_get, hh_api):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'found': 100,
            'items': [{'id': '1', 'name': 'Test'}]
        }
        mock_get.return_value = mock_response

        result = hh_api.get_vacancies("Python")
        assert isinstance(result, list)

    @patch('requests.get')
    def test_get_vacancies_error(self, mock_get, hh_api):
        mock_get.side_effect = Exception("Network error")

        result = hh_api.get_vacancies("Python")
        assert result == []

    def test_clear_cache(self, hh_api):
        hh_api.clear_cache()
        # Проверяем что метод выполняется без ошибок
        assert True

    @patch('src.api_modules.hh_api.HeadHunterAPI._CachedAPI__connect_to_api')
    def test_get_vacancies_with_timeout(self, mock_connect, hh_api):
        # Тестируем обработку таймаута
        mock_connect.side_effect = ConnectionError("Timeout")

        result = hh_api.get_vacancies("Python")
        assert result == []

    @patch('src.api_modules.hh_api.HeadHunterAPI._CachedAPI__connect_to_api')
    def test_get_vacancies_with_connection_error(self, mock_connect, hh_api):
        # Тестируем обработку ошибки соединения
        mock_connect.side_effect = Exception("Connection failed")

        result = hh_api.get_vacancies("Python")
        assert result == []

    @patch('src.api_modules.hh_api.HeadHunterAPI.get_vacancies_page')
    @patch('src.api_modules.hh_api.HeadHunterAPI._CachedAPI__connect_to_api')
    def test_get_vacancies_keyboard_interrupt(self, mock_connect, mock_get_page, hh_api):
        # Тестируем обработку KeyboardInterrupt
        mock_connect.return_value = {'found': 100, 'pages': 5, 'items': []}
        mock_get_page.side_effect = KeyboardInterrupt()

        result = hh_api.get_vacancies("Python")
        assert result == []


class TestSuperJobAPI:

    @pytest.fixture
    def sj_api(self):
        from src.config.sj_api_config import SJAPIConfig
        config = SJAPIConfig()
        return SuperJobAPI(config)

    def test_init(self, sj_api):
        assert sj_api is not None
        assert hasattr(sj_api, 'config')

    def test_validate_vacancy(self, sj_api):
        valid_vacancy = {
            'profession': 'Test Job',
            'link': 'https://test.com'
        }
        invalid_vacancy = {'profession': 'Test Job'}

        assert sj_api._validate_vacancy(valid_vacancy) is True
        assert sj_api._validate_vacancy(invalid_vacancy) is False

    def test_get_empty_response(self, sj_api):
        result = sj_api._get_empty_response()
        assert result == {'objects': []}

    @patch('src.api_modules.sj_api.SuperJobAPI._CachedAPI__connect_to_api')
    def test_get_vacancies_page_success(self, mock_connect, sj_api):
        mock_connect.return_value = {
            'objects': [
                {'profession': 'Test', 'link': 'url'},
                {'invalid': 'vacancy'}  # Будет отфильтрована
            ]
        }

        result = sj_api.get_vacancies_page("Python", 0)
        assert len(result) == 1
        assert result[0]['profession'] == 'Test'
        assert result[0]['source'] == 'superjob.ru'

    @patch('src.api_modules.sj_api.SuperJobAPI._CachedAPI__connect_to_api')
    def test_get_vacancies_page_error(self, mock_connect, sj_api):
        mock_connect.side_effect = Exception("Error")

        result = sj_api.get_vacancies_page("Python", 0)
        assert result == []

    @patch('src.api_modules.sj_api.SuperJobAPI._CachedAPI__connect_to_api')
    def test_get_vacancies_no_total(self, mock_connect, sj_api):
        mock_connect.return_value = {'total': 0, 'objects': []}

        result = sj_api.get_vacancies("Python")
        assert result == []

    @patch('src.api_modules.sj_api.SuperJobAPI.get_vacancies_page')
    @patch('src.api_modules.sj_api.SuperJobAPI._CachedAPI__connect_to_api')
    def test_get_vacancies_with_pagination(self, mock_connect, mock_get_page, sj_api):
        mock_connect.return_value = {
            'total': 100,
            'objects': []
        }
        mock_get_page.return_value = [{'profession': 'Test', 'link': 'url', 'source': 'superjob.ru'}]

        result = sj_api.get_vacancies("Python")
        assert isinstance(result, list)

    @patch('requests.get')
    def test_get_vacancies_success(self, mock_get, sj_api):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'total': 50,
            'objects': [{'id': 1, 'profession': 'Test'}]
        }
        mock_get.return_value = mock_response

        result = sj_api.get_vacancies("Python")
        assert isinstance(result, list)

    @patch('requests.get')
    def test_get_vacancies_error(self, mock_get, sj_api):
        mock_get.side_effect = Exception("Network error")

        result = sj_api.get_vacancies("Python")
        assert result == []

    def test_clear_cache(self, sj_api):
        sj_api.clear_cache()
        # Проверяем что метод выполняется без ошибок
        assert True

    def test_validate_vacancy_missing_required_fields(self, sj_api):
        # Тестируем валидацию с отсутствующими полями
        invalid_vacancy = {'id': 1}  # Нет profession и link
        assert sj_api._validate_vacancy(invalid_vacancy) is False

        # Тестируем с None значениями
        invalid_vacancy2 = {'profession': None, 'link': 'test'}
        assert sj_api._validate_vacancy(invalid_vacancy2) is False

        # Тестируем с пустыми строками
        invalid_vacancy3 = {'profession': '', 'link': 'test'}
        assert sj_api._validate_vacancy(invalid_vacancy3) is False

    @patch('src.api_modules.sj_api.SuperJobAPI._CachedAPI__connect_to_api')
    def test_get_vacancies_connection_error(self, mock_connect, sj_api):
        # Тестируем обработку ошибки соединения
        mock_connect.side_effect = ConnectionError("Connection failed")

        result = sj_api.get_vacancies("Python")
        assert result == []

    def test_init_with_test_api_key(self):
        # Тестируем инициализацию с тестовым ключом
        with patch.dict('os.environ', {}, clear=True):
            with patch('src.utils.env_loader.EnvLoader.get_env_var', return_value='v3.r.137440105.example.test_tool'):
                sj_api = SuperJobAPI()
                assert sj_api is not None

    @patch('src.api_modules.sj_api.SuperJobAPI.get_vacancies_page')
    @patch('src.api_modules.sj_api.SuperJobAPI._CachedAPI__connect_to_api')
    def test_get_vacancies_keyboard_interrupt(self, mock_connect, mock_get_page, sj_api):
        # Тестируем обработку KeyboardInterrupt
        mock_connect.return_value = {'total': 100, 'objects': []}
        mock_get_page.side_effect = KeyboardInterrupt()

        result = sj_api.get_vacancies("Python")
        assert result == []


class TestUnifiedAPI:

    @pytest.fixture
    def unified_api(self):
        return UnifiedAPI()

    def test_init(self, unified_api):
        assert unified_api is not None
        assert hasattr(unified_api, 'hh_api')
        assert hasattr(unified_api, 'sj_api')
        assert hasattr(unified_api, 'parser')

    def test_get_available_sources(self, unified_api):
        sources = unified_api.get_available_sources()
        assert sources == ['hh', 'sj']

    def test_validate_sources_valid(self, unified_api):
        result = unified_api.validate_sources(['hh', 'sj'])
        assert result == ['hh', 'sj']

    def test_validate_sources_invalid(self, unified_api):
        result = unified_api.validate_sources(['invalid', 'source'])
        assert result == ['hh', 'sj']  # Возвращает все доступные

    def test_validate_sources_partial(self, unified_api):
        result = unified_api.validate_sources(['hh', 'invalid'])
        assert result == ['hh']

    @patch('src.api_modules.hh_api.HeadHunterAPI.get_vacancies')
    @patch('src.api_modules.sj_api.SuperJobAPI.get_vacancies')
    def test_get_vacancies_from_all_sources(self, mock_sj, mock_hh, unified_api):
        # Мокаем HH данные
        mock_hh.return_value = [
            {
                'id': '1', 'name': 'HH Job', 'alternate_url': 'http://hh.ru/1',
                'salary': {'from': 100000}, 'employer': {'name': 'HH Company'}
            }
        ]

        # Мокаем SJ данные
        mock_sj.return_value = [
            {
                'id': 2, 'profession': 'SJ Job', 'link': 'http://sj.ru/2',
                'payment_from': 120000, 'firm_name': 'SJ Company'
            }
        ]

        result = unified_api.get_vacancies_from_sources("Python")
        assert isinstance(result, list)

    @patch('src.api_modules.hh_api.HeadHunterAPI.get_vacancies')
    def test_get_vacancies_hh_error(self, mock_hh, unified_api):
        mock_hh.side_effect = Exception("HH Error")

        result = unified_api.get_vacancies_from_sources("Python", sources=['hh'])
        assert result == []

    @patch('src.api_modules.sj_api.SuperJobAPI.get_vacancies')
    def test_get_vacancies_sj_error(self, mock_sj, unified_api):
        mock_sj.side_effect = Exception("SJ Error")

        result = unified_api.get_vacancies_from_sources("Python", sources=['sj'])
        assert result == []

    @patch('src.api_modules.hh_api.HeadHunterAPI.get_vacancies')
    def test_get_vacancies_from_hh(self, mock_hh, unified_api):
        mock_hh.return_value = [
            {
                'id': '1', 'name': 'HH Job', 'alternate_url': 'http://hh.ru/1',
                'salary': {'from': 100000}, 'employer': {'name': 'HH Company'}
            }
        ]

        result = unified_api.get_hh_vacancies("Python")
        assert isinstance(result, list)

    @patch('src.api_modules.sj_api.SuperJobAPI.get_vacancies')
    def test_get_vacancies_from_sj(self, mock_sj, unified_api):
        mock_sj.return_value = [
            {
                'id': 2, 'profession': 'SJ Job', 'link': 'http://sj.ru/2',
                'payment_from': 120000, 'firm_name': 'SJ Company'
            }
        ]

        result = unified_api.get_sj_vacancies("Python")
        assert isinstance(result, list)

    def test_clear_cache_selected(self, unified_api):
        with patch.object(unified_api.hh_api, 'clear_cache') as mock_hh_clear:
            with patch.object(unified_api.sj_api, 'clear_cache') as mock_sj_clear:
                unified_api.clear_cache({'hh': True, 'sj': False})
                mock_hh_clear.assert_called_once()
                mock_sj_clear.assert_not_called()

    def test_clear_all_cache(self, unified_api):
        with patch.object(unified_api.hh_api, 'clear_cache') as mock_hh_clear:
            with patch.object(unified_api.sj_api, 'clear_cache') as mock_sj_clear:
                unified_api.clear_all_cache()
                mock_hh_clear.assert_called_once()
                mock_sj_clear.assert_called_once()

    def test_clear_cache_error(self, unified_api):
        with patch.object(unified_api.hh_api, 'clear_cache', side_effect=Exception("Clear error")):
            unified_api.clear_cache({'hh': True})
            # Проверяем что ошибка обрабатывается
            assert True

    @patch('src.api_modules.sj_api.SuperJobAPI.get_vacancies')
    def test_get_vacancies_sj_conversion_error(self, mock_sj, unified_api):
        # Тестируем ошибку конвертации SJ вакансий
        mock_sj.return_value = [
            {'id': 1, 'profession': 'Test', 'link': 'http://test.com'}
        ]

        with patch.object(unified_api.parser, 'parse_vacancies', side_effect=Exception("Parse error")):
            result = unified_api.get_vacancies_from_sources("Python", sources=['sj'])
            assert result == []

    @patch('src.api_modules.sj_api.SuperJobAPI.get_vacancies')
    def test_get_vacancies_sj_no_data(self, mock_sj, unified_api):
        # Тестируем случай когда SJ не возвращает данные
        mock_sj.return_value = []

        result = unified_api.get_vacancies_from_sources("Python", sources=['sj'])
        assert result == []

    @patch('src.api_modules.sj_api.SuperJobAPI.get_vacancies')
    def test_get_vacancies_sj_unified_conversion_error(self, mock_sj, unified_api):
        # Тестируем ошибку конвертации в унифицированный формат
        mock_sj.return_value = [
            {'id': 1, 'profession': 'Test', 'link': 'http://test.com'}
        ]

        with patch.object(unified_api.parser, 'convert_to_unified_format', side_effect=Exception("Convert error")):
            result = unified_api.get_vacancies_from_sources("Python", sources=['sj'])
            assert result == []

    def test_get_sj_vacancies_with_period_conversion(self, unified_api):
        # Тестируем конвертацию параметра period в published для SJ API
        with patch.object(unified_api, 'get_vacancies_from_sources', return_value=[]) as mock_get:
            unified_api.get_sj_vacancies("Python", period=7)

            # Проверяем что period конвертируется в published и оба параметра передаются
            mock_get.assert_called_once_with("Python", sources=['sj'], period=7, published=7)

    @patch('src.api_modules.hh_api.HeadHunterAPI.get_vacancies')
    def test_get_hh_vacancies_error_logging(self, mock_hh, unified_api):
        # Тестируем логирование ошибок HH API
        mock_hh.side_effect = Exception("HH API Error")

        result = unified_api.get_vacancies_from_sources("Python", sources=['hh'])
        assert result == []

    @patch('src.vacancies.models.Vacancy.from_dict')  
    @patch('src.api_modules.hh_api.HeadHunterAPI.get_vacancies')
    def test_get_hh_vacancies_conversion_error(self, mock_hh, mock_vacancy, unified_api):
        # Тестируем ошибку конвертации HH вакансий
        mock_hh.return_value = [{'id': '1', 'name': 'Test'}]
        mock_vacancy.side_effect = Exception("Conversion error")

        result = unified_api.get_vacancies_from_sources("Python", sources=['hh'])
        assert result == []

    @patch('src.api_modules.sj_api.SuperJobAPI.get_vacancies')
    def test_get_vacancies_from_sources_sj_none_data(self, mock_sj, unified_api):
        # Тестируем случай когда SJ возвращает None (строка 59)
        mock_sj.return_value = None

        result = unified_api.get_vacancies_from_sources("Python", sources=['sj'])
        assert result == []

    @patch('src.api_modules.sj_api.SuperJobAPI.get_vacancies')
    def test_get_vacancies_from_sources_period_sync(self, mock_sj, unified_api):
        # Тестируем синхронизацию параметра period (строки 116-117)
        mock_sj.return_value = []

        unified_api.get_vacancies_from_sources("Python", sources=['sj'], period=30)

        # Проверяем что period был передан как published
        mock_sj.assert_called_once_with("Python", period=30, published=30)

    @patch('src.api_modules.sj_api.SuperJobAPI.get_vacancies')
    def test_period_condition_check_line_116(self, mock_sj, unified_api):
        # Модуль 1: Покрытие строки 116 - условие if 'period' in kwargs
        mock_sj.return_value = []
        # Вызываем БЕЗ period для покрытия False ветки
        unified_api.get_vacancies_from_sources("Python", sources=['sj'])
        # Вызываем С period для покрытия True ветки  
        unified_api.get_vacancies_from_sources("Python", sources=['sj'], period=1)
        assert mock_sj.call_count == 2

    @patch('src.api_modules.sj_api.SuperJobAPI.get_vacancies')
    def test_period_assignment_line_117(self, mock_sj, unified_api):
        # Модуль 2: Покрытие строки 117 - sj_kwargs['published'] = kwargs['period']
        mock_sj.return_value = []
        unified_api.get_vacancies_from_sources("Python", sources=['sj'], period=42)
        # Проверяем что выполнилось присваивание published = period
        mock_sj.assert_called_once_with("Python", period=42, published=42)

    def test_clear_all_cache_with_error(self, unified_api):
        # Тестируем ошибку при очистке всего кэша (строки 128-129)
        with patch.object(unified_api.hh_api, 'clear_cache', side_effect=Exception("HH clear error")) as mock_hh_clear:
            with patch.object(unified_api.sj_api, 'clear_cache') as mock_sj_clear:
                unified_api.clear_all_cache()

                # Проверяем что оба метода были вызваны несмотря на ошибку в первом
                mock_hh_clear.assert_called_once()
                mock_sj_clear.assert_called_once()

    def test_clear_all_cache_with_sj_error(self, unified_api):
        # Тестируем ошибку при очистке SJ кэша (строки 134-135)
        with patch.object(unified_api.hh_api, 'clear_cache') as mock_hh_clear:
            with patch.object(unified_api.sj_api, 'clear_cache', side_effect=Exception("SJ clear error")) as mock_sj_clear:
                unified_api.clear_all_cache()

                # Проверяем что оба метода были вызваны
                mock_hh_clear.assert_called_once()
                mock_sj_clear.assert_called_once()


class TestAPIConnector:

    @pytest.fixture
    def api_connector(self):
        return APIConnector()

    def test_init(self, api_connector):
        assert api_connector is not None
        assert hasattr(api_connector, 'config')

    @patch('requests.get')
    def test_get_vacancies(self, mock_get, api_connector):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'items': []}
        mock_get.return_value = mock_response

        result = api_connector.connect("https://test.com", {})
        assert mock_get.called

    @patch('requests.get')
    def test_connect_with_progress(self, mock_get, api_connector):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'test'}
        mock_get.return_value = mock_response

        result = api_connector.connect("https://test.com", {}, show_progress=True)
        assert result == {'data': 'test'}

    @patch('requests.get')
    def test_connect_timeout_error(self, mock_get, api_connector):
        import requests
        mock_get.side_effect = requests.Timeout("Timeout")

        with pytest.raises(ConnectionError):
            api_connector.connect("https://test.com", {})

    @patch('requests.get')
    def test_connect_http_error(self, mock_get, api_connector):
        import requests
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError("Not found")
        mock_response.text = "Not found"
        mock_get.return_value = mock_response

        with pytest.raises(ConnectionError):
            api_connector.connect("https://test.com", {})

    @patch('requests.get')
    def test_connect_rate_limit(self, mock_get, api_connector):
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        mock_response_429.headers = {'Retry-After': '0'}

        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {'data': 'success'}

        mock_get.side_effect = [mock_response_429, mock_response_200]

        result = api_connector.connect("https://test.com", {})
        assert result == {'data': 'success'}

    @patch('requests.get')
    def test_connect_json_decode_error(self, mock_get, api_connector):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        with pytest.raises(ConnectionError):
            api_connector.connect("https://test.com", {})

    @patch('requests.get')
    def test_connect_generic_exception(self, mock_get, api_connector):
        mock_get.side_effect = Exception("Generic error")

        with pytest.raises(ConnectionError, match="Unexpected error"):
            api_connector.connect("https://test.com", {})

    @patch('requests.get')
    def test_connect_http_error_no_response(self, mock_get, api_connector):
        import requests
        http_error = requests.HTTPError("HTTP Error")
        http_error.response = None
        mock_get.side_effect = http_error

        with pytest.raises(ConnectionError, match="HTTP error \\(no response details\\)"):
            api_connector.connect("https://test.com", {})

    @patch('requests.get')
    def test_connect_request_exception(self, mock_get, api_connector):
        # Тестируем RequestException (строка 88)
        import requests
        mock_get.side_effect = requests.RequestException("Request failed")

        with pytest.raises(ConnectionError, match="Connection error"):
            api_connector.connect("https://test.com", {})