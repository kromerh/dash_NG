import pandas as pd
import pymysql
import re
from sqlalchemy import create_engine

# read password and user to database
credentials_file = r'./credentials.pw'

credentials = pd.read_csv(credentials_file, header=0)
user = credentials['username'].values[0]
pw = credentials['password'].values[0]


db = pymysql.connect(host="twofast-RPi3-0",  # your host
					 user=user,  # username
					 passwd=pw,  # password
					 db="NG_twofast_DB", # name of the database
					 charset='utf8',
					 cursorclass=pymysql.cursors.DictCursor)

# truncate table
cur = db.cursor()
try:
    cur.execute("""TRUNCATE TABLE microwave_generator_control""")

except:
    cur.rollback()

cur.close()