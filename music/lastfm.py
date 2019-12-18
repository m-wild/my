import requests
import os
import time
import sqlite3
import logging

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO, handlers=[
  logging.StreamHandler(),
  logging.FileHandler("music/lastfm.log")
])

conn = sqlite3.connect("mwild.db")
user = "tehmantra"
api_key = os.environ.get("LASTFM_APIKEY")
api_url = "http://ws.audioscrobbler.com/2.0/"
E_OPERATION_FAILED = 8
E_SERVICE_OFFLINE = 11
E_TEMPORARY_ERROR = 16
E_RATE_LIMIT_EXCEEDED = 29

def main():
  try:
    db_init()
    get_tracks()
  except Exception as err:
    logging.exception(err)
  finally:
    conn.close()


def get_tracks():
  from_ts = db_get_last_ts()
  r = api_user_getrecenttracks(user, 1, from_ts)

  total_pages = int(r["recenttracks"]["@attr"]["totalPages"])

  logging.info("getting tracks from ts={}, total_pages={}".format(from_ts, total_pages))

  # start from last page and work backwards
  # this is better for error handling if something goes wrong
  page = total_pages
  while page > 0:
    r = api_user_getrecenttracks(user, page, from_ts)

    tracks = r["recenttracks"]["track"]
    db_insert(tracks)

    page -= 1
    time.sleep(.2)


# insert scrobbled tracks to the db
def db_insert(tracks):
  sqlparams = []
  for t in tracks:
    if "@attr" in t and "nowplaying" in t["@attr"]:
      continue

    sqlparams.append((t["date"]["uts"],
      t["artist"]["#text"],
      t["artist"]["mbid"],
      t["album"]["#text"],
      t["album"]["mbid"],
      t["name"],
      t["mbid"]))

  sql = """insert into music_scrobbles (date, artist, artist_mbid, album, album_mbid, track, track_mbid) 
           values (strftime('%s', ?, 'unixepoch', 'localtime'), ?, ?, ?, ?, ?, ?)"""
  conn.executemany(sql, sqlparams)
  conn.commit()

def db_get_last_ts():
  for r in conn.execute("select max(date) from music_scrobbles"):
    return r[0] or 0


def db_init():
  create = """create table if not exists music_scrobbles (
      date        datetime not null,
      artist      text     not null,
      artist_mbid text     null,
      album       text     null,
      album_mbid  text     null,
      track       text     not null,
      track_mbid  text     null
    );"""
  conn.execute(create)

# Last.fm API method user.getrecenttracks
# api response looks like:
# {
#   "recenttracks": {
#     "@attr": {
#       "page": "1",
#       "perPage": "1",
#       "total": "109594",
#       "totalPages": "54797",
#       "user": "tehmantra"
#     },
#     "track": [
#       {
#         "album": {
#           "#text": "The Direction of Last Things",
#           "mbid": "71a83d34-a1b6-44f1-ac41-0b8b3f68d56f"
#         },
#         "artist": {
#           "#text": "Intronaut",
#           "mbid": "1f40816c-9b2a-4a79-85e0-842b4841f930"
#         },
#         "date": {
#           "#text": "12 Dec 2019, 19:27",
#           "uts": "1576178875"
#         },
#         "image": [
#           ...
#         ],
#         "mbid": "5e88b7db-c2ec-44e2-803e-7908e14608b6",
#         "name": "City Hymnal",
#         "streamable": "0",
#         "url": "https://www.last.fm/music/Intronaut/_/City+Hymnal"
#       }
#     ]
#   }
# }
def api_user_getrecenttracks(user, page, from_ts, limit=200):
  logging.info("user.getrecenttracks page={}".format(page))
  params = {
    "limit": limit,
    "user": user,
    "page": page,
    "from": from_ts
  }
  return api_call("user.getrecenttracks", params)


# Call the last.fm API returning json
def api_call(method: str, params: dict):
  params.update({
    "api_key": api_key,
    "format": "json",
    "method": method
  })
  
  while True:
    r = requests.get(api_url, params)
    body = r.json()

    if r.status_code == 200:
      return body
    else:
      if body["error"] in [ E_OPERATION_FAILED, E_SERVICE_OFFLINE, E_TEMPORARY_ERROR, E_RATE_LIMIT_EXCEEDED ]:
        logging.warning(body["message"])
        time.sleep(60)
      else:
        err = "{}: {}".format(r.status_code, r.text)
        raise Exception(err)



main()
