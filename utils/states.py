from aiogram.fsm.state import State, StatesGroup


class Question(StatesGroup): # Раздел "Вопросы с собеседования"
    position = State()
    info = State()


class Material(StatesGroup): # Раздел "Полезные материалы"
    descr = State()
    info = State()


class Interview(StatesGroup): # Раздел "Резюме собеса"
    position = State()
    company = State()
    info = State()


class Other(StatesGroup): # Раздел "Другое"
    info = State()


class Mentor(StatesGroup):
    actions = State()
    confirm_delete = State()
    name = State()
    area = State()
    descr = State()
    price = State()
    contact = State()


class Subscription(StatesGroup):
    confirm_delete = State()


class NewChat(StatesGroup):
    name = State()


class Support(StatesGroup):
    message = State()


class Admin(StatesGroup):
    segment = State()
    message = State()
    find_user = State()
