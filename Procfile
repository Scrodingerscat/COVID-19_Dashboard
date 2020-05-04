web: gunicorn covid19dashboard.app:server
worker: python covid19dashboard/dbupdate.py
clock: python covid19dashboard/clock.py