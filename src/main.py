import logging
from tracemalloc import start
from decouple import config
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from utilities import get_inine_markup


API_TOKEN = config('API')
NUMBERS = ["ዜሮ", "አንድ", "ሁለት", "ሶስት", "አራት", "አምስት", "ስድስት", "ሰባት", "ስምንት", "ዘጠኝ", "አስር"]
CHANNEL_ID = -1001710132278

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    start = State()
    anv = State()
    anv_2 = State()

@dp.message_handler(commands=['start'], state='*')
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` command
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
        )
    )

    await bot.send_message(
        message.chat.id, 
        "Choose from an options👇",
        reply_markup=keyboard_markup
    )
    await Form.start.set()


##############################################################################################
# Amharic Numbers Voice #
@dp.callback_query_handler(text='amharic_numbers_voice', state=Form.start)
async def anv_inline_answer_callback_handler(query: types.CallbackQuery):
    answer_data = query.data

    keyboard_markup = get_inine_markup(
        (
            ("start", "anv_start"),
            ("help", "anv_help"),
        )
    )

    await query.message.edit_text(
        "ለዚኛው ጥናት ከ 0 እስከ 10 ድረስ ያሉትን ቁጥሮች በአማርኛ ድምፅ ያስፈልገናል።\
        ሁሉም ሪከርዶች ከ 1 - 5 ሰከንድ ባለው ውስጥ ቢሆኑ ይመረጣል። የድምፁ ጥራት አስፈላጊ አይደለም!\
        \nስለሆነም የቴሌግራም voice recorder በመጠቀም ይላኩልን። ስለ ሂደቱ እርዳታ ከፈለጉ ከስር help የሚለውን ይጫኑ። ዝግጁ ከሆኑ start የሚለውን ይጫኑ።\
        \n\n⚠️እባኮትን  ዳታውን ለጥናታዊ ጽሑፍ ስለምንጠቀመው ትክክለኛ ነገር እንዳስገቡ እርግጠኛ ይሁኑ!",
        reply_markup=keyboard_markup
)


@dp.callback_query_handler(text=['anv_start', 'anv_help'], state=Form.start)
async def anv_start_help_handler(query : types.CallbackQuery, state: FSMContext):
    answer = query.data
    if answer == "anv_start":
        await Form.anv.set()
        async with state.proxy() as data:
            data['current'] = 0
            data['voices'] = [None for i in range(11)]
        await bot.send_message(
            query.from_user.id,
            "nእባኮትን ዜሮ በማለት ሪከርድ አድርገው ይላኩ!"
        )
    elif answer == "anv_help":
        for i in [9, 10]:
            await bot.forward_message(
                query.from_user.id,
                CHANNEL_ID,
                i
            )
        await bot.send_message(
            query.from_user.id,
            "ለመጀመር ከታች Start የሚለውን ይጫኑ",
            reply_markup=get_inine_markup(
                (
                    ("start", "anv_start"),
                )
            )
        )


@dp.message_handler(state=Form.anv)
@dp.message_handler(content_types=['voice'], state=Form.anv)
async def anv_voice_handler(message: types.Message, state: FSMContext):
    # check if message is voice message
    if message.voice:
        confirm_keyboard = get_inine_markup([
            ("Next", "anv_confirm"),
            ("Retake", "anv_cancel"),
        ])
        await message.reply(
            "ወደቀጣይ ለመሄድ Next ይጫኑ። ድጋሚ ለመቅዳት Retake ይጫኑ።",
            reply_markup=confirm_keyboard
        )
        async with state.proxy() as data:
            data['voices'][data['current']] = message.voice.file_id
        await Form.next()
    else:
        async with state.proxy() as data:
            await message.reply(f"የቴሌግራም voice recorder በመጠቀም ትክክለኛ ቅጂ ያስገቡ!\nእባኮትን {NUMBERS[data['current']]} በማለት ሪከርድ አድርገው ይላኩ!")
        return


@dp.callback_query_handler(text=['anv_confirm', 'anv_cancel'], state=Form.anv_2)
async def anv_confirm_cancel_handler(query : types.CallbackQuery, state: FSMContext):
    answer = query.data
    if answer == "anv_confirm":
        async with state.proxy() as data:
            data['current'] += 1
            if data['current'] == 11:
                await bot.send_message(
                    query.from_user.id,
                    "ሁሉም ሪከርዶች ተሰጠው እርግጠኛ ይመረጣል። ከሆነም የተሰጠው ሪከርድ በማለት ላይ መመልከት ይችላሉ።"
                ) 

                for i in range(11):
                    await bot.send_voice(
                        CHANNEL_ID,
                        data['voices'][i],
                        caption=f"{query.from_user.first_name} {NUMBERS[i]}"
                    )
                await bot.send_message(
                    query.from_user.id,
                    "ሁሉንም ቅጂዎች አስገብተዋል እናመሰግናለን🙏"
                )

                await bot.send_message(
                    query.message.chat.id, 
                    "Choose from an options👇",
                    reply_markup=get_inine_markup(
                        (
                            ('Amharic Numbers Voice', 'amharic_numbers_voice'),
                        )
                    )
                )
                await Form.start.set()
            else:
                await query.answer("ሪከርዱ ተቀምጧል✅")
                await bot.delete_message(query.message.chat.id, query.message.message_id)
                await bot.send_message(
                    query.from_user.id,
                    f"እባኮትን {NUMBERS[data['current']]} በማለት ሪከርድ አድርገው ይላኩ!"
                )
                await Form.anv.set()

    elif answer == "anv_cancel":
        async with state.proxy() as data:
            await bot.delete_message(query.message.chat.id, query.message.message_id)
            await bot.send_message(
                query.from_user.id,
                f"እባኮትን {NUMBERS[data['current']]} በማለት ሪከርድ አድርገው ይላኩ!"
            )
            
            await Form.anv.set()

@dp.message_handler(state=Form.anv_2)
async def anv_2_handler(message: types.Message, state: FSMContext):
    await bot.delete_message(message.chat.id, message.message_id)

##############################################################################################

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)