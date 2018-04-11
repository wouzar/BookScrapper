from parser import Parser

import argparse

try:
    from const import BOOK_ID
except:
    BOOK_ID = None

argsparser = argparse.ArgumentParser(description='List of useful parameters')
argsparser.add_argument('--book_id', type=int, 
    help="id of the book from the site (by default it's fetched from the const.py file)")

args = argsparser.parse_args()

if args.book_id:
    book_id = args.book_id
elif BOOK_ID:
    book_id = BOOK_ID
else:
    raise Exception("No book to parse. Check library.py")

parser = Parser(book_id, in_memory=False)
parser.run()
