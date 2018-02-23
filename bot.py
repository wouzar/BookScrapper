import logging
import random
import urllib.parse

import requests
from bs4 import BeautifulSoup
from emoji import emojize
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler

from bot_token import bot_token
from const import SEARCH_TEMPLATE
from parser import Parser

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text=emojize("Привет! :v: \n\nЯ бот, который поможет тебе получить любую книгу "
                                  "с сайта LoveRead.ec в формате FB2. :books: \n\nДля этого используй команду "
                                  "/book с идентификатором книги. Например, /book 2039\n\n"
                                  "Также ты можешь положиться на волю случая и воспользоваться командой /random\n\n"
                                  "Или найти по ключевым словам с помощью /find",
                                  use_aliases=True))


def hello(bot, update):
    update.message.reply_text(
        emojize('Привет, {}! :v:'.format(update.message.from_user.first_name), use_aliases=True))


def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")


def cancel(bot, update):
    update.message.reply_text("Ладненько", reply_markup=ReplyKeyboardRemove)
    return ConversationHandler.END


def book(bot, update, args=None, user_data=None):
    if args:
        if len(args) > 1:
            update.message.reply_text("Error")
    keys = user_data.keys()
    if args or 'BOOK' in keys or 'BOOKS' in keys:
        try:
            if args:
                id = int(args[0])
                parser = Parser(id)
            elif 'BOOK' in keys:
                parser = user_data['BOOK']
            elif 'BOOKS' in keys:
                parser = Parser(int(user_data['BOOKS'][int(update.message.text)]))
            bot.send_message(chat_id=update.message.chat_id,
                             text=emojize(
                                 "Скачиваю \"%s\" by %s для тебя! :sparkles: \nОставайся на связи! :hourglass:" % (
                                     parser.book_name, parser.author
                                 )), use_aliases=True)
            filename = parser.run()
        except ValueError:
            update.message.reply_text(
                'Что-то не так с идентификатором книги... Попробуй еще раз!'
            )
            return
        bot.send_document(chat_id=update.message.chat_id,
                          document=open(filename, 'rb'))
        update.message.reply_text(
            emojize('Приятного чтения! \n:heart: :book:', use_aliases=True)
        )
        # update.message.reply_text(
        #    'Ничего страшного, попробуй снова!'
        # )


def init_random_book():
    id = random.randint(1, 100000)
    try:
        parser = Parser(id)
    except AttributeError:
        return None
    return parser


def random_book(bot, update, user_data):
    parser = None
    while parser is None:
        parser = init_random_book()
    user_data['BOOK'] = parser
    bot.send_message(chat_id=update.message.chat_id,
                     text="\"%s\" by %s." % (
                         parser.book_name, parser.author
                     ))
    reply_keyboard = [["Да!", "Нет", "Давай другую!"]]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, n_cols=2,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    update.message.reply_text("Ну что, читаем?", reply_markup=reply_markup)
    return 11


def find_books_on_site(args):
    query = ' '.join(args)
    query_param = urllib.parse.quote_plus(query, encoding='cp1251')
    response = requests.get(SEARCH_TEMPLATE % query_param)
    body = BeautifulSoup(response.content, "lxml")
    found_books = body.find('div', {'class': "contents"}).parent.parent.findAll('li')[1:]
    return found_books


def show_found_books(bot, update, user_data, index_start=0):
    for i, r_book in enumerate(user_data['found_books'][:5]):
        name, author = list(map(lambda x: x.text.strip(), r_book.findAll('a')))
        book_id = r_book.a.attrs['href'].split('?')[1].split('=')[1]
        user_data['BOOKS'][i + 1] = book_id
        bot.send_message(chat_id=update.message.chat_id,
                         text="%d. \"%s\" by %s" % (i + 1, name, author))


def prepare_next_books(user_data):
    if len(user_data['found_books']) > 5:
        user_data['found_books'] = user_data['found_books'][5:]
        reply_keyboard = [[str(x) for x in range(1, 6)], ["Отмена", "Дальше!"]]
    else:
        reply_keyboard = [[str(x) for x in range(1, len(user_data['found_books']) + 1)], ["Отмена"]]
        del user_data['found_books']
    return reply_keyboard


def find_book(bot, update, args=None, user_data=None):
    if args:
        user_data['found_books'] = find_books_on_site(args)
        user_data['BOOKS'] = {}

    if update.message.text == 'Дальше!' or args:
        show_found_books(bot, update, user_data)
        reply_keyboard = prepare_next_books(user_data)

        reply_markup = ReplyKeyboardMarkup(reply_keyboard, n_rows=2,
                                           one_time_keyboard=True,
                                           resize_keyboard=True)
        update.message.reply_text("Выбери номер книги внизу", reply_markup=reply_markup)
        return 12
    else:
        update.message.reply_text("Введи запрос!")


def main():
    updater = Updater(bot_token)
    dp = updater.dispatcher

    random_handler = ConversationHandler(
        entry_points=[CommandHandler('random', random_book, pass_user_data=True)],
        states={

            11: [RegexHandler('Да!', book, pass_user_data=True),
                 RegexHandler('Нет', cancel),
                 RegexHandler('Давай другую!', random_book, pass_user_data=True)
                 ]
        },
        fallbacks=[CommandHandler('cancel', cancel)], allow_reentry=True
    )

    find_handler = ConversationHandler(
        entry_points=[CommandHandler('find', find_book, pass_args=True, pass_user_data=True)],
        states={

            12: [RegexHandler('\d', book, pass_user_data=True),
                 RegexHandler('Отмена', cancel),
                 RegexHandler('Дальше!', find_book, pass_user_data=True)
                 ]
        },
        fallbacks=[CommandHandler('cancel', cancel)], allow_reentry=True
    )

    dp.add_handler(CommandHandler('hello', hello))
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('book', book, pass_args=True))
    dp.add_handler(random_handler)
    dp.add_handler(find_handler)
    dp.add_handler(MessageHandler(Filters.command, unknown))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
