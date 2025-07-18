
# Структура проекта

```
Project02/
├── src/                                    # Основной код приложения
│   ├── __init__.py
│   ├── user_interface.py                   # Точка входа для UI
│   │
│   ├── api_modules/                        # Модули для работы с API
│   │   ├── __init__.py
│   │   ├── base_api.py                     # Базовый абстрактный класс API
│   │   ├── cached_api.py                   # Базовый класс с кэшированием
│   │   ├── get_api.py                      # Низкоуровневый HTTP-клиент
│   │   ├── hh_api.py                       # API для работы с HH.ru
│   │   ├── sj_api.py                       # API для работы с SuperJob
│   │   └── unified_api.py                  # Унифицированный API
│   │
│   ├── config/                             # Конфигурация приложения
│   │   ├── __init__.py
│   │   ├── api_config.py                   # Основная конфигурация API
│   │   ├── hh_api_config.py                # Конфигурация HH API
│   │   ├── sj_api_config.py                # Конфигурация SuperJob API
│   │   └── ui_config.py                    # Конфигурация пользовательского интерфейса
│   │
│   ├── storage/                            # Система хранения данных
│   │   ├── __init__.py
│   │   ├── abstract.py                     # Абстрактный класс хранилища
│   │   └── json_saver.py                   # Реализация JSON-хранилища
│   │
│   ├── ui_interfaces/                      # Интерфейсы пользователя
│   │   ├── __init__.py
│   │   ├── console_interface.py            # Консольный интерфейс
│   │   └── source_selector.py              # Выбор источников данных
│   │
│   ├── utils/                              # Утилиты и вспомогательные модули
│   │   ├── __init__.py
│   │   ├── cache.py                        # Система кэширования
│   │   ├── env_loader.py                   # Загрузка переменных окружения
│   │   ├── file_handlers.py                # Работа с файлами
│   │   ├── menu_manager.py                 # Управление меню
│   │   ├── paginator.py                    # Пагинация данных
│   │   ├── salary.py                       # Работа с зарплатами
│   │   ├── search_utils.py                 # Поиск и фильтрация
│   │   ├── source_manager.py               # Управление источниками
│   │   ├── ui_helpers.py                   # Вспомогательные функции UI
│   │   ├── ui_navigation.py                # Навигация по интерфейсу
│   │   ├── ui_paginator.py                 # Пагинация для UI
│   │   ├── vacancy_formatter.py            # Форматирование вакансий
│   │   └── vacancy_operations.py           # Операции с вакансиями
│   │
│   └── vacancies/                          # Модели и парсеры вакансий
│       ├── __init__.py
│       ├── abstract.py                     # Абстрактная модель вакансии
│       ├── models.py                       # Основные модели вакансий
│       ├── sj_models.py                    # Модели для SuperJob
│       └── parsers/                        # Парсеры данных
│           ├── __init__.py
│           ├── hh_parser.py                # Парсер HH.ru
│           └── sj_parser.py                # Парсер SuperJob
│
├── tests/                                  # Тесты
│   ├── __init__.py
│   ├── conftest.py                         # Конфигурация pytest
│   ├── test_*.py                           # Тестовые файлы
│   └── ...
│
├── data/                                   # Данные приложения
│   ├── cache/                              # Кэш API
│   │   ├── hh/                             # Кэш HH.ru
│   │   └── sj/                             # Кэш SuperJob
│   └── storage/                            # Хранилище данных
│       └── vacancies.json                  # Сохраненные вакансии
│
├── docs/                                   # Документация
│   ├── project_structure.md                # Структура проекта
│   └── modules_interaction.md              # Схема взаимодействия
│
├── .env.sample                             # Пример файла переменных окружения
├── .gitignore                              # Исключения Git
├── .replit                                 # Конфигурация Replit
├── README.md                               # Описание проекта
├── pyproject.toml                          # Конфигурация проекта
├── user_app.py                             # Точка входа приложения
└── WorkFlow.txt                            # Описание рабочего процесса
```

## Описание основных компонентов

### 1. API Modules (`src/api_modules/`)
- **BaseAPI**: Абстрактный базовый класс для всех API
- **CachedAPI**: Базовый класс с поддержкой кэширования
- **APIConnector**: HTTP-клиент для выполнения запросов
- **HeadHunterAPI**: Специализированный API для HH.ru
- **SuperJobAPI**: Специализированный API для SuperJob
- **UnifiedAPI**: Унифицированный интерфейс для всех источников

### 2. Storage (`src/storage/`)
- **AbstractStorage**: Абстрактный класс для хранилищ
- **JSONSaver**: Реализация хранилища в JSON формате

### 3. Vacancies (`src/vacancies/`)
- **AbstractVacancy**: Абстрактная модель вакансии
- **Vacancy**: Основная модель вакансии
- **SuperJobVacancy**: Модель для SuperJob
- **Парсеры**: Преобразование данных из API в модели

### 4. UI Interfaces (`src/ui_interfaces/`)
- **UserInterface**: Консольный интерфейс пользователя
- **SourceSelector**: Выбор источников данных

### 5. Utils (`src/utils/`)
- Вспомогательные модули для различных операций
- Форматирование, поиск, навигация, пагинация

### 6. Config (`src/config/`)
- Конфигурация API и пользовательского интерфейса
- Настройки подключения и параметров
