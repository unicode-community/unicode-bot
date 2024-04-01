from fastapi import Depends, FastAPI

from db.database import Database, get_db
from utils.subscriptions import get_subscription_status

app = FastAPI()

@app.get("/subscribers/{tg_id}")
async def check_subscription_status(tg_id: int, db: Database = Depends(get_db)):
    return await get_subscription_status(user_tg_id=tg_id, db=db)
