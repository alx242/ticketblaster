import sqlite3

def connect():
  return sqlite3.connect('ticketblaster.db')

def insert(info):
  dbcon = connect()
  cur = dbcon.cursor()
  cur.execute("INSERT INTO ticket(info) VALUES('%(info)s')" % {"info": info})
  dbcon.commit()
  dbcon.close()

def getall():
  dbcon = connect()
  cur = dbcon.cursor()
  cur.execute("SELECT * FROM ticket")
  return cur.fetchall()

