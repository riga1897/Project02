
import requests
import json
from src.utils.env_loader import EnvLoader

def test_superjob_api():
    """Простой тест SuperJob API"""
    
    # Получаем API ключ
    api_key = EnvLoader.get_env_var('SUPERJOB_API_KEY', 'v3.r.137440105.example.test_tool')
    
    url = "https://api.superjob.ru/2.0/vacancies/"
    headers = {
        "X-Api-App-Id": api_key,
        "User-Agent": "VacancySearchApp/1.0"
    }
    
    # Минимальный набор параметров
    params = {
        "keyword": "Python",
        "count": 10,
        "page": 0
    }
    
    print(f"Testing SuperJob API...")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Params: {params}")
    print("-" * 50)
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Keys: {list(data.keys())}")
            print(f"Total: {data.get('total', 'N/A')}")
            print(f"More: {data.get('more', 'N/A')}")
            print(f"Objects count: {len(data.get('objects', []))}")
            
            if data.get('objects'):
                first_vacancy = data['objects'][0]
                print(f"First vacancy keys: {list(first_vacancy.keys())}")
                print(f"First vacancy profession: {first_vacancy.get('profession', 'N/A')}")
            
            return data
        else:
            print(f"Error response: {response.text}")
            return None
            
    except Exception as e:
        print(f"Exception: {e}")
        return None

if __name__ == "__main__":
    test_superjob_api()
