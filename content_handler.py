import urllib.parse
import urllib.request
import web_parser
import os
import json


UTF_8 = 'utf-8'
DEFAULT = {
    "allow_in_tags": ["p", "a", "b", "i", "u", "span"],
    "title_tag": "h1",
    "title_tag_attributes": {},
    "content_tag": "p",
    "content_tag_attributes": {},
    "word_wrap": 80,
    "link_tag": "a",
}


class ContentHandler:

    def __get_template(self, filename):
        """
        Чтение параметров из файла настроек
        здесь можно добавить их валидацию
        если файл не удалось считать, возвращаются параметры по умолчанию
        :param filename: str
        :return: str
        """
        try:
            file = open(filename)
            config = json.load(file)
        except Exception:
            config = DEFAULT

        return config

    def __get_content(self, url, filename):
        """
        Чтение HTML кода и его обработка классом парсера
        :param url: str
        :param filename: str
        :return: str
        """
        request = urllib.request.urlopen(url)
        html = request.read().decode(request.info().get_charsets()[-1])
        request.close()

        parser = web_parser.Parser(**self.__get_template(filename))

        if parser and html:
            parser.feed(html)
        parser.close()
        return parser.get_text()

    def __get_relative_path_filename(self, url):
        """
        Получение относительного пути из url и
        формирование названия итогового файла
        :param url: str
        :return: str
        """
        url_parse = urllib.parse.urlparse(url)
        url_path = url_parse.path
        path_items = url_path.split('/')[1:]
        # если в конце url '/', то останется пустой элемент
        if path_items[-1] == '':
            path_items.pop(-1)

        filename_tmp = path_items[-1].split('.')
        # если последний элемент пути - файл отбрасываем его расширение
        if len(filename_tmp) > 1:
            filename = filename_tmp[0]
        else:
            filename = path_items[-1]

        # удаляем последний элемент так как название файла не участвует в пути
        path_items.pop(-1)
        hostname = urllib.parse.urlparse(url).hostname
        relative_path = hostname + "/" + "/".join(path_items)
        result = relative_path + "/" + filename + '.txt'

        return relative_path, result

    def write_content_to_file(self, url, filename):
        """
        Запись полученных результатов в выходной файл
        :param url: str
        :param filename: str
        :return: str
        """
        content = self.__get_content(url, filename)
        if content == '':
            return 'Error: Empty content'

        try:
            relative_path, filename = self.__get_relative_path_filename(url)
            if not os.path.exists(relative_path):
                os.makedirs(relative_path)

            file = open(filename, 'w', encoding=UTF_8)
            file.write(content)
            file.close()
        except Exception:
            return 'Error: problem while writing to file'

        return "Success: Done"

