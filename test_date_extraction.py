import numpy as np
import pandas as pd
import pymysql

def getAvailableHistoricalDates():
	# returns available dates from the database
	db = pymysql.connect(host="twofast-RPi3-0",  # your host
						 user="doseReader",  # username
						 passwd="heiko",  # password
						 db="NG_twofast_DB")  # name of the database
	# Create a Cursor object to execute queries.
	cur = db.cursor()
	try:
		# DOSE
		# sql = "SELECT DATE(time) FROM data_dose" # 16.8s
		sql = "SELECT DISTINCT DATE(time) FROM data_dose" # 5.7 s
		cur.execute(sql)
		rows = cur.fetchall()
		df = pd.DataFrame( [[ij for ij in i] for i in rows] )
		df.rename(columns={0: 'date'}, inplace=True)		
		
		lst_dates = df['date'].apply(lambda x: '{}'.format(x))
		lst_dates = lst_dates.values.tolist()
	except:
		cur.rollback()

	cur.close()

	return lst_dates


a = getAvailableHistoricalDates()
[print(type(b)) for b in a]
print(a)