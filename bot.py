import logging
import sys
import asyncio
import random
import os
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode

# === Настройки ===
BOT_TOKEN = "your_bot_token"  # ← Замените на ваш токен от @BotFather
IMAGE_PATH = "cards"

# === Данные: карты и описания ===
DAILY_CARDS = {
    "Суд": (
        "Сегодня вы можете решить свою проблему — хоть только что возникшую, хоть застарелую.\n"
        "Просто держите глаза открытыми, чтобы не упустить эту возможность.\n"
        "Возможно, вам и не нужно будет ничего делать, — только ждать.\n\n"
        "Хотя иногда, чтобы найти окончательное решение, бывает нужен небольшой внутренний толчок.",
        "sud.jpg"
    ),
    "Дьявол": (
        "Хотя черт и не так страшен, как его малюют, однако сегодня вам, видимо, придется встретиться с теневой стороной своего характера.\n"
        "Возможно, вас будут склонять к какому-то неблаговидному поступку или к измене своим принципам.\n\n"
        "Это может быть и какое-то внезапное внутреннее побуждение, которого вы за собой не подозревали (или думали, что давно преодолели его) — зависть, ревность, алчность или жажда власти.\n"
        "Не стоит ни злиться на себя за это, ни взваливать вину на других, как не стоит и пытаться подавить в себе это побуждение.",
        "dyavol.jpg"
    ),
    "Колесо Фортуны": (
        "Бывают дни, когда мы должны покориться неизбежному.\n"
        "Если вы ощущаете, что события надвигаются неумолимо, то и дайте им произойти.\n"
        "Помните, что у каждого события есть свой смысл, даже если от нас он еще скрыт.\n\n"
        "Так что вполне возможно, что и для вас в конце концов все обернется к лучшему.",
        "koleso_fortuny.jpg"
    )
}

YES_NO_ANSWERS = [
    "Ответ на твой вопрос, однозначно да!",
    "К сожалению, нет!"
]

LOVE_LAYOUTS = {
    "Отношения": (
        "Будущее с загаданным мужчиной представляется невозможным. Оно окутано тайной. Увы, но будущее с этим человеком не принесёт вам счастья. "
        "Он вас не любит или же окажется не тем, за кого себя выдаёт. Доверять ему нельзя. Такие люди обычно стремятся к собственным интересам, "
        "не обращая внимания на чувства других. Они могут легко изменить вам и оставить вас наедине с проблемами. Не стоит ждать от такого человека честности и преданности. "
        "Ваша жизнь может быть запутанной и полной разочарований, если вы продолжите отношения с ним. Лучше найти кого-то, кто будет искренне вас любить и заботиться о вас.",
        "otnosheniya.jpg"
    ),
    "Чувства": (
        "Карты говорят о том, что он видит в вас вторую половинку и не представляет без вас свою жизнь. Его чувства к вам глубоки и искренни. "
        "Между вами существует крепкая эмоциональная связь, которую нелегко разорвать. Он ценит вашу поддержку, понимание и заботу. "
        "Только лишь с вами мужчина может поделиться самым сокровенным. В его сердце вы занимаете особое место. "
        "Несмотря на любые препятствия, ссоры или недопонимания, его любовь к вам не угаснет. Он готов идти на компромиссы и прилагать усилия для сохранения ваших отношений. "
        "В будущем вас ждёт много счастливых и радостных моментов вместе. Доверяйте своей интуиции и чувствам. Они не обманывают вас.",
        "chuvstva.jpg"
    ),
    "Перспектива": (
        "Начало отношений очень вероятно, если вы решитесь сделать первый шаг. Не бойтесь проявить инициативу. "
        "Иногда первый шаг может быть как простым знакомством, так и более серьёзным жестом, который выражает наши чувства. "
        "Важно осознавать, что любовь требует от нас усилий и готовности к риску, но именно эти моменты делают наши отношения более ценными и интересными. "
        "Не стоит ограничивать себя страхом или сомнениями — каждый новый этап в наших отношениях открывает перед нами новые возможности для роста и развития. "
        "Помните, что инициатива может проявляться в самых разных формах, и главное — это быть искренними и открытыми в выражении своих чувств.",
        "perspektiva.jpg"
    )
}

WORK_LAYOUTS = {
    "Расклад первый": (
        "Шестерка Мечей толкуется как умение слаженно работать в коллективе, как готовность воспринимать и применять в работе инновационные идеи и методы, "
        "а также как способность мыслить глобально, масштабно. Этот Аркан предполагает удачное применение знаний для решения вполне практических, утилитарных задач. "
        "Человек, которому выпал такой Аркан, наверняка найдет себя в сетевом бизнесе, сможет немало достичь на научном поприще. "
        "Еще одно отличительное значение Шестерки Мечей – стремление работать на себя, неприятие работы по найму. "
        "Кроме того, в данном случае вполне можно говорить о какой-нибудь свободной профессии, например, художника или писателя.",
        "rasclad1.jpg"
    ),
    "Расклад второй": (
        "Императрица предвещает творческую работу или перспективную должность. Для того, кому поручена реализация очень ответственного проекта, "
        "эта карта служит знаком очень добросовестного и плодотворного выполнения стоящих задач. Императрица может свидетельствовать о возможности свободного развития своих талантов, "
        "о повышении зарплаты, о приятных нововведениях и переменах на рабочем месте, которые связаны с материальной сферой (например, это может быть ремонт в личном кабинете, "
        "изменение рабочего графика на более удобный и комфортный и т.д.)",
        "rasclad2.jpg"
    ),
    "Расклад третий": (
        "Четверка Мечей в перевернутом виде обозначает ситуацию, когда человек оказался совсем не в нужное время в отнюдь не подходящем месте, "
        "да еще и с не очень хорошими людьми. И именно это является причиной выхода из состояния покоя (пассивности, привычной повседневности и т.п.). "
        "Когда перевернутая Четверка Мечей описывает человека, то ее значения – расхлябанность, отставание, спутанность в мыслях.\n\n"
        "Стабильный мирок, семья и друзья снова дают вам возможность попробовать свои силы. Будьте осторожны и благоразумны, в следующий раз этой помощи может не хватить. "
        "Вокруг вас и ваших дел ситуация накаляется.",
        "rasclad3.jpg"
    )
}

WISH_RESPONSES = [
    ("Твоё желание обязательно сбудется!", "wish_yes.jpg"),
    ("Твоё желание сбудется, но нужно приложить усилия для его исполнения", "wish_maybe.jpg"),
    ("К сожалению, твоё желание не сбудется, трудись дальше!", "wish_no.jpg")
]

# === Инициализация ===
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# === Главное меню ===
def main_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="🎴 Карта дня", callback_data="card_of_day")
    builder.button(text="❓ Быстрый вопрос (Да/Нет)", callback_data="yes_no")
    builder.button(text="❤️ Любовный расклад", callback_data="love_layout")
    builder.button(text="✨ Расклад на желание", callback_data="wish_layout")
    builder.button(text="💼 Расклад на работу/деньги", callback_data="work_layout")
    builder.button(text="📞 Связаться с тарологом", callback_data="contact")
    builder.adjust(2, 2, 1, 2)
    return builder.as_markup()

# === /start ===
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("🔮 Добро пожаловать в Таро-бота!\nВыберите действие:", reply_markup=main_menu())

# === Обработчики ===
@dp.callback_query(lambda c: c.data == "card_of_day")
async def card_of_day(callback: CallbackQuery):
    await callback.answer()
    name = random.choice(list(DAILY_CARDS.keys()))
    desc, img = DAILY_CARDS[name]
    path = os.path.join(IMAGE_PATH, img)
    if os.path.isfile(path):
        await callback.message.answer_photo(
            photo=FSInputFile(path),
            caption=f"🎴 <b>{name}</b>\n\n{desc}",
            parse_mode=ParseMode.HTML
        )
    else:
        await callback.message.answer(f"🎴 <b>{name}</b>\n\n{desc}", parse_mode=ParseMode.HTML)
    await callback.message.answer("Выберите следующее действие:", reply_markup=main_menu())

@dp.callback_query(lambda c: c.data == "yes_no")
async def yes_no_question(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Задайте любой вопрос мысленно, а я отвечу «Да» или «Нет».")
    await asyncio.sleep(20)
    ans = random.choice(YES_NO_ANSWERS)
    await callback.message.answer(f"🔮 {ans}")
    await callback.message.answer("Выберите следующее действие:", reply_markup=main_menu())

@dp.callback_query(lambda c: c.data == "love_layout")
async def love_layout_menu(callback: CallbackQuery):
    await callback.answer()
    builder = InlineKeyboardBuilder()
    for key in LOVE_LAYOUTS:
        builder.button(text=key, callback_data=f"love_{key}")
    builder.button(text="← Назад", callback_data="back")
    builder.adjust(1)
    await callback.message.edit_text("Выберите позицию в любовном раскладе:", reply_markup=builder.as_markup())

@dp.callback_query(lambda c: c.data.startswith("love_"))
async def send_love_layout(callback: CallbackQuery):
    await callback.answer()
    key = callback.data[5:]  # убираем "love_"
    if key in LOVE_LAYOUTS:
        desc, img = LOVE_LAYOUTS[key]
        path = os.path.join(IMAGE_PATH, img)
        if os.path.isfile(path):
            await callback.message.answer_photo(
                photo=FSInputFile(path),
                caption=f"❤️ <b>{key}</b>\n\n{desc}",
                parse_mode=ParseMode.HTML
            )
        else:
            await callback.message.answer(f"❤️ <b>{key}</b>\n\n{desc}", parse_mode=ParseMode.HTML)
    await callback.message.answer("Выберите следующее действие:", reply_markup=main_menu())

@dp.callback_query(lambda c: c.data == "work_layout")
async def work_layout(callback: CallbackQuery):
    await callback.answer()
    name = random.choice(list(WORK_LAYOUTS.keys()))
    desc, img = WORK_LAYOUTS[name]
    path = os.path.join(IMAGE_PATH, img)
    if os.path.isfile(path):
        await callback.message.answer_photo(
            photo=FSInputFile(path),
            caption=f"💼 <b>{name}</b>\n\n{desc}",
            parse_mode=ParseMode.HTML
        )
    else:
        await callback.message.answer(f"💼 <b>{name}</b>\n\n{desc}", parse_mode=ParseMode.HTML)
    await callback.message.answer("Выберите следующее действие:", reply_markup=main_menu())

@dp.callback_query(lambda c: c.data == "wish_layout")
async def wish_layout(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("✨ Загадайте своё желание мысленно...")
    await asyncio.sleep(20)
    desc, img = random.choice(WISH_RESPONSES)
    path = os.path.join(IMAGE_PATH, img)
    if os.path.isfile(path):
        await callback.message.answer_photo(
            photo=FSInputFile(path),
            caption=f"✨ {desc}",
            parse_mode=ParseMode.HTML
        )
    else:
        await callback.message.answer(f"✨ {desc}")
    await callback.message.answer("Выберите следующее действие:", reply_markup=main_menu())

@dp.callback_query(lambda c: c.data == "contact")
async def contact_tarologist(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Вы можете связаться с тарологом напрямую в мессенджере:\n\n📱 +79782147666")
    await callback.message.answer("Выберите следующее действие:", reply_markup=main_menu())

@dp.callback_query(lambda c: c.data == "back")
async def back_to_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text("🔮 Выберите действие:", reply_markup=main_menu())

# === Запуск ===
async def main():
    # Настройка логгера для aiogram (опционально, но полезно)
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # Информационное сообщение в консоль
    print("✅ Бот запускается...")
    print("⏳ Ожидание подключения к Telegram...")

    try:
        # Удаляем вебхук перед запуском polling
        print("🔄 Удаление вебхука...")
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Вебхук удален, запуск polling...")
        
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен вручную.")
    except Exception as e:
        print(f"❌ Произошла ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
