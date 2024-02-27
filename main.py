import telebot
from telebot import TeleBot, types
import sqlite3
import datetime
from datetime import datetime, timedelta
import requests
import wikipediaapi
import time

chats = [-1002019912722, -1001935476355]
bot = TeleBot('6623303214:AAEgqHq-iY6F1pfKnFLdrAhhO8BIpitDs2s')
print('[INFO] Telegram: Succesfully connected')

conn = sqlite3.connect('admins.db')
cur = conn.cursor()
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY,
        userid INTEGER UNIQUE
    )
"""
)
conn.commit()
conn.close()

print('[INFO] Sqlite3: DB operations completed')

def getuser(userid):
        try:
            a = bot.get_chat(userid)
        except Exception:
            return f'<a href="tg://user?id={userid}">Не удалось получить</>'
        
        if a.first_name != None:
            return f'<a href="tg://user?id={userid}">{a.first_name}</>'
        else:
            return f'<a href="tg://user?id={userid}">Не удалось получить</>'

def get_stats_string():
        con = sqlite3.connect('admins.db')
        cu = con.cursor()
        cu.execute('SELECT userid FROM admins')
        rows = cu.fetchall()
        stats_string = ""

        for row in rows:
            stats_string += f"{getuser({row[0]})}\n"
        return stats_string

class database:
    def __init__(self, user_id):
        self.user_id = user_id
    def addadmin(self):
        conn = sqlite3.connect('admins.db')
        cur = conn.cursor()
        cur.execute(f'SELECT userid FROM admins WHERE userid=?', (self.user_id,))
        result = cur.fetchone()
        if result and (result[0] != None):
            pass
        else:
            cur.execute(f'INSERT INTO admins (userid) VALUES (?)', (self.user_id,))
            conn.commit()
        conn.close()
    def deladmin(self):
        conn = sqlite3.connect('admins.db')
        cur = conn.cursor()
        cur.execute(f'SELECT userid FROM admins WHERE userid=?', (self.user_id,))
        result = cur.fetchone()
        if result and (result[0] != None):
            pass
        else:
            cur.execute(f'DELETE FROM admins WHERE userid=?', (self.user_id,))
            conn.commit()
    def check(self):
        conn = sqlite3.connect('admins.db')
        cur = conn.cursor()
        cur.execute(f'SELECT userid FROM admins WHERE userid=?', (self.user_id,))
        result = cur.fetchone()
        if result and (result[0] != None):
            return True
        else:
            return False
    

@bot.message_handler(commands=['start'])
def start(message):
    mention = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
    if message.chat.id == message.from_user.id:
        bot.send_message(
            message.chat.id,
            f'💞 <b>Доброго времени суток, {mention}!</>'
            '\n🤖 Я - помощник для чатов @fluoren'
            '\n❔ Мои админы:'
            f'\n{get_stats_string()}',
            parse_mode='html'
        )
        bot.send_sticker(
             message.chat.id,
             'CAACAgIAAxkBAAELAkllhDIB1VrnhBnCXM9SybZYtQZ0tAACBQADwDZPE_lqX5qCa011MwQ',
             reply_to_message_id=message.message_id
        )

@bot.message_handler(func=lambda message: message.text.lower().startswith('сап +админ '))
def admin(message):
    user_id = message.text.split()[2]
    if message.from_user.id == 5651166818:
            db = database(user_id)
            db.addadmin()
            bot.send_message(
                message.chat.id,
                f'🔮 {getuser(user_id)} теперь админ',
                parse_mode='html'
            )
    
@bot.message_handler(func=lambda message: message.text.lower().startswith('сап -админ '))
def unadmin(message):
    user_id = message.text.split()[2]
    if message.from_user.id == 5651166818:
            db = database(user_id)
            db.deladmin()
            bot.send_message(
                message.chat.id,
                f'⚠ {getuser(user_id)} больше не админ',
                parse_mode='html'
            )

    
@bot.message_handler(func=lambda message: message.text.lower().startswith('+бан'))
def ban(message):
    try:
        db = database(message.from_user.id)
        a = db.check()
        if a == True and message.reply_to_message:
            userid = message.reply_to_message.from_user.id
            mention = f'<a href="tg://user?id={userid}">{message.reply_to_message.from_user.first_name}</a>'
            admmention = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
            bot.ban_chat_member(
                message.chat.id,
                userid
            )
            bot.reply_to(
                message,
                f'🚪 <i>Пока-пока, {mention}!</> Заблокировал'
                f' участника по просьбе {admmention}',
                parse_mode='html'
            )
    except Exception as e:
        print(f'[ERROR] {e}')
        
@bot.message_handler(func=lambda message: message.text.lower().startswith('+кик'))
def kick(message):
    try:
        db = database(message.from_user.id)
        a = db.check()
        if a == True and message.reply_to_message:
            userid = message.reply_to_message.from_user.id
            mention = f'<a href="tg://user?id={userid}">{message.reply_to_message.from_user.first_name}</a>'
            admmention = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
            bot.ban_chat_member(
                message.chat.id,
                userid
            )
            bot.unban_chat_member(
                message.chat.id,
                userid
            )
            bot.reply_to(
                message,
                f'🚪 <i>Пока-пока, {mention}!</> Выгнал'
                f' участника по просьбе {admmention}',
                parse_mode='html'
            )
    except Exception as e:
        print(f'[ERROR] {e}')

@bot.message_handler(func=lambda message: message.text.lower().startswith('репорт'))
def report(message):
    if message.reply_to_message and message.chat.id != message.from_user.id:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(
            types.InlineKeyboardButton("✅ Разрешено", callback_data='clear'))
        ids2 = message.reply_to_message.from_user.id
        bot.send_message(
            chats[1],
            f'⚠ Новая жалоба на {getuser(ids2)} [<code>{ids2}</>]\n'
            f'От: {getuser(message.from_user.id)} [<code>{message.from_user.id}</>]\n'
            f'<a href="https://t.me/TheFireflyChat/{message.reply_to_message.message_id}">✉ Перейти</>',
            parse_mode='html',
            reply_markup=keyboard
        )
        bot.reply_to(
            message,
            '✅ Жалоба отправлена администрации'
        )
    elif not message.reply_to_message and message.chat.id != message.from_user.id:
        bot.reply_to(
            message,
            '❎ Жалоба должна быть ответом на сообщение'
        )

@bot.message_handler(func=lambda message: message.text.lower().startswith('+мут'))
def mute(message):
    try:
        db = database(message.from_user.id)
        a = db.check()
        if a == True and message.reply_to_message:
            userid = message.reply_to_message.from_user.id
            mention = f'<a href="tg://user?id={userid}">{message.reply_to_message.from_user.first_name}</a>'
            admmention = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
            hour = datetime.now() + timedelta(days=1)
            bot.restrict_chat_member(chat_id=message.chat.id,
                    user_id=userid,
                    can_send_messages=False,
                    can_send_media_messages=False,
                    until_date=hour.timestamp())
            bot.reply_to(
                message,
                f'❗ <i>Помолчи, {mention}!</> Обеззвучил'
                f' участника на сутки по просьбе {admmention}',
                parse_mode='html'
            )
    except Exception as e:
        print(f'[ERROR] {e}')

wiki_wiki = wikipediaapi.Wikipedia(
    language='ru',
    extract_format=wikipediaapi.ExtractFormat.WIKI,
    user_agent='wikipedia'
)

@bot.message_handler(func=lambda message: message.text.lower().startswith('вики '))
def wiki(message):
        query = message.text[5:].strip() 
        page = wiki_wiki.page(query)
        if page.exists():
            bot.send_chat_action(message.chat.id, 'typing')
            summary = page.summary[:1500]
            bot.reply_to(message, f'🔎 Результат по запросу <code>{query}</>:'
                        f'\n\n<i>{summary}</>',
                        parse_mode='html')
        else:
            bot.reply_to(message, "⚠ Не могу найти твой запрос")

@bot.message_handler(func=lambda message: message.text.lower().startswith('поиск '))
def google(message):
        q = message.text[6:].strip()
        if q:
            bot.send_chat_action(message.chat.id, 'typing')
            query = q.replace(" ", "+")
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text='Результаты', url=f'https://www.google.com/search?q={query}'))
            bot.reply_to(
                message,
                f'🔎 Поиск в Google по запросу <code>{q}</>:',
                reply_markup=markup,
                parse_mode='html'
            )

@bot.message_handler(func=lambda message: message.text.lower().startswith('словарь '))
def word(message):
        bot.send_chat_action(message.chat.id, 'typing')
        command_parts = message.text.split(' ')
        if len(command_parts) > 1:
            word = command_parts[1]
            response = requests.get(f'https://dictionary.yandex.net/api/v1/dicservice.json/lookup?key=dict.1.1.20240225T152855Z.23cbc4cec0e15ccd.837b2c0c98b01ac24455184eb72bdd77fa28d7ef&lang=ru-ru&text={word}')

            if response.status_code == 200:
                data = response.json()
                if 'def' in data and data['def']:
                    meanings = data['def'][0]['tr']
                    response_message = f"🔎 Значения <code>{word}</>:\n\n"
                    for index, meaning in enumerate(meanings, start=1):
                        if index <= 9:
                            response_message += f"{index}⃣ {meaning['text']}\n"
                    bot.send_message(message.chat.id, response_message,
                                    parse_mode='html')
                else:
                    bot.send_message(message.chat.id, f"⚠️ Не нашёл определение для <code>{word}</>",
                                    parse_mode='html')
            else:
                bot.send_message(message.chat.id, "⚠️ Произошла ошибка API. Попробуй позже")
        else:
            bot.send_message(message.chat.id, "❔ А что искать?")

@bot.message_handler(func=lambda message: message.text.lower().startswith('пинг'))
def ping(message):
            start_time = time.time()
            a = bot.send_message(message.chat.id, '🤖')
            end_time = time.time()

            ndelta = (end_time - start_time) * 1000 
            delta = round(ndelta, 3)
            bot.edit_message_text(f'✅ <b>ПОНГ!</> Ответ через: <code>{delta} мс</>',
                                chat_id=a.chat.id,
                                message_id=a.message_id,
                                parse_mode='html')

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'clear':
        bot.delete_message(
            message_id=call.message.message_id,
            chat_id=call.message.chat.id
        )

@bot.message_handler()
def leave(message):
    if message.chat.id in chats:
        pass
    else:
        bot.leave_chat(
            message.chat.id,
        )

bot.polling()
print('[INFO] Telegram: Connection closed')