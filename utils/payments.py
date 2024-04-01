def create_subscription_params(price: int):
    return {
        "amount": {
            "value": f"{price}.00",
            "currency": "RUB"
        },
        "capture": True,
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/unicode_dev_bot" # TODO заменить на конфиг
        },
        "description": "Оплата подписки",
        "save_payment_method": True
    }
