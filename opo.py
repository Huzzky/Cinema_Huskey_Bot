import telebot
from telebot import types
import random
import requests
import bs4
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import re
from telebot.types import ReplyKeyboardRemove,ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardMarkup, InlineKeyboardButton



info_films_dop = ['Продолжительность фильма: ', 'Год выхода фильма: ', 'Дата выхода фильма в России: ', 'Возрастное ограничение: ']
dop_full,dop_full2,dop_full3,dop_full4,dop_full5,href,info_films,proverka,name_cinema,name_metro,id_cinema,kino,description=[],[],[],[],[],[],[],[],[],[],[],[],[]
pol,pol1,pol2,pol3,pol4,pol5,count,aj,index=0,0,0,0,0,0,0,0,0
dict_cinema={}
TOKEN = '767349424:AAEVMUtfNPMWx8ePCA6wTiuqtWxuZxA3T2c'
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['help'])
def help(message):
	bot.send_message(message.chat.id, '''Привет, Вы обратились к команде /help. Значит у Вас есть проблемы.
Ладно, начну помогать:
1. Если Вы вводите название кинотеатра и сеансы не показываются, то поменяйте раскладку клавиатуры. 
2. Продолжение к первому. Если все равно не появляется, то, скорее всего, сеансов сейчас нет. Посмотрите завтра.
3. На завтрашний день сеансы бот не показывает, но это пока что!!!
4. Если бот не отвечает на сообщения, то попробуйте заново написать /films. Бывают баги и лаги.
5. Города будут добавляться со временем, но не сразу. Ждите.
6. Бот достаточно чувствительный и тупой, поэтому не надо ругаться на него и обливать грязью. Он дорабатывается.
7. Есть команда /kino
8. Список помощи будет дополняться, но для этого пишите на почту vladislav.bychkov01@gmail.com или в Вк vk.com/h4zci .''')




@bot.message_handler(commands=['start']) 
def handle_start(message):
	bot.send_message(message.chat.id,'Здравствуй, ' + str(message.from_user.first_name))
	bot.send_message(message.chat.id, '''Я - Бот, который может показывать расписание сеансов определенного фильма.
Для начала хочу тебе разъяснить, что код устроен странно. Я(Бот) еще не такой умный, чтобы использовать меня в машине Tesla.
Поэтому, пожалуйста, не надо меня насиловать своими сообщениями. В команде /help все написано.
Итак, чтобы начать - напиши /films и тебе выведится 100 фильмов, которые идут в прокате в Москве.
Также есть команда /kino, которая показывает все кинотеатры в Москве и МО. Поосле выбора покажет расписание.''')



@bot.message_handler(commands=['films'])
def handle_films(message):
	global count, aj
	global href_films, proverka,kino
	href_films=[]
	data1 = requests.get('https://msk.kinoafisha.info/movies/')
	data = data1.text
	bs = BeautifulSoup(data, 'html.parser')
	elms = bs.select('div.films_right a')
	for x in elms:
		count+=1
		href_films.append( x.attrs['href']) # Добавляем в массив ссылки, чтобы можно было
# Парсить Описание и сеансы
	elms2 = bs.select('span.link_border') #Поиск всех названий фильмов
	for x in elms2:
		if x.text=="Фильмы в прокате": # ограничение до панели "кнопок"
			break
		else:
			aj+=1
			if aj<=100:	
				kino.append('"'+x.text+'"'+" - /" +str(aj))
			else:
				pass
	
	bot.send_message(message.chat.id, '\n'.join(kino))
	kino=[]
	aj=0
	msg =bot.send_message(message.chat.id, "Выбери номер фильма: ")
	bot.register_next_step_handler(msg, OMl)
def OMl(message):
	global change_films, change_films_2
	global description
	global info_films
	change_films= message.text
	change_films_2 = change_films.lstrip('/')
	if change_films.lower == "выход" or change_films=='-':
		pass
	else:
		try:
			try:
				data1=requests.get(href_films[int(change_films_2)-1])#парсинг описания и сеансов фильма
				data = data1.text
				bs = BeautifulSoup(data, "html.parser")
				elms3=bs.select('span.movieInfoV2_descText p') #парсинг описания
				
				for i in elms3:
					description.append(i.text)
				elms4=bs.select('span.movieInfoV2_infoData') # Парсинг времени и выхода фильма
				for i in elms4:
					info_films.append(i.text)
					
				for o in range(len(info_films)):
					try:
						description.append(info_films_dop[o]+info_films[o])
					
					except IndexError:
						pass
				#print(description)
				bot.send_message(message.chat.id, '\n\n'.join(description))
				description, info_films = [], []
				button_hi = KeyboardButton('Список кинотеатров')
				greet_kb = ReplyKeyboardMarkup()
				greet_kb.add(button_hi)
				msg = bot.send_message(message.chat.id, "Ты можешь выбрать 'Выход' или написать название кинотетра. Например: 'ТРЦ «Миля»'. \n\nЕсли не знаешь какие есть кинотетры, то нажми на кнопку 'Список кинотеатров'.\nЕсли что-то не получается, то обратись к команде /help. \nВыбирай.", reply_markup=greet_kb)
				bot.register_next_step_handler(msg, seans_cinema)
			except IndexError:
				bot.send_message(message.chat.id, "Такого номера фильма нет, увы. Начни все заново - /films")
		except ValueError:
			bot.send_message(message.chat.id, "Ты ввел не номер фильма. Начни все заново - /films")

def seans_cinema(message):
	global dict_cinema,proverka,dop_full4
	reply_markup=greet_kb.ReplyKeyboardRemove()
	number_of_cinema=href_films[int(change_films_2)-1][35:]
	data1=requests.get('https://msk.kinoafisha.info/movies/'+str(number_of_cinema)+'#subMenuScrollTo') #парсинг описания и сеансов фильма
	data = data1.text
	bs = BeautifulSoup(data, 'html.parser')
	elms6=bs.select('a.theater_name')#Кинотеатр
	for i in elms6:
		proverka.append(i.text)
	bs = BeautifulSoup(data, "html.parser")
	change_second = message.text
	if change_second=='Выход':
		bot.send_message(message.chat.id, "Ладно.")
	elif change_second=='Выход':
		pass
	elif change_second=="Список кинотеатров":
		print(proverka)
		bot.send_message(message.chat.id, "Тебе выведет названия кинотетров, где есть сеансы этого фильма.")
		bot.send_message(message.chat.id, '\n'.join(proverka))
		proverka=[]
		bot.send_message(message.chat.id, "Введи еще раз /films и введи уже нужный кинотетр.")
	else:
		number_of_cinema=href_films[int(change_films_2)-1][35:]
		data1=requests.get('https://msk.kinoafisha.info/movies/'+str(number_of_cinema)+'#subMenuScrollTo') #парсинг описания и сеансов фильма
		data = data1.text
		bs = BeautifulSoup(data, "html.parser")
		elms9=bs.select('div.showtimes_cell')
		for i in elms9:
			dop_full.append(i.text.replace('\n',' '))
		for i in range(len(dop_full)):
			dop_full2.append(dop_full[i].replace('\r',' '))
		for i in range(len(dop_full2)):
			dop_full3.append(dop_full2[i].replace('\xa0', ' '))
		for i in range(len(dop_full3)):
			dop_full4.append(dop_full3[i].rstrip(' ').lstrip(' '))
		a=1
		dop_full4.remove('Время сеанса  20:50')
		dop_full4.remove('Сеанс начался  20:50')
		dop_full4.remove('Условные обозначения Помощь с билетами')
		dop_full4.remove('Можно купить билет  20:50 150')
		dop_full4.remove('Низкая цена  20:50 150')
		#print(dop_full4)
		go=0
		for i in range(len(dop_full4)):
			try:
				dict_cinema[dop_full4[go]]= dop_full4[go+1]
				go+=2
			except IndexError:
				pass
		for i in dict_cinema:
			if change_second in i:
				bot.send_message(message.chat.id, 'Сеансы: '+'\n\n'+ dict_cinema[i])
				dop_full4=[]
				dict_cinema={}
				proverka=[]

				
				
				
				
				
				
				
				
				

a,b,c,d,e,f =[], [], [],[],[],[]
count,index,ind,count2 = 0,0,0,1
time_none = 4
fa,fo ='',''

@bot.message_handler(commands=['kino'])
def first_step(message):
	global count, fa, fo,count2,b,a,c
	a = []
	fa,fo,count2 = '','',1
	c=[]
	data1 = requests.get('https://msk.kinoafisha.info/cinema/')
	data = data1.text 
	bs = BeautifulSoup(data, 'html.parser')
	elms = bs.select('a.theater_name.link.link-default')
	for i in elms:
		count+=1
		if count<183:
			b.append(i.attrs['href'])# Ссылки на кинотеатры
	elms = bs.select('div.theater_right')
	count=0
	for i in elms:
		count+=1
		if count<183:
			a.append(i.text.rstrip('\n').lstrip('\n')) # Список кинотеатров

	for i in a:
		if len(fa)<4000:
			fa+=i +' - /'+str(count2) + '\n\n'
			count2+=1
		else:
			fo+=i+' - /'+str(count2) + '\n\n'
			count2+=1
	bot.send_message(message.chat.id, fa)
	msg = bot.send_message(message.chat.id, fo + '\n\nВыбери кинотеатр для просмотра расписания. Или напиши "Назад" или "Выход"')
	bot.register_next_step_handler(msg, second_step)

def second_step(message):
	global ind, b,c,d,f
	change_of_cinema= message.text
	wordUp=set('!@#$%^&*(){}[]<>,.:;"№%-_+=qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMйцукенгшщзхъёфывапролджэячсмитьбюЙЦУКЕНГШЩЗХЪЁФЫВАПРОЛДЖЭЯЧСМИТЬБЮ')
	if change_of_cinema=='Назад' or change_of_cinema=='назад' or change_of_cinema=='Выход' or change_of_cinema=='выход':
		bot.send_message(message.chat.id, 'Ладно.')
		ind, b,c,d,f = 0, [], [],[],[]
	elif any(x for x in wordUp if x in change_of_cinema)==True:
		bot.send_message(message.chat.id, "Ты ввел не то, что нужно")
	else:
		if change_of_cinema.lstrip('/')==' ' or change_of_cinema.lstrip('/') == '':
			bot.send_message(message.chat.id, "Ты ввел только '/'")
		else:
			change_of_cinema_2 = change_of_cinema.lstrip('/')
			try:
				try:
					data1= requests.get(b[int(change_of_cinema_2)-1])
				except ValueError:
					pass
			except IndexError:
				pass
			data = data1.text
			bs = BeautifulSoup(data, 'html.parser')
			elms = bs.select('div.showtimes_item.fav.fav-film')
			# Здесь
			for i in elms:
				c.append(i.text.split('\n'))
			for i in c:
				for j in i:
					if j=='' or j=="Купить":
						pass
					else:
						d.append(''.join(j)) # Расписание и цена
			list_janre=['аниме','биографический','боевик','вестерн','военный','детектив','детский','документальный','драма','исторический','кинокомикс','комедия','концерт','короткометражный','криминал','мелодрама','мистика','музыка','мультфильм','мюзикл','научный','приключения','реалити-шоу','семейный','спорт','ток-шоу','триллер','ужасы','фантастика','фильм-нуар','фэнтези','эротика']

			for i in enumerate(d):
				for j in range(len(list_janre)):
					if list_janre[j] in i[1]:
						del d[i[0]]
						break
			for i in enumerate(d):
				if '₽' in i[1]:
					del d[i[0]]
			elms = bs.select('a.theaterInfo_addr.link.link-default') # Адрес
			adres_of_cinema = []
			for i in elms:
				adres_of_cinema.append(i.text.rstrip('\n'))
			elms = bs.select('div.theaterInfo_desc') # описание кинотеатра
			desc_of_cinema = []
			for i in elms:
				desc_of_cinema.append(i.text)
			bot.send_message(message.chat.id, 'Адрес: '+adres_of_cinema[0])
			bot.send_message(message.chat.id, 'Описание: '+'\n'.join(desc_of_cinema))
			bot.send_message(message.chat.id, 'Расписание: '+'\n'.join(d))
			adres_of_cinema,desc_of_cinema,d, data, change_of_cinema_2, change_of_cinema=[],[],[], "",0,0


				


bot.polling()
