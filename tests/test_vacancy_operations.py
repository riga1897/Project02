
import pytest
from unittest.mock import Mock, patch
from src.utils.vacancy_operations import VacancyOperations
from src.vacancies.models import Vacancy
from src.utils.salary import Salary


class TestVacancyOperations:
    """Тесты для класса VacancyOperations"""

    @pytest.fixture
    def vacancies_with_salary(self):
        """Фикстура с вакансиями, имеющими зарплату"""
        vacancy1 = Mock(spec=Vacancy)
        vacancy1.salary = Mock(spec=Salary)
        vacancy1.salary.salary_from = 100000
        vacancy1.salary.salary_to = 150000
        vacancy1.salary.get_max_salary.return_value = 150000
        vacancy1.salary.average = 125000
        
        vacancy2 = Mock(spec=Vacancy)
        vacancy2.salary = Mock(spec=Salary)
        vacancy2.salary.salary_from = 80000
        vacancy2.salary.salary_to = 120000
        vacancy2.salary.get_max_salary.return_value = 120000
        vacancy2.salary.average = 100000
        
        vacancy3 = Mock(spec=Vacancy)
        vacancy3.salary = Mock(spec=Salary)
        vacancy3.salary.salary_from = 200000
        vacancy3.salary.salary_to = None
        vacancy3.salary.get_max_salary.return_value = 200000
        vacancy3.salary.average = 200000
        
        return [vacancy1, vacancy2, vacancy3]

    @pytest.fixture
    def vacancies_without_salary(self):
        """Фикстура с вакансиями без зарплаты"""
        vacancy1 = Mock(spec=Vacancy)
        vacancy1.salary = None
        
        vacancy2 = Mock(spec=Vacancy)
        vacancy2.salary = Mock(spec=Salary)
        vacancy2.salary.salary_from = None
        vacancy2.salary.salary_to = None
        
        return [vacancy1, vacancy2]

    def test_get_vacancies_with_salary(self, vacancies_with_salary, vacancies_without_salary):
        """Тест фильтрации вакансий с указанной зарплатой"""
        all_vacancies = vacancies_with_salary + vacancies_without_salary
        
        result = VacancyOperations.get_vacancies_with_salary(all_vacancies)
        
        assert len(result) == 3
        assert all(v.salary and (v.salary.salary_from or v.salary.salary_to) for v in result)

    def test_sort_vacancies_by_salary_descending(self, vacancies_with_salary):
        """Тест сортировки вакансий по зарплате по убыванию"""
        result = VacancyOperations.sort_vacancies_by_salary(vacancies_with_salary, reverse=True)
        
        assert len(result) == 3
        # Проверяем порядок по убыванию
        max_salaries = [v.salary.get_max_salary() for v in result]
        assert max_salaries == sorted(max_salaries, reverse=True)

    def test_sort_vacancies_by_salary_ascending(self, vacancies_with_salary):
        """Тест сортировки вакансий по зарплате по возрастанию"""
        result = VacancyOperations.sort_vacancies_by_salary(vacancies_with_salary, reverse=False)
        
        assert len(result) == 3
        # Проверяем порядок по возрастанию
        max_salaries = [v.salary.get_max_salary() for v in result]
        assert max_salaries == sorted(max_salaries)

    def test_sort_vacancies_with_none_salary(self):
        """Тест сортировки вакансий с None зарплатой"""
        vacancy_with_none = Mock(spec=Vacancy)
        vacancy_with_none.salary = None
        
        vacancy_with_salary = Mock(spec=Vacancy)
        vacancy_with_salary.salary = Mock(spec=Salary)
        vacancy_with_salary.salary.get_max_salary.return_value = 100000
        
        vacancies = [vacancy_with_none, vacancy_with_salary]
        result = VacancyOperations.sort_vacancies_by_salary(vacancies)
        
        assert len(result) == 2

    def test_filter_vacancies_by_min_salary_with_from_only(self):
        """Тест фильтрации по минимальной зарплате (только нижняя граница)"""
        vacancy = Mock(spec=Vacancy)
        vacancy.salary = Mock(spec=Salary)
        vacancy.salary.salary_from = 120000
        vacancy.salary.salary_to = None
        
        result = VacancyOperations.filter_vacancies_by_min_salary([vacancy], 100000)
        assert len(result) == 1
        
        result = VacancyOperations.filter_vacancies_by_min_salary([vacancy], 150000)
        assert len(result) == 0

    def test_filter_vacancies_by_min_salary_with_to_only(self):
        """Тест фильтрации по минимальной зарплате (только верхняя граница)"""
        vacancy = Mock(spec=Vacancy)
        vacancy.salary = Mock(spec=Salary)
        vacancy.salary.salary_from = None
        vacancy.salary.salary_to = 120000
        
        result = VacancyOperations.filter_vacancies_by_min_salary([vacancy], 100000)
        assert len(result) == 1
        
        result = VacancyOperations.filter_vacancies_by_min_salary([vacancy], 150000)
        assert len(result) == 0

    def test_filter_vacancies_by_min_salary_with_both_bounds(self):
        """Тест фильтрации по минимальной зарплате (обе границы)"""
        vacancy = Mock(spec=Vacancy)
        vacancy.salary = Mock(spec=Salary)
        vacancy.salary.salary_from = 120000
        vacancy.salary.salary_to = 150000
        
        result = VacancyOperations.filter_vacancies_by_min_salary([vacancy], 100000)
        assert len(result) == 1
        
        result = VacancyOperations.filter_vacancies_by_min_salary([vacancy], 130000)
        assert len(result) == 0

    def test_filter_vacancies_by_min_salary_no_salary(self):
        """Тест фильтрации по минимальной зарплате без зарплаты"""
        vacancy = Mock(spec=Vacancy)
        vacancy.salary = None
        
        result = VacancyOperations.filter_vacancies_by_min_salary([vacancy], 100000)
        assert len(result) == 0

    def test_filter_vacancies_by_max_salary_with_from_only(self):
        """Тест фильтрации по максимальной зарплате (только нижняя граница)"""
        vacancy = Mock(spec=Vacancy)
        vacancy.salary = Mock(spec=Salary)
        vacancy.salary.salary_from = 80000
        vacancy.salary.salary_to = None
        
        result = VacancyOperations.filter_vacancies_by_max_salary([vacancy], 100000)
        assert len(result) == 1
        
        result = VacancyOperations.filter_vacancies_by_max_salary([vacancy], 70000)
        assert len(result) == 0

    def test_filter_vacancies_by_max_salary_with_to_only(self):
        """Тест фильтрации по максимальной зарплате (только верхняя граница)"""
        vacancy = Mock(spec=Vacancy)
        vacancy.salary = Mock(spec=Salary)
        vacancy.salary.salary_from = None
        vacancy.salary.salary_to = 120000
        
        result = VacancyOperations.filter_vacancies_by_max_salary([vacancy], 150000)
        assert len(result) == 1
        
        result = VacancyOperations.filter_vacancies_by_max_salary([vacancy], 100000)
        assert len(result) == 0

    def test_filter_vacancies_by_max_salary_with_both_bounds(self):
        """Тест фильтрации по максимальной зарплате (обе границы)"""
        vacancy = Mock(spec=Vacancy)
        vacancy.salary = Mock(spec=Salary)
        vacancy.salary.salary_from = 80000
        vacancy.salary.salary_to = 120000
        
        result = VacancyOperations.filter_vacancies_by_max_salary([vacancy], 150000)
        assert len(result) == 1
        
        result = VacancyOperations.filter_vacancies_by_max_salary([vacancy], 100000)
        assert len(result) == 0

    def test_filter_vacancies_by_salary_range_from_in_range(self):
        """Тест фильтрации по диапазону зарплат (нижняя граница в диапазоне)"""
        vacancy = Mock(spec=Vacancy)
        vacancy.salary = Mock(spec=Salary)
        vacancy.salary.salary_from = 120000
        vacancy.salary.salary_to = 180000
        
        result = VacancyOperations.filter_vacancies_by_salary_range([vacancy], 100000, 150000)
        assert len(result) == 1

    def test_filter_vacancies_by_salary_range_to_in_range(self):
        """Тест фильтрации по диапазону зарплат (верхняя граница в диапазоне)"""
        vacancy = Mock(spec=Vacancy)
        vacancy.salary = Mock(spec=Salary)
        vacancy.salary.salary_from = 80000
        vacancy.salary.salary_to = 120000
        
        result = VacancyOperations.filter_vacancies_by_salary_range([vacancy], 100000, 150000)
        assert len(result) == 1

    def test_filter_vacancies_by_salary_range_overlap(self):
        """Тест фильтрации по диапазону зарплат (пересечение диапазонов)"""
        vacancy = Mock(spec=Vacancy)
        vacancy.salary = Mock(spec=Salary)
        vacancy.salary.salary_from = 80000
        vacancy.salary.salary_to = 180000
        
        result = VacancyOperations.filter_vacancies_by_salary_range([vacancy], 100000, 150000)
        assert len(result) == 1

    def test_filter_vacancies_by_salary_range_no_overlap(self):
        """Тест фильтрации по диапазону зарплат (нет пересечения)"""
        vacancy = Mock(spec=Vacancy)
        vacancy.salary = Mock(spec=Salary)
        vacancy.salary.salary_from = 200000
        vacancy.salary.salary_to = 250000
        
        result = VacancyOperations.filter_vacancies_by_salary_range([vacancy], 100000, 150000)
        assert len(result) == 0

    @patch('src.utils.vacancy_operations.filter_vacancies_by_keyword')
    def test_filter_vacancies_by_multiple_keywords_empty_list(self, mock_filter):
        """Тест фильтрации по множественным ключевым словам с пустым списком"""
        vacancies = [Mock(spec=Vacancy)]
        
        result = VacancyOperations.filter_vacancies_by_multiple_keywords(vacancies, [])
        
        assert result == vacancies
        mock_filter.assert_not_called()

    @patch('src.utils.vacancy_operations.filter_vacancies_by_keyword')
    def test_filter_vacancies_by_multiple_keywords_with_matches(self, mock_filter):
        """Тест фильтрации по множественным ключевым словам с совпадениями"""
        vacancy1 = Mock(spec=Vacancy)
        vacancy2 = Mock(spec=Vacancy)
        vacancies = [vacancy1, vacancy2]
        
        # Настраиваем mock чтобы первое ключевое слово находило первую вакансию,
        # второе - обе вакансии
        def side_effect(vacs, keyword):
            if keyword == "python":
                return [vacancy1] if vacancy1 in vacs else []
            elif keyword == "developer":
                return vacs
            return []
        
        mock_filter.side_effect = side_effect
        
        result = VacancyOperations.filter_vacancies_by_multiple_keywords(vacancies, ["python", "developer"])
        
        assert len(result) == 2
        # Проверяем, что вакансии отсортированы по количеству совпадений
        assert hasattr(result[0], '_keyword_matches')
        assert hasattr(result[1], '_keyword_matches')

    @patch('src.utils.vacancy_operations.vacancy_contains_keyword')
    def test_search_vacancies_advanced_and_operator(self, mock_contains):
        """Тест продвинутого поиска с оператором AND"""
        vacancy1 = Mock(spec=Vacancy)
        vacancy2 = Mock(spec=Vacancy)
        vacancies = [vacancy1, vacancy2]
        
        # Первая вакансия содержит оба ключевых слова, вторая - только одно
        def side_effect(vacancy, keyword):
            if vacancy == vacancy1:
                return True
            elif vacancy == vacancy2 and keyword == "python":
                return True
            return False
        
        mock_contains.side_effect = side_effect
        
        result = VacancyOperations.search_vacancies_advanced(vacancies, "python AND django")
        
        assert len(result) == 1
        assert result[0] == vacancy1

    @patch('src.utils.vacancy_operations.VacancyOperations.filter_vacancies_by_multiple_keywords')
    def test_search_vacancies_advanced_or_operator(self, mock_filter):
        """Тест продвинутого поиска с оператором OR"""
        vacancies = [Mock(spec=Vacancy)]
        mock_filter.return_value = vacancies
        
        result = VacancyOperations.search_vacancies_advanced(vacancies, "python OR django")
        
        mock_filter.assert_called_once_with(vacancies, ["python", "django"])
        assert result == vacancies

    @patch('src.utils.vacancy_operations.VacancyOperations.filter_vacancies_by_multiple_keywords')
    def test_search_vacancies_advanced_comma_separator(self, mock_filter):
        """Тест продвинутого поиска с запятой как разделителем"""
        vacancies = [Mock(spec=Vacancy)]
        mock_filter.return_value = vacancies
        
        result = VacancyOperations.search_vacancies_advanced(vacancies, "python, django, flask")
        
        mock_filter.assert_called_once_with(vacancies, ["python", "django", "flask"])
        assert result == vacancies

    @patch('src.utils.vacancy_operations.VacancyOperations.filter_vacancies_by_multiple_keywords')
    def test_search_vacancies_advanced_space_separator(self, mock_filter):
        """Тест продвинутого поиска с пробелом как разделителем"""
        vacancies = [Mock(spec=Vacancy)]
        mock_filter.return_value = vacancies
        
        result = VacancyOperations.search_vacancies_advanced(vacancies, "python django flask")
        
        mock_filter.assert_called_once_with(vacancies, ["python", "django", "flask"])
        assert result == vacancies

    @patch('src.utils.vacancy_operations.filter_vacancies_by_keyword')
    def test_search_vacancies_advanced_single_keyword(self, mock_filter):
        """Тест продвинутого поиска с одним ключевым словом"""
        vacancies = [Mock(spec=Vacancy)]
        mock_filter.return_value = vacancies
        
        result = VacancyOperations.search_vacancies_advanced(vacancies, "python")
        
        mock_filter.assert_called_once_with(vacancies, "python")
        assert result == vacancies

    @patch('builtins.print')
    def test_debug_vacancy_search(self, mock_print):
        """Тест отладочной функции поиска по вакансии"""
        vacancy = Mock(spec=Vacancy)
        vacancy.title = "Python Developer"
        vacancy.employer = "Test Company"
        vacancy.url = "http://test.com"
        vacancy.description = "Python development position"
        vacancy.requirements = "Python experience required"
        vacancy.responsibilities = "Develop applications"
        
        VacancyOperations.debug_vacancy_search(vacancy, "python")
        
        # Проверяем, что print был вызван
        assert mock_print.called

    @patch('builtins.print')
    def test_debug_vacancy_keywords(self, mock_print):
        """Тест отладочной функции ключевых слов"""
        vacancy = Mock(spec=Vacancy)
        vacancy.title = "Python Developer"
        vacancy.url = "http://test.com"
        vacancy.description = "Excel and Python development"
        vacancy.requirements = "1C experience"
        vacancy.responsibilities = "R analytics"
        
        VacancyOperations.debug_vacancy_keywords(vacancy)
        
        # Проверяем, что print был вызван
        assert mock_print.called
