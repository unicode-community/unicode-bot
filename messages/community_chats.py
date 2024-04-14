from config.config import cfg

general_chat_names_without_links = "• " + "\n• ".join(cfg.general_chats.keys())
general_chat_names_with_links = "• " + "\n• ".join([f"[{name}]({link})" for name, link in cfg.general_chats.items()])

additional_chat_names_without_links = "• " + "\n• ".join(cfg.additional_chats.keys())
additional_chat_names_with_links = "• " + "\n• ".join([f"[{name}]({link})" for name, link in cfg.additional_chats.items()])

chats_for_subscriber = f"""
💬 *Основной чат:*

{general_chat_names_with_links}

🗯 *Дополнительные чаты по интересам:*

{additional_chat_names_with_links}

🗂 *Ты можешь добавить все чаты сразу,* [одной папкой]({cfg.folder_with_chats}).
"""

chats_for_unsubscriber = f"""
💬 *Основной чат:*

{general_chat_names_without_links}

🗯 *Дополнительные чаты по интересам:*

{additional_chat_names_without_links}

🔒 Для доступа к чатам тебе нужно *оформить подписку* на сообщество Unicode.
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

message_for_admins = "@{username}, `{full_name}` предложил идею для нового чата:\n```\n{info}```"