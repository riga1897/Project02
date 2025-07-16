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

    def test_vacancy_equality(self):
        """Тест сравнения вакансий"""
        v1 = Vacancy("Python Dev", "http://test.com", "100000", "Test desc", "id1")
        v2 = Vacancy("Python Dev", "http://test.com", "100000", "Test desc", "id1")
        v3 = Vacancy("Java Dev", "http://test.com", None, "Java coding", "id2")
        v4 = Vacancy("Python Dev", "http://test.com", "100000", "Test desc", "id3")

        # Проверка равенства (должны быть равны, если совпадают id)
        assert v1 == v2
        # Проверка неравенства
        assert v1 != v3
        # Проверка с разными id (даже если остальные поля одинаковы)
        assert v1 != v4
        # Проверка сравнения с объектом другого типа
        assert v1 != "not a vacancy object"

    def test_to_from_dict(self):
        """Тест преобразования в словарь и обратно"""
        vacancy = Vacancy("Python Dev", "http://test.com", "100000", "Test desc", "id1")
        data = vacancy.to_dict()
        new_vacancy = Vacancy.from_dict(data)
        assert new_vacancy == vacancy

    def test_str_representation(self):
        """Тест строкового представления вакансии"""
        vacancy1 = Vacancy("Python Dev", "http://test.com", "100000", "Test desc")
        vacancy2 = Vacancy("Java Dev", "http://test.com", None, "Java coding")

        assert str(vacancy1) == "Python Dev (100000)"
        assert str(vacancy2) == "Java Dev (Зарплата не указана)"
