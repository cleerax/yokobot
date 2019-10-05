import requests
from bs4 import BeautifulSoup
import xlrd
import re

def updsch(c):
    page = requests.get("https://www.mirea.ru/education/schedule-main/schedule/")
    soup = BeautifulSoup(page.text, "html.parser")

    result = soup.find("div", {"id" : "toggle-3"}).findAll("a", {"class" : "xls"})

    for x in result:
        if "IIT" in str(x) and "{0}k".format(c) in str(x):
            f = open("file.xlsx", "wb")
            y = requests.get(x["href"])
            f.write(y.content)
            break

def weather():
    response = requests.get("http://api.openweathermap.org/data/2.5/weather?q=moscow,ru&appid=1189a50bf4f2e8b409f2a81836efaa51&units=metric&lang=ru")
    info = response.json()

    t = "{0}-{1}".format(info["main"]["temp_min"], info["main"]["temp_max"])
    pr = info["main"]["pressure"] * 0.75
    main = info["weather"][0]["main"]
    descr = info["weather"][0]["description"].capitalize()

    speed = float(info["wind"]["speed"])
    if speed < 0.3:
        windType = "штиль"
    elif speed < 1.6:
        windType = "тихий"
    elif speed < 3.4:
        windType = "легкий"
    elif speed < 5.5:
        windType = "слабый"
    elif speed < 8:
        windType = "умеренный"
    elif speed < 10.8:
        windType = "свежий"
    elif speed < 13.9:
        windType = "сильный"
    elif speed < 17.2:
        windType = "крепкий"
    elif speed < 20.8:
        windType = "очень крепкий"
    elif speed < 24.5:
        windType = "шторм"
    elif speed < 28.5:
        windType = "сильный шторм (буря)"
    elif speed < 32.7:
        windType = "жестокий шторм"
    else:
        windType = "ураган"

    if ("deg" in info["wind"]):
        deg = float(info["wind"]["deg"])
        if deg < 22.5 or deg >= 337.5 or deg <= 360:
            deg = "северный"
        elif deg >= 22.5 or deg < 67.5:
            deg = "северо-восточный"
        elif deg >= 67.5 or deg < 112.5:
            deg = "восточный"
        elif deg >= 112.5 or deg < 157.5:
            deg = "юго-восточный"
        elif deg >= 157.5 or deg < 202.5:
            deg = "южный"
        elif deg >= 202.5 or deg < 247.5:
            deg = "юго-западный"
        elif deg >= 247.5 or deg < 292.5:
            deg = "западный"
        elif deg >= 292.5 or deg < 337.5:
            deg = "северо-западный"
    else:
        deg = "направление неизвестно"

    s = "Погода в Москве: {0}\r\n{1}, температура: {2}°C\r\nДавление: {3} мм рт. ст., влажность: {4}%\r\n\
Ветер: {5}, {6} м/с, {7}".format(main, descr, t, int(pr), info["main"]["humidity"], windType, speed, deg)
    return s

def schedule():
    book = xlrd.open_workbook("file.xlsx")
    sheet = book.sheet_by_index(0)

    num_cols = sheet.ncols
    #num_rows = sheet.nrows

    groups_list = []
    dayofw = ["пн", "вт", "ср", "чт", "пт", "сб"]
    groups = {}

    for col_index in range(num_cols):
        group_cell = str(sheet.cell(1, col_index).value)
        if re.fullmatch(r"И[НАВКМАС]БО[П]?-[01][0-9]-[01][0-9]", group_cell):
            i = 3
            groups_list.append(group_cell.upper())
            week = {"пн" : None, "вт" : None, "ср" : None, "чт" : None, "пт" : None, "сб" : None}
            for i in range(6):
                day = [[], [], [], [], [], []]
                for j in range(6):
                    for k in range(2):
                        row = 3 + k + j * 2 + i * 12
                        sbj = sheet.cell(row, col_index).value
                        lsnType = sheet.cell(row, col_index + 1).value
                        tchr = sheet.cell(row, col_index + 2).value
                        kab = sheet.cell(row, col_index + 3).value
                        if row % 2 != 0:
                            startTime = sheet.cell(row, 2).value
                            endTime = sheet.cell(row, 3).value
                            num = int(sheet.cell(row, 1).value)
                        else:
                            startTime = sheet.cell(row - 1, 2).value
                            endTime = sheet.cell(row - 1, 3).value
                            num = int(sheet.cell(row - 1, 1).value)
                        para = {"subject" : sbj, "start" : startTime, "end" : endTime, "number" : num,
                        "teacher" : tchr, "type" : lsnType, "kab" : kab}
                        day[k].append(para)
                week[dayofw[i]] = day
            groups.update({group_cell : week})
    return groups

def even(a):
    page = requests.get("https://www.mirea.ru/")
    soup = BeautifulSoup(page.text, "html.parser")

    result = re.findall(r'\d+' ,str(soup.find("div", {"class" : "date_text uk-display-inline-block"})))
    if a == 0:
        if int(result[1]) % 2 != 0:
            return 0
        else:
            return 1
    elif a == 1:
        return int(result[1])

'''for key in groups:
    print(key + ":")
    for key1 in groups[key]:
        print("     {0}".format(key1))
        for key2 in range(2):
            print("         {0}".format(key2 + 1))
            for key3 in range(6):
                print("             {0}".format(key3 + 1))
                for key4 in groups[key][key1][key2][key3]:
                    print("                 {0} -- {1}".format(key4, groups[key][key1][key2][key3][key4]))


        day = str(sheet.cell(3, 0).value)
        for row_index in range(4, 76):
            cell = str(sheet.cell(row_index, col_index).value)
            if cell != "":
                if row_index % 2 != 0:
                    startTime = str(sheet.cell(row_index, 2).value)
                    endTime = str(sheet.cell(row_index, 3).value)
                    num = str(int(sheet.cell(row_index, 1).value))
                lsnType = str(sheet.cell(row_index, col_index+1).value)
                tchr = str(sheet.cell(row_index, col_index+2).value)
                ch = str(sheet.cell(row_index, 4).value)
                kab = str(sheet.cell(row_index, col_index+3).value)
                para = {"name" : cell, "start" : startTime, "end" : endTime, "number" : num,
                "teacher" : tchr, "type" : lsnType, "kab" : kab}
                week[num] = para
                dayofw[ch] = week
                if row_index == i + 12:
                    groups[day] = dayofw
                    sch[group_cell] = groups
                    i = row_index
                    print(row_index)
                    day = str(sheet.cell(i, 0).value)
                    week = {}
                    dayofw = {}'''