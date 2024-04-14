from datetime import datetime

from pytz import timezone

from db.database import Database


async def get_subscription_status(user_tg_id: int, db: Database) -> dict:
    user_info = await db.get_user(user_id=user_tg_id)

    if user_info is None:
        is_subscriber = None
        is_subscribed_to_payments = None
        subscription_start = None
        subscription_end = None
    else:
        is_subscriber = (
            (user_info.is_subscriber) and
            (user_info.subscription_start <= datetime.now(tz=timezone("Europe/Moscow")) <= user_info.subscription_end)
        )

        is_subscribed_to_payments  = is_subscriber and user_info.is_subscribed_to_payments
        subscription_start = user_info.subscription_start if (is_subscriber and user_info.subscription_start) else None
        subscription_end = user_info.subscription_end if (is_subscriber and user_info.subscription_end) else None

    return {
        "is_subscriber": is_subscriber,
        "is_subscribed_to_payments": is_subscribed_to_payments,
        "subscription_start": subscription_start,
        "subscription_end": subscription_end,
    }
