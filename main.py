from aiogram import types
from aiogram.utils import executor
from database.manager import DBManager
from config import dp
from keyboards.mods_variety_kb import keyboard_mods
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text  #Пусть будет
from GPT.gpt import create_req


class Vacancie(StatesGroup):
    '''Класс состояний, позволит сконструировать цепочку запросов от телеграмма к программе, позволяет избежать ошибок'''
    wait_emp_name = State()
    wait_name = State()

class WaitingUserAnswers(StatesGroup):
    wait_user_ans = State()
    waiting_user_characters = State()
    wait_user_require = State()
    wait_user_achievements = State()
    wait_user_education_and_profile = State()


@dp.message_handler(commands='start')
async def choose_operating_mode(message: types.Message):
    await message.answer('Выбери режим работы', reply_markup=keyboard_mods)

@dp.message_handler(Text(equals='GPT'))
async def response(message:types.Message, state=FSMContext):
    await state.reset_state()
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton('Помоги')).add(KeyboardButton('Нет, спасибо'))
    await message.answer('Привет, я бот помощник, я могу помочь определиться тебе с профессией если хочешь)',
                         reply_markup=kb)
    await state.set_state(WaitingUserAnswers.wait_user_ans.state)


@dp.message_handler(content_types=['text'], state=WaitingUserAnswers.wait_user_ans)
async def first_step(message: types.Message, state=FSMContext):
    if message.text == 'Помоги':
        await state.update_data(choosen_ans=message.text)
        await state.set_state(WaitingUserAnswers.waiting_user_characters.state)
        await message.answer('Хорошо, давай начнем!\n\nРасскажи о себе по подробнее, не стесняйся, это конфиденциальная информация, можешь рассказать о своих увлечениях, хобби и т.п.')

    elif message.text == 'Нет, спасибо':
        await state.finish()
        await message.answer('Выбери мод', reply_markup=keyboard_mods)

    else:
        await message.answer('Выбирай ответы из списка пожалуйста)')


@dp.message_handler(content_types=['text'], state=WaitingUserAnswers.waiting_user_characters)
async def second_step(message:types.Message, state=FSMContext):
    await state.update_data(user_сharacters=message.text)
    await message.answer('отлично, теперь я хотел бы узнать кем бы ты сам хотел стать, если не знаешь то так и скажи)')
    await state.set_state(WaitingUserAnswers.wait_user_require.state)


@dp.message_handler(content_types=['text'], state=WaitingUserAnswers.wait_user_require)
async def third_step(message: types.Message, state=FSMContext):
    await state.update_data(user_require=message.text)
    await message.answer('хорошо) теперь расскажи пожалуйста про свои достижения в любой области')
    await state.set_state(WaitingUserAnswers.wait_user_achievements.state)


@dp.message_handler(content_types=['text'], state=WaitingUserAnswers.wait_user_achievements)
async def forth_step(message: types.Message, state=FSMContext):
    await state.update_data(user_achievements=message.text)
    await message.answer('Осталось немного, напиши пожалуйста свой профиль на котором ты учишься или учился, а так же какое у тебя образование')
    await state.set_state(WaitingUserAnswers.wait_user_education_and_profile.state)


@dp.message_handler(content_types=['text'], state=WaitingUserAnswers.wait_user_education_and_profile)
async def final_step(message: types.Message, state=FSMContext):
    await message.answer('Придется подождать несколько минут...')
    await state.update_data(user_profile_and_edc=message.text)
    data = await state.get_data()
    response = f"Мои характеристки: {data['user_сharacters']}, мои пожелания в плане работы: {data['user_require']}, вот мои достижения - {data['user_achievements']}, а вот мой профиль на котором я учусь: {data['user_profile_and_edc']}. Сделай пожалуйста на основе данных из прошлого предложения какие профессии мне могут подойти."
    print(f"{message.from_user.first_name} - {message.from_user.last_name}\n{response}")
    await message.answer(f"{create_req(response)}")
    await state.finish()


@dp.message_handler(Text(equals='Работодатели'))
async def says(message: types.Message, state=FSMContext):
    '''При передаче команды start, запускает состояния, отдает пользователю кнопки с существующими на данный момент работодателями'''
    await state.reset_state()  #Обновляет состояния при возвращении на главную
    obj_ = DBManager()
    await state.set_state(Vacancie.wait_emp_name.state)
    await message.answer(f'Приветствую тебя {message.from_user.first_name}, такие работодатели сейчас есть:', reply_markup=obj_.keyboard())


@dp.message_handler(content_types=['text'], state=Vacancie.wait_emp_name)
async def return_info_about_employer(message: types.Message, state=FSMContext):
    '''Возвращет пользователю кнопки с вакансиями выбранного работодателя на предыдущем шаге'''
    await state.set_state(Vacancie.wait_name.state) # ставит ожидание имени вакансии
    await state.update_data() # обновляет прошлое состояние, оно считается завершенным
    global id
    obj = DBManager()
    text = obj.get_info(message.text)
    try:
        id = text[0][2] # id работодателя на hh.ru
    except Exception:
        pass
    obj.post_employers_vacancies_to_db(id)
    vacancies = obj.get_vacancies(id)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for vacancie in vacancies:
        keyboard.add(vacancie[-1])
    keyboard.add(KeyboardButton('Назад'))
    await message.answer('Такие вакансии сейчас есть у этого работодателя', reply_markup=keyboard)


@dp.message_handler(content_types=['text'], state=Vacancie.wait_name)
async def get_info_vacancie(message: types.Message, state=FSMContext):
    '''Возвращает пользователю данные о выбранной пользователем вакансии на прошлом этапе'''
    if message.text == 'Назад':
        await state.finish()
        await message.answer('Возврат на главную', reply_markup=keyboard_mods)
    else:
        obj = DBManager()
        await state.update_data()
        vacancies = obj.get_vacancies(id)
        for vacancie in vacancies:
            if message.text in vacancie:
                await message.answer(f"{vacancie[-1]}\n\nТребования:\n{vacancie[-2]}\n\nСсылка на вакансию:\n{vacancie[-4]}\n\nЗарплата: {vacancie[-3]}руб", parse_mode='HTML')
                break
    #P.S. в state.update_data() можно записать полученные данные update_data(name=message.text) и в дальнейшем сформировать словарь,
    #Например вы хотите создать вакансию и через состояния можно записать все полученные данные в словарь и запостить их в ваше бд,
    #упростит вам работу


if __name__ == '__main__':
    test = DBManager()
    test.create_customers_table()
    test.create_vacancie_table()
    # print(test.get_companies_and_vacancies_count())
    # print(test.get_all_vacancies())
    # print(test.get_avg_salary())
    # print(test.get_vacancies_with_keyword('specialist'))
    executor.start_polling(dispatcher=dp, skip_updates=True)