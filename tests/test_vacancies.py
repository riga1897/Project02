
import pytest
from src.vacancies.models import Vacancy
from src.vacancies.sj_models import SuperJobVacancy


class TestVacancy:
    
    @pytest.fixture
    def vacancy_data(self):
        return {
            'id': '123',
            'name': 'Python Developer',
            'url': 'https://example.com',
            'salary_from': 50000,
            'salary_to': 80000,
            'currency': 'RUB',
            'employer': 'Test Company',
            'description': 'Test description',
            'requirements': 'Python, Django',
            'area': 'Moscow',
            'published': '2024-01-01',
            'source': 'hh.ru'
        }
    
    @pytest.fixture
    def vacancy(self, vacancy_data):
        return Vacancy(**vacancy_data)
    
    def test_init(self, vacancy):
        assert vacancy.id == '123'
        assert vacancy.name == 'Python Developer'
        assert vacancy.salary_from == 50000
        assert vacancy.salary_to == 80000
        assert vacancy.source == 'hh.ru'
    
    def test_from_dict(self, vacancy_data):
        vacancy = Vacancy.from_dict(vacancy_data)
        assert vacancy.id == '123'
        assert vacancy.name == 'Python Developer'
    
    def test_from_dict_missing_fields(self):
        data = {'id': '123', 'name': 'Test'}
        vacancy = Vacancy.from_dict(data)
        assert vacancy.id == '123'
        assert vacancy.name == 'Test'
        assert vacancy.salary_from is None
    
    def test_to_dict(self, vacancy):
        data = vacancy.to_dict()
        assert isinstance(data, dict)
        assert data['id'] == '123'
        assert data['name'] == 'Python Developer'
    
    def test_get_salary_range(self, vacancy):
        salary_range = vacancy.get_salary_range()
        assert '50000' in salary_range
        assert '80000' in salary_range
        assert 'RUB' in salary_range
    
    def test_get_salary_range_no_salary(self):
        vacancy = Vacancy(id='123', name='Test')
        salary_range = vacancy.get_salary_range()
        assert salary_range == "Не указана"
    
    def test_get_salary_range_from_only(self):
        vacancy = Vacancy(id='123', name='Test', salary_from=50000, currency='RUB')
        salary_range = vacancy.get_salary_range()
        assert 'от 50000' in salary_range
        assert 'RUB' in salary_range
    
    def test_get_salary_range_to_only(self):
        vacancy = Vacancy(id='123', name='Test', salary_to=80000, currency='RUB')
        salary_range = vacancy.get_salary_range()
        assert 'до 80000' in salary_range
        assert 'RUB' in salary_range
    
    def test_str_representation(self, vacancy):
        str_repr = str(vacancy)
        assert 'Python Developer' in str_repr
        assert 'Test Company' in str_repr
    
    def test_repr_representation(self, vacancy):
        repr_str = repr(vacancy)
        assert 'Vacancy' in repr_str
        assert '123' in repr_str
    
    def test_eq_comparison(self, vacancy_data):
        vacancy1 = Vacancy(**vacancy_data)
        vacancy2 = Vacancy(**vacancy_data)
        assert vacancy1 == vacancy2
    
    def test_ne_comparison(self, vacancy_data):
        vacancy1 = Vacancy(**vacancy_data)
        vacancy_data['id'] = '456'
        vacancy2 = Vacancy(**vacancy_data)
        assert vacancy1 != vacancy2
    
    def test_lt_comparison(self):
        vacancy1 = Vacancy(id='1', name='Test1', salary_from=50000)
        vacancy2 = Vacancy(id='2', name='Test2', salary_from=60000)
        assert vacancy1 < vacancy2
    
    def test_lt_comparison_no_salary(self):
        vacancy1 = Vacancy(id='1', name='Test1')
        vacancy2 = Vacancy(id='2', name='Test2', salary_from=60000)
        assert vacancy1 < vacancy2


class TestSuperJobVacancy:
    
    @pytest.fixture
    def sj_vacancy_data(self):
        return {
            'profession': 'Python Developer',
            'link': 'https://example.com',
            'payment_from': 50000,
            'payment_to': 80000,
            'currency': 'rub',
            'firm_name': 'Test Company',
            'candidat': 'Test requirements',
            'town': {'title': 'Moscow'},
            'date_published': 1640995200,  # 2022-01-01
            'source': 'superjob.ru'
        }
    
    @pytest.fixture
    def sj_vacancy(self, sj_vacancy_data):
        return SuperJobVacancy(**sj_vacancy_data)
    
    def test_init(self, sj_vacancy):
        assert sj_vacancy.profession == 'Python Developer'
        assert sj_vacancy.link == 'https://example.com'
        assert sj_vacancy.payment_from == 50000
        assert sj_vacancy.payment_to == 80000
    
    def test_from_dict(self, sj_vacancy_data):
        vacancy = SuperJobVacancy.from_dict(sj_vacancy_data)
        assert vacancy.profession == 'Python Developer'
        assert vacancy.link == 'https://example.com'
    
    def test_from_dict_missing_fields(self):
        data = {'profession': 'Test', 'link': 'https://example.com'}
        vacancy = SuperJobVacancy.from_dict(data)
        assert vacancy.profession == 'Test'
        assert vacancy.link == 'https://example.com'
        assert vacancy.payment_from is None
    
    def test_to_dict(self, sj_vacancy):
        data = sj_vacancy.to_dict()
        assert isinstance(data, dict)
        assert data['profession'] == 'Python Developer'
        assert data['link'] == 'https://example.com'
    
    def test_get_salary_range(self, sj_vacancy):
        salary_range = sj_vacancy.get_salary_range()
        assert '50000' in salary_range
        assert '80000' in salary_range
        assert 'RUB' in salary_range
    
    def test_get_salary_range_no_salary(self):
        vacancy = SuperJobVacancy(profession='Test', link='https://example.com')
        salary_range = vacancy.get_salary_range()
        assert salary_range == "Не указана"
    
    def test_str_representation(self, sj_vacancy):
        str_repr = str(sj_vacancy)
        assert 'Python Developer' in str_repr
        assert 'Test Company' in str_repr
    
    def test_repr_representation(self, sj_vacancy):
        repr_str = repr(sj_vacancy)
        assert 'SuperJobVacancy' in repr_str
        assert 'Python Developer' in repr_str
