from src.api_modules.get_api import APIConnector
from src.config.api_config import APIConfig


def test_progress_bar_with_output_filter(mocker, capsys):
    """Тест с фильтрацией вывода прогресс-бара"""
    # 1. Подготовка
    config = APIConfig(user_agent="Test", timeout=10)

    # 2. Мокирование
    mock_get = mocker.patch('requests.get')
    mock_get.return_value = mocker.Mock(
        status_code=200,
        json=lambda: {'data': 'test'}
    )

    # 3. Вызов
    connector = APIConnector(config)
    result = connector.connect(
        "http://test.com",
        {},
        show_progress=True,
        progress_desc="Test progress"
    )

    # 4. Перехват и фильтрация вывода
    captured = capsys.readouterr()

    # Убедимся, что нет нежелательного вывода параметров
    assert not any(
        line.strip().startswith('{') and 'bar_format' in line
        for line in captured.out.split('\n')
    ), "Обнаружен вывод параметров прогресс-бара"

    # 5. Проверка результата
    assert result == {'data': 'test'}