from aiogram import types
from aiogram.utils import executor
from database.manager import DBManager
from config import dp
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

class Vacancie(StatesGroup):
    wait_emp_name = State()
    wait_name = State()


@dp.message_handler(commands=['start'])
async def says(message: types.Message, state=FSMContext):
    await state.reset_state()
    obj_ = DBManager()
    await state.set_state(Vacancie.wait_emp_name.state)
    await message.answer(f'Приветствую тебя {message.from_user.first_name}, такие работодатели сейчас есть:', reply_markup=obj_.keyboard())


@dp.message_handler(content_types=['text'], state=Vacancie.wait_emp_name)
async def return_info_about_employer(message: types.Message, state=FSMContext):
    await state.set_state(Vacancie.wait_name.state)
    await state.update_data()
    global id
    obj = DBManager()
    text = obj.get_info(message.text)
    try:
        id = text[0][2]
    except Exception:
        pass
    obj.post_employers_vacancies_to_db(id)
    vacancies = obj.get_vacancies(id)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for vacancie in vacancies:
        keyboard.add(vacancie[-1])
    await message.answer('Такие вакансии сейчас есть у этого работодателя', reply_markup=keyboard)

@dp.message_handler(content_types=['text'], state=Vacancie.wait_name)
async def get_info_vacancie(message: types.Message, state=FSMContext):
    obj = DBManager()
    await state.update_data()
    vacancies = obj.get_vacancies(id)
    for vacancie in vacancies:
        if message.text in vacancie:
            await message.answer(f"{vacancie[-1]}\n\nТребования:\n{vacancie[-2]}\n\nСсылка на вакансию:\n{vacancie[-4]}\n\nЗарплата: {vacancie[-3]}руб", parse_mode='HTML')
            break



if __name__ == '__main__':
    test = DBManager()
    executor.start_polling(dispatcher=dp, skip_updates=True)