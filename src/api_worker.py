from abc import ABC, abstractmethod


class BaseAPI(ABC):
    """Абстрактный класс для работы с API"""
    pass

    @abstractmethod
    def connect_to_api(self):
        """Абстрактный метод, вынуждает дочерние классы переопределять метод 'connect_to_api'"""


    @abstractmethod
    def load_vacancies(self):
        """Абстрактный метод, вынуждает дочерние классы переопределять метод 'connect_to_api'"""

class HeadHunterAPI(BaseAPI):
    def connect_to_api(self):
        pass

    def load_vacancies(self):
        pass
