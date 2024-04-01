from datetime import datetime

from db.database import Database


async def get_subscription_status(user_tg_id: int, db: Database) -> dict:
    user_info = await db.get_user(user_id=user_tg_id)

    is_subscriber = (user_info.is_subscriber) and (user_info.subscription_start <= datetime.now() <= user_info.subscription_end)

    return {
        "is_subscriber": is_subscriber,
        "is_subscribed_to_payments": user_info.is_subscribed_to_payments if (is_subscriber and user_info.is_subscribed_to_payments) else None,
        "subscription_start": user_info.subscription_start if (is_subscriber and user_info.subscription_start) else None,
        "subscription_end": user_info.subscription_end if (is_subscriber and user_info.subscription_end) else None,
    }
