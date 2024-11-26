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
    # Список файлов изображений со статистикой
    statistics_files = [
        'statistics1.png',
        'statistics2.png',
        'statistics3.png',
        'statistics4.png',
        'statistics5.png'
    ]

    for file in statistics_files:
        try:
            with open(file, 'rb') as photo:
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)
            await asyncio.sleep(1)  # Задержка между отправками (по желанию)
        except FileNotFoundError:
            await update.message.reply_text(f"Файл {file} не найден.")
        except Exception as e:
            await update.message.reply_text(f"Произошла ошибка при отправке изображения {file}: {e}")


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



# URL для получения данных о заказах (замените на вашу ссылку)
#orders_data_url = 'https://docs.google.com/spreadsheets/d/1C-CR7dmSmctGUY-g-d4z1V3fOzKNx_LvBeuAoCWVkmM/export?format=csv'   Замените на действительную ссылку на ваш CSV

# URL для получения данных о запасах (замените на вашу ссылку)
#materials_data_url = 'https://docs.google.com/spreadsheets/d/1JyMQt09-4fmQjYGynGgJ_ivowgR4gXkdXrWzTzmJ5Nw/export?format=csv'   Замените на действительную ссылку на ваш CSV


import dash
from dash import dcc, html
import pandas as pd
import requests
from io import StringIO
import plotly.express as px

# Инициализация приложения Dash
app = dash.Dash(__name__)

# Функция для получения данных из внешнего источника
def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return pd.read_csv(StringIO(response.content.decode('utf-8')))
    else:
        raise Exception(f"Error fetching data: {response.status_code}")

# URL для получения данных (замените на ваши ссылки)
orders_data_url = 'https://docs.google.com/spreadsheets/d/1C-CR7dmSmctGUY-g-d4z1V3fOzKNx_LvBeuAoCWVkmM/export?format=csv'  # Замените на действительную ссылку на ваш CSV
materials_data_url = 'https://docs.google.com/spreadsheets/d/1JyMQt09-4fmQjYGynGgJ_ivowgR4gXkdXrWzTzmJ5Nw/export?format=csv'  # Замените на действительную ссылку на ваш CSV

# Получаем данные о заказах
orders_df = fetch_data(orders_data_url)

# Получаем данные о запасах материалов
materials_df = fetch_data(materials_data_url)

# Создание круговой диаграммы для статусов заказов
order_status_counts = orders_df['Статус заказа'].value_counts().reset_index()
order_status_counts.columns = ['Статус заказа', 'Количество']
order_status_fig = px.pie(order_status_counts, values='Количество', names='Статус заказа', title='Статусы заказов')

# Создание круговой диаграммы для запасов материалов
material_stock_counts = materials_df['Статус уведомления'].value_counts().reset_index()
material_stock_counts.columns = ['Статус уведомления', 'Количество']
material_stock_fig = px.pie(material_stock_counts, values='Количество', names='Статус уведомления', title='Статусы уведомлений по запасам')

# Создание гистограммы для количества заказов по клиентам
customer_order_counts = orders_df['Имя клиента'].value_counts().reset_index()
customer_order_counts.columns = ['Имя клиента', 'Количество заказов']
customer_order_fig = px.bar(customer_order_counts, x='Имя клиента', y='Количество заказов', title='Количество заказов по клиентам')

# Создание линейного графика для изменения запасов материалов во времени (пример)
time_series_fig = px.line(materials_df, x='Дата последнего заказа', y='Текущий запас', title='Изменение текущих запасов во времени')

# Создание гистограммы для распределения количества товаров в заказах
quantity_distribution_fig = px.histogram(orders_df, x='Количество', title='Распределение количества товаров в заказах')

# Определение макета приложения с вкладками
app.layout = html.Div(children=[
    html.H1(children='Статистика'),

    dcc.Tabs([
        dcc.Tab(label='Статусы заказов', children=[
            dcc.Graph(
                id='order-status-pie-chart',
                figure=order_status_fig
            )
        ]),
        dcc.Tab(label='Запасы материалов', children=[
            dcc.Graph(
                id='material-stock-pie-chart',
                figure=material_stock_fig
            )
        ]),
        dcc.Tab(label='Количество заказов по клиентам', children=[
            dcc.Graph(
                id='customer-order-bar-chart',
                figure=customer_order_fig
            )
        ]),
        dcc.Tab(label='Изменение запасов во времени', children=[
            dcc.Graph(
                id='time-series-line-chart',
                figure=time_series_fig
            )
        ]),
        dcc.Tab(label='Распределение количества товаров в заказах', children=[
            dcc.Graph(
                id='quantity-distribution-histogram',
                figure=quantity_distribution_fig
            )
        ])
    ])
])

# Запуск сервера
if __name__ == '__main__':
#    app.run_server(debug=True)

    asyncio.run(main())
