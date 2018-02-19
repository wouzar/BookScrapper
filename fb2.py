import base64
from urllib.request import urlopen


class FB2:
    IMAGE_TEMPLATE = '<binary id="%s.jpg" content-type="image/jpeg">%s </binary>'
    IMAGE_BUFFER_LIST = []

    def __init__(self, book, author):
        self.doc = open('%s.%s.fb2' % (author, book), "w+")
        self.doc.write("""<?xml version="1.0" encoding="utf-8"?>
        <FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0" xmlns:xlink="http://www.w3.org/1999/xlink">
          <description>
          
            <title-info>
              <genre></genre>
              <author>
                <nickname>%s</nickname>
              </author>
              <book-title> %s </book-title>
              <coverpage>
                <image xlink:href="#cover.jpg"/>
              </coverpage>
              <lang>ru</lang>
            </title-info>
            
            <document-info>
              <author>
                <nickname>pasana</nickname>
              </author>
              <program-used>https://github.com/pasana/BookScrapper</program-used>
              <date>6.2.2018</date>
              
              <id>1a7c50fa-ff75-4176-8418-4d91b31bc2b0</id>
              <version>1.0</version>
            </document-info>
            
          </description>
          <body>
            <section>
            """ % (author, book))

    def add_paragraph(self):
        self.doc.write("<p>")

    def add_to_paragraph(self, text, bold=False, italic=False):
        result_text = text.replace('\r', ' ').replace('\n', '')
        if bold:
            result_text = "<strong> %s </strong>" % result_text
        if italic:
            result_text = "<emphasized> %s </emphasized>" % result_text
        self.doc.write(result_text)

    def finish_paragraph(self):
        self.doc.write("</p>\n")

    def insert_picture(self, url):
        bin_image = base64.b64encode(urlopen(url).read()).decode("utf-8")
        l = len(self.IMAGE_BUFFER_LIST)
        if l == 0:
            self.IMAGE_BUFFER_LIST += [self.IMAGE_TEMPLATE % ("cover", bin_image)]
        else:
            self.doc.write('<image l:href="#%d.jpg"/>' % l)
            self.IMAGE_BUFFER_LIST += [self.IMAGE_TEMPLATE % (str(l), bin_image)]

    def add_heading(self, text, level=3):
        result_text = text.replace('\r', ' ').replace('\n', '')
        self.doc.write("</section>\n<section>\n<title>\n<strong> <p> %s </p> </strong>\n</title>\n" % result_text)

    def close(self):
        self.doc.write("</section>\n</body>\n")
        for im in self.IMAGE_BUFFER_LIST:
            self.doc.write(im)
            self.doc.write('\n')
            self.doc.write("</FictionBook>")
        self.doc.close()
