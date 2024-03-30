from utils.subscriptions import unicode_base, unicode_guest, unicode_starter

welcome_subscribe = """🌈 Пожалуйста, выбери тип подписки, который тебя интересует:"""

for subscription in [unicode_guest, unicode_base]: # TODO добавить unicode_starter
    welcome_subscribe += f"""\n\n*{subscription.name}* ({subscription.price} ₽/мес)\n""" + "• " + "\n• ".join(subscription.features)

choice_type_subscr = """👉 *Выбери интересующий тебя вариант подписки*"""

choice_update_or_break_subscr = """🔄 *Хочешь изменить или отменить подписку?*"""

last_active_time_subscr = """📆 Подписка действительна до: {date}"""

current_subscr = """✅ Твоя подписка: *{subscr} ({price} ₽/мес)*"""

unicode_guest_info = f"""С подпиской *{unicode_guest.name}* ты получаешь:\n\n""" + "\n\n".join(unicode_guest.features_emoji)

unicode_starter_info = f"""С подпиской *{unicode_starter.name}* ты получаешь:\n\n""" + "\n\n".join(unicode_starter.features_emoji)

unicode_base_info = f"""С подпиской *{unicode_base.name}* ты получаешь:\n\n""" + "\n\n".join(unicode_base.features_emoji)

break_subscr = """❓ *Ты точно хочешь отменить свою подписку?*\n\nТекущая подписка будет действовать до *{date}*."""

succesful_break_subscr = """✅ Твоя подписка успешно отменена."""

successful_pay_subscr = """✅ Подписка успешно активирована!"""

error_pay_subscr = """⚠️ *При оформлении подписки возникла ошибка.* Пожалуйста, попробуй снова, либо обратись в поддержку."""

already_activated_subscr = """✅ Данный вид подписки уже активирован."""
