import pytest
from src.vacancies.models import Vacancy


class TestVacancy:
    """Тесты для класса Vacancy"""

    def test_cast_to_object_list(self):
        """Тест преобразования списка словарей в список объектов"""
        test_data = [
            {"title": "Test", "url": "test.com", "salary": "100", "description": "desc"},
            {"title": "Test2", "url": "test.com", "salary": None, "description": "desc2"}
        ]
        result = Vacancy.cast_to_object_list(test_data)
        assert len(result) == 2
        assert isinstance(result[0], Vacancy)
        assert result[0].title == "Test"
        assert result[1].salary is None

    def test_vacancy_equality(self, sample_vacancy):
        """Тест сравнения вакансий"""
        v1 = sample_vacancy
        v2 = Vacancy("Python Dev", "http://test.com", "100000", "Test desc")
        v3 = Vacancy("Java Dev", "http://test.com", None, "Java coding")
        assert v1 == v2
        assert v1 != v3

    def test_to_from_dict(self, sample_vacancy):
        """Тест преобразования в словарь и обратно"""
        data = sample_vacancy.to_dict()
        new_vacancy = Vacancy.from_dict(data)
        assert new_vacancy == sample_vacancy

    def test_str_representation(self, sample_vacancy):
        """Тест строкового представления вакансии"""
        assert str(sample_vacancy) == "Python Dev (100000)"

    def test_vacancy_equality(self, sample_vacancy):
        """Тест сравнения вакансий"""
        v1 = sample_vacancy
        v2 = Vacancy("Python Dev", "http://test.com", "100000", "Test desc")
        v3 = Vacancy("Java Dev", "http://test.com", None, "Java coding")
        assert v1 == v2
        assert v1 != v3
        # Add this new test case
        assert v1 != "not a vacancy object"  # This will exercise line 63
