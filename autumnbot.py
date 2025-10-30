
import telebot
import telebot.types
from telebot import types
import json
from datetime import *
from gspread import Client, Spreadsheet, Worksheet, service_account
import psycopg2
from psycopg2.extras import Json
from time import perf_counter
import re
from secretdata import get_tokens, get_conn_data

tokens = get_tokens()
old_token = tokens[0]
new_token = tokens[2]
conn_data = get_conn_data()
bot = telebot.TeleBot(new_token)
conn = psycopg2.connect(**conn_data)
cur = conn.cursor()
try:
    cur.execute("SELECT * from shusers")
    frdb = cur.fetchall()
except:
    cur.close()
    conn.close()
    conn = psycopg2.connect(**conn_data)
    cur = conn.cursor()
    cur.execute("CREATE TABLE shusers(id INTEGER PRIMARY KEY,reg BOOLEAN,login CHARACTER VARYING(100),gender CHARACTER(1),data JSON, summary INTEGER,percents NUMERIC,maxes JSON,month BOOLEAN)")
    cur.close()
    conn.close()
    conn = psycopg2.connect(**conn_data)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO shusers VALUES (813662308, True,'Тестовый0000','М','[]',0,0,'['01.03',0]',False)")
    cur.execute("SELECT * from shusers")
    frdb = cur.fetchall()
cur.close()
conn.close()
users = []
info = {}  # данные при регистрации
data = {}  # данные которые заносят пользователи
idlogins = {}  # айдишники к логинам
summary = {}
percents = {}
maxes = {}
month = []
distances = {}
for i in frdb:
    users.append(str(i[0]))
    info[str(i[0])] = [i[1], i[7]]
    data[str(i[0])] = i[2]
    idlogins[i[0]] = i[1]
    summary[str(i[0])] = int(i[3])
    percents[str(i[0])] = float(i[4])
    maxes[str(i[0])] = i[5]
    if i[6]:
        month.append(str(i[0]))
    distances[str(i[0])] = i[7]
otveti = {}
end_date = date(2025, 11, 30)
dt = [1000000, 777777]
admins = [813662308, 335152794]
logins = {}
for key, value in idlogins.items():
    logins[value] = key
indexes = {}  # хранится куррент дата для сохранения данных, на название не смотрите
notmax = []
if len(summary.items()) < 10:
    summarytop = []  # топ по сумме
    for key, value in sorted(summary.items(), key=lambda x: int(x[1]), reverse=True):
        summarytop.append(f'{idlogins[int(key)]} - {value} шагов')
else:
    summarytop = []
    for key, value in sorted(summary.items(), key=lambda x: int(x[1]), reverse=True)[:11]:
        summarytop.append(f'{idlogins[int(key)]} - {value} шагов')
if len(maxes.items()) < 10:
    maxestop = []  # топ по максимуму за раз
    for key, value in sorted(maxes.items(), key=lambda x: int(x[1][1]), reverse=True):
        if key not in month:
            maxestop.append(f'{idlogins[int(key)]} - {value[1]} шагов')
else:
    maxestop = []
    for key, value in sorted(maxes.items(), key=lambda x: int(x[1][1]), reverse=True):
        if len(maxestop) < 10:
            if key not in month:
                maxestop.append(f'{idlogins[int(key)]} - {value[1]} шагов')
        else:
            break


@bot.message_handler(commands=['start', 'menu'])
def main(message):
    if str(message.chat.id) not in users:
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton(
            text='Зарегистрироваться', callback_data='reg'))
        bot.send_message(
            message.chat.id, 'Осень\n\nДистанция: 1 000 000 или 777 777 шагов \n\nОписание: за период с 1 сентября по 30 ноября (включительно) нашагай суммарно 1 000 000 шагов (чуть больше 10 тысяч шагов в день) или 777 777 шагов, в зависимости от выбранной цели. Учет любым шагомером телефона или часов и в данном боте.\nНе забудь вступить в мероприятие в стаффе для получения ачивки. (https://staff.skbkontur.ru/group/33876).\nАдмин челленджа @vyazayajuli', reply_markup=mk)
    else:
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton(
            text='Занести данные за день', callback_data='data'))
        mk.add(types.InlineKeyboardButton(
            text='Занести за месяц', callback_data='month_goal'))
        mk.add(types.InlineKeyboardButton(
            text='Топ по сумме', callback_data='summarytop'))
        mk.add(types.InlineKeyboardButton(
            text='Топ за день', callback_data='maxestop'))
        mk.add(types.InlineKeyboardButton(
            text='Ваши логин и цель', callback_data='data_now'))
        if str(message.chat.id) in summary:
            mk.add(types.InlineKeyboardButton(
                text='Внесенные данные по шагам', callback_data='steps_for_date'))
        mk.add(types.InlineKeyboardButton(
            text='Сообщение в поддержку бота', callback_data='help'))
        if str(message.chat.id) in summary:
            tdy = date.today()
            ost = end_date-tdy
            goal = (distances[str(message.chat.id)] -
                    summary[str(message.chat.id)])//(ost.days+1)
            if goal < 0:
                goal = 0
            bot.send_message(
                message.chat.id, f'Ваш прогресс составляет: {percents[str(message.chat.id)]}%\n\n{summary[str(message.chat.id)]} шагов из {distances[str(message.chat.id)]} шагов\n\nНеобходимо шагов в день:{goal}', reply_markup=mk)
        else:
            bot.send_message(
                message.chat.id, 'Для занесения данных нажмите на кнопку занести данные', reply_markup=mk)


@bot.message_handler(commands=['backup'])
def backup(message):
    if message.chat.id in admins:
        bot.send_message(message.chat.id, 'users:\n'+json.dumps(users))
        bot.send_message(message.chat.id, 'info:\n'+json.dumps(info))
        bot.send_message(message.chat.id, 'data:\n'+json.dumps(data))
        bot.send_message(message.chat.id, 'logins:\n'+json.dumps(logins))
        bot.send_message(message.chat.id, 'summary:\n'+json.dumps(summary))
        bot.send_message(message.chat.id, 'percents:\n'+json.dumps(percents))
        bot.send_message(message.chat.id, 'maxes:\n'+json.dumps(maxes))
        bot.send_message(message.chat.id, 'month:\n'+json.dumps(month))
    else:
        bot.send_message(message.chat.id, 'Вы не являетесь администратором!')


@bot.message_handler(commands=['info'])
def information(message):
    if message.chat.id in admins:
        bot.send_message(
            message.chat.id, 'Отправьте логин пользователя информацию по которому желаете посмотреть(логин нужно отправлять также как вводил его пользователь!)')
        bot.register_next_step_handler(message, logintoinfo)
    else:
        bot.send_message('Вы не являетесь администратором')


def logintoinfo(message):
    login = message.text
    if login.lower() in [i.lower() for i in logins]:
        user_id = logins[login]
        out = f'Текущие данные пользователя:\nЛогин:{info[str(message.chat.id)][0]}\nДистанция:{info[str(message.chat.id)][1]}\n\nВнесенные данные по шагам пользователя:'
        ditems = list(data[str(user_id)].items())
        dmonths = []
        for i in ditems:
            if i[0] in ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь',]:
                del ditems[ditems.index(i)]
                dmonths.append(i)
        listdates = sorted(ditems, key=lambda x: (
            int(x[0][3:]), int(x[0][0:2])))
        listdates = dmonths + listdates
        for i in listdates:
            if int(i[1]) != 0:
                out += f'\n*{i[0]}*: {i[1]}'
        bot.send_message(message.chat.id, out, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, 'Логин не найден!')


@bot.callback_query_handler(lambda call: True)
def callback(call):
    global maxestop
    if call.data == 'reg':  # занос фио
        bot.send_message(
            call.message.chat.id, 'Введите логин: (любые буквы и цифры без специальных символов) до 99 символов , пример: Разработчик, Тестовый0000, TestТест')
        bot.register_next_step_handler(call.message, login)
    elif call.data == 'data':
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton('Отмена', callback_data='cancel'))
        bot.send_message(call.message.chat.id,
                         'Внесите дату в формате дд.мм, например 13 сентября будет 13.09', reply_markup=mk)
        bot.register_next_step_handler(call.message, get_date)
    elif call.data == 'help':
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton('Отмена', callback_data='cancel'))
        bot.send_message(call.message.chat.id,
                         'Отправьте свое сообщение в поддержку бота(поддержка в боте принимает только текст, если вы хотите отправить скриншот проблемы пишите @HedgehogOld )', reply_markup=mk)
        bot.register_next_step_handler(call.message, help)
    elif call.data == 'summarytop':
        strr = ''
        for i in summarytop:
            strr += i
            strr += '\n'
        bot.send_message(call.message.chat.id, f'Топ по сумме:\n{strr}')
    elif call.data == 'maxestop':
        strr = ''
        for i in maxestop:
            strr += i
            strr += '\n'
        bot.send_message(call.message.chat.id, f'Топ за день:\n{strr}')
    elif call.data == 'change_data':
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton(
            'Cменить логин', callback_data='change_login'))
        mk.add(types.InlineKeyboardButton(
            'Назад', callback_data='cancel'))
        bot.send_message(
            call.message.chat.id, f'Ваши текущие данные:\nЛогин:{info[str(call.message.chat.id)][0]}\nДистанция:{info[str(call.message.chat.id)][1]}', reply_markup=mk)
    elif call.data == 'data_now':
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton(
            'Назад', callback_data='cancel'))
        bot.send_message(
            call.message.chat.id, f'Ваши текущие данные:\nЛогин:{info[str(call.message.chat.id)][0]}\nДистанция:{info[str(call.message.chat.id)][1]}', reply_markup=mk)
    elif call.data == 'change_login':
        bot.send_message(call.message.chat.id, 'Отправьте новый логин:')
        bot.register_next_step_handler(call.message, change_login)
    elif call.data == 'steps_for_date':
        ditems = list(data[str(call.message.chat.id)].items())
        dmonths = []
        for i in ditems:
            if i[0] in ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь',]:
                del ditems[ditems.index(i)]
                dmonths.append(i)
        print(ditems)
        listdates = sorted(ditems, key=lambda x: (
            int(x[0][3:]), int(x[0][0:2])))
        listdates = dmonths + listdates
        out = 'Внесенные данные по шагам:'
        for i in listdates:
            if int(i[1]) != 0:
                out += f'\n\n*{i[0]}*: {i[1]}'
        bot.send_message(call.message.chat.id, out, parse_mode='Markdown')
    elif 'otvet' in call.data:
        uid = int(call.data[5:])
        otveti[call.message.chat.id] = uid
        bot.send_message(call.message.chat.id, 'Введите ответ на сообщение:')
        bot.register_next_step_handler(call.message, otvet)
    elif call.data == 'month_goal':
        mk = types.InlineKeyboardMarkup()
        if date(2025, 9, 30) >= date(2025, 9, 30):
            mk.add(types.InlineKeyboardButton(
                'Сентябрь', callback_data='mto09'))
        if date.today() >= date(2025, 10, 31):
            mk.add(types.InlineKeyboardButton(
                'Октябрь', callback_data='mto10'))
        if date.today() >= date(2025, 11, 30):
            mk.add(types.InlineKeyboardButton('Ноябрь', callback_data='mto11'))
        mk.add(types.InlineKeyboardButton('Назад', callback_data='cancel'))
        bot.send_message(
            call.message.chat.id, 'Выберите месяц за который хотите внести(вносить за месяц можно только когда он закончится):', reply_markup=mk)
    elif call.data[:3] == 'mto':
        mnth = call.data[3:]
        if mnth == '09':
            mnt = 'Сентябрь'
        elif mnth == '10':
            mnt = 'Октябрь'
        elif mnth == '11':
            mnt = 'Ноябрь'
        hitrost = False
        hitrostm = ''
        if mnt == 'Сентябрь':
            for i in data[str(call.message.chat.id)]:
                print(i[3:])
                if i[3:] == '09':
                    if data[str(call.message.chat.id)][i] != 0:
                        hitrost = True
                        hitrostm = 'Сентябрь'
                        break
        elif mnt == 'Октябрь':
            for i in data[str(call.message.chat.id)]:
                if i[3:] == '10':
                    if data[str(call.message.chat.id)][i] != 0:
                        hitrost = True
                        hitrostm = 'Октябрь'
                        break
        elif mnt == 'Ноябрь':
            for i in data[str(call.message.chat.id)]:
                if i[3:] == '11':
                    if data[str(call.message.chat.id)][i] != 0:
                        hitrost = True
                        hitrostm = 'Ноябрь'
                        break
        if not hitrost:
            indexes[str(call.message.chat.id)] = mnt
            notmax.append(str(call.message.chat.id))
            mk = types.InlineKeyboardMarkup()
            mk.add(types.InlineKeyboardButton('Назад', callback_data='cancel'))
            bot.send_message(
                call.message.chat.id, 'Отправьте целое число - количество шагов:', reply_markup=mk)
            bot.register_next_step_handler(call.message, get_data)
        else:
            mk = types.InlineKeyboardMarkup()
            mk.add(types.InlineKeyboardButton(
                'Вернуться в основное меню', callback_data='cancel'))
            bot.send_message(
                call.message.chat.id, f'Вы уже вносили данные  за {hitrostm} по дням(как минимум один день), пожалуйста, либо скорректируйте данные либо внесите шаги за другой месяц', reply_markup=mk)
    elif call.data[:2] == 'dt':
        distances[str(call.message.chat.id)] = int(call.data[2:])
        info[str(call.message.chat.id)].append(int(call.data[2:]))
        users.append(str(call.message.chat.id))
        data[str(call.message.chat.id)] = {}
        summary[str(call.message.chat.id)] = 0
        percents[str(call.message.chat.id)] = 0
        maxes[str(call.message.chat.id)] = ['01.09', 0]
        print(info)
        print(users)
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton(
            text='Занести данные за день', callback_data='data'))
        mk.add(types.InlineKeyboardButton(
            text='Занести за месяц', callback_data='month_goal'))
        mk.add(types.InlineKeyboardButton(
            text='Топ по сумме', callback_data='summarytop'))
        mk.add(types.InlineKeyboardButton(
            text='Топ за день', callback_data='maxestop'))
        mk.add(types.InlineKeyboardButton(
            text='Ваши логин и цель', callback_data='data_now'))
        mk.add(types.InlineKeyboardButton(
            text='Сменить данные', callback_data='change_data'))
        mk.add(types.InlineKeyboardButton(
            text='Сообщение в поддержку бота', callback_data='help'))
        for key, value in logins.items():
            idlogins[value] = key
        save(str(call.message.chat.id))
        bot.send_message(
            call.message.chat.id, 'Поздравляю, Вы зарегистрированы!\nТеперь вы можете вносить данные.', reply_markup=mk)
    elif call.data == 'cancel':
        main(call.message)


def help(message):
    try:
        uz = message.from_user.username
    except:
        uz = 'нету'
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton(
        'Ответить', callback_data='otvet'+str(message.chat.id)))
    bot.send_message(
        813662308, f'Новое сообщение в поддержку:\nПользователь: @{uz}\nСообщение: {message.text}', reply_markup=mk)
    bot.send_message(message.chat.id, 'Сообщение успешно отправлено!')


def otvet(message):
    uid = otveti[message.chat.id]
    bot.send_message(
        uid, f'Ответ на ваше сообщение в поддержку:\n{message.text}')
    bot.send_message(message.chat.id, 'Ответ успешно отправлен!')


# занос логина, обработка фио


'''
def name(message):
    info[str(message.chat.id)] = []
    info[str(message.chat.id)].append(message.text)
    bot.send_message(
        message.chat.id, 'Введите логин в соответствии с форматом ФамилияЕфон, пример: Иванов9876:')
    bot.register_next_step_handler(message, login)
'''
# занос пола, обработка логина


def login(message):
    regex = r'[а-яА-Я0-9a-zA-Z]+'
    out = re.match(regex, message.text)
    if out:
        conn = psycopg2.connect(**conn_data)
        cur = conn.cursor()
        cur.execute("SELECT login from shusers")
        temp_all_logins = cur.fetchall()
        all_logins = []
        for i in temp_all_logins:
            all_logins.append(i[0])
        print(all_logins)
        cur.close()
        conn.close()
        if message.text not in all_logins:
            info[str(message.chat.id)] = [message.text]
            logins[message.text] = message.chat.id
            mk = types.InlineKeyboardMarkup()
            for i in dt:
                mk.add(types.InlineKeyboardButton(
                    str(i), callback_data='dt'+str(i)))
            bot.send_message(
                message.chat.id, 'Выберите дистанцию:', reply_markup=mk)
        else:
            bot.send_message(
                message.chat.id, 'Попробуйте ещё раз, такой логин уже занят, также измените логин в анкете мероприятия в стаффе https://staff.skbkontur.ru/group/33876')
            bot.register_next_step_handler(message, login)
    else:
        bot.send_message(
            message.chat.id, 'Попробуйте ещё раз, логин не соответствует формату:')
        bot.register_next_step_handler(message, login)

# обработка логина


# получение даты заноса


def get_date(message):
    date = False
    hitrost = False
    if message.text[0:2].isdigit() and message.text[3:].isdigit() and message.text[2] == '.' and 1 <= int(message.text[0:2]) <= 31 and 1 <= int(message.text[3:]) <= 12:
        if message.text[3:] in ['09', '10', '11']:
            if message.text[3:] == '09' and 'Сентябрь' in list(data[str(message.chat.id)].keys()):
                if data[str(message.chat.id)]['Сентябрь'] != 0:
                    hitrost = True
                    hitrostm = 'Сентябрь'
            elif message.text[3:] == '10' and 'Октябрь' in list(data[str(message.chat.id)].keys()):
                if data[str(message.chat.id)]['Октябрь'] != 0:
                    hitrost = True
                    hitrostm = 'Октябрь'
            elif message.text[3:] == '11' and 'Ноябрь' in list(data[str(message.chat.id)].keys()):
                if data[str(message.chat.id)]['Ноябрь'] != 0:
                    hitrost = True
                    hitrostm = 'Ноябрь'
            if not hitrost:
                febr = False
                date = True
                if message.text[3:] == '02':
                    febr = True
                if febr:
                    if 1 <= int(message.text[0:2]) <= 28:
                        date = True
                    else:
                        date = False
        if date and not hitrost:
            indexes[str(message.chat.id)] = message.text
            if str(message.chat.id) in notmax:
                del notmax[notmax.index(str(message.chat.id))]
            mk = types.InlineKeyboardMarkup()
            mk.add(types.InlineKeyboardButton(
                'Отмена', callback_data='cancel'))
            bot.send_message(
                message.chat.id, 'Отправьте целое число - количество шагов:', reply_markup=mk)
            bot.register_next_step_handler(message, get_data)
        else:
            if hitrost:
                mk = types.InlineKeyboardMarkup()
                mk.add(types.InlineKeyboardButton(
                    'Отмена', callback_data='cancel'))
                bot.send_message(
                    message.chat.id, f'Вы уже вносили данные за {hitrostm}, пожалуйста либо откорректируйте данные, либо внесите данные за день другого месяца', reply_markup=mk)
                bot.register_next_step_handler(message, get_date)
            else:
                mk = types.InlineKeyboardMarkup()
                mk.add(types.InlineKeyboardButton(
                    'Отмена', callback_data='cancel'))
                bot.send_message(
                    message.chat.id, 'Попробуйте ещё раз, число не соответствует датам челленджа', reply_markup=mk)
                bot.register_next_step_handler(message, get_date)
    else:
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton('Отмена', callback_data='cancel'))
        bot.send_message(
            message.chat.id, 'Попробуйте ещё раз, число не соответствует формату дд.мм', reply_markup=mk)
        bot.register_next_step_handler(message, get_date)

# получение ко-лва шагов


def get_data(message):
    global summarytop
    global maxestop
    try:
        kolvo = int(message.text)
        yes = True
    except:
        bot.send_message(
            message.chat.id, 'Вы отправили не число, попробуйте ещё раз')
        bot.register_next_step_handler(message, get_data)
        yes = False
    if yes:
        index = indexes[str(message.chat.id)]
        data[str(message.chat.id)][index] = kolvo
        distance = distances[str(message.chat.id)]
        summary[str(message.chat.id)] = sum(
            data[str(message.chat.id)].values())
        percent = round(summary[str(message.chat.id)]/distance*100, 2)
        percents[str(message.chat.id)] = percent
        if str(message.chat.id) not in notmax:
            if str(message.chat.id) in maxes:
                if kolvo > maxes[str(message.chat.id)][1]:
                    maxes[str(message.chat.id)] = [index, kolvo]
                if index == maxes[str(message.chat.id)][0]:
                    maxes[str(message.chat.id)] = [index, kolvo]
            else:
                maxes[str(message.chat.id)] = [index, kolvo]
        if len(summary.items()) < 10:
            summarytop = []
            for key, value in sorted(summary.items(), key=lambda x: int(x[1]), reverse=True):

                summarytop.append(f'{idlogins[int(key)]} - {value} шагов')
        else:
            summarytop = []
            for key, value in sorted(summary.items(), key=lambda x: int(x[1]), reverse=True)[:11]:
                summarytop.append(f'{idlogins[int(key)]} - {value} шагов')
        if len(maxes.items()) < 10:
            maxestop = []
            for key, value in sorted(maxes.items(), key=lambda x: int(x[1][1]), reverse=True):
                if key not in month:
                    maxestop.append(f'{idlogins[int(key)]} - {value[1]} шагов')
        else:
            maxestop = []
            for key, value in sorted(maxes.items(), key=lambda x: int(x[1][1]), reverse=True)[:11]:
                if len(maxestop) < 10:
                    if key not in month:
                        maxestop.append(
                            f'{idlogins[int(key)]} - {value[1]} шагов')
                else:
                    break
        save(str(message.chat.id))
        if str(message.chat.id) in notmax:
            del notmax[notmax.index(str(message.chat.id))]
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton(
            text='Занести данные за день', callback_data='data'))
        mk.add(types.InlineKeyboardButton(
            text='Занести за месяц', callback_data='month_goal'))
        mk.add(types.InlineKeyboardButton(
            text='Топ по сумме', callback_data='summarytop'))
        mk.add(types.InlineKeyboardButton(
            text='Топ за день', callback_data='maxestop'))
        mk.add(types.InlineKeyboardButton(
            text='Ваши логин и цель', callback_data='data_now'))
        mk.add(types.InlineKeyboardButton(
            text='Внесенные данные по шагам', callback_data='steps_for_date'))
        mk.add(types.InlineKeyboardButton(
            text='Сообщение в поддержку бота', callback_data='help'))
        tdy = date.today()
        ost = end_date-tdy
        goal = (distances[str(message.chat.id)] -
                summary[str(message.chat.id)])//(ost.days+1)
        if goal < 0:
            goal = 0
        bot.send_message(
            message.chat.id, f'Вы занесли данные!\nЕсли вы допустили опечатку в данных - подайте данные за день или месяц еще раз, они перезапишутся.\nВаш прогресс составляет: {percents[str(message.chat.id)]}%\n\n{summary[str(message.chat.id)]} шагов из {distances[str(message.chat.id)]} шагов\n\nНеобходимо шагов в день:{goal}', reply_markup=mk)

# сохранение всех файлов


def save(aidi):
    conn = psycopg2.connect(**conn_data)
    cur = conn.cursor()
    cur.execute("SELECT id from shusers")
    all_id = cur.fetchall()
    all_id = [int(i[0]) for i in all_id]
    print(all_id)
    cur.close()
    conn.close()
    start = perf_counter()
    conn = psycopg2.connect(**conn_data)
    cur = conn.cursor()
    i = aidi
    idd = int(i)
    mnt = i in month
    if idd in all_id:
        print(1)
        out = [Json(data[i]), summary[i], Json(maxes[i]),
               percents[i], mnt, idlogins[idd]]
        cur.execute(
            f'UPDATE shusers SET data=%s, summary=%s, maxes=%s, percents = %s, month=%s, login = %s WHERE id = %s', (*out, idd))
    else:
        print(2)
        out = [idd, idlogins[idd], Json(data[i]), summary[i], percents[i], Json(
            maxes[i]), mnt, distances[i]]
        cur.execute(
            f'INSERT INTO shusers VALUES (%s,%s,%s,%s,%s,%s,%s,%s)', out)
    conn.commit()
    conn.close()
    end = perf_counter()
    print(end-start)
# изменение логина


def change_login(message):
    global logins
    global idlogins
    regex = r'[а-яА-Я0-9a-zA-Z]+'
    out = re.match(regex, message.text)
    if out:
        info[str(message.chat.id)][0] = message.text
        idlogins[message.chat.id] = message.text
        logins = {}
        for key, value in idlogins.items():
            logins[value] = key
        save(str(message.chat.id))
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton('В меню', callback_data='cancel'))
        bot.send_message(
            message.chat.id, f'Логин успешно изменен!\nТеперь ваш логин: {info[str(message.chat.id)][0]}', reply_markup=mk)
    else:
        bot.send_message(
            message.chat.id, 'Попробуйте ещё раз, логин не соответствует формату:')
        bot.register_next_step_handler(message, change_login)


admins = [813662308, 335152794]


@bot.message_handler(commands=['data'])
def get_all_data(message):
    if message.chat.id in admins:
        dt = data.values()
        ml = 0
        dtv = {}
        for i in dt:
            dtv = dtv | i
        print(dtv)
        print('test1')
        dtvkeys = list(dtv.keys())
        dtmonths = []
        for i in dtvkeys:
            if i in ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь',]:
                del dtvkeys[dtvkeys.index(i)]
                dtmonths.append(i)
        dtv = sorted(dtvkeys, key=lambda x: (int(x[3:]), int(x[:2])))
        dtv = dtmonths+dtv
        print(dtv)
        client = client_init_json()
        table = get_table_by_url(client,
                                 'https://docs.google.com/spreadsheets/d/10TPKbnAEdbhzQS4GvaBegrD_m1TA5-qJsh_T4z95VB0')
        table.worksheet('Данные').delete_rows(1, len(users)+2)
        users_list = []
        for i in users:
            if data[i] != {}:
                user_list = []
                user_list.append(idlogins[int(i)])
                user_list.append(info[i][1])
                user_list.append(summary[i])
                user_dates = ['' for i in range(len(dtv))]
                print(user_dates)

                print('yes2')
                for key, value in data[i].items():
                    user_dates[dtv.index(key)] = value
                user_list += user_dates
                users_list.append(user_list)
        print('yes')
        # for i in sorted(users_list,key=lambda x: x[0],reverse=True):
        table.worksheet('Данные').insert_rows(
            sorted(users_list, key=lambda x: x[0]), row=1)
        print('yes3')
        insert_one(table=table,
                   title='Данные',
                   data=['Логин', 'Дистанция', 'Общее количество шагов'] + dtv)
        bot.send_message(
            message.chat.id, 'https://docs.google.com/spreadsheets/d/10TPKbnAEdbhzQS4GvaBegrD_m1TA5-qJsh_T4z95VB0 Ссылка на таблицу для просмотра')


def client_init_json() -> Client:
    """Создание клиента для работы с Google Sheets."""
    return service_account(filename='table-project-oldhedgehog-0ea3f168cce2.json')


def get_table_by_url(client: Client, table_url):
    """Получение таблицы из Google Sheets по ссылке."""
    return client.open_by_url(table_url)


def get_worksheet_info(table: Spreadsheet) -> dict:
    """Возвращает количество листов в таблице и их названия."""
    worksheets = table.worksheets()
    worksheet_info = {
        "count": len(worksheets),
        "names": [worksheet.title for worksheet in worksheets]
    }
    return worksheet_info


def insert_one(table: Spreadsheet, title: str, data: list, index: int = 1):
    """Вставка данных в лист."""
    worksheet = table.worksheet(title)
    # worksheet.delete_rows(1,1000)
    worksheet.insert_row(data, index=index)


def test_add_data():
    """Тестирование добавления данных в таблицу."""
    client = client_init_json()
    table = get_table_by_url(
        client, 'https://docs.google.com/spreadsheets/d/10TPKbnAEdbhzQS4GvaBegrD_m1TA5-qJsh_T4z95VB0')


@bot.message_handler(commands=['addstepsfordates'])
def addsteps1(message):
    bot.send_message(
        message.chat.id, 'Занесите данные в формате:\nдд.мм,дд.мм;кол-во шагов,кол-во шагов\nКоличество пар: дат и кол-ва шагов - не ограничено')
    bot.register_next_step_handler(message, addsteps2)


def addsteps2(message):
    global summarytop
    global maxestop
    global maxes
    global summary
    inp = message.text
    try:
        sp_inp = inp.split(';')
        datess = sp_inp[0]
        shags = sp_inp[1]
        datess = datess.split(',')
        shags = shags.split(',')
        yes2 = True
    except:
        yes2 = False
    if yes2:
        try:
            for i in range(len(datess)):
                yes = False
                try:
                    kolvo = int(shags[i])
                    datas = datess[i]
                    if datas[0:2].isdigit() and datas[3:].isdigit() and datas[2] == '.' and 1 <= int(datas[0:2]) <= 31 and 1 <= int(datas[3:]) <= 12:
                        if datas[3:] in ['09', '10', '11']:
                            febr = False
                            yes = True
                        if datas[3:] == '02':
                            febr = True
                        if febr:
                            if 1 <= int(datas[0:2]) <= 28:
                                yes = True
                            else:
                                yes = False

                except:
                    bot.send_message(
                        message.chat.id, 'Вы отправили не по формату или в ваших данных ошибка, попробуйте ещё раз')
                    bot.register_next_step_handler(message, addsteps2)
                    yes = False
                    break
                if yes:
                    index = datas
                    data[str(message.chat.id)][index] = kolvo
                    distance = distances[str(message.chat.id)]
                    summary[str(message.chat.id)] = sum(
                        data[str(message.chat.id)].values())
                    percent = round(
                        summary[str(message.chat.id)]/distance*100, 2)
                    percents[str(message.chat.id)] = percent
                    if str(message.chat.id) in maxes:
                        if kolvo > maxes[str(message.chat.id)][1]:
                            maxes[str(message.chat.id)] = [index, kolvo]
                        if index == maxes[str(message.chat.id)][0]:
                            maxes[str(message.chat.id)] = [index, kolvo]
                    else:
                        maxes[str(message.chat.id)] = [index, kolvo]
                else:
                    bot.send_message(
                        message.chat.id, 'Вы отправили не по формату или в ваших данных ошибка, попробуйте ещё раз')
                    bot.register_next_step_handler(message, addsteps2)
                    break
            if yes:
                if len(summary.items()) < 10:
                    summarytop = []
                    for key, value in sorted(summary.items(), key=lambda x: int(x[1]), reverse=True):

                        summarytop.append(
                            f'{idlogins[int(key)]} - {value} шагов')
                else:
                    summarytop = []
                    for key, value in sorted(summary.items(), key=lambda x: int(x[1]), reverse=True)[:11]:
                        summarytop.append(
                            f'{idlogins[int(key)]} - {value} шагов')

                if len(maxes.items()) < 10:
                    maxestop = []
                    for key, value in sorted(maxes.items(), key=lambda x: int(x[1][1]), reverse=True):
                        if key not in month:
                            maxestop.append(
                                f'{idlogins[int(key)]} - {value[1]} шагов')
                else:
                    maxestop = []
                    for key, value in sorted(maxes.items(), key=lambda x: int(x[1][1]), reverse=True)[:11]:
                        if len(maxestop) < 10:
                            if key not in month:
                                maxestop.append(
                                    f'{idlogins[int(key)]} - {value[1]} шагов')
                        else:
                            break
                save(str(message.chat.id))

                mk = types.InlineKeyboardMarkup()
                mk.add(types.InlineKeyboardButton(
                    text='Занести данные за день', callback_data='data'))
                mk.add(types.InlineKeyboardButton(
                    text='Занести за месяц', callback_data='month_goal'))
                mk.add(types.InlineKeyboardButton(
                    text='Топ по сумме', callback_data='summarytop'))
                mk.add(types.InlineKeyboardButton(
                    text='Топ за день', callback_data='maxestop'))
                mk.add(types.InlineKeyboardButton(
                    text='Ваши логин и цель', callback_data='data_now'))
                mk.add(types.InlineKeyboardButton(
                    text='Внесенные данные по шагам', callback_data='steps_for_date'))
                mk.add(types.InlineKeyboardButton(
                    text='Сообщение в поддержку бота', callback_data='help'))
                tdy = date.today()
                ost = end_date-tdy
                goal = (distances[str(message.chat.id)] -
                        summary[str(message.chat.id)])//(ost.days+1)
                if goal < 0:
                    goal = 0
                bot.send_message(
                    message.chat.id, f'Вы занесли данные!\nВаш прогресс составляет: {percents[str(message.chat.id)]}%\n\n{summary[str(message.chat.id)]} шагов из {distances[str(message.chat.id)]} шагов\n\nНеобходимо шагов в день:{goal}', reply_markup=mk)
        except:
            bot.send_message(
                message.chat.id, 'Вы отправили не по формату или в ваших данных ошибка, попробуйте ещё раз')
            bot.register_next_step_handler(message, addsteps2)
    else:
        bot.send_message(
            message.chat.id, 'Вы отправили не по формату или в ваших данных ошибка, попробуйте ещё раз')
        bot.register_next_step_handler(message, addsteps2)


print(str(date.today()))
print('Бот запущен! Версия: 1.07 Осенний бот: ограничение занесения по месяцам')
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print('Поймалась ошибка!')
        print(e)
        print(type(e))
        now = date.today()
        f9 = open(f'bot\logs\logs_{now}.txt', 'a')
        f9.write(str(e)+'\n')
        f9.close()
