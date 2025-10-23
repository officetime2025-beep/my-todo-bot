from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters, JobQueue
import json
import os
import logging

# Настройка логов (полезно для отладки в Railway)
logging.basicConfig(level=logging.INFO)

# Токен из переменной среды (обязательно задай в Railway!)
TOKEN = os.environ["TOKEN"]

# Категории
CATEGORIES = [
    "личное", "покупки", "офистайм",
    "дом/мыла", "здоровье", "Глеб", "Никита"
]

# Хранилище данных
user_data = {}
DATA_FILE = "tasks.json"

def load_data():
    global user_data
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
                user_data = {int(k): v for k, v in raw.items()}
        except Exception as e:
            print(f"Ошибка загрузки: {e}")

def save_data():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка сохранения: {e}")

def get_main_keyboard():
    buttons = [[KeyboardButton(cat)] for cat in CATEGORIES]
    buttons.append([KeyboardButton("📋 Показать всё")])  # «Очистить всё» удалено
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)

async def send_daily_reminder(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    user_id = job.chat_id

    if user_id not in user_data:
        return

    # Считаем невыполненные задачи
    total_pending = 0
    for cat in CATEGORIES:
        tasks = user_data[user_id][cat]
        pending = [t for t in tasks if not t["done"]]
        total_pending += len(pending)

    if total_pending > 0:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"🕒 Доброе утро! У тебя {total_pending} невыполненных задач. Не забудь про них! 😊"
        )
    else:
        await context.bot.send_message(
            chat_id=user_id,
            text="✨ Все задачи выполнены! Отличная работа! 🎉"
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_
        user_data[user_id] = {cat: [] for cat in CATEGORIES}

    # Настройка ежедневного напоминания
    job_queue = context.job_queue
    # Удаляем старые задания
    current_jobs = job_queue.get_jobs_by_name(str(user_id))
    for job in current_jobs:
        job.schedule_removal()
    # Запускаем напоминание:
    # - первый раз через 10 секунд (для теста!)
    # - потом каждые 24 часа
    job_queue.run_repeating(
        send_daily_reminder,
        interval=24 * 60 * 60,  # 24 часа
        first=10,               # первый запуск через 10 секунд
        chat_id=update.effective_chat.id,
        name=str(user_id)
    )

    await update.message.reply_text(
        "Привет! 👋 Я твой персональный список дел.\n\n"
        "Выбери категорию ниже или напиши задачу — я добавлю её в 'прочее'.",
        reply_markup=get_main_keyboard()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id not in user_
        user_data[user_id] = {cat: [] for cat in CATEGORIES}

    # Выбор категории
    if text in CATEGORIES:
        context.user_data["selected_category"] = text
        tasks = user_data[user_id][text]
        if not tasks:
            await update.message.reply_text(
                f"В категории *{text}* пока пусто.\nНапиши задачу — я добавлю её!",
                parse_mode="Markdown"
            )
            return

        # Отправляем каждую задачу отдельным сообщением с кнопками
        for i, task in enumerate(tasks):
            mark = "✅" if task["done"] else "⬜"
            msg_text = f"{mark} *{task['text']}*"
            toggle_data = f"toggle_{text}_{i}"
            delete_data = f"delete_{text}_{i}"
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Выполнено", callback_data=toggle_data),
                    InlineKeyboardButton("❌ Удалить", callback_data=delete_data)
                ]
            ])
            await update.message.reply_text(msg_text, parse_mode="Markdown", reply_markup=keyboard)
        return

    # Показать всё
    if text == "📋 Показать всё":
        full_msg = "📝 *Все задачи:*\n\n"
        has_tasks = False
        for cat in CATEGORIES:
            tasks = user_data[user_id][cat]
            if tasks:
                has_tasks = True
                full_msg += f"🔹 *{cat.capitalize()}*:\n"
                for task in tasks:
                    mark = "✅" if task["done"] else "⬜"
                    full_msg += f"  • {mark} {task['text']}\n"
                full_msg += "\n"
        if not has_tasks:
            full_msg = "✨ Все списки пусты!"
        await update.message.reply_text(full_msg, parse_mode="Markdown")
        return

    # Добавление новой задачи
    selected_cat = context.user_data.get("selected_category", "прочее")
    user_data[user_id][selected_cat].append({"text": text, "done": False})
    save_data()
    await update.message.reply_text(
        f"✅ Добавлено в *{selected_cat}*:\n«{text}»",
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    data = query.data

    # Обработка переключения статуса
    if data.startswith("toggle_"):
        parts = data.split("_", 2)
        if len(parts) != 3:
            return
        _, category, index_str = parts
        try:
            index = int(index_str)
        except ValueError:
            return

        if user_id not in user_data or category not in user_data[user_id]:
            await query.edit_message_text("❌ Данные устарели. Открой категорию заново.")
            return

        tasks = user_data[user_id][category]
        if 0 <= index < len(tasks):
            tasks[index]["done"] = not tasks[index]["done"]
            save_data()
            mark = "✅" if tasks[index]["done"] else "⬜"
            await query.edit_message_text(
                text=f"{mark} *{tasks[index]['text']}*",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("✅ Выполнено", callback_data=f"toggle_{category}_{index}"),
                        InlineKeyboardButton("❌ Удалить", callback_data=f"delete_{category}_{index}")
                    ]
                ])
            )
        return

    # Обработка удаления
    if data.startswith("delete_"):
        parts = data.split("_", 2)
        if len(parts) != 3:
            return
        _, category, index_str = parts
        try:
            index = int(index_str)
        except ValueError:
            return

        if user_id not in user_data or category not in user_data[user_id]:
            await query.edit_message_text("❌ Данные устарели.")
            return

        tasks = user_data[user_id][category]
        if 0 <= index < len(tasks):
            deleted_task = tasks.pop(index)
            save_data()
            await query.edit_message_text(f"❌ Удалено: *{deleted_task['text']}*", parse_mode="Markdown")
        return

# Запуск приложения
if __name__ == "__main__":
    load_data()
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Бот запущен!")
    app.run_polling()


