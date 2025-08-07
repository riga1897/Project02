from unittest.mock import Mock

from src.utils.search_utils import filter_vacancies_by_keyword, vacancy_contains_keyword
from src.vacancies.models import Vacancy


class TestFilterVacanciesByKeyword:
    """Тест функции filter_vacancies_by_keyword"""

    @staticmethod
    def create_mock_vacancy(**kwargs):
        """Создание мок-объекта вакансии с заданными атрибутами"""
        vacancy = Mock(spec=Vacancy)
        # Устанавливаем значения по умолчанию
        vacancy.vacancy_id = kwargs.get("vacancy_id", "123")
        vacancy.title = kwargs.get("title", "")
        vacancy.requirements = kwargs.get("requirements", "")
        vacancy.responsibilities = kwargs.get("responsibilities", "")
        vacancy.description = kwargs.get("description", "")
        vacancy.detailed_description = kwargs.get("detailed_description", "")
        vacancy.skills = kwargs.get("skills", [])
        vacancy.employer = kwargs.get("employer", {})
        vacancy.employment = kwargs.get("employment", "")
        vacancy.schedule = kwargs.get("schedule", "")
        vacancy.experience = kwargs.get("experience", "")
        vacancy.benefits = kwargs.get("benefits", "")
        return vacancy

    def test_filter_by_vacancy_id(self):
        """Тест фильтрации по ID вакансии"""
        vacancy1 = self.create_mock_vacancy(vacancy_id="python123")
        vacancy2 = self.create_mock_vacancy(vacancy_id="java456")

        result = filter_vacancies_by_keyword([vacancy1, vacancy2], "python")

        assert len(result) == 1
        assert result[0].vacancy_id == "python123"
        assert result[0]._relevance_score == 15

    def test_filter_by_title(self):
        """Тест фильтрации по заголовку"""
        vacancy1 = self.create_mock_vacancy(title="Python Developer")
        vacancy2 = self.create_mock_vacancy(title="Java Developer")

        result = filter_vacancies_by_keyword([vacancy1, vacancy2], "python")

        assert len(result) == 1
        assert result[0].title == "Python Developer"
        assert result[0]._relevance_score == 10

    def test_filter_by_requirements(self):
        """Тест фильтрации по требованиям"""
        vacancy1 = self.create_mock_vacancy(requirements="Python, Django")
        vacancy2 = self.create_mock_vacancy(requirements="Java, Spring")

        result = filter_vacancies_by_keyword([vacancy1, vacancy2], "python")

        assert len(result) == 1
        assert result[0]._relevance_score == 5

    def test_filter_by_responsibilities(self):
        """Тест фильтрации по обязанностям"""
        vacancy1 = self.create_mock_vacancy(responsibilities="Develop Python applications")
        vacancy2 = self.create_mock_vacancy(responsibilities="Develop Java applications")

        result = filter_vacancies_by_keyword([vacancy1, vacancy2], "python")

        assert len(result) == 1
        assert result[0]._relevance_score == 5

    def test_filter_by_description(self):
        """Тест фильтрации по описанию"""
        vacancy1 = self.create_mock_vacancy(description="We need Python developer")
        vacancy2 = self.create_mock_vacancy(description="We need Java developer")

        result = filter_vacancies_by_keyword([vacancy1, vacancy2], "python")

        assert len(result) == 1
        assert result[0]._relevance_score == 3

    def test_filter_by_detailed_description(self):
        """Тест фильтрации по детальному описанию"""
        vacancy1 = self.create_mock_vacancy(detailed_description="Python is required")
        vacancy2 = self.create_mock_vacancy(detailed_description="Java is required")

        result = filter_vacancies_by_keyword([vacancy1, vacancy2], "python")

        assert len(result) == 1
        assert result[0]._relevance_score == 4

    def test_filter_by_skills_dict(self):
        """Тест фильтрации по навыкам (словари)"""
        vacancy1 = self.create_mock_vacancy(skills=[{"name": "Python"}, {"name": "Django"}])
        vacancy2 = self.create_mock_vacancy(skills=[{"name": "Java"}, {"name": "Spring"}])

        result = filter_vacancies_by_keyword([vacancy1, vacancy2], "python")

        assert len(result) == 1
        assert result[0]._relevance_score == 6

    def test_filter_by_skills_string(self):
        """Тест фильтрации по навыкам (строки)"""
        vacancy1 = self.create_mock_vacancy(skills=["Python", "Django"])
        vacancy2 = self.create_mock_vacancy(skills=["Java", "Spring"])

        result = filter_vacancies_by_keyword([vacancy1, vacancy2], "python")

        assert len(result) == 1
        assert result[0]._relevance_score == 6

    def test_filter_by_employer_name(self):
        """Тест фильтрации по имени работодателя"""
        vacancy1 = self.create_mock_vacancy(employer={"name": "Python Corp"})
        vacancy2 = self.create_mock_vacancy(employer={"name": "Java Inc"})

        result = filter_vacancies_by_keyword([vacancy1, vacancy2], "python")

        assert len(result) == 1
        assert result[0]._relevance_score == 4

    def test_filter_by_employment(self):
        """Тест фильтрации по типу занятости"""
        vacancy1 = self.create_mock_vacancy(employment="Python developer full-time")
        vacancy2 = self.create_mock_vacancy(employment="Java developer part-time")

        result = filter_vacancies_by_keyword([vacancy1, vacancy2], "python")

        assert len(result) == 1
        assert result[0]._relevance_score == 3

    def test_filter_by_schedule(self):
        """Тест фильтрации по графику работы"""
        vacancy1 = self.create_mock_vacancy(schedule="Python projects schedule")
        vacancy2 = self.create_mock_vacancy(schedule="Java projects schedule")

        result = filter_vacancies_by_keyword([vacancy1, vacancy2], "python")

        assert len(result) == 1
        assert result[0]._relevance_score == 3

    def test_filter_by_experience(self):
        """Тест фильтрации по опыту работы"""
        vacancy1 = self.create_mock_vacancy(experience="Python experience required")
        vacancy2 = self.create_mock_vacancy(experience="Java experience required")

        result = filter_vacancies_by_keyword([vacancy1, vacancy2], "python")

        assert len(result) == 1
        assert result[0]._relevance_score == 3

    def test_filter_by_benefits(self):
        """Тест фильтрации по льготам"""
        vacancy1 = self.create_mock_vacancy(benefits="Python training provided")
        vacancy2 = self.create_mock_vacancy(benefits="Java training provided")

        result = filter_vacancies_by_keyword([vacancy1, vacancy2], "python")

        assert len(result) == 1
        assert result[0]._relevance_score == 2

    def test_multiple_matches_scoring(self):
        """Тест суммирования баллов при множественных совпадениях"""
        vacancy = self.create_mock_vacancy(
            title="Python Developer", requirements="Python, Django", description="Python development"
        )

        result = filter_vacancies_by_keyword([vacancy], "python")

        assert len(result) == 1
        assert result[0]._relevance_score == 18  # 10 + 5 + 3

    def test_case_insensitive_search(self):
        """Тест регистронезависимого поиска"""
        vacancy = self.create_mock_vacancy(title="PYTHON Developer")

        result = filter_vacancies_by_keyword([vacancy], "python")

        assert len(result) == 1

    def test_empty_vacancies_list(self):
        """Тест с пустым списком вакансий"""
        result = filter_vacancies_by_keyword([], "python")

        assert result == []

    def test_no_matches(self):
        """Тест без совпадений"""
        vacancy = self.create_mock_vacancy(title="Java Developer")

        result = filter_vacancies_by_keyword([vacancy], "python")

        assert result == []

    def test_sorting_by_relevance(self):
        """Тест сортировки по релевантности"""
        vacancy1 = self.create_mock_vacancy(title="Python Developer")  # score 10
        vacancy2 = self.create_mock_vacancy(vacancy_id="python123")  # score 15
        vacancy3 = self.create_mock_vacancy(description="Python dev")  # score 3

        result = filter_vacancies_by_keyword([vacancy1, vacancy2, vacancy3], "python")

        assert len(result) == 3
        assert result[0].vacancy_id == "python123"  # highest score first
        assert result[1].title == "Python Developer"
        assert result[2].description == "Python dev"

    def test_none_values_handling(self):
        """Тест обработки None значений"""
        vacancy = self.create_mock_vacancy()
        vacancy.title = None
        vacancy.requirements = None
        vacancy.responsibilities = None
        vacancy.description = None
        vacancy.detailed_description = None
        vacancy.skills = None
        vacancy.employer = None
        vacancy.employment = None
        vacancy.schedule = None
        vacancy.experience = None
        vacancy.benefits = None

        result = filter_vacancies_by_keyword([vacancy], "python")

        assert result == []


class TestVacancyContainsKeyword:
    """Тест функции vacancy_contains_keyword"""

    @staticmethod
    def create_mock_vacancy(**kwargs):
        """Создание мок-объекта вакансии"""
        vacancy = Mock(spec=Vacancy)
        vacancy.title = kwargs.get("title", "")
        vacancy.requirements = kwargs.get("requirements", "")
        vacancy.responsibilities = kwargs.get("responsibilities", "")
        vacancy.description = kwargs.get("description", "")
        vacancy.detailed_description = kwargs.get("detailed_description", "")
        vacancy.skills = kwargs.get("skills", [])
        vacancy.profession = kwargs.get("profession", "")
        return vacancy

    def test_contains_in_title(self):
        """Тест поиска в заголовке"""
        vacancy = self.create_mock_vacancy(title="Python Developer")

        assert vacancy_contains_keyword(vacancy, "python") is True

    def test_contains_in_requirements(self):
        """Тест поиска в требованиях"""
        vacancy = self.create_mock_vacancy(requirements="Python experience")

        assert vacancy_contains_keyword(vacancy, "python") is True

    def test_contains_in_responsibilities(self):
        """Тест поиска в обязанностях"""
        vacancy = self.create_mock_vacancy(responsibilities="Develop Python apps")

        assert vacancy_contains_keyword(vacancy, "python") is True

    def test_contains_in_description(self):
        """Тест поиска в описании"""
        vacancy = self.create_mock_vacancy(description="We need Python developer")

        assert vacancy_contains_keyword(vacancy, "python") is True

    def test_contains_in_detailed_description(self):
        """Тест поиска в детальном описании"""
        vacancy = self.create_mock_vacancy(detailed_description="Python required")

        assert vacancy_contains_keyword(vacancy, "python") is True

    def test_contains_in_profession(self):
        """Тест поиска в профессии (для SuperJob)"""
        vacancy = self.create_mock_vacancy(profession="Python Developer")

        assert vacancy_contains_keyword(vacancy, "python") is True

    def test_contains_in_skills_dict(self):
        """Тест поиска в навыках (словари)"""
        vacancy = self.create_mock_vacancy(skills=[{"name": "Python"}, {"name": "Django"}])

        assert vacancy_contains_keyword(vacancy, "python") is True

    def test_not_contains_keyword(self):
        """Тест отсутствия ключевого слова"""
        vacancy = self.create_mock_vacancy(title="Java Developer")

        assert vacancy_contains_keyword(vacancy, "python") is False

    def test_case_insensitive_search(self):
        """Тест регистронезависимого поиска"""
        vacancy = self.create_mock_vacancy(title="PYTHON Developer")

        assert vacancy_contains_keyword(vacancy, "python") is True

    def test_none_values_handling(self):
        """Тест обработки None значений"""
        vacancy = self.create_mock_vacancy()
        vacancy.title = None
        vacancy.requirements = None
        vacancy.responsibilities = None
        vacancy.description = None
        vacancy.detailed_description = None
        vacancy.skills = None

        # Добавляем атрибут profession для теста hasattr
        vacancy.profession = None

        assert vacancy_contains_keyword(vacancy, "python") is False

    def test_missing_profession_attribute(self):
        """Тест отсутствия атрибута profession"""
        vacancy = Mock(spec=Vacancy)
        vacancy.title = ""
        vacancy.requirements = ""
        vacancy.responsibilities = ""
        vacancy.description = ""
        vacancy.detailed_description = ""
        vacancy.skills = []
        # Не устанавливаем атрибут profession

        assert vacancy_contains_keyword(vacancy, "python") is False

    def test_empty_skills_list(self):
        """Тест с пустым списком навыков"""
        vacancy = self.create_mock_vacancy(skills=[])

        assert vacancy_contains_keyword(vacancy, "python") is False
