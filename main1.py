
import logging
import openai
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from googletrans import Translator



API_TOKEN = None
UNSPLASH_ACCESS_KEY = None

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())



openai.api_key = None


info_callback = CallbackData("info", "action")


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    info_button = InlineKeyboardButton(text="Информация", callback_data=info_callback.new(action="show_info"))
    keyboard.add(info_button)
    await message.reply("Привет! я твой универсальный разговорный помощник!.", reply_markup=keyboard)

@dp.callback_query_handler(info_callback.filter(action="show_info"))
async def show_info(callback_query: types.CallbackQuery, callback_data: dict):
    await callback_query.message.answer("Этот бот был разработан для проекта СИРИУС.ИИ.")
    await callback_query.answer()

translator = Translator()

def translate_text(text, dest_language):
    return translator.translate(text, dest=dest_language).text

async def generate_gpt_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=124
    )
    return response.choices[0].text.strip()

async def send_image_by_context(context, message):
    translated_context = translate_text(context, 'en')

    url = f"https://api.unsplash.com/search/photos?query={translated_context}&client_id={UNSPLASH_ACCESS_KEY}"
    response = requests.get(url)
    if response.status_code == 200 and response.json()['results']:
        image_url = response.json()['results'][0]['urls']['regular']
        caption_en = f"Yes, sure! This is image for you request - {translated_context}"
        caption_ru = translate_text(caption_en, 'ru')  # Перевод описания обратно на русский
        await message.reply_photo(photo=image_url, caption=caption_ru)
    else:
        await message.reply("Извините, но я не смог сгенерировать это :(")

@dp.message_handler()
async def handle_message(message: types.Message):
    user_input = message.text.lower()

    if any(keyword in user_input for keyword in ['отправь', 'скинь', 'покажи', 'фото', 'прислать', 'показать', 'скниуть', 'скинуть', 'покаж', 'откинуть картинку', 'картинку','фотку', 'фотографию', 'изображение',]):
        prompt_for_image = user_input.split(maxsplit=1)[1] if ' ' in user_input else ""
        await send_image_by_context(prompt_for_image, message)
    else:
        gpt_response = await generate_gpt_response(user_input)
        await message.reply(gpt_response)

if __name__ == '__main__':
    import asyncio

    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling())
    loop.run_forever()
