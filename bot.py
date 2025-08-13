import telebot
import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from database import DatabaseManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

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
            "👋 Welcome to the Questionnaire Bot!\n\n"
            "I can help you with questionnaires and data collection.\n\n"
            "Available commands:\n"
            "/start - Show this welcome message\n"
            "/schema - Show database structure\n"
            "/tables - List available tables\n"
            "/help - Show help information"
        )
        bot.reply_to(message, welcome_text)
    
    @bot.message_handler(commands=['help'])
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
        bot.reply_to(message, help_text)
    
    @bot.message_handler(commands=['schema'])
    def schema_command(message):
        """Handle /schema command to show database structure."""
        if not db_manager:
            bot.reply_to(message, "❌ Database connection not available")
            return
        
        try:
            schema = db_manager.get_database_schema()
            if not schema:
                bot.reply_to(message, "❌ Unable to retrieve database schema")
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
                    bot.reply_to(message, chunk)
            else:
                bot.reply_to(message, schema_text)
                
        except Exception as e:
            bot.reply_to(message, f"❌ Error retrieving schema: {str(e)}")
    
    @bot.message_handler(commands=['tables'])
    def tables_command(message):
        """Handle /tables command to list available tables."""
        if not db_manager:
            bot.reply_to(message, "❌ Database connection not available")
            return
        
        try:
            tables = db_manager.get_all_tables()
            if not tables:
                bot.reply_to(message, "❌ No tables found or database connection failed")
                return
            
            tables_text = "📊 Available Tables:\n\n"
            for i, table in enumerate(tables, 1):
                tables_text += f"{i}. {table}\n"
            
            bot.reply_to(message, tables_text)
            
        except Exception as e:
            bot.reply_to(message, f"❌ Error retrieving tables: {str(e)}")
    
    @bot.message_handler(func=lambda message: True)
    def handle_all_messages(message):
        """Handle all other messages - placeholder for future questionnaire logic."""
        response = (
            "💬 I received your message!\n\n"
            "Currently, I'm set up to show database information.\n"
            "Questionnaire functionality will be implemented here.\n\n"
            "Use /help to see available commands."
        )
        bot.reply_to(message, response)

# Flask routes
@app.route('/')
def home():
    """Home page for health check."""
    return jsonify({
        "status": "online",
        "service": "Telegram Questionnaire Bot",
        "message": "Bot is running successfully"
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Telegram webhook."""
    try:
        update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
        bot.process_new_updates([update])
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "database": "connected" if db_manager and db_manager.connection else "disconnected"
    })

@app.route('/set-webhook')
def set_webhook():
    """Set webhook URL for Telegram bot."""
    try:
        webhook_url = os.environ.get('WEBHOOK_URL')
        if not webhook_url:
            return jsonify({"error": "WEBHOOK_URL not set"}), 400
        
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url + '/webhook')
        
        return jsonify({
            "status": "success",
            "webhook_url": webhook_url + '/webhook'
        })
    except Exception as e:
        logger.error(f"Webhook setup error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Setup database and handlers
    if setup_database():
        logger.info("Database connected successfully")
    else:
        logger.warning("Database connection failed")
    
    setup_handlers()
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=False)
