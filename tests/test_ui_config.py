from src.config.ui_config import UIConfig, UIPaginationConfig, ui_config, ui_pagination_config


class TestUIPaginationConfig:
    """Тест конфигурации пагинации UI"""

    def test_default_initialization(self):
        """Тест инициализации с параметрами по умолчанию"""
        config = UIPaginationConfig()

        assert config.default_items_per_page == 10
        assert config.search_results_per_page == 5
        assert config.saved_vacancies_per_page == 10
        assert config.top_vacancies_per_page == 10
        assert config.max_items_per_page == 50
        assert config.min_items_per_page == 1

    def test_custom_initialization(self):
        """Тест инициализации с кастомными параметрами"""
        config = UIPaginationConfig(
            default_items_per_page=15,
            search_results_per_page=8,
            saved_vacancies_per_page=12,
            top_vacancies_per_page=20,
            max_items_per_page=100,
            min_items_per_page=2,
        )

        assert config.default_items_per_page == 15
        assert config.search_results_per_page == 8
        assert config.saved_vacancies_per_page == 12
        assert config.top_vacancies_per_page == 20
        assert config.max_items_per_page == 100
        assert config.min_items_per_page == 2

    def test_get_items_per_page_search_context(self):
        """Тест получения количества элементов для контекста поиска"""
        config = UIPaginationConfig()
        items = config.get_items_per_page("search")

        assert items == 5

    def test_get_items_per_page_saved_context(self):
        """Тест получения количества элементов для контекста сохраненных"""
        config = UIPaginationConfig()
        items = config.get_items_per_page("saved")

        assert items == 10

    def test_get_items_per_page_top_context(self):
        """Тест получения количества элементов для контекста топ"""
        config = UIPaginationConfig()
        items = config.get_items_per_page("top")

        assert items == 10

    def test_get_items_per_page_default_context(self):
        """Тест получения количества элементов для контекста по умолчанию"""
        config = UIPaginationConfig()
        items = config.get_items_per_page(None)

        assert items == 10

    def test_get_items_per_page_unknown_context(self):
        """Тест получения количества элементов для неизвестного контекста"""
        config = UIPaginationConfig()
        items = config.get_items_per_page("unknown")

        assert items == 10

    def test_validate_items_per_page_valid_value(self):
        """Тест валидации корректного значения"""
        config = UIPaginationConfig()
        validated = config.validate_items_per_page(25)

        assert validated == 25

    def test_validate_items_per_page_below_minimum(self):
        """Тест валидации значения ниже минимального"""
        config = UIPaginationConfig()
        validated = config.validate_items_per_page(0)

        assert validated == 1

    def test_validate_items_per_page_above_maximum(self):
        """Тест валидации значения выше максимального"""
        config = UIPaginationConfig()
        validated = config.validate_items_per_page(100)

        assert validated == 50

    def test_validate_items_per_page_at_minimum(self):
        """Тест валидации значения на минимальной границе"""
        config = UIPaginationConfig()
        validated = config.validate_items_per_page(1)

        assert validated == 1

    def test_validate_items_per_page_at_maximum(self):
        """Тест валидации значения на максимальной границе"""
        config = UIPaginationConfig()
        validated = config.validate_items_per_page(50)

        assert validated == 50


class TestUIConfig:
    """Тест основной конфигурации UI"""

    def test_default_initialization(self):
        """Тест инициализации с параметрами по умолчанию"""
        config = UIConfig()

        assert config.items_per_page == 5
        assert config.max_display_items == 20

    def test_custom_initialization(self):
        """Тест инициализации с кастомными параметрами"""
        config = UIConfig(items_per_page=10, max_display_items=30)

        assert config.items_per_page == 10
        assert config.max_display_items == 30

    def test_get_pagination_settings_default(self):
        """Тест получения настроек пагинации по умолчанию"""
        config = UIConfig()
        settings = config.get_pagination_settings()

        expected = {"items_per_page": 5, "max_display_items": 20}
        assert settings == expected

    def test_get_pagination_settings_with_overrides(self):
        """Тест получения настроек пагинации с переопределением"""
        config = UIConfig()
        settings = config.get_pagination_settings(items_per_page=15, max_display_items=40)

        expected = {"items_per_page": 15, "max_display_items": 40}
        assert settings == expected

    def test_get_pagination_settings_partial_overrides(self):
        """Тест получения настроек пагинации с частичным переопределением"""
        config = UIConfig()
        settings = config.get_pagination_settings(items_per_page=8)

        expected = {"items_per_page": 8, "max_display_items": 20}
        assert settings == expected


class TestGlobalInstances:
    """Тест глобальных экземпляров конфигурации"""

    def test_ui_pagination_config_instance(self):
        """Тест глобального экземпляра UIPaginationConfig"""
        assert isinstance(ui_pagination_config, UIPaginationConfig)
        assert ui_pagination_config.default_items_per_page == 10

    def test_ui_config_instance(self):
        """Тест глобального экземпляра UIConfig"""
        assert isinstance(ui_config, UIConfig)
        assert ui_config.items_per_page == 5
