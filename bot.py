from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import json
import os

# Настройки
TOKEN = "8402424321:AAH-LHIMD1X_0ehxO5joFNLp8fePNYND76g"

# Категории
CATEGORIES = [
    "личное", "покупки", "офистайм",
    "дом/мыла", "здоровье", "ребёнок", "прочее"
]

# Хранилище: { user_id: { category: [ { "text": "...", "done": False }, ... ] } }
user_data = {}

# Сохранение и загрузка (опционально, для перезапуска)
DATA_FILE = "tasks.json"

def load_data():
    global user_data
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
                # Преобразуем ключи user_id из str обратно в int
                user_data = {int(k): v for k, v in raw.items()}
        except Exception as e:
            print(f"Ошибка загрузки: {e}")

def save_data():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка сохранения: {e}")

# Главное меню с кнопками
def get_main_keyboard():
    buttons = [[KeyboardButton(cat)] for cat in CATEGORIES]
    buttons.append([KeyboardButton("📋 Показать всё"), KeyboardButton("🗑️ Очистить всё")])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data:
        user_data[user_id] = {cat: [] for cat in CATEGORIES}
    await update.message.reply_text(
        "Привет! 👋 Я твой персональный список дел.\n\n"
        "Выбери категорию ниже или напиши задачу — я добавлю её в 'прочее'.",
        reply_markup=get_main_keyboard()
    )

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # Инициализация для нового пользователя
    if user_id not in user_data:
        user_data[user_id] = {cat: [] for cat in CATEGORIES}

    # Если сообщение — это название категории
    if text in CATEGORIES:
        context.user_data["selected_category"] = text
        tasks = user_data[user_id][text]
        if tasks:
            msg = f"📌 *{text.capitalize()}*:\n\n"
            for i, task in enumerate(tasks, 1):
                mark = "✅" if task["done"] else "⬜"
                msg += f"{i}. {mark} {task['text']}\n"
            msg += f"\nНапиши новую задачу или номер для отметки (например: 1)"
        else:
            msg = f"В категории *{text}* пока пусто.\nНапиши задачу — я добавлю её!"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    # Команда "Показать всё"
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

    # Команда "Очистить всё"
    if text == "🗑️ Очистить всё":
        user_data[user_id] = {cat: [] for cat in CATEGORIES}
        save_data()
        await update.message.reply_text("Все задачи удалены! 🧹")
        return

    # Пользователь прислал задачу или номер
    selected_cat = context.user_data.get("selected_category", "прочее")

    # Проверяем, не является ли текст номером задачи
    if text.isdigit():
        task_num = int(text) - 1
        tasks = user_data[user_id][selected_cat]
        if 0 <= task_num < len(tasks):
            tasks[task_num]["done"] = not tasks[task_num]["done"]
            status = "выполнена" if tasks[task_num]["done"] else "возвращена в работу"
            await update.message.reply_text(f"Задача №{task_num + 1} {status} ✅")
            save_data()
        else:
            await update.message.reply_text("Нет задачи с таким номером.")
        return

    # Иначе — добавляем новую задачу
    user_data[user_id][selected_cat].append({"text": text, "done": False})
    save_data()
    await update.message.reply_text(f"✅ Добавлено в *{selected_cat}*:\n«{text}»", parse_mode="Markdown")

# Основной запуск
if __name__ == "__main__":
    load_data()
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен!")
    app.run_polling()