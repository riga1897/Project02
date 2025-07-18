import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Добавляем путь к исходному коду
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api_modules.hh_api import HeadHunterAPI
from src.api_modules.sj_api import SuperJobAPI
from src.api_modules.unified_api import UnifiedAPI
from src.api_modules.get_api import APIConnector
from src.config.api_config import APIConfig


class TestHeadHunterAPI:

    @pytest.fixture
    def hh_api(self):
        config = {
            'url': 'https://api.hh.ru/vacancies',
            'headers': {'User-Agent': 'TestApp'},
            'get_params': {'per_page': 100}
        }
        return HeadHunterAPI(config)

    def test_init(self, hh_api):
        assert hh_api is not None
        assert hh_api.base_url == 'https://api.hh.ru/vacancies'

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


class TestSuperJobAPI:

    @pytest.fixture
    def sj_api(self):
        config = {
            'url': 'https://api.superjob.ru/2.0/vacancies/',
            'headers': {'X-Api-App-Id': 'test_key'},
            'get_params': {'count': 100}
        }
        return SuperJobAPI(config)

    def test_init(self, sj_api):
        assert sj_api is not None
        assert sj_api.base_url == 'https://api.superjob.ru/2.0/vacancies/'

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


class TestUnifiedAPI:

    @pytest.fixture
    def unified_api(self):
        config = APIConfig()
        hh_api = Mock()
        sj_api = Mock()
        return UnifiedAPI(config, hh_api, sj_api)

    def test_init(self, unified_api):
        assert unified_api is not None

    def test_get_vacancies_from_all_sources(self, unified_api):
        unified_api.hh_api.get_vacancies.return_value = [{'source': 'hh', 'id': '1'}]
        unified_api.sj_api.get_vacancies.return_value = [{'source': 'sj', 'id': '2'}]

        result = unified_api.get_vacancies_from_all_sources("Python")
        assert len(result) == 2

    def test_get_vacancies_from_hh(self, unified_api):
        unified_api.hh_api.get_vacancies.return_value = [{'source': 'hh', 'id': '1'}]

        result = unified_api.get_vacancies_from_hh("Python")
        assert len(result) == 1

    def test_get_vacancies_from_sj(self, unified_api):
        unified_api.sj_api.get_vacancies.return_value = [{'source': 'sj', 'id': '1'}]

        result = unified_api.get_vacancies_from_sj("Python")
        assert len(result) == 1


class TestAPIConnector:

    @pytest.fixture
    def api_connector(self):
        return APIConnector()

    def test_init(self, api_connector):
        assert api_connector is not None
        assert hasattr(api_connector, 'unified_api')

    def test_get_vacancies(self, api_connector):
        with patch.object(api_connector.unified_api, 'get_vacancies_from_all_sources') as mock_get:
            mock_get.return_value = [{'id': '1', 'title': 'Test'}]

            result = api_connector.get_vacancies("Python")
            assert len(result) == 1
            mock_get.assert_called_once_with("Python")