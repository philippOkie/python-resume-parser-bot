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

# Щоб протестувати скріпти

    перейти в папку скріптів, розкоментувати тести і запустити команду:
        python3 robota_ua_parser.py
        python3 work_ua_parser.py
