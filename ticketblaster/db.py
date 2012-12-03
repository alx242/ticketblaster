import sqlite3

def connect():
  return sqlite3.connect('ticketblaster.db')

def add(info):
  dbcon = connect()
  cur = dbcon.cursor()
  cur.execute("INSERT INTO tickets(info) VALUES('%(info)s')" %
              {"info": info})
  dbcon.commit()
  dbcon.close()

def grab(owner, index):
  dbcon = connect()
  cur = dbcon.cursor()
  cur.execute("UPDATE tickets SET owner='%(owner)s' WHERE id='%(id)s'" %
              {"owner": owner, "id": index})
  dbcon.commit()
  dbcon.close()

def delete(index):
  dbcon = connect()
  cur = dbcon.cursor()
  cur.execute("DELETE FROM tickets WHERE id='%(id)s'" %
              {"id": index})
  dbcon.commit()
  dbcon.close()

def set(target, value, index):
  dbcon = connect()
  cur = dbcon.cursor()
  cur.execute("UPDATE tickets SET %(target)s='%(value)s' WHERE id='%(id)s'" %
              {"target": target, "value": value, "id": index})
  dbcon.commit()
  dbcon.close()

def getall():
  dbcon = connect()
  cur = dbcon.cursor()
  cur.execute("SELECT * FROM tickets")
  return cur.fetchall()

