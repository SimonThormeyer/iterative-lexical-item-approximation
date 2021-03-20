from datetime import timedelta
from os import environ 

SECRET_KEY = environ.get('SECRET_KEY')
SESSION_TYPE = 'filesystem'
SEND_FILE_MAX_AGE_DEFAULT = 0
SESSION_PERMANENT = True
PERMANENT_SESSION_LIFETIME = timedelta(minutes=10)
# The maximum number of items the session stores 
# before it starts deleting some, default 500
SESSION_FILE_THRESHOLD = 5 