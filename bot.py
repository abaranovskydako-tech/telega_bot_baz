import telebot
import os
import logging
from dotenv import load_dotenv
from database import DatabaseManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot
bot = telebot.TeleBot(os.environ.get('TELEGRAM_BOT_TOKEN'))
db_manager = None

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
        welcome_text = (
            "👋 Добро пожаловать в Бот Опросов!\n\n"
            "Я помогу вам с проведением опросов и сбором данных.\n\n"
            "Доступные команды:\n"
            "/start - Показать это приветственное сообщение\n"
            "/schema - Показать структуру базы данных\n"
            "/tables - Список доступных таблиц\n"
            "/help - Показать справку"
        )
        bot.reply_to(message, welcome_text)
    
    @bot.message_handler(commands=['help'])
    def help_command(message):
        """Handle /help command."""
        help_text = (
            "📚 Справка по боту\n\n"
            "Этот бот предназначен для сбора данных опросов и сохранения их в базе данных.\n\n"
            "Команды:\n"
            "• /start - Приветственное сообщение\n"
            "• /schema - Просмотр структуры базы данных\n"
            "• /tables - Список таблиц базы данных\n"
            "• /help - Эта справка\n\n"
            "Бот будет динамически адаптироваться к существующей структуре вашей базы данных."
        )
        bot.reply_to(message, welcome_text)
    
    @bot.message_handler(commands=['schema'])
    def schema_command(message):
        """Handle /schema command to show database structure."""
        if not db_manager:
            bot.reply_to(message, "❌ Подключение к базе данных недоступно")
            return
        
        try:
            schema = db_manager.get_database_schema()
            if not schema:
                bot.reply_to(message, "❌ Не удалось получить схему базы данных")
                return
            
            schema_text = "🗄️ Схема базы данных:\n\n"
            for table_name, columns in schema.items():
                schema_text += f"📋 Таблица: {table_name}\n"
                for col in columns:
                    pk_marker = " 🔑" if col['pk'] else ""
                    null_marker = " ❌" if col['notnull'] else " ✅"
                    schema_text += f"  • {col['name']} ({col['type']}){pk_marker}{null_marker}\n"
                schema_text += "\n"
            
            # Split long messages if needed
            if len(schema_text) > 4096:
                for i in range(0, len(schema_text), 4096):
                    chunk = schema_text[i:i+4096]
                    bot.reply_to(message, chunk)
            else:
                bot.reply_to(message, schema_text)
                
        except Exception as e:
            bot.reply_to(message, f"❌ Ошибка при получении схемы: {str(e)}")
    
    @bot.message_handler(commands=['tables'])
    def tables_command(message):
        """Handle /tables command to list available tables."""
        if not db_manager:
            bot.reply_to(message, "❌ Подключение к базе данных недоступно")
            return
        
        try:
            tables = db_manager.get_all_tables()
            if not tables:
                bot.reply_to(message, "❌ Таблицы не найдены или подключение к базе данных не удалось")
                return
            
            tables_text = "📊 Доступные таблицы:\n\n"
            for i, table in enumerate(tables, 1):
                tables_text += f"{i}. {table}\n"
            
            bot.reply_to(message, tables_text)
            
        except Exception as e:
            bot.reply_to(message, f"❌ Ошибка при получении таблиц: {str(e)}")
    
    @bot.message_handler(func=lambda message: True)
    def handle_all_messages(message):
        """Handle all other messages - placeholder for future questionnaire logic."""
        response = (
            "💬 Я получил ваше сообщение!\n\n"
            "В настоящее время я настроен на показ информации о базе данных.\n"
            "Функциональность опросов будет реализована здесь.\n\n"
            "Используйте /help для просмотра доступных команд."
        )
        bot.reply_to(message, response)



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
