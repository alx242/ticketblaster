import sqlite3

def connect():
  dbcon = sqlite3.connect('ticketblaster.db')
  cur = dbcon.cursor()
  return dbcon, cur

def close(dbcon):
  dbcon.commit()
  dbcon.close()

def add(info):
  dbcon, cur = connect()
  cur.execute("INSERT INTO tickets(info) VALUES(?)", (info,))
  close(dbcon)

def grab(owner, index):
  dbcon, cur = connect()
  cur.execute("UPDATE tickets SET owner=? WHERE id=?", (owner, index))
  close(dbcon)

def delete(index):
  dbcon, cur = connect()
  cur.execute("DELETE FROM tickets WHERE id=?", index)
  close(dbcon)

def set(target, value, index):
  dbcon, cur = connect()
  if target in ('info', 'owner', 'created', 'done', 'deleted'):
    sql = "UPDATE tickets SET %(target)s=? WHERE id=?" % {"target": target}
    cur.execute(sql, (value, index))
  else:
    raise Exception("unsupported_sql_value")
  close(dbcon)

def getall():
  dbcon, cur = connect()
  cur.execute("SELECT * FROM tickets")
  rows = cur.fetchall()
  close(dbcon)
  return rows

