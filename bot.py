import telebot
import os
from dotenv import load_dotenv
from database import DatabaseManager

load_dotenv()

class TelegramBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found")
            
        self.bot = telebot.TeleBot(self.token)
        self.db_manager = None
        self.setup_database()
        self.setup_handlers()
    
    def setup_database(self):
        db_path = os.getenv('DATABASE_PATH', './questionnaire.db')
        username = os.getenv('DB_USERNAME', '')
        password = os.getenv('DB_PASSWORD', '')
        
        self.db_manager = DatabaseManager(db_path, username, password)
        
        if not self.db_manager.connect():
            print("Database connection failed")
    
    def setup_handlers(self):
        """Setup all bot message handlers."""
        
        @self.bot.message_handler(commands=['start'])
        def start_command(message):
            """Handle /start command."""
            welcome_text = (
                "👋 Welcome to the Questionnaire Bot!\n\n"
                "I can help you with questionnaires and data collection.\n\n"
                "Available commands:\n"
                "/start - Show this welcome message\n"
                "/schema - Show database structure\n"
                "/tables - List available tables\n"
                "/help - Show help information"
            )
            self.bot.reply_to(message, welcome_text)
        
        @self.bot.message_handler(commands=['help'])
        def help_command(message):
            """Handle /help command."""
            help_text = (
                "📚 Bot Help\n\n"
                "This bot is designed to collect questionnaire data and store it in a database.\n\n"
                "Commands:\n"
                "• /start - Welcome message\n"
                "• /schema - View database structure\n"
                "• /tables - List database tables\n"
                "• /help - This help message\n\n"
                "The bot will dynamically adapt to your existing database structure."
            )
            self.bot.reply_to(message, help_text)
        
        @self.bot.message_handler(commands=['schema'])
        def schema_command(message):
            """Handle /schema command to show database structure."""
            if not self.db_manager:
                self.bot.reply_to(message, "❌ Database connection not available")
                return
            
            try:
                schema = self.db_manager.get_database_schema()
                if not schema:
                    self.bot.reply_to(message, "❌ Unable to retrieve database schema")
                    return
                
                schema_text = "🗄️ Database Schema:\n\n"
                for table_name, columns in schema.items():
                    schema_text += f"📋 Table: {table_name}\n"
                    for col in columns:
                        pk_marker = " 🔑" if col['pk'] else ""
                        null_marker = " ❌" if col['notnull'] else " ✅"
                        schema_text += f"  • {col['name']} ({col['type']}){pk_marker}{null_marker}\n"
                    schema_text += "\n"
                
                # Split long messages if needed
                if len(schema_text) > 4096:
                    for i in range(0, len(schema_text), 4096):
                        chunk = schema_text[i:i+4096]
                        self.bot.reply_to(message, chunk)
                else:
                    self.bot.reply_to(message, schema_text)
                    
            except Exception as e:
                self.bot.reply_to(message, f"❌ Error retrieving schema: {str(e)}")
        
        @self.bot.message_handler(commands=['tables'])
        def tables_command(message):
            """Handle /tables command to list available tables."""
            if not self.db_manager:
                self.bot.reply_to(message, "❌ Database connection not available")
                return
            
            try:
                tables = self.db_manager.get_all_tables()
                if not tables:
                    self.bot.reply_to(message, "❌ No tables found or database connection failed")
                    return
                
                tables_text = "📊 Available Tables:\n\n"
                for i, table in enumerate(tables, 1):
                    tables_text += f"{i}. {table}\n"
                
                self.bot.reply_to(message, tables_text)
                
            except Exception as e:
                self.bot.reply_to(message, f"❌ Error retrieving tables: {str(e)}")
        
        @self.bot.message_handler(func=lambda message: True)
        def handle_all_messages(message):
            """Handle all other messages - placeholder for future questionnaire logic."""
            # This is where future questionnaire logic will be implemented
            response = (
                "💬 I received your message!\n\n"
                "Currently, I'm set up to show database information.\n"
                "Questionnaire functionality will be implemented here.\n\n"
                "Use /help to see available commands."
            )
            self.bot.reply_to(message, response)
    
    def run(self):
        """Start the bot."""
        print("🤖 Starting Telegram bot...")
        try:
            self.bot.polling(none_stop=True)
        except KeyboardInterrupt:
            print("\n🛑 Bot stopped by user")
        except Exception as e:
            print(f"❌ Bot error: {e}")
        finally:
            if self.db_manager:
                self.db_manager.disconnect()
            print("🔌 Database connection closed")

if __name__ == "__main__":
    try:
        bot = TelegramBot()
        bot.run()
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
