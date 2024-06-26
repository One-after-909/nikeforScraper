import requests
import json
from pymongo import MongoClient


class Scraper:
    """Parent class for specific languages. Implements datastructures and saving to file/DB."""

    def __init__(self, url: str = "", db_connection: str = "", db_name: str = ""):
        self.lang_code = ""
        self.DB = None
        self.url = url
        if db_connection != "":
            mongo = MongoClient()
            self.DB = mongo[db_name]

        self.data = None
        self.test_data = None

    def save_to_file(self, file_name, save_test: bool = False):
        data = self.test_data if save_test else self.data
        with open(file_name, 'w') as f:
            json.dump(data, f)

    def save_to_mongo(self):
        collection = self.DB["bibles"]
        collection.insert_many(self.data)

    def load_data(self, data):
        self.data = data

    def load_from_file(self, file_path):
        with open(file_path, "r") as f:
            self.data = json.load(f)

    def dump(self):
        return self.data

    def __exit__(self):
        if self.DB is not None:
            self.DB.close()


class ScraperCZ(Scraper):
    def __init__(self, *args, **kwargs):
        super(ScraperCZ, self).__init__(*args, **kwargs)
        self.url = "http://bible.liturgie.cz/services/" if self.url == "" else self.url
        self.lang_code = "cz"

    def get_chapter_text(self, book_id: int, chapter: int, verbose: bool = False) -> list:
        url = self.url + "Verses.ashx?BookId=" + str(book_id) + "&Chapter=" + str(chapter)
        chapter_data = get_response(url)
        chapter_data_new = []
        for verse in chapter_data:
            verse_new = {}
            for x in verse:
                verse_new[x[:1].lower()+x[1:]] = verse[x]
            chapter_data_new.append(verse_new)
        chapter_data = chapter_data_new
        return chapter_data

    def get_chapters(self, book_id: int, verbose: bool = False) -> list:
        chapters_raw = get_response(self.url + "Chapters.ashx?BookId=" + str(book_id))
        chapters = []
        for chapter_raw in chapters_raw:
            chapter = {}
            for x in chapter_raw:
                chapter[x[:1].lower() + x[1:]] = chapter_raw[x]
            chapters.append(chapter)

        chapters_count = len(chapters)
        for chapter_index in range(len(chapters)):
            if verbose:
                print("Chapter {}/{}".format(chapter_index+1, chapters_count))
            chapter_data = self.get_chapter_text(book_id, chapters[chapter_index]["chapter"], verbose)
            chapters[chapter_index]["verses"] = chapter_data

        return chapters

    def get_book(self, book: dict, verbose: bool = False) -> dict:
        if verbose:
            print(book["name"])
        book["lang"] = "cz"
        book["chapters"] = self.get_chapters(book["id"], verbose)
        return book

    def get_book_headers(self):
        books = get_response(self.url + "Books.ashx")
        books_new = []

        for book in books:
            book_new = {}
            for x in book:
                book_new[x.lower()] = book[x]
            books_new.append(book_new)
        books = books_new
        return books

    def get_books(self, verbose: bool = False) -> list:
        books = self.get_book_headers()
        books_done = []
        for book in books:
            books_done.append(self.get_book(book, verbose))
        return books_done

    def load_from_url(self, verbose: bool = False):
        self.data = self.get_books(True)


def get_response(url):
    data = requests.get(url)
    return data.json()["DataItems"]
