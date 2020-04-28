import mysql.connector
import sys
import csv

cnx = mysql.connector.connect(user='', password='',host='dbtonanuvem.c9sdzu2icdqg.us-east-1.rds.amazonaws.com',database='cameradb')

cursor = cnx.cursor()

QUERY = "SELECT * from registros;"

cursor.execute(QUERY)

result = cursor.fetchall()

c = csv.writer(open('registros.csv','w'))

for x in result:
	c.writerow(x)

cursor.close()
cnx.close()
