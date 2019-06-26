import pandas as pd
import pymysql


# read password and user to database
credentials_file = r'./credentials.pw'

credentials = pd.read_csv(credentials_file, header=0)
user = credentials['username'].values[0]
pw = credentials['password'].values[0]


def insert_into_DB(tableName, lstCols, lstValues, username, password):
	"""
	Inserts a new row in the database in the table tableName. The column names should be in the form of a list and the respective
	values should also be a list in the order of the columns to be updated into.
	"""

	# connect to the database
	db = pymysql.connect(host="twofast-RPi3-0",  # your host
					 user=username,  # username
					 passwd=password,  # password
					 db="NG_twofast_DB", # name of the database
					 charset='utf8',
					 cursorclass=pymysql.cursors.DictCursor)
	cur = db.cursor()

	# SQL statement execution
	# Assert that the length of the columns matches the length of the values
	assert len(lstCols) == len(lstValues)

	# IF only power or frequency to update, i.e. one value
	if len(lstCols) == 1:
		try:
			cur.execute("INSERT INTO %(tablename)s (%(col)s) VALUES (%(val)s)" % {"tablename": tableName, "col": lstCols[0], "val":lstValues[0]})
		except:
			cur.rollback()
	else:
	# more than one value to update
		try:
			cur.execute("INSERT INTO %(tablename)s (%(col1)s, %(col2)s) VALUES (%(val1)s, %(val2)s)" % {"tablename": tableName, "col1": lstCols[0], "col2": lstCols[1], "val1":lstValues[0], "val2":lstValues[1]})
		except:
			cur.rollback()

	db.commit()
	cur.close()