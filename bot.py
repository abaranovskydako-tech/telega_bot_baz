import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import os
import logging
import re
from datetime import datetime
from dotenv import load_dotenv
import database
from data_generator import PersonalDataGenerator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot
bot = telebot.TeleBot(os.environ.get('TELEGRAM_BOT_TOKEN'))
data_generator = PersonalDataGenerator()

# User states for survey
user_states = {}  # {user_id: {'state': 'waiting_name', 'data': {}}

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

def create_new_survey_keyboard():
    """Создает клавиатуру для завершения опроса с кнопкой нового опроса."""
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    keyboard.add(
        InlineKeyboardButton("🚀 Начать новый опрос", callback_data="new_survey")
    )
    
    return keyboard

def save_survey_data(user_id, data):
    """Save survey data to database."""
    try:
        # Сохраняем только данные пользователя в новую БД
        full_name = data.get('full_name', '')
        birth_date = data.get('birth_date', '')
        citizenship = data.get('citizenship', '')
        
        # Конвертируем дату из формата ДД.ММ.ГГГГ в формат для PostgreSQL
        if birth_date:
            try:
                # Парсим дату и конвертируем в формат YYYY-MM-DD
                parsed_date = datetime.strptime(birth_date, '%d.%m.%Y')
                birth_date = parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                logger.error(f"Invalid date format: {birth_date}")
                birth_date = None
        
        # Сохраняем в базу данных
        new_id = database.save_response(user_id, full_name, birth_date, citizenship)
        logger.info(f"Survey data saved successfully for user {user_id} with ID {new_id}")
        return True
    except Exception as e:
        logger.error(f"Error saving survey data: {e}")
        return False

def create_survey_report(data):
    """Create survey completion report showing only user-entered data."""
    # Определяем поля, которые пользователь ввел сам
    user_entered_fields = {
        'full_name': '👤 ФИО',
        'birth_date': '📅 Дата рождения', 
        'citizenship': '🌍 Гражданство'
    }
    
    # Определяем поля, которые заполняются автоматически
    auto_filled_fields = {
        'phone_number': '📱 Телефон',
        'email': '📧 Email',
        'address': '🏠 Адрес',
        'passport_series': '📄 Паспорт (серия)',
        'passport_number': '📄 Паспорт (номер)',
        'education': '🎓 Образование',
        'occupation': '💼 Профессия',
        'income_level': '💰 Уровень дохода',
        'marital_status': '💍 Семейное положение',
        'children_count': '👶 Дети'
    }
    
    # Формируем отчет только с данными пользователя
    report = "🎉 Опрос завершен успешно!\n\n"
    report += "📋 Введенные вами данные:\n"
    
    for field, label in user_entered_fields.items():
        if field in data and data[field]:
            report += f"{label}: {data[field]}\n"
    
    report += "\n✅ Все данные сохранены в базе данных!"
    
    return report

def setup_database():
    """Setup database connection."""
    try:
        # Инициализируем базу данных
        database.init_db()
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return False

def setup_handlers():
    """Setup all bot message handlers."""
    def handle_start_survey(message, user_id):
        """Handle start survey button."""
        user_states[user_id] = {'state': 'waiting_name', 'data': {}}
        
        bot.edit_message_text(
            "📝 Начинаем опрос!\n\n"
            "🌍 Вопрос 1: Введите ваше полное ФИО\n\n"
            "Пример: Иванов Иван Иванович",
            chat_id=message.chat.id,
            message_id=message.message_id
        )
        
        # Отправляем сообщение с просьбой ввести ФИО
        bot.send_message(message.chat.id, "✍️ Введите ваше ФИО:")

    def handle_help_info(message):
        """Handle help info button."""
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
            "4. Получите отчет с вашими данными"
        )
        bot.edit_message_text(help_text, chat_id=message.chat.id, message_id=message.message_id)

    def handle_cancel_survey(message, user_id):
        """Handle cancel survey button."""
        if user_id in user_states:
            del user_states[user_id]
            bot.edit_message_text("❌ Опрос отменен.", chat_id=message.chat.id, message_id=message.message_id)
            bot.send_message(message.chat.id, "Используйте /start для начала нового опроса.")
        else:
            bot.answer_callback_query(message.id, "❌ У вас нет активного опроса.")

    def handle_new_survey(message, user_id):
        """Handle new survey button."""
        # Сбрасываем состояние и начинаем заново
        user_states[user_id] = {'state': 'waiting_name', 'data': {}}
        
        bot.edit_message_text(
            "🔄 Начинаем новый опрос!\n\n"
            "🌍 Вопрос 1: Введите ваше полное ФИО\n\n"
            "Пример: Иванов Иван Иванович",
            chat_id=message.chat.id,
            message_id=message.message_id
        )
        
        bot.send_message(message.chat.id, "✍️ Введите ваше ФИО:")

    def handle_show_progress(message, user_id):
        """Handle show progress button."""
        if user_id not in user_states:
            bot.answer_callback_query(message.id, "❌ У вас нет активного опроса.")
            return
        
        current_state = user_states[user_id]['state']
        data = user_states[user_id]['data']
        
        progress_text = "📊 Прогресс опроса:\n\n"
        
        if 'full_name' in data:
            progress_text += f"✅ ФИО: {data['full_name']}\n"
        else:
            progress_text += "❌ ФИО: не заполнено\n"
        
        if 'birth_date' in data:
            progress_text += f"✅ Дата рождения: {data['birth_date']}\n"
        else:
            progress_text += "❌ Дата рождения: не заполнено\n"
        
        if 'citizenship' in data:
            progress_text += f"✅ Гражданство: {data['citizenship']}\n"
        else:
            progress_text += "❌ Гражданство: не заполнено\n"
        
        progress_text += f"\n🎯 Текущий этап: {current_state}"
        
        bot.edit_message_text(progress_text, chat_id=message.chat.id, message_id=message.message_id)

    def handle_restart_survey(message, user_id):
        """Handle restart survey button."""
        # Сбрасываем состояние и начинаем заново
        user_states[user_id] = {'state': 'waiting_name', 'data': {}}
        
        bot.edit_message_text(
            "🔄 Опрос перезапущен!\n\n"
            "🌍 Вопрос 1: Введите ваше полное ФИО\n\n"
            "Пример: Иванов Иван Иванович",
            chat_id=message.chat.id,
            message_id=message.message_id
        )
        
        bot.send_message(message.chat.id, "✍️ Введите ваше ФИО:")

    def handle_citizenship_selection(message, user_id, citizenship):
        """Handle citizenship selection from keyboard."""
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
            bot.edit_message_text("✅ Гражданство выбрано!", chat_id=message.chat.id, message_id=message.message_id)
            bot.send_message(message.chat.id, report, reply_markup=create_new_survey_keyboard())
            
            # Очищаем состояние пользователя
            del user_states[user_id]
        else:
            bot.edit_message_text("❌ Ошибка при сохранении данных.", chat_id=message.chat.id, message_id=message.message_id)

    def handle_custom_citizenship(message, user_id):
        """Handle custom citizenship input request."""
        user_states[user_id]['state'] = 'waiting_custom_citizenship'
        
        bot.edit_message_text(
            "✏️ Введите ваше гражданство вручную:",
            chat_id=message.chat.id,
            message_id=message.message_id
        )

    def handle_date_example(message, user_id, date_example):
        """Handle date example selection."""
        user_states[user_id]['data']['birth_date'] = date_example
        user_states[user_id]['state'] = 'waiting_citizenship'
        
        citizenship_text = (
            f"✅ Дата рождения выбрана: {date_example}\n\n"
            f"🌍 Вопрос 3: Укажите ваше гражданство\n\n"
            "Выберите из списка или введите вручную:"
        )
        
        bot.edit_message_text(citizenship_text, chat_id=message.chat.id, message_id=message.message_id)
        bot.send_message(message.chat.id, "Выберите гражданство:", reply_markup=create_citizenship_keyboard())

    def handle_date_manual(message, user_id):
        """Handle manual date input request."""
        user_states[user_id]['state'] = 'waiting_birth_date'
        
        bot.edit_message_text(
            "✏️ Введите дату рождения в формате ДД.ММ.ГГГГ\n\n"
            "Пример: 15.03.1990",
            chat_id=message.chat.id,
            message_id=message.message_id
        )

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
            f"Введите в формате ДД.ММ.ГГГГ (например: 15.03.1990)",
            reply_markup=create_date_format_keyboard()
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
                "Выберите из списка или введите вручную:"
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
            bot.reply_to(message, report, reply_markup=create_new_survey_keyboard())
            
            # Очищаем состояние пользователя
            del user_states[user_id]
        else:
            bot.reply_to(message, "❌ Ошибка при сохранении данных. Попробуйте еще раз или используйте /cancel")

    def handle_custom_citizenship_input(message, text):
        """Handle custom citizenship input."""
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
            bot.reply_to(message, report, reply_markup=create_new_survey_keyboard())
            
            # Очищаем состояние пользователя
            del user_states[user_id]
        else:
            bot.reply_to(message, "❌ Ошибка при сохранении данных. Попробуйте еще раз или используйте /cancel")
    
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
            "4. Получите отчет с вашими данными"
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

# --- универсальный запуск бота ---
def run_bot():
    """Запуск телеграм-бота."""
    # Setup database and handlers
    if setup_database():
        logger.info("Database connected successfully")
    else:
        logger.warning("Database connection failed")
    
    setup_handlers()
    
    # Run bot in polling mode
    logger.info("Starting Telegram bot...")
    bot.polling(none_stop=True)

if __name__ == "__main__":
    run_bot()
