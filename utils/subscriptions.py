from datetime import datetime

from db.database import Database


class Subscription:
    @classmethod
    def add_feature(cls, feature):
        cls.features.append(feature)

    @classmethod
    def check_feature_access(cls, feature) -> bool:
        return feature in cls.features


class UnicodeGuest(Subscription):
    name = "👤 Unicode Guest"
    db_name = "unicode_guest"
    price = 99
    features = ["Доступ в основные чаты сообщества"]
    features_emoji = ["🗣 Доступ в основные чаты сообщества"]


class UnicodeStandard(UnicodeGuest):
    name = "🟠 Unicode Starter"
    db_name = "unicode_starter"
    price = 399
    features = UnicodeGuest.features# + ["Доступ к боту для IT знакомств"] # TODO включить когда будет нужно
    features_emoji = UnicodeGuest.features_emoji# + ["🤝 Доступ к боту для IT знакомств"] # TODO включить когда будет нужно


class UnicodeBase(UnicodeStandard):
    name = "🟣 Unicode Base"
    db_name = "unicode_base"
    price = 499
    features = UnicodeStandard.features + ["Доступ в приватный телеграм канал", "Доступ к базе знаний", "Доступ к размещению в таблице менторов"]
    features_emoji = UnicodeStandard.features_emoji + ["🟣 Доступ в приватный телеграм канал", "📚 Доступ к базе знаний", "🏅 Доступ к размещению в таблице менторов"]


async def get_subscription_status(user_tg_id: int, db: Database) -> dict:
    user_info = await db.get_user(user_id=user_tg_id)

    is_subscriber = (user_info.subscription_db_name is not None) and (user_info.subscription_start <= datetime.now() <= user_info.subscription_end)
    subscription_db_name = user_info.subscription_db_name if is_subscriber else None

    subscription_classes = {
        "unicode_guest": UnicodeGuest,
        "unicode_starter": UnicodeStandard,
        "unicode_base": UnicodeBase
    }

    subscription_class = subscription_classes.get(subscription_db_name, None)

    return {
        "is_subscriber": is_subscriber,
        "is_subscribed_to_payments": is_subscriber and user_info.is_subscribed_to_payments,
        "subscription_end": is_subscriber and user_info.subscription_end,
        "subscription_db_name": subscription_db_name,
        "subscription_features": subscription_class.features if subscription_class else None,
        "subscription_features_emoji": subscription_class.features_emoji if subscription_class else None
    }


unicode_guest = UnicodeGuest()
unicode_starter = UnicodeStandard()
unicode_base = UnicodeBase()

match_subscription = {
    "unicode_guest": unicode_guest,
    "unicode_starter": unicode_starter,
    "unicode_base": unicode_base
}
