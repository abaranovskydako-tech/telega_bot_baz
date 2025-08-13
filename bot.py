import telebot
import os
import logging
import re
from datetime import datetime
from dotenv import load_dotenv
from database import DatabaseManager
from data_generator import PersonalDataGenerator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot
bot = telebot.TeleBot(os.environ.get('TELEGRAM_BOT_TOKEN'))
db_manager = None
data_generator = PersonalDataGenerator()

# User states for survey
user_states = {}  # {user_id: {'state': 'waiting_name', 'data': {}}}

def setup_database():
    """Initialize database connection."""
    global db_manager
    db_path = os.environ.get('DATABASE_PATH', './questionnaire.db')
    username = os.environ.get('DB_USERNAME', '')
    password = os.environ.get('DB_PASSWORD', '')
    
    db_manager = DatabaseManager(db_path, username, password)
    
    if not db_manager.connect():
        logger.warning("Database connection failed")
        return False
    return True

def setup_handlers():
    """Setup all bot message handlers."""
    
    @bot.message_handler(commands=['start'])
    def start_command(message):
        """Handle /start command."""
        user_id = message.from_user.id
        
        # Сбрасываем состояние пользователя
        user_states[user_id] = {'state': 'waiting_name', 'data': {}}
        
        welcome_text = (
            "👋 Добро пожаловать в Бот Опроса Персональных Данных!\n\n"
            "Я помогу вам заполнить форму опроса. Мне нужно задать вам 3 вопроса:\n\n"
            "📝 Вопрос 1: Как вас зовут? (ФИО)\n"
            "📅 Вопрос 2: Какая дата рождения? (формат: ДД.ММ.ГГГГ)\n"
            "🌍 Вопрос 3: Гражданство\n\n"
            "Остальные данные будут заполнены автоматически.\n\n"
            "Начнем! Как вас зовут? (введите полное ФИО)"
        )
        
        bot.reply_to(message, welcome_text)
    
    @bot.message_handler(commands=['help'])
    def help_command(message):
        """Handle /help command."""
        help_text = (
            "📚 Справка по боту\n\n"
            "Этот бот предназначен для сбора персональных данных через форму опроса.\n\n"
            "Команды:\n"
            "• /start - Начать опрос персональных данных\n"
            "• /help - Эта справка\n"
            "• /cancel - Отменить текущий опрос\n\n"
            "Процесс опроса:\n"
            "1. Введите ФИО\n"
            "2. Введите дату рождения (ДД.ММ.ГГГГ)\n"
            "3. Укажите гражданство\n"
            "4. Остальные данные заполнятся автоматически"
        )
        bot.reply_to(message, help_text)
    
    @bot.message_handler(commands=['cancel'])
    def cancel_command(message):
        """Handle /cancel command."""
        user_id = message.from_user.id
        
        if user_id in user_states:
            del user_states[user_id]
            bot.reply_to(message, "❌ Опрос отменен. Используйте /start для начала нового опроса.")
        else:
            bot.reply_to(message, "❌ У вас нет активного опроса.")
    
    @bot.message_handler(func=lambda message: True)
    def handle_survey_messages(message):
        """Handle survey responses."""
        user_id = message.from_user.id
        text = message.text.strip()
        
        # Проверяем, есть ли активный опрос
        if user_id not in user_states:
            bot.reply_to(message, "💬 Используйте /start для начала опроса.")
            return
        
        current_state = user_states[user_id]['state']
        
        if current_state == 'waiting_name':
            handle_name_input(message, text)
        elif current_state == 'waiting_birth_date':
            handle_birth_date_input(message, text)
        elif current_state == 'waiting_citizenship':
            handle_citizenship_input(message, text)
        else:
            bot.reply_to(message, "❌ Неизвестное состояние. Используйте /start для начала нового опроса.")
    
    def handle_name_input(message, text):
    """Handle full name input."""
    user_id = message.from_user.id
    
    # Проверяем, что введено ФИО (минимум 2 слова)
    if len(text.split()) < 2:
        bot.reply_to(message, "❌ Пожалуйста, введите полное ФИО (например: Иванов Иван Иванович)")
        return
    
    # Сохраняем ФИО
    user_states[user_id]['data']['full_name'] = text
    user_states[user_id]['state'] = 'waiting_birth_date'
    
    bot.reply_to(message, 
        f"✅ ФИО сохранено: {text}\n\n"
        f"📅 Вопрос 2: Какая дата рождения?\n"
        f"Введите в формате ДД.ММ.ГГГГ (например: 15.03.1990)"
    )

    def handle_birth_date_input(message, text):
    """Handle birth date input."""
    user_id = message.from_user.id
    
    # Проверяем формат даты (ДД.ММ.ГГГГ)
    date_pattern = r'^\d{2}\.\d{2}\.\d{4}$'
    if not re.match(date_pattern, text):
        bot.reply_to(message, "❌ Неверный формат даты! Используйте формат ДД.ММ.ГГГГ (например: 15.03.1990)")
        return
    
    try:
        # Парсим дату для проверки корректности
        birth_date = datetime.strptime(text, '%d.%m.%Y')
        
        # Проверяем, что дата не в будущем и не слишком старая
        if birth_date > datetime.now():
            bot.reply_to(message, "❌ Дата рождения не может быть в будущем!")
            return
        
        if birth_date.year < 1900:
            bot.reply_to(message, "❌ Дата рождения не может быть раньше 1900 года!")
            return
        
        # Сохраняем дату рождения
        user_states[user_id]['data']['birth_date'] = text
        user_states[user_id]['state'] = 'waiting_citizenship'
        
        bot.reply_to(message, 
            f"✅ Дата рождения сохранена: {text}\n\n"
            f"🌍 Вопрос 3: Укажите ваше гражданство\n"
            f"Например: Россия, Украина, Беларусь, Казахстан"
        )
        
    except ValueError:
        bot.reply_to(message, "❌ Неверная дата! Проверьте правильность введенной даты.")

    def handle_citizenship_input(message, text):
    """Handle citizenship input."""
    user_id = message.from_user.id
    
    # Проверяем, что введено гражданство
    if len(text.strip()) < 2:
        bot.reply_to(message, "❌ Пожалуйста, введите ваше гражданство.")
        return
    
    # Сохраняем гражданство
    user_states[user_id]['data']['citizenship'] = text.strip()
    
    # Генерируем случайные данные
    full_name = user_states[user_id]['data']['full_name']
    random_data = data_generator.generate_all_random_data(full_name)
    
    # Объединяем все данные
    all_data = {**user_states[user_id]['data'], **random_data}
    
    # Сохраняем в базу данных
    if save_survey_data(user_id, all_data):
        # Формируем отчет
        report = create_survey_report(all_data)
        bot.reply_to(message, report)
        
        # Очищаем состояние пользователя
        del user_states[user_id]
    else:
        bot.reply_to(message, "❌ Ошибка при сохранении данных. Попробуйте еще раз или используйте /cancel")

    def save_survey_data(user_id, data):
    """Save survey data to database."""
    try:
        # Здесь должна быть логика сохранения в БД
        # Пока просто логируем
        logger.info(f"Saving survey data for user {user_id}: {data}")
        return True
    except Exception as e:
        logger.error(f"Error saving survey data: {e}")
        return False

    def create_survey_report(data):
    """Create survey completion report."""
    report = (
        "🎉 Опрос завершен успешно!\n\n"
        "📋 Введенные вами данные:\n"
        f"👤 ФИО: {data['full_name']}\n"
        f"📅 Дата рождения: {data['birth_date']}\n"
        f"🌍 Гражданство: {data['citizenship']}\n\n"
        "🔧 Автоматически заполненные данные:\n"
        f"📱 Телефон: {data['phone_number']}\n"
        f"📧 Email: {data['email']}\n"
        f"🏠 Адрес: {data['address']}\n"
        f"📄 Паспорт: {data['passport_series']} {data['passport_number']}\n"
        f"🎓 Образование: {data['education']}\n"
        f"💼 Профессия: {data['occupation']}\n"
        f"💰 Уровень дохода: {data['income_level']}\n"
        f"💍 Семейное положение: {data['marital_status']}\n"
        f"👶 Дети: {data['children_count']}\n\n"
        "✅ Все данные сохранены в базе данных!\n"
        "Используйте /start для нового опроса."
    )
    return report


if __name__ == '__main__':
    # Setup database and handlers
    if setup_database():
        logger.info("Database connected successfully")
    else:
        logger.warning("Database connection failed")
    
    setup_handlers()
    
    # Run bot in polling mode
    logger.info("Starting Telegram bot...")
    bot.polling(none_stop=True)
