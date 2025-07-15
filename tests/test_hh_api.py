from unittest.mock import patch


class TestHeadHunterAPI:
    @patch('src.api_modules.get_api.APIConnector.connect')
    def test_get_vacancies_page(self, mock_connect, default_hh_api):
        mock_connect.return_value = {'items': [{'id': '1', 'name': 'Python Dev'}]}
        result = default_hh_api.get_vacancies_page("Python")
        assert len(result) == 1
        assert result[0]['name'] == 'Python Dev'

    @patch('src.api_modules.hh_api.HeadHunterAPI.get_vacancies_page')
    def test_get_vacancies_pagination(self, mock_get_page, default_hh_api):
        mock_get_page.side_effect = [
            [{'id': str(i), 'name': f'Dev {i}'} for i in range(50)],
            [{'id': str(i), 'name': f'Dev {i}'} for i in range(50, 75)],
            []
        ]
        result = default_hh_api.get_vacancies("Python")
        assert len(result) == 75
        assert result[0]['name'] == 'Dev 0'
        assert result[74]['name'] == 'Dev 74'

    def test_custom_config(self, custom_hh_api):
        assert custom_hh_api.config.user_agent == "TestAgent/1.0"
        assert custom_hh_api.config.timeout == 10
        # assert custom_hh_api.config.get_hh_params()['per_page'] == 10
