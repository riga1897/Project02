
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.api_modules.sj_api import SuperJobAPI
import json

def test_specific_vacancy():
    """Тестирование конкретной вакансии SuperJob по ID"""
    api = SuperJobAPI()
    
    print("=== Прямой запрос к SuperJob API ===")
    
    # Делаем запрос для поиска вакансии по ID
    try:
        # SuperJob API не позволяет искать по ID напрямую,
        # но мы можем найти вакансию через поиск
        params = {
            'keyword': 'бухгалтер',
            'count': 100  # увеличиваем количество для поиска
        }
        
        response = api._connect_to_api(
            "https://api.superjob.ru/2.0/vacancies/",
            params,
            "sj"
        )
        
        if 'objects' in response:
            # Ищем вакансию с нужным ID
            target_vacancy = None
            for vacancy in response['objects']:
                if str(vacancy.get('id')) == '50354308':
                    target_vacancy = vacancy
                    break
            
            if target_vacancy:
                print(f"=== Найдена вакансия ID: {target_vacancy['id']} ===")
                print(f"Название: {target_vacancy.get('profession', 'Не указано')}")
                print(f"URL: {target_vacancy.get('link', 'Не указано')}")
                
                # Проверяем поля с текстом
                description = target_vacancy.get('vacancyRichText', '')
                candidat = target_vacancy.get('candidat', '')
                work = target_vacancy.get('work', '')
                
                print(f"\n=== Анализ текстовых полей ===")
                print(f"vacancyRichText длина: {len(description)}")
                print(f"candidat длина: {len(candidat)}")
                print(f"work длина: {len(work)}")
                
                # Объединяем весь текст
                full_text = f"{description} {candidat} {work}".lower()
                print(f"Полный текст длина: {len(full_text)}")
                
                # Ищем ключевые слова
                keywords_to_check = ['excel', 'r', '1c', '1с']
                print(f"\n=== Проверка ключевых слов ===")
                
                for keyword in keywords_to_check:
                    count = full_text.count(keyword.lower())
                    if count > 0:
                        print(f"✓ '{keyword}': найдено {count} раз")
                        # Показываем контекст
                        import re
                        pattern = r'.{0,30}' + re.escape(keyword.lower()) + r'.{0,30}'
                        matches = re.findall(pattern, full_text)
                        for i, match in enumerate(matches[:3]):  # Показываем первые 3 совпадения
                            print(f"  Контекст {i+1}: ...{match}...")
                    else:
                        print(f"✗ '{keyword}': НЕ найдено")
                
                # Сохраняем полные данные вакансии для анализа
                with open('vacancy_50354308_raw.json', 'w', encoding='utf-8') as f:
                    json.dump(target_vacancy, f, ensure_ascii=False, indent=2)
                print(f"\n=== Данные сохранены в vacancy_50354308_raw.json ===")
                
            else:
                print("Вакансия с ID 50354308 не найдена в результатах поиска")
                print(f"Найдено {len(response['objects'])} вакансий")
        else:
            print("Неожиданная структура ответа API")
            print(json.dumps(response, ensure_ascii=False, indent=2)[:500])
            
    except Exception as e:
        print(f"Ошибка при запросе к API: {e}")

if __name__ == "__main__":
    test_specific_vacancy()
