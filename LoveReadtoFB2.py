import requests
from bs4 import BeautifulSoup

from const import TEMPLATE
from fb2 import FB2
from parser import Parser

try:
    from const import BOOK_AUTHOR, BOOK_NAME, BOOK_ID
except:
    raise Exception("No book to parse. Check library.py")

document = FB2(BOOK_NAME, BOOK_AUTHOR)
parser = Parser(document, BOOK_ID)
page = 0
# unique = set()
while True:
    page += 1
    print(TEMPLATE % (BOOK_ID, page))
    response = requests.get(TEMPLATE % (BOOK_ID, page))
    body = BeautifulSoup(response.content)
    parser.process_page(body)
    if body.find('span', text='Вперед'):
        break

document.close()
# print(unique)
