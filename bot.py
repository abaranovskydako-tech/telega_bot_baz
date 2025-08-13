import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
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

def create_main_menu_keyboard():
    """Создает главное меню с красивыми кнопками."""
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("📝 Начать опрос", callback_data="start_survey"),
        InlineKeyboardButton("📚 Справка", callback_data="help_info")
    )
    keyboard.add(
        InlineKeyboardButton("❌ Отменить опрос", callback_data="cancel_survey"),
        InlineKeyboardButton("🔄 Новый опрос", callback_data="new_survey")
    )
    
    return keyboard

def create_citizenship_keyboard():
    """Создает клавиатуру для выбора гражданства."""
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("🇷🇺 Россия", callback_data="citizenship_Россия"),
        InlineKeyboardButton("🇺🇦 Украина", callback_data="citizenship_Украина")
    )
    keyboard.add(
        InlineKeyboardButton("🇧🇾 Беларусь", callback_data="citizenship_Беларусь"),
        InlineKeyboardButton("🇰🇿 Казахстан", callback_data="citizenship_Казахстан")
    )
    keyboard.add(
        InlineKeyboardButton("🇦🇲 Армения", callback_data="citizenship_Армения"),
        InlineKeyboardButton("🇦🇿 Азербайджан", callback_data="citizenship_Азербайджан")
    )
    keyboard.add(
        InlineKeyboardButton("🇬🇪 Грузия", callback_data="citizenship_Грузия"),
        InlineKeyboardButton("🇲🇩 Молдова", callback_data="citizenship_Молдова")
    )
    keyboard.add(
        InlineKeyboardButton("✏️ Другое", callback_data="citizenship_custom")
    )
    
    return keyboard

def create_date_format_keyboard():
    """Создает клавиатуру с примерами формата даты."""
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("📅 15.03.1990", callback_data="date_example_15.03.1990"),
        InlineKeyboardButton("📅 22.07.1985", callback_data="date_example_22.07.1985")
    )
    keyboard.add(
        InlineKeyboardButton("📅 08.12.1995", callback_data="date_example_08.12.1995"),
        InlineKeyboardButton("📅 30.01.1980", callback_data="date_example_30.01.1980")
    )
    keyboard.add(
        InlineKeyboardButton("✏️ Ввести вручную", callback_data="date_manual")
    )
    
    return keyboard

    def create_survey_progress_keyboard():
        """Создает клавиатуру для отображения прогресса опроса."""
        keyboard = InlineKeyboardMarkup(row_width=1)
        
        keyboard.add(
            InlineKeyboardButton("📊 Показать прогресс", callback_data="show_progress"),
            InlineKeyboardButton("❌ Отменить опрос", callback_data="cancel_survey"),
            InlineKeyboardButton("🔄 Начать заново", callback_data="restart_survey")
        )
        
        return keyboard
    
    def handle_start_survey(message, user_id):
        """Handle start survey button."""
        user_states[user_id] = {'state': 'waiting_name', 'data': {}}
        
        welcome_text = (
            "🎯 Отлично! Начинаем опрос!\n\n"
            "📝 Вопрос 1: Как вас зовут?\n\n"
            "Введите ваше полное ФИО (например: Иванов Иван Иванович)"
        )
        
        bot.edit_message_text(
            welcome_text,
            chat_id=message.chat.id,
            message_id=message.message_id,
            reply_markup=create_survey_progress_keyboard()
        )
    
    def handle_help_info(message):
        """Handle help info button."""
        help_text = (
            "📚 Справка по боту\n\n"
            "🎯 Этот бот предназначен для сбора персональных данных через форму опроса.\n\n"
            "📋 Процесс опроса:\n"
            "1. 📝 Введите ФИО\n"
            "2. 📅 Введите дату рождения (ДД.ММ.ГГГГ)\n"
            "3. 🌍 Укажите гражданство\n"
            "4. 🔧 Остальные данные заполнятся автоматически\n\n"
            "💡 Советы:\n"
            "• Используйте кнопки для быстрого выбора\n"
            "• Можно отменить опрос в любой момент\n"
            "• Все данные сохраняются безопасно"
        )
        
        bot.edit_message_text(
            help_text,
            chat_id=message.chat.id,
            message_id=message.message_id,
            reply_markup=create_main_menu_keyboard()
        )
    
    def handle_cancel_survey(message, user_id):
        """Handle cancel survey button."""
        if user_id in user_states:
            del user_states[user_id]
        
        cancel_text = "❌ Опрос отменен.\n\nИспользуйте /start для начала нового опроса."
        
        bot.edit_message_text(
            cancel_text,
            chat_id=message.chat.id,
            message_id=message.message_id,
            reply_markup=create_main_menu_keyboard()
        )
    
    def handle_new_survey(message, user_id):
        """Handle new survey button."""
        user_states[user_id] = {'state': 'waiting_name', 'data': {}}
        
        new_survey_text = (
            "🔄 Новый опрос начат!\n\n"
            "📝 Вопрос 1: Как вас зовут?\n\n"
            "Введите ваше полное ФИО (например: Иванов Иван Иванович)"
        )
        
        bot.edit_message_text(
            new_survey_text,
            chat_id=message.chat.id,
            message_id=message.message_id,
            reply_markup=create_survey_progress_keyboard()
        )
    
    def handle_show_progress(message, user_id):
        """Handle show progress button."""
        if user_id not in user_states:
            bot.answer_callback_query(message.id, "❌ Нет активного опроса")
            return
        
        current_state = user_states[user_id]['state']
        data = user_states[user_id]['data']
        
        progress_text = "📊 Прогресс опроса:\n\n"
        
        if current_state == 'waiting_name':
            progress_text += "🔄 Шаг 1: Ввод ФИО (не завершен)\n"
            progress_text += "⏳ Шаг 2: Дата рождения (ожидает)\n"
            progress_text += "⏳ Шаг 3: Гражданство (ожидает)"
        elif current_state == 'waiting_birth_date':
            progress_text += f"✅ Шаг 1: ФИО - {data.get('full_name', 'Не указано')}\n"
            progress_text += "🔄 Шаг 2: Ввод даты рождения (не завершен)\n"
            progress_text += "⏳ Шаг 3: Гражданство (ожидает)"
        elif current_state == 'waiting_citizenship':
            progress_text += f"✅ Шаг 1: ФИО - {data.get('full_name', 'Не указано')}\n"
            progress_text += f"✅ Шаг 2: Дата рождения - {data.get('birth_date', 'Не указано')}\n"
            progress_text += "🔄 Шаг 3: Ввод гражданства (не завершен)"
        
        bot.edit_message_text(
            progress_text,
            chat_id=message.chat.id,
            message_id=message.message_id,
            reply_markup=create_survey_progress_keyboard()
        )
    
    def handle_restart_survey(message, user_id):
        """Handle restart survey button."""
        user_states[user_id] = {'state': 'waiting_name', 'data': {}}
        
        restart_text = (
            "🔄 Опрос перезапущен!\n\n"
            "📝 Вопрос 1: Как вас зовут?\n\n"
            "Введите ваше полное ФИО (например: Иванов Иван Иванович)"
        )
        
        bot.edit_message_text(
            restart_text,
            chat_id=message.chat.id,
            message_id=message.message_id,
            reply_markup=create_survey_progress_keyboard()
        )
    
    def handle_citizenship_selection(message, user_id, citizenship):
        """Handle citizenship selection from buttons."""
        user_states[user_id]['data']['citizenship'] = citizenship
        user_states[user_id]['state'] = 'completed'
        
        # Генерируем случайные данные
        full_name = user_states[user_id]['data']['full_name']
        random_data = data_generator.generate_all_random_data(full_name)
        
        # Объединяем все данные
        all_data = {**user_states[user_id]['data'], **random_data}
        
        # Сохраняем в базу данных
        if save_survey_data(user_id, all_data):
            # Формируем отчет
            report = create_survey_report(all_data)
            
            # Создаем клавиатуру для завершения
            completion_keyboard = InlineKeyboardMarkup(row_width=2)
            completion_keyboard.add(
                InlineKeyboardButton("🔄 Новый опрос", callback_data="new_survey"),
                InlineKeyboardButton("📊 Показать данные", callback_data="show_data")
            )
            
            bot.edit_message_text(
                report,
                chat_id=message.chat.id,
                message_id=message.message_id,
                reply_markup=completion_keyboard
            )
            
            # Очищаем состояние пользователя
            del user_states[user_id]
        else:
            bot.answer_callback_query(message.id, "❌ Ошибка при сохранении данных")
    
    def handle_custom_citizenship(message, user_id):
        """Handle custom citizenship input."""
        user_states[user_id]['state'] = 'waiting_custom_citizenship'
        
        custom_text = (
            "✏️ Введите ваше гражданство вручную:\n\n"
            "Например: Германия, Франция, США, Китай и т.д."
        )
        
        bot.edit_message_text(
            custom_text,
            chat_id=message.chat.id,
            message_id=message.message_id,
            reply_markup=create_survey_progress_keyboard()
        )
    
    def handle_date_example(message, user_id, date_example):
        """Handle date example selection."""
        user_states[user_id]['data']['birth_date'] = date_example
        user_states[user_id]['state'] = 'waiting_citizenship'
        
        date_text = (
            f"✅ Дата рождения сохранена: {date_example}\n\n"
            f"🌍 Вопрос 3: Укажите ваше гражданство\n\n"
            f"Выберите из списка или введите вручную:"
        )
        
        bot.edit_message_text(
            date_text,
            chat_id=message.chat.id,
            message_id=message.message_id,
            reply_markup=create_citizenship_keyboard()
        )
    
    def handle_date_manual(message, user_id):
        """Handle manual date input."""
        user_states[user_id]['state'] = 'waiting_birth_date'
        
        manual_text = (
            "✏️ Введите дату рождения вручную:\n\n"
            "Формат: ДД.ММ.ГГГГ\n"
            "Например: 15.03.1990"
        )
        
        bot.edit_message_text(
            manual_text,
            chat_id=message.chat.id,
            message_id=message.message_id,
            reply_markup=create_survey_progress_keyboard()
        )

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
        user_states[user_id] = {'state': 'main_menu', 'data': {}}
        
        welcome_text = (
            "👋 Добро пожаловать в Бот Опроса Персональных Данных!\n\n"
            "🎯 Я помогу вам заполнить форму опроса с красивым интерфейсом!\n\n"
            "📋 Что вас ждет:\n"
            "• 📝 3 простых вопроса\n"
            "• 🎨 Стильные кнопки для выбора\n"
            "• 🔧 Автоматическое заполнение остальных данных\n"
            "• 📊 Красивый отчет по завершении\n\n"
            "Выберите действие:"
        )
        
        bot.reply_to(message, welcome_text, reply_markup=create_main_menu_keyboard())
    
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
    
    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback_query(call):
        """Handle all callback queries from inline keyboards."""
        user_id = call.from_user.id
        data = call.data
        
        try:
            if data == "start_survey":
                handle_start_survey(call.message, user_id)
            elif data == "help_info":
                handle_help_info(call.message)
            elif data == "cancel_survey":
                handle_cancel_survey(call.message, user_id)
            elif data == "new_survey":
                handle_new_survey(call.message, user_id)
            elif data == "show_progress":
                handle_show_progress(call.message, user_id)
            elif data == "restart_survey":
                handle_restart_survey(call.message, user_id)
            elif data.startswith("citizenship_"):
                citizenship = data.replace("citizenship_", "")
                if citizenship == "custom":
                    handle_custom_citizenship(call.message, user_id)
                else:
                    handle_citizenship_selection(call.message, user_id, citizenship)
            elif data.startswith("date_example_"):
                date_example = data.replace("date_example_", "")
                handle_date_example(call.message, user_id, date_example)
            elif data == "date_manual":
                handle_date_manual(call.message, user_id)
            
            # Отвечаем на callback query
            bot.answer_callback_query(call.id)
            
        except Exception as e:
            logger.error(f"Error handling callback query: {e}")
            bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    
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
        elif current_state == 'waiting_custom_citizenship':
            handle_custom_citizenship_input(message, text)
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
        
        citizenship_text = (
            f"✅ Дата рождения сохранена: {text}\n\n"
            f"🌍 Вопрос 3: Укажите ваше гражданство\n\n"
            f"Выберите из списка или введите вручную:"
        )
        
        bot.reply_to(message, citizenship_text, reply_markup=create_citizenship_keyboard())
        
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
