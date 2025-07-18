
# Схема взаимодействия модулей и классов

## Архитектурная диаграмма

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                USER INTERFACE                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│  user_app.py                                                                    │
│  ├── UserInterface (console_interface.py)                                      │
│  │   ├── MenuManager (menu_manager.py)                                         │
│  │   ├── SourceSelector (source_selector.py)                                  │
│  │   ├── VacancyOperations (vacancy_operations.py)                            │
│  │   └── UI Helpers (ui_helpers.py, ui_navigation.py)                         │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              UNIFIED API LAYER                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│  UnifiedAPI (unified_api.py)                                                   │
│  ├── Координация запросов к различным источникам                                │
│  ├── Объединение результатов                                                   │
│  └── Управление кэшем                                                          │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
    ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
    │     HH.ru API       │  │   SuperJob API      │  │   Future APIs       │
    │                     │  │                     │  │                     │
    │  HeadHunterAPI      │  │  SuperJobAPI        │  │  (Расширяемость)    │
    │  ├── CachedAPI      │  │  ├── CachedAPI      │  │                     │
    │  ├── APIConnector   │  │  ├── APIConnector   │  │                     │
    │  └── HHAPIConfig    │  │  └── SJAPIConfig    │  │                     │
    └─────────────────────┘  └─────────────────────┘  └─────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DATA PROCESSING                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Parsers (src/vacancies/parsers/)                                              │
│  ├── HHParser - Парсинг данных HH.ru                                           │
│  ├── SJParser - Парсинг данных SuperJob                                        │
│  └── Конвертация в унифицированный формат                                      │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DATA MODELS                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Models (src/vacancies/)                                                       │
│  ├── AbstractVacancy - Базовая абстракция                                      │
│  ├── Vacancy - Основная модель вакансии                                        │
│  ├── SuperJobVacancy - Специфичная модель SuperJob                             │
│  └── Salary - Модель зарплаты                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              STORAGE LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Storage (src/storage/)                                                        │
│  ├── AbstractStorage - Абстрактный интерфейс хранилища                         │
│  ├── JSONSaver - Реализация JSON-хранилища                                     │
│  └── File Operations (file_handlers.py)                                        │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              UTILITY LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Utils (src/utils/)                                                            │
│  ├── Cache - Система кэширования                                               │
│  ├── Paginator - Пагинация данных                                              │
│  ├── Search Utils - Поиск и фильтрация                                         │
│  ├── Vacancy Formatter - Форматирование вывода                                 │
│  └── Environment Loader - Загрузка конфигурации                                │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Детальная схема взаимодействия классов

### 1. Инициализация приложения
```
user_app.py
    └── main()
        └── UserInterface()
            ├── HeadHunterAPI()
            ├── SuperJobAPI()  
            ├── UnifiedAPI()
            ├── JSONSaver()
            └── MenuManager()
```

### 2. Поток данных при поиске вакансий
```
UserInterface.search_vacancies()
    └── UnifiedAPI.get_vacancies_from_sources()
        ├── HeadHunterAPI.get_vacancies()
        │   ├── CachedAPI.__connect_to_api()  [ПРИВАТНЫЙ]
        │   ├── APIConnector.connect()
        │   └── Vacancy.from_dict()
        └── SuperJobAPI.get_vacancies()
            ├── CachedAPI.__connect_to_api()  [ПРИВАТНЫЙ]
            ├── APIConnector.connect()
            ├── SuperJobParser.parse_vacancies()
            └── Vacancy.from_dict()
```

### 3. Система кэширования
```
CachedAPI
    ├── __connect_to_api()  [ПРИВАТНЫЙ]
    │   ├── Cache.get()
    │   ├── APIConnector.connect()
    │   └── Cache.set()
    └── clear_cache()
```

### 4. Сохранение и загрузка данных
```
JSONSaver
    ├── add_vacancy()
    │   ├── load_vacancies()
    │   ├── Vacancy.to_dict()
    │   └── _save_to_file()
    └── load_vacancies()
        └── Vacancy.from_dict()
```

### 5. Пользовательский интерфейс
```
UserInterface
    ├── MenuManager
    │   ├── display_menu()
    │   └── handle_choice()
    ├── SourceSelector
    │   └── select_sources()
    ├── VacancyOperations
    │   ├── display_vacancies()
    │   ├── filter_vacancies()
    │   └── sort_vacancies()
    └── UI Navigation
        ├── paginate()
        └── format_output()
```

## Принципы архитектуры

### 1. Разделение ответственности
- **API Layer**: Получение данных из внешних источников
- **Data Layer**: Модели и парсинг данных
- **Storage Layer**: Сохранение и загрузка данных
- **UI Layer**: Взаимодействие с пользователем
- **Utils Layer**: Вспомогательные функции

### 2. Абстракция и наследование
```
AbstractVacancy
    └── Vacancy
        └── SuperJobVacancy

AbstractStorage
    └── JSONSaver

BaseAPI
    └── CachedAPI
        ├── HeadHunterAPI
        └── SuperJobAPI
```

### 3. Принцип единственной ответственности
- Каждый класс имеет четко определенную роль
- Разделение конфигурации, логики и представления
- Независимые модули для различных функций

### 4. Расширяемость
- Легко добавить новые источники данных
- Простое добавление новых типов хранилищ
- Модульная структура UI

### 5. Инкапсуляция
- Приватные методы (двойное подчеркивание)
- Четкие интерфейсы между модулями
- Скрытие деталей реализации

## Потоки данных

### Поиск вакансий:
1. **UI** → **UnifiedAPI** → **Specific API** → **APIConnector** → **External API**
2. **External API** → **Parser** → **Vacancy Model** → **Cache** → **UI**

### Сохранение:
1. **UI** → **JSONSaver** → **File System**

### Загрузка:
1. **UI** → **JSONSaver** → **File System** → **Vacancy Model** → **UI**

### Кэширование:
1. **API Request** → **Cache Check** → **Cache Hit/Miss** → **API Call/Cache Return**
