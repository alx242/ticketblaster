import sqlite3
import os

def connect():
  conn = sqlite3.connect('ticketblaster.db')
  conn.row_factory = sqlite3.Row
  cur = conn.cursor()
  return conn, cur

def close(dbcon):
  dbcon.commit()
  dbcon.close()

def init():
  dbcon, cur = connect()
  sql = ("CREATE TABLE tickets(id INTEGER PRIMARY KEY, "
         "                     info TEXT, "
         "                     owner VARCHAR(32), "
         "                     created TIMESTAMP DEFAULT CURRENT_TIMESTAMP, "
         "                     done BOOLEAN DEFAULT 0) ")
  cur.execute(sql)
  close(dbcon)

def already_exists():
  return os.path.isfile("ticketblaster.db")

def add(info):
  dbcon, cur = connect()
  cur.execute("INSERT INTO tickets(info) VALUES(?)", (info,))
  close(dbcon)

def get(index):
  dbcon, cur = connect()
  cur.execute("SELECT * FROM tickets WHERE id=?", (index,))
  rows = cur.fetchall()
  close(dbcon)
  return rows

def exists(index):
  rows = get(index)
  return len(rows) > 0

def grab(owner, index):
  dbcon, cur = connect()
  cur.execute("UPDATE tickets SET owner=? WHERE id=?", (owner, index))
  close(dbcon)

def set(target, value, index):
  dbcon, cur = connect()
  if target in ('info', 'owner', 'created', 'done', 'deleted'):
    sql = "UPDATE tickets SET %(target)s=? WHERE id=?" % {"target": target}
    cur.execute(sql, (value, index))
  else:
    raise Exception("unsupported_sql_value")
  close(dbcon)

"""
Get all tickets of these types:
 - active
 - ungrabbed
 - all
"""
def getall(ticket_type="all"):
  dbcon, cur = connect()
  if ticket_type == 'active':
    cur.execute("SELECT * FROM tickets WHERE done = 0 AND deleted = 0")
  elif ticket_type == 'unpicked': 
    cur.execute("SELECT * FROM tickets WHERE done = 0 AND deleted = 0 and owner IS NULL")
  else:
    cur.execute("SELECT * FROM tickets")
  rows = cur.fetchall()
  close(dbcon)
  return rows

