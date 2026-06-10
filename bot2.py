from config2 import TOKEN
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

QUESTIONS = [
    {
        "text": "Вы узнали, что коллега распускает о вас слухи. Ваша реакция?",
        "options": [
            ("Поговорю с ним напрямую и выясню всё лично", "p"),
            ("Промолчу — не хочу конфликта", "i"),
        ],
    },
    {
        "text": " Вам предлагают рискованный, но интересный проект. Что выберете?",
        "options": [
            ("Соглашусь — это шанс проявить себя", "p"),
            ("Откажусь — стабильность важнее", "i"),
        ],
    },
    {
        "text": "На вечеринке вы обычно:",
        "options": [
            ("Знакомлюсь с новыми людьми и заряжаюсь энергией", "p"),
            (" Держусь рядом с друзьями и избегаю толпы", "i"),
        ],
    },
    {
        "text": " Друг просит помощи, но у вас важные дела. Как поступите?",
        "options": [
            ("Отложу свои дела — друг важнее", "p"),
            ("Объясню ситуацию и помогу позже", "i"),
        ],
    },
    {
        "text": "Вы приняли решение, но окружающие с вами не согласны. Вы:",
        "options": [
            ("Остаюсь при своём мнении, если уверен(а) в правоте", "p"),
            ("Прислушаюсь — вдруг они правы", "i"),
        ],
    },
    {
        "text": " Как вы справляетесь со стрессом?",
        "options": [
            ("Действую — занятость помогает отвлечься", "p"),
            ("Остаюсь наедине с собой и обдумываю всё", "i"),
        ],
    },
    {
        "text": "Вы получили критику на свою работу. Первая реакция?",
        "options": [
            ("Воспринимаю как урок и стараюсь улучшить результат", "p"),
            ("Расстраиваюсь, но со временем принимаю", "i"),
        ],
    },
     {
        "text": "Как вы обычно принимаете важные решения?",
        "options": [
            ("Доверяю интуиции и чувствам", "p"),
            ("Анализирую факты и взвешиваю все варианты", "i"),
        ],
    },
     {
        "text": "Вы видите незнакомца в беде. Ваши действия?",
        "options": [
            ("Сразу подхожу и предлагаю помощь", "p"),
            ("Оцениваю ситуацию — может, справится сам", "i"),
        ],
    },
     {
        "text": "Как вы относитесь к переменам в жизни?",
        "options": [
            ("Люблю перемены — это развитие и новые возможностит", "p"),
            (" Предпочитаю привычный уклад — он даёт уверенность", "i"),
        ],
    },
]

RESULTS = {
    "p": {
        "emoji": "🐓",
        "title": "ТЫ — ПЕТУХ",
        "desc": (
            "Ты громкий, самоуверенный и всегда первым кричишь «ку-ка-ре-ку».\n"
            "Любишь командовать, не терпишь конкуренции и встаёшь раньше всех.\n"
            "Во дворе ты — авторитет. Главное — не перепутай с кем споришь 😏"
        ),
    },
    "i": {
        "emoji": "🦃",
        "title": "ТЫ — ИНДЮК",
        "desc": (
            "Ты величественный, надутый и ходишь с видом, будто весь мир тебе должен.\n"
            "Обижаешься молча, но очень красиво. Окружающие должны сами догадаться о твоей грандиозности.\n"
            "Бал-бал-бал — это не просто звук, это философия жизни 🦃"
        ),
    },
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["q_index"] = 0
    await send_question(update, context, first=True)


async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE, first=False):
    idx = context.user_data["q_index"]
    q = QUESTIONS[idx]
    total = len(QUESTIONS)

    keyboard = [
        [InlineKeyboardButton(opt[0], callback_data="ans")]
        for opt in q["options"]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"Вопрос {idx + 1}/{total}\n\n{q['text']}"

    if first:
        await update.message.reply_text(
            "🐾 Добро пожаловать в тест «Кто ты из животных»\n\n"
        )
        await update.message.reply_text(text, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["q_index"] += 1

    if context.user_data["q_index"] >= len(QUESTIONS):
        await show_result(update, context)
    else:
        await send_question(update, context)


async def show_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = random.choice(["p", "i"])
    result = RESULTS[key]

    text = (
        f"{result['emoji']} <b>{result['title']}</b>\n\n"
        f"{result['desc']}"
    )

    keyboard = [[InlineKeyboardButton("🔄 Пройти снова", callback_data="restart")]]
    await update.callback_query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML"
    )


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    context.user_data["q_index"] = 0
    await send_question(update, context)


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_answer, pattern=r"^ans$"))
    app.add_handler(CallbackQueryHandler(restart, pattern=r"^restart$"))

    logger.info("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()