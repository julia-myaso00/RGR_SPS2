import logging
import nest_asyncio
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Применяем nest_asyncio для работы в уже запущенном цикле событий
nest_asyncio.apply()

# Глобальные переменные для хранения состояния заказа и статусов
user_orders = {}
order_statuses = {}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        ["Сделать заказ"],
        ["Проверить статус заказа"],
        ["Статистика"]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text('Выберите действие:', reply_markup=reply_markup)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    user_id = update.message.from_user.id

    if user_message == "Сделать заказ":
        await update.message.reply_text("Введите название товара:")
        user_orders[user_id] = {"step": "waiting_for_product_name"}
    elif user_message == "Проверить статус заказа":
        if user_id in order_statuses:
            status = order_statuses[user_id]
            await update.message.reply_text(f"Статус вашего заказа: {status}")
        else:
            await update.message.reply_text("У вас нет активных заказов.")
    elif user_message == "Статистика":
        await send_statistics(update, context)
    else:
        if user_id in user_orders:
            if user_orders[user_id]["step"] == "waiting_for_product_name":
                user_orders[user_id]["product_name"] = user_message
                user_orders[user_id]["step"] = "waiting_for_quantity"
                await update.message.reply_text("Введите количество:")
            elif user_orders[user_id]["step"] == "waiting_for_quantity":
                quantity = user_message
                product_name = user_orders[user_id]["product_name"]

                # Сохраняем статус заказа
                order_statuses[user_id] = f"Заказ на {quantity} единиц(ы) '{product_name}' оформлен."

                await update.message.reply_text(f"Ваш заказ на {quantity} единиц(ы) '{product_name}' оформлен.")

                # Запускаем асинхронную задачу для изменения статуса через минуту
                asyncio.create_task(change_order_status(user_id, context))

                del user_orders[user_id]  # Удаляем пользователя из состояния после завершения заказа
        else:
            await update.message.reply_text("Пожалуйста, выберите действие из меню.")


async def send_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Отправляем изображение со статистикой
    try:
        with open('statistics.png', 'rb') as photo:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)
    except FileNotFoundError:
        await update.message.reply_text("Изображение со статистикой не найдено.")


async def change_order_status(user_id, context):
    # Ждем 60 секунд (1 минута)
    await asyncio.sleep(60)

    # Изменяем статус заказа на "Выполнено"
    order_statuses[user_id] = "Выполнено"

    # Отправляем уведомление пользователю о завершении заказа
    await context.bot.send_message(chat_id=user_id, text="Ваш заказ выполнен!")


async def main() -> None:
    # Замените 'YOUR_TOKEN' на токен вашего бота
    token = "8063385964:AAG_UUxYA6qgwiVV3gDt_5pEBnPc8mya7Mk"  # Убедитесь, что это правильный токен

    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await application.run_polling()


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
