import asyncio
import random
import asyncpg
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, MenuButtonWebApp

# --- НАЛАШТУВАННЯ ---
TOKEN = "8651975082:AAFlZvdRVKjddrZvy_UwA-FsemEDik5ZfXg"

# Точний і перевірений рядок підключення до Supabase
DB_URI = "postgresql://postgres.mngdxiparifskygfmpdx:DaniilTorba18177@aws-0-eu-west-1.pooler.supabase.com:6543/postgres?sslmode=require"

# Твоя партнерська ссилка First Casino
CASINO_LINK = "https://1casinowin.com/?refcode=68ee9add-a6e4-4cc3-b714-09930c4ff705&subid=%7B%7Bsubid%7D%7D&clickid=%7B%7Bclickid%7D%7D&utm_source=tg&utm_medium=zakrouokno_-__(tt+tg)&utm_campaign=zakrouoknotg"

TG_CHANNEL_LINK = "https://t.me/freespinsbotfirst" 
CHANNEL_ID = "@freespinsbotfirst" 

# Твій єдиний ID в admin'ах
ADMIN_IDS = [6299034881] 

MANAGER_NAMES = ["Артем", "Андрій", "Максим", "Олександр", "Дмитро", "Сергій"]

# Кнопки для юзерів
BTN_BONUS = "✦ АКТИВУВАТИ БОНУС"
BTN_INFO = "📖 ІНСТРУКЦІЯ"
BTN_MANAGER = "👨‍💻 ЗВ'ЯЗОК З МЕНЕДЖЕРОМ"
MENU_BUTTONS_USER = [BTN_BONUS, BTN_INFO, BTN_MANAGER]

# Кнопки для адміна
BTN_ADMIN_STATS = "📊 СТАТИСТИКА"
BTN_ADMIN_SEND = "✉️ ЗРОБИТИ РОЗСИЛКУ"
BTN_ADMIN_TEMPLATES = "📁 ШАБЛОНИ РОЗСИЛКИ"
BTN_ADMIN_BACK = "◀️ НАЗАД В АДМІНКУ"

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- СТАНИ ДЛЯ FSM АДМІНКИ ---
class AdminStates(StatesGroup):
    waiting_for_broadcast = State()
    waiting_for_template_name = State()
    waiting_for_template_content = State()

# --- ІНІЦІАЛІЗАЦІЯ ХМАРНОЇ БАЗИ (PostgreSQL) ---
async def init_db():
    conn = await asyncpg.connect(DB_URI)
    # Таблиця користувачів
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            reg_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_spin TEXT
        )
    """)
    # Таблиця кліків (аналітика)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS clicks (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            action_type TEXT DEFAULT 'casino_click', 
            click_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Таблиця шаблонів розсилки
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS templates (
            id SERIAL PRIMARY KEY,
            title TEXT,
            text TEXT,
            photo_id TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    await conn.close()

async def log_click(user_id, action_type="casino_click"):
    conn = await asyncpg.connect(DB_URI)
    await conn.execute("INSERT INTO clicks (user_id, action_type) VALUES ($1, $2)", user_id, action_type)
    await conn.close()

# --- КЛАВІАТУРИ ---
def get_user_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=BTN_BONUS)],
        [KeyboardButton(text=BTN_INFO)],
        [KeyboardButton(text=BTN_MANAGER)]
    ], resize_keyboard=True)

def get_admin_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=BTN_ADMIN_STATS)],
        [KeyboardButton(text=BTN_ADMIN_SEND), KeyboardButton(text=BTN_ADMIN_TEMPLATES)]
    ], resize_keyboard=True)

def get_casino_inline():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 ЗАБРАТИ БОНУС В FIRST CASINO", url=CASINO_LINK)]
    ])

# --- СИНЯ КНОПКА ВЕБ-АППА ---
async def set_blue_menu_button(user_id: int):
    try:
        await bot.set_chat_menu_button(
            chat_id=user_id,
            menu_button=MenuButtonWebApp(
                text="📱 НА САЙТ",
                web_app=WebAppInfo(url=CASINO_LINK)
            )
        )
    except Exception as e:
        print(f"Помилка встановлення синьої кнопки: {e}")

# --- ОПИС БОТА ---
async def set_bot_description():
    try:
        desc_text = (
            "✦ FIRST CASINO | Офіційний бот активації\n\n"
            "Бот для миттєвого підключення твого Telegram ID до ліцензійної системи казино №1 в Україні.\n\n"
            "▼ Що вміє цей бот:\n"
            "✦ Активує бездепозитний бонус 275 ГРН для нових гравців\n"
            "✦ Нараховує пакет щоденних Фріспінів (ФС) за твоїм ID\n"
            "✦ Відкриває сторінку реєстрації прямо всередині Telegram\n\n"
            "Натискай «СТАРТ» нижче, щоб зафіксувати свои бонуси та відкрити сайт First Casino!"
        )
        await bot.set_my_description(description=desc_text)
    except Exception as e:
        print(f"Помилка встановлення опису бота: {e}")

# --- АДМІН-ПАНЕЛЬ СУВОРО ПО КОМАНДІ /admin ---
@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if message.from_user.id not in ADMIN_IDS: return
    await message.answer("💼 <b>Панель управління кнопками активована:</b>", reply_markup=get_admin_keyboard(), parse_mode="HTML")

@dp.message(F.text == BTN_ADMIN_BACK)
async def admin_back(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    await state.clear()
    await message.answer("💼 Панель адміністратора:", reply_markup=get_admin_keyboard())

# --- ДЕТАЛЬНА СТАТИСТИКА ---
@dp.message(F.text == BTN_ADMIN_STATS)
async def admin_stats(message: types.Message):
    if message.from_user.id not in ADMIN_IDS: return
    
    conn = await asyncpg.connect(DB_URI)
    total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
    users_today = await conn.fetchval("SELECT COUNT(*) FROM users WHERE reg_date >= NOW() - INTERVAL '1 day'")
    users_week = await conn.fetchval("SELECT COUNT(*) FROM users WHERE reg_date >= NOW() - INTERVAL '7 days'")
    unique_casino_clicks = await conn.fetchval("SELECT COUNT(DISTINCT user_id) FROM clicks WHERE action_type = 'casino_click'")
    total_casino_clicks = await conn.fetchval("SELECT COUNT(*) FROM clicks WHERE action_type = 'casino_click'")
    await conn.close()
    
    click_conversion = (unique_casino_clicks / total_users * 100) if total_users > 0 else 0
    
    stats_text = (
        "📊 <b>ДЕТАЛЬНА АНАЛІТИКА ВОРОНКИ (FIRST CASINO):</b>\n\n"
        "👥 <b>Трафік у боті:</b>\n"
        f"├ Всього у базі: <b>{total_users} юзерів</b>\n"
        f"├ За останні 24 год: <b>+{users_today}</b>\n"
        f"└ За останні 7 днів: <b>+{users_week}</b>\n\n"
        "🎯 <b>Переходи на форму реєстрації:</b>\n"
        f"├ Унікальних переходів: <b>{unique_casino_clicks}</b>\n"
        f"├ Загальна кількість кліків: <b>{total_casino_clicks}</b>\n"
        f"└ <b>Чиста конверсія бота (CR): {click_conversion:.2f}%</b>"
    )
    await message.answer(stats_text, parse_mode="HTML")

# --- РОЗСИЛКА (З ВИБОРОМ ШАБЛОНУ) ---
@dp.message(F.text == BTN_ADMIN_SEND)
async def admin_send_choose_type(message: types.Message):
    if message.from_user.id not in ADMIN_IDS: return
    
    conn = await asyncpg.connect(DB_URI)
    templates = await conn.fetch("SELECT id, title FROM templates")
    await conn.close()
    
    inline_kb = [[InlineKeyboardButton(text="✏️ Надіслати нове повідомлення", callback_data="bc_type_new")]]
    
    if templates:
        inline_kb.append([InlineKeyboardButton(text="─── АБО ОБЕРІТЬ ШАБЛОН ───", callback_data="ignore")])
        for row in templates:
            inline_kb.append([InlineKeyboardButton(text=f"📋 {row['title']}", callback_data=f"tmpl_view_{row['id']}")])
            
    markup = InlineKeyboardMarkup(inline_keyboard=inline_kb)
    await message.answer("✉️ <b>Оберіть варіант розсилки:</b>\n\nВи можете надіслати новий матеріал прямо зараз або вибрати один із раніше створених шаблонів:", reply_markup=markup, parse_mode="HTML")

@dp.callback_query(F.data == "bc_type_new")
async def admin_send_new_trigger(call: types.CallbackQuery, state: FSMContext):
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=BTN_ADMIN_BACK)]], resize_keyboard=True)
    await state.set_state(AdminStates.waiting_for_broadcast)
    await call.message.answer("📝 <b>Надішліть матеріал для розсилку.</b>\n\nЦе може бути чистий текст або картинка з підписом:", reply_markup=kb, parse_mode="HTML")
    await call.answer()

@dp.message(AdminStates.waiting_for_broadcast)
async def admin_send_execute(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    
    photo_id = message.photo[-1].file_id if message.photo else None
    text = message.caption if photo_id else message.text
    
    if not text and not photo_id:
        await message.answer("⚠️ Повідомлення порожнє. Надішліть текст або картинку:")
        return

    await state.clear()
    await message.answer("⏳ Масова розсилка запущена, зачекайте...", reply_markup=get_admin_keyboard())
    
    conn = await asyncpg.connect(DB_URI)
    users = await conn.fetch("SELECT user_id FROM users")
    await conn.close()
    
    success = 0
    for row in users:
        try:
            if photo_id:
                await bot.send_photo(row['user_id'], photo_id, caption=text, parse_mode="HTML")
            else:
                await bot.send_message(row['user_id'], text, parse_mode="HTML")
            success += 1
            await asyncio.sleep(0.05)
        except: continue
        
    await message.answer(f"✅ <b>Розсилка завершена!</b>\n\nУспішно доставлено: <b>{success}</b> юзерам.", parse_mode="HTML")

# --- СИСТЕМА ШАБЛОНІВ ---
@dp.message(F.text == BTN_ADMIN_TEMPLATES)
async def admin_templates_menu(message: types.Message):
    if message.from_user.id not in ADMIN_IDS: return
    
    conn = await asyncpg.connect(DB_URI)
    templates = await conn.fetch("SELECT id, title FROM templates")
    await conn.close()
    
    inline_kb = []
    for row in templates:
        inline_kb.append([InlineKeyboardButton(text=f"📋 {row['title']}", callback_data=f"tmpl_view_{row['id']}")])
    
    inline_kb.append([InlineKeyboardButton(text="➕ Створити новий шаблон", callback_data="tmpl_create")])
    markup = InlineKeyboardMarkup(inline_keyboard=inline_kb)
    await message.answer("📁 <b>Управління шаблонами розсилок:</b>", reply_markup=markup, parse_mode="HTML")

@dp.callback_query(F.data == "tmpl_create")
async def tmpl_create_start(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_template_name)
    await call.message.answer("📝 Введіть <b>коротку назву</b> для шаблону (для списку в меню):", parse_mode="HTML")
    await call.answer()

@dp.message(AdminStates.waiting_for_template_name)
async def tmpl_create_name(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    await state.update_data(tmpl_title=message.text.strip())
    await state.set_state(AdminStates.waiting_for_template_content)
    await message.answer("✏️ Тепер надішліть <b>вміст шаблону</b> (текст або foto з підписом):", parse_mode="HTML")

@dp.message(AdminStates.waiting_for_template_content)
async def tmpl_create_save(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    data = await state.get_data()
    title = data['tmpl_title']
    
    photo_id = message.photo[-1].file_id if message.photo else None
    text = message.caption if photo_id else message.text
    
    await state.clear()
    
    conn = await asyncpg.connect(DB_URI)
    await conn.execute("INSERT INTO templates (title, text, photo_id) VALUES ($1, $2, $3)", title, text, photo_id)
    await conn.close()
    
    await message.answer(f"✅ Шаблон <b>«{title}»</b> успешно збережено!", reply_markup=get_admin_keyboard(), parse_mode="HTML")

@dp.callback_query(F.data.startswith("tmpl_view_"))
async def tmpl_view(call: types.CallbackQuery):
    t_id = int(call.data.split("_")[2])
    conn = await asyncpg.connect(DB_URI)
    res = await conn.fetchrow("SELECT title, text, photo_id FROM templates WHERE id = $1", t_id)
    await conn.close()
    
    if not res: return
    
    inline_kb = [
        [InlineKeyboardButton(text="🚀 Запустити розсилку за цим шаблоном", callback_data=f"tmpl_send_{t_id}")],
        [InlineKeyboardButton(text="🗑 Видалити шаблон", callback_data=f"tmpl_del_{t_id}")]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=inline_kb)
    
    if res['photo_id']:
        await call.message.answer_photo(res['photo_id'], caption=f"📋 <b>Шаблон: {res['title']}</b>\n\n{res['text'] or ''}", reply_markup=markup, parse_mode="HTML")
    else:
        await call.message.answer(f"📋 <b>Шаблон: {res['title']}</b>\n\n<code>{res['text']}</code>", reply_markup=markup, parse_mode="HTML")
    await call.answer()

# ФІКС: Замінено помилковий message на call.message
@dp.callback_query(F.data.startswith("tmpl_send_"))
async def tmpl_send_execute(call: types.CallbackQuery):
    t_id = int(call.data.split("_")[2])
    conn = await asyncpg.connect(DB_URI)
    res = await conn.fetchrow("SELECT text, photo_id FROM templates WHERE id = $1", t_id)
    users = await conn.fetch("SELECT user_id FROM users")
    await conn.close()
    
    if not res: return
    
    await call.message.answer("⏳ Шаблонна розсилка запущена...")
    success = 0
    for row in users:
        try: 
            if res['photo_id']:
                await bot.send_photo(row['user_id'], res['photo_id'], caption=res['text'], parse_mode="HTML")
            else:
                await bot.send_message(row['user_id'], res['text'], parse_mode="HTML")
            success += 1
            await asyncio.sleep(0.05)
        except: continue
        
    await call.message.answer(f"✅ Успішно розіслано шаблон для <b>{success}</b> юзерів.", reply_markup=get_admin_keyboard(), parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data.startswith("tmpl_del_"))
async def tmpl_delete(call: types.CallbackQuery):
    t_id = int(call.data.split("_")[2])
    conn = await asyncpg.connect(DB_URI)
    await conn.execute("DELETE FROM templates WHERE id = $1", t_id)
    await conn.close()
    await call.message.answer("🗑 Шаблон успішно видалено.")
    await call.answer()

# --- ОБРОБКА ЮЗЕРСЬКИХ КНОПОК ---
@dp.message(F.text == BTN_BONUS)
async def bonus(message: types.Message):
    user_id = message.from_user.id
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ["left", "kicked"]:
            await message.answer(
                "❌ <b>ДОСТУП ОБМЕЖЕНО</b>\n\n"
                "Для активації особистого бонусу підпишись на наш офіційний канал:\n\n"
                f"👉 {TG_CHANNEL_LINK}\n\n"
                f"<i>Після підписки натисни кнопку '{BTN_BONUS}' ще раз!</i>",
                reply_markup=get_user_keyboard(),
                parse_mode="HTML"
            )
            return 
    except Exception as e: print(e)

    await set_blue_menu_button(user_id)
    await log_click(user_id, action_type="casino_click")
    
    await message.answer(
        "⚡ <b>Доступ активовано!</b>\n\n"
        "Натисни на синю кнопку <b>📱 НА САЙТ</b> внизу екрана (ліворуч від поля введення повідомлення), "
        "щоб відкрити швидку реєстрацію у First Casino прямо всередині Telegram! ▼",
        reply_markup=get_casino_inline(),
        parse_mode="HTML"
    )

@dp.message(F.text == BTN_INFO)
async def guide(message: types.Message):
    await message.answer(
        f"✦ <b>ІНСТРУКЦІЯ З АКТИВАЦІЇ БОНУСУ:</b>\n\n"
        f"1. Натискай синю кнопку <b>📱 НА САЙТ</b> ліворуч від поля введення.\n"
        f"2. У тебе прямо в Telegram відкриється сторінка First Casino.\n"
        f"3. Проходь швидку реєстрацію за 10 секунд.\n"
        f"4. Забирай свій вітальний бонус у розділі 'Бонуси'!", 
        parse_mode="HTML"
    )

@dp.message(F.text == BTN_MANAGER)
async def manager_request(message: types.Message):
    await message.answer(
        "👨‍💻 <b>Ви увійшли в чат з менеджером</b>\n\n"
        "Напишіть ваше питання одним повідомленням нижче ▼\n"
        "<i>Наш менеджер відповість вам прямо тут у найкоротший час.</i>", 
        parse_mode="HTML"
    )

# --- ПЕРЕСИЛКА ПИТАНЬ ДО АДМІНА ---
@dp.message(F.chat.type == "private", lambda msg: msg.from_user.id not in ADMIN_IDS and msg.text not in MENU_BUTTONS_USER and not msg.text.startswith("/"))
async def forward_to_admin(message: types.Message):
    for admin_id in ADMIN_IDS:
        try: 
            await bot.send_message(
                admin_id, 
                f"📩 <b>НОВЕ ПИТАННЯ:</b>\nID: <code>{message.from_user.id}</code>\n"
                f"Від: @{message.from_user.username or 'NoUser'}\n\n"
                f"Текст: {message.text}", 
                parse_mode="HTML"
            )
        except: continue
    await asyncio.sleep(1)
    await message.answer(f"👨‍💻 Менеджер <b>{random.choice(MANAGER_NAMES)}</b> вивчає ваше питання. Зачекайте відповіді прямо тут.", parse_mode="HTML")

# --- КОМАНДА СТАРТ ---
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id, username, first_name = message.from_user.id, message.from_user.username, message.from_user.first_name
    
    conn = await asyncpg.connect(DB_URI)
    await conn.execute("""
        INSERT INTO users (user_id, username, first_name) 
        VALUES ($1, $2, $3) 
        ON CONFLICT (user_id) DO NOTHING
    """, user_id, username, first_name)
    await conn.close()
    
    await set_blue_menu_button(user_id)
    
    await message.answer(
        f"👋 Привіт, <b>{first_name}</b>!\n\n"
        f"Твій особистий кабінет First Casino активовано за Telegram ID.\n\n"
        f"Для швидкого переходу до реєстрації натискай синю кнопку <b>📱 НА САЙТ</b> внизу екрана ліворуч! 👇", 
        reply_markup=get_user_keyboard(), 
        parse_mode="HTML"
    )

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await init_db()
    await set_bot_description()
    print("🚀 Бот онлайн (Supabase Хмара)!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())