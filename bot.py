import logging
import random

from emoji import emojize
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler

from bot_token import bot_token
from parser import Parser

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text=emojize("Привет! :v: \n\nЯ бот, который поможет тебе получить любую книгу "
                                  "с сайта LoveRead.ec в формате FB2. :books: \n\nДля этого используй команду "
                                  "/book с идентификатором книги. Например, /book 2039\n\nТакже ты можешь положиться на волю случая и воспользоваться командой /random",
                                  use_aliases=True))


def hello(bot, update):
    update.message.reply_text(
        emojize('Привет, {}! :v:'.format(update.message.from_user.first_name), use_aliases=True))


def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")


def cancel(bot, update):
    update.message.reply_text("Ладненько")
    return ConversationHandler.END


def book(bot, update, args=None, user_data=None):
    if args:
        if len(args) > 1:
            update.message.reply_text("Error")
    if args or user_data['BOOK']:
        try:
            if args:
                id = int(args[0])
                parser = Parser(id)
            elif user_data['BOOK']:
                parser = user_data['BOOK']
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
    update.message.reply_text(
        'Ничего страшного, попробуй снова!'
    )


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


def main():
    updater = Updater(bot_token)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('random', random_book, pass_user_data=True)],
        states={

            11: [RegexHandler('Да!', book, pass_user_data=True),
                 RegexHandler('Нет', cancel),
                 RegexHandler('Давай другую!', random_book, pass_user_data=True)
                 ]
        },
        fallbacks=[CommandHandler('cancel', cancel)], allow_reentry=True
    )

    dp.add_handler(CommandHandler('hello', hello))
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('book', book, pass_args=True))
    dp.add_handler(conv_handler)
    dp.add_handler(MessageHandler(Filters.command, unknown))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
