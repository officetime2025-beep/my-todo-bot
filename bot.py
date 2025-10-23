from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os

# Токен из переменной среды
TOKEN = os.environ["8402424321:AAH-LHIMD1X_0ehxO5joFNLp8fePNYND76g"]

# Хранилище задач (в памяти)
tasks = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я простой список дел.\n"
        "Команды:\n"
        "/add <текст> — добавить задачу\n"
        "/list — показать задачи\n"
        "/done <номер> — отметить как выполненную\n"
        "/clear — удалить всё"
    )

async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Используй: /add Купить хлеб")
        return
    task = " ".join(context.args)
    tasks.append({"text": task, "done": False})
    await update.message.reply_text(f"✅ Добавлено: {task}")

async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tasks:
        await update.message.reply_text("Список пуст ✨")
        return
    message = "📝 Задачи:\n\n"
    for i, t in enumerate(tasks, 1):
        mark = "✅" if t["done"] else "⬜"
        message += f"{i}. {mark} {t['text']}\n"
    await update.message.reply_text(message)

async def done_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Используй: /done 1")
        return
    index = int(context.args[0]) - 1
    if 0 <= index < len(tasks):
        tasks[index]["done"] = True
        await update.message.reply_text(f"✅ Задача №{index + 1} выполнена!")
    else:
        await update.message.reply_text("Нет задачи с таким номером.")

async def clear_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks.clear()
    await update.message.reply_text("🗑️ Список очищен!")

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_task))
    app.add_handler(CommandHandler("list", list_tasks))
    app.add_handler(CommandHandler("done", done_task))
    app.add_handler(CommandHandler("clear", clear_tasks))
    print("✅ Бот запущен!")
    app.run_polling()

