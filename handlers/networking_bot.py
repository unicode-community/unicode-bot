from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from db.database import Database
from keyboards.general import subscribe_and_return_to_menu
from keyboards.networking_bot import redirect_to_bot_and_return_to_menu
from messages.networking_bot import add_for_unsubscribers, welcome_networking_bot
from utils import get_subscription_status

router = Router()

@router.callback_query(F.data == "unicode_networking")
async def networking_bot(callback: types.CallbackQuery, state: FSMContext, db: Database) -> None:
    await state.clear()
    subscriber_info = await get_subscription_status(user_tg_id=callback.from_user.id, db=db)

    access_to_networking_bot = (
        (subscriber_info["subscription_db_name"] is not None)
        and ("Доступ к боту для IT знакомств" in subscriber_info["subscription_features"])
    )
    if access_to_networking_bot:
        await callback.message.answer(
            text=welcome_networking_bot,
            reply_markup=redirect_to_bot_and_return_to_menu
        )
    else:
        await callback.message.answer(
            text=welcome_networking_bot + "\n" + add_for_unsubscribers,
            reply_markup=subscribe_and_return_to_menu
        )
    await callback.answer()
