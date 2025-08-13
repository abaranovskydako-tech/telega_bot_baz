import random
import string
from datetime import datetime, timedelta

class PersonalDataGenerator:
    """Генератор случайных персональных данных."""
    
    def __init__(self):
        self.phone_prefixes = ['+7', '+375', '+380', '+48', '+49']
        self.email_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'yandex.ru']
        self.cities = ['Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Казань']
        self.streets = ['Ленина', 'Пушкина', 'Гагарина', 'Мира', 'Советская']
        self.education_levels = ['Среднее', 'Среднее специальное', 'Высшее', 'Бакалавриат', 'Магистратура']
        self.occupations = ['Инженер', 'Программист', 'Менеджер', 'Учитель', 'Врач', 'Юрист']
        self.income_levels = ['Низкий', 'Средний', 'Высокий', 'Очень высокий']
        self.marital_statuses = ['Холост/Не замужем', 'Женат/Замужем', 'Разведен/Разведена', 'Вдовец/Вдова']
    
    def generate_phone_number(self):
        """Генерирует случайный номер телефона."""
        prefix = random.choice(self.phone_prefixes)
        if prefix == '+7':  # Российский формат
            number = ''.join([str(random.randint(0, 9)) for _ in range(10)])
            return f"+7{number}"
        else:  # Другие страны
            number = ''.join([str(random.randint(0, 9)) for _ in range(9)])
            return f"{prefix}{number}"
    
    def generate_email(self, full_name):
        """Генерирует email на основе ФИО."""
        # Убираем пробелы и приводим к нижнему регистру
        name_parts = full_name.lower().replace(' ', '')
        # Добавляем случайные цифры
        random_numbers = ''.join([str(random.randint(0, 9)) for _ in range(3)])
        domain = random.choice(self.email_domains)
        return f"{name_parts}{random_numbers}@{domain}"
    
    def generate_address(self):
        """Генерирует случайный адрес."""
        city = random.choice(self.cities)
        street = random.choice(self.streets)
        house = random.randint(1, 200)
        apartment = random.randint(1, 100)
        return f"{city}, ул. {street}, д. {house}, кв. {apartment}"
    
    def generate_passport_data(self):
        """Генерирует случайные паспортные данные."""
        series = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        number = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        issued_by = f"УФМС России по {random.choice(self.cities)}"
        
        # Дата выдачи (в пределах последних 10 лет)
        years_ago = random.randint(1, 10)
        issue_date = datetime.now() - timedelta(days=365*years_ago)
        issue_date_str = issue_date.strftime("%d.%m.%Y")
        
        return {
            'series': series,
            'number': number,
            'issued_by': issued_by,
            'issue_date': issue_date_str
        }
    
    def generate_inn(self):
        """Генерирует случайный ИНН."""
        return ''.join([str(random.randint(0, 9)) for _ in range(12)])
    
    def generate_snils(self):
        """Генерирует случайный СНИЛС."""
        numbers = ''.join([str(random.randint(0, 9)) for _ in range(9)])
        control = ''.join([str(random.randint(0, 9)) for _ in range(2)])
        return f"{numbers[:3]}-{numbers[3:6]}-{numbers[6:9]} {control}"
    
    def generate_education(self):
        """Генерирует случайное образование."""
        return random.choice(self.education_levels)
    
    def generate_occupation(self):
        """Генерирует случайную профессию."""
        return random.choice(self.occupations)
    
    def generate_income_level(self):
        """Генерирует случайный уровень дохода."""
        return random.choice(self.income_levels)
    
    def generate_marital_status(self):
        """Генерирует случайный семейный статус."""
        return random.choice(self.marital_statuses)
    
    def generate_children_count(self):
        """Генерирует случайное количество детей."""
        return random.randint(0, 5)
    
    def generate_all_random_data(self, full_name):
        """Генерирует все случайные данные для заполнения таблицы."""
        passport_data = self.generate_passport_data()
        
        return {
            'phone_number': self.generate_phone_number(),
            'email': self.generate_email(full_name),
            'address': self.generate_address(),
            'passport_number': passport_data['number'],
            'passport_series': passport_data['series'],
            'passport_issued_by': passport_data['issued_by'],
            'passport_issue_date': passport_data['issue_date'],
            'inn': self.generate_inn(),
            'snils': self.generate_snils(),
            'education': self.generate_education(),
            'occupation': self.generate_occupation(),
            'income_level': self.generate_income_level(),
            'marital_status': self.generate_marital_status(),
            'children_count': self.generate_children_count()
        }
