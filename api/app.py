import sqlite3
from flask import Flask, g, jsonify

app = Flask(__name__)

def dict_factory(cursor, row):
  d = {}
  for idx, col in enumerate(cursor.description):
    d[col[0]] = row[idx]
  return d


def get_db():
  if "db" not in g:
    g.db = sqlite3.connect(
      "mwild.db",
      detect_types=sqlite3.PARSE_DECLTYPES
    )
    g.db.row_factory = dict_factory # rows as dicts
  return g.db

def query(q: str, args=()):
  db: sqlite3.Connection = get_db()
  cur = db.execute(q, args)
  return cur.fetchall()
  

@app.teardown_appcontext
def dispose(err):
  db: sqlite3.Connection = g.pop("db", None)
  if db is not None:
    db.close()

@app.route("/")
def hello_world():
  return "Hello, World!"
  
@app.route("/music_scrobbles")
def get_music_scrobbles():
  return jsonify(query("select * from music_scrobbles limit 1000"))