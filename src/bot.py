from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)

secretCode = "Your_Code"

# Сценарии с вопросами
scenarios = {
    "Фишинг": {
        "questions": [
            {
                "question": "Что такое фишинг?",
                "options": ["Атака с целью кражи данных", "Обновление ПО", "Тестирование сайта"],
                "answer": "Атака с целью кражи данных"
            },
            {
                "question": "Как распознать фишинг?",
                "options": ["Подозрительная ссылка", "Официальный логотип", "HTTPS-сертификат"],
                "answer": "Подозрительная ссылка"
            },
            {
                "question": "Что делать при получении фишингового письма?",
                "options": ["Переслать друзьям", "Удалить и сообщить", "Открыть вложение"],
                "answer": "Удалить и сообщить"
            }
        ]
    },
    "Социальная инженерия": {
        "questions": [
            {
                "question": "Что такое социальная инженерия?",
                "options": ["Хакерская программа", "Манипуляция людьми для получения данных", "Сетевая атака"],
                "answer": "Манипуляция людьми для получения данных"
            },
            {
                "question": "Как избежать атак социальной инженерии?",
                "options": ["Всегда делиться паролем", "Не открывать незнакомые ссылки", "Игнорировать антивирус"],
                "answer": "Не открывать незнакомые ссылки"
            },
            {
                "question": "Кто может быть целью социальной инженерии?",
                "options": ["Любой пользователь", "Только ИТ-специалисты", "Только военные"],
                "answer": "Любой пользователь"
            }
        ]
    },
    "Слабые пароли": {
        "questions": [
            {
                "question": "Что считается слабым паролем?",
                "options": ["123456", "qwerty", "Оба варианта"],
                "answer": "Оба варианта"
            },
            {
                "question": "Какой пароль безопасен?",
                "options": ["Имя пользователя", "Короткий PIN", "Сложный и уникальный"],
                "answer": "Сложный и уникальный"
            },
            {
                "question": "Нужно ли использовать один пароль везде?",
                "options": ["Да, это удобно", "Нет, это рискованно", "Можно, если пароль длинный"],
                "answer": "Нет, это рискованно"
            }
        ]
    },
    "Защита сети": {
        "questions": [
            {
                "question": "Что помогает защитить Wi-Fi-сеть?",
                "options": ["Открытая сеть", "Сложный пароль", "Отключённый пароль"],
                "answer": "Сложный пароль"
            },
            {
                "question": "Для чего используется VPN?",
                "options": ["Для ускорения интернета", "Для обеспечения конфиденциальности", "Для обновлений"],
                "answer": "Для обеспечения конфиденциальности"
            },
            {
                "question": "Что такое межсетевой экран (Firewall)?",
                "options": ["Программа для музыки", "Защита от несанкционированного доступа", "Игровое приложение"],
                "answer": "Защита от несанкционированного доступа"
            }
        ]
    },
    "Мобильная безопасность": {
        "questions": [
            {
                "question": "Какой риск связан с публичным Wi-Fi?",
                "options": ["Высокая скорость", "Потеря зарядки", "Перехват данных"],
                "answer": "Перехват данных"
            },
            {
                "question": "Нужно ли устанавливать антивирус на смартфон?",
                "options": ["Нет", "Только на Android", "Да, особенно при загрузке приложений из сторонних источников"],
                "answer": "Да, особенно при загрузке приложений из сторонних источников"
            },
            {
                "question": "Что делать при потере смартфона?",
                "options": ["Ничего", "Удалённо заблокировать", "Ждать возврата"],
                "answer": "Удалённо заблокировать"
            }
        ]
    }
}

# Состояния
CHOOSING, TESTING = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [list(scenarios.keys())]
    await update.message.reply_text(
        "Выберите тему для теста:",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return CHOOSING


async def choose_scenario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    selected = update.message.text
    if selected not in scenarios:
        await update.message.reply_text("Пожалуйста, выберите корректную тему.")
        return CHOOSING

    context.user_data["scenario"] = selected
    context.user_data["score"] = 0
    context.user_data["current_q"] = 0

    return await ask_question(update, context)


async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    scenario = scenarios[context.user_data["scenario"]]
    index = context.user_data["current_q"]

    if index < len(scenario["questions"]):
        q = scenario["questions"][index]
        reply_keyboard = [q["options"]]
        await update.message.reply_text(
            q["question"],
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, resize_keyboard=True
            ),
        )
        return TESTING
    else:
        score = context.user_data["score"]
        total = len(scenario["questions"])
        await update.message.reply_text(f"Тест завершён. Ваш результат: {score} из {total}\nЧтобы начать заново, "
                                        f"напишите /start.")
        return ConversationHandler.END


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = update.message.text
    scenario = scenarios[context.user_data["scenario"]]
    index = context.user_data["current_q"]
    correct = scenario["questions"][index]["answer"]

    if answer == correct:
        context.user_data["score"] += 1

    context.user_data["current_q"] += 1
    return await ask_question(update, context)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Тест прерван.")
    return ConversationHandler.END


def main() -> None:
    # Замените "YOUR_TOKEN" на токен вашего бота
    application = ApplicationBuilder().token(secretCode).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, choose_scenario)
            ],
            TESTING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    print("Бот запущен...")
    application.run_polling()


if __name__ == "__main__":
    main()
