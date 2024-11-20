import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


# Функция для создания меню
def create_menu():
    keyboard = [
        ['Отправить заказ', 'Уведомление о доставке'],
        ['Запрос отзыва', 'Статус заказа'],
        ['Отправить чертёж']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# Функция для старта
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Добро пожаловать! Выберите действие:', reply_markup=create_menu())


# Функция для обработки текстовых сообщений (заказов)
async def handle_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_choice = update.message.text

    if user_choice == 'Отправить заказ':
        await update.message.reply_text('Пожалуйста, введите ваш заказ.')

    elif user_choice == 'Уведомление о доставке':
        await notify_delivery(update, context)

    elif user_choice == 'Запрос отзыва':
        await request_feedback(update, context)

    elif user_choice == 'Статус заказа':
        await notify_status(update, context)

    elif user_choice == 'Отправить чертёж':
        await send_drawing(update, context)

    else:
        await update.message.reply_text(f'Ваш заказ принят: {user_choice}')


# Функция для обработки документов и изображений
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    await file.download('user_order_file')
    await update.message.reply_text('Документ получен!')


# Функция для уведомления о статусе заказа
async def notify_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Статус вашего заказа обновлён!')


# Функция для отправки чертежей на согласование
async def send_drawing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open('drawing.png', 'rb') as drawing:
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=drawing)
    await update.message.reply_text('Чертёж отправлен на согласование.')


# Функция для уведомления о доставке
async def notify_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    delivery_status = "Ваш заказ был успешно доставлен!"
    await update.message.reply_text(delivery_status)


# Функция для запроса отзыва от клиента
async def request_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    feedback_request = "Пожалуйста, оставьте отзыв о нашем сервисе!"
    await update.message.reply_text(feedback_request)


# Основная функция

TOKEN = '8063385964:AAG_UUxYA6qgwiVV3gDt_5pEBnPc8mya7Mk'

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_order))
app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_document))

# Пример команды для уведомления о статусе заказа
app.add_handler(CommandHandler("status", notify_status))

# Пример команды для отправки чертежа на согласование
app.add_handler(CommandHandler("send_drawing", send_drawing))

# Команда для уведомления о доставке
app.add_handler(CommandHandler("notify_delivery", notify_delivery))

# Команда для запроса отзыва от клиента
app.add_handler(CommandHandler("request_feedback", request_feedback))

app.run_polling()

"""
git init
git add RGR.py
git commit -m "Initial commit"
"""