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
        from src.config.api_config import APIConfig
        config = APIConfig(user_agent='TestApp')
        return HeadHunterAPI(config)

    def test_init(self, hh_api):
        assert hh_api is not None
        assert hh_api._config.user_agent == 'TestApp'

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
        from src.config.api_config import APIConfig
        config = APIConfig(user_agent='TestApp')
        return SuperJobAPI(config)

    def test_init(self, sj_api):
        assert sj_api is not None
        assert hasattr(sj_api, 'config')

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
        return UnifiedAPI()

    def test_init(self, unified_api):
        assert unified_api is not None

    @patch('src.api_modules.hh_api.HeadHunterAPI.get_vacancies')
    @patch('src.api_modules.sj_api.SuperJobAPI.get_vacancies')
    def test_get_vacancies_from_all_sources(self, mock_sj, mock_hh, unified_api):
        mock_hh.return_value = [{'source': 'hh', 'id': '1'}]
        mock_sj.return_value = [{'source': 'sj', 'id': '2'}]

        result = unified_api.get_vacancies_from_sources("Python")
        assert isinstance(result, list)

    @patch('src.api_modules.hh_api.HeadHunterAPI.get_vacancies')
    def test_get_vacancies_from_hh(self, mock_hh, unified_api):
        mock_hh.return_value = [{'source': 'hh', 'id': '1'}]

        result = unified_api.get_hh_vacancies("Python")
        assert isinstance(result, list)

    @patch('src.api_modules.sj_api.SuperJobAPI.get_vacancies')
    def test_get_vacancies_from_sj(self, mock_sj, unified_api):
        mock_sj.return_value = [{'source': 'sj', 'id': '1'}]

        result = unified_api.get_sj_vacancies("Python")
        assert isinstance(result, list)


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

        result = api_connector.get_data("https://test.com")
        assert mock_get.called