# -*- coding: utf-8 -*-
from apscheduler.schedulers.blocking import BlockingScheduler

# import sys
# import os.path

# sys.path.append(os.path.join(os.path.dirname(__file__), "."))
import dbupdate as db

sched = BlockingScheduler()


@sched.scheduled_job("interval", hour=2)
def morning():
    db.job()
    print("This job will done every 2 hours")


sched.start()
