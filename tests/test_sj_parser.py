from unittest.mock import Mock, patch

from src.vacancies.models import Vacancy
from src.vacancies.parsers.sj_parser import SuperJobParser


class TestSuperJobParser:
    """Тесты для парсера SuperJob"""

    def test_parse_vacancies_success(self):
        """Тест успешного парсинга вакансий"""
        vacancies_data = [
            {
                'id': '123',
                'profession': 'Python Developer',
                'link': 'https://superjob.ru/test',
                'candidat': 'Python, Django',
                'work': 'Development'
            }
        ]
        
        result = SuperJobParser.parse_vacancies(vacancies_data)
        
        assert len(result) == 1
        assert isinstance(result[0], Vacancy)
        assert result[0].title == 'Python Developer'

    @patch('src.vacancies.parsers.sj_parser.logger')
    def test_parse_vacancies_with_value_error(self, mock_logger):
        """Тест обработки ValueError при парсинге"""
        vacancies_data = [
            {'invalid': 'data'}  # Неверная структура данных
        ]
        
        with patch('src.vacancies.models.Vacancy.from_dict', side_effect=ValueError("Test error")):
            result = SuperJobParser.parse_vacancies(vacancies_data)
        
        assert len(result) == 0
        mock_logger.warning.assert_called_once()

    @patch('src.vacancies.parsers.sj_parser.logger')
    def test_parse_vacancies_with_exception(self, mock_logger):
        """Тест обработки неожиданного исключения при парсинге"""
        vacancies_data = [
            {'id': '123', 'profession': 'Test'}
        ]
        
        with patch('src.vacancies.models.Vacancy.from_dict', side_effect=Exception("Unexpected error")):
            result = SuperJobParser.parse_vacancies(vacancies_data)
        
        assert len(result) == 0
        mock_logger.error.assert_called_once()

    @patch('src.vacancies.parsers.sj_parser.logger')
    def test_parse_vacancies_logs_info(self, mock_logger):
        """Тест логирования информации о парсинге"""
        vacancies_data = [
            {
                'id': '123',
                'profession': 'Python Developer',
                'link': 'https://superjob.ru/test'
            },
            {
                'id': '456',
                'profession': 'Java Developer',
                'link': 'https://superjob.ru/test2'
            }
        ]
        
        SuperJobParser.parse_vacancies(vacancies_data)
        
        mock_logger.info.assert_called_with("Успешно распарсено 2 вакансий SuperJob из 2")

    def test_convert_to_unified_format_with_salary(self):
        """Тест конвертации в унифицированный формат с зарплатой"""
        # Создаем mock объект зарплаты
        mock_salary = Mock()
        mock_salary.to_dict.return_value = {
            'from': 50000,
            'to': 100000,
            'currency': 'RUR',
            'period': 'месяц'
        }
        
        # Создаем mock вакансию
        sj_vacancy = Mock(spec=Vacancy)
        sj_vacancy.vacancy_id = '123'
        sj_vacancy.title = 'Python Developer'
        sj_vacancy.url = 'https://superjob.ru/test'
        sj_vacancy.salary = mock_salary
        sj_vacancy.description = 'Test description'
        sj_vacancy.requirements = 'Python, Django'
        sj_vacancy.employer = {'name': 'Test Company'}
        sj_vacancy.experience = 'От 1 года'
        sj_vacancy.employment = 'Полная занятость'
        sj_vacancy.schedule = 'Полный день'
        sj_vacancy.published_at = None
        sj_vacancy.detailed_description = 'Detailed description'
        sj_vacancy.benefits = 'Good benefits'
        sj_vacancy.source = 'superjob.ru'
        
        result = SuperJobParser.convert_to_unified_format(sj_vacancy)
        
        assert result['id'] == '123'
        assert result['name'] == 'Python Developer'
        assert result['title'] == 'Python Developer'
        assert result['url'] == 'https://superjob.ru/test'
        assert result['alternate_url'] == 'https://superjob.ru/test'
        assert result['salary']['period'] == 'месяц'
        assert result['description'] == 'Test description'
        assert result['requirements'] == 'Python, Django'
        assert result['responsibilities'] == 'Test description'
        assert result['employer'] == {'name': 'Test Company'}
        assert result['experience'] == 'От 1 года'
        assert result['employment'] == 'Полная занятость'
        assert result['schedule'] == 'Полный день'
        assert result['published_at'] is None
        assert result['skills'] == []
        assert result['keywords'] == []
        assert result['detailed_description'] == 'Detailed description'
        assert result['benefits'] == 'Good benefits'
        assert result['source'] == 'superjob.ru'

    def test_convert_to_unified_format_without_salary(self):
        """Тест конвертации в унифицированный формат без зарплаты"""
        # Создаем mock вакансию без зарплаты
        sj_vacancy = Mock(spec=Vacancy)
        sj_vacancy.vacancy_id = '456'
        sj_vacancy.title = 'Junior Developer'
        sj_vacancy.url = 'https://superjob.ru/test2'
        sj_vacancy.salary = None
        sj_vacancy.description = 'Junior position'
        sj_vacancy.requirements = 'Basic knowledge'
        sj_vacancy.employer = None
        sj_vacancy.experience = None
        sj_vacancy.employment = None
        sj_vacancy.schedule = None
        sj_vacancy.published_at = Mock()
        sj_vacancy.published_at.isoformat.return_value = '2023-01-01T10:00:00'
        sj_vacancy.detailed_description = None
        sj_vacancy.benefits = None
        sj_vacancy.source = 'superjob.ru'
        
        result = SuperJobParser.convert_to_unified_format(sj_vacancy)
        
        assert result['id'] == '456'
        assert result['salary'] is None
        assert result['published_at'] == '2023-01-01T10:00:00'
        assert result['employer'] is None
        assert result['experience'] is None
        assert result['employment'] is None
        assert result['schedule'] is None
        assert result['detailed_description'] is None
        assert result['benefits'] is None

    def test_convert_to_unified_format_with_month_period(self):
        """Тест конвертации с периодом 'month' в зарплате"""
        # Создаем mock объект зарплаты с периодом 'month'
        mock_salary = Mock()
        mock_salary.to_dict.return_value = {
            'from': 50000,
            'to': 100000,
            'currency': 'RUR',
            'period': 'month'
        }
        
        sj_vacancy = Mock(spec=Vacancy)
        sj_vacancy.vacancy_id = '789'
        sj_vacancy.title = 'Test'
        sj_vacancy.url = 'https://test.com'
        sj_vacancy.salary = mock_salary
        sj_vacancy.description = 'Test'
        sj_vacancy.requirements = 'Test'
        sj_vacancy.employer = None
        sj_vacancy.experience = None
        sj_vacancy.employment = None
        sj_vacancy.schedule = None
        sj_vacancy.published_at = None
        sj_vacancy.detailed_description = None
        sj_vacancy.benefits = None
        sj_vacancy.source = 'superjob.ru'
        
        result = SuperJobParser.convert_to_unified_format(sj_vacancy)
        
        assert result['salary']['period'] == 'месяц'
