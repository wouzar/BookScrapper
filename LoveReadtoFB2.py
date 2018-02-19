from parser import Parser

try:
    from const import BOOK_ID
except:
    raise Exception("No book to parse. Check library.py")

parser = Parser(BOOK_ID)
parser.run()
