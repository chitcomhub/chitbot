# Бот написан на Python 3.7

import requests
import configurations # содержит токен и id группы
import boto3
from datetime import datetime
import random

def point(event, context):
	print(event)

	dynamodb = boto3.resource('dynamodb')
	top_table = dynamodb.Table('top')
	tasks_table = dynamodb.Table('tasks')
	admin_table = dynamodb.Table('admin')
	champ_table = dynamodb.Table('champ')
	books_table = dynamodb.Table('books')

	# достаем из БД DynamoDB таблицу tasks
	response = tasks_table.scan()
	tasks_items = response['Items']

	# достаем из БД DynamoDB таблицу top
	response = top_table.scan()
	top_items = response['Items']

	# достаем из БД DynamoDB таблицу admin
	response = admin_table.scan()
	admin_items = response['Items']

	# достаем из БД DynamoDB таблицу champ
	response = champ_table.scan()
	champ_items = response['Items']

	# достаем из БД DynamoDB таблицу books
	response = books_table.scan()
	books_items = response['Items']

	message_text = event["message"]["text"]
	chat_id = event["message"]["chat"]["id"]
	username = event["message"]["from"]["username"]
	user_id = event["message"]["from"]["id"]
	name = event["message"]["from"]["first_name"]
	timestamp = event["message"]["date"]

	for i in champ_items:
		champ_date = i['timestamp']

	now_time = datetime.now().strftime('%H:%M:%S')
	ts = champ_date - timestamp
	hours_left = datetime.utcfromtimestamp(ts).strftime('%H:%M:%S')

	# команды для админа
	for i in admin_items:
		admin_id = i['id']

		if message_text[0] == "/" and user_id == admin_id:
			words = message_text.split()
			command = words[0][1:]
			if command == "admin" or command == "admin@chit_champ_bot":
				text = """
					Неужели сам %s пожаловал?!
					У меня в меню есть следующие команды:

					/start - начать турнир.
					/add_champ - добавить новый турнир. (не работает)
					/get_champ - показать N-ый турнир. (не работает)
					/list_champ - получить список турниров. (не работает)
					/update_champ - обновить турнир. (не работает)
					/delete_champ - удалить турнир. (не работает)
					/add_admin - добавить нового админа. (не работает)
					/list_champ - список админов. (не работает)
					""" % i['name']
				send_message(chat_id, text)

			elif command == "start" or command == "start@chit_champ_bot":
				text = """
					Начнем турнир по программированию CHIT CHAMP.
					\nТурнир определит сильнейших программистов в CHITCOM комьюнити.

					1. Для начала надо зарегистрироваться.
					Просто отправь мне текст /regme.
					После этого ты сможешь увидеть себя в /top.

					3. /top - это рейтинг программистов.
					Чтобы быть на высоте, тебе нужно набирать баллы, выполняя задачи.

					4. /task - задачи, которые тебе придется решить.
					За каждую выполненную задачу ты получаешь 1 балл.
					Балл забирает тот, кто первым выполнит задачу.
					Ответы нужно присылать примерно так: "JANE" (без кавычек).
					Чтобы отвечать на задачи, нужно сначала зарегистрироваться.
					Чтобы зарегистрироваться, отправь мне /regme.
					\nСтань победителем CHIT CHAMP и докажи, что ты лучший.
					"""
				send_message(chat_id, text)
	
	# запрет на запуск бота в других чатах
	if chat_id != configurations.group_id and user_id != admin_id:
			text = """
				Мне запрещено общаться вне группы CHITCOM.
				Если у тебя есть вопросы, то можешь написать моим разработчикам:
				@azamat_human
				@efive
				@arbios
			"""
			send_message(chat_id, text)
			raise Exception('Попытались мне написать в чате: ' + str(chat_id))


	# бот библиотекарь
	if message_text == "/addbook" or message_text == "/addbook@chit_champ_bot":
		text = "Чтобы добавить книгу, введите примерно такой текст:\n\n/addbook=Марк Лутц/Изучаем Python/2010/Русский"
		send_message(chat_id, text)

	elif "/addbook=" in message_text:
		for i in books_items:
			# if int(user_id) == i['id']:
			# 	send_message(chat_id, "Введите \"/addbook=Марк Лутц/Изучаем Python/2010/Русский\" (без кавычек)")
			# 	break
		
			message_list = message_text.replace("/addbook=", "")
			message_list = message_list.split("/")
			author = message_list[0]
			title = message_list[1]
			year = message_list[2]
			language = message_list[3]

			books_table.put_item(
			   Item={
			   		'id': random.randint(1, 10000000),
			        'author': author,
			        'title': title,
			        'year': year,
			        'language': language,
			   		'owner': username
			    }
			)
			send_message(chat_id, "Добавлена книга %s от @%s\nСмотри в /books" % (title, username))

	elif message_text == "/books" or message_text == "/books@chit_champ_bot":
		# функция сортирует по столбцу id
			def get_key(key):
				return key['id']

			sorted_items = sorted(books_items, key = get_key, reverse = True)

			n = 0
			book_text = 'Библиотека:\n\nАвтор | Название | Дата | Перевод | Владелец\n\n'
			for i in sorted_items:
				n += 1
				book_text += "%i. %s  | %s | %s | %s | @%s\n" % (
					n,
					i['author'],
					i['title'],
					i['year'],
					i['language'],
					i['owner']
				)

			send_message(chat_id, '%s' % book_text.strip())


	# команды для участников
	elif message_text[0] == "/":
		words = message_text.split()
		command = words[0][1:]

		if command == "regme" or command == "regme@chit_champ_bot":
			this_user = True
			for i in top_items:
				if int(user_id) == i['id']:
					send_message(chat_id, 'Ты уже ранее был зарегистрирован\nСмотри в /top')
					this_user = False
					break
			
			if this_user == True:
				top_table.put_item(
				   Item={
				   		'id' : user_id,
				        'nickname': username,
				        'name': name,
				        'points': 0
				    }
				)
				send_message(chat_id, "Я занес тебя в список участников\nСмотри в /top")

		elif command == "task" or command == "task@chit_champ_bot":

			if champ_date > timestamp:
				text = """
				Ты куда-то торопишься, %s?\nДо начала турнира еще есть время.
				\nЕсли быть точнее, то: \n%s (час, минута, секунда)""" % (name, hours_left)
				send_message(chat_id, text)

			else:
				# функция сортирует по столбцу id
				def get_key(key):
					return key['id']

				sorted_items = sorted(tasks_items, key = get_key)

				end_game = True
				for i in sorted_items:
					if i['winner'] == "0":
						tasks_text = "Задача №%s: \n\t%s\n\n" % (i['id'], i['task'])
						send_message(chat_id, tasks_text)
						end_game = False
						break
				if end_game == True:
					end_text = """Турнир окончен.
					Наберите /top, чтобы увидеть рейтинг программистов"""
					send_message(chat_id, end_text)

		elif command == "top" or command == "top@chit_champ_bot":

			# функция сортирует по столбцу points
			def get_key(key):
				return key['points']

			sorted_items = sorted(top_items, key = get_key, reverse = True)

			top_text = 'Рейтинг программистов:\n\n№ | Никнейм | Имя | Баллы\n\n'
			n = 0
			for i in sorted_items:
				n += 1
				top_text += " %s  | @%s | %s | %s\n" % (n,
					i['nickname'],
					i['name'],
					i['points'])

			send_message(chat_id, '%s' % top_text.strip())

	elif message_text == "Пока, бот":
		send_message(chat_id, "Пока, %s" % name)

	# сравнение ответов участников
	else:
		top_id = 0
		for i in top_items:
			if user_id == i['id']:
				top_id = i['id']
				break

		if user_id == top_id:
			for i in tasks_items:
				if message_text == i['solution'] and i['winner'] == '0':
					text = """@%s решил задачу №%s и получил 1 балл.
						Решение: %s.
						Чтоб перейти на следующее задание, введите /task
						""" % (username, i['id'], i['solution'])

					# добавляем правильно ответившего в поле winner
					tasks_table.update_item(
					    Key={
					        'id': i['id']
					    },
					    UpdateExpression='SET winner = :val1',
					    ExpressionAttributeValues={
					        ':val1': username
					    }
					)

					# добавляем балл за верный ответ
					for i in top_items:
						if i['id'] == int(user_id):
							point = i['points']

					top_table.update_item(
					    Key={
					        'id': user_id
					    },
					    UpdateExpression='SET points = :val1',
					    ExpressionAttributeValues={
					        ':val1': point + 1
					    }
					)

					send_message(chat_id, text)
					break

				elif message_text == i['solution']:
					text = """Эту задачу уже решил @%s.
						Решение: %s.
						Ты должен решить уже следующую задачу.
						Чтоб перейти к действующей задаче, введите /task
						""" % (i['winner'], i['solution'])

					send_message(chat_id, text)
					break


def send_message(chat_id, text):
	url = "https://api.telegram.org/bot{token}/{method}".format(
		token=configurations.token,
		method="sendMessage"
	)
	data = {
		"chat_id": chat_id,
		"text": text
	}
	r = requests.post(url, data = data)
	print(r.json())