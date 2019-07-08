import pandas as pd
import tkinter as tk
import numpy as np
import warnings
import os

from contextlib import suppress
from sklearn.neighbors import NearestNeighbors

warnings.filterwarnings("ignore")


class RecommendationSystem:

    def __init__(self):
        self.ratings = pd.read_csv('BX-Book-Ratings.csv', sep=';', encoding="latin-1")
        # BX-Books.csv is not a valid csv file, it contains few mistakes => error_bad_lines=False
        self.books = pd.read_csv('BX-Books.csv', sep=';', error_bad_lines=False, encoding="latin-1",
                                 warn_bad_lines=False)
        self.books.drop(['Image-URL-S', 'Image-URL-M', 'Image-URL-L'], axis=1, inplace=True)
        self.ratings.columns = ['UserID', 'ISBN', 'BookRating']
        self.books.columns = ['ISBN', 'BookTitle', 'BookAuthor', 'YearOfPublication', 'publisher']

        self.valid_ratings = self.ratings[self.ratings.ISBN.isin(self.books.ISBN)]
        self.non_zero_ratings = self.valid_ratings[self.valid_ratings.BookRating != 0]

        # in real system we cannot repair all issues in given dataset so we need to skip wrong lines
        self.books = self.books[self.books.YearOfPublication.apply(lambda x: str(x).isnumeric())]
        self.books.YearOfPublication = pd.to_numeric(self.books.YearOfPublication)

        with suppress(tk.TclError):
            self.root = tk.Tk()
            self.listbox = tk.Listbox(self.root)

        counts = self.non_zero_ratings['UserID'].value_counts()
        self.non_zero_ratings = self.non_zero_ratings[
            self.non_zero_ratings['UserID'].isin(counts[counts > 15].index)]
        counts = self.non_zero_ratings['ISBN'].value_counts()
        self.non_zero_ratings = self.non_zero_ratings[self.non_zero_ratings['ISBN'].isin(counts[counts > 10].index)]
        counts = self.non_zero_ratings['BookRating'].value_counts()
        self.non_zero_ratings = self.non_zero_ratings[
            self.non_zero_ratings['BookRating'].isin(counts[counts > 50].index)]

        self.books = self.books[self.books['ISBN'].isin(self.non_zero_ratings.ISBN)]

        self.matrix_ratings = self.non_zero_ratings.pivot(index='ISBN', columns='UserID', values='BookRating')
        self.matrix_ratings.apply(lambda row: row.fillna(0, inplace=True), axis=1)

        self.space = np.array(list(map(lambda x: list(self.matrix_ratings.loc[x]), self.matrix_ratings.index)))
        self.model = self.get_trained_space(self.space)
        print("Clustering finished.")

    @staticmethod
    def get_trained_space(space):
        return NearestNeighbors(n_neighbors=9).fit(space)

    def listbox_update(self, data):
        self.listbox.delete(0, 'end')
        self.listbox.insert('end', *sorted(data, key=str.lower))  # need to sort according to reviews

    def on_keyrelease(self, event):
        value = event.widget.get().strip().lower()
        self.listbox_update(self.books.BookTitle[:20] if not value else list(
            filter(lambda x: value in x.lower(), self.books.BookTitle))[:30])

    def print_recommendation(self, selected_book):
        selected_book_index = list(self.matrix_ratings.index).index(selected_book)
        distances, indices = self.model.kneighbors([self.space[selected_book_index]])
        print("\n".join(list(map(lambda i: str(
            self.books[self.books['ISBN'] == self.matrix_ratings.index[i]].BookTitle), indices[0][1:]))))

        print(distances)

    def on_select(self, event):
        selected_book = self.books.loc[self.books.BookTitle == event.widget.get(
            event.widget.curselection()), :].values[0][0]
        self.print_recommendation(selected_book)

    def on_select_minimal(self, book_name):
        selected_book = self.books.loc[self.books.BookTitle == book_name, :].values[0][0]
        self.print_recommendation(selected_book)

    def main(self):
        try:
            entry = tk.Entry(self.root)
            entry.pack()
            entry.bind('<KeyRelease>', self.on_keyrelease)

            self.listbox.pack()
            self.listbox.bind('<Double-Button-1>', self.on_select)
            self.listbox.bind('<Return>', self.on_select)
            self.listbox_update(self.books.BookTitle[:20])

            self.root.mainloop()
        except AttributeError:
            self.on_select_minimal(os.environ.get('BOOK_NAME', 'The Green Mile: Night Journey (Green Mile Series)'))


RS = RecommendationSystem()
RS.main()
