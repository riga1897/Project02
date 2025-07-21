
import pytest
from unittest.mock import MagicMock, patch
from typing import List, Dict

from src.api_modules.base_api import BaseJobAPI


class ConcreteAPI(BaseJobAPI):
    """Конкретная реализация BaseJobAPI для тестирования"""
    
    def get_vacancies(self, search_query: str, **kwargs) -> List[Dict]:
        """Реализация абстрактного метода для тестов"""
        return [{"name": "Test Vacancy", "employer": {"name": "Test Company"}}]
    
    def _validate_vacancy(self, vacancy: Dict) -> bool:
        """Реализация абстрактного метода для тестов"""
        return "name" in vacancy


class TestBaseJobAPI:
    """Тесты для BaseJobAPI"""
    
    def setup_method(self):
        """Настройка для каждого теста"""
        self.api = ConcreteAPI()
    
    def test_create_dedup_key_hh_source(self):
        """Тест создания ключа дедупликации для HH"""
        vacancy = {
            "name": "Python Developer",
            "employer": {"name": "Tech Company"},
            "salary": {"from": 100000, "to": 150000}
        }
        
        key = BaseJobAPI._create_dedup_key(vacancy, "hh")
        
        assert key == ("python developer", "tech company", "100000-150000")
    
    def test_create_dedup_key_hh_no_salary(self):
        """Тест создания ключа дедупликации для HH без зарплаты"""
        vacancy = {
            "name": "Python Developer",
            "employer": {"name": "Tech Company"},
            "salary": None
        }
        
        key = BaseJobAPI._create_dedup_key(vacancy, "hh")
        
        assert key == ("python developer", "tech company", "")
    
    def test_create_dedup_key_hh_empty_salary(self):
        """Тест создания ключа дедупликации для HH с пустой зарплатой"""
        vacancy = {
            "name": "Python Developer",
            "employer": {"name": "Tech Company"},
            "salary": {"from": None, "to": None}
        }
        
        key = BaseJobAPI._create_dedup_key(vacancy, "hh")
        
        assert key == ("python developer", "tech company", "0-0")
    
    def test_create_dedup_key_sj_source(self):
        """Тест создания ключа дедупликации для SuperJob"""
        vacancy = {
            "profession": "Python Developer",
            "firm_name": "Tech Company",
            "payment_from": 100000,
            "payment_to": 150000
        }
        
        key = BaseJobAPI._create_dedup_key(vacancy, "sj")
        
        assert key == ("python developer", "tech company", "100000-150000")
    
    def test_create_dedup_key_sj_no_payment(self):
        """Тест создания ключа дедупликации для SuperJob без зарплаты"""
        vacancy = {
            "profession": "Python Developer",
            "firm_name": "Tech Company"
        }
        
        key = BaseJobAPI._create_dedup_key(vacancy, "sj")
        
        assert key == ("python developer", "tech company", "0-0")
    
    def test_create_dedup_key_unknown_source(self):
        """Тест создания ключа дедупликации для неизвестного источника"""
        vacancy = {
            "title": "Python Developer",
            "employer": {"name": "Tech Company"}
        }
        
        key = BaseJobAPI._create_dedup_key(vacancy, "unknown")
        
        assert key == ("python developer", "tech company", "0-0")
    
    def test_create_dedup_key_fallback_fields(self):
        """Тест создания ключа дедупликации с fallback полями"""
        vacancy = {
            "profession": "Python Developer",
            "firm_name": "Tech Company"
        }
        
        key = BaseJobAPI._create_dedup_key(vacancy, "unknown")
        
        assert key == ("python developer", "tech company", "0-0")
    
    def test_create_dedup_key_empty_fields(self):
        """Тест создания ключа дедупликации с пустыми полями"""
        vacancy = {}
        
        key = BaseJobAPI._create_dedup_key(vacancy, "hh")
        
        assert key == ("", "", "")
    
    @patch('src.api_modules.base_api.logger')
    def test_deduplicate_vacancies_removes_duplicates(self, mock_logger):
        """Тест дедупликации с удалением дублей"""
        vacancies = [
            {"name": "Python Developer", "employer": {"name": "Tech Co"}, "salary": {"from": 100000, "to": 150000}},
            {"name": "Python Developer", "employer": {"name": "Tech Co"}, "salary": {"from": 100000, "to": 150000}},
            {"name": "Java Developer", "employer": {"name": "Other Co"}, "salary": {"from": 120000, "to": 160000}}
        ]
        
        unique_vacancies = self.api._deduplicate_vacancies(vacancies, "hh")
        
        assert len(unique_vacancies) == 2
        assert unique_vacancies[0]["name"] == "Python Developer"
        assert unique_vacancies[1]["name"] == "Java Developer"
        
        # Проверяем, что логирование было вызвано
        mock_logger.debug.assert_called()
        mock_logger.info.assert_called_with("HH дедупликация: 3 -> 2 вакансий")
    
    @patch('src.api_modules.base_api.logger')
    def test_deduplicate_vacancies_no_duplicates(self, mock_logger):
        """Тест дедупликации без дублей"""
        vacancies = [
            {"name": "Python Developer", "employer": {"name": "Tech Co"}, "salary": {"from": 100000, "to": 150000}},
            {"name": "Java Developer", "employer": {"name": "Other Co"}, "salary": {"from": 120000, "to": 160000}}
        ]
        
        unique_vacancies = self.api._deduplicate_vacancies(vacancies, "hh")
        
        assert len(unique_vacancies) == 2
        mock_logger.info.assert_called_with("HH дедупликация: 2 -> 2 вакансий")
    
    @patch('src.api_modules.base_api.logger')
    def test_deduplicate_vacancies_empty_list(self, mock_logger):
        """Тест дедупликации пустого списка"""
        vacancies = []
        
        unique_vacancies = self.api._deduplicate_vacancies(vacancies, "sj")
        
        assert len(unique_vacancies) == 0
        mock_logger.info.assert_called_with("SJ дедупликация: 0 -> 0 вакансий")
    
    @patch('src.api_modules.base_api.logger')
    def test_deduplicate_vacancies_sj_source(self, mock_logger):
        """Тест дедупликации для SuperJob"""
        vacancies = [
            {"profession": "Python Developer", "firm_name": "Tech Co", "payment_from": 100000, "payment_to": 150000},
            {"profession": "Python Developer", "firm_name": "Tech Co", "payment_from": 100000, "payment_to": 150000}
        ]
        
        unique_vacancies = self.api._deduplicate_vacancies(vacancies, "sj")
        
        assert len(unique_vacancies) == 1
        mock_logger.info.assert_called_with("SJ дедупликация: 2 -> 1 вакансий")
    
    def test_abstract_methods_require_implementation(self):
        """Тест того, что абстрактные методы требуют реализации"""
        with pytest.raises(TypeError):
            BaseJobAPI()
    
    def test_concrete_implementation_works(self):
        """Тест работы конкретной реализации"""
        api = ConcreteAPI()
        
        vacancies = api.get_vacancies("Python")
        assert len(vacancies) == 1
        assert vacancies[0]["name"] == "Test Vacancy"
        
        is_valid = api._validate_vacancy({"name": "Test"})
        assert is_valid is True
        
        is_invalid = api._validate_vacancy({"title": "Test"})
        assert is_invalid is False
