import pytest
from src.vacancies.models import Vacancy


class TestVacancy:
    def test_vacancy_creation(self):
        vacancy = Vacancy(
            title="Test", 
            url="http://test.com", 
            salary={"from": 100000, "currency": "RUR"}, 
            description="Test vacancy"
        )
        assert vacancy.title == "Test"
        assert vacancy.salary.average == 100000
        assert "от 100000 RUR" in str(vacancy.salary)

    def test_salary_comparison(self):
        v1 = Vacancy("A", "http://a.com", {"from": 100000}, "Desc", "id1")
        v2 = Vacancy("B", "http://b.com", {"from": 150000}, "Desc", "id2")

        assert v1 < v2
        assert v2 > v1
        assert v1 <= v2
        assert v2 >= v1

    def test_to_from_dict(self):
        vacancy = Vacancy(
            title="Test",
            url="http://test.com",
            salary={"from": 100000, "to": 150000, "currency": "RUR"},
            description="Test",
            vacancy_id="test_id"
        )
        data = vacancy.to_dict()
        new_vacancy = Vacancy.from_dict(data)

        assert new_vacancy == vacancy
        assert new_vacancy.salary.average == 125000

    def test_cast_to_object_list(self):
        test_data = [
            {
                "title": "A",
                "url": "http://a.com",
                "salary": {"from": 100000},
                "description": "Desc",
                "id": "1"
            },
            {
                "title": "B",
                "url": "http://b.com",
                "salary": None,
                "description": "Desc",
                "id": "2"
            }
        ]
        result = Vacancy.cast_to_object_list(test_data)
        assert len(result) == 2
        assert result[0].salary.average == 100000
        assert result[1].salary.average == 0
        