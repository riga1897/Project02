# Этот файл больше не нужен, так как функциональность перенесена в унифицированный класс Vacancy
# Используйте src/vacancies/models.py для работы с вакансиями из любого источника

# Для совместимости со старым кодом:
from .models import Vacancy as SuperJobVacancy

__all__ = ['SuperJobVacancy']