from parsers.work_ua_parser import WorkUaParser
from parsers.robota_ua_parser import RobotaUaParser
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes
import os

load_dotenv()
TOKEN = os.getenv('TOKEN')

# Stages of the conversation
JOB_POSITION, LOCATION, SALARY, EXPERIENCE, ENGLISH_LANGUAGE, KEYWORDS, SITE_SELECTION, RESUME_COUNT = range(8)

# Initialize the bot
application = Application.builder().token(TOKEN).build()

# Start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I am a bot that helps you find resumes for a given job position. \n"
        "You can search for resumes on Work.ua and Robota.ua.\n"
        "To get started, enter /search."
    )

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Here are the available commands:\n"
        "/start - Starts the bot\n"
        "/search - Starts a resume search\n"
        "/help - Shows this message"
    )

# Start search command
async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Enter the job position (e.g., Data Scientist, Web Developer):")
    return JOB_POSITION

# Conversation steps
async def job_position_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["job_position"] = update.message.text
    await update.message.reply_text("Enter the location (e.g., Kyiv, Lviv or type '-' to skip):")
    return LOCATION

async def location_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["location"] = update.message.text
    await update.message.reply_text("Enter salary expectation (e.g., 20000 or type '-' to skip):")
    return SALARY

async def salary_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    salary_input = update.message.text
    context.user_data["salary"] = None if salary_input == "-" else salary_input
    await update.message.reply_text("Enter minimum years of experience (e.g., 7 or type '-' to skip):")
    return EXPERIENCE

async def experience_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    experience_input = update.message.text
    context.user_data["years_of_experience"] = None if experience_input == "-" else experience_input
    await update.message.reply_text("Is English required? ('yes' or type '-' to skip):")
    return ENGLISH_LANGUAGE

async def english_language_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["english_language"] = update.message.text.lower()
    await update.message.reply_text("Enter keywords (e.g., data analyst python sql or type '-' to skip):")
    return KEYWORDS

async def keywords_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["keywords"] = update.message.text
    await update.message.reply_text("Which site do you want to search resumes on?\n1. Work.ua\n2. Robota.ua")
    return SITE_SELECTION

async def site_selection_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    site_choice = update.message.text.strip()

    if site_choice == "1":
        parser_class, site_name = WorkUaParser, "Work.ua"
    elif site_choice == "2":
        parser_class, site_name = RobotaUaParser, "Robota.ua"
    else:
        await update.message.reply_text("Invalid choice. Please enter 1 for Work.ua or 2 for Robota.ua.")
        return SITE_SELECTION

    context.user_data["site"] = site_name
    context.user_data["parser_class"] = parser_class
    await update.message.reply_text("How many resumes would you like to retrieve? (Enter a number):")
    return RESUME_COUNT

async def resume_count_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count_input = update.message.text.strip()
    if not count_input.isdigit() or int(count_input) <= 0:
        await update.message.reply_text("Please enter a valid positive number.")
        return RESUME_COUNT

    context.user_data["resume_count"] = int(count_input)
    parser_class = context.user_data["parser_class"]
    site_name = context.user_data["site"]

    # Parse salary and experience if they are provided
    salary = int(context.user_data["salary"]) if context.user_data["salary"] and context.user_data["salary"].isdigit() else None
    experience = int(context.user_data["years_of_experience"]) if context.user_data["years_of_experience"] and context.user_data["years_of_experience"].isdigit() else None

    parser = parser_class(
        job_position=context.user_data["job_position"],
        location=context.user_data["location"],
        salary=salary,
        experience=experience,
        english_language=context.user_data["english_language"],
        keywords=context.user_data["keywords"]
    )

    await update.message.reply_text(f"Fetching {context.user_data['resume_count']} resumes from {site_name}...")

    try:
        resumes = parser.fetch_resumes()

        if not resumes:
            await update.message.reply_text("No resumes found for the given criteria.")
            return ConversationHandler.END

        # Display only the requested number of resumes
        for idx, resume in enumerate(resumes[:context.user_data["resume_count"]], start=1):
            skills_str = ", ".join(resume.get('skills', [])) if resume.get('skills') else 'Not Specified'
            await update.message.reply_text(
                f"\nResume {idx}:\n"
                f"Position: {resume.get('position', 'N/A')}\n"
                f"Location: {resume.get('location', 'N/A')}\n"
                f"Salary: {resume.get('salary_expectation', 'N/A')}\n"
                f"Skills: {skills_str}\n"
                f"Link: {resume.get('link', 'N/A')}"
            )
    except Exception as e:
        await update.message.reply_text(f"An error occurred while fetching resumes: {e}")

    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[CommandHandler("search", search_command)],
    states={
        JOB_POSITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, job_position_step)],
        LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, location_step)],
        SALARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, salary_step)],
        EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, experience_step)],
        ENGLISH_LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, english_language_step)],
        KEYWORDS: [MessageHandler(filters.TEXT & ~filters.COMMAND, keywords_step)],
        SITE_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, site_selection_step)],
        RESUME_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, resume_count_step)],
    },
    fallbacks=[CommandHandler("start", start_command)]
)

application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(conv_handler)

if __name__ == "__main__":
    application.run_polling()
