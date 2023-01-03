import os
import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Progressbar

import pandas as pd
import snscrape.modules.twitter as sntwitter
from tkcalendar import DateEntry

# based on https://github.com/mehranshakarami/AI_Spectrum/blob/main/2022/snscrape/tweets.py

class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        # Term
        row = 0
        self.term_label = tk.Label(master, text='Term')
        self.term_label.grid(row=row, column=0, padx=5, pady=5)
        self.term_input = tk.Entry(master)
        self.term_input.grid(row=row, column=1, columnspan=3, padx=5, pady=5, sticky=tk.W+tk.E)
        self.term_input.focus_set()
        self.term = tk.StringVar()
        # Tell the entry widget to watch the term variable.
        self.term_input["textvariable"] = self.term
        # Define a callback for when the user hits return.
        # It retrieves and exports tweets for the given term
        self.term_input.bind('<Key-Return>',
                               self.get_tweets)

        # Handle
        row += 1
        self.handle_label = tk.Label(master, text='Handle')
        self.handle_label.grid(row=row, column=0, padx=5, pady=5)
        self.handle_input = tk.Entry(master)
        self.handle_input.grid(row=row, column=1, padx=5, pady=5)
        self.handle = tk.StringVar()
        # Tell the entry widget to watch the handle variable.
        self.handle_input["textvariable"] = self.handle
        # Define a callback for when the user hits return.
        # It retrieves and exports tweets for the given handle
        self.handle_input.bind('<Key-Return>',
                               self.get_tweets)

        # Limit
        self.limit_label = tk.Label(master, text='Limit')
        self.limit_label.grid(row=row, column=2, padx=5, pady=5)
        self.limit_input = tk.Entry(master)
        self.limit_input.grid(row=row, column=3, padx=5, pady=5)
        self.limit = tk.StringVar()
        self.limit.set(5000)
        # Tell the entry widget to watch the handle variable.
        self.limit_input["textvariable"] = self.limit

        # Since Date / Until Date
        row += 1
        self.since_label = tk.Label(master, text='Since')
        self.since_label.grid(row=row, column=0, padx=5, pady=5)
        self.cal_since = DateEntry(
            master, selectmode='day', year=2010, month=1, day=1)
        self.cal_since.grid(row=row, column=1, padx=15)
        self.until_label = tk.Label(master, text='Until')
        self.until_label.grid(row=row, column=2, padx=5, pady=5)
        self.cal_until = DateEntry(master, selectmode='day')
        self.cal_until.grid(row=row, column=3, padx=15)

        # Button to export tweets
        row += 1
        self.button = tk.Button(
            master, text='Export tweets', command=self.get_tweets)
        self.button.grid(row=row, columnspan=4, padx=5, pady=5)

        # Progress
        row += 1
        self.pb = Progressbar(master, orient='horizontal',
                              length=100, mode='determinate')
        self.pb.grid(row=row, columnspan=4, padx=5, pady=5)
        row += 1
        self.pb_label = tk.Label(master)
        self.pb_label.grid(row=row, columnspan=4, padx=5, pady=5)

    def get_tweets(self, event=None):
        handle = str(self.handle.get())
        term = str(self.term.get())
        if (handle.strip() == '' and term.strip() == ''):
            messagebox.showinfo("No term or handle", "Please provide a term and/or a handle to search for.")
            return
        self.pb['value'] = 0
        self.export_handle_tweet_to_csv(term, handle, int(self.limit.get()), self.cal_until.get_date(
        ).strftime("%Y-%m-%d"), self.cal_since.get_date().strftime("%Y-%m-%d"))

    def update_progress(self, value, total):
        self.pb["maximum"] = total
        self.pb["value"] = value
        self.pb_label['text'] = f"{value} Tweets found"
        self.master.update()

    def export_handle_tweet_to_csv(self, term, handle, limit, until, since):
        if (str(handle).strip() != ""):
            query = f"{term} from:{handle} until:{until} since:{since}"
        else :
            query = f"{term} until:{until} since:{since}"
        tweets = []
        print(query)
        i = 0
        self.update_progress(i, limit)

        for tweet in sntwitter.TwitterSearchScraper(query).get_items():

            if len(tweets) == limit:
                break
            else:
                tweets.append([tweet.date, tweet.user.username,
                              tweet.content, tweet.url])
                i += 1
                self.update_progress(i, limit)
        self.update_progress(i, i)
        df = pd.DataFrame(tweets, columns=['Date', 'User', 'Tweet', 'URL'])
        # print(df)

        # to save to csv
        if (str(handle).strip() != ""):
            file_name = f'{term}@{handle}_tweets.csv'
        else :
            file_name = f'{term}_tweets.csv'
        df.to_csv(file_name, sep=";")
        current_dir = os.getcwd()
        os.startfile(current_dir + "\\" + file_name)


root = tk.Tk()
root.resizable(False, False)
TwitterSearchScraper = App(root)
TwitterSearchScraper.master.title("Twitter Search Scraper")

# start the program
TwitterSearchScraper.mainloop()
