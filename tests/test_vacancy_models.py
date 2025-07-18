
"""
Комплексные тесты для моделей вакансий
"""

import pytest
from src.vacancies.models import Vacancy
from src.vacancies.sj_models import SuperJobVacancy
from src.utils.salary import Salary


class TestVacancy:
    """Тесты для основной модели Vacancy"""
    
    @pytest.fixture
    def vacancy_data(self):
        """Тестовые данные для вакансии"""
        return {
            'name': 'Python Developer',
            'alternate_url': 'https://hh.ru/vacancy/123',
            'salary': {'from': 100000, 'to': 150000, 'currency': 'RUR'},
            'snippet': {'responsibility': 'Разработка на Python'},
            'employer': {'name': 'Tech Company'},
            'id': '123'
        }
    
    @pytest.fixture
    def vacancy_no_salary_data(self):
        """Тестовые данные для вакансии без зарплаты"""
        return {
            'name': 'Intern Position',
            'alternate_url': 'https://hh.ru/vacancy/456',
            'salary': None,
            'snippet': {'responsibility': 'Стажировка'},
            'employer': {'name': 'Startup'},
            'id': '456'
        }
    
    def test_vacancy_creation_with_salary(self, vacancy_data):
        """Тест создания вакансии с зарплатой"""
        vacancy = Vacancy(
            title=vacancy_data['name'],
            url=vacancy_data['alternate_url'],
            salary=vacancy_data['salary'],
            description=vacancy_data['snippet']['responsibility'],
            vacancy_id=vacancy_data['id']
        )
        
        assert vacancy.title == 'Python Developer'
        assert vacancy.url == 'https://hh.ru/vacancy/123'
        assert vacancy.salary.average == 125000
        assert vacancy.vacancy_id == '123'
    
    def test_vacancy_creation_without_salary(self, vacancy_no_salary_data):
        """Тест создания вакансии без зарплаты"""
        vacancy = Vacancy(
            title=vacancy_no_salary_data['name'],
            url=vacancy_no_salary_data['alternate_url'],
            salary=vacancy_no_salary_data['salary'],
            description=vacancy_no_salary_data['snippet']['responsibility'],
            vacancy_id=vacancy_no_salary_data['id']
        )
        
        assert vacancy.title == 'Intern Position'
        assert vacancy.salary.average == 0
    
    def test_vacancy_comparison(self):
        """Тест сравнения вакансий по зарплате"""
        vacancy1 = Vacancy(
            title="Junior",
            url="http://test1.com",
            salary={'from': 50000, 'currency': 'RUR'},
            description="Junior position",
            vacancy_id="1"
        )
        
        vacancy2 = Vacancy(
            title="Senior",
            url="http://test2.com",
            salary={'from': 150000, 'currency': 'RUR'},
            description="Senior position",
            vacancy_id="2"
        )
        
        assert vacancy2 > vacancy1
        assert vacancy1 < vacancy2
        assert vacancy1 != vacancy2
    
    def test_vacancy_to_dict(self, vacancy_data):
        """Тест сериализации вакансии в словарь"""
        vacancy = Vacancy(
            title=vacancy_data['name'],
            url=vacancy_data['alternate_url'],
            salary=vacancy_data['salary'],
            description=vacancy_data['snippet']['responsibility'],
            vacancy_id=vacancy_data['id']
        )
        
        result = vacancy.to_dict()
        
        assert result['title'] == 'Python Developer'
        assert result['url'] == 'https://hh.ru/vacancy/123'
        assert result['salary']['from'] == 100000
        assert result['id'] == '123'
    
    def test_vacancy_from_dict(self, vacancy_data):
        """Тест десериализации вакансии из словаря"""
        dict_data = {
            'title': vacancy_data['name'],
            'url': vacancy_data['alternate_url'],
            'salary': vacancy_data['salary'],
            'description': vacancy_data['snippet']['responsibility'],
            'id': vacancy_data['id']
        }
        
        vacancy = Vacancy.from_dict(dict_data)
        
        assert vacancy.title == 'Python Developer'
        assert vacancy.url == 'https://hh.ru/vacancy/123'
        assert vacancy.salary.average == 125000
    
    def test_cast_to_object_list(self):
        """Тест преобразования списка словарей в список объектов"""
        data = [
            {
                'title': 'Python Dev',
                'url': 'http://test1.com',
                'salary': {'from': 100000, 'currency': 'RUR'},
                'description': 'Test',
                'id': '1'
            },
            {
                'title': 'Java Dev',
                'url': 'http://test2.com',
                'salary': None,
                'description': 'Test',
                'id': '2'
            }
        ]
        
        result = Vacancy.cast_to_object_list(data)
        
        assert len(result) == 2
        assert all(isinstance(v, Vacancy) for v in result)
        assert result[0].salary.average == 100000
        assert result[1].salary.average == 0


class TestSuperJobVacancy:
    """Тесты для модели SuperJobVacancy"""
    
    @pytest.fixture
    def sj_data(self):
        """Тестовые данные для SuperJob вакансии"""
        return {
            'profession': 'Python Developer',
            'link': 'https://superjob.ru/vacancy/123',
            'payment_from': 100000,
            'payment_to': 150000,
            'currency': 'rub',
            'candidat': 'Опыт работы с Python',
            'firm_name': 'Tech Company',
            'id': 123
        }
    
    def test_superjob_vacancy_creation(self, sj_data):
        """Тест создания SuperJob вакансии"""
        vacancy = SuperJobVacancy.from_api_data(sj_data)
        
        assert vacancy.title == 'Python Developer'
        assert vacancy.url == 'https://superjob.ru/vacancy/123'
        assert vacancy.salary.average == 125000
        assert vacancy.source == 'superjob'
    
    def test_superjob_vacancy_no_salary(self):
        """Тест создания SuperJob вакансии без зарплаты"""
        data = {
            'profession': 'Intern',
            'link': 'https://superjob.ru/vacancy/456',
            'payment_from': 0,
            'payment_to': 0,
            'currency': 'rub',
            'candidat': 'Стажировка',
            'firm_name': 'Startup',
            'id': 456
        }
        
        vacancy = SuperJobVacancy.from_api_data(data)
        
        assert vacancy.title == 'Intern'
        assert vacancy.salary.average == 0
