# python-resume-parser-bot

### 1. Створення та активація віртуального середовища

# python -m venv myenv

Активуємо його:

    На Windows:

        myenv\Scripts\activate

    На macOS та Linux:

        source myenv/bin/activate

# 2. Встановлення залежностей

Далі створимо файл requirements.txt (якщо його ще немає) і додамо всі необхідні бібліотеки:

requests
beautifulsoup4
selenium
python-dotenv
python-telegram-bot

pip install -r requirements.txt

# 3. Налаштування python-dotenv

- Створіть файл .env у папці проекту.

TOKEN=your_telegram_token

from dotenv import load_dotenv
import os

load_dotenv() # Завантажує .env файл

TOKEN = os.getenv("TOKEN")

# 3.5 Створення бота в Bot-father

- Відкрийте Telegram та знайдіть бота BotFather.
- Відправте команду /start, а потім /newbot.
- Введіть ім'я для вашого бота (наприклад, "Мій бот").
- Введіть унікальне ім'я користувача для бота, яке закінчується на bot (наприклад, my_first_bot).
- Отримайте токен API, який виглядає приблизно так: 123456789:ABCdefGHIjklMNOpqrstuvWXyz
 
# 4. Запуск бота

python3 main.py

# Щоб протестувати скріпти

    перейти в папку скріптів, розкоментувати тести і запустити команду:
        python3 robota_ua_parser.py
        python3 work_ua_parser.py
