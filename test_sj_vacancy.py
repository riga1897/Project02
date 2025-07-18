
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.api_modules.sj_api import SuperJobAPI
import json

def test_specific_vacancy():
    """Тестирование конкретной вакансии SuperJob по ID"""
    api = SuperJobAPI()
    
    print("=== Прямой запрос к SuperJob API ===")
    
    # Пробуем разные поисковые запросы
    search_queries = [
        'бухгалтер',
        'ведущий бухгалтер',
        'нефинансовые активы',
        'бухгалтерия',
        'основные средства'
    ]
    
    target_vacancy = None
    
    for query in search_queries:
        print(f"\n--- Поиск по запросу: '{query}' ---")
        try:
            params = {
                'keyword': query,
                'count': 100,
                'published': 1  # за последний день
            }
            
            response = api._connect_to_api(
                "https://api.superjob.ru/2.0/vacancies/",
                params,
                "sj"
            )
            
            if 'objects' in response:
                print(f"Найдено {len(response['objects'])} вакансий")
                
                # Ищем вакансию с нужным ID
                for vacancy in response['objects']:
                    if str(vacancy.get('id')) == '50354308':
                        target_vacancy = vacancy
                        print(f"✓ Найдена целевая вакансия!")
                        break
                
                if target_vacancy:
                    break
                else:
                    # Показываем первые несколько ID для отладки
                    ids = [str(v.get('id')) for v in response['objects'][:5]]
                    print(f"Первые 5 ID: {ids}")
            else:
                print("Неожиданная структура ответа")
                
        except Exception as e:
            print(f"Ошибка при поиске по '{query}': {e}")
    
    if target_vacancy:
        print(f"\n=== Анализ найденной вакансии ID: {target_vacancy['id']} ===")
        print(f"Название: {target_vacancy.get('profession', 'Не указано')}")
        print(f"URL: {target_vacancy.get('link', 'Не указано')}")
        print(f"Компания: {target_vacancy.get('firm_name', 'Не указана')}")
        
        # Анализируем все текстовые поля
        text_fields = {
            'vacancyRichText': target_vacancy.get('vacancyRichText', ''),
            'candidat': target_vacancy.get('candidat', ''),
            'work': target_vacancy.get('work', ''),
            'profession': target_vacancy.get('profession', ''),
            'firm_name': target_vacancy.get('firm_name', '')
        }
        
        print(f"\n=== Анализ текстовых полей ===")
        for field_name, field_value in text_fields.items():
            # Обрабатываем случай, когда field_value может быть None
            if field_value is None:
                field_value = ''
            print(f"{field_name}: {len(field_value)} символов")
        
        # Объединяем весь текст (фильтруем None значения)
        all_text = ' '.join(str(value) if value is not None else '' for value in text_fields.values()).lower()
        print(f"Общий объем текста: {len(all_text)} символов")
        
        # Проверяем ключевые слова
        keywords_to_check = ['excel', 'r', '1c', '1с', 'word', 'опыт', 'бухгалтер']
        print(f"\n=== Проверка ключевых слов ===")
        
        for keyword in keywords_to_check:
            import re
            # Поиск целых слов
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            matches = re.findall(pattern, all_text)
            
            if matches:
                print(f"✓ '{keyword}': найдено {len(matches)} раз")
                
                # Показываем контекст первого вхождения
                match_pos = all_text.find(keyword.lower())
                if match_pos != -1:
                    start = max(0, match_pos - 40)
                    end = min(len(all_text), match_pos + len(keyword) + 40)
                    context = all_text[start:end]
                    print(f"  Контекст: ...{context}...")
            else:
                print(f"✗ '{keyword}': НЕ найдено")
        
        # Сохраняем данные для детального анализа
        with open('vacancy_50354308_full.json', 'w', encoding='utf-8') as f:
            json.dump(target_vacancy, f, ensure_ascii=False, indent=2)
        print(f"\n=== Данные сохранены в vacancy_50354308_full.json ===")
        
    else:
        print("\n❌ Вакансия с ID 50354308 не найдена ни по одному запросу")
        print("Возможные причины:")
        print("- Вакансия была удалена или архивирована")
        print("- Она не индексируется в поиске")
        print("- Нужен более специфический поисковый запрос")
        
        # Попробуем получить последние вакансии без фильтра
        print("\n--- Проверка последних вакансий без фильтра ---")
        try:
            params = {
                'count': 50,
                'published': 1
            }
            
            response = api._connect_to_api(
                "https://api.superjob.ru/2.0/vacancies/",
                params,
                "sj"
            )
            
            if 'objects' in response:
                print(f"Получено {len(response['objects'])} последних вакансий")
                ids = [str(v.get('id')) for v in response['objects']]
                print(f"Диапазон ID: {min(ids)} - {max(ids)}")
                
                if '50354308' in ids:
                    print("✓ ID 50354308 найден в последних вакансиях!")
                else:
                    print("✗ ID 50354308 не найден даже в последних вакансиях")
                    
        except Exception as e:
            print(f"Ошибка при получении последних вакансий: {e}")

if __name__ == "__main__":
    test_specific_vacancy()
