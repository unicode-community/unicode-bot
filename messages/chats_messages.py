# В этот словарь можно добавлять новые чаты
# TODO сделать этот словарь в виде конфига и тут его прочитывать

general_chats = {
    "UNI: ОСНОВНОЙ": "https://t.me/+Pphu6iu6VGwwYmRi",
}

additional_chats = {
    "UNI: резюме": "https://t.me/+vLW1bN_CDE5iZWM6",
    "UNI: python": "https://t.me/+3iec-KVDof4wZGIy",
    "UNI: data science": "https://t.me/+-yVI9LU9klk2ZjJi",
    "UNI: база знаний": "https://t.me/+UWs3Kbqu6uUzNWZi"
}


general_chat_names_without_links = "• " + "\n• ".join(general_chats.keys())
general_chat_names_with_links = "• " + "\n• ".join([f"[{name}]({link})" for name, link in general_chats.items()])

additional_chat_names_without_links = "• " + "\n• ".join(additional_chats.keys())
additional_chat_names_with_links = "• " + "\n• ".join([f"[{name}]({link})" for name, link in additional_chats.items()])

chats_for_subscriber = f"""
💬 *Основной чат:*

{general_chat_names_with_links}

🗯 *Дополнительные чаты по интересам:*

{additional_chat_names_with_links}

🗂 *Ты можешь добавить все чаты сразу,* [одной папкой](https://t.me/addlist/l69T0iycJCMwMTZi).
"""

chats_for_unsubscriber = f"""
💬 *Основной чат:*

{general_chat_names_without_links}

🗯 *Дополнительные чаты по интересам:*

{additional_chat_names_without_links}

🔒 Для доступа к чатам тебе нужно оформить соответствующую подписку на сообщество Unicode.
"""


rules_to_create_new_chat = """
🌈 Ты можешь предложить создать *новый* дополнительный чат по интересам. При этом, ты должен стать его *модератором* и *согласиться*:

1️⃣ *Следить* за соблюдением правил хорошего общения.

2️⃣ *Отвечать* на вопросы участников чата.

3️⃣ *При желании, организовывать* различные активности в этом чате.

🔥 Хочешь принять правила и продолжить?
"""

ask_new_chat_name = """🤔 Какую тему для чата ты хочешь предложить?"""

feedback_after_create_new_chat = """👍 Отлично! Модератор рассмотрит твоё предложение и скоро с тобой свяжется."""
