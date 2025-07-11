import logging

import requests

logger = logging.getLogger(__name__)


def get_vacancies(search_text, exclude_text):
    url = 'https://api.hh.ru/vacancies'
    params = {
        'text': search_text,
        'exclude': exclude_text,
        'search_field': 'name',
        'area': 1,
        'period': 1,
        'only_with_salary': True,
        'per_page': 100,
        'page': 0
    }

    vacancies = []
    while True:
        response = requests.get(url, params=params)
        data = response.json()
        vacancies += data['items']

        if data['pages'] == params['page']:
            break
        else:
            params['page'] += 1

    result = []
    for vacancy in vacancies:
        vacancy_data = {
            'name': vacancy['name'],
            'salary': vacancy['salary']['from'] if vacancy['salary']['from'] is not None else 'Not specified',
            'url': vacancy['url']
        }
        result.append(vacancy_data)

    logger.info(f"Found {len(result)} vacancies")
    return result
