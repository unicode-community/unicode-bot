from datetime import datetime

from fastapi import Depends, FastAPI

from db.database import Database, get_db
from utils.subscriptions import UnicodeBase, UnicodeGuest, UnicodeStandard

app = FastAPI()

@app.get("/subscribers/{tg_id}")
async def check_subscription_status(tg_id: int, db: Database = Depends(get_db)):
    user_info = await db.get_user(user_id=tg_id)

    is_subscriber = (user_info.subscription_db_name is not None) and (user_info.subscription_start <= datetime.now() <= user_info.subscription_end)
    subscription_db_name = user_info.subscription_db_name if is_subscriber else None

    subscription_classes = {
        "unicode_guest": UnicodeGuest,
        "unicode_starter": UnicodeStandard,
        "unicode_base": UnicodeBase
    }

    subscription_class = subscription_classes.get(subscription_db_name, None)

    return {
        "result": is_subscriber,
        "is_subscribed_to_payments": is_subscriber and user_info.is_subscribed_to_payments,
        "subscription_end": is_subscriber and user_info.subscription_end,
        "subscription_db_name": subscription_db_name,
        "subscription_features": subscription_class.features if subscription_class else None,
    }
