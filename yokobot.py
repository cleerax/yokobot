import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import re
from prikol import schedule, updsch, even, weather
from datetime import datetime

def keyboard0():
    kb = VkKeyboard(one_time=True)
    kb.add_button("1 курс")
    kb.add_button("2 курс")
    kb.add_line
    kb.add_button("3 курс")
    kb.add_button("4 курс")
    return kb

def kboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("на сегодня", color=VkKeyboardColor.POSITIVE)
    keyboard.add_button("на завтра", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("на эту неделю", color=VkKeyboardColor.DEFAULT)
    keyboard.add_button("на следующую неделю", color=VkKeyboardColor.DEFAULT)
    keyboard.add_line()
    keyboard.add_button("какая неделя?")
    keyboard.add_button("какая группа?")
    keyboard.add_line()
    keyboard.add_button("Текущая погода в Москве", color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button("Сменить группу", color=VkKeyboardColor.NEGATIVE)
    return keyboard

def weekday(a):
    dayofw = ["пн", "вт", "ср", "чт", "пт", "сб"]
    b = datetime.today().weekday()
    if b != 6 and a == 0:
        return dayofw[b]
    elif a == 1 and b == 5:
        return dayofw[0]
    elif a == 1 and b != 6:
        return dayofw[b + 1]
    elif a == 1:
        return dayofw[0]
    else:
        return "вс"

def writing(sch, group, today, chet):
    if today == "вс":
        return "Выходной день пар нет иди баиньки"
    s = "\r\n"
    countall = 0

    for i in range(6):
        count = 0
        para = sch[group][today][chet][i]
        for j in para.keys():
            if para[j] == "":
                para[j] = '—'
                count += 1
        if count == 4:
            s += "{0}) —\r\n".format(i+1)
            countall += 1
        else:
            s += "{0}) {1}, {2}, {3}, {4}\r\n".format(i+1, para["subject"], para["type"], para["teacher"], para["kab"])
    if countall == 6:
        s = "Пар нет"
    return s

def writingweek(sch, group, a, chet):
    s = ""
    n = 0
    if a == 1:
        if chet == 0:
            chet = 1
        elif chet == 1:
            chet = 0
        
    for key in sch[group].keys():
        sp = ""
        countall = 0

        for i in range(6):
            count = 0
            para = sch[group][key][chet][i]
            for j in para.keys():
                if para[j] == "":
                    para[j] = '—'
                    count += 1
            if count == 4:
                sp += "{0}) —\r\n".format(i+1)
                countall += 1
            else:
                sp += "{0}) {1}, {2}, {3}, {4}\r\n".format(i+1, para["subject"], para["type"], para["teacher"], para["kab"])
        if countall == 6:
            sp = "Пар нет"

        arr = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
        s += "{0}\r\n{1}\r\n".format(arr[n], sp)
        n += 1
        
    return s

def main():
    circles = r'[ ]*[1-4][ ]?(?:[Кк][Уу][Рр][Сс])?'

    vk_session = vk_api.VkApi(token="06c2b7552d29c798a00b440e14e49bc89a7ef2e2557ceeabc479fad98c1ce0ffe65e90327a907681138f4")
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    today = weekday(0)
    chet = even(0)
    arr = {"понедельник" : "пн", "вторник" : "вт", "среда" : "ср", "четверг" : "чт", "пятница" : "пт", "суббота" : "сб"}
    groop = r"И[НАВКМАС]БО[П]?-[01][0-9]-[01][0-9]"
    yey = {"9" : 1, "8" : 2, "7" : 3, "6" : 4}

    c = {}
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text and not event.user_id in c.keys() \
        or event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text == "Сменить группу" and c[u] == 2:
            keyboard = keyboard0()
            u = event.user_id
            group = {u : ""}
            c = {u : 0}
            circle = {u : 0}
            vk.messages.send(
                user_id=event.user_id,
                random_id=get_random_id(),
                message="Выберите курс",
                keyboard = keyboard.get_keyboard()
            )
            c[u] += 1
        elif event.type == VkEventType.MESSAGE_NEW and event.to_me and not re.fullmatch(circles, event.text) and c[u] == 1:
            vk.messages.send(
                user_id=event.user_id,
                random_id=get_random_id(),
                message="Неверный курс",
                keyboard = keyboard.get_keyboard()
            )
            print(event.text)
        elif event.type == VkEventType.MESSAGE_NEW and event.to_me and re.fullmatch(circles, event.text) and c[u] == 1:
            circle[u] = int(event.text[0])
            vk.messages.send(
                user_id=event.user_id,
                random_id=get_random_id(),
                message="Выбран {0} курс".format(circle[u])
            )
            vk.messages.send(
                user_id=event.user_id,
                random_id=get_random_id(),
                message="Введите свою группу типа как \"ИЖБО-99-28\"",
            )
            c[u] += 1
            updsch(circle[u])
            sch = schedule()
        elif event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text.upper() not in sch.keys() and group[u] == "":
            vk.messages.send(
                user_id=event.user_id,
                random_id=get_random_id(),
                message="Введенной вами группы не найдено, повторите ввод"
            )
        elif event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text.upper() in sch.keys() and group[u] == "":
            group[u] = event.text.upper()
            temp = group[u]
            keyboard = kboard()
            if group[u][4] == 'П':
                temp = group[u]
                temp[4] = 'п'
            vk.messages.send(
                user_id=event.user_id,
                random_id=get_random_id(),
                message="Выбрана группа {0}".format(temp),
                keyboard=keyboard.get_keyboard()
            )
            vk.messages.send(
                user_id=event.user_id,
                random_id=get_random_id(),
                message="Доступные операции:\r\n\
Расписание на сегодня, на завтра, на эту неделю и на следующую неделю\r\n\
Узнать погоду короче да, а также комманды \"Бот *номер группы*\", которая поменяет выбранную группу \
и \"Бот *день недели* *номер группы*\", которая выведет расписание определенной группы в определенный день"
            )
        elif event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text.lower() == "на сегодня" and c[u] == 2:
            s = writing(sch, group[u], today, chet)
            vk.messages.send(
                user_id=event.user_id,
                random_id=get_random_id(),
                message="Расписание на сегодня:{0}".format(s)
            )
        elif event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text.lower() == "на завтра" and c[u] == 2:
            s = writing(sch, group[u], weekday(1), chet)
            vk.messages.send(
                user_id=event.user_id,
                random_id=get_random_id(),
                message="Расписание на завтра:{0}".format(s)
            )
        elif event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text.lower() == "на эту неделю" and c[u] == 2:
            s = writingweek(sch, group[u], 0, chet)
            vk.messages.send(
                user_id=event.user_id,
                random_id=get_random_id(),
                message="Расписание на эту неделю:\r\n{0}".format(s)
            )
        elif event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text.lower() == "на следующую неделю" and c[u] == 2:
            s = writingweek(sch, group[u], 1, chet)
            vk.messages.send(
                user_id=event.user_id,
                random_id=get_random_id(),
                message="Расписание на следующую неделю:\r\n{0}".format(s)
            )
        elif event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text.lower() == "текущая погода в москве" and c[u] == 2:
            vk.messages.send(
                user_id=event.user_id,
                random_id=get_random_id(),
                message=weather()
            )
        elif event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text.lower() == "какая группа?" and c[u] == 2:
            vk.messages.send(
                user_id=event.user_id,
                random_id=get_random_id(),
                message="Выбранная группа: {0}".format(group[u])
            )
        elif event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text.lower() == "какая неделя?" and c[u] == 2:
            vk.messages.send(
                user_id=event.user_id,
                random_id=get_random_id(),
                message="Сейчас идет {0} неделя".format(even(1))
            )
        elif event.type == VkEventType.MESSAGE_NEW and event.to_me and len(event.text.split(' ')) == 2 and \
            event.text.split(' ')[0].lower() == "бот" and re.fullmatch(groop, event.text.split(' ')[1].upper()) and c[u] == 2:
            temp = event.text.split(' ')[1].upper()
            if int(temp[-1]) in range(5, 9):
                temps = circle[u]
                circle[u] = yey[temp[-1]]
                updsch(circle[u])
                sch = schedule()
                if temp in sch.keys():
                    group[u] = event.text.split(' ')[1].upper()
                    temp = group[u]
                    if group[u][4] == 'П':
                        temp = group[u]
                        temp[4] = 'п' 
                    vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        message="Показать расписание группы {0}".format(temp)
                    )
                else:
                    vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        message="Данной группы не найдено на {0} курсе".format(circle[u])
                    )
                    circle[u] = temps
                    updsch(circle[u])
                    sch = schedule()
            else:
                vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        message="Группа введена некорректно"
                    )
        elif event.type == VkEventType.MESSAGE_NEW and event.to_me and len(event.text.split(' ')) == 3 and \
            event.text.split(' ')[0].lower() == "бот" and re.fullmatch(groop, event.text.split(' ')[2].upper()) and \
            event.text.split(' ')[1].lower() in arr.keys() and c[u] == 2:
            temp = event.text.split(' ')[2].upper()
            if int(temp[-1]) in range(5, 9):
                temps = circle[u]
                circle[u] = yey[temp[-1]]
                updsch(circle[u])
                sch = schedule()
                if temp in sch.keys():
                    tempg = group[u]
                    group[u] = event.text.split(' ')[2].upper()
                    temp = group[u]
                    s = "\r\n\r\nЧетная неделя:\r\n" + writing(sch, group[u], arr[event.text.split(' ')[1].lower()], 1)
                    s += "\r\nНечетная неделя:\r\n" + writing(sch, group[u], arr[event.text.split(' ')[1].lower()], 0)
                    if group[u][4] == 'П':
                        temp = group[u]
                        temp[4] = 'п' 
                    vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        message="Расписание группы {0} на {1}:{2}".format(temp, event.text.split(' ')[1].lower(), s)
                    )
                    group[u] = tempg
                    circle[u] = temps
                    updsch(circle[u])
                    sch = schedule()
                else:
                    vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        message="Данной группы не найдено на {0} курсе".format(circle[u])
                    )
                    circle[u] = temps
                    updsch(circle[u])
                    sch = schedule()
            else:
                vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        message="Группа введена некорректно"
                    )
        elif event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text and c[u] == 2:
            vk.messages.send(
                user_id=event.user_id,
                random_id=get_random_id(),
                message="Неизвестная команда"
            )

if __name__ == "__main__":
    main()