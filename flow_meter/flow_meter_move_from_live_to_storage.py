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
cnx = create_engine("mysql+pymysql://writer:heiko@twofast-RPi3-0:3306/NG_twofast_DB", echo=False)
def get_live_values():

	query = "SELECT time, read_voltage FROM flow_meter_readout_live"
	df = pd.read_sql(query, db)

	return df

def save_to_storage(df, sqlTable):
	df.to_sql(name=sqlTable, con=cnx, if_exists = 'append', index=False)

df = get_live_values()

sqlTable = 'flow_meter_readout_storage'

save_to_storage(df, sqlTable)


# truncate live table
cur = db.cursor()
try:
    cur.execute("""TRUNCATE TABLE flow_meter_readout_live""")

except:
    cur.rollback()

cur.close()