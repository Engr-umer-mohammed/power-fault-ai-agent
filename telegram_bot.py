import os
import re
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes
)
from telegram.request import HTTPXRequest
from agent import PowerFaultAgent
from file_handler import SensorFileHandler

load_dotenv()
# LOGGING
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# CONVERSATION STATE
WAITING_FOR_DATA = 1

# TELEGRAM BOT CLASS
class TelegramFaultBot:
    """
    Telegram interface for the Power Fault AI Agent.
    Handles all user interactions, commands,
    file uploads, and inline buttons.
    """

    def __init__(self):

        # Load bot token
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.bot_token:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN not found.\n"
                "Add it to your .env file:\n"
                "TELEGRAM_BOT_TOKEN=your_token_here"
            )

        # Initialize AI agent
        logger.info("Initializing Power Fault AI Agent...")
        self.agent = PowerFaultAgent()
        logger.info("Agent ready.")

        # Initialize file handler
        self.file_handler = SensorFileHandler()
        logger.info("File handler ready.")

        # Track active user sessions
        self.user_sessions = {}


    # INTERNAL HELPERS


    def _parse_sensor_input(self, text):
        """
        Parse sensor readings from plain text.

        Supports:
            Format 1: voltage_a: 220, voltage_b: 218 ...
            Format 2: 220, 218, 221, 45, 50.0

        Returns sensor_data dict or None.
        """
        sensor_data = {}

        # Format 1 — key value pairs
        kv_pattern = r"(\w+)\s*:\s*([\d.]+)"
        matches = re.findall(kv_pattern, text)

        if matches:
            for key, value in matches:
                key = key.lower().strip()
                if key in [
                    "voltage_a", "voltage_b", "voltage_c",
                    "current", "frequency"
                ]:
                    try:
                        sensor_data[key] = float(value)
                    except ValueError:
                        pass

        # Format 2 — comma separated numbers
        if not sensor_data:
            numbers = re.findall(r"[\d.]+", text)
            if len(numbers) >= 5:
                try:
                    sensor_data = {
                        "voltage_a": float(numbers[0]),
                        "voltage_b": float(numbers[1]),
                        "voltage_c": float(numbers[2]),
                        "current":   float(numbers[3]),
                        "frequency": float(numbers[4])
                    }
                except ValueError:
                    return None

        # Check all required fields present
        required = [
            "voltage_a", "voltage_b", "voltage_c",
            "current", "frequency"
        ]

        if all(k in sensor_data for k in required):
            sensor_data["location"] = (
                f"Telegram "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            return sensor_data

        return None

    async def _send_report(self, update, report):


        # Clean characters that break Telegram Markdown
        clean = (
            report
            .replace("**", "")
            .replace("##", "")
            .replace("$", "USD")
            .replace("\\(", "(")
            .replace("\\)", ")")
        )

        # Split if longer than 3800 characters
        if len(clean) > 3800:
            parts = [
                clean[i:i + 3800]
                for i in range(0, len(clean), 3800)
            ]
            for idx, part in enumerate(parts, 1):
                label = (
                    f"Part {idx} of {len(parts)}\n"
                    f"{'─' * 30}\n\n"
                )
                try:
                    await update.message.reply_text(
                        f"```\n{label}{part}\n```",
                        parse_mode="Markdown"
                    )
                except Exception:
                    # Fallback without markdown
                    await update.message.reply_text(
                        f"{label}{part}"
                    )
        else:
            try:
                await update.message.reply_text(
                    f"```\n{clean}\n```",
                    parse_mode="Markdown"
                )
            except Exception:
                # Fallback without markdown
                await update.message.reply_text(clean)

    def _main_keyboard(self):

        return InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "🔍 New Analysis",
                callback_data="analyze"
            )],
            [InlineKeyboardButton(
                "📊 View History",
                callback_data="history"
            )],
            [InlineKeyboardButton(
                "📈 Agent Status",
                callback_data="status"
            )],
        ])

    def _start_keyboard(self):
        """Welcome screen keyboard."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "🔍 Start Fault Analysis",
                callback_data="analyze"
            )],
            [InlineKeyboardButton(
                "📊 View History",
                callback_data="history"
            )],
            [InlineKeyboardButton(
                "📈 Status",
                callback_data="status"
            )],
            [InlineKeyboardButton(
                "ℹ️ About",
                callback_data="about"
            )],
        ])



    async def cmd_start(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle /start command."""

        user = update.effective_user

        text = (
            f"⚡ Hello {user.first_name}!\n"
            f"Welcome to Power Fault AI Agent.\n\n"
            f"I analyze electrical power system\n"
            f"faults using Google Gemini AI.\n\n"
            f"WHAT I CAN DO:\n"
            f"  Analyze 3-phase voltage readings\n"
            f"  Detect faults and imbalance\n"
            f"  Generate professional reports\n"
            f"  Read CSV, Excel, JSON, TXT files\n"
            f"  Remember past faults for patterns\n\n"
            f"COMMANDS:\n"
            f"  /analyze — Start fault analysis\n"
            f"  /history — View fault history\n"
            f"  /status  — Agent status\n"
            f"  /help    — Full help guide\n"
            f"  /about   — About this agent\n"
            f"  /cancel  — Cancel operation\n\n"
            f"Quick start: Press the button below\n"
            f"or upload a CSV/Excel/JSON/TXT file!"
        )

        await update.message.reply_text(
            text,
            reply_markup=self._start_keyboard()
        )

    async def cmd_help(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle /help command."""

        text = (
            "📖 HELP GUIDE\n"
            "==============\n\n"
            "FORMAT 1 — Key Value:\n"
            "  voltage_a: 220\n"
            "  voltage_b: 218\n"
            "  voltage_c: 221\n"
            "  current: 45\n"
            "  frequency: 50.0\n\n"
            "FORMAT 2 — Numbers Only:\n"
            "  220, 218, 221, 45, 50.0\n\n"
            "QUICK EXAMPLES:\n"
            "  Normal    : 220, 219, 221, 45, 50.0\n"
            "  Warning   : 220, 182, 219, 67, 49.8\n"
            "  Emergency : 210, 208, 211, 145, 47.2\n\n"
            "FILE UPLOAD:\n"
            "  Send CSV, Excel, JSON, or TXT file\n"
            "  I will analyze every row in the file\n\n"
            "CSV FILE FORMAT EXAMPLE:\n"
            "  voltage_a,voltage_b,voltage_c,current,frequency\n"
            "  220,219,221,45,50.0\n"
            "  220,182,219,67,49.8\n\n"
            "COMMANDS:\n"
            "  /analyze — Start guided analysis\n"
            "  /history — View stored faults\n"
            "  /status  — Agent status\n"
            "  /cancel  — Cancel operation"
        )

        await update.message.reply_text(text)

    async def cmd_about(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle /about command."""

        text = (
            "POWER FAULT AI AGENT\n"
            "=====================\n\n"
            "DEVELOPER\n"
            "  Name     : Umer Mohamed\n"
            "  Title    : Senior Electrical Engineer\n"
            "  LinkedIn : linkedin.com/in/engr-umer-mohammed\n"
            "  GitHub   : github.com/Engr-umer-mohammed\n"
            "  Email    : umermohammed62@gmail.com\n\n"
            "TECHNOLOGY\n"
            "  AI Model : Google Gemini 3.5 Flash\n"
            "  Framework: Python Telegram Bot\n"
            "  Storage  : JSON + Text files\n\n"
            "CAPABILITIES\n"
            "  Real-time fault detection\n"
            "  Voltage imbalance calculation\n"
            "  AI powered root cause analysis\n"
            "  Cross-session memory and learning\n"
            "  Multi-format file reading\n"
            "  Auto text report saving\n"
            "  24/7 auto reconnection\n\n"
            "Version : 2.0\n"
            "Status  : Online"
        )

        await update.message.reply_text(text)

    async def cmd_status(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle /status command."""

        total = self.agent.memory.get_total_faults()

        reports_count = 0
        if os.path.exists("reports"):
            reports_count = len([
                f for f in os.listdir("reports")
                if f.endswith(".txt")
            ])

        text = (
            "AGENT STATUS\n"
            "=============\n\n"
            f"  Faults in memory   : {total}\n"
            f"  Text reports saved : {reports_count}\n"
            f"  AI Model           : {self.agent.model}\n"
            f"  Status             : Online\n"
            f"  Auto-Reconnect     : Enabled\n"
            f"  File Support       : CSV Excel JSON TXT"
        )

        await update.message.reply_text(text)

    async def cmd_history(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle /history command."""

        total = self.agent.memory.get_total_faults()

        if total == 0:
            await update.message.reply_text(
                "No faults in memory yet.\n"
                "Use /analyze to start!"
            )
            return

        recent = self.agent.memory.get_recent_faults(
            count=5
        )

        text = (
            f"FAULT HISTORY\n"
            f"==============\n\n"
            f"Total stored: {total}\n\n"
            f"Most Recent:\n"
            f"{'─' * 35}\n"
            f"{recent}"
        )

        await update.message.reply_text(text)

    async def cmd_cancel(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle /cancel command."""

        user_id = update.effective_user.id

        if user_id in self.user_sessions:
            del self.user_sessions[user_id]

        await update.message.reply_text(
            "Operation cancelled.\n"
            "Use /analyze to start a new analysis."
        )

        return ConversationHandler.END



    async def start_analysis(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):

        logger.info("start_analysis triggered")

        user_id = update.effective_user.id
        self.user_sessions[user_id] = {
            "step": "waiting"
        }

        prompt = (
            "FAULT ANALYSIS STARTED\n"
            "=======================\n\n"
            "Enter sensor readings:\n\n"
            "Format 1 — Key Value:\n"
            "  voltage_a: 220, voltage_b: 218,\n"
            "  voltage_c: 221, current: 45,\n"
            "  frequency: 50.0\n\n"
            "Format 2 — Numbers Only:\n"
            "  220, 218, 221, 45, 50.0\n\n"
            "Or upload a CSV, Excel, JSON, TXT file.\n\n"
            "Type /cancel to cancel."
        )

        await update.message.reply_text(prompt)
        return WAITING_FOR_DATA

    async def handle_analysis_input(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):

        logger.info("handle_analysis_input triggered")

        user_id = update.effective_user.id
        user_input = update.message.text.strip()

        sensor_data = self._parse_sensor_input(user_input)

        if sensor_data is None:
            await update.message.reply_text(
                "Could not read those values.\n\n"
                "Please use this format:\n"
                "  220, 218, 221, 45, 50.0\n\n"
                "Or:\n"
                "  voltage_a: 220, voltage_b: 218,\n"
                "  voltage_c: 221, current: 45,\n"
                "  frequency: 50.0\n\n"
                "Type /cancel to cancel."
            )
            return WAITING_FOR_DATA

        thinking = await update.message.reply_text(
            "Analyzing with AI...\nPlease wait."
        )

        try:
            report = self.agent.run(sensor_data)
            await thinking.delete()
            await self._send_report(update, report)

            await update.message.reply_text(
                "Analysis complete.\n"
                "Report saved automatically.",
                reply_markup=self._main_keyboard()
            )

            if user_id in self.user_sessions:
                del self.user_sessions[user_id]

            return ConversationHandler.END

        except Exception as error:
            logger.error(f"Analysis error: {error}")
            await thinking.delete()
            await update.message.reply_text(
                f"Error during analysis:\n{str(error)}\n\n"
                "Please try again or type /cancel."
            )
            return WAITING_FOR_DATA

    # FILE UPLOAD HANDLER

    async def handle_document(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Handle uploaded files.
        Reads all rows and runs agent on each.
        """
        document = update.message.document
        file_name = document.file_name
        extension = os.path.splitext(file_name)[1].lower()

        supported = [
            ".csv", ".xlsx", ".xls", ".json", ".txt"
        ]

        if extension not in supported:
            await update.message.reply_text(
                f"Unsupported format: {extension}\n\n"
                f"Supported:\n"
                f"  CSV, Excel, JSON, TXT"
            )
            return

        processing = await update.message.reply_text(
            f"Received: {file_name}\n"
            f"Reading sensor data..."
        )

        temp_path = None

        try:
            # Download to temp folder
            tg_file = await context.bot.get_file(
                document.file_id
            )
            os.makedirs("temp", exist_ok=True)
            temp_path = os.path.join("temp", file_name)
            await tg_file.download_to_drive(temp_path)

            # Parse the file
            readings, error = self.file_handler.read_file(
                temp_path
            )

            if error:
                await processing.delete()
                await update.message.reply_text(
                    f"Could not read file:\n\n{error}"
                )
                return

            if not readings:
                await processing.delete()
                await update.message.reply_text(
                    "No valid sensor readings found.\n\n"
                    "Required columns:\n"
                    "  voltage_a, voltage_b, voltage_c,\n"
                    "  current, frequency"
                )
                return

            # Show file summary
            summary = self.file_handler.generate_file_summary(
                readings
            )
            await processing.delete()
            await update.message.reply_text(
                f"```\n{summary}\n```",
                parse_mode="Markdown"
            )

            await update.message.reply_text(
                f"Analyzing {len(readings)} readings...\n"
                f"This may take a moment."
            )

            # Analyze each reading
            # row_index avoids conflict with report slicing
            for row_index, sensor_data in enumerate(
                readings, 1
            ):
                progress = await update.message.reply_text(
                    f"Reading {row_index} of {len(readings)}..."
                )

                report = self.agent.run(sensor_data)

                await progress.delete()

                header = (
                    f"READING {row_index} of {len(readings)}\n"
                    f"Location: "
                    f"{sensor_data.get('location', 'N/A')}\n"
                    f"{'=' * 35}\n\n"
                )

                await self._send_report(
                    update,
                    header + report
                )

                # Delay between API calls
                # prevents 503 rate limit errors
                if row_index < len(readings):
                    time.sleep(3)

            await update.message.reply_text(
                f"File Analysis Complete!\n\n"
                f"Readings analyzed : {len(readings)}\n"
                f"Records in memory : "
                f"{self.agent.memory.get_total_faults()}\n"
                f"Text reports saved to reports folder.",
                reply_markup=self._main_keyboard()
            )

        except Exception as error:
            logger.error(f"File error: {error}")
            import traceback
            traceback.print_exc()
            await update.message.reply_text(
                f"Error processing file:\n{str(error)}"
            )

        finally:
            # Always clean temp file
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception as cleanup_err:
                    logger.warning(
                        f"Temp cleanup failed: {cleanup_err}"
                    )


    # BUTTON CALLBACK HANDLER

    async def button_callback(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Handle all inline keyboard button presses.
        Uses reply_text not edit_message_text
        so analyze button works correctly.
        """
        query = update.callback_query
        await query.answer()

        logger.info(f"Button: {query.data}")

        if query.data == "analyze":
            user_id = update.effective_user.id
            self.user_sessions[user_id] = {
                "step": "waiting"
            }
            await query.message.reply_text(
                "FAULT ANALYSIS STARTED\n"
                "=======================\n\n"
                "Enter sensor readings:\n\n"
                "Format 1 — Key Value:\n"
                "  voltage_a: 220, voltage_b: 218,\n"
                "  voltage_c: 221, current: 45,\n"
                "  frequency: 50.0\n\n"
                "Format 2 — Numbers Only:\n"
                "  220, 218, 221, 45, 50.0\n\n"
                "Or upload a file.\n\n"
                "Type /cancel to cancel."
            )
            return WAITING_FOR_DATA

        elif query.data == "history":
            total = self.agent.memory.get_total_faults()
            if total == 0:
                await query.message.reply_text(
                    "No faults in memory yet.\n"
                    "Use /analyze to start!"
                )
            else:
                recent = self.agent.memory.get_recent_faults(
                    count=5
                )
                await query.message.reply_text(
                    f"FAULT HISTORY\n"
                    f"==============\n\n"
                    f"Total stored: {total}\n\n"
                    f"Most Recent:\n{recent}"
                )

        elif query.data == "status":
            total = self.agent.memory.get_total_faults()
            reports_count = 0
            if os.path.exists("reports"):
                reports_count = len([
                    f for f in os.listdir("reports")
                    if f.endswith(".txt")
                ])
            await query.message.reply_text(
                "AGENT STATUS\n"
                "=============\n\n"
                f"  Faults in memory   : {total}\n"
                f"  Text reports saved : {reports_count}\n"
                f"  AI Model           : {self.agent.model}\n"
                f"  Status             : Online"
            )

        elif query.data == "about":
            await query.message.reply_text(
                "POWER FAULT AI AGENT v2.0\n\n"
                "Developer: Umer Mohamed\n"
                "Senior Electrical Power Engineer\n\n"
                "AI: Google Gemini 3.5 Flash\n"
                "Storage: JSON + Text files\n\n"
                "Features:\n"
                "  Fault detection and diagnosis\n"
                "  Cross-session memory\n"
                "  File upload support\n"
                "  Auto report saving"
            )

        elif query.data == "save_report":
            await query.message.reply_text(
                "Report Already Saved!\n\n"
                "Text file saved to reports folder.\n"
                "JSON record saved to memory.\n\n"
                "Use /history to view stored faults."
            )

        return None

    # GENERAL MESSAGE HANDLER

    async def handle_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Handle all text messages outside conversation.
        Tries to parse as sensor data automatically.
        """
        user_id = update.effective_user.id
        user_input = update.message.text

        # User is inside active analysis session
        if user_id in self.user_sessions:
            await update.message.reply_text(
                "You are in an active analysis session.\n\n"
                "Please enter your sensor readings now.\n"
                "Type /cancel to cancel."
            )
            return

        # Try to parse as sensor readings directly
        sensor_data = self._parse_sensor_input(user_input)

        if sensor_data:
            thinking = await update.message.reply_text(
                "Analyzing fault data with AI..."
            )
            try:
                report = self.agent.run(sensor_data)
                await thinking.delete()
                await self._send_report(update, report)
                await update.message.reply_text(
                    "Analysis complete.\n"
                    "Report saved automatically.",
                    reply_markup=self._main_keyboard()
                )
            except Exception as error:
                await thinking.delete()
                logger.error(f"Error: {error}")
                await update.message.reply_text(
                    f"Error: {str(error)}\n\n"
                    "Please try again."
                )
        else:
            await update.message.reply_text(
                "I am the Power Fault Detection Agent.\n\n"
                "Send sensor readings like:\n"
                "  220, 218, 221, 45, 50.0\n\n"
                "Or upload a CSV, Excel, JSON, TXT file.\n\n"
                "Type /help for full instructions.\n"
                "Type /analyze for guided analysis."
            )


# BOT RUNNER
def run_bot():
    """Build and run the Telegram bot application."""

    bot = TelegramFaultBot()

    request = HTTPXRequest(connection_pool_size=256)

    app = (
        Application.builder()
        .token(bot.bot_token)
        .request(request)
        .build()
    )

    # Conversation handler for guided analysis
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("analyze", bot.start_analysis),
            CommandHandler("analysis", bot.start_analysis),
        ],
        states={
            WAITING_FOR_DATA: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    bot.handle_analysis_input
                ),
                MessageHandler(
                    filters.Document.ALL,
                    bot.handle_document
                ),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", bot.cmd_cancel)
        ],
        allow_reentry=True
    )

    # Register handlers in priority order
    app.add_handler(
        CommandHandler("start",   bot.cmd_start)
    )
    app.add_handler(
        CommandHandler("help",    bot.cmd_help)
    )
    app.add_handler(
        CommandHandler("about",   bot.cmd_about)
    )
    app.add_handler(
        CommandHandler("status",  bot.cmd_status)
    )
    app.add_handler(
        CommandHandler("history", bot.cmd_history)
    )
    app.add_handler(
        CommandHandler("cancel",  bot.cmd_cancel)
    )
    app.add_handler(conv_handler)
    app.add_handler(
        CallbackQueryHandler(bot.button_callback)
    )
    app.add_handler(
        MessageHandler(
            filters.Document.ALL,
            bot.handle_document
        )
    )
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            bot.handle_message
        )
    )

    print("\n" + "=" * 45)
    print("  POWER FAULT AI TELEGRAM BOT v2.0")
    print("  Bot is running — Press Ctrl+C to stop")
    print("=" * 45 + "\n")

    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )


def main():
    """Main entry point with auto reconnect logic."""

    MAX_RETRIES = 5
    RETRY_DELAY = 10
    attempt = 1

    print("=" * 45)
    print("  POWER FAULT AI TELEGRAM BOT v2.0")
    print("  Starting up...")
    print("=" * 45)

    while attempt <= MAX_RETRIES:
        try:
            print(
                f"\nAttempt {attempt} of {MAX_RETRIES}: "
                f"Starting bot..."
            )
            run_bot()
            print("Bot stopped normally.")
            break

        except KeyboardInterrupt:
            print("\nBot stopped by user.")
            break

        except Exception as error:
            print(f"\nError on attempt {attempt}:")
            print(f"  Type   : {type(error).__name__}")
            print(f"  Message: {error}")

            import traceback
            traceback.print_exc()

            if attempt < MAX_RETRIES:
                print(
                    f"\nRetrying in {RETRY_DELAY} seconds..."
                )
                time.sleep(RETRY_DELAY)
            else:
                print("Max retries exceeded. Stopping.")
                break

            attempt += 1


if __name__ == "__main__":
    main()