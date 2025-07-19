
import pytest
import sys
from pathlib import Path

# Добавляем путь к исходному коду
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.hh_api_config import HHAPIConfig


class TestHHAPIConfig:
    
    @pytest.fixture
    def hh_config(self):
        return HHAPIConfig()
    
    def test_init_default(self, hh_config):
        assert hh_config.area == 1
        assert hh_config.per_page == 50
        assert hh_config.only_with_salary is False
        assert hh_config.custom_params is None
    
    def test_init_with_params(self):
        config = HHAPIConfig(area=2, per_page=100, only_with_salary=True)
        assert config.area == 2
        assert config.per_page == 100
        assert config.only_with_salary is True
    
    def test_get_params_default(self, hh_config):
        params = hh_config.get_params()
        assert params['area'] == 1
        assert params['per_page'] == 50
        assert params['only_with_salary'] is False
    
    def test_get_params_with_override(self, hh_config):
        params = hh_config.get_params(area=2, per_page=25)
        assert params['area'] == 2
        assert params['per_page'] == 25
        assert params['only_with_salary'] is False
    
    def test_get_params_with_custom(self):
        config = HHAPIConfig(custom_params={'custom_key': 'custom_value'})
        params = config.get_params()
        assert params['custom_key'] == 'custom_value'




import pytest
import sys
from pathlib import Path

# Добавляем путь к исходному коду
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.api_config import APIConfig, HHAPIConfig
from src.config.sj_api_config import SJAPIConfig
from src.config.ui_config import UIConfig


class TestHHAPIConfig:
    
    @pytest.fixture
    def hh_config(self):
        return HHAPIConfig()
    
    def test_init_default(self, hh_config):
        assert hh_config.area == 1
        assert hh_config.per_page == 50
        assert hh_config.only_with_salary is False
        assert hh_config.custom_params is None
    
    def test_init_with_params(self):
        config = HHAPIConfig(area=2, per_page=100, only_with_salary=True)
        assert config.area == 2
        assert config.per_page == 100
        assert config.only_with_salary is True
    
    def test_get_params_default(self, hh_config):
        params = hh_config.get_params()
        assert params['area'] == 1
        assert params['per_page'] == 50
        assert params['only_with_salary'] is False
    
    def test_get_params_with_override(self, hh_config):
        params = hh_config.get_params(area=2, per_page=25)
        assert params['area'] == 2
        assert params['per_page'] == 25
        assert params['only_with_salary'] is False
    
    def test_get_params_with_custom(self):
        config = HHAPIConfig(custom_params={'custom_key': 'custom_value'})
        params = config.get_params()
        assert params['custom_key'] == 'custom_value'


class TestAPIConfig:
    
    @pytest.fixture
    def api_config(self):
        return APIConfig()
    
    def test_init_default(self, api_config):
        assert api_config.user_agent == "MyVacancyApp/1.0"
        assert api_config.timeout == 15
        assert api_config.request_delay == 0.5
        assert api_config.max_pages == 20
        assert isinstance(api_config.hh_config, HHAPIConfig)
    
    def test_init_with_params(self):
        hh_config = HHAPIConfig(area=2)
        config = APIConfig(
            user_agent="TestApp/1.0",
            timeout=30,
            request_delay=1.0,
            hh_config=hh_config,
            max_pages=10
        )
        assert config.user_agent == "TestApp/1.0"
        assert config.timeout == 30
        assert config.request_delay == 1.0
        assert config.max_pages == 10
        assert config.hh_config.area == 2
    
    def test_get_pagination_params_default(self, api_config):
        params = api_config.get_pagination_params()
        assert params['max_pages'] == 20
    
    def test_get_pagination_params_with_override(self, api_config):
        params = api_config.get_pagination_params(max_pages=5)
        assert params['max_pages'] == 5


class TestSJAPIConfig:
    
    @pytest.fixture
    def sj_config(self):
        return SJAPIConfig()
    
    def test_init_default(self, sj_config):
        assert sj_config.count == 500
        assert sj_config.published == 15
        assert sj_config.custom_params is None
    
    def test_init_with_params(self):
        config = SJAPIConfig(count=50, published=7, custom_params={'test': 'value'})
        assert config.count == 50
        assert config.published == 7
        assert config.custom_params == {'test': 'value'}
    
    def test_get_params_default(self, sj_config):
        params = sj_config.get_params()
        assert params['count'] == 500
        assert params['order_field'] == 'date'
        assert params['order_direction'] == 'desc'
        assert params['published'] == 15
    
    def test_get_params_with_override(self, sj_config):
        params = sj_config.get_params(count=50, town=2)
        assert params['count'] == 50
        assert params['town'] == 2
        assert params['order_field'] == 'date'
        assert params['order_direction'] == 'desc'
    
    def test_get_params_with_keyword(self, sj_config):
        params = sj_config.get_params(keyword="Python")
        assert params['keyword'] == "Python"
        assert params['count'] == 500
        assert params['order_field'] == 'date'
    
    def test_get_params_with_page(self, sj_config):
        params = sj_config.get_params(page=2)
        assert params['page'] == 2
        assert params['count'] == 500
    
    def test_get_params_with_custom_params(self):
        config = SJAPIConfig(custom_params={'custom_key': 'custom_value'})
        params = config.get_params()
        assert params['custom_key'] == 'custom_value'
        assert params['count'] == 500


class TestUIConfig:
    
    @pytest.fixture
    def ui_config(self):
        return UIConfig()
    
    def test_init_default(self, ui_config):
        assert ui_config.items_per_page == 5
        assert ui_config.max_display_items == 20
    
    def test_init_with_params(self):
        config = UIConfig()
        config.items_per_page = 10
        config.max_display_items = 50
        assert config.items_per_page == 10
        assert config.max_display_items == 50
    
    def test_get_pagination_settings(self, ui_config):
        settings = ui_config.get_pagination_settings()
        assert settings['items_per_page'] == 5
        assert settings['max_display_items'] == 20
    
    def test_get_pagination_settings_with_override(self, ui_config):
        settings = ui_config.get_pagination_settings(items_per_page=10)
        assert settings['items_per_page'] == 10
        assert settings['max_display_items'] == 20
