from .subscriptions import unicode_base, unicode_guest, unicode_starter


def create_subscription_params(subscription_db_name, price, subscription_name):
    return {
        "amount": {
            "value": price,
            "currency": "RUB"
        },
        "capture": True,
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/unicode_dev_bot" # TODO заменить на конфиг
        },
        "metadata": {
            "subscription_db_name": subscription_db_name
        },
        "description": f"Оплата подписки {subscription_name}",
        "save_payment_method": True
    }


unicode_guest_params = create_subscription_params(
    subscription_db_name=unicode_guest.db_name,
    price=f"{unicode_guest.price}.00",
    subscription_name=unicode_guest.name
)


unicode_starter_params = create_subscription_params(
    subscription_db_name=unicode_starter.db_name,
    price=f"{unicode_starter.price}.00",
    subscription_name=unicode_starter.name
)


unicode_base_params = create_subscription_params(
    subscription_db_name=unicode_base.db_name,
    price=f"{unicode_base.price}.00",
    subscription_name=unicode_base.name
)
