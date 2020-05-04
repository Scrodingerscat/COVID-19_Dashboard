from apscheduler.schedulers.blocking import BlockingScheduler

# import sys
# import os.path

# sys.path.append(os.path.join(os.path.dirname(__file__), "."))
import dbupdate as db

sched = BlockingScheduler()

tz = "America/Toronto"


@sched.scheduled_job("cron", hour=11, minute=30, timezone=tz)
def morning():
    db.job()
    print("data update at 11:30am.")


@sched.scheduled_job("cron", hour=19, minute=30, timezone=tz)
def afternoon():
    db.job()
    print("data update at 19:30pm.")


sched.start()
