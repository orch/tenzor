import textwrap
from html.parser import HTMLParser


HREF = 'href'


class Parser(HTMLParser):

    title_tag = None
    title_tag_attributes = None
    content_tag = None
    content_tag_attributes = None
    allow_in_tags = None
    word_wrap = None
    link_tags = None

    title = None
    title_flag = False
    context = None
    paragraph = None
    content = None
    paragraph_flag = False

    def __init__(self, **kwargs):
        super().__init__()

        self.title_tag = kwargs["title_tag"]  # тэг заголовка
        self.title_tag_attributes = kwargs["title_tag_attributes"]  # атрибуты для тэга заголовка
        self.content_tag = kwargs["content_tag"]  # тэг параграфа
        self.content_tag_attributes = kwargs["content_tag_attributes"]  # атрибуты для тэга параграфа
        self.allow_in_tags = kwargs["allow_in_tags"]  # тэги которые могут быть вложены в параграф
        self.word_wrap = kwargs["word_wrap"]  # размер строки
        self.link_tag = kwargs["link_tag"]  # тэг для ссылки

        self.context = []   # вложенные тэги в параграф
        self.paragraph = []  # содержимое параграфа
        self.content = []  # итоговый текст статьи разделенный абзацами
        self.title = ''  # заголовок статьи

    def get_text(self):
        """
        Из списка по абзацам получаем
        итоговую строку с отступами между абзацами и строками
        :return: str
        """
        text = self.title + "\n\n"
        for paragraph in self.content:
            str = ''.join(paragraph)
            text += "\n".join(textwrap.wrap(str, self.word_wrap)) + "\n\n"

        return text

    def set_paragraph(self, tag, attrs):
        """
        Установка флага о том, что сейчас парсится параграф
        Флаг можно установить только из выключенного состояния,
        поэтому в начале проверка текущего значения
        Добавление тэга в контекст
        :param tag: str
        :param attrs: tuple
        :return: None
        """
        if not self.paragraph_flag:
            dict_attrs = dict(attrs)
            if tag == self.content_tag:
                self.paragraph_flag = True

                for tag_attr in self.content_tag_attributes:
                    if tag_attr in dict_attrs or\
                            dict_attrs[tag_attr] == self.content_tag_attributes[tag_attr]:
                        self.paragraph_flag = True
                    else:
                        self.paragraph_flag = False

        if self.paragraph_flag:
            self.context.append(tag)

    def unset_paragraph(self):
        """
        Сброс фдага параграфа
        Удаление тэга из контекста
        :return: None
        """
        if self.paragraph_flag:
            self.context.pop()
            if not self.context:
                self.paragraph_flag = False

    def set_title(self, tag, attrs):
        """
        Установка флага заголовка
        :param tag: str
        :param attrs: tuple
        :return: None
        """
        dict_attrs = dict(attrs)

        if not self.title_flag and tag == self.title_tag:
            self.title_flag = True
            for tag_attr in self.title_tag_attributes:
                if not ((tag_attr in dict_attrs) and
                        (dict_attrs[tag_attr] == self.title_tag_attributes[tag_attr])):
                    self.title_flag = False

    def handle_starttag(self, tag, attrs):
        """
        Метод вызывается во время обработки открывающего тэга
        Если необходимо, устанавливает флаг параграфа,
        сохраняет информацию о ссылке и
        устанавливает флаг заголовка
        :param tag: str
        :param attrs: tuple
        :return: None
        """
        self.set_paragraph(tag, attrs)
        dict_attrs = dict(attrs)
        if self.paragraph_flag:
            for tag in self.link_tag:
                if HREF in dict_attrs:
                    self.paragraph.append('['+dict_attrs[HREF]+']')
        self.set_title(tag, attrs)

    def handle_data(self, data):
        """
        Метод вызывается во время обработки информаци внутри тэга
        Если разрешено, то добавляем информацию в параграф
        :param data: str
        :return: None
        """
        if len(self.context) > 0:
            tag = self.context[-1]
        else:
            tag = None
        if self.paragraph_flag and tag in self.allow_in_tags:
            self.paragraph.append(data)

        if self.title_flag:
            self.title = data
            self.title_flag = False

    def handle_endtag(self, tag):
        """
        Метод вызывается во время обработки закрывающего тэга
        Добавляем полученный на прошлом этапе параграф в контент
        :param tag: str
        :return: None
        """
        self.unset_paragraph()
        if self.paragraph and tag == self.content_tag:
            self.content.append(self.paragraph)
            self.paragraph = []

