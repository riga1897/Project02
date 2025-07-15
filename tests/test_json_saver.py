import pytest
from src.storage.json_saver import JSONSaver
from src.vacancies.models import Vacancy


class TestJSONSaver:
    """Тесты для класса JSONSaver"""

    def test_add_vacancy(self, temp_json_file, sample_vacancy):
        """Тест добавления вакансии"""
        saver = JSONSaver(temp_json_file)
        saver.add_vacancy(sample_vacancy)
        assert len(saver.get_vacancies()) == 1

    def test_delete_vacancy(self, temp_json_file, sample_vacancies):
        """Тест удаления вакансии"""
        saver = JSONSaver(temp_json_file)
        for v in sample_vacancies:
            saver.add_vacancy(v)

        saver.delete_vacancy(sample_vacancies[0])
        assert len(saver.get_vacancies()) == 2

    def test_filter_vacancies(self, temp_json_file, sample_vacancies):
        """Тест фильтрации вакансий"""
        saver = JSONSaver(temp_json_file)
        for v in sample_vacancies:
            saver.add_vacancy(v)

        filtered = saver.get_vacancies({"title": "Python Dev"})
        assert len(filtered) == 1
        assert filtered[0].title == "Python Dev"

    def test_empty_storage(self, temp_json_file):
        """Тест работы с пустым хранилищем"""
        saver = JSONSaver(temp_json_file)
        assert len(saver.get_vacancies()) == 0
        assert saver.get_vacancies({"title": "Non-existent"}) == []
