
import json
import logging
from src.api_modules.sj_api import SuperJobAPI
from src.vacancies.parsers.sj_parser import SuperJobParser
from src.vacancies.models import Vacancy

# Настроим логирование
logging.basicConfig(level=logging.INFO)

def debug_vacancy_by_id(vacancy_id: str):
    """Отладка конкретной вакансии SuperJob по ID"""
    print(f"=== Отладка вакансии SuperJob ID: {vacancy_id} ===")
    
    # Инициализируем API и парсер
    sj_api = SuperJobAPI()
    parser = SuperJobParser()
    
    # Ищем вакансию в кэше
    cache_files = []
    import os
    cache_dir = "data/cache/sj"
    
    if os.path.exists(cache_dir):
        for filename in os.listdir(cache_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(cache_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'objects' in data:
                            for vacancy in data['objects']:
                                if str(vacancy.get('id')) == vacancy_id:
                                    print(f"\nНайдена вакансия в кэше: {filename}")
                                    print(f"Название: {vacancy.get('profession', 'Не указано')}")
                                    print(f"ID: {vacancy.get('id')}")
                                    print(f"URL: {vacancy.get('link', 'Не указан')}")
                                    
                                    # Извлекаем текст для анализа ключевых слов
                                    description = vacancy.get('vacancyRichText', '')
                                    candidat = vacancy.get('candidat', '')
                                    work = vacancy.get('work', '')
                                    
                                    full_text = f"{description} {candidat} {work}".lower()
                                    
                                    print(f"\nАнализ текста на наличие 'excel':")
                                    print(f"Длина полного текста: {len(full_text)} символов")
                                    
                                    # Ищем все вхождения excel
                                    excel_positions = []
                                    pos = 0
                                    while True:
                                        pos = full_text.find('excel', pos)
                                        if pos == -1:
                                            break
                                        excel_positions.append(pos)
                                        pos += 1
                                    
                                    if excel_positions:
                                        print(f"Найдено {len(excel_positions)} вхождений 'excel' в позициях: {excel_positions}")
                                        
                                        # Показываем контекст для каждого вхождения
                                        for i, pos in enumerate(excel_positions):
                                            start = max(0, pos - 30)
                                            end = min(len(full_text), pos + 35)
                                            context = full_text[start:end]
                                            print(f"  Контекст {i+1}: ...{context}...")
                                    else:
                                        print("Слово 'excel' НЕ найдено в тексте")
                                    
                                    # Тестируем парсер
                                    print(f"\n=== Тестирование парсера ===")
                                    try:
                                        sj_vacancy = parser.parse_vacancy(vacancy)
                                        unified_data = parser.convert_to_unified_format(sj_vacancy)
                                        vacancy_obj = Vacancy.from_dict(unified_data)
                                        
                                        print(f"Извлеченные ключевые слова: {vacancy_obj.keywords}")
                                        
                                        # Покажем процесс извлечения ключевых слов
                                        print(f"\n=== Процесс извлечения ключевых слов ===")
                                        keywords_list = ['python', 'java', 'javascript', 'react', 'angular', 'vue', 'sql', 'postgresql', 'mysql', 'excel', 'word', 'powerpoint', '1c', 'git', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'linux', 'windows', 'macos', 'html', 'css', 'bootstrap', 'jquery', 'typescript', 'php', 'laravel', 'symfony', 'django', 'flask', 'spring', 'hibernate', 'maven', 'gradle', 'npm', 'yarn', 'webpack', 'babel', 'sass', 'less', 'mongodb', 'redis', 'elasticsearch', 'kafka', 'rabbitmq', 'jenkins', 'gitlab', 'jira', 'confluence', 'figma', 'photoshop', 'illustrator']
                                        
                                        found_keywords = []
                                        for keyword in keywords_list:
                                            import re
                                            pattern = r'\b' + re.escape(keyword) + r'\b'
                                            if re.search(pattern, full_text):
                                                found_keywords.append(keyword)
                                                if keyword == 'excel':
                                                    print(f"✓ Найдено ключевое слово: {keyword}")
                                        
                                        print(f"Все найденные ключевые слова: {found_keywords}")
                                        
                                    except Exception as e:
                                        print(f"Ошибка при парсинге: {e}")
                                    
                                    return vacancy
                                    
                except Exception as e:
                    print(f"Ошибка чтения файла {filename}: {e}")
    
    print(f"Вакансия с ID {vacancy_id} не найдена в кэше")
    return None

if __name__ == "__main__":
    debug_vacancy_by_id("50354308")
