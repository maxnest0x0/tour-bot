from time import time
from random import randint,shuffle,choice
from datetime import date
RussianSymbols = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
OtherSymbols = '.,!? '
original_file = 'TEST.txt'
edit_file = 'example.txt'
CitiesFrom = ['Екатеринбурга'] #Добавить городов
StartSinceCity = [
    'Хочу поехать',
    'Хочу заселиться',
    'Хочу поездку',
    'Планирую поехать',
    'Планирую заселиться',
    'Планирую о поездке',
    'Мечтаю поехать',
    'Мечтаю заселиться',
    'Мечтаю о поездке',
    'Размышляю о поздке',
    'Размышляю о заселении',
    'Размышляю о поездке',
    'Желательно заселиться',
    'Отправиться хочу'
]
StartSinceData = [
    'Планирую поехать с',
    'Хочу заселиться с',
    'Планирую заселиться c',
    'Размышляю о заселении с',
    'Думаю о заселении с',
    'Планирую поехать',
    'Хочу заселиться',
    'Планирую заселиться',
    'Размышляю о заселении',
    'Думаю о заселении',
    'Желательно заселиться',
    'Думаю поеду',
    'Отправлюсь',
    'Поеду',
    'Хотелось бы поехать'
]
Country_Cities = {'Камбоджу': ['Сиемреап'], 
'Шотландию': ['Эдинбург'], 
'Уругвай': ['Монтевидео'], 
'Германию': ['Гамбург', 'Кроицберг', 'Мюнхен', 'Кёльн'], 
'Венгрию': ['Будапешт'], 
'Украину': ['Киев'], 
'Канаду': ['Квебек', 'Оттаву', 'Вануверу','Торонто'], 
'Турцию': ['Анкару', 'Бодрум'], 
'Китай': ['Шэшьчжэнь', 'Гонконг', 'Пекин', 'Гуанчжоу','Шанхай'], 
'Данию': ['Копенгаген'], 
'Израиль': ['Тель-Авив'], 
'Объединённые Арабские Эмираты': ['Абу-Даби', 'Дубай'], 
'Индию': ['Мумбаи','Гоа'], 
'Египет': ['Каир'], 
'Испанию': ['Мадрид', 'Малагу','Барселону'], 
'Австралию': ['Брисбен', 'Канберру','Кэрнс'], 
'Румынию': ['Бухарест'], 
'Швейцарию': ['Берн','Церматт'], 
'ЮАР': ['Кейптаун'], 
'Францию': ['Ниццу', 'Париж'],
'Казахстан': ['Алматы'], 
'США': ['Сиэтл', 'Чикаго ', 'Каролину','Орланду','Новый Орлеан'], 
'Руспублику Корея': ['Сеул'], 
'Италию': ['Милан', 'Неаполь','Рим','Флоренцию'], 
'Польшу': ['Варшаву'], 
'Японию': ['Фукуоку', 'Саппоро','Токио'], 
'Таиланд': ['Бангкок', 'Хуахин', 'Чиангмай'], 
'Ирландию': ['Дублин'], 
'Марокко': ['Марракеш'], 
'Португалию': ['Лиссабон'], 
'Бразилию': ['Сан-Паулу','Рио-де-Жанейро'], 
'Швецию': ['Гётеборг', 'Мальмё','Стокгольм'], 
'Мексику': ['Пуэрто-Вальярту'], 
'Литву': ['Вильнюс'],
'Нидерланды':['Амстердам'],
'Англию':['Лондон'],
'Чили':['Сентьяго'],
'Республику Сингапур':['Сингапур'],
'Бельгию':['Брюссель'],
'Норвегию':['Осло'],
'Чехию':['Прагу'],
'Бутан':['Тхимпху'],
'Латвию':['Ригу'],
'Австрию':['Зальцбург'],
'Словению':['Люблян']}
def new_d_m(first_year = 2024):
    '''
    Создание дня,месяца,года и возвращение их значений
    '''
    monthwithoutfebruary = [1,3,4,5,6,7,8,9,10,11,12]
    year = randint(first_year,2026)
    day = randint(1,30) 
    if day > 28:      #Если это не февраль то выбираем любой оставшийся месяц
        month = choice(monthwithoutfebruary)
    else:                 #Если же февраль возможен то выбираем любой месяц без ограничений
        month = randint(1,12)
    return day,month,year
class Data:
    month_list = [' января', ' февраля', ' марта', ' апреля', ' мая', ' июня', ' июля', ' августа', ' сентября', ' октября', ' ноября', ' декабря']
    @classmethod
    def day_mon_yea(cls):
        '''
        Создание 2 дат (начало - конец) отпуска
        '''
        cls.day,cls.month,cls.year_1 = new_d_m()
        cls.day_2,cls.month_2,cls.year_2 = new_d_m(cls.year_1)
        return cls.day,cls.month,cls.year_1,cls.day_2,cls.month_2,cls.year_2
    def __init__(self):
        self.day,self.month,self.year_1,self.day_2,self.month_2,self.year_2 = Data.day_mon_yea()
    def create_data(self):
        '''
        Редактирование дат начала и конца отпуска до реальных дат(конец позже выезда и отпуск не больше 50 дней)
        '''    
        while not (5 < (date(self.year_2, self.month_2, self.day_2) - date(self.year_1, self.month, self.day)).days < 50):
            self.day,self.month,self.year_1,self.day_2,self.month_2,self.year_2 = Data.day_mon_yea()
        count_days = (date(self.year_2, self.month_2, self.day_2) - date(self.year_1, self.month, self.day)).days
        day_1 = str(self.day)
        day_2 = str(self.day_2)
        if randint(0,1):
            month_1 = Data.month_list[int(self.month) - 1]
            month_2 = Data.month_list[int(self.month_2) - 1]
            year_1 = ''
            year_2 = ''
        else:
            month_1 = f".{self.month:02d}"
            year_1 = f".{self.year_1}"
            month_2 = f".{self.month_2:02d}"
            year_2 = f".{self.year_2}"
        first_data = day_1 + month_1 + year_1
        second_data = day_2 + month_2 + year_2  
        return first_data,second_data,count_days
class humans:
    def __init__(self) -> None:
        self.count_child = randint(0,3)
        self.count_adult = randint(1,2)
        self.count_baby = randint(0,1)
    def create_family(self):
        if self.count_baby == 0:
            baby = ''
        else:
            a = randint(0,1)
            list = ['с 1 малышом ','и один малыш ']
            baby = list[a]
        if self.count_child == 0:
            child = ''
        elif self.count_child == 1:
            a = randint(0,1)
            list = ['с 1 ребенком ','и один ребенок ']
            child = list[a]
        elif self.count_child == 2:
            a = randint(0,2)
            list = ['с 2 детьми ','и двумя детьми ','с двумя детьми ']
            child = list[a]
        else:
            a = randint(0,2)
            list = ['с 3 детьми ','и три ребенка ','с тремя детьми ']
            child = list[a]
        if self.count_adult == 1:
            a = randint(0,1)
            list = ['1 взрослым ','одним взрослым ']
            adult = list[a]
        elif self.count_adult == 2:
            a = randint(0,1)
            list = ['2 взрослыми ','двумя взрослыми ']
            adult = list[a]
        family = adult + child + baby
        return family,self.count_adult,self.count_child,self.count_baby
#Finding = from_city(ekaterinburg) + startcity + first_data + second_data. family
#Finding = startdata + in_city + first_data + second_data. family
def StringCounts(original_file,edit_file):
    '''
    Выводит колво строчек в двух файлах
    '''
    with open(original_file,'r',encoding='UTF-8') as file:
        with open(edit_file,'r',encoding='UTF-8') as file1:    
            print(f'Колво стр ориг - {len(file.readlines())}\nКолво стр копии - {len(file1.readlines())}')
def SpacesDelete(original_file,edit_file):
    '''
    Удаляет все пробелы вначале,конце,между строчек
    '''
    with open(original_file,'r',encoding='UTF-8') as file:
        with open(edit_file,'w',encoding='UTF-8') as file1:
            for String in file.readlines():
                if len(String) > 1:
                    file1.write(String.strip(' '))
def DeleteOtherSymbols(original_file,edit_file):
    '''
    Удаляет все символы кроме букв алфавита из текста файла и записывает эти данные в второй файл
    '''
    with open(original_file,'r',encoding='UTF-8') as file:    
        with open(edit_file,'w+',encoding='UTF-8') as file1:    
            for string in file.readlines():    
                stringWithword = ''
                for symbol in string:
                    if symbol.lower() in RussianSymbols:
                        stringWithword += symbol.lower()
                    elif symbol.lower() in OtherSymbols:
                        stringWithword += ' '
                file1.write(f'{stringWithword}\n')
def get_all_words(original_file):
    '''
    Находит все уникальные слова в тексте файла и количество использований найденных слов в тексте
    '''
    Words = dict()
    with open(original_file,'r',encoding='UTF-8') as file:    
        for string in file.readlines():
            word = ''
            for symbol in string:
                if (symbol not in OtherSymbols):
                    word += symbol
                else:
                    if word in Words:
                        Words[word] += 1
                    else:
                        Words[word] = 1
                    word = ''
    with open('words.txt','w+',encoding='UTF-8') as file:
        for key,value in Words.items():
            string = f'{key} - {value}\n'
            file.write(string)
if __name__ == '__main__':
    print('Начинаю программу!')
    t1 = time()
    cout = 0
    # with open('Done.txt','a+',encoding='UTF-8') as file:
    #     with open('tags.txt','a+',encoding='UTF-8') as tag_file:
    #         for start in StartSinceCity:
    #             for country,cities in Country_Cities.items():
    #                 for city in cities:
    #                     for fromcity in CitiesFrom:
    #                         for i in range(2):
    #                             data = Data()
    #                             human = humans()
    #                             first_data,second_data,countdays = data.create_data()
    #                             family,count_adult,count_child,count_baby = human.create_family()
    #                             string1 = f'{start} в {country} в {city} из {fromcity} с {first_data} до {second_data} c {family}'
    #                             tags1 = f'Страна:{country},куда:{city},откуда:{fromcity},датаначала:{first_data},датаконца:{second_data},взрослые:{count_adult},дети:{count_child},малыши:{count_baby}'
                                
    #                             first_data,second_data,countdays = data.create_data()
    #                             family,count_adult,count_child,count_baby = human.create_family()
    #                             string2 = f'{start} в {city} в {country} из {fromcity} с {first_data} до {second_data} c {family}'
    #                             tags2 = f'Страна:{country},куда:{city},откуда:{fromcity},датаначала:{first_data},датаконца:{second_data},взрослые:{count_adult},дети:{count_child},малыши:{count_baby}'
                                
    #                             first_data,second_data,countdays = data.create_data()
    #                             family,count_adult,count_child,count_baby = human.create_family()
    #                             string3 = f'{start} в {city} из {fromcity} с {first_data} до {second_data} c {family}'
    #                             tags3 = f'Страна:{0},куда:{city},откуда:{fromcity},датаначала:{first_data},датаконца:{second_data},взрослые:{count_adult},дети:{count_child},малыши:{count_baby}'

    #                             file.write(f"{string1}\n")
    #                             file.write(f"{string2}\n")
    #                             file.write(f"{string3}\n")
    #                             tag_file.write(f"{tags1}\n")
    #                             tag_file.write(f"{tags2}\n")
    #                             tag_file.write(f"{tags3}\n")
    with open('Done.txt','a+',encoding='UTF-8') as file:
        with open('tags.txt','a+',encoding='UTF-8') as tag_file:
            for start in StartSinceData:
                for country,cities in Country_Cities.items():
                    for city in cities:
                        for fromcity in CitiesFrom:
                            for i in range(2):
                                data = Data()
                                human = humans()
                                
                                first_data,second_data,countdays = data.create_data()
                                family,count_adult,count_child,count_baby = human.create_family()
                                string1 = f'{start} {first_data} до {second_data} из {fromcity} в {city} в {country} с {family}'
                                tags1 = f'Страна:{country},куда:{city},откуда:{fromcity},датаначала:{first_data},датаконца:{second_data},взрослые:{count_adult},дети:{count_child},малыши:{count_baby}'
                                
                                first_data,second_data,countdays = data.create_data()
                                family,count_adult,count_child,count_baby = human.create_family()
                                string2 = f'{start} с {first_data} по {second_data} в {city} в {country} из {fromcity} с {family}'
                                tags2 = f'Страна:{country},куда:{city},откуда:{fromcity},датаначала:{first_data},датаконца:{second_data},взрослые:{count_adult},дети:{count_child},малыши:{count_baby}'
                                
                                first_data,second_data,countdays = data.create_data()
                                family,count_adult,count_child,count_baby = human.create_family()
                                string3 = f'{start} с {first_data} до {second_data} в {country} в {city} из {fromcity} с {family}'
                                tags3 = f'Страна:{country},куда:{city},откуда:{fromcity},датаначала:{first_data},датаконца:{second_data},взрослые:{count_adult},дети:{count_child},малыши:{count_baby}'
                                
                                file.write(f"{string1}\n")
                                file.write(f"{string2}\n")
                                file.write(f"{string3}\n")
                                tag_file.write(f"{tags1}\n")
                                tag_file.write(f"{tags2}\n")
                                tag_file.write(f"{tags3}\n")
    #DeleteOtherSymbols(original_file,edit_file)    #~30 мс
    #StringCounts(original_file,edit_file)       #~10мс
    #get_all_words(edit_file)
    """with open('Done.txt','r',encoding='UTF-8') as file:
        with open('example.txt','w',encoding='UTF-8') as file1:
            unsorted_file = file.readlines()
            shuffle(unsorted_file)
            file1.writelines(unsorted_file)"""
    # with open('Done.txt','r',encoding='UTF-8') as file:
    #     with open('example')
    data = Data()
    print(data.create_data())
    t2 = time()
    print(f'{round(t2-t1,6)*1000} мс\nГотово!')