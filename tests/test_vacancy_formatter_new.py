
"""
Новые тесты для модуля vacancy_formatter
"""

import pytest
from src.utils.vacancy_formatter import VacancyFormatter
from src.vacancies.models import Vacancy


class TestVacancyFormatterNew:
    """Новые тесты для класса VacancyFormatter"""
    
    @pytest.fixture
    def full_vacancy(self):
        """Вакансия с полными данными"""
        return Vacancy(
            title="Senior Python Developer",
            url="https://example.com/1",
            salary={"from": 150000, "to": 200000, "currency": "RUR"},
            description="Разработка высоконагруженных систем",
            requirements="Python, Django, PostgreSQL, Redis",
            responsibilities="Разработка API, оптимизация базы данных",
            employer={"name": "Tech Company Ltd"},
            experience="От 3 до 6 лет",
            employment="Полная занятость",
            schedule="Полный день",
            skills=[
                {"name": "Python"},
                {"name": "Django"},
                {"name": "PostgreSQL"},
                {"name": "Redis"},
                {"name": "Docker"},
                {"name": "Kubernetes"}
            ],
            vacancy_id="1"
        )
    
    @pytest.fixture
    def minimal_vacancy(self):
        """Вакансия с минимальными данными"""
        return Vacancy(
            title="Junior Developer",
            url="https://example.com/2",
            salary=None,
            description="Стажировка",
            vacancy_id="2"
        )
    
    def test_format_vacancy_info_full_data(self, full_vacancy):
        """Тест форматирования вакансии с полными данными"""
        result = VacancyFormatter.format_vacancy_info(full_vacancy)
        
        assert "Senior Python Developer" in result
        assert "Tech Company Ltd" in result
        assert "150000" in result
        assert "200000" in result
        assert "От 3 до 6 лет" in result
        assert "Полная занятость" in result
        assert "Полный день" in result
        assert "Python" in result
        assert "Django" in result
        assert "https://example.com/1" in result
        assert "ID: 1" in result
        assert "Разработка API" in result
    
    def test_format_vacancy_info_minimal_data(self, minimal_vacancy):
        """Тест форматирования вакансии с минимальными данными"""
        result = VacancyFormatter.format_vacancy_info(minimal_vacancy)
        
        assert "Junior Developer" in result
        assert "https://example.com/2" in result
        assert "ID: 2" in result
        assert "Зарплата: Не указана" in result
        assert "Компания: Не указана" in result
    
    def test_format_vacancy_info_with_number(self, full_vacancy):
        """Тест форматирования вакансии с порядковым номером"""
        result = VacancyFormatter.format_vacancy_info(full_vacancy, number=5)
        
        assert "5." in result
        assert "Senior Python Developer" in result
    
    def test_format_salary_full_range(self, full_vacancy):
        """Тест форматирования полного диапазона зарплаты"""
        result = VacancyFormatter.format_salary(full_vacancy.salary)
        
        assert "от 150000" in result
        assert "до 200000" in result
        assert "RUR" in result
    
    def test_format_salary_from_only(self):
        """Тест форматирования только нижней границы зарплаты"""
        vacancy = Vacancy(
            title="Test",
            url="https://test.com",
            salary={"from": 100000, "currency": "RUR"},
            description="Test",
            vacancy_id="test"
        )
        
        result = VacancyFormatter.format_salary(vacancy.salary)
        
        assert "от 100000" in result
        assert "RUR" in result
        assert "до" not in result
    
    def test_format_salary_to_only(self):
        """Тест форматирования только верхней границы зарплаты"""
        vacancy = Vacancy(
            title="Test",
            url="https://test.com",
            salary={"to": 80000, "currency": "RUR"},
            description="Test",
            vacancy_id="test"
        )
        
        result = VacancyFormatter.format_salary(vacancy.salary)
        
        assert "до 80000" in result
        assert "RUR" in result
        assert "от" not in result
    
    def test_format_salary_none(self, minimal_vacancy):
        """Тест форматирования отсутствующей зарплаты"""
        result = VacancyFormatter.format_salary(minimal_vacancy.salary)
        
        assert "не указана" in result.lower()
    
    def test_format_company_info_dict(self, full_vacancy):
        """Тест форматирования информации о компании из словаря"""
        result = VacancyFormatter.format_company_info(full_vacancy.employer)
        
        assert result == "Tech Company Ltd"
    
    def test_format_company_info_string(self):
        """Тест форматирования информации о компании из строки"""
        result = VacancyFormatter.format_company_info("Some Company")
        
        assert result == "Some Company"
    
    def test_format_company_info_none(self):
        """Тест форматирования отсутствующей информации о компании"""
        result = VacancyFormatter.format_company_info(None)
        
        assert result == "Не указана"
    
    def test_format_company_info_empty_dict(self):
        """Тест форматирования пустого словаря компании"""
        result = VacancyFormatter.format_company_info({})
        
        assert result == "Не указана"
    
    def test_display_vacancy_info_with_number(self, full_vacancy, capsys):
        """Тест отображения вакансии с номером"""
        VacancyFormatter.display_vacancy_info(full_vacancy, number=1)
        
        captured = capsys.readouterr()
        assert "1." in captured.out
        assert "Senior Python Developer" in captured.out
        assert "---" in captured.out
    
    def test_display_vacancy_info_without_number(self, minimal_vacancy, capsys):
        """Тест отображения вакансии без номера"""
        VacancyFormatter.display_vacancy_info(minimal_vacancy)
        
        captured = capsys.readouterr()
        assert "Junior Developer" in captured.out
        assert "Зарплата: Не указана" in captured.out
        assert "---" in captured.out
    
    def test_format_vacancy_with_many_skills(self):
        """Тест форматирования вакансии с большим количеством навыков"""
        skills = [{"name": f"Skill{i}"} for i in range(10)]
        
        vacancy = Vacancy(
            title="Developer",
            url="https://example.com",
            salary=None,
            description="Test",
            skills=skills,
            vacancy_id="test"
        )
        
        result = VacancyFormatter.format_vacancy_info(vacancy)
        
        assert "Skill0" in result
        assert "Skill4" in result
        assert "еще 5" in result  # Проверяем, что показывается информация о дополнительных навыках
    
    def test_format_vacancy_with_long_requirements(self):
        """Тест форматирования вакансии с длинными требованиями"""
        long_requirements = "Очень длинные требования к кандидату, которые превышают обычную длину и должны быть обрезаны в определенном месте для лучшей читаемости."
        
        vacancy = Vacancy(
            title="Developer",
            url="https://example.com",
            salary=None,
            description="Test",
            requirements=long_requirements,
            vacancy_id="test"
        )
        
        result = VacancyFormatter.format_vacancy_info(vacancy)
        
        assert "Требования:" in result
        assert "..." in result  # Проверяем, что длинные требования обрезаются
