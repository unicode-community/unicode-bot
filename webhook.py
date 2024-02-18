from datetime import datetime

from fastapi import FastAPI, Depends
from db.database import get_db, Database

app = FastAPI()

@app.get("/subscribers/{tg_id}")
async def check_subscription_status(tg_id: int, db: Database = Depends(get_db)):
    user_info = await db.get_subscriber(user_id=tg_id)
    is_subscriber = (user_info is not None) and (user_info.subscription_start <= datetime.now() <= user_info.subscription_end)

    return {
        'result': is_subscriber
    }
