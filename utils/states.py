from aiogram.fsm.state import State, StatesGroup


class Question(StatesGroup):
    position = State()
    info = State()


class Material(StatesGroup):
    descr = State()
    info = State()


class Interview(StatesGroup):
    position = State()
    company = State()
    info = State()


class Mentor(StatesGroup):
    actions = State()
    confirm_delete = State()
    name = State()
    direction = State()
    descr = State()
    price = State()
    contact = State()
