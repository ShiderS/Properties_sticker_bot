from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

kb_user = [
    [KeyboardButton(text="Обратная связь")],
    [KeyboardButton(text="Создать стикерпак")],
    [KeyboardButton(text="Помощь")],
]
keyboard_user = ReplyKeyboardMarkup(keyboard=kb_user)


kb_user_pattern = [
    [KeyboardButton(text="Выбрать шаблон")],
    [KeyboardButton(text="Создать шаблон")],
    [KeyboardButton(text="Меню")],
]
keyboard_user_pattern = ReplyKeyboardMarkup(keyboard=kb_user_pattern)


kb_user_create_pattern = [
    [KeyboardButton(text="Публичный")],
    [KeyboardButton(text="Приватный")],
    [KeyboardButton(text="Меню")],
]
keyboard_user_create_pattern = ReplyKeyboardMarkup(
    keyboard=kb_user_create_pattern,
)
