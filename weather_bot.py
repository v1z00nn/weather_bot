import os
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Конфигурация (используем ваши ключи)
BOT_TOKEN = "8068887041:AAEGUKxng2fVJ8dQaxBXya8MYrdZy8URgXI"
OWM_API_KEY = "147c757022d894df7709443c3c7851c1"

async def start(update: Update, context):
    """Обработчик команды /start"""
    buttons = [
        ["🌤️ Красногорск"],
        ["🌆 Москва", "🏖️ Сочи"],
        ["❓ Помощь"]
    ]
    markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(
        "🏙️ Выберите город или напишите название:",
        reply_markup=markup
    )

async def handle_message(update: Update, context):
    """Обработчик текстовых сообщений"""
    text = update.message.text.lower()
    
    # Определяем город по кнопке или тексту
    if "красногорск" in text:
        city = "Krasnogorsk,RU"
    elif "москва" in text:
        city = "Moscow,RU"
    elif "сочи" in text:
        city = "Sochi,RU"
    elif "помощь" in text or "help" in text:
        await update.message.reply_text("ℹ️ Просто выберите город или напишите его название!")
        return
    else:
        # Пытаемся определить город из текста
        city = f"{text.capitalize()},RU"
    
    # Получаем и отправляем погоду
    weather_data = get_weather(city)
    await update.message.reply_text(weather_data)

def get_weather(city):
    """Получение погоды через OpenWeatherMap API"""
    try:
        # Формируем URL запроса
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OWM_API_KEY}&units=metric&lang=ru"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Обработка ошибок API
        if data.get("cod") != 200:
            error_msg = data.get("message", "Неизвестная ошибка")
            return f"🚨 Ошибка: {error_msg}\nКод ошибки: {data.get('cod')}"
        
        # Парсинг данных
        city_name = data.get("name", city.split(',')[0])
        temp = data["main"]["temp"]
        feels = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        desc = data["weather"][0]["description"].capitalize()
        icon_code = data["weather"][0]["icon"]
        
        # Подбираем emoji по иконке
        icon_emoji = {
            "01": "☀️", "02": "⛅", "03": "☁️", "04": "☁️",
            "09": "🌧️", "10": "🌦️", "11": "⛈️", "13": "❄️", "50": "🌫️"
        }.get(icon_code[:2], "🌡️")
        
        # Форматируем ответ
        return (
            f"{icon_emoji} <b>{city_name}</b>\n"
            f"• Температура: <b>{temp}°C</b> (ощущается как {feels}°C)\n"
            f"• Погода: {desc}\n"
            f"• Влажность: {humidity}%\n"
            f"• Ветер: {wind} м/с\n"
            f"\n<code>Данные: OpenWeatherMap</code>"
        )
    
    except Exception as e:
        return f"⚠️ Ошибка: {str(e)}\nПопробуйте позже или выберите другой город"

if __name__ == "__main__":
    print("Запуск бота погоды...")
    
    # Создаем приложение
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    print("Бот успешно запущен! Для остановки нажмите Ctrl+C")
    app.run_polling()
