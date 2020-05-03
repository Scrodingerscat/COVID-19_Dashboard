from apscheduler.schedulers.blocking import BlockingScheduler

# import sys
# import os.path

# sys.path.append(os.path.join(os.path.dirname(__file__), "."))
import worker

sched = BlockingScheduler()


@sched.scheduled_job("interval", minutes=3)
def timed_job():
    print("This job is run every three minutes.")
    worker.job()


sched.start()
