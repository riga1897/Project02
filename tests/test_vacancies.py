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

    def test_cast_to_object_list_with_extra_fields(self):
        """Тест преобразования данных с лишними полями"""
        test_data = [
            {
                "id": "123",
                "title": "Python Developer", 
                "url": "https://hh.ru/vacancy/123",
                "salary": "100 000-150 000 руб.",
                "description": "Описание вакансии...",
                "extra_field": "some value"  # Дополнительное поле
            }
        ]
        result = Vacancy.cast_to_object_list(test_data)
        assert len(result) == 1
        assert isinstance(result[0], Vacancy)
        assert result[0].title == "Python Developer"
        assert result[0].url == "https://hh.ru/vacancy/123"
        assert result[0].salary == "100 000-150 000 руб."
        assert result[0].description == "Описание вакансии..."
        # Проверяем, что лишние поля не попали в объект
        assert not hasattr(result[0], 'id')
        assert not hasattr(result[0], 'extra_field')

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
