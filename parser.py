from bs4 import NavigableString

from const import *


class Parser:
    def __init__(self, document, book_id):
        self.doc = document
        self.book_id = book_id

    def process_page(self, body):
        book = body.find('div', class_="MsoNormal").children
        for element in book:
            if element == '\n':
                continue
            self.process_element(element)

    def process_element(self, element):
        element_tag, element_class, children_n, is_new_paragraph = self.get_triple(element)
        # unique.add((element_tag, element_class,))

        if element_tag in ['a'] or is_new_paragraph or element_tag == 'br':
            return

        if element_tag == 'img':
            self.doc.insert_picture(SITE + element['src'])
        elif element_tag == 'p':
            self.doc.add_paragraph()
            if not children_n:
                if element_class == 'MsoNormal':
                    self.doc.add_to_paragraph(element.text)
                elif element_class == 'strong':
                    self.doc.add_to_paragraph(element.text, bold=True)
                elif element_class == 'em':
                    self.doc.add_to_paragraph(element.text, italic=False)
            else:
                self.process_children(element.contents, element_class)
            self.doc.finish_paragraph()
        elif element_tag == 'div':
            if not element_class:
                return
            if not children_n:
                if element_class[:-1] == 'take_h':
                    self.doc.add_heading(element.text, level=int(element_class[-1]))
            else:
                if element_class[:-1] == 'take_h':
                    if element.contents[1].name == 'br':
                        self.doc.add_heading("%s. %s" % (element.contents[0], element.contents[2]),
                                             level=int(element_class[-1]))
                    else:
                        print(element)
                elif element_class == 'em':
                    self.doc.add_paragraph()
                    self.process_children(element.contents, element_class)
                    self.doc.finish_paragraph()
                elif element_class == 'poem':
                    pass  # TODO
        elif element_tag[0] == 'h' and len(element_tag) == 2:
            self.doc.add_heading(element.text, level=int(element_tag[1]))

    def get_triple(self, element):
        name = element.name
        try:
            el_class = element['class'][0]
        except:
            el_class = None
        try:
            children = element.contents.__len__()
            if children == 1 and type(element.contents[0]) == NavigableString:  # means no tags in
                children = None
        except:
            children = None

        is_new_paragraph = False
        if type(element) == NavigableString and element == "\n":
            is_new_paragraph = True

        return name, el_class, children, is_new_paragraph

    def process_children(self, children, parent_class):
        for part in children:
            part_tag, part_class, part_children, part_is_new_paragraph = self.get_triple(part)
            # unique.add((part_tag, part_class,))
            if part_is_new_paragraph:
                continue
            if not part_children:
                self.process_leaf(part, part_tag, part_class, parent_class)
                # check it
                if part_tag == 'div' and part_children == 1:
                    part_tag, part_class, part_children, part_is_new_paragraph = self.get_triple(
                        part.contents[0])
                if part_tag == 'p' and part_class == 'MsoNormal':
                    self.doc.add_to_paragraph(part.text)
            else:
                pass

    def process_leaf(self, part, part_tag, part_class, parent_class=None):
        if part_tag is None and part_class is None:
            if parent_class == 'em':
                self.doc.add_to_paragraph(part, italic=True)
            else:
                self.doc.add_to_paragraph(part)
        elif part_tag == 'img':
            self.doc.insert_picture(SITE + part['src'])
        elif part_tag == 'i' or part_class == 'em':
            self.doc.add_to_paragraph(part.text, italic=True)
        elif part_tag == 'b' or part_class == ['strong']:
            self.doc.add_to_paragraph(part.text, bold=True)
        elif part_tag == 'a':
            pass  # TODO