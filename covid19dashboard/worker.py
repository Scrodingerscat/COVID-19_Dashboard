# -*- coding: utf-8 -*-
import pandas as pd
import os
import sqlite3
import time
import schedule

# Set database path
currentpath = os.path.abspath(os.path.dirname(__file__))
folder = "data"
db = "COVID19.db"
path = os.path.abspath(os.path.join(currentpath, "..", folder, db))


def job():
    # Read csv file from url
    df = pd.read_csv("https://health-infobase.canada.ca/src/data/covidLive/covid19.csv")

    # Save into database
    conn = sqlite3.connect(path, check_same_thread=False)
    df.to_sql("covid", index=False, con=conn, if_exists="replace")
    conn.close()
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print("Database update has completed: ", now)


# schedule.every(8).hours.do(job)

# while True:
#     schedule.run_pending()
#     time.sleep(1)  # wait one minute
