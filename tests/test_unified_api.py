
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.api_modules.unified_api import UnifiedAPI
from src.vacancies.models import Vacancy


@pytest.fixture
def unified_api():
    """Фикстура для создания экземпляра UnifiedAPI"""
    with patch('src.api_modules.unified_api.HeadHunterAPI'), \
         patch('src.api_modules.unified_api.SuperJobAPI'), \
         patch('src.api_modules.unified_api.SuperJobParser'):
        return UnifiedAPI()


class TestUnifiedAPI:
    """Тесты для класса UnifiedAPI"""

    def test_init(self):
        """Тест инициализации UnifiedAPI"""
        with patch('src.api_modules.unified_api.HeadHunterAPI') as mock_hh, \
             patch('src.api_modules.unified_api.SuperJobAPI') as mock_sj, \
             patch('src.api_modules.unified_api.SuperJobParser') as mock_parser:
            
            api = UnifiedAPI()
            
            mock_hh.assert_called_once()
            mock_sj.assert_called_once() 
            mock_parser.assert_called_once()
            assert api.hh_api == mock_hh.return_value
            assert api.sj_api == mock_sj.return_value
            assert api.parser == mock_parser.return_value

    def test_deduplicate_cross_platform_empty_list(self, unified_api):
        """Тест дедупликации пустого списка"""
        result = unified_api._deduplicate_cross_platform([])
        assert result == []

    def test_deduplicate_cross_platform_single_vacancy(self, unified_api):
        """Тест дедупликации одной вакансии"""
        vacancy = {
            'name': 'Python Developer',
            'employer': {'name': 'Tech Corp'},
            'salary': {'from': 100000, 'to': 150000}
        }
        result = unified_api._deduplicate_cross_platform([vacancy])
        assert result == [vacancy]

    def test_deduplicate_cross_platform_no_duplicates(self, unified_api):
        """Тест дедупликации без дублей"""
        vacancies = [
            {
                'name': 'Python Developer',
                'employer': {'name': 'Tech Corp'},
                'salary': {'from': 100000, 'to': 150000}
            },
            {
                'name': 'Java Developer', 
                'employer': {'name': 'Other Corp'},
                'salary': {'from': 120000, 'to': 160000}
            }
        ]
        result = unified_api._deduplicate_cross_platform(vacancies)
        assert len(result) == 2

    def test_deduplicate_cross_platform_with_duplicates(self, unified_api):
        """Тест дедупликации с дублями"""
        vacancies = [
            {
                'name': 'Python Developer',
                'employer': {'name': 'Tech Corp'},
                'salary': {'from': 100000, 'to': 150000}
            },
            {
                'name': 'Python Developer',
                'employer': {'name': 'Tech Corp'}, 
                'salary': {'from': 100000, 'to': 150000}
            }
        ]
        result = unified_api._deduplicate_cross_platform(vacancies)
        assert len(result) == 1

    def test_deduplicate_cross_platform_hh_format(self, unified_api):
        """Тест дедупликации для формата HH"""
        vacancy = {
            'name': 'Python Developer',
            'employer': {'name': 'Tech Corp'},
            'salary': {'from': 100000, 'to': 150000}
        }
        result = unified_api._deduplicate_cross_platform([vacancy])
        assert len(result) == 1

    def test_deduplicate_cross_platform_sj_format(self, unified_api):
        """Тест дедупликации для формата SuperJob"""
        vacancy = {
            'profession': 'Python Developer',
            'firm_name': 'Tech Corp',
            'payment_from': 100000,
            'payment_to': 150000
        }
        result = unified_api._deduplicate_cross_platform([vacancy])
        assert len(result) == 1

    def test_deduplicate_cross_platform_mixed_formats(self, unified_api):
        """Тест дедупликации смешанных форматов"""
        vacancies = [
            {
                'name': 'Python Developer',
                'employer': {'name': 'Tech Corp'},
                'salary': {'from': 100000, 'to': 150000}
            },
            {
                'profession': 'Python Developer',
                'firm_name': 'Tech Corp', 
                'payment_from': 100000,
                'payment_to': 150000
            }
        ]
        result = unified_api._deduplicate_cross_platform(vacancies)
        assert len(result) == 1

    def test_deduplicate_cross_platform_no_salary(self, unified_api):
        """Тест дедупликации без зарплаты"""
        vacancy = {
            'name': 'Python Developer',
            'employer': {'name': 'Tech Corp'}
        }
        result = unified_api._deduplicate_cross_platform([vacancy])
        assert len(result) == 1

    def test_deduplicate_cross_platform_null_salary(self, unified_api):
        """Тест дедупликации с null зарплатой"""
        vacancy = {
            'name': 'Python Developer',
            'employer': {'name': 'Tech Corp'},
            'salary': None
        }
        result = unified_api._deduplicate_cross_platform([vacancy])
        assert len(result) == 1

    def test_get_vacancies_from_sources_default_sources(self, unified_api):
        """Тест получения вакансий с источниками по умолчанию"""
        unified_api.hh_api.get_vacancies_with_deduplication.return_value = []
        unified_api.sj_api.get_vacancies_with_deduplication.return_value = []
        
        with patch.object(unified_api, 'get_available_sources', return_value=['hh', 'sj']):
            result = unified_api.get_vacancies_from_sources('python')
            
        assert result == []

    def test_get_vacancies_from_sources_hh_only(self, unified_api):
        """Тест получения вакансий только с HH"""
        mock_vacancy_data = {
            'name': 'Python Developer',
            'employer': {'name': 'Tech Corp'},
            'salary': {'from': 100000, 'to': 150000}
        }
        
        unified_api.hh_api.get_vacancies_with_deduplication.return_value = [mock_vacancy_data]
        
        with patch('src.api_modules.unified_api.Vacancy') as mock_vacancy_class:
            mock_vacancy = Mock()
            mock_vacancy.to_dict.return_value = mock_vacancy_data
            mock_vacancy_class.from_dict.return_value = mock_vacancy
            
            result = unified_api.get_vacancies_from_sources('python', sources=['hh'])
            
        assert len(result) == 1

    def test_get_vacancies_from_sources_sj_only(self, unified_api):
        """Тест получения вакансий только с SuperJob"""
        mock_sj_data = {
            'profession': 'Python Developer',
            'firm_name': 'Tech Corp',
            'payment_from': 100000
        }
        
        unified_api.sj_api.get_vacancies_with_deduplication.return_value = [mock_sj_data]
        
        mock_sj_vacancy = Mock()
        unified_api.parser.parse_vacancies.return_value = [mock_sj_vacancy]
        
        mock_unified_data = {
            'name': 'Python Developer',
            'employer': {'name': 'Tech Corp'}
        }
        unified_api.parser.convert_to_unified_format.return_value = mock_unified_data
        
        with patch('src.api_modules.unified_api.Vacancy') as mock_vacancy_class:
            mock_vacancy = Mock()
            mock_vacancy.to_dict.return_value = mock_unified_data
            mock_vacancy_class.from_dict.return_value = mock_vacancy
            
            result = unified_api.get_vacancies_from_sources('python', sources=['sj'])
            
        assert len(result) == 1

    def test_get_vacancies_from_sources_both_sources(self, unified_api):
        """Тест получения вакансий с обоих источников"""
        mock_hh_data = {
            'name': 'Python Developer',
            'employer': {'name': 'Tech Corp'}
        }
        mock_sj_data = {
            'profession': 'Java Developer',
            'firm_name': 'Other Corp'
        }
        
        unified_api.hh_api.get_vacancies_with_deduplication.return_value = [mock_hh_data]
        unified_api.sj_api.get_vacancies_with_deduplication.return_value = [mock_sj_data]
        
        mock_sj_vacancy = Mock()
        unified_api.parser.parse_vacancies.return_value = [mock_sj_vacancy]
        
        mock_unified_sj_data = {
            'name': 'Java Developer',
            'employer': {'name': 'Other Corp'}
        }
        unified_api.parser.convert_to_unified_format.return_value = mock_unified_sj_data
        
        with patch('src.api_modules.unified_api.Vacancy') as mock_vacancy_class:
            mock_vacancy_hh = Mock()
            mock_vacancy_hh.to_dict.return_value = mock_hh_data
            mock_vacancy_sj = Mock()
            mock_vacancy_sj.to_dict.return_value = mock_unified_sj_data
            mock_vacancy_class.from_dict.side_effect = [mock_vacancy_hh, mock_vacancy_sj]
            
            result = unified_api.get_vacancies_from_sources('python', sources=['hh', 'sj'])
            
        assert len(result) == 2

    def test_get_vacancies_from_sources_hh_error(self, unified_api):
        """Тест обработки ошибки HH API"""
        unified_api.hh_api.get_vacancies_with_deduplication.side_effect = Exception("HH Error")
        unified_api.sj_api.get_vacancies_with_deduplication.return_value = []
        
        result = unified_api.get_vacancies_from_sources('python', sources=['hh', 'sj'])
        assert result == []

    def test_get_vacancies_from_sources_sj_error(self, unified_api):
        """Тест обработки ошибки SuperJob API"""
        unified_api.hh_api.get_vacancies_with_deduplication.return_value = []
        unified_api.sj_api.get_vacancies_with_deduplication.side_effect = Exception("SJ Error")
        
        result = unified_api.get_vacancies_from_sources('python', sources=['hh', 'sj'])
        assert result == []

    def test_get_vacancies_from_sources_sj_conversion_error(self, unified_api):
        """Тест обработки ошибки конвертации SuperJob"""
        mock_sj_data = {'profession': 'Python Developer'}
        unified_api.sj_api.get_vacancies_with_deduplication.return_value = [mock_sj_data]
        unified_api.hh_api.get_vacancies_with_deduplication.return_value = []
        
        mock_sj_vacancy = Mock()
        unified_api.parser.parse_vacancies.return_value = [mock_sj_vacancy]
        unified_api.parser.convert_to_unified_format.side_effect = Exception("Conversion Error")
        
        result = unified_api.get_vacancies_from_sources('python', sources=['sj'])
        assert result == []

    def test_get_vacancies_from_sources_period_mapping(self, unified_api):
        """Тест маппинга параметра period для SuperJob"""
        unified_api.hh_api.get_vacancies_with_deduplication.return_value = []
        unified_api.sj_api.get_vacancies_with_deduplication.return_value = []
        
        unified_api.get_vacancies_from_sources('python', sources=['sj'], period=7)
        
        unified_api.sj_api.get_vacancies_with_deduplication.assert_called_once_with('python', published=7)

    def test_get_hh_vacancies_success(self, unified_api):
        """Тест успешного получения вакансий HH"""
        mock_data = {'name': 'Python Developer'}
        unified_api.hh_api.get_vacancies_with_deduplication.return_value = [mock_data]
        
        with patch('src.api_modules.unified_api.Vacancy') as mock_vacancy_class:
            mock_vacancy = Mock()
            mock_vacancy_class.from_dict.return_value = mock_vacancy
            
            result = unified_api.get_hh_vacancies('python')
            
        assert result == [mock_vacancy]

    def test_get_hh_vacancies_error(self, unified_api):
        """Тест обработки ошибки при получении вакансий HH"""
        unified_api.hh_api.get_vacancies_with_deduplication.side_effect = Exception("HH Error")
        
        result = unified_api.get_hh_vacancies('python')
        assert result == []

    def test_get_sj_vacancies_success(self, unified_api):
        """Тест успешного получения вакансий SuperJob"""
        mock_sj_data = {'profession': 'Python Developer'}
        unified_api.sj_api.get_vacancies_with_deduplication.return_value = [mock_sj_data]
        
        mock_sj_vacancy = Mock()
        unified_api.parser.parse_vacancies.return_value = [mock_sj_vacancy]
        
        mock_unified_data = {'name': 'Python Developer'}
        unified_api.parser.convert_to_unified_format.return_value = mock_unified_data
        
        with patch('src.api_modules.unified_api.Vacancy') as mock_vacancy_class:
            mock_vacancy = Mock()
            mock_vacancy_class.from_dict.return_value = mock_vacancy
            
            result = unified_api.get_sj_vacancies('python')
            
        assert result == [mock_vacancy]

    def test_get_sj_vacancies_empty_data(self, unified_api):
        """Тест получения пустых данных от SuperJob"""
        unified_api.sj_api.get_vacancies_with_deduplication.return_value = []
        
        result = unified_api.get_sj_vacancies('python')
        assert result == []

    def test_get_sj_vacancies_error(self, unified_api):
        """Тест обработки ошибки при получении вакансий SuperJob"""
        unified_api.sj_api.get_vacancies_with_deduplication.side_effect = Exception("SJ Error")
        
        result = unified_api.get_sj_vacancies('python')
        assert result == []

    def test_get_sj_vacancies_conversion_error(self, unified_api):
        """Тест обработки ошибки конвертации SuperJob"""
        mock_sj_data = {'profession': 'Python Developer'}
        unified_api.sj_api.get_vacancies_with_deduplication.return_value = [mock_sj_data]
        
        mock_sj_vacancy = Mock()
        unified_api.parser.parse_vacancies.return_value = [mock_sj_vacancy]
        unified_api.parser.convert_to_unified_format.side_effect = Exception("Conversion Error")
        
        result = unified_api.get_sj_vacancies('python')
        assert result == []

    def test_get_sj_vacancies_period_mapping(self, unified_api):
        """Тест маппинга параметра period для SuperJob в get_sj_vacancies"""
        unified_api.sj_api.get_vacancies_with_deduplication.return_value = []
        
        unified_api.get_sj_vacancies('python', period=7)
        
        unified_api.sj_api.get_vacancies_with_deduplication.assert_called_once_with('python', published=7)

    def test_clear_cache_hh_only(self, unified_api):
        """Тест очистки кэша только HH"""
        unified_api.clear_cache({'hh': True, 'sj': False})
        
        unified_api.hh_api.clear_cache.assert_called_once_with('hh')
        unified_api.sj_api.clear_cache.assert_not_called()

    def test_clear_cache_sj_only(self, unified_api):
        """Тест очистки кэша только SuperJob"""
        unified_api.clear_cache({'hh': False, 'sj': True})
        
        unified_api.sj_api.clear_cache.assert_called_once_with('sj')
        unified_api.hh_api.clear_cache.assert_not_called()

    def test_clear_cache_both(self, unified_api):
        """Тест очистки кэша обеих API"""
        unified_api.clear_cache({'hh': True, 'sj': True})
        
        unified_api.hh_api.clear_cache.assert_called_once_with('hh')
        unified_api.sj_api.clear_cache.assert_called_once_with('sj')

    def test_clear_cache_neither(self, unified_api):
        """Тест без очистки кэша"""
        unified_api.clear_cache({'hh': False, 'sj': False})
        
        unified_api.hh_api.clear_cache.assert_not_called()
        unified_api.sj_api.clear_cache.assert_not_called()

    def test_clear_cache_error(self, unified_api):
        """Тест обработки ошибки при очистке кэша"""
        unified_api.hh_api.clear_cache.side_effect = Exception("Clear cache error")
        
        # Не должно вызывать исключение
        unified_api.clear_cache({'hh': True})

    def test_clear_all_cache_success(self, unified_api):
        """Тест успешной очистки всего кэша"""
        unified_api.clear_all_cache()
        
        unified_api.hh_api.clear_cache.assert_called_once_with('hh')
        unified_api.sj_api.clear_cache.assert_called_once_with('sj')

    def test_clear_all_cache_hh_error(self, unified_api):
        """Тест обработки ошибки при очистке кэша HH"""
        unified_api.hh_api.clear_cache.side_effect = Exception("HH cache error")
        
        unified_api.clear_all_cache()
        
        # SuperJob кэш все равно должен очиститься
        unified_api.sj_api.clear_cache.assert_called_once_with('sj')

    def test_clear_all_cache_sj_error(self, unified_api):
        """Тест обработки ошибки при очистке кэша SuperJob"""
        unified_api.sj_api.clear_cache.side_effect = Exception("SJ cache error")
        
        unified_api.clear_all_cache()
        
        # HH кэш все равно должен очиститься
        unified_api.hh_api.clear_cache.assert_called_once_with('hh')

    def test_get_available_sources(self, unified_api):
        """Тест получения доступных источников"""
        result = unified_api.get_available_sources()
        assert result == ['hh', 'sj']

    def test_validate_sources_valid(self, unified_api):
        """Тест валидации корректных источников"""
        result = unified_api.validate_sources(['hh', 'sj'])
        assert result == ['hh', 'sj']

    def test_validate_sources_partial_valid(self, unified_api):
        """Тест валидации частично корректных источников"""
        result = unified_api.validate_sources(['hh', 'invalid'])
        assert result == ['hh']

    def test_validate_sources_none_valid(self, unified_api):
        """Тест валидации некорректных источников"""
        with patch.object(unified_api, 'get_available_sources', return_value=['hh', 'sj']):
            result = unified_api.validate_sources(['invalid', 'also_invalid'])
            
        assert result == ['hh', 'sj']
