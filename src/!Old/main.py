from datetime import datetime

from parser import get_vacancies
from file_manager import save_to_json
from logger import setup_logging
from config import SEARCH_TEXT, EXCLUDE_TEXT

logger = setup_logging()

if __name__ == "__main__":
    logger.info("Application starts....")

    date_today = datetime.now().strftime("%Y_%m_%d")
    file_name = f"{date_today}_{SEARCH_TEXT.replace(' ', '_')}.json"

    vacancies = get_vacancies(SEARCH_TEXT, EXCLUDE_TEXT)
    save_to_json(vacancies, file_name)

    logger.info("Application finished")
