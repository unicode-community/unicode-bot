unicode_guest_params = {
    "amount": {
        "value": "99.00",
        "currency": "RUB"
    },
    "capture": True,
    "confirmation": {
        "type": "redirect",
        "return_url": "https://t.me/unicode_dev_bot"
    },
    "metadata": {
        "subscription_type": "unicode_guest"
    },
    "description": "Оплаты подписки 👤 Unicode Guest (99 ₽/мес)",
    "save_payment_method": True
}

unicode_base_params = {
    "amount": {
        "value": "499.00",
        "currency": "RUB"
    },
    "capture": True,
    "confirmation": {
        "type": "redirect",
        "return_url": "https://t.me/unicode_dev_bot"
    },
    "metadata": {
        "subscription_type": "unicode_base"
    },
    "description": "Оплаты подписки 🟣 Unicode Base (499 ₽/мес)",
    "save_payment_method": True
}
