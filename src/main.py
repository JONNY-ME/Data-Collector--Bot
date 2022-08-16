import logging
from decouple import config
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from utilities import get_inine_markup


API_TOKEN = config('API')
NUMBERS = ["ዜሮ", "አንድ", "ሁለት", "ሶስት", "አራት", "አምድት", "ስድስት", "ሰባት", "ስምንት", "ዘጠኝ", "አስር"]


# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    anv = State()

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi👋 Welcome!\
        \nWe use this bot for the purpose of data gathering for different research purposes.\
        \n   ✅Your data is safe with us!\
        \n   ✅None of your personal Info is required!\
        \nThankyou for your collabration🙏"
    )


    keyboard_markup = get_inine_markup(
        (
            ('Amharic Numbers Voice', 'amharic_numbers_voice'),
            # (),
        )
    )

    await bot.send_message(
        message.chat.id, 
        "Choose from an options👇",
        reply_markup=keyboard_markup
    )

@dp.callback_query_handler(text='amharic_numbers_voice')  
async def anv_inline_answer_callback_handler(query: types.CallbackQuery):
    answer_data = query.data
    # always answer callback queries, even if you have nothing to say
    # await query.answer(f'You answered with {answer_data!r}')

    keyboard_markup = get_inine_markup(
        (
            ("start", "anv_start"),
            ("help", "anv_help"),
        )
    )

    await bot.send_message(
        query.from_user.id, 
        "ለዚኛው ጥናት ከ 0 እስከ 10 ድረስ ያሉትን ቁጥሮች በአማርኛ ድምፅ ያስፈልገናል።\
        \nስለሆነም የቴሌግራም voice recorder በመጠቀም ይላኩልን። ስለ ሂደቱ እርዳታ ከፈለጉ ከስር help የሚለውን ይጫኑ። ዝግጁ ከሆኑ start የሚለውን ይጫኑ።\
        \n\n⚠️እባኮትን  ዳታውን ለጥናታዊ ጽሑፍ ስለምንጠቀመው ትክክለኛ ነገር እንዳስገቡ እርግጠኛ ይሁኑ!",
        reply_markup=keyboard_markup
)


@dp.callback_query_handler(text=['anv_start', 'anv_help'])
async def anv_start_help_handler(query : types.CallbackQuery, state: FSMContext):
    answer = query.data
    if answer == "anv_start":
        await Form.anv.set()
        async with state.proxy() as data:
            data['current'] = 0
        await bot.send_message(
            query.from_user.id,
            "ሁሉም ሪከርዶች ከ 3 - 10 ሰከንድ ባለው ውስጥ ቢሆኑ ይመረጣል። የድምፁ ጥራት አስፈላጊ አይደለም!\
            \nእባኮትን ዜሮ በማለት ሪከርድ አድርገው ይላኩ!"
        )
    elif answer == "anv_help":
        pass 



@dp.message_handler(state=Form.anv)
async def process_voice_accepting(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        print(data['current'])

    print(message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)