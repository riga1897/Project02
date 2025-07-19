
# Структура классов проекта и их взаимодействия

## 1. Абстрактные базовые классы

### AbstractVacancy (src/vacancies/abstract.py)
- **Назначение**: Абстрактный базовый класс для всех типов вакансий
- **Ключевые методы**:
  - `__init__()` - абстрактная инициализация
  - `to_dict()` - преобразование в словарь
  - `from_dict(cls, data)` - создание объекта из словаря

### AbstractVacancyStorage (src/storage/abstract.py)
- **Назначение**: Абстрактный базовый класс для хранения вакансий
- **Ключевые методы**:
  - Определяет интерфейс для сохранения/загрузки вакансий

### BaseAPI (src/api_modules/base_api.py)
- **Назначение**: Базовый класс для всех API модулей
- **Ключевые методы**:
  - `get_vacancies(search_query, **kwargs)` - получение вакансий
  - `clear_cache(api_prefix)` - очистка кэша

## 2. Основные модели данных

### Salary (src/utils/salary.py)
- **Назначение**: Класс для представления зарплатной информации
- **Атрибуты**: 
  - `amount_from` - минимальная зарплата
  - `amount_to` - максимальная зарплата
  - `currency` - валюта
- **Ключевые методы**:
  - `average` - расчет средней зарплаты
  - `to_dict()` - преобразование в словарь
  - `__str__()` - строковое представление

### Vacancy (src/vacancies/models.py)
- **Наследует от**: AbstractVacancy
- **Композиция с**: Salary
- **Назначение**: Унифицированный класс вакансии из любого источника
- **Ключевые методы**:
  - `_validate_salary()` - создает объект Salary
  - `from_dict()` - универсальный парсинг данных
  - `to_dict()` - преобразование в унифицированный словарь
  - Операторы сравнения (`__lt__`, `__eq__`, etc.)

### HHVacancy (src/vacancies/hh_models.py)
- **Наследует от**: AbstractVacancy
- **Композиция с**: Salary
- **Назначение**: Специализированный класс для вакансий с HeadHunter
- **Ключевые методы**:
  - `_validate_salary()` - создает объект Salary специфично для HH

### SuperJobVacancy (src/vacancies/sj_models.py)
- **Наследует от**: AbstractVacancy
- **Композиция с**: Salary
- **Назначение**: Специализированный класс для вакансий с SuperJob
- **Ключевые методы**:
  - `_validate_salary()` - создает объект Salary специфично для SJ

## 3. Хранение данных

### JSONSaver (src/storage/json_saver.py)
- **Наследует от**: AbstractVacancyStorage
- **Работает с**: Vacancy (коллекциями объектов)
- **Назначение**: Сохранение и загрузка вакансий в JSON формате
- **Ключевые методы**:
  - `add_vacancy()` - добавление вакансий с обновлением существующих
  - `load_vacancies()` - загрузка с десериализацией Salary
  - `_save_to_file()` - сериализация объектов Salary через vacancy.to_dict()
  - `delete_vacancy_by_id()` - удаление по ID
  - `get_vacancies()` - получение всех вакансий

## 4. API классы

### HHAPI (src/api_modules/hh_api.py)
- **Наследует от**: BaseAPI
- **Назначение**: API для работы с HeadHunter
- **Связь**: Создает данные для HHVacancy

### SuperJobAPI (src/api_modules/sj_api.py)
- **Наследует от**: BaseAPI
- **Назначение**: API для работы с SuperJob
- **Связь**: Создает данные для SuperJobVacancy

### CachedAPI (src/api_modules/cached_api.py)
- **Наследует от**: BaseAPI
- **Назначение**: API с кэшированием запросов

### UnifiedAPI (src/api_modules/unified_api.py)
- **Использует**: HHAPI, SuperJobAPI
- **Назначение**: Единый интерфейс для работы с несколькими API
- **Ключевые методы**:
  - Объединяет результаты разных API

## 5. Парсеры

### HHParser (src/vacancies/parsers/hh_parser.py)
- **Создает**: HHVacancy объекты
- **Назначение**: Парсинг данных из HeadHunter API

### SuperJobParser (src/vacancies/parsers/sj_parser.py)
- **Создает**: SuperJobVacancy объекты
- **Назначение**: Парсинг данных из SuperJob API

## 6. UI и утилиты

### ConsoleInterface (src/ui_interfaces/console_interface.py)
- **Использует**: JSONSaver для хранения данных
- **Назначение**: Пользовательский интерфейс консоли

### VacancyOperations (src/utils/vacancy_operations.py)
- **Работает с**: коллекциями Vacancy
- **Назначение**: Операции над вакансиями (фильтрация, сортировка)

### VacancyFormatter (src/utils/vacancy_formatter.py)
- **Работает с**: объектами Vacancy
- **Назначение**: Форматирование вывода вакансий

## Схема взаимодействий

### Связи наследования:
```
AbstractVacancy <- Vacancy
AbstractVacancy <- HHVacancy  
AbstractVacancy <- SuperJobVacancy
AbstractVacancyStorage <- JSONSaver
BaseAPI <- HHAPI
BaseAPI <- SuperJobAPI
BaseAPI <- CachedAPI
```

### Композиционные связи (содержит):
```
Vacancy -> Salary (через _validate_salary())
HHVacancy -> Salary (через _validate_salary())
SuperJobVacancy -> Salary (через _validate_salary())
JSONSaver -> [Vacancy] (коллекции)
```

### Связи использования:
```
UnifiedAPI -> HHAPI, SuperJobAPI
ConsoleInterface -> JSONSaver
VacancyOperations -> Vacancy
VacancyFormatter -> Vacancy
HHParser -> HHVacancy
SuperJobParser -> SuperJobVacancy
```

### Методы создающие связи с Salary:
1. `Vacancy._validate_salary()` → создает Salary
2. `HHVacancy._validate_salary()` → создает Salary  
3. `SuperJobVacancy._validate_salary()` → создает Salary
4. `JSONSaver._save_to_file()` → сериализует Salary через vacancy.to_dict()
5. `JSONSaver.load_vacancies()` → десериализует Salary через Vacancy.from_dict()

### Центральная роль Salary:
- Используется во всех моделях вакансий как основа для зарплатных данных
- Обеспечивает унификацию представления зарплаты из разных источников
- Поддерживает операции сравнения для сортировки вакансий по зарплате
- Сериализуется/десериализуется через методы to_dict()/from_dict()

## Принципы архитектуры:

1. **Абстракция**: Базовые абстрактные классы определяют общий интерфейс
2. **Наследование**: Конкретные реализации наследуют от абстрактных классов
3. **Композиция**: Salary инкапсулирован в классах вакансий
4. **Единая ответственность**: Каждый класс отвечает за свою область
5. **Полиморфизм**: Все вакансии могут обрабатываться через общий интерфейс AbstractVacancy
